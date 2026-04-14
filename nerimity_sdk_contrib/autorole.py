"""AutoRolePlugin - assign a role automatically when a member joins.

Usage::

    await bot.plugins.load(AutoRolePlugin(
        server_id="123",
        role_id="456",
    ))
"""
from nerimity_sdk.plugins.manager import PluginBase, listener


class AutoRolePlugin(PluginBase):
    """Assigns a role to every new member that joins."""
    name = "autorole"

    def __init__(self, server_id: str, role_id: str) -> None:
        super().__init__()
        self.server_id = server_id
        self.role_id = role_id

    @listener("server:member_joined")
    async def on_join(self, event) -> None:
        from nerimity_sdk.events.payloads import MemberJoinedEvent
        if not isinstance(event, MemberJoinedEvent):
            return
        if event.server_id != self.server_id:
            return
        try:
            await self.bot.rest.add_role(self.server_id, event.member.user.id, self.role_id)
        except Exception as exc:
            self.bot.logger.error(f"[AutoRole] Failed to assign role: {exc}")
