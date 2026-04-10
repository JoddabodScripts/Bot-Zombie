# Troubleshooting

Common problems and how to fix them.

---

## "python is not recognized" or "pip is not recognized"

Python isn't on your PATH. Two options:

**Option 1 — Reinstall Python with PATH enabled:**
1. Uninstall Python from **Settings → Apps**
2. Re-download from [python.org/downloads](https://www.python.org/downloads/)
3. Run the installer and **check "Add Python to PATH"** before clicking Install

**Option 2 — Try `py` instead:**
```
py -m pip install nerimity-sdk
py bot.py
```

---

## Bot is online but slash commands aren't showing up

Slash commands can take up to a minute to register after the bot starts. Wait a bit, then try again.

If they still don't appear, make sure your bot has been added to the server with the correct permissions.

---

## Bot is online but not responding to commands

- Make sure you're typing the command in a channel the bot can see
- Check the terminal for any error messages
- Make sure `bot.run()` is at the bottom of your file

---

## `ModuleNotFoundError: No module named 'nerimity_sdk'`

The SDK isn't installed in the Python environment you're running. Try:

```
pip install nerimity-sdk
```

If you have multiple Python versions installed, make sure you're using the same one for both `pip` and `python`.

---

## `KeyError: 'NERIMITY_TOKEN'`

Your `.env` file isn't being found or is in the wrong place.

- Make sure `.env` is in the **same folder** as `bot.py`
- Make sure it contains exactly: `NERIMITY_TOKEN=your_token_here` (no quotes, no spaces around `=`)
- Make sure you have `load_dotenv()` at the top of your bot file

To check, open Command Prompt in your bot folder and run:
```
notepad .env
```

---

## Bot crashes immediately on startup

Look at the error message in the terminal — it usually tells you exactly what's wrong. Common causes:

- Invalid or expired token → regenerate it from the developer portal
- Missing a required package → run `pip install nerimity-sdk` again
- Syntax error in your code → check the line number in the error

---

## Changes to my code aren't taking effect

Make sure you saved the file! In Notepad press `Ctrl + S`. If you're using VS Code it saves automatically (or press `Ctrl + S`).

Then restart the bot: press `Ctrl + C` in the terminal to stop it, then run `python bot.py` again.
