"""OAuth2 wrapper for Nerimity.

Useful for web dashboards that let server owners configure the bot via browser.

Flow::

    1. Redirect user to Nerimity's OAuth2 authorize URL
    2. Nerimity redirects back to your redirect_uri with ?code=...
    3. Exchange the code for an access token
    4. Use the token to fetch the user's profile and servers

Usage::

    from nerimity_sdk.oauth2 import OAuth2Client

    client = OAuth2Client(
        client_id="your_app_id",
        client_secret="your_app_secret",
        redirect_uri="https://yoursite.com/callback",
    )

    # Step 1 - send user to this URL
    url = client.authorize_url(scopes=["identify", "servers"])

    # Step 2 - in your callback handler:
    token = await client.exchange_code(code=request.args["code"])

    user    = await client.get_current_user(token["accessToken"])
    servers = await client.get_current_user_servers(token["accessToken"])

    # Later - refresh an expired token:
    new_token = await client.refresh_token(token["refreshToken"])
"""
from __future__ import annotations
from typing import Optional
from urllib.parse import urlencode
import aiohttp

BASE = "https://nerimity.com/api/oauth2"
AUTHORIZE_URL = "https://nerimity.com/oauth2/authorize"


class OAuth2Client:
    """Nerimity OAuth2 helper.

    Parameters
    ----------
    client_id:     Your application ID (from developer settings)
    client_secret: Your application secret
    redirect_uri:  The redirect URI registered on your application
    """

    def __init__(self, client_id: str, client_secret: str,
                 redirect_uri: str) -> None:
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri

    def authorize_url(self, scopes: Optional[list[str]] = None) -> str:
        """Build the URL to redirect users to for authorization."""
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
        }
        if scopes:
            params["scope"] = " ".join(scopes)
        return f"{AUTHORIZE_URL}?{urlencode(params)}"

    async def exchange_code(self, code: str) -> dict:
        """Exchange an authorization code for an access token.

        Returns dict with keys: accessToken, expiresIn, refreshToken
        """
        return await self._token_request(
            grantType="authorization_code",
            code=code,
            redirectUri=self.redirect_uri,
        )

    async def refresh_token(self, refresh_token: str) -> dict:
        """Exchange a refresh token for a new access token."""
        return await self._token_request(
            grantType="refresh_token",
            refreshToken=refresh_token,
        )

    async def get_current_user(self, access_token: str) -> dict:
        """Fetch the authorized user's profile."""
        return await self._get(f"{BASE}/users/current", access_token)

    async def get_current_user_servers(self, access_token: str) -> list[dict]:
        """Fetch the servers the authorized user is in."""
        return await self._get(f"{BASE}/users/current/servers", access_token)

    # ── Internal ──────────────────────────────────────────────────────────────

    async def _token_request(self, **params) -> dict:
        params.update(clientId=self.client_id, clientSecret=self.client_secret)
        async with aiohttp.ClientSession() as s:
            async with s.post(f"{BASE}/token", params=params) as resp:
                if resp.status >= 400:
                    raise RuntimeError(f"OAuth2 token error ({resp.status}): {await resp.text()}")
                return await resp.json()

    async def _get(self, url: str, access_token: str) -> dict | list:
        async with aiohttp.ClientSession() as s:
            async with s.get(url, headers={"Authorization": access_token}) as resp:
                if resp.status >= 400:
                    raise RuntimeError(f"OAuth2 error ({resp.status}): {await resp.text()}")
                return await resp.json()
