"""Async httpx client for the Aruba OS 8 / Mobility Conductor REST API.

Mirrors the structural template of platforms/apstra/client.py with these AOS8 deltas:
  * Auth via UIDARUBA: cookie jar + query-param injection (NOT a bearer header).
  * Method whitelist: GET and POST only — AOS8 does not support PUT/PATCH/DELETE.
  * Application-level error detection: _global_result.status != "0" -> AOS8APIError.
  * URL log sanitizer redacts UIDARUBA=<value> from any logged URL.
  * Explicit ``if ... raise`` instead of ``assert`` (python -O hazard fix).

References:
  - .planning/phases/02-api-client/02-RESEARCH.md §Architecture Patterns 1-7
  - https://developer.arubanetworks.com/aos8/docs/login
  - https://developer.arubanetworks.com/aos8/docs/showcommand-api
"""

from __future__ import annotations

import asyncio
import re
from typing import Any, Literal

import httpx
from loguru import logger

from hpe_networking_mcp.config import AOS8Secrets
from hpe_networking_mcp.utils.logging import mask_secret

__all__ = ["AOS8Client", "AOS8AuthError", "AOS8APIError"]

_AUTH_TIMEOUT = 15.0
_REQUEST_TIMEOUT = 30.0
_HEALTH_TIMEOUT = 10.0

_UIDARUBA_RE = re.compile(r"(UIDARUBA=)[^&\s]+", re.IGNORECASE)
# AOS 8 carries the same UIDARUBA token in a SESSION cookie on every
# request and rotates it via Set-Cookie on every response. Match the
# value through the next `;`, `,`, or whitespace so a redacted Set-Cookie
# header keeps its trailing attributes (`path=/`, `HttpOnly`, ...) intact.
_SESSION_COOKIE_RE = re.compile(r"(SESSION=)[^;,\s]+", re.IGNORECASE)


def _sanitize_for_log(value: str | httpx.URL) -> str:
    """Redact UIDARUBA query values and SESSION cookie values for logging.

    Applies to URLs, raw query strings, ``Cookie`` request headers, and
    ``Set-Cookie`` response headers — every place the AOS 8 session token
    can appear in transport metadata.

    Args:
        value: The string (URL, header, or query) to sanitize.

    Returns:
        Same string with ``UIDARUBA=<value>`` and ``SESSION=<value>``
        replaced by ``UIDARUBA=<redacted>`` and ``SESSION=<redacted>``.
    """
    sanitized = _UIDARUBA_RE.sub(r"\1<redacted>", str(value))
    return _SESSION_COOKIE_RE.sub(r"\1<redacted>", sanitized)


# Back-compat alias — older import sites may still reference this name.
_sanitize_url_for_log = _sanitize_for_log


class AOS8AuthError(RuntimeError):
    """Raised when login fails (HTTP, JSON, or _global_result rejection)."""


class AOS8APIError(RuntimeError):
    """Raised when AOS8 returns 2xx with _global_result.status != '0'."""


