"""PollPlugin - create a timed poll with reaction counting.

Usage::

    await bot.plugins.load(PollPlugin())

Then in your bot::

    @bot.command("poll", description="Start a poll")
    async def poll(ctx):
        await ctx.bot_plugins["poll"].create(
            ctx,
            question="Should we add a music channel?",
            options=["👍 Yes", "👎 No", "🤷 Maybe"],
            duration=60,   # seconds
        )
"""
from __future__ import annotations
import asyncio
from nerimity_sdk.plugins.manager import PluginBase, listener


class PollPlugin(PluginBase):
    """Timed reaction polls with automatic result tallying."""
    name = "poll"

    def __init__(self) -> None:
        super().__init__()
        # message_id → {emoji: count}
        self._polls: dict[str, dict[str, int]] = {}

    async def create(self, ctx, question: str,
                     options: list[str] | None = None,
                     duration: int = 60) -> None:
        """Send a poll message, react with options, then post results after duration.

        Parameters
        ----------
        ctx:      Command context
        question: The poll question
        options:  List of emoji strings to use as options (default: 👍 👎)
        duration: How long to accept votes, in seconds
        """
        if options is None:
            options = ["👍", "👎"]

        lines = [f"📊 **{question}**", ""]
        for opt in options:
            lines.append(f"{opt}")
        lines += ["", f"⏱️ Poll closes in {duration}s"]

        msg = await ctx.reply("\n".join(lines))
        self._polls[msg.id] = {opt: 0 for opt in options}

        for opt in options:
            await self.bot.rest.add_reaction(msg.channel_id, msg.id, opt)

        await asyncio.sleep(duration)

        # Fetch final counts from cache
        counts = self._polls.pop(msg.id, {})
        result_lines = [f"📊 **{question}** - Results:"]
        for opt, count in sorted(counts.items(), key=lambda x: -x[1]):
            bar = "█" * count + "░" * max(0, 10 - count)
            result_lines.append(f"{opt}  {bar}  {count} vote{'s' if count != 1 else ''}")

        await self.bot.rest.create_message(msg.channel_id, "\n".join(result_lines))

    @listener("message:reaction_added")
    async def on_react(self, event) -> None:
        from nerimity_sdk.events.payloads import ReactionAddedEvent
        if not isinstance(event, ReactionAddedEvent):
            return
        if event.message_id not in self._polls:
            return
        if event.name in self._polls[event.message_id]:
            self._polls[event.message_id][event.name] = event.count

    @listener("message:reaction_removed")
    async def on_unreact(self, event) -> None:
        from nerimity_sdk.events.payloads import ReactionRemovedEvent
        if not isinstance(event, ReactionRemovedEvent):
            return
        if event.message_id not in self._polls:
            return
        if event.name in self._polls[event.message_id]:
            self._polls[event.message_id][event.name] = event.count
