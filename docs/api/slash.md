# Slash Commands

Slash commands in nerimity-sdk are the same as prefix commands — `@bot.slash` is an alias for `@bot.command`.

```python
@bot.command("ban", description="Ban a user")
async def ban(ctx):
    ...
```

This registers `/ban` in Nerimity's slash menu **and** handles `!ban`. You don't need a separate slash handler.

## `@bot.slash` alias

If you prefer the explicit name:

```python
@bot.slash("ban", description="Ban a user")
async def ban(ctx):
    ...
```

Identical behaviour.

## Hiding from the slash menu

Use `@bot.command_private` (or `@bot.slash_private`) to keep a command prefix-only:

```python
@bot.command_private("debug")
async def debug(ctx):
    await ctx.reply("internal info")
```

This never appears in the `/` menu.

## SlashContext vs Context

There is no separate `SlashContext` — slash and prefix invocations both receive the same `Context` object. See [Context](context.md) for the full reference.

## Registration

Public commands are automatically synced to Nerimity's API on bot ready. You'll see:

```
[Bot] Synced 3 command(s): ['ping', 'ban', 'kick']
```

in the logs when it works.
