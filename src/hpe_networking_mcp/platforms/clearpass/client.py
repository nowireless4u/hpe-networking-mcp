"""ClearPass async API client (replaces the pyclearpass SDK).

Tools obtain the client from the lifespan context via :func:`get_clearpass_client`.

The ``request()`` method preserves pyclearpass's response contract exactly —
decoded JSON (dict/list) for JSON accepts with a raw-text fallback, raw bytes
for non-JSON accepts, and **error bodies returned, never raised** (callers
inspect ``{"status": 403, ...}`` dicts, exactly as they did against
``ClearPassAPILogin._send_request``).

Behavior intentionally mirrored from the previous pyclearpass-based layer:

* OAuth2 client-credentials token from ``POST {server}/oauth`` with a JSON
  body (ClearPass's token endpoint accepts JSON; this is what both
  pyclearpass and our old ``ClearPassTokenManager`` sent).
* ``Authorization: Bearer <token>`` + ``accept`` header per request.
* On a 401/403 auth-failure body: invalidate, refresh, replay exactly once
  (the behavior our ``_send_request`` monkey-patch added — now first-class).
* ``verify_ssl`` honored from config (pyclearpass hardcoded ``False``; we
  overrode it per-instance before).

Tokens expire after 8 hours (28800 s); expiry is now tracked proactively from
the token response via the shared :class:`AsyncTokenManager`, so the 403
storm after a token aged out can no longer happen in the first place.
"""

from __future__ import annotations

import json
from typing import Any

import httpx
from fastmcp.exceptions import ToolError
from fastmcp.server.dependencies import get_context
from loguru import logger

from hpe_networking_mcp.config import ClearPassSecrets
from hpe_networking_mcp.platforms._common.auth import AsyncTokenManager, AuthError, TokenResult
from hpe_networking_mcp.utils.logging import mask_secret

_REQUEST_TIMEOUT = 30.0
_AUTH_TIMEOUT = 30.0
_DEFAULT_TOKEN_TTL_SECS = 28800.0  # ClearPass default: 8 hours

# ClearPass returns both 401 (invalid token) and 403 (insufficient perms /
# expired client-credentials token). We retry on either since a stale token
# surfaces as 403 in practice.
_AUTH_ERROR_STATUSES = frozenset({401, 403})


class ClearPassAuthError(AuthError):
    """Raised when OAuth2 client-credentials authentication fails."""


def _is_auth_error(body: Any) -> bool:
    """Detect a 401/403 auth-failure payload in a decoded response body.

    ClearPass error bodies look like::

        {"type": "...", "title": "Forbidden", "status": 403, "detail": "Forbidden"}
    """
    if not isinstance(body, dict):
        return False
    status = body.get("status")
    return isinstance(status, int) and status in _AUTH_ERROR_STATUSES


