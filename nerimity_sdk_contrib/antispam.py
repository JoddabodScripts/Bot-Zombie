"""AntiSpamPlugin - rate-limit messages per user, auto-mute/kick on threshold.

Usage::

    await bot.plugins.load(AntiSpamPlugin(
        max_messages=5,      # messages allowed per window
        window=5.0,          # seconds
        action="kick",       # "kick", "ban", or "delete"
        log_channel_id="123",
    ))
"""
from __future__ import annotations
import time
from collections import defaultdict
from nerimity_sdk.plugins.manager import PluginBase, listener
from nerimity_sdk.utils.mentions import mention


class AntiSpamPlugin(PluginBase):
    """Detects message spam and kicks/bans/deletes accordingly."""
    name = "antispam"

    def __init__(self, max_messages: int = 5, window: float = 5.0,
                 action: str = "kick", log_channel_id: str | None = None) -> None:
        super().__init__()
        self.max_messages = max_messages
        self.window = window
        self.action = action
        self.log_channel_id = log_channel_id
        # user_id → list of timestamps
        self._buckets: dict[str, list[float]] = defaultdict(list)

    @listener("message:created")
    async def on_message(self, event) -> None:
        from nerimity_sdk.events.payloads import MessageCreatedEvent
        if not isinstance(event, MessageCreatedEvent):
            return
        msg = event.message
        if not msg.server_id:
            return

        uid = msg.created_by.id
        now = time.monotonic()
        bucket = self._buckets[uid]
        # Prune old timestamps outside the window
        self._buckets[uid] = [t for t in bucket if now - t < self.window]
        self._buckets[uid].append(now)

        if len(self._buckets[uid]) <= self.max_messages:
            return

        # Threshold exceeded
        self._buckets[uid].clear()
        log = f"🚨 AntiSpam: {mention(uid)} triggered spam filter in {msg.server_id}"

        if self.action == "delete":
            await self.bot.rest.delete_message(msg.channel_id, msg.id)
        elif self.action == "kick":
            await self.bot.rest.kick_member(msg.server_id, uid)
            log += " - kicked"
        elif self.action == "ban":
            await self.bot.rest.ban_member(msg.server_id, uid)
            log += " - banned"

        if self.log_channel_id:
            await self.bot.rest.create_message(self.log_channel_id, log)
