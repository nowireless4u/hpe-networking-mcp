"""Async httpx client for the Aruba EdgeConnect (Silver Peak) Orchestrator REST API.

The Orchestrator exposes two authentication modes; this client supports both,
chosen by which credentials are configured:

  * **API key** (``edgeconnect_api_key``) — sent as the ``X-Auth-Token`` header
    on every request. No login handshake. This is the SDK's
    ``Orchestrator(api_key=...)`` path (verified: ``self.headers =
    {"X-Auth-Token": api_key}``).
  * **Username/password** (``edgeconnect_user`` + ``edgeconnect_password``) —
    ``POST /authentication/login`` establishes a session cookie jar; the
    ``orchCsrfToken`` cookie is echoed back as the ``X-XSRF-TOKEN`` header on
    later requests (required when Orchestrator's "Enforce CSRF Check" is on).
    A 401 forces one re-login; ``aclose()`` logs the session out.

Every request carries ``?source=menu_rest_apis_id`` — the Orchestrator tags
REST-API traffic by source, matching pyedgeconnect. The base path is
``/gms/rest`` (so the effective base URL is ``https://<host>/gms/rest``).

We deliberately do NOT depend on the ``pyedgeconnect`` SDK at runtime — it is
sync-only and the SDK-removal policy (#468/#470) ports vendor auth flows to
async httpx directly. The documented raw-``requests`` login flow is the
blueprint this mirrors.
"""

from __future__ import annotations

import json
import re
from typing import Any, Literal

import httpx
from fastmcp.exceptions import ToolError
from fastmcp.server.dependencies import get_context
from loguru import logger

from hpe_networking_mcp.config import EdgeConnectSecrets
from hpe_networking_mcp.platforms._common.auth import AsyncTokenManager, AuthError, TokenResult
from hpe_networking_mcp.utils.logging import mask_secret

__all__ = [
    "EdgeConnectAuthError",
    "EdgeConnectClient",
    "format_http_error",
    "get_edgeconnect_client",
]

_AUTH_TIMEOUT = 15.0
_REQUEST_TIMEOUT = 30.0
_HEALTH_TIMEOUT = 10.0

# Orchestrator tags REST-API traffic by source; pyedgeconnect appends this to
# every call. Harmless when absent, so we always send it.
_SOURCE_PARAM = {"source": "menu_rest_apis_id"}
# CSRF cookie set on login when "Enforce CSRF Check" is enabled; echoed back as
# the X-XSRF-TOKEN header on subsequent requests.
_CSRF_COOKIE = "orchCsrfToken"
# Sentinel "token" for session auth when CSRF enforcement is OFF: there is no
# CSRF value, but AsyncTokenManager rejects an empty token, and the session
# cookie (carried by the httpx jar) is what actually authenticates. This marks
# "logged in" without emitting an X-XSRF-TOKEN header.
_SESSION_SENTINEL = "__edgeconnect_session__"  # noqa: S105 — not a credential

# Redact the API key / CSRF token from any logged header line.
_AUTH_HEADER_RE = re.compile(r"(X-Auth-Token|X-XSRF-TOKEN)\s*[:=]\s*[^\s,;]+", re.IGNORECASE)


def _sanitize_for_log(value: str) -> str:
    """Redact X-Auth-Token / X-XSRF-TOKEN values for logging."""
    return _AUTH_HEADER_RE.sub(r"\1=<redacted>", str(value))


class EdgeConnectAuthError(AuthError):
    """Raised when the Orchestrator login handshake fails."""


