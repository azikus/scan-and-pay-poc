"""Local interface discovery and live listener state for the Mac demo server."""

import asyncio
import re
import subprocess
from collections.abc import Awaitable, Callable
from datetime import UTC, datetime
from ipaddress import IPv4Address, IPv4Network
from typing import Literal

from pydantic import Field

from backend.models import Model

LOCAL_RANGES = tuple(
    IPv4Network(value)
    for value in ("10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16", "169.254.0.0/16")
)


def local_address(value: str) -> bool:
    try:
        address = IPv4Address(value)
    except ValueError:
        return False
    return any(address in network for network in LOCAL_RANGES)


def interface_addresses(output: str) -> dict[str, str]:
    """Physical en* interfaces only: no public IPs, VPNs or virtual bridges."""
    addresses = {}
    for block in re.split(r"(?=^\S)", output, flags=re.MULTILINE):
        header = re.match(r"(en\d+): flags=[0-9a-fA-F]+<([^>]+)>", block)
        if not header or "UP" not in header[2].split(",") or "status: inactive" in block:
            continue
        for address in re.findall(r"^\s+inet (\S+)", block, flags=re.MULTILINE):
            if local_address(address):
                addresses[address] = header[1]
    return dict(sorted(addresses.items()))


def discover_addresses() -> dict[str, str]:
    result = subprocess.run(
        ["/sbin/ifconfig"], capture_output=True, text=True, check=True, timeout=2
    )
    return interface_addresses(result.stdout)


class ConnectionAddress(Model):
    url: str
    interface: str
    kind: Literal["network", "link_local"]


class ConnectionStatus(Model):
    automatic: bool = False
    refresh_seconds: int | None = None
    checked_at: datetime | None = None
    addresses: list[ConnectionAddress] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class LocalNetwork:
    def __init__(
        self,
        port: int,
        discover: Callable[[], dict[str, str]] = discover_addresses,
    ) -> None:
        self.port = port
        self.discover = discover
        self.status = ConnectionStatus(automatic=True, refresh_seconds=2)
        self.listeners: dict[str, asyncio.Server] = {}
        self.bind: Callable[[str], Awaitable[asyncio.Server]]
        self.retire: Callable[[asyncio.Server], None]

    async def refresh(self) -> None:
        try:
            found = await asyncio.to_thread(self.discover)
        except (OSError, subprocess.SubprocessError):
            self.status.warnings = ["Address refresh failed. Previous listeners are shown."]
            return
        # Defense in depth if a different discovery implementation is supplied.
        addresses = {address: name for address, name in found.items() if local_address(address)}
        warnings = []
        for address in list(self.listeners):
            if address not in addresses:
                self.retire(self.listeners.pop(address))
        for address in addresses:
            if address in self.listeners:
                continue
            try:
                self.listeners[address] = await self.bind(address)
            except OSError:
                warnings.append(f"Could not listen on {address}. Retrying automatically.")
        self.status = ConnectionStatus(
            automatic=True,
            refresh_seconds=2,
            checked_at=datetime.now(UTC),
            addresses=[
                ConnectionAddress(
                    url=f"http://{address}:{self.port}",
                    interface=addresses[address],
                    kind="link_local" if IPv4Address(address).is_link_local else "network",
                )
                for address in sorted(self.listeners)
            ],
            warnings=warnings,
        )

    async def watch(self) -> None:
        while True:
            await asyncio.sleep(2)
            await self.refresh()


def manual_status(host: str | None, port: int | None) -> ConnectionStatus:
    addresses = []
    if host and port and local_address(host):
        addresses.append(
            ConnectionAddress(
                url=f"http://{host}:{port}",
                interface="",
                kind="link_local" if IPv4Address(host).is_link_local else "network",
            )
        )
    return ConnectionStatus(addresses=addresses)