class AOS8Client:
    """Async AOS8 REST API client with UIDARUBA token caching and 401-refresh retry.

    The constructor performs NO HTTP I/O — login is lazy and occurs on the
    first call to ``_ensure_token()``. An ``asyncio.Lock`` serializes token
    acquisition so concurrent callers never fire parallel logins.

    Usage in tools::

        client = ctx.lifespan_context["aos8_client"]
        data = await client.request("GET", "/v1/configuration/object/ap_group")
        return data.json()
    """

    def __init__(self, config: AOS8Secrets) -> None:
        """Initialize the client. No HTTP calls are made here.

        Args:
            config: AOS8 credentials and connection settings.
        """
        self._config = config
        self._lock = asyncio.Lock()
        self._token: str | None = None
        self._http = self._make_http_client()
        if config.verify_ssl is False:
            logger.warning("AOS8: SSL verification disabled — operator opted in via aos8_verify_ssl=false")

    def _make_http_client(self) -> httpx.AsyncClient:
        """Create a fresh httpx.AsyncClient with debug event hooks."""

        async def _log_request(request: httpx.Request) -> None:
            # The Cookie header carries SESSION=<UIDARUBA> and the query
            # string carries UIDARUBA=<UIDARUBA>; both must be redacted
            # before reaching the log sink. See issue #233.
            cookie_hdr = _sanitize_for_log(request.headers.get("cookie", "<none>"))
            params_str = _sanitize_for_log(str(request.url.params))
            logger.info(
                "AOS8 HTTP → {} {} | cookie={!r} | params={}",
                request.method,
                request.url.path,
                cookie_hdr,
                params_str,
            )

        async def _log_response(response: httpx.Response) -> None:
            # AOS 8 rotates the SESSION cookie on every successful response,
            # so the Set-Cookie header carries a fresh UIDARUBA each time.
            set_cookie = _sanitize_for_log(response.headers.get("set-cookie", "<none>"))
            logger.info(
                "AOS8 HTTP ← {} {} | set-cookie={}",
                response.status_code,
                response.url.path,
                set_cookie,
            )

        return httpx.AsyncClient(
            base_url=f"https://{self._config.host}:{self._config.port}",
            verify=self._config.verify_ssl,
            timeout=_REQUEST_TIMEOUT,
            event_hooks={"request": [_log_request], "response": [_log_response]},
        )

    @property
    def server(self) -> str:
        """Return ``host:port`` of the configured AOS8 controller.

        Returns:
            String in the form ``"host:port"``.
        """
        return f"{self._config.host}:{self._config.port}"

    async def _ensure_token(self) -> str:
        """Return the cached UIDARUBA token, acquiring one under the lock if needed.

        Returns:
            The UIDARUBA session token string.

        Raises:
            AOS8AuthError: If login fails or token is not set after login.
        """
        if self._token is not None:
            return self._token
        async with self._lock:
            if self._token is None:
                await self._login_locked()
        if self._token is None:
            raise AOS8AuthError("login completed without setting token")
        return self._token

    async def _refresh_token(self) -> str:
        """Force-refresh the UIDARUBA token under the lock.

        Returns:
            The new UIDARUBA session token string.

        Raises:
            AOS8AuthError: If the refresh login fails or token is not set.
        """
        async with self._lock:
            self._token = None
            await self._login_locked()
        if self._token is None:
            raise AOS8AuthError("refresh login completed without setting token")
        return self._token

    async def _login_locked(self) -> None:
        """Perform the login request. Caller must hold ``self._lock``.

        Posts credentials to ``/v1/api/login`` with form-encoded body.
        On success, stores the UIDARUBA token in ``self._token``.

        Raises:
            AOS8AuthError: On transport error, non-200 status, non-JSON response,
                or ``_global_result.status != "0"``.
        """
        logger.info("AOS8: requesting new session token from {}", self._config.host)
        # Clear any stale SESSION cookies from a prior (expired) session before
        # re-logging in — preserves the persistent _http (and any test-installed
        # MockTransport) while still giving AOS8 a clean cookie jar for login.
        self._http.cookies.clear()

        try:
            response = await self._http.post(
                "/v1/api/login",
                data={"username": self._config.username, "password": self._config.password},
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=_AUTH_TIMEOUT,
            )
        except httpx.HTTPError as exc:
            raise AOS8AuthError(f"AOS8 login request failed: {exc}") from exc

        if response.status_code != 200:
            raise AOS8AuthError(f"AOS8 login failed with HTTP {response.status_code}: {response.text[:200]}")

        try:
            body = response.json()
        except ValueError as exc:
            raise AOS8AuthError(f"AOS8 login returned non-JSON body: {response.text[:200]}") from exc

        gr: dict[str, Any] = body.get("_global_result") or {}
        if str(gr.get("status")) != "0":
            status_str = gr.get("status_str", "unknown")
            raise AOS8AuthError(f"AOS8 login rejected: {status_str}")

        token: str | None = gr.get("UIDARUBA")
        if not token:
            raise AOS8AuthError(f"AOS8 login response missing UIDARUBA field: {gr}")

        self._token = token
        logger.info("AOS8: obtained session token {}", mask_secret(token))

    def _check_global_result(self, response: httpx.Response) -> None:
        """Raise AOS8APIError if the response contains a non-zero _global_result.

        AOS8 often returns HTTP 200 with an application-level error embedded in
        ``_global_result.status``. This method inspects every 2xx JSON response.

        Args:
            response: The httpx response to inspect.

        Raises:
            AOS8APIError: If ``_global_result.status`` is present and not ``"0"``.
        """
        content_type = response.headers.get("content-type", "")
        if "json" not in content_type.lower():
            return
        try:
            body = response.json()
        except ValueError:
            return
        if not isinstance(body, dict):
            return
        gr = body.get("_global_result")
        if not isinstance(gr, dict):
            return
        status = str(gr.get("status"))
        if status not in ("0", "None"):
            status_str = gr.get("status_str", "unknown")
            raise AOS8APIError(f"AOS8 API error (status={status}): {status_str}")

    def _sync_token_from_cookie(self, response: httpx.Response) -> None:
        """Keep self._token in sync with the SESSION cookie AOS8 rotates on each response.

        AOS8 may issue a new SESSION cookie on any successful API response. If
        the cookie value differs from the cached token, update the token so the
        next request uses the current value rather than the stale one.

        Args:
            response: The httpx response to inspect for a rotated SESSION cookie.
        """
        session_cookie = response.cookies.get("SESSION")
        if session_cookie and session_cookie != self._token:
            logger.debug("AOS8: session token rotated — updating cached token")
            self._token = session_cookie

    async def request(
        self,
        method: Literal["GET", "POST"],
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json_body: Any = None,
        data: Any = None,
        timeout: float | None = None,
    ) -> httpx.Response:
        """Send an authenticated AOS8 request, refreshing the token once on 401.

        Only GET and POST are permitted; any other method raises ValueError.
        The UIDARUBA token is injected as a query parameter on every request.

        Args:
            method: HTTP method — must be "GET" or "POST".
            path: Path starting with "/v1/...".
            params: Optional additional query parameters.
            json_body: Optional JSON payload.
            data: Optional form-encoded payload.
            timeout: Per-call timeout override in seconds.

        Returns:
            The httpx.Response after ``raise_for_status()`` and
            ``_check_global_result()``.

        Raises:
            ValueError: If method is not GET or POST.
            AOS8AuthError: If token acquisition fails.
            AOS8APIError: If ``_global_result.status != "0"`` in the response.
            httpx.HTTPStatusError: On 4xx/5xx after retry.
            httpx.HTTPError: On transport errors.
        """
        method_up = method.upper()
        if method_up not in ("GET", "POST"):
            raise ValueError(f"AOS8 only supports GET and POST; got {method!r}")

        token = await self._ensure_token()
        merged_params: dict[str, Any] = {"UIDARUBA": token, **(params or {})}
        effective_timeout = timeout if timeout is not None else _REQUEST_TIMEOUT

        response = await self._http.request(
            method_up,
            path,
            params=merged_params,
            json=json_body if json_body is not None else None,
            data=data if data is not None else None,
            timeout=effective_timeout,
        )

        if response.status_code == 401:
            logger.info(
                "AOS8: 401 on {} {} — refreshing token once",
                method_up,
                _sanitize_url_for_log(path),
            )
            token = await self._refresh_token()
            merged_params = {"UIDARUBA": token, **(params or {})}
            response = await self._http.request(
                method_up,
                path,
                params=merged_params,
                json=json_body if json_body is not None else None,
                data=data if data is not None else None,
                timeout=effective_timeout,
            )

        response.raise_for_status()
        self._check_global_result(response)
        self._sync_token_from_cookie(response)
        return response

    async def health_check(self) -> dict[str, Any]:
        """Probe the controller by fetching show version output.

        Returns a dict with controller hostname and AOS software version,
        suitable for the server's health tool.

        Returns:
            Dict with keys ``hostname``, ``version``, and ``raw`` (full body).

        Raises:
            AOS8AuthError: If login fails.
            AOS8APIError: If the response contains a non-zero global result.
            httpx.HTTPStatusError: On HTTP error responses.
        """
        response = await self.request(
            "GET",
            "/v1/configuration/showcommand",
            params={"command": "show version"},
            timeout=_HEALTH_TIMEOUT,
        )
        self._sync_token_from_cookie(response)
        body: dict[str, Any] = response.json()

        hostname: str | None = body.get("Hostname") or body.get("hostname")
        if hostname is None:
            data = body.get("_data")
            hostname = data[0] if isinstance(data, list) and data else "unknown"

        version: str = body.get("Version") or body.get("version") or "unknown"
        return {"hostname": hostname, "version": version, "raw": body}

    async def aclose(self) -> None:
        """Log out from AOS8 and close the underlying httpx client.

        Attempts a POST to ``/v1/api/logout`` if a token is held. Errors during
        logout are caught and logged as warnings — shutdown must not fail because
        the controller is unreachable.
        """
        if self._token is not None:
            try:
                await self._http.post("/v1/api/logout", timeout=_AUTH_TIMEOUT)
                logger.info("AOS8: logged out cleanly")
            except Exception as exc:  # noqa: BLE001
                logger.warning("AOS8: logout failed during shutdown — {}", exc)
            finally:
                self._token = None
        await self._http.aclose()
