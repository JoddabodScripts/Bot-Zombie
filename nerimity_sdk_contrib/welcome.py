from nerimity_sdk.plugins.manager import PluginBase, listener
from nerimity_sdk.utils.mentions import mention


class WelcomePlugin(PluginBase):
    """Sends a welcome message when a member joins.

    Usage::

        await bot.plugins.load(WelcomePlugin(
            channel_id="123",
            message="👋 Welcome {mention} to the server!",
        ))

    Template variables: {mention}, {username}, {tag}
    """
    name = "welcome"

    def __init__(self, channel_id: str,
                 message: str = "👋 Welcome {mention}!") -> None:
        super().__init__()
        self.channel_id = channel_id
        self.message_template = message

    @listener("server:member_joined")
    async def on_join(self, event) -> None:
        from nerimity_sdk.events.payloads import MemberJoinedEvent
        if not isinstance(event, MemberJoinedEvent):
            return
        user = event.member.user
        text = (self.message_template
                .replace("{mention}", mention(user.id))
                .replace("{username}", user.username)
                .replace("{tag}", user.tag))
        await self.bot.rest.create_message(self.channel_id, text)
