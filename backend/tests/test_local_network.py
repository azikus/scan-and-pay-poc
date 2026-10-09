import asyncio
import subprocess
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import pytest
import uvicorn
from fastapi.testclient import TestClient

from backend.api import create_app
from backend.local_network import (
    ConnectionAddress,
    ConnectionStatus,
    LocalNetwork,
    discover_addresses,
    interface_addresses,
    local_address,
    manual_status,
)
from backend.local_server import LocalServer, main

INTERFACES = """lo0: flags=8049<UP,LOOPBACK,RUNNING> mtu 16384
    inet 127.0.0.1 netmask 0xff000000
    inet6 ::1 prefixlen 128
utun0: flags=8051<UP,POINTOPOINT,RUNNING> mtu 1500
    inet 10.12.0.3 netmask 0xffffff00
bridge100: flags=8863<UP,BROADCAST,RUNNING> mtu 1500
    inet 192.168.64.1 netmask 0xffffff00
en0: flags=8863<UP,BROADCAST,RUNNING> mtu 1500
    inet 172.20.10.2 netmask 0xfffffff0 broadcast 172.20.10.15
    inet6 fe80::123 prefixlen 64
    status: active
en24: flags=8b63<UP,BROADCAST,RUNNING> mtu 1500
    inet 169.254.10.2 netmask 0xffff0000
    status: active
en1: flags=8863<UP,BROADCAST,RUNNING> mtu 1500
    inet 192.168.1.12 netmask 0xffffff00
    status: inactive
en2: flags=8863<BROADCAST,RUNNING> mtu 1500
    inet 10.0.0.3 netmask 0xffffff00
en3: flags=8863<UP,BROADCAST,RUNNING> mtu 1500
    inet 8.8.8.8 netmask 0xffffff00
    inet invalid netmask 0xffffff00
"""


def test_interface_discovery_uses_only_active_physical_private_ipv4(monkeypatch):
    expected = {"169.254.10.2": "en24", "172.20.10.2": "en0"}
    assert interface_addresses(INTERFACES) == expected
    assert interface_addresses("") == {}
    run = Mock(return_value=SimpleNamespace(stdout=INTERFACES))
    monkeypatch.setattr(subprocess, "run", run)
    assert discover_addresses() == expected
    assert run.call_args.args == (["/sbin/ifconfig"],)
    assert run.call_args.kwargs["timeout"] == 2


@pytest.mark.parametrize("address", ["8.8.8.8", "0.0.0.0", "127.0.0.1", "192.0.2.1", "::1", "bad"])
def test_public_loopback_reserved_and_invalid_addresses_never_become_phone_listeners(address):
    assert not local_address(address)


async def test_switching_addresses_keeps_unchanged_listeners_and_retires_only_old_ones():
    discover = Mock(return_value={"192.168.1.12": "en0", "169.254.10.2": "en24"})
    network = LocalNetwork(8000, discover)
    network.bind = AsyncMock(side_effect=lambda _: Mock())
    network.retire = Mock()
    await network.refresh()
    old_wifi, usb = network.listeners["192.168.1.12"], network.listeners["169.254.10.2"]
    assert len(network.status.addresses) == 2
    first_check = network.status.checked_at
    await network.refresh()
    assert network.bind.await_count == 2
    assert not network.retire.called
    discover.return_value = {"172.20.10.2": "en0", "169.254.10.2": "en24", "8.8.8.8": "en1"}
    await network.refresh()
    network.retire.assert_called_once_with(old_wifi)
    assert network.listeners["169.254.10.2"] is usb
    assert network.bind.await_count == 3
    assert network.status.checked_at >= first_check
    assert [(a.url, a.kind) for a in network.status.addresses] == [
        ("http://169.254.10.2:8000", "link_local"),
        ("http://172.20.10.2:8000", "network"),
    ]
    discover.return_value = {}
    await network.refresh()
    assert network.status.addresses == []
    assert network.retire.call_count == 3


async def test_failed_bind_is_not_advertised_and_retried_on_next_refresh():
    network = LocalNetwork(8010, lambda: {"10.0.0.2": "en0"})
    network.bind = AsyncMock(side_effect=[OSError("private OS error"), Mock()])
    network.retire = Mock()
    await network.refresh()
    assert not network.status.addresses
    assert network.status.warnings == ["Could not listen on 10.0.0.2. Retrying automatically."]
    await network.refresh()
    assert network.status.addresses[0].url == "http://10.0.0.2:8010"
    assert network.status.warnings == []


@pytest.mark.parametrize("failure", [OSError(), subprocess.TimeoutExpired("ifconfig", 2)])
async def test_discovery_failure_keeps_previous_listeners_and_warns(failure):
    discover = Mock(return_value={"10.0.0.2": "en0"})
    network = LocalNetwork(8000, discover)
    network.bind = AsyncMock(return_value=Mock())
    network.retire = Mock()
    await network.refresh()
    before = network.status.model_dump()
    discover.side_effect = failure
    await network.refresh()
    assert not network.retire.called
    assert network.status.addresses[0].url == "http://10.0.0.2:8000"
    assert network.status.checked_at == before["checked_at"]
    assert "Previous listeners" in network.status.warnings[0]


