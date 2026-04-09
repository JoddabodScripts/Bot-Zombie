"""RoleMenuPlugin — react to a message to get a role, unreact to remove it.

Usage::

    await bot.plugins.load(RoleMenuPlugin(
        message_id="123",
        roles={
            "👍": "role_id_1",
            "🎮": "role_id_2",
            "🎨": "role_id_3",
        }
    ))

The bot must have MANAGE_ROLES permission in the server.
"""
from nerimity_sdk.plugins.manager import PluginBase, listener


class RoleMenuPlugin(PluginBase):
    """Assign/remove roles based on reactions to a specific message.

    Parameters
    ----------
    message_id: The ID of the role menu message to watch
    roles:      Dict mapping emoji → role_id
    """
    name = "role_menu"

    def __init__(self, message_id: str, roles: dict[str, str]) -> None:
        super().__init__()
        self.message_id = message_id
        self.roles = roles  # {"👍": "role_id", ...}

    @listener("message:reaction_added")
    async def on_react(self, event) -> None:
        from nerimity_sdk.events.payloads import ReactionAddedEvent
        if not isinstance(event, ReactionAddedEvent):
            return
        if event.message_id != self.message_id:
            return
        role_id = self.roles.get(event.name)
        if not role_id:
            return
        msg = self.bot.cache.messages.get(self.message_id)
        server_id = msg.server_id if msg else None
        if not server_id:
            return
        await self.bot.rest.add_role(server_id, event.user_id, role_id)

    @listener("message:reaction_removed")
    async def on_unreact(self, event) -> None:
        from nerimity_sdk.events.payloads import ReactionRemovedEvent
        if not isinstance(event, ReactionRemovedEvent):
            return
        if event.message_id != self.message_id:
            return
        role_id = self.roles.get(event.name)
        if not role_id:
            return
        msg = self.bot.cache.messages.get(self.message_id)
        server_id = msg.server_id if msg else None
        if not server_id:
            return
        await self.bot.rest.remove_role(server_id, event.user_id, role_id)
