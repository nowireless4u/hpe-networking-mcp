"""Unit tests for CentralClient — the pycentral-compatible async replacement.

Pins the ``command()`` contract that all ~660 Central tools rely on through
``retry_central_command``: the ``{code, msg, headers}`` return dict, None
param stripping, empty-body omission, JSON serialization, Bearer auth, and
the 401 → refresh-once → retry flow.
"""

from __future__ import annotations

import json

import httpx
import pytest

from hpe_networking_mcp.config import CentralSecrets
from hpe_networking_mcp.platforms.central.client import (
    CentralClient,
    create_connection,
    verify_connection,
)


@pytest.mark.unit
class TestNoPycentralAnywhere:
    """The pycentral SDK was removed in v3.3.11.0 — no module under src/ may import it."""

    def test_no_pycentral_imports_in_src(self):
        import ast
        import pathlib

        import hpe_networking_mcp

        root = pathlib.Path(hpe_networking_mcp.__file__).parent
        offenders: list[str] = []
        for path in root.rglob("*.py"):
            tree = ast.parse(path.read_text())
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    if any(a.name.split(".")[0] == "pycentral" for a in node.names):
                        offenders.append(f"{path}:{node.lineno}")
                elif isinstance(node, ast.ImportFrom) and node.module and node.module.split(".")[0] == "pycentral":
                    offenders.append(f"{path}:{node.lineno}")
        assert not offenders, f"pycentral imports found (SDK was removed): {offenders}"

    def test_no_pycentral_in_lockfile(self):
        """A stale uv.lock kept INSTALLING pycentral for 7 releases after the
        SDK was removed from pyproject (#445) — `uv sync --frozen` skips the
        pyproject↔lock consistency check, so import guards alone can't see it.
        """
        import pathlib

        lockfile = pathlib.Path(__file__).resolve().parents[2] / "uv.lock"
        assert lockfile.is_file(), "uv.lock not found next to pyproject.toml"
        assert 'name = "pycentral"' not in lockfile.read_text(), (
            "pycentral is in uv.lock — regenerate the lock (uv lock); the SDK was removed in v3.3.11.0"
        )


def _make_secrets(**overrides) -> CentralSecrets:
    base = {
        "base_url": "https://central.example.test",
        "client_id": "central-client-id",
        "client_secret": "central-client-secret",
    }
    base.update(overrides)
    return CentralSecrets(**base)


def _make_client(handler, token: str = "test-token") -> CentralClient:
    """Build a CentralClient with a MockTransport and a primed token."""
    client = CentralClient(_make_secrets())
    client._http = httpx.AsyncClient(
        base_url="https://central.example.test",
        transport=httpx.MockTransport(handler),
    )
    client._tokens.prime(token, expires_in=3600)
    return client


