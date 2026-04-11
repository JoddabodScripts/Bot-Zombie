# REST Client

`bot.rest` gives you direct access to the Nerimity HTTP API. All methods are async and return typed objects.

```python
await bot.rest.send_message(channel_id, "Hello!")
```

You can also set a custom timeout (default is 30s):

```python
bot.rest.timeout = 60.0
```

---

## Messages

### `await bot.rest.send_message(channel_id, content, *, embed=None, buttons=None, silent=False)`
Send a message to a channel. Returns `Message`.

### `await bot.rest.edit_message(channel_id, message_id, content=None, *, embed=None, buttons=None)`
Edit one of the bot's own messages. Returns `Message`.

### `await bot.rest.delete_message(channel_id, message_id)`
Delete a message.

### `await bot.rest.fetch_message(channel_id, message_id)`
Fetch a single message by ID. Returns `Message`.

### `await bot.rest.fetch_messages(channel_id, *, limit=50, before=None, after=None)`
Fetch a list of messages. Returns `list[Message]`.

### `await bot.rest.pin_message(channel_id, message_id)`
Pin a message in a channel.

### `await bot.rest.add_reaction(channel_id, message_id, emoji, emoji_id=None)`
Add a reaction to a message.

### `await bot.rest.remove_reaction(channel_id, message_id, emoji, emoji_id=None)`
Remove a reaction from a message.

---

## Channels

### `await bot.rest.fetch_channel(channel_id)`
Fetch a channel by ID. Returns `Channel`.

### `await bot.rest.create_channel(server_id, name, *, type="TEXT", category_id=None)`
Create a new channel in a server. Returns `Channel`.

### `await bot.rest.delete_channel(channel_id)`
Delete a channel.

### `await bot.rest.update_channel(channel_id, *, name=None, topic=None)`
Update a channel's name or topic. Returns `Channel`.

---

## Servers

### `await bot.rest.fetch_server(server_id)`
Fetch a server by ID. Returns `Server`.

### `await bot.rest.fetch_server_members(server_id)`
Fetch all members of a server. Returns `list[Member]`.

---

## Members

### `await bot.rest.fetch_member(server_id, user_id)`
Fetch a single member. Returns `Member`.

### `await bot.rest.kick_member(server_id, user_id)`
Kick a member from a server.

### `await bot.rest.ban_member(server_id, user_id)`
Ban a member from a server.

### `await bot.rest.unban_member(server_id, user_id)`
Remove a ban.

### `await bot.rest.fetch_bans(server_id)`
Fetch all bans for a server. Returns `list[Ban]`.

### `await bot.rest.set_nickname(server_id, user_id, nickname)`
Set a member's nickname. Pass `None` to reset.

### `await bot.rest.add_role(server_id, user_id, role_id)`
Assign a single role to a member.

### `await bot.rest.remove_role(server_id, user_id, role_id)`
Remove a role from a member.

### `await bot.rest.add_roles(server_id, user_id, role_ids)`
Assign multiple roles at once. More efficient than calling `add_role` in a loop.

```python
await bot.rest.add_roles(server_id, user_id, ["role1", "role2", "role3"])
```

---

## Roles

### `await bot.rest.create_role(server_id, name, *, hex_color=None, permissions=None)`
Create a new role. Returns `Role`.

### `await bot.rest.delete_role(server_id, role_id)`
Delete a role.

### `await bot.rest.update_role(server_id, role_id, *, name=None, hex_color=None, permissions=None)`
Update a role. Returns `Role`.

---

## Users

### `await bot.rest.fetch_user(user_id)`
Fetch a user by ID. Returns `User`.

---

## Slash commands

### `await bot.rest.register_slash_command(name, description, options=None)`
Manually register a slash command globally. Usually handled automatically.

### `await bot.rest.delete_slash_command(command_id)`
Delete a registered slash command.
