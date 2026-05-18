"""Aruba UXI REST API client with async httpx and OAuth2 token management.

Authenticates via POST to the GreenLake SSO endpoint using client-credentials
grant. Tokens have a 7199-second TTL; a 60-second buffer triggers proactive
refresh. An asyncio.Lock serializes concurrent refresh under load.

Base URL: ``https://api.capenetworks.com/networking-uxi/v1alpha1``
Token URL: ``https://sso.common.cloud.hpe.com/as/token.oauth2``

IMPORTANT: The token POST uses a separate httpx.AsyncClient with NO base_url.
Never reuse self._http for the token request — it is bound to api.capenetworks.com
and would resolve the SSO hostname incorrectly (Pitfall 5).
"""

from __future__ import annotations

import asyncio
import json
import time
from typing import Any

import httpx
from fastmcp.exceptions import ToolError
from fastmcp.server.dependencies import get_context
from loguru import logger

from hpe_networking_mcp.config import UXISecrets
from hpe_networking_mcp.utils.logging import mask_secret

_TOKEN_URL = "https://sso.common.cloud.hpe.com/as/token.oauth2"  # nosec B105
_UXI_BASE_URL = "https://api.capenetworks.com/networking-uxi/v1alpha1"
_TOKEN_BUFFER_SECS = 60  # re-fetch when within 60 s of expiry (D-04)
_REQUEST_TIMEOUT = 30.0
_AUTH_TIMEOUT = 10.0


