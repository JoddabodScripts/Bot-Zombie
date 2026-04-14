import asyncio
import hashlib
import json
import os
import secrets
import subprocess
import sys
import tempfile
from pathlib import Path
from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

DATA = Path("/data")
DATA.mkdir(parents=True, exist_ok=True)
BOTS_FILE  = DATA / "bots.json"
USERS_FILE = DATA / "users.json"

_bots:    dict[str, dict] = {}   # token → {proc, code}
_users:   dict[str, dict] = {}   # username → {pw_hash, bot_token}
_sessions: dict[str, str] = {}   # session_token → username


# ── Persistence ────────────────────────────────────────────────────────────

def _load():
    if BOTS_FILE.exists():
        try:
            for token, code in json.loads(BOTS_FILE.read_text()).items():
                _bots[token] = {"proc": _launch(token, code), "code": code}
        except Exception:
            pass
    if USERS_FILE.exists():
        try:
            _users.update(json.loads(USERS_FILE.read_text()))
        except Exception:
            pass

def _save_bots():
    BOTS_FILE.write_text(json.dumps({t: b["code"] for t, b in _bots.items()}))

def _save_users():
    USERS_FILE.write_text(json.dumps(_users))

def _hash(pw: str) -> str:
    return hashlib.sha256(pw.encode()).hexdigest()


# ── Bot process management ─────────────────────────────────────────────────

def _launch(token: str, code: str) -> subprocess.Popen:
    code = code.replace('os.environ["NERIMITY_TOKEN"]', f'"{token}"')
    code = code.replace("os.environ['NERIMITY_TOKEN']", f'"{token}"')
    tmp = tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode="w")
    tmp.write(code)
    tmp.flush()
    tmp.close()
    return subprocess.Popen(
        [sys.executable, tmp.name],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        env={**os.environ, "NERIMITY_TOKEN": token, "NERIMITY_CHILD": "1"},
    )

async def _watchdog():
    while True:
        await asyncio.sleep(20)
        for token, bot in list(_bots.items()):
            if bot["proc"].poll() is not None:
                bot["proc"] = _launch(token, bot["code"])


# ── Auth helpers ───────────────────────────────────────────────────────────

def _require_session(authorization: Optional[str]) -> str:
    """Returns username or raises 401."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(401, "Not authenticated")
    token = authorization.removeprefix("Bearer ").strip()
    username = _sessions.get(token)
    if not username:
        raise HTTPException(401, "Invalid or expired session")
    return username


# ── Startup ────────────────────────────────────────────────────────────────

@app.on_event("startup")
async def startup():
    _load()
    asyncio.create_task(_watchdog())


# ── Auth endpoints ─────────────────────────────────────────────────────────

class AuthRequest(BaseModel):
    username: str
    password: str

@app.post("/auth/register")
async def register(req: AuthRequest):
    u = req.username.strip().lower()
    if not u or len(u) < 3:
        raise HTTPException(400, "Username must be at least 3 characters")
    if u in _users:
        raise HTTPException(409, "Username already taken")
    _users[u] = {"pw_hash": _hash(req.password), "bot_token": ""}
    _save_users()
    session = secrets.token_hex(32)
    _sessions[session] = u
    return {"session": session, "username": u}

@app.post("/auth/login")
async def login(req: AuthRequest):
    u = req.username.strip().lower()
    user = _users.get(u)
    if not user or user["pw_hash"] != _hash(req.password):
        raise HTTPException(401, "Invalid username or password")
    session = secrets.token_hex(32)
    _sessions[session] = u
    return {"session": session, "username": u, "bot_token": user.get("bot_token", "")}

@app.post("/auth/logout")
async def logout(authorization: Optional[str] = Header(None)):
    username = _require_session(authorization)
    token = authorization.removeprefix("Bearer ").strip()
    _sessions.pop(token, None)
    return {"status": "logged out"}


# ── Bot endpoints (require auth) ───────────────────────────────────────────

class DeployRequest(BaseModel):
    code: str
    bot_token: Optional[str] = None  # if provided, saves it to account

@app.post("/deploy")
async def deploy(req: DeployRequest, authorization: Optional[str] = Header(None)):
    username = _require_session(authorization)
    user = _users[username]

    # use provided token or saved one
    token = (req.bot_token or user.get("bot_token", "")).strip()
    if not token:
        raise HTTPException(400, "No bot token — save one to your account first")

    # save token to account if new
    if req.bot_token and req.bot_token != user.get("bot_token"):
        user["bot_token"] = req.bot_token.strip()
        _save_users()

    if token in _bots:
        p = _bots[token]["proc"]
        if p.poll() is None:
            p.terminate()
    _bots[token] = {"proc": _launch(token, req.code), "code": req.code}
    _save_bots()
    return {"status": "started"}

@app.post("/stop")
async def stop(authorization: Optional[str] = Header(None)):
    username = _require_session(authorization)
    token = _users[username].get("bot_token", "")
    bot = _bots.pop(token, None)
    if bot and bot["proc"].poll() is None:
        bot["proc"].terminate()
    _save_bots()
    return {"status": "stopped"}

@app.get("/status")
async def status(authorization: Optional[str] = Header(None)):
    username = _require_session(authorization)
    token = _users[username].get("bot_token", "")
    bot = _bots.get(token)
    return {"running": bool(bot and bot["proc"].poll() is None), "bot_token": token}


# ── Health ─────────────────────────────────────────────────────────────────

@app.get("/health")
async def health():
    return {"ok": True, "bots": len(_bots)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