def test_connection_endpoint_requires_auth_and_never_probes_or_dispatches(
    settings, definitions, adapters
):
    network = LocalNetwork(
        8000, Mock(side_effect=AssertionError("Request must not scan interfaces"))
    )
    network.status = ConnectionStatus(
        automatic=True,
        refresh_seconds=2,
        addresses=[
            ConnectionAddress(url="http://172.20.10.2:8000", interface="en0", kind="network")
        ],
    )
    app = create_app(settings, definitions, adapters, network=network)
    with TestClient(app) as client:
        assert client.get("/v1/admin/connection").status_code == 401
        headers = {"Authorization": "Bearer " + settings.token.get_secret_value()}
        response = client.get("/v1/admin/connection", headers=headers)
        assert response.status_code == 200
        assert response.headers["cache-control"] == "no-store"
        assert response.json()["addresses"][0]["url"] == "http://172.20.10.2:8000"
        assert settings.token.get_secret_value() not in response.text
        assert all(adapter.calls == 0 for adapter in adapters.values())
        with app.state.store.connection() as db:
            assert db.execute("SELECT COUNT(*) FROM budget").fetchone()[0] == 0
        shell = client.get("/admin").text
        assert "network-addresses" in shell
        assert "172.20.10.2" not in shell
        network.status = ConnectionStatus(automatic=True, refresh_seconds=2)
        assert client.get("/v1/admin/connection", headers=headers).json()["addresses"] == []


def test_manual_launch_is_not_misrepresented_as_automatic(settings, definitions, adapters):
    with TestClient(create_app(settings, definitions, adapters)) as client:
        response = client.get(
            "/v1/admin/connection",
            headers={"Authorization": "Bearer " + settings.token.get_secret_value()},
        )
        assert response.json() == ConnectionStatus().model_dump(mode="json")
    assert manual_status(None, None).addresses == []
    assert manual_status("0.0.0.0", 8000).addresses == []
    assert manual_status("172.20.10.2", 8000).addresses[0].kind == "network"
    assert manual_status("169.254.10.2", 8000).addresses[0].kind == "link_local"


async def test_uvicorn_listener_uses_same_app_state_and_does_not_close_requests(monkeypatch):
    network = LocalNetwork(8000, lambda: {})
    config = uvicorn.Config("backend.api:create_app", factory=True)
    server = LocalServer(config, network)
    server.servers = []
    server.lifespan = SimpleNamespace(state={"shared": "app"})
    protocol = Mock(return_value=asyncio.Protocol())
    config.http_protocol_class = protocol
    listener = Mock()
    create = AsyncMock(return_value=listener)
    monkeypatch.setattr(asyncio.get_running_loop(), "create_server", create)
    connection = Mock()
    server.server_state.connections.add(connection)
    assert await server.bind_address("172.20.10.2") is listener
    create.call_args.args[0]()
    assert protocol.call_args.kwargs["server_state"] is server.server_state
    assert protocol.call_args.kwargs["app_state"] is server.lifespan.state
    assert create.call_args.kwargs["host"] == "172.20.10.2"
    server.retire_listener(listener)
    listener.close.assert_called_once()
    assert server.servers == []
    assert not connection.shutdown.called


async def test_monitor_starts_and_cancels_without_restarting_backend_lifespan(monkeypatch):
    network = LocalNetwork(8000, lambda: {})
    server = LocalServer(uvicorn.Config("backend.api:create_app", factory=True), network)
    start = AsyncMock()
    stop = AsyncMock()
    monkeypatch.setattr(uvicorn.Server, "startup", start)
    monkeypatch.setattr(uvicorn.Server, "shutdown", stop)
    await server.startup()
    assert network.status.checked_at is not None
    await server.shutdown()
    assert server.watcher.cancelled()
    start.assert_awaited_once()
    stop.assert_awaited_once()
    server.watcher = None
    await server.shutdown()


async def test_watch_refreshes_until_cancelled(monkeypatch):
    network = LocalNetwork(8000)
    network.refresh = AsyncMock(side_effect=[None, asyncio.CancelledError()])
    sleep = AsyncMock()
    monkeypatch.setattr(asyncio, "sleep", sleep)
    with pytest.raises(asyncio.CancelledError):
        await network.watch()
    assert network.refresh.await_count == 2
    assert sleep.call_args.args == (2,)


async def test_failed_app_startup_never_opens_network_listeners(monkeypatch):
    network = LocalNetwork(8000, Mock(side_effect=AssertionError("Must not discover")))
    server = LocalServer(uvicorn.Config("backend.api:create_app", factory=True), network)

    async def failed_startup(_self, sockets=None):
        _self.should_exit = True

    monkeypatch.setattr(uvicorn.Server, "startup", failed_startup)
    await server.startup()
    assert server.watcher is None
    assert network.listeners == {}


def test_launcher_keeps_one_loopback_owner_and_attaches_network_state(monkeypatch):
    run = Mock()
    monkeypatch.setattr(LocalServer, "run", run)
    monkeypatch.setattr("sys.argv", ["scanpay-serve", "--port", "8001"])
    main()
    run.assert_called_once()
    monkeypatch.setattr("sys.argv", ["scanpay-serve", "--port", "0"])
    with pytest.raises(SystemExit):
        main()
