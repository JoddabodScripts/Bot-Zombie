"""SuggestionPlugin — /suggest <idea>, posts to a suggestions channel with reactions.

Usage::

    await bot.plugins.load(SuggestionPlugin(
        channel_id="123",
        upvote="👍",
        downvote="👎",
    ))
"""
from nerimity_sdk.plugins.manager import PluginBase
from nerimity_sdk.utils.mentions import mention


class SuggestionPlugin(PluginBase):
    name = "suggestions"

    def __init__(self, channel_id: str,
                 upvote: str = "👍", downvote: str = "👎") -> None:
        super().__init__()
        self.channel_id = channel_id
        self.upvote = upvote
        self.downvote = downvote

    async def on_load(self) -> None:
        plugin = self

        @self.bot.command("suggest", description="Submit a suggestion")
        async def suggest_cmd(ctx):
            if not ctx.rest_text:
                return await ctx.reply("Usage: /suggest <your idea>")
            msg = await self.bot.rest.create_message(
                plugin.channel_id,
                f"💡 **Suggestion** from {mention(ctx.author.id)}:\n{ctx.rest_text}"
            )
            await self.bot.rest.add_reaction(plugin.channel_id, msg["id"], plugin.upvote)
            await self.bot.rest.add_reaction(plugin.channel_id, msg["id"], plugin.downvote)
            await ctx.reply("✅ Suggestion submitted!")
