"""AFKPlugin - /afk <reason>, bot replies to mentions with the AFK message.

Usage::

    await bot.plugins.load(AFKPlugin())

Users run /afk <reason> to go AFK. When someone mentions them, the bot
replies with their AFK message. Sending any message clears AFK status.
"""
from __future__ import annotations
from nerimity_sdk.plugins.manager import PluginBase, listener
from nerimity_sdk.utils.mentions import mention, parse_mention_ids


class AFKPlugin(PluginBase):
    name = "afk"

    def __init__(self) -> None:
        super().__init__()
        # user_id → reason
        self._afk: dict[str, str] = {}

    async def on_load(self) -> None:
        plugin = self

        @self.bot.command("afk", description="Set your AFK status")
        async def afk_cmd(ctx):
            reason = ctx.rest_text or "AFK"
            plugin._afk[ctx.author.id] = reason
            await ctx.reply(f"💤 You are now AFK: *{reason}*")

    @listener("message:created")
    async def on_message(self, event) -> None:
        from nerimity_sdk.events.payloads import MessageCreatedEvent
        if not isinstance(event, MessageCreatedEvent):
            return
        msg = event.message
        uid = msg.created_by.id

        # Clear AFK if the user sends a message
        if uid in self._afk:
            del self._afk[uid]
            try:
                await self.bot.rest.create_message(
                    msg.channel_id, f"✅ Welcome back {mention(uid)}! AFK status cleared."
                )
            except Exception:
                pass
            return

        # Notify if a mentioned user is AFK
        mentioned_ids = parse_mention_ids(msg.content or "")
        for mid in mentioned_ids:
            reason = self._afk.get(mid)
            if reason:
                try:
                    await self.bot.rest.create_message(
                        msg.channel_id,
                        f"💤 {mention(mid)} is AFK: *{reason}*"
                    )
                except Exception:
                    pass
