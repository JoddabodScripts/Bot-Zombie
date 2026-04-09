from nerimity_sdk.plugins.manager import PluginBase, listener
from nerimity_sdk.utils.mentions import mention


class StarboardPlugin(PluginBase):
    """Reposts highly-reacted messages to a starboard channel.

    Usage::

        await bot.plugins.load(StarboardPlugin(
            channel_id="123",
            emoji="⭐",
            threshold=3,
        ))
    """
    name = "starboard"

    def __init__(self, channel_id: str, emoji: str = "⭐",
                 threshold: int = 3) -> None:
        super().__init__()
        self.channel_id = channel_id
        self.emoji = emoji
        self.threshold = threshold
        self._posted: set[str] = set()

    @listener("message:reaction_added")
    async def on_reaction(self, event) -> None:
        from nerimity_sdk.events.payloads import ReactionAddedEvent
        if not isinstance(event, ReactionAddedEvent):
            return
        if event.name != self.emoji or event.count < self.threshold:
            return
        if event.message_id in self._posted:
            return
        self._posted.add(event.message_id)
        msg = self.bot.cache.messages.get(event.message_id)
        content = msg.content if msg else f"(message {event.message_id})"
        author = mention(msg.created_by.id) if msg else "unknown"
        await self.bot.rest.create_message(
            self.channel_id,
            f"{self.emoji} **{event.count}** | {author}\n{content}"
        )
