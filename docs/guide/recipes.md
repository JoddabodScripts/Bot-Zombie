# Recipes

Copy-paste these into your bot and change the parts in `ALL_CAPS`.

---

## Welcome new members

```python
@bot.on("server:member_joined")
async def on_join(event):
    await bot.rest.create_message(
        "YOUR_CHANNEL_ID",
        f"👋 Welcome {event.member.user.username} to the server!"
    )
```

---

## React to a message

```python
@bot.command("like", description="React with a thumbs up")
async def like(ctx):
    await ctx.react("👍")
```

---

## Ask the user a follow-up question

```python
@bot.command("name", description="Tell me your name")
async def ask_name(ctx):
    response = await ctx.ask("What's your name?", timeout=30)
    if response is None:
        return await ctx.reply("You took too long!")
    await ctx.reply(f"Nice to meet you, {response.content}!")
```

---

## Ask yes or no

```python
@bot.command("reset", description="Reset your data")
async def reset(ctx):
    confirmed = await ctx.confirm("Are you sure you want to reset everything?")
    if not confirmed:
        return await ctx.reply("Cancelled.")
    # do the reset here
    await ctx.reply("✅ Done!")
```

---

## Send a DM to the user

```python
@bot.command("secret", description="Send you a secret message")
async def secret(ctx):
    await ctx.reply_dm("🤫 This is just for you!")
    await ctx.reply("Check your DMs!")
```

---

## Delete the command message after responding

```python
@bot.command("shh", description="Reply then disappear")
async def shh(ctx):
    await ctx.reply_then_delete("This message will self-destruct in 5 seconds 💣", delay=5)
    await ctx.delete()  # delete the user's command too
```

---

## Send a message with buttons

```python
from nerimity_sdk import Button

@bot.command("vote", description="Quick vote")
async def vote(ctx):
    await ctx.reply(
        "What do you think?",
        buttons=[
            Button(id="vote_yes", label="👍 Yes"),
            Button(id="vote_no",  label="👎 No", alert=True),
        ]
    )

@bot.button("vote_yes")
async def on_yes(bctx):
    await bctx.popup("Thanks!", "You voted Yes 👍")

@bot.button("vote_no")
async def on_no(bctx):
    await bctx.popup("Thanks!", "You voted No 👎")
```

---

## Run something on a schedule

```python
# Requires: pip install "nerimity-sdk[cron]"

@bot.cron("0 9 * * 1")   # Every Monday at 9am UTC
async def monday_message():
    await bot.rest.create_message("YOUR_CHANNEL_ID", "Good morning! Happy Monday 🌅")
```

Cron format: `minute hour day month weekday`
- `"0 9 * * *"` - every day at 9am
- `"*/30 * * * *"` - every 30 minutes
- `"0 12 * * 5"` - every Friday at noon

---

## Kick someone (with confirmation)

```python
from nerimity_sdk import Permissions

@bot.command("kick", description="Kick a member", guild_only=True,
             requires=Permissions.KICK_MEMBERS)
async def kick(ctx):
    if not ctx.mentions:
        return await ctx.reply("Mention someone to kick: /kick @user")
    target = ctx.mentions[0]
    confirmed = await ctx.confirm(f"Kick {target.username}?")
    if not confirmed:
        return await ctx.reply("Cancelled.")
    await ctx.rest.kick_member(ctx.server_id, target.id)
    await ctx.reply(f"👢 Kicked {target.username}.")
```

---

## Store and retrieve per-server settings

```python
@bot.command("setprefix", description="Change the bot prefix", guild_only=True)
async def setprefix(ctx):
    if not ctx.args:
        return await ctx.reply("Usage: /setprefix <new prefix>")
    new = ctx.args[0]
    await bot.store.set(f"prefix:{ctx.server_id}", new)
    await bot.prefix_resolver.set(ctx.server_id, new)
    await ctx.reply(f"✅ Prefix changed to `{new}`")
```

---

## Add a leveling system

```python
from nerimity_sdk_contrib import LevelingPlugin

# In your on_ready or main():
await bot.plugins.load(LevelingPlugin(
    announce_channel_id="YOUR_CHANNEL_ID",
    xp_per_message=10,
    xp_cooldown=60,   # seconds between XP grants
))
# Users now earn XP for chatting.
# /level - shows their level and progress bar
# /leaderboard - shows top 10
```

---

## Auto-welcome with a plugin

```python
from nerimity_sdk_contrib import WelcomePlugin

await bot.plugins.load(WelcomePlugin(
    channel_id="YOUR_CHANNEL_ID",
    message="👋 Welcome {mention} to the server! Say hi!",
))
```

---

## Full minimal bot template

```python
import os
from dotenv import load_dotenv
from nerimity_sdk import Bot

load_dotenv()
bot = Bot(token=os.environ["NERIMITY_TOKEN"])

@bot.on("ready")
async def on_ready(me):
    print(f"✅ {me.username} is online!")

@bot.on_command_error
async def on_error(ctx, error):
    await ctx.reply(f"❌ {error}")

@bot.command("ping", description="Check if the bot is alive")
async def ping(ctx):
    await ctx.reply("Pong! 🏓")

bot.run()
```
