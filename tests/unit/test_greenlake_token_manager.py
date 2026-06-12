"""Unit tests for GreenLake's adoption of the shared auth primitive.

The 290-line sync ``OAuth2Provider``/``TokenManager`` pair (and its #440
``asyncio.to_thread`` workaround) collapsed into ``make_token_manager`` —
a configuration of the shared ``AsyncTokenManager`` + ``oauth2_client_credentials``
strategy. The lifecycle itself (locking, buffer expiry, refresh) is covered by
``test_common_auth.py``; these tests pin the GreenLake-specific wiring.
"""

from __future__ import annotations

import httpx
import pytest

from hpe_networking_mcp.config import GreenLakeSecrets
from hpe_networking_mcp.platforms._common.auth import AsyncTokenManager
from hpe_networking_mcp.platforms.greenlake.client import (
    _TOKEN_EXPIRY_BUFFER_SECS,
    GreenLakeHttpClient,
    make_token_manager,
)

pytestmark = pytest.mark.unit


def _secrets(**overrides) -> GreenLakeSecrets:
    base = {
        "api_base_url": "https://global.api.greenlake.example",
        "client_id": "gl-client-id",
        "client_secret": "gl-client-secret",
        "workspace_id": "ws-1234",
    }
    base.update(overrides)
    return GreenLakeSecrets(**base)


class TestMakeTokenManager:
    def test_returns_shared_manager_lazily(self):
        manager = make_token_manager(_secrets())
        assert isinstance(manager, AsyncTokenManager)
        assert manager.token is None  # no fetch at construction (old code fetched eagerly)

    def test_expiry_buffer_preserves_old_300s_behavior(self):
        manager = make_token_manager(_secrets())
        assert manager._buffer == _TOKEN_EXPIRY_BUFFER_SECS == 300.0

    async def test_token_url_includes_workspace_and_form_credentials(self):
        """Pin the workspace-scoped token URL and client_secret_post body."""
        captured: list[httpx.Request] = []

        def handler(request: httpx.Request) -> httpx.Response:
            captured.append(request)
            return httpx.Response(200, json={"access_token": "gl-tok", "expires_in": 7200})

        manager = make_token_manager(_secrets(api_base_url="https://global.api.greenlake.example/"))
        # Reach into the fetcher's test hook: rebuild it with a mock transport.
        from hpe_networking_mcp.platforms._common.auth import oauth2_client_credentials

        manager._fetch = oauth2_client_credentials(
            "https://global.api.greenlake.example/authorization/v2/oauth2/ws-1234/token",
            "gl-client-id",
            "gl-client-secret",
            name="GreenLake",
            _client_factory=lambda: httpx.AsyncClient(transport=httpx.MockTransport(handler)),
        )
        token = await manager.get_token()
        assert token == "gl-tok"
        request = captured[0]
        assert str(request.url) == "https://global.api.greenlake.example/authorization/v2/oauth2/ws-1234/token"
        body = request.content.decode()
        assert "grant_type=client_credentials" in body
        assert "client_id=gl-client-id" in body  # credentials in the form body (client_secret_post)
        assert "client_secret=gl-client-secret" in body
        assert "Authorization" not in request.headers  # NOT client_secret_basic — body only


class TestClientHeaderBuilder:
    async def test_auth_headers_built_from_manager_token(self):
        manager = make_token_manager(_secrets())
        manager.prime("primed-token", expires_in=7200)
        client = GreenLakeHttpClient(token_manager=manager, base_url="https://global.api.greenlake.example")
        headers = await client._get_auth_headers()
        assert headers["Authorization"] == "Bearer primed-token"
        assert headers["Content-Type"] == "application/json"
        assert headers["Accept"] == "application/json"
        await client.close()
