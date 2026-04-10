"""ModerationLogPlugin — logs mod actions (kicks, bans, unbans, role changes) to a channel.

Usage::

    await bot.plugins.load(ModerationLogPlugin(log_channel_id="123"))
"""
from nerimity_sdk.plugins.manager import PluginBase, listener
from nerimity_sdk.utils.mentions import mention


class ModerationLogPlugin(PluginBase):
    name = "moderation_log"

    def __init__(self, log_channel_id: str) -> None:
        super().__init__()
        self.log_channel_id = log_channel_id

    async def _log(self, text: str) -> None:
        try:
            await self.bot.rest.create_message(self.log_channel_id, text)
        except Exception as exc:
            self.bot.logger.error(f"[ModerationLog] {exc}")

    @listener("server:member_left")
    async def on_leave(self, event) -> None:
        from nerimity_sdk.events.payloads import MemberLeftEvent
        if not isinstance(event, MemberLeftEvent):
            return
        await self._log(f"🚨 {mention(event.user_id)} left or was removed from server `{event.server_id}`")

    @listener("server:member_updated")
    async def on_member_update(self, event) -> None:
        # role changes come through here
        data = event if isinstance(event, dict) else {}
        uid = data.get("userId") or data.get("user_id")
        sid = data.get("serverId") or data.get("server_id")
        if uid and sid:
            await self._log(f"🔧 Member {mention(uid)} updated in `{sid}`")
