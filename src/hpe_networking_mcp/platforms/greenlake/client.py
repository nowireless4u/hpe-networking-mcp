# (c) Copyright 2025 Hewlett Packard Enterprise Development LP
"""Async HTTP client for the HPE GreenLake API.

Ported from the per-service ``AuditLogsHttpClient`` /
``DevicesHttpClient`` etc. into a single shared
``GreenLakeHttpClient``.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import httpx
from fastmcp.exceptions import ToolError
from loguru import logger

from hpe_networking_mcp.platforms._common.auth import AsyncTokenManager, oauth2_client_credentials
from hpe_networking_mcp.platforms._common.url import path_seg

if TYPE_CHECKING:
    from fastmcp import Context

    from hpe_networking_mcp.config import GreenLakeSecrets

# The old TokenManager refreshed when within 300 s of expiry — preserved here.
_TOKEN_EXPIRY_BUFFER_SECS = 300.0
_AUTH_TIMEOUT = 30.0


def make_token_manager(secrets: GreenLakeSecrets) -> AsyncTokenManager:
    """Build the GreenLake token manager on the shared auth primitive.

    Token endpoint: ``{api_base_url}/authorization/v2/oauth2/{workspace_id}/token``
    with the client-credentials grant, credentials in the form body
    (``client_secret_post`` — what the old ``OAuth2Provider`` sent).
    Construction is non-blocking; the first request fetches the token.
    """
    token_url = f"{secrets.api_base_url.rstrip('/')}/authorization/v2/oauth2/{path_seg(secrets.workspace_id)}/token"
    return AsyncTokenManager(
        oauth2_client_credentials(
            token_url,
            secrets.client_id,
            secrets.client_secret,
            name="GreenLake",
            timeout=_AUTH_TIMEOUT,
        ),
        name="GreenLake",
        expiry_buffer=_TOKEN_EXPIRY_BUFFER_SECS,
    )


def get_greenlake_client(ctx: Context) -> GreenLakeHttpClient:
    """Return a configured GreenLake client, or raise a clear 503 ToolError.

    GreenLake is optional: when its Docker secrets are absent or startup
    failed, ``server.py`` stores ``greenlake_token_manager = None`` and
    ``config.greenlake`` is ``None``. Tools that dereference those directly
    crash with an opaque ``AttributeError`` (issue #444). This helper checks
    both up front and raises an actionable ``ToolError`` instead, so a
    disabled/failed integration produces a recoverable "not configured"
    response rather than an internal error.

    Args:
        ctx: The FastMCP request context.

    Returns:
        A ``GreenLakeHttpClient`` bound to the configured base URL.

    Raises:
        ToolError: 503 when GreenLake is not configured or failed to start.
    """
    lifespan = ctx.lifespan_context
    token_manager = lifespan.get("greenlake_token_manager")
    config = lifespan.get("config")
    greenlake_cfg = getattr(config, "greenlake", None) if config is not None else None
    if token_manager is None or greenlake_cfg is None:
        raise ToolError(
            {
                "status_code": 503,
                "message": (
                    "GreenLake is not configured or failed to initialize. Provide the GreenLake "
                    "Docker secrets (greenlake_api_base_url, greenlake_client_id, "
                    "greenlake_client_secret, greenlake_workspace_id) and restart the server."
                ),
            }
        )
    return GreenLakeHttpClient(token_manager=token_manager, base_url=greenlake_cfg.api_base_url)


class GreenLakeHttpClient:
    """Async HTTP client with automatic OAuth2 token management."""

    def __init__(self, token_manager: AsyncTokenManager, base_url: str) -> None:
        self.token_manager = token_manager
        self.base_url = base_url.rstrip("/")

        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(30.0),
            limits=httpx.Limits(max_connections=10, max_keepalive_connections=5),
        )

    # -- HTTP verbs --------------------------------------------------------

    async def get(
        self,
        endpoint: str,
        params: dict[str, Any] | None = None,
        additional_headers: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """Perform an authenticated GET request."""
        url = f"{self.base_url}{endpoint}"
        headers = await self._get_auth_headers()
        if additional_headers:
            headers.update(additional_headers)

        logger.debug("GET {}", url)
        try:
            response = await self.client.get(url, headers=headers, params=params)
            response.raise_for_status()
            return response.json()  # type: ignore[no-any-return]
        except httpx.HTTPStatusError as e:
            logger.error(
                "HTTP error {}: {}",
                e.response.status_code,
                e.response.text,
            )
            raise
        except Exception as e:
            logger.error("Request failed: {}", str(e))
            raise

    async def post(
        self,
        endpoint: str,
        data: dict[str, Any] | None = None,
        additional_headers: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """Perform an authenticated POST request."""
        url = f"{self.base_url}{endpoint}"
        headers = await self._get_auth_headers()
        if additional_headers:
            headers.update(additional_headers)

        logger.debug("POST {}", url)
        try:
            response = await self.client.post(url, headers=headers, json=data)
            response.raise_for_status()
            return response.json()  # type: ignore[no-any-return]
        except httpx.HTTPStatusError as e:
            logger.error(
                "HTTP error {}: {}",
                e.response.status_code,
                e.response.text,
            )
            raise
        except Exception as e:
            logger.error("Request failed: {}", str(e))
            raise

    # -- helpers -----------------------------------------------------------

    async def _get_auth_headers(self) -> dict[str, str]:
        """Build auth + accept headers, refreshing if needed.

        Token acquisition runs through the shared ``AsyncTokenManager`` —
        natively async, so a slow token endpoint can't block the event loop
        (the #440 ``to_thread`` workaround is no longer needed).
        """
        token = await self.token_manager.get_token()
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    async def close(self) -> None:
        """Close the underlying httpx client."""
        await self.client.aclose()

    async def __aenter__(self) -> GreenLakeHttpClient:
        return self

    async def __aexit__(
        self,
        exc_type: object,
        exc_val: object,
        exc_tb: object,
    ) -> None:
        await self.close()
