"""Unit tests for UXIClient — OAuth2 token management, HTTP helpers, cursor pagination.

TDD RED phase: tests are written before client.py implementation.
Covers UXI-AUTH-02, UXI-AUTH-03, UXI-AUTH-04 from the phase requirements.
"""

from __future__ import annotations

import inspect
import time
from unittest.mock import patch

import pytest

from hpe_networking_mcp.config import UXISecrets


def _make_secrets(**overrides) -> UXISecrets:
    base = {
        "client_id": "test-client-id",
        "client_secret": "test-client-secret",
    }
    base.update(overrides)
    return UXISecrets(**base)


@pytest.mark.unit
class TestNoPyhpeuxiImport:
    """UXI-AUTH-03: client.py must not import pyhpeuxi."""

    def test_pyhpeuxi_not_in_source(self):
        from hpe_networking_mcp.platforms.uxi import client as client_module

        src = inspect.getsource(client_module)
        assert "pyhpeuxi" not in src, "client.py must not import pyhpeuxi (UXI-AUTH-03)"


@pytest.mark.unit
class TestUXIClientConstants:
    """Verify module-level constants exist with correct values."""

    def test_token_url_constant(self):
        from hpe_networking_mcp.platforms.uxi.client import _TOKEN_URL

        assert _TOKEN_URL == "https://sso.common.cloud.hpe.com/as/token.oauth2"

    def test_base_url_constant(self):
        from hpe_networking_mcp.platforms.uxi.client import _UXI_BASE_URL

        assert _UXI_BASE_URL == "https://api.capenetworks.com/networking-uxi/v1alpha1"

    def test_token_buffer_secs_constant(self):
        from hpe_networking_mcp.platforms.uxi.client import _TOKEN_BUFFER_SECS

        assert _TOKEN_BUFFER_SECS == 60


@pytest.mark.unit
class TestUXIClientInit:
    """UXIClient initializes with correct defaults."""

    def test_init_sets_config(self):
        from hpe_networking_mcp.platforms.uxi.client import UXIClient

        secrets = _make_secrets()
        client = UXIClient(secrets)
        assert client._config is secrets

    def test_init_token_is_none(self):
        from hpe_networking_mcp.platforms.uxi.client import UXIClient

        client = UXIClient(_make_secrets())
        assert client._token is None

    def test_init_expires_at_is_zero(self):
        from hpe_networking_mcp.platforms.uxi.client import UXIClient

        client = UXIClient(_make_secrets())
        assert client._expires_at == 0.0

    def test_init_http_client_has_base_url(self):
        from hpe_networking_mcp.platforms.uxi.client import _UXI_BASE_URL, UXIClient

        client = UXIClient(_make_secrets())
        assert str(client._http.base_url).rstrip("/") == _UXI_BASE_URL.rstrip("/")


@pytest.mark.unit
class TestUXIClientTokenExpiry:
    """UXI-AUTH-04: Time-based token expiry with 60-second buffer."""

    async def test_ensure_token_calls_fetch_when_expires_at_zero(self):
        """_expires_at=0.0 means always-expired; _fetch_token_locked must be called."""
        from hpe_networking_mcp.platforms.uxi.client import UXIClient

        client = UXIClient(_make_secrets())
        assert client._expires_at == 0.0  # always expired

        fetch_called = []

        async def mock_fetch():
            fetch_called.append(True)
            client._token = "fresh-token"
            client._expires_at = time.time() + 7199

        client._fetch_token_locked = mock_fetch
        token = await client._ensure_token()
        assert fetch_called, "_fetch_token_locked was not called for expired token"
        assert token == "fresh-token"

    async def test_ensure_token_returns_cached_when_valid(self):
        """Valid cached token (within TTL) must be returned without re-fetching."""
        from hpe_networking_mcp.platforms.uxi.client import _TOKEN_BUFFER_SECS, UXIClient

        client = UXIClient(_make_secrets())
        client._token = "cached-token"
        # Set expiry well beyond the buffer
        client._expires_at = time.time() + _TOKEN_BUFFER_SECS + 600

        fetch_called = []

        async def mock_fetch():
            fetch_called.append(True)

        client._fetch_token_locked = mock_fetch
        token = await client._ensure_token()
        assert not fetch_called, "_fetch_token_locked should NOT be called for valid cached token"
        assert token == "cached-token"

    async def test_ensure_token_refreshes_when_within_buffer(self):
        """Token expiring within the 60-second buffer triggers a refresh."""
        from hpe_networking_mcp.platforms.uxi.client import _TOKEN_BUFFER_SECS, UXIClient

        client = UXIClient(_make_secrets())
        client._token = "about-to-expire"
        # Set expiry within the buffer window (30 seconds from now < 60 second buffer)
        client._expires_at = time.time() + (_TOKEN_BUFFER_SECS - 30)

        fetch_called = []

        async def mock_fetch():
            fetch_called.append(True)
            client._token = "refreshed-token"
            client._expires_at = time.time() + 7199

        client._fetch_token_locked = mock_fetch
        token = await client._ensure_token()
        assert fetch_called, "_fetch_token_locked must be called when token is within buffer"
        assert token == "refreshed-token"


