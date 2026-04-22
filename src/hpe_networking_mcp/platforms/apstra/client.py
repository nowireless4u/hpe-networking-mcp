"""Apstra API client with async httpx, token caching, and auth retry.

Apstra authenticates via POST /api/user/login (username/password) which returns
a bearer token used in the ``AuthToken`` header. There is no refresh endpoint;
on 401 the only recourse is re-login. An asyncio.Lock serializes token
acquisition across concurrent callers.

SSL verification is honored from config (source used verify=False unconditionally).
"""

from __future__ import annotations

import asyncio
import json
from typing import Any

import httpx
from fastmcp.exceptions import ToolError
from fastmcp.server.dependencies import get_context
from loguru import logger

from hpe_networking_mcp.config import ApstraSecrets
from hpe_networking_mcp.utils.logging import mask_secret

_REQUEST_TIMEOUT = 30.0
_AUTH_TIMEOUT = 10.0


class ApstraAuthError(RuntimeError):
    """Raised when Apstra login fails."""


class ApstraClient:
    """Async Apstra REST API client with token caching and 401-refresh retry.

    Usage in tools::

        client = await get_apstra_client()
        data = await client.request("GET", "/api/blueprints")
        return data.json()["items"]
    """

    def __init__(self, config: ApstraSecrets) -> None:
        self._config = config
        self._token: str | None = None
        self._lock = asyncio.Lock()
        base_url = f"https://{config.server}:{config.port}"
        self._http = httpx.AsyncClient(
            base_url=base_url,
            verify=config.verify_ssl,
            timeout=_REQUEST_TIMEOUT,
        )

    @property
    def server(self) -> str:
        """Return ``host:port`` of the configured Apstra server."""
        return f"{self._config.server}:{self._config.port}"

    async def aclose(self) -> None:
        """Close the underlying httpx client."""
        await self._http.aclose()

    async def _ensure_token(self) -> str:
        """Return the cached token, acquiring one under the lock if needed."""
        if self._token is not None:
            return self._token
        async with self._lock:
            if self._token is None:
                await self._login_locked()
            assert self._token is not None
            return self._token

    async def _refresh_token(self) -> str:
        """Force-refresh the token under the lock."""
        async with self._lock:
            self._token = None
            await self._login_locked()
            assert self._token is not None
            return self._token

    async def _login_locked(self) -> None:
        """Perform the login request. Caller must hold ``self._lock``."""
        payload = {"username": self._config.username, "password": self._config.password}
        logger.info("Apstra: requesting new AuthToken from {}", self._config.server)
        try:
            response = await self._http.post(
                "/api/user/login",
                json=payload,
                headers={"Content-Type": "application/json", "Cache-Control": "no-cache"},
                timeout=_AUTH_TIMEOUT,
            )
        except httpx.HTTPError as e:
            raise ApstraAuthError(f"Apstra login request failed: {e}") from e

        # Apstra returns 201 Created on successful login
        if response.status_code not in (200, 201):
            raise ApstraAuthError(f"Apstra login failed with HTTP {response.status_code}: {response.text[:200]}")

        try:
            body = response.json()
        except ValueError as e:
            raise ApstraAuthError(f"Apstra login returned non-JSON body: {response.text[:200]}") from e

        token = body.get("token")
        if not token:
            raise ApstraAuthError(f"Apstra login response missing 'token' field: {body}")

        self._token = token
        logger.info("Apstra: obtained AuthToken {}", mask_secret(token))

    def _auth_headers(self, token: str) -> dict[str, str]:
        return {
            "AuthToken": token,
            "Content-Type": "application/json",
            "Cache-Control": "no-cache",
        }

    async def request(
        self,
        method: str,
        path: str,
        *,
        json_body: Any = None,
        params: dict[str, Any] | None = None,
        timeout: float | None = None,
    ) -> httpx.Response:
        """Send an authenticated request, refreshing the token once on 401.

        Args:
            method: HTTP method ("GET", "POST", "PUT", "DELETE", "PATCH").
            path: Path starting with "/api/...".
            json_body: Optional JSON payload (serialized with httpx's ``json=``).
            params: Optional query parameters.
            timeout: Optional per-call timeout override (seconds).

        Returns:
            The httpx.Response after ``raise_for_status()``.

        Raises:
            ApstraAuthError: If login fails.
            httpx.HTTPStatusError: On 4xx/5xx other than 401-retry.
            httpx.HTTPError: On transport errors.
        """
        token = await self._ensure_token()
        kwargs: dict[str, Any] = {"headers": self._auth_headers(token)}
        if json_body is not None:
            kwargs["json"] = json_body
        if params:
            kwargs["params"] = params
        if timeout is not None:
            kwargs["timeout"] = timeout

        response = await self._http.request(method, path, **kwargs)
        if response.status_code == 401:
            logger.info("Apstra: 401 on {} {} — refreshing token once", method, path)
            token = await self._refresh_token()
            kwargs["headers"] = self._auth_headers(token)
            response = await self._http.request(method, path, **kwargs)
        response.raise_for_status()
        return response

    async def get_json(self, path: str, **kwargs: Any) -> Any:
        """Shortcut for a GET that returns parsed JSON."""
        response = await self.request("GET", path, **kwargs)
        return response.json()

    async def health_check(self) -> bool:
        """Probe credentials by acquiring a token. Returns True if login succeeds."""
        await self._ensure_token()
        return True


async def get_apstra_client() -> ApstraClient:
    """Retrieve the shared ApstraClient from the lifespan context.

    Raises:
        ToolError: If Apstra is not configured or the client is unavailable.
    """
    ctx = get_context()
    client: ApstraClient | None = ctx.lifespan_context.get("apstra_client")
    if client is None:
        raise ToolError(
            {
                "status_code": 503,
                "message": "Apstra API client not available. Check your Apstra credentials.",
            }
        )
    return client


def format_http_error(exc: BaseException) -> dict[str, Any]:
    """Shape any exception into a consistent dict for tool returns.

    Surfaces status code and response body for ``httpx.HTTPStatusError``;
    everything else falls back to a generic shape so call sites can use this
    helper uniformly inside broad ``except Exception`` blocks.
    """
    if isinstance(exc, httpx.HTTPStatusError):
        status = exc.response.status_code
        text = exc.response.text[:500]
        try:
            body: Any = exc.response.json()
        except (ValueError, json.JSONDecodeError):
            body = text
        return {"status_code": status, "message": str(exc), "body": body}
    return {"status_code": 0, "message": str(exc), "body": None}
