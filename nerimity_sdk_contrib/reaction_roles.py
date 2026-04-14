"""ReactionRolesPlugin - persistent reaction roles stored in bot.store.

Unlike RoleMenuPlugin, this survives bot restarts.

Usage::

    plugin = ReactionRolesPlugin()
    await bot.plugins.load(plugin)

    # Add a role mapping at runtime:
    await plugin.add(message_id="123", emoji="👍", role_id="456", server_id="789")
"""
from nerimity_sdk.plugins.manager import PluginBase, listener

_STORE_KEY = "reaction_roles"


class ReactionRolesPlugin(PluginBase):
    name = "reaction_roles"

    def __init__(self) -> None:
        super().__init__()
        # {"msg_id:emoji": {"role_id": ..., "server_id": ...}}
        self._mappings: dict[str, dict] = {}

    async def on_load(self) -> None:
        saved = await self.bot.store.get(_STORE_KEY)
        if isinstance(saved, dict):
            self._mappings = saved

    async def add(self, message_id: str, emoji: str,
                  role_id: str, server_id: str) -> None:
        self._mappings[f"{message_id}:{emoji}"] = {
            "role_id": role_id, "server_id": server_id
        }
        await self.bot.store.set(_STORE_KEY, self._mappings)

    async def remove(self, message_id: str, emoji: str) -> None:
        self._mappings.pop(f"{message_id}:{emoji}", None)
        await self.bot.store.set(_STORE_KEY, self._mappings)

    @listener("message:reaction_added")
    async def on_react(self, event) -> None:
        from nerimity_sdk.events.payloads import ReactionAddedEvent
        if not isinstance(event, ReactionAddedEvent):
            return
        mapping = self._mappings.get(f"{event.message_id}:{event.name}")
        if not mapping:
            return
        try:
            await self.bot.rest.add_role(mapping["server_id"], event.user_id, mapping["role_id"])
        except Exception as exc:
            self.bot.logger.error(f"[ReactionRoles] add_role failed: {exc}")

    @listener("message:reaction_removed")
    async def on_unreact(self, event) -> None:
        from nerimity_sdk.events.payloads import ReactionRemovedEvent
        if not isinstance(event, ReactionRemovedEvent):
            return
        mapping = self._mappings.get(f"{event.message_id}:{event.name}")
        if not mapping:
            return
        try:
            await self.bot.rest.remove_role(mapping["server_id"], event.user_id, mapping["role_id"])
        except Exception as exc:
            self.bot.logger.error(f"[ReactionRoles] remove_role failed: {exc}")
