# nerimity-sdk

A Python library for building bots on [Nerimity](https://nerimity.com).

```bash
pip install nerimity-sdk
```

## How it works

You create a `Bot`, attach handlers with decorators, then call `bot.run()`.
The bot connects over a WebSocket, receives events, and dispatches them to your handlers.

```
Nerimity → WebSocket → GatewayClient → EventEmitter → your handlers
```

Everything your handlers need is in the `ctx` object passed to them.

## Quickstart

**Get a token:** [nerimity.com/app/settings/developer/applications](https://nerimity.com/app/settings/developer/applications) → create app → add Bot → copy token.

```bash
nerimity create my-bot
cd my-bot && cp .env.example .env   # open .env and paste token
python bot.py
```

Or manually:

```python
import os
from dotenv import load_dotenv
from nerimity_sdk import Bot

load_dotenv()
bot = Bot(token=os.environ["NERIMITY_TOKEN"], prefix="!") # or make a .env file with this in it NERIMITY_TOKEN=your_token

@bot.on("ready")
async def on_ready(me):
    print(f"Logged in as {me.username}#{me.tag}")

@bot.command("ping", description="Replies with Pong!")
async def ping(ctx):
    await ctx.reply("Pong!")

bot.run()
```

## What's available

| Feature | How to use |
|---|---|
| Event listeners | `@bot.on("message:created")` |
| Prefix + slash commands | `@bot.command("ping")` — works as `!ping` and `/ping` |
| Prefix-only commands | `@bot.command_private("debug")` |
| Argument converters | `args=[Int, MemberConverter]` |
| Confirmation prompts | `await ctx.confirm("Sure?")` |
| Multi-step conversations | `await ctx.ask("Your name?")` |
| DMs | `await ctx.author.send(bot.rest, "Hi!")` |
| Edit messages | `await ctx.edit(msg.id, "updated!")` |
| File uploads | `await ctx.reply_file("image.png")` |
| Paginator | `await Paginator(pages).send(ctx)` |
| Mention helpers | `mention(user_id)` / `ctx.mentions` |
| Webhooks | `await Webhook(token).send("Hello!")` |
| Persistent storage | `JsonStore` / `SqliteStore` / `RedisStore` |
| Scheduled tasks | `@bot.cron("0 9 * * *")` |
| Event waiting (typed) | `await bot.wait_for("member_joined", ...)` |
| Plugins (hot-reload) | `await bot.plugins.load(MyPlugin())` |
| Contrib plugins | `pip install nerimity-sdk-contrib` |
| Error handlers | `@bot.on_command_error` |
| Cooldown feedback | automatic "try again in Xs" message |
| Stale cache detection | `user.stale == True` after reconnect |
| Static analysis | `nerimity lint` |
| Debug mode | `Bot(debug=True)` |
| Auto-reload on save | `Bot(watch=True)` |

See the [Getting Started guide](guide/installation.md) or the [Example Bot](example.md) for a full working example.
