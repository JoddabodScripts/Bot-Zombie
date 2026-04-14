"""TicketPlugin - users DM the bot to open a support ticket; staff reply via DM relay.

How it works:
  1. User sends the bot a DM - a ticket is opened.
  2. Every DM from the user is forwarded to the staff channel.
  3. Staff reply with "!reply <user_id> <message>" to respond.
  4. User sends "!close" or staff uses "!close <user_id>" to close the ticket.

Usage::

    await bot.plugins.load(TicketPlugin(
        staff_channel_id="123",
        open_message="👋 Ticket opened! Staff will reply shortly.",
        close_message="✅ Your ticket has been closed.",
    ))
"""
from __future__ import annotations
from nerimity_sdk.plugins.manager import PluginBase, listener
from nerimity_sdk.utils.mentions import mention


class TicketPlugin(PluginBase):
    """DM-based support ticket system."""
    name = "tickets"

    def __init__(self, staff_channel_id: str,
                 open_message: str = "👋 Ticket opened! Staff will reply shortly.",
                 close_message: str = "✅ Your ticket has been closed.") -> None:
        super().__init__()
        self.staff_channel_id = staff_channel_id
        self.open_message = open_message
        self.close_message = close_message
        # user_id → True (open tickets)
        self._open: set[str] = set()

    @listener("message:created")
    async def on_message(self, event) -> None:
        from nerimity_sdk.events.payloads import MessageCreatedEvent
        if not isinstance(event, MessageCreatedEvent):
            return
        msg = event.message
        uid = msg.created_by.id

        # Ignore bot's own messages
        if self.bot._me and uid == self.bot._me.id:
            return

        # ── DM from user (no server_id) ──────────────────────────────────────
        if not msg.server_id:
            content = (msg.content or "").strip()

            if content.lower() == "!close" and uid in self._open:
                self._open.discard(uid)
                await self.bot.rest.create_message(msg.channel_id, self.close_message)
                await self.bot.rest.create_message(
                    self.staff_channel_id,
                    f"🔒 Ticket closed by {mention(uid)} (`{uid}`)"
                )
                return

            if uid not in self._open:
                self._open.add(uid)
                await self.bot.rest.create_message(msg.channel_id, self.open_message)

            # Forward to staff channel
            username = msg.created_by.username
            await self.bot.rest.create_message(
                self.staff_channel_id,
                f"📩 **Ticket** from {mention(uid)} (`{uid}` - {username}):\n{content}\n"
                f"_Reply: `!reply {uid} <message>` | Close: `!close {uid}`_"
            )
            return

        # ── Staff commands in staff channel ───────────────────────────────────
        if msg.channel_id != self.staff_channel_id:
            return

        content = (msg.content or "").strip()

        if content.startswith("!reply "):
            parts = content[7:].split(None, 1)
            if len(parts) < 2:
                return
            target_uid, reply_text = parts
            if target_uid not in self._open:
                await self.bot.rest.create_message(
                    self.staff_channel_id, f"⚠️ No open ticket for `{target_uid}`."
                )
                return
            channel_data = await self.bot.rest.open_dm(target_uid)
            await self.bot.rest.create_message(channel_data["id"], f"**Staff:** {reply_text}")

        elif content.startswith("!close "):
            target_uid = content[7:].strip()
            if target_uid in self._open:
                self._open.discard(target_uid)
                channel_data = await self.bot.rest.open_dm(target_uid)
                await self.bot.rest.create_message(channel_data["id"], self.close_message)
                await self.bot.rest.create_message(
                    self.staff_channel_id,
                    f"🔒 Ticket for `{target_uid}` closed by staff."
                )
