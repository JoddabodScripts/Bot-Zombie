"""Webhook wrapper for Nerimity.

Usage::

    from nerimity_sdk.webhooks import Webhook

    wh = Webhook("your_webhook_token")
    await wh.send("Hello from a webhook!")
    await wh.send("Custom name", username="GitHub", avatar_url="https://...")
"""
from __future__ import annotations
from typing import Optional
import aiohttp

WEBHOOK_URL = "https://nerimity.com/api/webhooks/{token}"


class Webhook:
    """Execute a Nerimity webhook.

    Get your webhook token from:
    Channel settings → Webhooks → Create → copy the token from the URL.
    """

    def __init__(self, token: str) -> None:
        self.token = token
        self._url = WEBHOOK_URL.format(token=token)

    async def send(self, content: str, *,
                   username: Optional[str] = None,
                   avatar_url: Optional[str] = None) -> dict:
        """Send a message via this webhook. Returns the created Message dict."""
        body: dict = {"content": content}
        if username:
            body["username"] = username
        if avatar_url:
            body["avatarUrl"] = avatar_url

        async with aiohttp.ClientSession() as session:
            async with session.post(self._url, json=body) as resp:
                if resp.status >= 400:
                    text = await resp.text()
                    raise RuntimeError(f"Webhook failed ({resp.status}): {text}")
                return await resp.json()