class UXIClient:
    """Async Aruba UXI REST API client with time-based OAuth2 token caching.

    Usage in tools::

        client = await get_uxi_client()
        data = await client.uxi_get("/sensors", next_cursor=cursor, limit=page_size)
        return data
    """

    def __init__(self, config: UXISecrets) -> None:
        self._config = config
        self._token: str | None = None
        self._expires_at: float = 0.0  # Unix timestamp; 0 = always expired (D-01)
        self._lock = asyncio.Lock()  # serializes concurrent refresh (D-02)
        self._http = httpx.AsyncClient(
            base_url=_UXI_BASE_URL,
            timeout=_REQUEST_TIMEOUT,
        )

    async def aclose(self) -> None:
        """Close the underlying httpx client. Called from server.py lifespan."""
        await self._http.aclose()

    async def _ensure_token(self) -> str:
        """Return cached token, acquiring one under the lock if needed or expired."""
        if self._token and time.time() + _TOKEN_BUFFER_SECS < self._expires_at:
            return self._token
        async with self._lock:
            # Re-check inside lock — another coroutine may have refreshed
            if self._token and time.time() + _TOKEN_BUFFER_SECS < self._expires_at:
                return self._token
            await self._fetch_token_locked()
        if self._token is None:  # guard: assert is stripped under python -O
            raise RuntimeError("UXI token fetch succeeded but self._token is still None")
        return self._token

    def _invalidate_token(self) -> None:
        """Force token re-fetch on the next request (e.g. after a 401)."""
        self._token = None
        self._expires_at = 0.0

    async def _fetch_token_locked(self) -> None:
        """POST to GreenLake SSO to acquire a new access token.

        Caller must hold self._lock. Uses a separate httpx.AsyncClient with NO
        base_url so the SSO hostname resolves correctly (Pitfall 5 prevention).
        """
        logger.info("UXI: requesting new access token (client_id: {})", mask_secret(self._config.client_id))
        async with httpx.AsyncClient(timeout=_AUTH_TIMEOUT) as auth_http:
            resp = await auth_http.post(
                _TOKEN_URL,
                data={
                    "grant_type": "client_credentials",
                    "client_id": self._config.client_id,
                    "client_secret": self._config.client_secret,
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
        resp.raise_for_status()
        body = resp.json()
        self._token = body["access_token"]
        expires_in = body.get("expires_in", 7199)
        self._expires_at = time.time() + expires_in
        logger.info("UXI: token acquired (expires_in={}s)", expires_in)

    async def _get_json(self, path: str, *, params: dict[str, Any] | None = None) -> Any:
        """Issue an authenticated GET request and return parsed JSON."""
        token = await self._ensure_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        response = await self._http.request("GET", path, headers=headers, params=params)
        if response.status_code == 401:
            self._invalidate_token()
        response.raise_for_status()
        return response.json()

    async def uxi_get_single(self, path: str) -> Any:
        """GET a single UXI resource by path (no pagination params)."""
        return await self._get_json(path)

    async def uxi_get(
        self,
        path: str,
        *,
        next_cursor: str | None = None,
        limit: int = 50,
        extra_params: dict | None = None,
    ) -> dict:
        """GET a UXI list endpoint with cursor pagination params.

        NOTE: query param is 'limit' (not 'page_size') and 'next' (not 'cursor').
        Both None and '' next_cursor values are correctly excluded (D-05/Pitfall 6).

        Args:
            path: API path, e.g. ``/sensors``.
            next_cursor: Opaque cursor from a prior response's ``next`` field.
                Omit (or pass None) for the first page.
            limit: Max items per page (default 50, max 100).
            extra_params: Additional query parameters merged into the request.

        Returns:
            Parsed JSON dict — typically ``{items: [...], count: N, next: str|null}``.
        """
        params: dict[str, Any] = {"limit": limit}
        if next_cursor:  # both None and "" are excluded correctly (D-05/Pitfall 6)
            params["next"] = next_cursor
        if extra_params:
            params.update(extra_params)
        return await self._get_json(path, params=params)

    async def uxi_post(self, path: str, json_body: Any) -> Any:
        """POST a JSON body to the UXI API and return parsed JSON."""
        token = await self._ensure_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        response = await self._http.request("POST", path, headers=headers, json=json_body)
        if response.status_code == 401:
            self._invalidate_token()
        response.raise_for_status()
        return response.json()

    async def uxi_patch(self, path: str, json_body: Any) -> Any:
        """PATCH a resource on the UXI API and return parsed JSON."""
        token = await self._ensure_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        response = await self._http.request("PATCH", path, headers=headers, json=json_body)
        if response.status_code == 401:
            self._invalidate_token()
        response.raise_for_status()
        return response.json()

    async def uxi_delete(self, path: str) -> dict[str, Any]:
        """DELETE a resource on the UXI API."""
        token = await self._ensure_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        response = await self._http.request("DELETE", path, headers=headers)
        if response.status_code == 401:
            self._invalidate_token()
        response.raise_for_status()
        if response.status_code == 204 or not response.content:
            return {"status_code": response.status_code}
        return response.json()

    async def health_check(self) -> bool:
        """Probe by calling GET /sensors?limit=1 (D-08). Returns True if reachable."""
        await self.uxi_get("/sensors", limit=1)
        return True


async def get_uxi_client() -> UXIClient:
    """Retrieve the shared UXIClient from the lifespan context.

    Raises:
        ToolError: If UXI is not configured or the client is unavailable.
    """
    ctx = get_context()
    client: UXIClient | None = ctx.lifespan_context.get("uxi_client")
    if client is None:
        raise ToolError(
            {
                "status_code": 503,
                "message": "UXI API client not available. Check your uxi_client_id and uxi_client_secret secrets.",
            }
        )
    return client


_SENSITIVE_BODY_KEYS = frozenset({"access_token", "client_secret", "client_id", "Authorization", "password", "token"})


def _sanitize_body(body: Any) -> Any:
    """Remove known-sensitive keys from a parsed JSON body before surfacing to callers."""
    if isinstance(body, dict):
        return {k: "***" if k in _SENSITIVE_BODY_KEYS else v for k, v in body.items()}
    return body


def format_http_error(exc: BaseException) -> dict[str, Any]:
    """Shape any exception into a consistent dict for tool returns.

    Surfaces status code and sanitized response body for ``httpx.HTTPStatusError``;
    network/protocol errors return only the exception class name to avoid leaking
    hostnames or TLS details to callers.
    """
    if isinstance(exc, httpx.HTTPStatusError):
        status = exc.response.status_code
        text = exc.response.text[:500]
        try:
            body: Any = _sanitize_body(exc.response.json())
        except (ValueError, json.JSONDecodeError):
            body = text
        return {"status_code": status, "message": str(exc), "body": body}
    # For network/protocol errors, log detail server-side but return only class name.
    logger.debug("UXI network error: {}", exc)
    return {"status_code": 0, "message": f"{type(exc).__name__}: connection or protocol error", "body": None}
