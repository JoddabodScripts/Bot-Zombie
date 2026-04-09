import re
from nerimity_sdk.plugins.manager import PluginBase, listener
from nerimity_sdk.utils.mentions import mention


class AutoModPlugin(PluginBase):
    """Deletes messages containing blocked words or regex patterns.

    Usage::

        await bot.plugins.load(AutoModPlugin(
            blocked=["badword", r"\\bspam+\\b"],
            log_channel_id="123",   # optional
        ))
    """
    name = "automod"

    def __init__(self, blocked: list[str],
                 log_channel_id: str | None = None) -> None:
        super().__init__()
        self._pattern = re.compile("|".join(blocked), re.IGNORECASE)
        self.log_channel_id = log_channel_id

    @listener("message:created")
    async def on_message(self, event) -> None:
        from nerimity_sdk.events.payloads import MessageCreatedEvent
        if not isinstance(event, MessageCreatedEvent):
            return
        msg = event.message
        if not self._pattern.search(msg.content or ""):
            return
        await self.bot.rest.delete_message(msg.channel_id, msg.id)
        if self.log_channel_id:
            await self.bot.rest.create_message(
                self.log_channel_id,
                f"🚫 Deleted message from {mention(msg.created_by.id)}: ||{msg.content}||"
            )
