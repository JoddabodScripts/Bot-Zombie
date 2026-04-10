"""CounterPlugin — keeps a channel name updated with a live count.

Usage::

    await bot.plugins.load(CounterPlugin(
        server_id="123",
        channel_id="456",
        label="Members",          # channel will be named "Members: 42"
        interval=300,             # update every 5 minutes
    ))

The count source is the number of cached members for the server by default.
Pass a custom `count_fn` async callable to use any value.
"""
from __future__ import annotations
import asyncio
from typing import Callable, Awaitable
from nerimity_sdk.plugins.manager import PluginBase


class CounterPlugin(PluginBase):
    name = "counter"

    def __init__(self, server_id: str, channel_id: str,
                 label: str = "Members", interval: int = 300,
                 count_fn: Callable[[], Awaitable[int]] | None = None) -> None:
        super().__init__()
        self.server_id = server_id
        self.channel_id = channel_id
        self.label = label
        self.interval = int(interval)
        self._count_fn = count_fn

    async def on_load(self) -> None:
        asyncio.create_task(self._loop())

    async def _loop(self) -> None:
        while True:
            try:
                if self._count_fn:
                    count = await self._count_fn()
                else:
                    server = self.bot.cache.servers.get(self.server_id)
                    count = len(server.members) if server else 0
                await self.bot.rest.request(
                    "PATCH", f"/channels/{self.channel_id}",
                    json={"name": f"{self.label}: {count}"}
                )
            except Exception as exc:
                self.bot.logger.error(f"[Counter] Update failed: {exc}")
            await asyncio.sleep(self.interval)
