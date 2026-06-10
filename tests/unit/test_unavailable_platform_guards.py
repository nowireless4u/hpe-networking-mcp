"""Unit tests for the unavailable/misconfigured-platform guards and async
token handling added for issues #442, #443, #444, #440.

These cover the defensive paths that fire when an optional platform is not
configured (or failed to initialize) so tools return a clear 503 ``ToolError``
instead of crashing with an internal ``AttributeError``, plus the GreenLake
token work moving off the event loop.
"""

from __future__ import annotations

import inspect
from types import SimpleNamespace
from typing import Any

import pytest
from fastmcp.exceptions import ToolError

pytestmark = pytest.mark.unit


def _ctx(**lifespan: Any) -> SimpleNamespace:
    """Minimal stand-in for the FastMCP request context."""
    return SimpleNamespace(lifespan_context=dict(lifespan))


# --------------------------------------------------------------------------- #
# #443 — Central connection guard + retry hardening
# --------------------------------------------------------------------------- #


class TestCentralUnavailableGuard:
    def test_get_central_conn_raises_503_when_none(self) -> None:
        from hpe_networking_mcp.platforms.central.utils import get_central_conn

        with pytest.raises(ToolError) as exc:
            get_central_conn(_ctx(central_conn=None))
        assert exc.value.args[0]["status_code"] == 503
        assert "Central" in exc.value.args[0]["message"]

    def test_get_central_conn_raises_503_when_missing(self) -> None:
        from hpe_networking_mcp.platforms.central.utils import get_central_conn

        with pytest.raises(ToolError) as exc:
            get_central_conn(_ctx())  # key absent entirely
        assert exc.value.args[0]["status_code"] == 503

    def test_get_central_conn_returns_conn_when_present(self) -> None:
        from hpe_networking_mcp.platforms.central.utils import get_central_conn

        sentinel = object()
        assert get_central_conn(_ctx(central_conn=sentinel)) is sentinel

    def test_retry_central_command_raises_503_when_conn_none(self) -> None:
        from hpe_networking_mcp.platforms.central.utils import retry_central_command

        with pytest.raises(ToolError) as exc:
            retry_central_command(None, "GET", "network-monitoring/v1/sites-health")
        assert exc.value.args[0]["status_code"] == 503

    def test_log_transport_error_does_not_crash_on_none_conn(self) -> None:
        # The original handler dereferenced ``central_conn.logger`` and raised a
        # second AttributeError when the conn was None. The safe logger must not.
        from hpe_networking_mcp.platforms.central.utils import _log_transport_error

        _log_transport_error(None, "transport error with no conn")  # must not raise

    def test_log_transport_error_prefers_conn_logger(self) -> None:
        from hpe_networking_mcp.platforms.central.utils import _log_transport_error

        calls: list[str] = []
        conn = SimpleNamespace(logger=SimpleNamespace(error=lambda msg: calls.append(msg)))
        _log_transport_error(conn, "boom")
        assert calls == ["boom"]


# --------------------------------------------------------------------------- #
# #444 / #440 — GreenLake client guard + async token headers
# --------------------------------------------------------------------------- #


class TestGreenLakeUnavailableGuard:
    def test_get_greenlake_client_raises_503_when_token_manager_none(self) -> None:
        from hpe_networking_mcp.platforms.greenlake.client import get_greenlake_client

        config = SimpleNamespace(greenlake=SimpleNamespace(api_base_url="https://gl.example.com"))
        with pytest.raises(ToolError) as exc:
            get_greenlake_client(_ctx(greenlake_token_manager=None, config=config))
        assert exc.value.args[0]["status_code"] == 503
        assert "GreenLake" in exc.value.args[0]["message"]

    def test_get_greenlake_client_raises_503_when_config_greenlake_none(self) -> None:
        from hpe_networking_mcp.platforms.greenlake.client import get_greenlake_client

        config = SimpleNamespace(greenlake=None)
        with pytest.raises(ToolError) as exc:
            get_greenlake_client(_ctx(greenlake_token_manager=object(), config=config))
        assert exc.value.args[0]["status_code"] == 503

    def test_get_greenlake_client_returns_client_when_configured(self) -> None:
        from hpe_networking_mcp.platforms.greenlake.client import GreenLakeHttpClient, get_greenlake_client

        config = SimpleNamespace(greenlake=SimpleNamespace(api_base_url="https://gl.example.com/"))
        client = get_greenlake_client(_ctx(greenlake_token_manager=object(), config=config))
        assert isinstance(client, GreenLakeHttpClient)
        assert client.base_url == "https://gl.example.com"  # trailing slash stripped


class TestGreenLakeAsyncTokenHeaders:
    def test_get_auth_headers_is_coroutine(self) -> None:
        # #440 — token acquisition runs off the event loop via asyncio.to_thread,
        # so the header builder must be a coroutine function now.
        from hpe_networking_mcp.platforms.greenlake.client import GreenLakeHttpClient

        assert inspect.iscoroutinefunction(GreenLakeHttpClient._get_auth_headers)

    async def test_get_auth_headers_runs_sync_token_manager_off_loop(self) -> None:
        from hpe_networking_mcp.platforms.greenlake.client import GreenLakeHttpClient

        # A synchronous token manager (as TokenManager really is) must still work
        # when awaited through to_thread, and Accept is appended.
        token_manager = SimpleNamespace(get_auth_headers=lambda: {"Authorization": "Bearer abc"})
        client = GreenLakeHttpClient(token_manager=token_manager, base_url="https://gl.example.com")
        try:
            headers = await client._get_auth_headers()
        finally:
            await client.close()
        assert headers["Authorization"] == "Bearer abc"
        assert headers["Accept"] == "application/json"


# --------------------------------------------------------------------------- #
# #442 — Mist getSelf startup resolver tolerates HTTP 200 non-JSON
# --------------------------------------------------------------------------- #


class _FakeResp:
    def __init__(self, status_code: int, text: str, *, json_exc: Exception | None = None, json_val: Any = None) -> None:
        self.status_code = status_code
        self.text = text
        self._json_exc = json_exc
        self._json_val = json_val

    def json(self) -> Any:
        if self._json_exc is not None:
            raise self._json_exc
        return self._json_val


class _FakeClient:
    def __init__(self, resp: _FakeResp) -> None:
        self._resp = resp

    async def get(self, path: str) -> _FakeResp:
        return self._resp


class TestMistGetSelfNonJson:
    async def test_http_200_non_json_returns_none(self) -> None:
        from hpe_networking_mcp.platforms.mist._client import resolve_org_id_from_self

        resp = _FakeResp(200, "<html>login portal</html>", json_exc=ValueError("not json"))
        result = await resolve_org_id_from_self(_FakeClient(resp))  # type: ignore[arg-type]
        assert result is None

    async def test_http_200_non_object_body_returns_none(self) -> None:
        from hpe_networking_mcp.platforms.mist._client import resolve_org_id_from_self

        resp = _FakeResp(200, "[]", json_val=["unexpected", "list"])
        result = await resolve_org_id_from_self(_FakeClient(resp))  # type: ignore[arg-type]
        assert result is None

    async def test_http_200_valid_json_resolves_org_id(self) -> None:
        from hpe_networking_mcp.platforms.mist._client import resolve_org_id_from_self

        body = {"privileges": [{"scope": "org", "org_id": "org-abc-123"}]}
        resp = _FakeResp(200, "{...}", json_val=body)
        result = await resolve_org_id_from_self(_FakeClient(resp))  # type: ignore[arg-type]
        assert result == "org-abc-123"
