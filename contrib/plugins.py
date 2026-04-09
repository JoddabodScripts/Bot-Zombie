"""
nerimity-sdk contrib plugins
============================
Copy any of these into your plugins/ folder, or install nerimity-sdk-contrib.

Usage:
    from contrib.plugins import WelcomePlugin, AutoModPlugin, StarboardPlugin, LoggingPlugin
    await bot.plugins.load(WelcomePlugin(channel_id="123"))
"""
from __future__ import annotations
from nerimity_sdk.plugins.manager import PluginBase, listener
from nerimity_sdk.utils.mentions import mention


class WelcomePlugin(PluginBase):
    """Sends a welcome message when a member joins."""
    name = "welcome"

    def __init__(self, channel_id: str, message: str = "👋 Welcome {mention}!") -> None:
        super().__init__()
        self.channel_id = channel_id
        self.message_template = message

    @listener("server:member_joined")
    async def on_join(self, event) -> None:
        from nerimity_sdk.events.payloads import MemberJoinedEvent
        if not isinstance(event, MemberJoinedEvent):
            return
        text = self.message_template.replace("{mention}", mention(event.member.user.id))
        await self.bot.rest.create_message(self.channel_id, text)


class AutoModPlugin(PluginBase):
    """Deletes messages containing blocked words/patterns."""
    name = "automod"

    def __init__(self, blocked: list[str], log_channel_id: str | None = None) -> None:
        super().__init__()
        import re
        self._pattern = re.compile("|".join(re.escape(w) for w in blocked), re.IGNORECASE)
        self.log_channel_id = log_channel_id

    @listener("message:created")
    async def on_message(self, event) -> None:
        from nerimity_sdk.events.payloads import MessageCreatedEvent
        if not isinstance(event, MessageCreatedEvent):
            return
        msg = event.message
        if self._pattern.search(msg.content or ""):
            await self.bot.rest.delete_message(msg.channel_id, msg.id)
            if self.log_channel_id:
                await self.bot.rest.create_message(
                    self.log_channel_id,
                    f"🚫 Deleted message from {mention(msg.created_by.id)}: ||{msg.content}||"
                )


class StarboardPlugin(PluginBase):
    """Reposts messages that reach a reaction threshold to a starboard channel."""
    name = "starboard"

    def __init__(self, channel_id: str, emoji: str = "⭐", threshold: int = 3) -> None:
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
        if event.name != self.emoji:
            return
        if event.count < self.threshold:
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


class LoggingPlugin(PluginBase):
    """Logs server events (joins, leaves, deletes, edits) to a channel."""
    name = "logging"

    def __init__(self, channel_id: str) -> None:
        super().__init__()
        self.channel_id = channel_id

    async def _log(self, text: str) -> None:
        await self.bot.rest.create_message(self.channel_id, text)

    @listener("server:member_joined")
    async def on_join(self, event) -> None:
        from nerimity_sdk.events.payloads import MemberJoinedEvent
        if isinstance(event, MemberJoinedEvent):
            await self._log(f"➡️ {mention(event.member.user.id)} joined")

    @listener("server:member_left")
    async def on_leave(self, event) -> None:
        from nerimity_sdk.events.payloads import MemberLeftEvent
        if isinstance(event, MemberLeftEvent):
            await self._log(f"⬅️ <user {event.user_id}> left")

    @listener("message:deleted")
    async def on_delete(self, event) -> None:
        from nerimity_sdk.events.payloads import MessageDeletedEvent
        if isinstance(event, MessageDeletedEvent):
            msg = self.bot.cache.messages.get(event.message_id)
            content = f"||{msg.content}||" if msg else f"(id: {event.message_id})"
            await self._log(f"🗑️ Message deleted in <#{event.channel_id}>: {content}")

    @listener("message:updated")
    async def on_edit(self, event) -> None:
        from nerimity_sdk.events.payloads import MessageUpdatedEvent
        if isinstance(event, MessageUpdatedEvent):
            new = event.updated.get("content", "")
            await self._log(f"✏️ Message edited in <#{event.channel_id}>: {new}")
