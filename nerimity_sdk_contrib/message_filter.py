"""MessageFilterPlugin - block links, invites, or custom regex patterns.

Usage::

    await bot.plugins.load(MessageFilterPlugin(
        block_links=True,
        block_invites=True,
        patterns=[r"\\bdiscord\\.gg\\b"],
        log_channel_id="123",
        exempt_roles=["mod_role_id"],
    ))
"""
from __future__ import annotations
import re
from nerimity_sdk.plugins.manager import PluginBase, listener
from nerimity_sdk.utils.mentions import mention

_LINK_RE = re.compile(r"https?://", re.IGNORECASE)
_INVITE_RE = re.compile(r"nerimity\.com/i/", re.IGNORECASE)


class MessageFilterPlugin(PluginBase):
    name = "message_filter"

    def __init__(self, block_links: bool = False, block_invites: bool = False,
                 patterns: list[str] | None = None,
                 log_channel_id: str | None = None,
                 exempt_roles: list[str] | None = None) -> None:
        super().__init__()
        self.block_links = block_links
        self.block_invites = block_invites
        self.log_channel_id = log_channel_id
        self.exempt_roles = set(exempt_roles or [])
        custom = patterns or []
        self._pattern = re.compile("|".join(custom), re.IGNORECASE) if custom else None

    def _is_exempt(self, member) -> bool:
        if not member:
            return False
        return bool(self.exempt_roles & set(member.role_ids))

    @listener("message:created")
    async def on_message(self, event) -> None:
        from nerimity_sdk.events.payloads import MessageCreatedEvent
        if not isinstance(event, MessageCreatedEvent):
            return
        msg = event.message
        content = msg.content or ""
        if self.bot._me and msg.created_by.id == self.bot._me.id:
            return

        # Check exemption
        if msg.server_id:
            member = self.bot.cache.members.get(f"{msg.server_id}:{msg.created_by.id}")
            if self._is_exempt(member):
                return

        reason = None
        if self.block_links and _LINK_RE.search(content):
            reason = "links"
        elif self.block_invites and _INVITE_RE.search(content):
            reason = "invites"
        elif self._pattern and self._pattern.search(content):
            reason = "blocked pattern"

        if not reason:
            return

        await self.bot.rest.delete_message(msg.channel_id, msg.id)
        if self.log_channel_id:
            await self.bot.rest.create_message(
                self.log_channel_id,
                f"🚫 Deleted message from {mention(msg.created_by.id)} ({reason}): ||{content[:200]}||"
            )
