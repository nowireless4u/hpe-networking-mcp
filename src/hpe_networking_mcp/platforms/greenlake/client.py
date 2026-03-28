# (c) Copyright 2025 Hewlett Packard Enterprise Development LP
"""Async HTTP client for the HPE GreenLake API.

Ported from the per-service ``AuditLogsHttpClient`` / ``DevicesHttpClient`` etc.
into a single shared ``GreenLakeHttpClient``.
"""

from __future__ import annotations

from typing import Any

import httpx
from loguru import logger

from hpe_networking_mcp.platforms.greenlake.auth import TokenManager


class GreenLakeHttpClient:
    """Async HTTP client with automatic OAuth2 token management."""

    def __init__(self, token_manager: TokenManager, base_url: str) -> None:
        self.token_manager = token_manager
        self.base_url = base_url.rstrip("/")

        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(30.0),
            limits=httpx.Limits(max_connections=10, max_keepalive_connections=5),
        )

    # -- HTTP verbs ---------------------------------------------------------

    async def get(
        self,
        endpoint: str,
        params: dict[str, Any] | None = None,
        additional_headers: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """Perform an authenticated GET request."""
        url = f"{self.base_url}{endpoint}"
        headers = self._get_auth_headers()
        if additional_headers:
            headers.update(additional_headers)

        logger.debug("GET {}", url)
        try:
            response = await self.client.get(url, headers=headers, params=params)
            response.raise_for_status()
            return response.json()  # type: ignore[no-any-return]
        except httpx.HTTPStatusError as e:
            logger.error("HTTP error {}: {}", e.response.status_code, e.response.text)
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
        headers = self._get_auth_headers()
        if additional_headers:
            headers.update(additional_headers)

        logger.debug("POST {}", url)
        try:
            response = await self.client.post(url, headers=headers, json=data)
            response.raise_for_status()
            return response.json()  # type: ignore[no-any-return]
        except httpx.HTTPStatusError as e:
            logger.error("HTTP error {}: {}", e.response.status_code, e.response.text)
            raise
        except Exception as e:
            logger.error("Request failed: {}", str(e))
            raise

    # -- helpers ------------------------------------------------------------

    def _get_auth_headers(self) -> dict[str, str]:
        """Build auth + accept headers, refreshing the token if needed."""
        headers: dict[str, str] = self.token_manager.get_auth_headers()
        headers["Accept"] = "application/json"
        return headers

    async def close(self) -> None:
        """Close the underlying httpx client."""
        await self.client.aclose()

    async def __aenter__(self) -> GreenLakeHttpClient:
        return self

    async def __aexit__(self, exc_type: object, exc_val: object, exc_tb: object) -> None:
        await self.close()
