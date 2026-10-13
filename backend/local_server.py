"""One API process, with listeners following its private network addresses."""

import argparse
import asyncio
import socket
from contextlib import suppress

import uvicorn

from backend.api import create_app
from backend.local_network import LocalNetwork


class LocalServer(uvicorn.Server):
    def __init__(self, config: uvicorn.Config, network: LocalNetwork) -> None:
        super().__init__(config)
        self.network = network
        self.watcher: asyncio.Task[None] | None = None
        network.bind = self.bind_address
        network.retire = self.retire_listener

    async def bind_address(self, address: str) -> asyncio.Server:
        # Share Uvicorn's protocol, lifespan, connection and request state with loopback.
        def protocol() -> asyncio.Protocol:
            # Config annotates this as Protocol; Uvicorn's loaded HTTP class accepts these.
            return self.config.http_protocol_class(  # type: ignore[call-arg]
                config=self.config,
                server_state=self.server_state,
                app_state=self.lifespan.state,
            )

        server = await asyncio.get_running_loop().create_server(
            protocol, host=address, port=self.network.port, family=socket.AF_INET
        )
        self.servers.append(server)
        return server

    def retire_listener(self, server: asyncio.Server) -> None:
        # Stop accepting at the old address; existing requests/jobs are left running.
        server.close()
        self.servers.remove(server)

    async def startup(self, sockets: list[socket.socket] | None = None) -> None:
        await super().startup(sockets)
        if self.should_exit:
            return
        await self.network.refresh()
        self.watcher = asyncio.create_task(self.network.watch())

    async def shutdown(self, sockets: list[socket.socket] | None = None) -> None:
        if self.watcher:
            self.watcher.cancel()
            with suppress(asyncio.CancelledError):
                await self.watcher
        await super().shutdown(sockets)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    if not 1 <= args.port <= 65535:
        parser.error("port must be between 1 and 65535")
    network = LocalNetwork(args.port)
    app = create_app(network=network)
    config = uvicorn.Config(
        app, host="127.0.0.1", port=args.port, workers=1, access_log=False, proxy_headers=False
    )
    LocalServer(config, network).run()


if __name__ == "__main__":
    main()
