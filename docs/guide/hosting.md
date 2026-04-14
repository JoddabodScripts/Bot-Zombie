# Keeping Your Bot Online 24/7

Running `python bot.py` on your PC works for testing, but the bot goes offline when you close the terminal or shut down your computer. Here's how to keep it running permanently.

---

## Option 1 - Railway (easiest, free tier available)

[Railway](https://railway.app) lets you deploy your bot in a few clicks with no server knowledge needed.

1. Push your bot code to a GitHub repo (make sure `.env` is in `.gitignore` - never commit your token!)
2. Go to [railway.app](https://railway.app) and sign in with GitHub
3. Click **New Project → Deploy from GitHub repo** and select your repo
4. Go to your project's **Variables** tab and add `NERIMITY_TOKEN` with your token
5. Railway will build and start your bot automatically

Your bot will stay online as long as your Railway project is active.

---

## Option 2 - A VPS (more control)

A cheap VPS (Virtual Private Server) gives you a Linux machine in the cloud that runs 24/7. Good options:

- [Hetzner](https://www.hetzner.com) - very cheap, starts around €4/month
- [DigitalOcean](https://www.digitalocean.com) - beginner-friendly, starts at $4/month
- [Oracle Cloud](https://www.oracle.com/cloud/free/) - has a free tier

Once you have a VPS, connect via SSH, install Python, upload your bot files, and run it with a process manager like `screen` or `pm2` so it keeps running after you disconnect:

```bash
pip install nerimity-sdk
screen -S mybot
python bot.py
# Press Ctrl+A then D to detach - bot keeps running in the background
```

---

## Option 3 - Run it on your PC with auto-start (Windows)

If your PC is always on, you can make the bot start automatically with Windows:

1. Press `Win + R`, type `shell:startup`, press Enter
2. Create a `.bat` file in that folder with this content:

```
@echo off
cd C:\path\to\your\bot
python bot.py
```

Replace `C:\path\to\your\bot` with the actual path to your bot folder. The bot will start every time Windows boots.

---

## Important: never commit your token

Whichever option you use, keep your token out of your code and out of GitHub. Always use a `.env` file locally and environment variables on your hosting platform.
