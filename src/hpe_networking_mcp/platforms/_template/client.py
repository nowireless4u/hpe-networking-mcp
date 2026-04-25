"""Template HTTP client with bearer-token auth, async httpx, and 401-refresh hook.

This is the minimal pattern most modern REST APIs need: bearer token in the
``Authorization`` header, async transport via ``httpx.AsyncClient``, a
``request()`` shortcut that handles auth + 401 retry, and a
``health_check()`` that the cross-platform ``health`` probe calls.

When copying this template, the auth flavor is the most common thing to change:

- **Bearer token (this template)** — keep as-is; set ``self._token``
  from config in ``__init__``.
- **OAuth2 client_credentials** — replace ``_login_locked`` with a token
  endpoint call; cache + auto-refresh on 401 + before expiry. See
  ``platforms/greenlake/auth.py`` for the canonical implementation.
- **Username/password login endpoint** — replace ``_login_locked`` with
  a POST to the login endpoint that returns a session token. See
  ``platforms/apstra/client.py``.
- **Vendor SDK** — skip this file entirely; wrap the SDK in a thin
  adapter that exposes ``.health_check()`` and your tool surface. See
  ``platforms/mist/client.py``.
"""

from __future__ import annotations

import asyncio
import json
from typing import Any

import httpx
from fastmcp.exceptions import ToolError
from fastmcp.server.dependencies import get_context
from loguru import logger

# When copying this template, replace this import with your platform's secrets type.
# from hpe_networking_mcp.config import MyplatformSecrets  # noqa: ERA001
from hpe_networking_mcp.utils.logging import mask_secret

_REQUEST_TIMEOUT = 30.0
_AUTH_TIMEOUT = 10.0


class TemplateAuthError(RuntimeError):
    """Raised when the platform's auth handshake fails.

    Rename to ``<Platform>AuthError`` when copying.
    """


class TemplateClient:
    """Async REST API client with bearer-token auth and 401-refresh retry.

    Rename to ``<Platform>Client`` when copying. Base URL, auth header
    name, and refresh strategy may need to change.

    Usage in tools::

        client = await get_template_client()
        data = await client.get_json("/api/v1.0/Things")
        return data
    """

    def __init__(self, config: Any) -> None:
        # Replace ``Any`` with your ``<Platform>Secrets`` type.
        self._config = config
        self._token: str | None = getattr(config, "api_token", None)
        self._lock = asyncio.Lock()
        # Replace with your real base URL — typically built from config fields.
        base_url = getattr(config, "base_url", "https://example.invalid")
        self._http = httpx.AsyncClient(
            base_url=base_url,
            verify=getattr(config, "verify_ssl", True),
            timeout=_REQUEST_TIMEOUT,
        )

    @property
    def base_url(self) -> str:
        """Return the configured base URL (host + scheme)."""
        return str(self._http.base_url)

    async def aclose(self) -> None:
        """Close the underlying httpx client. Called from ``server.py:lifespan``."""
        await self._http.aclose()

    async def _ensure_token(self) -> str:
        """Return the cached token, acquiring one under the lock if needed.

        For static-token auth (this template's default) the token comes
        from config directly. For OAuth2 / login-endpoint flavors,
        replace with a real acquisition routine.
        """
        if self._token is not None:
            return self._token
        async with self._lock:
            if self._token is None:
                await self._login_locked()
            assert self._token is not None
            return self._token

    async def _refresh_token(self) -> str:
        """Force-refresh the token under the lock.

        For static-token auth this just re-reads the config (same token);
        for refreshable auth it calls the token endpoint.
        """
        async with self._lock:
            self._token = None
            await self._login_locked()
            assert self._token is not None
            return self._token

    async def _login_locked(self) -> None:
        """Acquire a fresh token. Caller must hold ``self._lock``.

        Default implementation: pull the token from config (static
        bearer token, no refresh endpoint). Replace with a POST to your
        login / token endpoint for OAuth2 / username-password flavors.
        """
        token = getattr(self._config, "api_token", None)
        if not token:
            raise TemplateAuthError("No api_token in config and no token endpoint configured.")
        self._token = token
        logger.info("Template: token loaded {}", mask_secret(token))

    def _auth_headers(self, token: str) -> dict[str, str]:
        """Build the headers for an authenticated request.

        Bearer is the default; some platforms use a custom header name
        (e.g. Apstra's ``AuthToken``, Mist's ``Authorization: Token``).
        """
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
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
        """Send an authenticated request, refreshing the token once on 401."""
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
            logger.info("Template: 401 on {} {} — refreshing token once", method, path)
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
        """Probe credentials by acquiring a token. Returns True if it works.

        Override with a real reachability check (e.g. GET /health) if
        your platform exposes one.
        """
        await self._ensure_token()
        return True


async def get_template_client() -> TemplateClient:
    """Retrieve the shared client from the lifespan context.

    Rename to ``get_<platform>_client`` when copying. The ctx key
    must match what ``server.py:lifespan`` populates.
    """
    ctx = get_context()
    client: TemplateClient | None = ctx.lifespan_context.get("_template_client")
    if client is None:
        raise ToolError(
            {
                "status_code": 503,
                "message": "Template API client not available. Check your credentials.",
            }
        )
    return client


def format_http_error(exc: BaseException) -> dict[str, Any]:
    """Shape any exception into a consistent dict for tool returns.

    Surfaces status code and response body for ``httpx.HTTPStatusError``;
    everything else falls back to a generic shape so call sites can use
    this helper uniformly inside broad ``except Exception`` blocks. Same
    pattern used by every other platform.
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
