"""Axis Atmos Cloud REST API client.

Auth: static bearer token, manually generated in the Axis admin portal at
*Settings → Admin API → New API Token*. The user picks read/write scope and
expiration; there is no refresh endpoint. On 401 the only recourse is to
regenerate the token in the portal — we surface a clear error and let the
operator handle it.

Base URL: ``https://admin-api.axissecurity.com/api/v1.0``.

JWT-exp decoding is intentionally NOT in this PR — it lands in Wave 2.
"""

from __future__ import annotations

import asyncio
import json
from typing import Any

import httpx
from fastmcp.exceptions import ToolError
from fastmcp.server.dependencies import get_context
from loguru import logger

from hpe_networking_mcp.config import AxisSecrets
from hpe_networking_mcp.utils.logging import mask_secret

_AXIS_BASE_URL = "https://admin-api.axissecurity.com/api/v1.0"
_REQUEST_TIMEOUT = 30.0


class AxisAuthError(RuntimeError):
    """Raised when the Axis API token is missing or rejected."""


class AxisClient:
    """Async Axis Atmos Cloud REST API client.

    Static-token auth — token comes from config and is never refreshed.
    On 401 we raise a clear error pointing operators at the portal.
    """

    def __init__(self, config: AxisSecrets) -> None:
        self._config = config
        self._token: str = config.api_token
        self._lock = asyncio.Lock()
        self._http = httpx.AsyncClient(
            base_url=_AXIS_BASE_URL,
            timeout=_REQUEST_TIMEOUT,
        )
        logger.info("Axis: client initialized (token: {})", mask_secret(self._token))

    @property
    def base_url(self) -> str:
        """Return the configured base URL."""
        return _AXIS_BASE_URL

    async def aclose(self) -> None:
        """Close the underlying httpx client. Called from server.py:lifespan."""
        await self._http.aclose()

    def _auth_headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self._token}",
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
        """Send an authenticated request.

        Args:
            method: HTTP method.
            path: Path starting with ``/`` (e.g. ``/Connectors``). The
                ``/api/v1.0`` prefix is already in the base URL.
            json_body: Optional JSON payload.
            params: Optional query parameters.
            timeout: Optional per-call timeout override (seconds).

        Returns:
            The httpx.Response after ``raise_for_status()``.

        Raises:
            AxisAuthError: On 401 — token expired or revoked; regenerate in the portal.
            httpx.HTTPStatusError: On other 4xx/5xx.
            httpx.HTTPError: On transport errors.
        """
        kwargs: dict[str, Any] = {"headers": self._auth_headers()}
        if json_body is not None:
            kwargs["json"] = json_body
        if params:
            kwargs["params"] = params
        if timeout is not None:
            kwargs["timeout"] = timeout

        response = await self._http.request(method, path, **kwargs)
        if response.status_code == 401:
            raise AxisAuthError(
                "Axis API returned 401. The API token is missing, expired, or revoked. "
                "Regenerate the token at Settings → Admin API → New API Token in the Axis portal "
                "and update the axis_api_token secret."
            )
        response.raise_for_status()
        return response

    async def get_json(self, path: str, **kwargs: Any) -> Any:
        """Shortcut for a GET that returns parsed JSON."""
        response = await self.request("GET", path, **kwargs)
        return response.json()

    async def health_check(self) -> bool:
        """Probe the Axis ``/Health`` endpoint. Returns True if reachable.

        Used by ``platforms/health.py:_probe_axis()``.
        """
        # /Health is documented in the Axis API at /api/v1.0/Health and
        # returns 200 with a small JSON body when the platform is up.
        await self.request("GET", "/Health")
        return True


async def get_axis_client() -> AxisClient:
    """Retrieve the shared AxisClient from the lifespan context.

    Raises:
        ToolError: If Axis is not configured or the client is unavailable.
    """
    ctx = get_context()
    client: AxisClient | None = ctx.lifespan_context.get("axis_client")
    if client is None:
        raise ToolError(
            {
                "status_code": 503,
                "message": "Axis API client not available. Check your axis_api_token secret.",
            }
        )
    return client


def format_http_error(exc: BaseException) -> dict[str, Any]:
    """Shape any exception into a consistent dict for tool returns."""
    if isinstance(exc, httpx.HTTPStatusError):
        status = exc.response.status_code
        text = exc.response.text[:500]
        try:
            body: Any = exc.response.json()
        except (ValueError, json.JSONDecodeError):
            body = text
        return {"status_code": status, "message": str(exc), "body": body}
    return {"status_code": 0, "message": str(exc), "body": None}