@pytest.mark.unit
class TestCommandContract:
    async def test_returns_pycentral_shaped_dict(self):
        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(200, json={"items": [1, 2]}, headers={"X-Request-Id": "abc"})

        client = _make_client(handler)
        resp = await client.command(api_method="GET", api_path="network-monitoring/v1/aps")
        assert resp["code"] == 200
        assert resp["msg"] == {"items": [1, 2]}
        assert resp["headers"]["x-request-id"] == "abc"
        await client.aclose()

    async def test_non_json_body_returned_as_text(self):
        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(502, text="<html>bad gateway</html>")

        client = _make_client(handler)
        resp = await client.command(api_method="GET", api_path="x")
        assert resp["code"] == 502
        assert resp["msg"] == "<html>bad gateway</html>"
        await client.aclose()

    async def test_status_errors_not_raised(self):
        """pycentral parity: 4xx/5xx come back in code, never raised."""

        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(404, json={"error": "not found"})

        client = _make_client(handler)
        resp = await client.command(api_method="GET", api_path="missing")
        assert resp["code"] == 404
        await client.aclose()

    async def test_bearer_token_and_json_headers_sent(self):
        captured: list[httpx.Request] = []

        def handler(request: httpx.Request) -> httpx.Response:
            captured.append(request)
            return httpx.Response(200, json={})

        client = _make_client(handler, token="tok-xyz")
        await client.command(api_method="GET", api_path="network-monitoring/v1/aps")
        request = captured[0]
        assert request.headers["Authorization"] == "Bearer tok-xyz"
        assert request.headers["Content-Type"] == "application/json"
        assert request.headers["Accept"] == "application/json"
        await client.aclose()

    async def test_none_params_stripped(self):
        captured: list[httpx.Request] = []

        def handler(request: httpx.Request) -> httpx.Response:
            captured.append(request)
            return httpx.Response(200, json={})

        client = _make_client(handler)
        await client.command(
            api_method="GET",
            api_path="network-monitoring/v1/aps",
            api_params={"limit": 20, "filter": None, "sort": None},
        )
        assert captured[0].url.params.get("limit") == "20"
        assert "filter" not in captured[0].url.params
        assert "sort" not in captured[0].url.params
        await client.aclose()

    async def test_empty_body_not_sent(self):
        """pycentral parity: api_data={} / None must not send a request body."""
        captured: list[httpx.Request] = []

        def handler(request: httpx.Request) -> httpx.Response:
            captured.append(request)
            return httpx.Response(202, json={})

        client = _make_client(handler)
        await client.command(api_method="POST", api_path="x", api_data={})
        await client.command(api_method="POST", api_path="y", api_data=None)
        assert captured[0].content == b""
        assert captured[1].content == b""
        await client.aclose()

    async def test_dict_body_serialized_as_json(self):
        captured: list[httpx.Request] = []

        def handler(request: httpx.Request) -> httpx.Response:
            captured.append(request)
            return httpx.Response(200, json={})

        client = _make_client(handler)
        await client.command(api_method="POST", api_path="x", api_data={"name": "HQ", "enabled": True})
        assert json.loads(captured[0].content) == {"name": "HQ", "enabled": True}
        await client.aclose()

    async def test_path_appended_to_base_url(self):
        captured: list[httpx.Request] = []

        def handler(request: httpx.Request) -> httpx.Response:
            captured.append(request)
            return httpx.Response(200, json={})

        client = _make_client(handler)
        await client.command(api_method="GET", api_path="network-monitoring/v1/sites-health")
        assert str(captured[0].url) == "https://central.example.test/network-monitoring/v1/sites-health"
        await client.aclose()


@pytest.mark.unit
class Test401Refresh:
    async def test_401_refreshes_token_once_and_retries(self):
        from hpe_networking_mcp.platforms._common.auth import TokenResult

        calls: list[str] = []

        def handler(request: httpx.Request) -> httpx.Response:
            calls.append(request.headers["Authorization"])
            if len(calls) == 1:
                return httpx.Response(401, json={"error": "token expired"})
            return httpx.Response(200, json={"ok": True})

        client = _make_client(handler, token="stale-token")

        async def fresh_fetch() -> TokenResult:
            return TokenResult("fresh-token", expires_in=3600)

        client._tokens._fetch = fresh_fetch
        resp = await client.command(api_method="GET", api_path="x")
        assert resp["code"] == 200
        assert calls == ["Bearer stale-token", "Bearer fresh-token"]
        await client.aclose()

    async def test_second_401_returned_not_looped(self):
        from hpe_networking_mcp.platforms._common.auth import TokenResult

        count = 0

        def handler(request: httpx.Request) -> httpx.Response:
            nonlocal count
            count += 1
            return httpx.Response(401, json={"error": "still bad"})

        client = _make_client(handler)

        async def fetch() -> TokenResult:
            return TokenResult("another-token", expires_in=3600)

        client._tokens._fetch = fetch
        resp = await client.command(api_method="GET", api_path="x")
        assert resp["code"] == 401
        assert count == 2  # original + exactly one retry
        await client.aclose()


@pytest.mark.unit
class TestFactoriesAndHealth:
    def test_create_connection_returns_client_without_network_io(self):
        client = create_connection(_make_secrets())
        assert isinstance(client, CentralClient)
        assert client._tokens.token is None  # lazy: no token fetch at construction

    async def test_health_check_true_on_200(self):
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.url.path == "/network-monitoring/v1/sites-health"
            assert request.url.params.get("limit") == "1"
            return httpx.Response(200, json={"items": [], "total": 0})

        client = _make_client(handler)
        assert await client.health_check() is True
        await client.aclose()

    async def test_verify_connection_raises_runtime_error_on_failure(self):
        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(403, json={"error": "forbidden"})

        client = _make_client(handler)
        with pytest.raises(RuntimeError, match="connectivity check failed"):
            await verify_connection(client)
        await client.aclose()
