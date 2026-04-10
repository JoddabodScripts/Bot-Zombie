# Quick Start

New to Python? No problem! Follow these steps and you'll have a working bot in about 5 minutes.

## 1. Get a token

Your token is like a password that lets your bot log in.

1. Go to [nerimity.com/app/settings/developer/applications](https://nerimity.com/app/settings/developer/applications)
2. Click **New Application**, give it a name
3. Go to the **Bot** tab → click **Add Bot**
4. Copy the token — keep it secret, never share it 🔒

## 2. Install the SDK

Open **Command Prompt** (`Win + R` → type `cmd` → Enter) and run:

```
pip install nerimity-sdk
```

## 3. Create your bot file

Create a new folder somewhere (e.g. `my-bot` on your Desktop), then open Command Prompt in that folder.

> **Tip:** In File Explorer, navigate to your folder, click the address bar, type `cmd`, and press Enter.

Create a file called `bot.py` and paste this in:

```python
import os
from dotenv import load_dotenv
from nerimity_sdk import Bot

load_dotenv()
bot = Bot(token=os.environ["NERIMITY_TOKEN"])

@bot.on("ready")
async def on_ready(me):
    print(f"✅ Logged in as {me.username}!")

@bot.command("ping", description="Check if the bot is alive")
async def ping(ctx):
    await ctx.reply("Pong! 🏓")

bot.run()
```

In the same folder, create a file called `.env` (just `.env`, no other name):

```
NERIMITY_TOKEN=paste_your_token_here
```

## 4. Run it

In Command Prompt:

```
python bot.py
```

You should see `✅ Logged in as YourBot!` in the terminal.

Go to Nerimity and type `/ping` in any channel your bot can see — it should reply **Pong! 🏓**

---

## How it works (the basics)

You don't need to understand all of this right away — just copy the patterns and experiment!

**`@bot.command("name")`** — a *decorator* that tells the SDK "when someone types `/name`, run this function".

**`ctx`** — short for "context". It's passed to every command and holds everything about the message: who sent it, what channel it's in, etc.

**`await ctx.reply("...")`** — sends a message back. The `await` is needed because sending a message takes a moment (it goes over the internet).

---

## Add more commands

Just copy this pattern and change the name and reply:

```python
@bot.command("hello", description="Say hello")
async def hello(ctx):
    await ctx.reply(f"Hello, {ctx.author.username}! 👋")

@bot.command("flip", description="Flip a coin")
async def flip(ctx):
    import random
    result = random.choice(["Heads! 🪙", "Tails! 🪙"])
    await ctx.reply(result)
```

---

## Use what the user typed

`ctx.args` is a list of the words the user typed after the command:

```python
@bot.command("say", description="Repeat something")
async def say(ctx):
    if not ctx.args:
        return await ctx.reply("Type something after /say!")
    await ctx.reply(" ".join(ctx.args))
```

`/say hello world` → bot replies `hello world`

Or use `ctx.rest_text` to get everything as one string:

```python
@bot.command("announce", description="Make an announcement")
async def announce(ctx):
    if not ctx.rest_text:
        return await ctx.reply("Type your announcement after /announce")
    await ctx.reply(f"📢 {ctx.rest_text}")
```

---

## Handle errors nicely

Without this, if something goes wrong the user sees nothing. Add this once near the top of your bot:

```python
@bot.on_command_error
async def on_error(ctx, error):
    await ctx.reply(f"❌ Something went wrong: {error}")
```

---

## Save data between restarts

```python
from nerimity_sdk import Bot, JsonStore

bot = Bot(token=os.environ["NERIMITY_TOKEN"], store=JsonStore("data.json"))

@bot.command("remember", description="Remember something")
async def remember(ctx):
    if not ctx.rest_text:
        return await ctx.reply("Tell me what to remember!")
    await bot.store.set(f"note:{ctx.author.id}", ctx.rest_text)
    await ctx.reply(f"Got it! I'll remember: {ctx.rest_text}")

@bot.command("recall", description="What did I remember?")
async def recall(ctx):
    note = await bot.store.get(f"note:{ctx.author.id}")
    await ctx.reply(note or "I don't have anything saved for you yet.")
```

---

## What's next?

- [Recipes](recipes.md) — copy-paste examples for common bot patterns
- [Commands in depth](../api/commands.md) — all the options for commands
- [Plugins](../api/plugins.md) — split your bot into separate files
- [Example Bot](../example.md) — a complete bot showing everything at once

---

## Linux

Open a terminal and follow the same steps — just use `pip3` if `pip` isn't found, and there's no need for the File Explorer tip.
