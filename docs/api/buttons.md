# Buttons

## Building buttons

```python
from nerimity_sdk import Button

msg = await ctx.reply(
    "Are you sure?",
    buttons=[
        Button(id="confirm_delete_123", label="✅ Yes, delete"),
        Button(id="cancel_delete_123",  label="❌ Cancel", alert=True),
    ]
)
```

`alert=True` renders the button in red.

> **Note:** Button IDs cannot contain colons (`:`). Use underscores (`_`) as separators instead.

## Handling clicks

```python
@bot.button("confirm:{action}:{target}")
async def on_confirm(bctx):
    action = bctx.params["action"]   # "delete"
    target = bctx.params["target"]   # "123"
    # do the thing...
    await bctx.popup("Done!", f"{action} on {target} completed.")

@bot.button("cancel:{action}:{target}")
async def on_cancel(bctx):
    await bctx.popup("Cancelled", "Nothing was changed.")
```

`bctx.popup(title, content)` shows a modal dialog to the user who clicked - it doesn't post a message in the channel.

`bctx.reply(content)` posts a message in the channel instead.

## TTL (auto-expiry)

```python
@bot.button(f"confirm:{msg.id}", ttl=300)   # expires after 5 minutes
async def on_confirm(bctx):
    ...
```

After the TTL expires the handler is removed and clicks are silently ignored.

## Registering handlers

Use `{name}` segments in patterns to capture dynamic parts:

```python
@bot.button("confirm:{action}:{target}")
async def on_confirm(bctx):
    action = bctx.params["action"]   # e.g. "delete"
    target = bctx.params["target"]   # e.g. "123"
    await bctx.reply(f"Confirmed: {action} on {target}")
```

Wildcard patterns also work:

```python
@bot.button("poll:yes:*")
async def on_yes(bctx): ...
```

### TTL (time-to-live)

Registrations expire after `ttl` seconds. Old buttons stop responding cleanly:

```python
@bot.button("vote:*", ttl=300)   # expires after 5 minutes
async def on_vote(bctx): ...
```

## ButtonContext

| Property | Type | Description |
|---|---|---|
| `bctx.button_id` | `str` | Full button ID |
| `bctx.message_id` | `str` | Message containing the button |
| `bctx.channel_id` | `str` | Channel ID |
| `bctx.server_id` | `str \| None` | Server ID |
| `bctx.user_id` | `str` | User who clicked |
| `bctx.user` | `User \| None` | Resolved from cache |
| `bctx.params` | `dict[str, str]` | Captured pattern segments |

### `await bctx.reply(content)`
Send a message to the channel.

### `await bctx.update_message(content)`
Edit the message that contains the button.

### `await bctx.defer()`
Acknowledge the click silently (no-op placeholder for API parity).

## Error handling

```python
@bot.on_button_error
async def on_button_error(bctx, error):
    await bctx.reply(f"❌ {error}")
```