class EdgeConnectClient:
    """Async EdgeConnect Orchestrator REST client with cookie-session or API-key auth.

    The constructor performs NO HTTP I/O — login is lazy and serialized through
    the shared :class:`AsyncTokenManager`, so concurrent first-callers never
    fire parallel logins. In API-key mode there is no login at all; the
    "token" is simply the static key.

    Usage in tools::

        client = await get_edgeconnect_client()
        data = (await client.request("GET", "/appliance")).json()
        return data
    """

    def __init__(self, config: EdgeConnectSecrets) -> None:
        """Initialize the client. No HTTP calls are made here.

        Args:
            config: EdgeConnect credentials and connection settings.
        """
        self._config = config
        self._use_api_key = bool(config.api_key)
        self._tokens = AsyncTokenManager(self._fetch_token, name="EdgeConnect")
        self._http = self._make_http_client()
        if config.verify_ssl is False:
            logger.warning(
                "EdgeConnect: SSL verification disabled — operator opted in via edgeconnect_verify_ssl=false"
            )

    def _make_http_client(self) -> httpx.AsyncClient:
        """Create a fresh httpx.AsyncClient (cookie jar enabled) with log hooks."""

        async def _log_request(request: httpx.Request) -> None:
            logger.info("EdgeConnect HTTP → {} {}", request.method, request.url.path)

        async def _log_response(response: httpx.Response) -> None:
            logger.info("EdgeConnect HTTP ← {} {}", response.status_code, response.url.path)

        return httpx.AsyncClient(
            base_url=f"https://{self._config.host}/gms/rest",
            verify=self._config.verify_ssl,
            timeout=_REQUEST_TIMEOUT,
            event_hooks={"request": [_log_request], "response": [_log_response]},
        )

    @property
    def server(self) -> str:
        """Return the configured Orchestrator host."""
        return str(self._config.host)

    async def aclose(self) -> None:
        """Log out the session (user/pass mode only) and close the httpx client."""
        if not self._use_api_key and self._tokens.token is not None:
            try:
                await self._http.get("/authentication/logout", params=_SOURCE_PARAM, timeout=_HEALTH_TIMEOUT)
            except httpx.HTTPError as exc:
                logger.debug("EdgeConnect: logout failed (ignored): {}", exc)
        await self._http.aclose()

    async def _fetch_token(self) -> TokenResult:
        """Auth fetch strategy for :class:`AsyncTokenManager`.

        API-key mode: returns the static key (never expires; a 401 means a bad
        key, so re-fetch yields the same value and the second attempt fails
        cleanly). User/pass mode: performs the login POST, lets the httpx cookie
        jar capture the session, and returns the ``orchCsrfToken`` value (or an
        empty placeholder when CSRF enforcement is off — the session cookie
        alone authenticates).

        Raises:
            EdgeConnectAuthError: On transport error, non-200 login, or missing
                credentials.
        """
        if self._use_api_key:
            key = self._config.api_key or ""
            logger.info("EdgeConnect: using API key {}", mask_secret(key))
            return TokenResult(key)

        if not (self._config.user and self._config.password):
            raise EdgeConnectAuthError("EdgeConnect: no api_key and no user/password configured.")

        logger.info("EdgeConnect: logging in to {} as {}", self._config.host, self._config.user)
        # Clear any stale session cookies before re-logging in (preserves the
        # persistent _http and any test-installed MockTransport).
        self._http.cookies.clear()
        try:
            response = await self._http.post(
                "/authentication/login",
                params=_SOURCE_PARAM,
                json={
                    "user": self._config.user,
                    "password": self._config.password,
                    "token": "",  # nosec B105 — login API requires empty field, not a credential
                    "loginType": self._config.login_type,
                },
                timeout=_AUTH_TIMEOUT,
            )
        except httpx.HTTPError as exc:
            raise EdgeConnectAuthError(f"EdgeConnect login request failed: {exc}") from exc

        if response.status_code != 200:
            raise EdgeConnectAuthError(
                f"EdgeConnect login failed with HTTP {response.status_code}: {response.text[:200]}"
            )

        csrf = self._http.cookies.get(_CSRF_COOKIE) or ""
        if csrf:
            logger.info("EdgeConnect: login OK, CSRF token captured {}", mask_secret(csrf))
        else:
            logger.info("EdgeConnect: login OK (no CSRF enforcement — session cookie only)")
        # The CSRF value doubles as the cache token; when CSRF is off, fall back
        # to a non-empty sentinel (the session cookie on the jar authenticates,
        # and AsyncTokenManager rejects an empty token).
        return TokenResult(csrf or _SESSION_SENTINEL)

    def _auth_headers(self, token: str) -> dict[str, str]:
        """Build auth headers for a request.

        API-key mode attaches ``X-Auth-Token``; user/pass mode attaches
        ``X-XSRF-TOKEN`` when a CSRF token is present (the session cookie,
        carried by the httpx jar, does the rest).
        """
        headers = {"Content-Type": "application/json", "Accept": "application/json"}
        if self._use_api_key:
            headers["X-Auth-Token"] = token
        elif token and token != _SESSION_SENTINEL:
            headers["X-XSRF-TOKEN"] = token
        return headers

    async def request(
        self,
        method: Literal["GET", "POST", "PUT", "DELETE"],
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json_body: Any = None,
        headers: dict[str, Any] | None = None,
        timeout: float | None = None,
    ) -> httpx.Response:
        """Send an authenticated request, refreshing auth once on 401.

        The ``source`` query param is injected on every call; the session
        cookie (user/pass) or ``X-Auth-Token`` (API key) carries auth.

        Args:
            method: HTTP method (GET/POST/PUT/DELETE).
            path: Path under ``/gms/rest`` (e.g. ``/appliance``).
            params: Optional additional query parameters.
            json_body: Optional JSON request body.
            headers: Optional extra request headers (merged over the auth headers).
            timeout: Per-call timeout override in seconds.

        Returns:
            The httpx.Response after ``raise_for_status()``.
        """
        token = await self._tokens.get_token()
        merged_params = {**_SOURCE_PARAM, **(params or {})}
        kwargs: dict[str, Any] = {
            "headers": {**self._auth_headers(token), **(headers or {})},
            "params": merged_params,
        }
        if json_body is not None:
            kwargs["json"] = json_body
        if timeout is not None:
            kwargs["timeout"] = timeout

        response = await self._http.request(method, path, **kwargs)
        if response.status_code == 401:
            logger.info("EdgeConnect: 401 on {} {} — refreshing auth once", method, path)
            token = await self._tokens.refresh()
            kwargs["headers"] = {**self._auth_headers(token), **(headers or {})}
            response = await self._http.request(method, path, **kwargs)
        response.raise_for_status()
        return response

    async def health_check(self) -> bool:
        """Probe reachability + credentials. Returns True on success.

        Acquires auth (login or key) then performs a lightweight authenticated
        GET against ``/authentication/loginStatus``.
        """
        await self.request("GET", "/authentication/loginStatus", timeout=_HEALTH_TIMEOUT)
        return True


