"""BirthdayPlugin - users set their birthday, bot announces on the day.

Usage::

    await bot.plugins.load(BirthdayPlugin(
        announce_channel_id="123",
    ))

Users set their birthday with the auto-registered /birthday command.
Birthdays stored as "birthday:{user_id}" = "MM-DD" in bot.store.
"""
from __future__ import annotations
import asyncio
from datetime import datetime, timezone
from nerimity_sdk.plugins.manager import PluginBase
from nerimity_sdk.utils.mentions import mention


class BirthdayPlugin(PluginBase):
    name = "birthday"

    def __init__(self, announce_channel_id: str,
                 message: str = "🎂 Happy Birthday {mention}!") -> None:
        super().__init__()
        self.announce_channel_id = announce_channel_id
        self.message_template = message

    async def on_load(self) -> None:
        plugin = self

        @self.bot.command("birthday", description="Set your birthday (MM-DD)")
        async def birthday_cmd(ctx):
            if not ctx.args:
                return await ctx.reply("Usage: /birthday MM-DD  e.g. /birthday 04-20")
            value = ctx.args[0]
            try:
                datetime.strptime(value, "%m-%d")
            except ValueError:
                return await ctx.reply("Invalid format. Use MM-DD e.g. `04-20`.")
            await plugin.bot.store.set(f"birthday:{ctx.author.id}", value)
            await ctx.reply(f"🎂 Birthday set to {value}!")

        asyncio.create_task(self._daily_loop())

    async def _daily_loop(self) -> None:
        while True:
            now = datetime.now(timezone.utc)
            today = now.strftime("%m-%d")
            # Check all stored birthdays
            keys = await self.bot.store.keys("birthday:*")
            for key in keys:
                val = await self.bot.store.get(key)
                if val == today:
                    uid = key.split(":", 1)[1]
                    text = self.message_template.replace("{mention}", mention(uid))
                    try:
                        await self.bot.rest.create_message(self.announce_channel_id, text)
                    except Exception:
                        pass
            # Sleep until next midnight UTC
            seconds_until_midnight = 86400 - (now.hour * 3600 + now.minute * 60 + now.second)
            await asyncio.sleep(seconds_until_midnight)
