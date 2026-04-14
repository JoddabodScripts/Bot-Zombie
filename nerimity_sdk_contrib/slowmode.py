"""SlowmodePlugin - per-channel message rate limiting enforced by the bot.

Usage::

    await bot.plugins.load(SlowmodePlugin())

Then use the auto-registered commands::

    /slowmode set <channel_id> <seconds>
    /slowmode off <channel_id>
"""
from __future__ import annotations
import time
from nerimity_sdk.plugins.manager import PluginBase, listener


class SlowmodePlugin(PluginBase):
    name = "slowmode"

    def __init__(self) -> None:
        super().__init__()
        # channel_id → seconds
        self._limits: dict[str, float] = {}
        # "channel_id:user_id" → last message timestamp
        self._last: dict[str, float] = {}

    async def on_load(self) -> None:
        plugin = self

        @self.bot.command("slowmode", description="Set or remove slowmode for a channel",
                          usage="<set <channel_id> <seconds>> | <off <channel_id>>")
        async def slowmode_cmd(ctx):
            if not ctx.args:
                return await ctx.reply("Usage: /slowmode set <channel_id> <seconds> | /slowmode off <channel_id>")
            sub = ctx.args[0].lower()
            if sub == "set" and len(ctx.args) >= 3:
                channel_id = ctx.args[1]
                try:
                    seconds = float(ctx.args[2])
                except ValueError:
                    return await ctx.reply("Seconds must be a number.")
                plugin._limits[channel_id] = seconds
                await ctx.reply(f"⏱ Slowmode set to {seconds}s in <#{channel_id}>")
            elif sub == "off" and len(ctx.args) >= 2:
                plugin._limits.pop(ctx.args[1], None)
                await ctx.reply(f"✅ Slowmode removed from <#{ctx.args[1]}>")
            else:
                await ctx.reply("Usage: /slowmode set <channel_id> <seconds> | /slowmode off <channel_id>")

    @listener("message:created")
    async def on_message(self, event) -> None:
        from nerimity_sdk.events.payloads import MessageCreatedEvent
        if not isinstance(event, MessageCreatedEvent):
            return
        msg = event.message
        limit = self._limits.get(msg.channel_id)
        if not limit:
            return
        if self.bot._me and msg.created_by.id == self.bot._me.id:
            return
        key = f"{msg.channel_id}:{msg.created_by.id}"
        now = time.monotonic()
        last = self._last.get(key, 0)
        if now - last < limit:
            await self.bot.rest.delete_message(msg.channel_id, msg.id)
            return
        self._last[key] = now