@pytest.mark.unit
class TestUXIClientPaginationParams:
    """D-05/Pitfall 1: uxi_get() must use 'limit' and 'next', not 'page_size'/'cursor'."""

    async def test_uxi_get_with_cursor_passes_next_param(self):
        """next_cursor='abc' must produce params={'limit': 10, 'next': 'abc'}."""
        from hpe_networking_mcp.platforms.uxi.client import UXIClient

        client = UXIClient(_make_secrets())
        client._token = "tok"
        client._expires_at = time.time() + 9999

        captured_params = {}

        async def mock_get_json(path, *, params=None):
            captured_params.update(params or {})
            return {}

        client._get_json = mock_get_json
        await client.uxi_get("/sensors", next_cursor="abc", limit=10)
        assert captured_params.get("next") == "abc", "next_cursor should map to 'next' param"
        assert captured_params.get("limit") == 10
        assert "page_size" not in captured_params
        assert "cursor" not in captured_params

    async def test_uxi_get_without_cursor_omits_next_param(self):
        """next_cursor=None must NOT include 'next' in params."""
        from hpe_networking_mcp.platforms.uxi.client import UXIClient

        client = UXIClient(_make_secrets())
        client._token = "tok"
        client._expires_at = time.time() + 9999

        captured_params = {}

        async def mock_get_json(path, *, params=None):
            captured_params.update(params or {})
            return {}

        client._get_json = mock_get_json
        await client.uxi_get("/sensors", next_cursor=None, limit=10)
        assert "next" not in captured_params, "next_cursor=None should not produce 'next' param"
        assert captured_params.get("limit") == 10

    async def test_uxi_get_with_empty_string_cursor_omits_next_param(self):
        """next_cursor='' is falsy in Python — must NOT include 'next' in params (Pitfall 6)."""
        from hpe_networking_mcp.platforms.uxi.client import UXIClient

        client = UXIClient(_make_secrets())
        client._token = "tok"
        client._expires_at = time.time() + 9999

        captured_params = {}

        async def mock_get_json(path, *, params=None):
            captured_params.update(params or {})
            return {}

        client._get_json = mock_get_json
        await client.uxi_get("/sensors", next_cursor="", limit=10)
        assert "next" not in captured_params, "next_cursor='' (falsy) should not produce 'next' param"
        assert captured_params.get("limit") == 10


@pytest.mark.unit
class TestGetUXIClientHelper:
    """get_uxi_client() raises ToolError when lifespan context has uxi_client=None."""

    async def test_get_uxi_client_raises_tool_error_when_none(self):
        from fastmcp.exceptions import ToolError

        from hpe_networking_mcp.platforms.uxi.client import get_uxi_client

        class _FakeCtx:
            lifespan_context = {"uxi_client": None}

        with (
            patch("hpe_networking_mcp.platforms.uxi.client.get_context", return_value=_FakeCtx()),
            pytest.raises(ToolError),
        ):
            await get_uxi_client()

    async def test_get_uxi_client_returns_client_when_present(self):
        from hpe_networking_mcp.platforms.uxi.client import UXIClient, get_uxi_client

        client = UXIClient(_make_secrets())

        class _FakeCtx:
            lifespan_context = {"uxi_client": client}

        with patch("hpe_networking_mcp.platforms.uxi.client.get_context", return_value=_FakeCtx()):
            result = await get_uxi_client()
        assert result is client


@pytest.mark.unit
class TestClientIsolation:
    """UXI-AUTH-02: UXIClient has its own httpx.AsyncClient instance."""

    def test_uxi_client_has_own_http_client(self):
        """UXIClient._http must be an httpx.AsyncClient (isolated, not shared)."""
        import httpx

        from hpe_networking_mcp.platforms.uxi.client import UXIClient

        client = UXIClient(_make_secrets())
        assert isinstance(client._http, httpx.AsyncClient)


@pytest.mark.unit
class TestNoSemaphore:
    """UXI-DYN-03: UXIClient uses passive 429 handling only (D-07) — no semaphore."""

    def test_no_asyncio_semaphore_attribute(self):
        """UXIClient must not have a 'semaphore' or '_semaphore' attribute (D-07).

        Rate limiting is handled passively by RetryMiddleware — no proactive
        semaphore should be added to UXIClient.
        """
        from hpe_networking_mcp.platforms.uxi.client import UXIClient

        client = UXIClient(_make_secrets())
        assert not hasattr(client, "semaphore"), (
            "UXIClient has 'semaphore' attribute — passive 429 handling only (D-07)"
        )
        assert not hasattr(client, "_semaphore"), (
            "UXIClient has '_semaphore' attribute — passive 429 handling only (D-07)"
        )


@pytest.mark.unit
class TestFormatHttpError:
    """format_http_error() shapes exceptions into consistent dicts."""

    def test_http_status_error_extracts_status_code(self):
        import httpx

        from hpe_networking_mcp.platforms.uxi.client import format_http_error

        request = httpx.Request("GET", "https://example.com/api")
        response = httpx.Response(404, text="not found", request=request)
        exc = httpx.HTTPStatusError("404", request=request, response=response)
        result = format_http_error(exc)
        assert result["status_code"] == 404
        assert "not found" in result["body"] or result["body"] is not None

    def test_generic_exception_returns_status_zero(self):
        from hpe_networking_mcp.platforms.uxi.client import format_http_error

        exc = RuntimeError("connection refused")
        result = format_http_error(exc)
        assert result["status_code"] == 0
        assert result["body"] is None
        assert "connection or protocol error" in result["message"]
