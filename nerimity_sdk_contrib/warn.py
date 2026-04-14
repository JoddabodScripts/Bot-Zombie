"""WarnPlugin - /warn @user <reason>, stores warnings, auto-kicks at threshold.

Usage::

    await bot.plugins.load(WarnPlugin(
        threshold=3,          # kicks at 3 warnings
        log_channel_id="123", # optional
    ))
"""
from __future__ import annotations
from nerimity_sdk.plugins.manager import PluginBase
from nerimity_sdk.utils.mentions import mention, parse_mention_ids

_STORE_PREFIX = "warns"


class WarnPlugin(PluginBase):
    name = "warns"

    def __init__(self, threshold: int = 3,
                 log_channel_id: str | None = None) -> None:
        super().__init__()
        self.threshold = int(threshold)
        self.log_channel_id = log_channel_id

    async def _get_warns(self, server_id: str, user_id: str) -> list:
        return (await self.bot.store.get(f"{_STORE_PREFIX}:{server_id}:{user_id}")) or []

    async def _set_warns(self, server_id: str, user_id: str, warns: list) -> None:
        await self.bot.store.set(f"{_STORE_PREFIX}:{server_id}:{user_id}", warns)

    async def on_load(self) -> None:
        plugin = self

        @self.bot.command("warn", description="Warn a user",
                          usage="<@user> <reason>", guild_only=True)
        async def warn_cmd(ctx):
            ids = parse_mention_ids(ctx.message.content or "")
            if not ids:
                return await ctx.reply("Usage: /warn @user <reason>")
            target_id = ids[0]
            reason = ctx.rest_text or "No reason given"
            warns = await plugin._get_warns(ctx.server_id, target_id)
            warns.append({"reason": reason, "by": ctx.author.id})
            await plugin._set_warns(ctx.server_id, target_id, warns)
            count = len(warns)
            msg = f"⚠️ {mention(target_id)} warned ({count}/{plugin.threshold}): {reason}"
            await ctx.reply(msg)
            if plugin.log_channel_id:
                await plugin.bot.rest.create_message(plugin.log_channel_id, msg)
            if count >= plugin.threshold:
                await plugin.bot.rest.kick_member(ctx.server_id, target_id)
                await plugin._set_warns(ctx.server_id, target_id, [])
                kick_msg = f"🚨 {mention(target_id)} was kicked after {count} warnings."
                await ctx.reply(kick_msg)
                if plugin.log_channel_id:
                    await plugin.bot.rest.create_message(plugin.log_channel_id, kick_msg)

        @self.bot.command("warnings", description="Show warnings for a user",
                          usage="<@user>", guild_only=True)
        async def warnings_cmd(ctx):
            ids = parse_mention_ids(ctx.message.content or "")
            if not ids:
                return await ctx.reply("Usage: /warnings @user")
            target_id = ids[0]
            warns = await plugin._get_warns(ctx.server_id, target_id)
            if not warns:
                return await ctx.reply(f"{mention(target_id)} has no warnings.")
            lines = [f"⚠️ **Warnings for {mention(target_id)}** ({len(warns)}):"]
            for i, w in enumerate(warns, 1):
                lines.append(f"  {i}. {w['reason']} (by {mention(w['by'])})")
            await ctx.reply("\n".join(lines))

        @self.bot.command("clearwarns", description="Clear all warnings for a user",
                          usage="<@user>", guild_only=True)
        async def clearwarns_cmd(ctx):
            ids = parse_mention_ids(ctx.message.content or "")
            if not ids:
                return await ctx.reply("Usage: /clearwarns @user")
            target_id = ids[0]
            await plugin._set_warns(ctx.server_id, target_id, [])
            await ctx.reply(f"✅ Cleared all warnings for {mention(target_id)}.")