class ClearPassClient:
    """Async ClearPass REST API client with pyclearpass-compatible responses.

    Usage in tools::

        client = await get_clearpass_client()
        result = await client.request("get", "/guest", params={"limit": 25})
    """

    def __init__(self, config: ClearPassSecrets) -> None:
        self._config = config
        self._tokens = AsyncTokenManager(self._fetch_token, name="ClearPass")
        self._http = httpx.AsyncClient(
            base_url=config.server,
            verify=config.verify_ssl,
            timeout=_REQUEST_TIMEOUT,
        )

    @property
    def server(self) -> str:
        """Return the configured ClearPass API base URL."""
        return str(self._http.base_url)

    async def aclose(self) -> None:
        """Close the underlying httpx client. Called from ``server.py:lifespan``."""
        await self._http.aclose()

    async def _fetch_token(self) -> TokenResult:
        """Fetch strategy for :class:`AsyncTokenManager` — one ``/oauth`` POST.

        Faithful port of the old ``ClearPassTokenManager._refresh`` (same JSON
        body, same error messages).
        """
        payload = {
            "grant_type": "client_credentials",
            "client_id": self._config.client_id,
            "client_secret": self._config.client_secret,
        }
        logger.info("ClearPass: requesting new OAuth2 access token")
        try:
            response = await self._http.post("/oauth", json=payload, timeout=_AUTH_TIMEOUT)
        except httpx.HTTPError as e:
            raise ClearPassAuthError(f"ClearPass OAuth2 request failed: {e}") from e

        if response.status_code != 200:
            raise ClearPassAuthError(f"ClearPass OAuth2 failed with HTTP {response.status_code}: {response.text[:200]}")

        try:
            data = response.json()
        except ValueError as e:
            raise ClearPassAuthError(f"ClearPass OAuth2 returned non-JSON body: {response.text[:200]}") from e

        token = data.get("access_token")
        if not token:
            detail = data.get("detail") or data.get("error_description") or data
            raise ClearPassAuthError(f"ClearPass OAuth2 response missing access_token: {detail}")

        logger.info("ClearPass: obtained token {}", mask_secret(token))
        expires_in = float(data.get("expires_in", _DEFAULT_TOKEN_TTL_SECS))
        return TokenResult(token=token, expires_in=expires_in)

    @staticmethod
    def _decode(response: httpx.Response, accept: str) -> Any:
        """Mirror pyclearpass's response decoding exactly.

        JSON accepts: ``json.loads`` of the text with a raw-text fallback.
        Anything else: raw bytes.
        """
        if "json" in accept:
            try:
                return json.loads(response.text)
            except json.JSONDecodeError:
                return response.text
        return response.content

    async def request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json_body: Any = None,
        accept: str = "application/json",
    ) -> Any:
        """Send an authenticated request; pyclearpass-compatible return contract.

        Args:
            method: HTTP verb, lowercase or uppercase (``get``/``post``/...).
            path: API path starting with ``/`` (e.g. ``/guest/{id}`` resolved),
                appended to the configured server base URL.
            params: Query-string parameters. pyclearpass parity: ``None`` and
                ``""`` entries are dropped, and dict values are compact-JSON
                encoded (how ClearPass ``filter`` params travel).
            json_body: JSON request body (dict/list), omitted when ``None``.
                pyclearpass parity: top-level ``""``-valued keys of dict
                bodies are dropped before sending (``_remove_empty_keys``).
            accept: ``accept`` header / response decoding mode.

        Returns:
            Decoded JSON (dict/list), raw text on JSON-decode failure, or raw
            bytes for non-JSON accepts. **Error bodies are returned, not
            raised** — callers inspect ``{"status": ..., "title": ...}`` dicts
            exactly as they did with pyclearpass.

        Raises:
            ClearPassAuthError: When token acquisition itself fails.
            httpx.HTTPError: On transport-level failures (connect, timeout).
        """
        token = await self._tokens.get_token()
        body = await self._send(method, path, params, json_body, accept, token)
        if not _is_auth_error(body):
            return body

        logger.info(
            "ClearPass: auth error on {} {} — refreshing token and retrying once",
            method.upper(),
            path,
        )
        try:
            token = await self._tokens.refresh()
        except ClearPassAuthError as e:
            logger.warning("ClearPass: token refresh failed — {}", e)
            return body
        return await self._send(method, path, params, json_body, accept, token)

    async def _send(
        self,
        method: str,
        path: str,
        params: dict[str, Any] | None,
        json_body: Any,
        accept: str,
        token: str,
    ) -> Any:
        kwargs: dict[str, Any] = {
            "headers": {
                "Authorization": f"Bearer {token}",
                "accept": accept,
            }
        }
        if params:
            cleaned = {k: v for k, v in params.items() if v is not None and v != ""}
            kwargs["params"] = {
                k: json.dumps(v, separators=(",", ":"), ensure_ascii=False) if isinstance(v, dict) else v
                for k, v in cleaned.items()
            }
        if json_body is not None:
            if isinstance(json_body, dict):
                json_body = {k: v for k, v in json_body.items() if v != ""}
            kwargs["json"] = json_body
        response = await self._http.request(method.upper(), path, **kwargs)
        return self._decode(response, accept)

    async def health_check(self) -> bool:
        """Probe credentials by acquiring a token. Returns True if it works."""
        await self._tokens.get_token()
        return True


def create_client(secrets: ClearPassSecrets) -> ClearPassClient:
    """Build a new :class:`ClearPassClient` from config secrets.

    Construction is cheap and non-blocking — the first API call triggers the
    initial token fetch.
    """
    return ClearPassClient(secrets)


async def get_clearpass_client() -> ClearPassClient:
    """Retrieve the shared ClearPassClient from the lifespan context.

    Raises:
        ToolError: If ClearPass is not configured or the client is unavailable.
    """
    ctx = get_context()
    client: ClearPassClient | None = ctx.lifespan_context.get("clearpass_client")
    if client is None:
        raise ToolError(
            {
                "status_code": 503,
                "message": "ClearPass API client not available. Check your ClearPass credentials.",
            }
        )
    return client


def format_http_error(exc: BaseException) -> dict[str, Any]:
    """Shape any exception into a consistent dict for tool returns.

    Surfaces status code and response body for ``httpx.HTTPStatusError``;
    everything else falls back to a generic shape so call sites can use this
    helper uniformly inside broad ``except Exception`` blocks. Same pattern
    used by every other platform.
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
