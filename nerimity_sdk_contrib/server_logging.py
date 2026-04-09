from nerimity_sdk.plugins.manager import PluginBase, listener
from nerimity_sdk.utils.mentions import mention


class LoggingPlugin(PluginBase):
    """Logs server events to a channel: joins, leaves, deletes, edits.

    Usage::

        await bot.plugins.load(LoggingPlugin(channel_id="123"))
    """
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
