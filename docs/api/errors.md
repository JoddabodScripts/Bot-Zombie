# Error Types

All SDK errors inherit from `NerimitySdkError`. You can catch them specifically or use the error handler decorators on `Bot`.

```python
from nerimity_sdk.errors import (
    NerimitySdkError,
    CommandError,
    PermissionError,
    CooldownError,
    ArgumentError,
    NotFoundError,
    APIError,
)
```

---

## Error hierarchy

```
NerimitySdkError
├── CommandError          # base for all command-related errors
│   ├── PermissionError   # user lacks required permission
│   ├── CooldownError     # command on cooldown
│   ├── ArgumentError     # wrong number or type of arguments
│   └── GuildOnlyError    # command used outside a server
├── APIError              # HTTP error from the Nerimity API
│   ├── NotFoundError     # 404 - resource doesn't exist
│   ├── ForbiddenError    # 403 - bot lacks permission
│   └── RateLimitError    # 429 - rate limited
└── GatewayError          # WebSocket connection error
```

---

## Handling errors

### In command handlers

```python
@bot.on_command_error
async def on_error(ctx, error):
    if isinstance(error, CooldownError):
        await ctx.reply(f"⏳ Try again in {error.retry_after:.1f}s")
    elif isinstance(error, PermissionError):
        await ctx.reply(f"🚫 You need the `{error.permission}` permission.")
    elif isinstance(error, ArgumentError):
        await ctx.reply(f"❌ {error}")
    else:
        await ctx.reply(f"Something went wrong: {error}")
```

### In slash handlers

```python
@bot.on_slash_error
async def on_slash_error(sctx, error):
    await sctx.reply(f"❌ {error}")
```

### In button handlers

```python
@bot.on_button_error
async def on_button_error(bctx, error):
    await bctx.reply(f"❌ {error}")
```

---

## Reference

### `CommandError`
Base class for errors raised inside command handlers.

| Attribute | Type | Description |
|---|---|---|
| `message` | `str` | Human-readable error message |

### `PermissionError`
Raised when `requires=` is set on a command and the user doesn't have it.

| Attribute | Type | Description |
|---|---|---|
| `permission` | `str` | Name of the missing permission |

### `CooldownError`
Raised when a command is invoked before its cooldown expires.

| Attribute | Type | Description |
|---|---|---|
| `retry_after` | `float` | Seconds until the command can be used again |
| `scope` | `str` | `"user"` or `"server"` |

### `ArgumentError`
Raised when argument parsing fails - wrong type, missing required arg, etc.

| Attribute | Type | Description |
|---|---|---|
| `message` | `str` | What went wrong |

### `GuildOnlyError`
Raised when a `guild_only=True` command is used in a DM.

### `APIError`
Raised when the Nerimity API returns an error response.

| Attribute | Type | Description |
|---|---|---|
| `status` | `int` | HTTP status code |
| `message` | `str` | Error message from the API |
| `route` | `str` | The API route that failed |

### `NotFoundError(APIError)`
HTTP 404 - the resource (message, channel, user, etc.) doesn't exist.

### `ForbiddenError(APIError)`
HTTP 403 - the bot doesn't have permission to perform the action.

### `RateLimitError(APIError)`
HTTP 429 - the bot is being rate limited.

| Attribute | Type | Description |
|---|---|---|
| `retry_after` | `float` | Seconds to wait before retrying |

### `GatewayError`
Raised when the WebSocket connection fails or drops unexpectedly.
