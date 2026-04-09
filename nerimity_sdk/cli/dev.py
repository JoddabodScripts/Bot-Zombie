"""nerimity dev — run your bot in development mode.

Equivalent to setting debug=True, watch=True on your Bot, but without
having to touch your bot.py at all. Just run:

    nerimity dev bot.py
"""
from __future__ import annotations
import os
import sys
import logging


_COLOURS = {
    "DEBUG":    "\033[36m",   # cyan
    "INFO":     "\033[32m",   # green
    "WARNING":  "\033[33m",   # yellow
    "ERROR":    "\033[31m",   # red
    "CRITICAL": "\033[35m",   # magenta
    "RESET":    "\033[0m",
}


class _PrettyFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        colour = _COLOURS.get(record.levelname, "")
        reset  = _COLOURS["RESET"]
        ts     = self.formatTime(record, "%H:%M:%S")
        level  = f"{colour}{record.levelname:<8}{reset}"
        name   = f"\033[2m{record.name}\033[0m"
        return f"{ts}  {level}  {name}  {record.getMessage()}"


def _setup_pretty_logging() -> None:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(_PrettyFormatter())
    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(logging.DEBUG)


def run(bot_file: str) -> None:
    _setup_pretty_logging()

    # Inject dev flags via environment so bot.py doesn't need changing
    os.environ.setdefault("NERIMITY_DEBUG", "1")
    os.environ.setdefault("NERIMITY_WATCH", "1")

    print(f"\033[32m[dev]\033[0m Starting {bot_file} in development mode "
          f"(debug=True, watch=True)\n")

    # Patch Bot.__init__ to force debug/watch on regardless of what bot.py sets
    try:
        import nerimity_sdk.bot as _bot_module
        _orig_init = _bot_module.Bot.__init__

        def _patched_init(self, *args, **kwargs):
            kwargs["debug"] = True
            kwargs["watch"] = True
            _orig_init(self, *args, **kwargs)

        _bot_module.Bot.__init__ = _patched_init
    except Exception:
        pass  # if patching fails, env vars are still set

    # Run the bot file in its own namespace
    import runpy
    runpy.run_path(bot_file, run_name="__main__")
