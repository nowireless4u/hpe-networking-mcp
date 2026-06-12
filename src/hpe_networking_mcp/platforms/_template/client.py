"""Template HTTP client with bearer-token auth, async httpx, and 401-refresh hook.

This is the minimal pattern most modern REST APIs need: bearer token in the
``Authorization`` header, async transport via ``httpx.AsyncClient``, a
``request()`` shortcut that handles auth + 401 retry, and a
``health_check()`` that the cross-platform ``health`` probe calls.

Token acquisition, caching, and lock-serialized refresh run through the
shared :class:`AsyncTokenManager` (``platforms/_common/auth.py``). When
copying this template, the *fetch strategy* is the thing to change:

- **Static token (this template)** — ``_fetch_token`` reads the token from
  config; no refresh endpoint.
- **OAuth2 client_credentials** — pass
  ``oauth2_client_credentials(token_url, client_id, client_secret, name=...)``
  as the manager's fetch instead of a method. See ``platforms/uxi/client.py``.
- **Username/password login endpoint** — make ``_fetch_token`` POST to the
  login endpoint and return ``TokenResult(token)`` (no expiry — the token
  lives until a 401 forces re-login). See ``platforms/apstra/client.py``.
- **Vendor SDK** — skip this file entirely; wrap the SDK in a thin
  adapter that exposes ``.health_check()`` and your tool surface.

How the credential is *attached* to requests stays here in the client —
override ``_auth_headers`` for custom header names, or the request methods
themselves for cookie / query-param auth (see ``platforms/aos8/client.py``).
"""

from __future__ import annotations

import json
from typing import Any

import httpx
from fastmcp.exceptions import ToolError
from fastmcp.server.dependencies import get_context
from loguru import logger

from hpe_networking_mcp.platforms._common.auth import AsyncTokenManager, AuthError, TokenResult

# When copying this template, replace this import with your platform's secrets type.
# from hpe_networking_mcp.config import MyplatformSecrets  # noqa: ERA001
from hpe_networking_mcp.utils.logging import mask_secret

_REQUEST_TIMEOUT = 30.0
_AUTH_TIMEOUT = 10.0  # pass as `timeout=` to oauth2_client_credentials / login POSTs


class TemplateAuthError(AuthError):
    """Raised when the platform's auth handshake fails.

    Rename to ``<Platform>AuthError`` when copying. Subclassing the shared
    ``AuthError`` lets call sites catch either the platform flavor or the
    base.
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
        # Static-token flavor: ``_fetch_token`` reads from config. For OAuth2,
        # pass ``oauth2_client_credentials(...)`` as the fetch instead.
        self._tokens = AsyncTokenManager(self._fetch_token, name="Template")
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

    async def _fetch_token(self) -> TokenResult:
        """Fetch strategy for :class:`AsyncTokenManager`.

        Default implementation: pull the token from config (static bearer
        token, no refresh endpoint) — ``expires_in=None`` means it never
        goes stale. For a username/password login endpoint, POST to it
        here instead and return the session token (see Apstra). For
        OAuth2, drop this method and pass ``oauth2_client_credentials``
        to the manager (see UXI).
        """
        token = getattr(self._config, "api_token", None)
        if not token:
            raise TemplateAuthError("No api_token in config and no token endpoint configured.")
        logger.info("Template: token loaded {}", mask_secret(token))
        return TokenResult(token)

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
        token = await self._tokens.get_token()
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
            token = await self._tokens.refresh()
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
        await self._tokens.get_token()
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
