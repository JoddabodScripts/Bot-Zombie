"""
Bot Zombie Dashboard Server
Run with: uvicorn dashboard_server:app --reload --port 7700
"""
import asyncio
import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import aiohttp

app = FastAPI(title="Bot Zombie Dashboard")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── State ──────────────────────────────────────────────────────────────────
bots: dict[str, dict] = {}  # token -> {proc, log_file, code_file, started_at}
DATA_DIR = Path("bot_zombie_data")
DATA_DIR.mkdir(exist_ok=True)

# ── Models ─────────────────────────────────────────────────────────────────
class SpawnRequest(BaseModel):
    token: str
    code: str

class StopRequest(BaseModel):
    token: str

class EmbedRequest(BaseModel):
    token: str
    channel_id: str
    html: str
    content: Optional[str] = ""

class VerifyRequest(BaseModel):
    token: str

# ── Helpers ────────────────────────────────────────────────────────────────
def bot_dir(token: str) -> Path:
    safe = token[-12:].replace("/", "_")
    d = DATA_DIR / safe
    d.mkdir(exist_ok=True)
    return d

# ── Routes ─────────────────────────────────────────────────────────────────

@app.post("/api/verify")
async def verify_token(req: VerifyRequest):
    """Verify a bot token against the Nerimity API."""
    async with aiohttp.ClientSession() as session:
        async with session.get(
            "https://nerimity.com/api/applications/bot",
            headers={"Authorization": req.token},
        ) as resp:
            if resp.status == 200:
                data = await resp.json()
                return {"ok": True, "bot": data}
            return {"ok": False, "status": resp.status}


@app.post("/api/spawn")
async def spawn_bot(req: SpawnRequest):
    """Write bot code to a temp file and spawn it as a subprocess."""
    if req.token in bots:
        proc = bots[req.token]["proc"]
        if proc.poll() is None:
            raise HTTPException(400, "Bot is already running")
        # clean up dead process
        del bots[req.token]

    d = bot_dir(req.token)
    code_file = d / "bot.py"
    log_file  = d / "bot.log"

    code_file.write_text(req.code, encoding="utf-8")
    log_handle = open(log_file, "w", encoding="utf-8")

    proc = subprocess.Popen(
        [sys.executable, str(code_file)],
        stdout=log_handle,
        stderr=subprocess.STDOUT,
        cwd=str(d),
    )

    bots[req.token] = {
        "proc": proc,
        "log_file": log_file,
        "code_file": code_file,
        "started_at": time.time(),
        "log_handle": log_handle,
    }
    return {"ok": True, "pid": proc.pid}


@app.post("/api/stop")
async def stop_bot(req: StopRequest):
    """Stop a running bot process."""
    entry = bots.get(req.token)
    if not entry:
        raise HTTPException(404, "Bot not running")
    proc = entry["proc"]
    proc.terminate()
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()
    entry["log_handle"].close()
    del bots[req.token]
    return {"ok": True}


@app.get("/api/status/{token_tail}")
async def bot_status(token_tail: str):
    """Check if a bot is running by last 12 chars of token."""
    for token, entry in bots.items():
        if token.endswith(token_tail):
            proc = entry["proc"]
            running = proc.poll() is None
            return {
                "running": running,
                "pid": proc.pid,
                "started_at": entry["started_at"],
                "uptime": time.time() - entry["started_at"] if running else 0,
            }
    return {"running": False}


@app.get("/api/logs/{token_tail}")
async def stream_logs(token_tail: str, lines: int = 100):
    """Return last N lines of bot log."""
    for token, entry in bots.items():
        if token.endswith(token_tail):
            log_file = entry["log_file"]
            if not log_file.exists():
                return {"lines": []}
            text = log_file.read_text(encoding="utf-8", errors="replace")
            all_lines = text.splitlines()
            return {"lines": all_lines[-lines:]}
    # check archived logs even if bot stopped
    for d in DATA_DIR.iterdir():
        log_file = d / "bot.log"
        if log_file.exists() and d.name in token_tail:
            text = log_file.read_text(encoding="utf-8", errors="replace")
            return {"lines": text.splitlines()[-lines:]}
    return {"lines": []}


@app.post("/api/send_embed")
async def send_embed(req: EmbedRequest):
    """Send an htmlEmbed message to a Nerimity channel."""
    payload = {"htmlEmbed": req.html}
    if req.content:
        payload["content"] = req.content
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"https://nerimity.com/api/channels/{req.channel_id}/messages",
            headers={
                "Authorization": req.token,
                "Content-Type": "application/json",
            },
            json=payload,
        ) as resp:
            body = await resp.json()
            return {"ok": resp.status < 300, "status": resp.status, "data": body}


@app.get("/api/save_code")
async def get_saved_code(token_tail: str):
    """Return the last saved bot.py for a token."""
    for d in DATA_DIR.iterdir():
        if d.name in token_tail or token_tail in d.name:
            code_file = d / "bot.py"
            if code_file.exists():
                return {"code": code_file.read_text(encoding="utf-8")}
    return {"code": ""}


# ── Static files (serve docs/ folder) ─────────────────────────────────────
DOCS_DIR = Path(__file__).parent / "docs"
if DOCS_DIR.exists():
    app.mount("/", StaticFiles(directory=str(DOCS_DIR), html=True), name="static")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("dashboard_server:app", host="0.0.0.0", port=7700, reload=True)