async def get_edgeconnect_client() -> EdgeConnectClient:
    """Retrieve the shared client from the lifespan context.

    Raises:
        ToolError: 503 when EdgeConnect is not configured / failed to init.
    """
    ctx = get_context()
    client: EdgeConnectClient | None = ctx.lifespan_context.get("edgeconnect_client")
    if client is None:
        raise ToolError(
            {
                "status_code": 503,
                "message": "EdgeConnect API client not available. Check your credentials.",
            }
        )
    return client


async def edgeconnect_request(
    ctx: Any,
    method: Literal["GET", "POST", "PUT", "DELETE"],
    path: str,
    *,
    query_params: dict[str, Any] | None = None,
    header_params: dict[str, Any] | None = None,
    body: Any = None,
) -> Any:
    """Transport shim for generated tools — fetch client, send, return parsed JSON.

    Reads the shared client from the lifespan context, sends the request, and
    returns parsed JSON (or raw text for non-JSON bodies, or a small status dict
    for empty 2xx bodies). Any HTTP/transport failure is re-raised as a
    ``ToolError`` shaped by :func:`format_http_error`.

    Args:
        ctx: The FastMCP request context (carries ``lifespan_context``).
        method: HTTP method (GET/POST/PUT/DELETE).
        path: Path under ``/gms/rest`` (e.g. ``/appliance``).
        query_params: Optional query parameters.
        header_params: Optional request headers (spec-declared header params).
        body: Optional JSON request body.

    Returns:
        Parsed JSON, raw text, or ``{"status_code", "message"}`` for empty bodies.

    Raises:
        ToolError: 503 when the platform is not configured, or a shaped error
            on upstream HTTP/transport failure.
    """
    client: EdgeConnectClient | None = ctx.lifespan_context.get("edgeconnect_client")
    if client is None:
        raise ToolError(
            {
                "status_code": 503,
                "message": "EdgeConnect API client not available. Check your credentials.",
            }
        )
    try:
        response = await client.request(method, path, params=query_params, headers=header_params, json_body=body)
    except ToolError:
        raise
    except Exception as exc:
        raise ToolError(format_http_error(exc)) from exc

    if not response.content:
        return {"status_code": response.status_code, "message": "OK (empty response)"}
    try:
        return response.json()
    except ValueError:
        return response.text


def format_http_error(exc: BaseException) -> dict[str, Any]:
    """Shape any exception into a consistent dict for tool returns.

    Surfaces status code and response body for ``httpx.HTTPStatusError``;
    everything else falls back to a generic shape. Same pattern as every other
    platform.
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
