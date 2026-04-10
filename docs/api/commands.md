# Commands

Commands are functions that run when a user types `/ping` in chat.

`@bot.command` does both at once — it registers the command with Nerimity's `/` slash menu **and** handles the prefix version. You only write the handler once.

```python
@bot.command("ping", description="Check if the bot is alive")
async def ping(ctx):
    await ctx.reply("Pong! 🏓")
```

Users can now trigger this with `/ping`. That's it.

If you want a command that **only** works with the prefix and never appears in the `/` menu:

```python
@bot.command_private("debug", description="Internal debug info")
async def debug(ctx):
    await ctx.reply("secret stuff")
```

`@bot.slash` and `@bot.slash_private` are just aliases:

```python
@bot.slash("ping")           # identical to @bot.command("ping")
@bot.slash_private("debug")  # identical to @bot.command_private("debug")
```

---

## Reading arguments

When a user types `!add 5 10`, the words after the command name are in `ctx.args`:

```python
@bot.command("add")
async def add(ctx):
    # ctx.args = ["5", "10"]  ← raw strings
    a = int(ctx.args[0])
    b = int(ctx.args[1])
    await ctx.reply(f"{a + b}")
```

But doing `int()` yourself is annoying and gives ugly errors. Use **converters** instead:

```python
from nerimity_sdk import Int

@bot.command("add", args=[Int, Int])
async def add(ctx):
    a, b = ctx.args   # already ints — if the user types garbage, they get a friendly error
    await ctx.reply(f"{a + b}")
```

Or even simpler — just use **type annotations** and the SDK figures it out automatically:

```python
@bot.command("add")
async def add(ctx, a: int, b: int):
    await ctx.reply(f"{a + b}")
```

No `args=` needed. The SDK reads the annotations and applies the right converters.

### Available converters

| Converter | What it accepts | What you get |
|---|---|---|
| `Int` | `42`, `-5` | `int` |
| `MemberConverter` | `[@:id]`, user ID, username | `Member` object |
| `UserConverter` | `[@:id]`, user ID | `User` object |
| `ChannelConverter` | channel ID | `Channel` object |

If conversion fails, the bot automatically replies with a friendly error and stops — your function never runs.

---

## Flags

Users can pass named options with `--`:

```
!ban @user --reason="spamming" --silent
```

```python
@bot.command("ban")
async def ban(ctx):
    reason = ctx.flags.get("reason", "No reason given")
    silent = ctx.flags.get("silent", False)
    await ctx.reply(f"Banned. Reason: {reason}")
```

---

## Quoted strings

Quoted arguments are kept together:

```
!echo "hello world"   →   ctx.args = ["hello world"]
!echo hello world     →   ctx.args = ["hello", "world"]
```

---

## Useful options

```python
@bot.command(
    "kick",
    description="Kick a member",   # shown in !help
    usage="<@member> [reason]",     # shown in !help
    category="Moderation",          # groups commands in !help
    aliases=["k"],                  # !k works too
    guild_only=True,                # DMs get a friendly error
    cooldown=5.0,                   # 5 second per-user cooldown
    args=[MemberConverter],         # auto-convert first arg to Member
)
async def kick(ctx):
    member = ctx.args[0]
    await ctx.rest.kick_member(ctx.server_id, member.user.id)
    await ctx.reply(f"Kicked {member.user.username}.")
```

---

## Confirmation prompts

For destructive commands, ask the user to confirm before doing anything:

```python
@bot.command("clear", args=[Int])
async def clear(ctx):
    count = ctx.args[0]

    confirmed = await ctx.confirm(f"Delete {count} messages?")
    if not confirmed:
        return await ctx.reply("Cancelled.")

    msgs = await ctx.fetch_messages(limit=count)
    await ctx.rest.bulk_delete_messages(ctx.channel_id, [m.id for m in msgs])
    await ctx.reply(f"Deleted {len(msgs)} messages.")
```

`ctx.confirm()` sends the prompt, waits for the user to reply yes or no, and returns `True`, `False`, or `None` (timeout).

---

## Multi-step conversations

Ask follow-up questions with `ctx.ask()`:

```python
@bot.command("setup")
async def setup(ctx):
    name = await ctx.ask("What should I call you?", timeout=30)
    if name is None:
        return await ctx.reply("Timed out.")

    await bot.store.set(f"user:{ctx.author.id}:name", name.content)
    await ctx.reply(f"Got it, {name.content}!")
```

---

## Permission checks

Only run a command if the user has the right permissions.

**Shortcut — `requires=`** (recommended):

```python
from nerimity_sdk import Permissions

@bot.command("ban", requires=Permissions.BAN_MEMBERS)
async def ban(ctx):
    ...  # only runs if the user has BAN_MEMBERS
```

Pass multiple permissions as a list:

```python
@bot.command("nuke", requires=[Permissions.BAN_MEMBERS, Permissions.MANAGE_CHANNELS])
async def nuke(ctx): ...
```

**Legacy — `required_user_perms=`** (still works):

```python
@bot.command("ban", required_user_perms=[Permissions.BAN_MEMBERS])
async def ban(ctx): ...
```

---

## Middleware

Middleware runs before your command. Return `False` to stop the command:

```python
async def admins_only(ctx, next):
    if ctx.author.id not in ADMIN_IDS:
        await ctx.reply("Admins only.")
        return False   # ← stops here, command never runs
    await next(ctx)    # ← continue to the command

# Apply to one command:
@bot.command("secret", middleware=[admins_only])
async def secret(ctx): ...

# Apply to all commands:
bot.router.use(admins_only)
```

---

## Auto-generated help

`bot.router.help_text()` builds a help message from your command metadata automatically:

```python
@bot.command("help")
async def help_cmd(ctx):
    await ctx.reply(bot.router.help_text())

# Filter to one category:
    await ctx.reply(bot.router.help_text(category="Moderation"))
```

For long help menus, use the paginator:

```python
from nerimity_sdk import Paginator

@bot.command("help")
async def help_cmd(ctx):
    pages = bot.router.help_text().split("\n\n")
    await Paginator(pages).send(ctx)
```

---

## Error handling

Without this, errors are logged silently. With it, users see a friendly message:

```python
@bot.on_command_error
async def on_error(ctx, error):
    await ctx.reply(f"❌ Something went wrong: {error}")
```
