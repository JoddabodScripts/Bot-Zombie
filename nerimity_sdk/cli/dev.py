"""nerimity dev — development runner.

- Auto-restarts the bot when any .py file in the working directory changes
- Checks PyPI for a newer version of nerimity-sdk on startup
- Pretty coloured log output

Usage:
    nerimity dev bot.py
"""
from __future__ import annotations
import logging
import os
import sys
import subprocess
import time


_COLOURS = {
    "DEBUG":    "\033[36m",
    "INFO":     "\033[32m",
    "WARNING":  "\033[33m",
    "ERROR":    "\033[31m",
    "CRITICAL": "\033[35m",
    "RESET":    "\033[0m",
    "BOLD":     "\033[1m",
    "DIM":      "\033[2m",
}


class _PrettyFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        c = _COLOURS
        ts    = self.formatTime(record, "%H:%M:%S")
        level = f"{c[record.levelname]}{record.levelname:<8}{c['RESET']}"
        name  = f"{c['DIM']}{record.name}{c['RESET']}"
        return f"{ts}  {level}  {name}  {record.getMessage()}"


def _setup_pretty_logging() -> None:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(_PrettyFormatter())
    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(logging.DEBUG)


def _check_for_update() -> None:
    """Print a notice if a newer nerimity-sdk is available on PyPI."""
    try:
        import urllib.request, json
        from nerimity_sdk import __version__ as current
        with urllib.request.urlopen(
            "https://pypi.org/pypi/nerimity-sdk/json", timeout=3
        ) as resp:
            latest = json.loads(resp.read())["info"]["version"]

        if latest != current:
            c = _COLOURS
            pip = "pip" if sys.platform != "win32" else "pip"
            print(
                f"\n{c['BOLD']}{c['WARNING']}⚠  nerimity-sdk update available: "
                f"{current} → {latest}{c['RESET']}\n"
                f"   Run: {c['BOLD']}pip install nerimity-sdk=={latest}{c['RESET']}\n"
            )
    except Exception:
        pass  # no internet / PyPI down — silently skip


def _snapshot(directory: str) -> dict[str, float]:
    """Return a dict of {filepath: mtime} for all .py files under directory."""
    snap: dict[str, float] = {}
    for root, _, files in os.walk(directory):
        # skip hidden dirs and common noise
        if any(part.startswith(".") or part in ("__pycache__", ".venv", "venv", "site")
               for part in root.split(os.sep)):
            continue
        for f in files:
            if f.endswith(".py"):
                path = os.path.join(root, f)
                try:
                    snap[path] = os.path.getmtime(path)
                except OSError:
                    pass
    return snap


def run(bot_file: str) -> None:
    _setup_pretty_logging()
    _check_for_update()

    directory = os.path.dirname(os.path.abspath(bot_file))
    c = _COLOURS

    print(f"{c['BOLD']}{c['INFO']}[dev]{c['RESET']} Watching {directory} for changes...\n")

    while True:
        snapshot = _snapshot(directory)

        # Build the subprocess command — same Python interpreter, force dev flags via env
        env = os.environ.copy()
        env["NERIMITY_DEBUG"] = "1"
        env["NERIMITY_WATCH"] = "0"  # we handle watching ourselves

        cmd = [sys.executable, bot_file]
        proc = subprocess.Popen(cmd, env=env)

        try:
            while proc.poll() is None:
                time.sleep(0.5)
                current = _snapshot(directory)
                changed = [p for p, m in current.items()
                           if snapshot.get(p) != m or p not in snapshot]
                if changed:
                    rel = os.path.relpath(changed[0], directory)
                    print(f"\n{c['WARNING']}[dev] {rel} changed — restarting...{c['RESET']}\n")
                    proc.terminate()
                    try:
                        proc.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        proc.kill()
                    break
                snapshot = current
        except KeyboardInterrupt:
            print(f"\n{c['DIM']}[dev] Stopping.{c['RESET']}")
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
            sys.exit(0)
