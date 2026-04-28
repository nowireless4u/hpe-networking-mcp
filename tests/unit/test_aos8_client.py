"""Wave 0 TDD test scaffold for AOS8Client.

Tests will fail with ImportError until Plan 02 creates client.py — that is the
correct RED state. Each test maps to one CLIENT-NN requirement from
.planning/phases/02-api-client/02-RESEARCH.md.
"""

from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Any

import httpx
import pytest

from hpe_networking_mcp.config import AOS8Secrets
from hpe_networking_mcp.platforms.aos8.client import (
    AOS8APIError,
    AOS8AuthError,
    AOS8Client,
)

pytestmark = pytest.mark.unit

_FIXTURES = Path(__file__).parent / "fixtures"
_LOGIN_OK = {"_global_result": {"status": "0", "UIDARUBA": "tok-supersecret-12345"}}


def _make_secrets(**overrides: Any) -> AOS8Secrets:
    base = {
        "host": "conductor.test",
        "port": 4343,
        "username": "admin",
        "password": "secret",
        "verify_ssl": True,
    }
    base.update(overrides)
    return AOS8Secrets(**base)


def _install_mock_transport(client: AOS8Client, handler) -> list[httpx.Request]:
    """Replace client._http with one driven by MockTransport. Returns request log."""
    calls: list[httpx.Request] = []

    def _wrapper(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        return handler(request)

    transport = httpx.MockTransport(_wrapper)
    client._http = httpx.AsyncClient(
        base_url=f"https://{client._config.host}:{client._config.port}",
        transport=transport,
        verify=client._config.verify_ssl,
    )
    return calls


class TestAOS8ClientLogin:
    async def test_login_success_caches_token(self):
        client = AOS8Client(_make_secrets())

        def handler(request):
            return httpx.Response(200, json=_LOGIN_OK)

        calls = _install_mock_transport(client, handler)
        tok = await client._ensure_token()
        assert tok == "tok-supersecret-12345"
        await client._ensure_token()
        login_calls = [c for c in calls if c.url.path == "/v1/api/login"]
        assert len(login_calls) == 1
        await client._http.aclose()

    async def test_login_serialized_under_lock(self):
        client = AOS8Client(_make_secrets())
        login_count = 0

        def handler(request):
            nonlocal login_count
            if request.url.path == "/v1/api/login":
                login_count += 1
            return httpx.Response(200, json=_LOGIN_OK)

        _install_mock_transport(client, handler)
        await asyncio.gather(client._ensure_token(), client._ensure_token(), client._ensure_token())
        assert login_count == 1
        await client._http.aclose()

    async def test_login_rejected_global_result_nonzero(self):
        client = AOS8Client(_make_secrets())

        def handler(request):
            return httpx.Response(
                200,
                json={
                    "_global_result": {"status": "1", "status_str": "auth failed"},
                },
            )

        _install_mock_transport(client, handler)
        with pytest.raises(AOS8AuthError, match="auth failed"):
            await client._ensure_token()
        await client._http.aclose()


class TestAOS8ClientLazy:
    async def test_init_does_not_login(self):
        client = AOS8Client(_make_secrets())
        calls: list[httpx.Request] = []

        def handler(request):
            calls.append(request)
            return httpx.Response(200, json=_LOGIN_OK)

        _install_mock_transport(client, handler)
        assert calls == []
        await client._http.aclose()


class TestAOS8ClientRequest:
    async def test_401_triggers_refresh_and_retry_once(self):
        client = AOS8Client(_make_secrets())
        login_count = 0
        request_count = 0

        def handler(request):
            nonlocal login_count, request_count
            if request.url.path == "/v1/api/login":
                login_count += 1
                return httpx.Response(200, json=_LOGIN_OK)
            request_count += 1
            if request_count == 1:
                return httpx.Response(401, json={})
            return httpx.Response(200, json={"_global_result": {"status": "0"}, "ok": True})

        _install_mock_transport(client, handler)
        response = await client.request("GET", "/v1/configuration/object/foo")
        assert response.status_code == 200
        assert login_count == 2  # initial + 1 refresh
        await client._http.aclose()

    async def test_double_401_raises(self):
        client = AOS8Client(_make_secrets())
        login_count = 0

        def handler(request):
            nonlocal login_count
            if request.url.path == "/v1/api/login":
                login_count += 1
                return httpx.Response(200, json=_LOGIN_OK)
            return httpx.Response(401, json={})

        _install_mock_transport(client, handler)
        with pytest.raises(httpx.HTTPStatusError):
            await client.request("GET", "/v1/configuration/object/foo")
        assert login_count == 2
        await client._http.aclose()

    async def test_global_result_error_raises(self):
        client = AOS8Client(_make_secrets())

        def handler(request):
            if request.url.path == "/v1/api/login":
                return httpx.Response(200, json=_LOGIN_OK)
            return httpx.Response(200, json={"_global_result": {"status": "1", "status_str": "boom"}})

        _install_mock_transport(client, handler)
        with pytest.raises(AOS8APIError, match="boom"):
            await client.request("GET", "/v1/configuration/object/foo")
        await client._http.aclose()

    async def test_global_result_status_int_normalization(self):
        client = AOS8Client(_make_secrets())

        def handler(request):
            if request.url.path == "/v1/api/login":
                return httpx.Response(200, json=_LOGIN_OK)
            return httpx.Response(200, json={"_global_result": {"status": 1, "status_str": "intboom"}})

        _install_mock_transport(client, handler)
        with pytest.raises(AOS8APIError, match="intboom"):
            await client.request("GET", "/v1/configuration/object/foo")
        await client._http.aclose()


class TestAOS8ClientLogging:
    async def test_uidaruba_never_in_logs(self, loguru_capture):
        client = AOS8Client(_make_secrets())
        req_count = 0

        def handler(request):
            nonlocal req_count
            if request.url.path == "/v1/api/login":
                return httpx.Response(200, json=_LOGIN_OK)
            if request.url.path == "/v1/api/logout":
                return httpx.Response(200, json={"_global_result": {"status": "0"}})
            req_count += 1
            if req_count == 1:
                return httpx.Response(401, json={})
            return httpx.Response(200, json={"_global_result": {"status": "0"}, "ok": True})

        _install_mock_transport(client, handler)
        await client.request("GET", "/v1/configuration/object/foo")
        await client.aclose()
        joined = "\n".join(loguru_capture)
        assert "tok-supersecret-12345" not in joined, f"UIDARUBA token leaked into log output: {joined!r}"


class TestAOS8ClientMisc:
    def test_verify_ssl_false_emits_warning(self, loguru_capture):
        AOS8Client(_make_secrets(verify_ssl=False))
        warnings = [m for m in loguru_capture if "WARNING" in m and "SSL" in m]
        assert warnings, f"Expected SSL warning, captured: {loguru_capture}"

    def test_custom_port_in_base_url(self):
        client = AOS8Client(_make_secrets(port=8443))
        assert str(client._http.base_url).rstrip("/") == "https://conductor.test:8443"


class TestAOS8ClientHealth:
    async def test_health_check_returns_hostname_and_version(self):
        fixture_body = json.loads((_FIXTURES / "aos8_show_version.json").read_text())
        client = AOS8Client(_make_secrets())

        def handler(request):
            if request.url.path == "/v1/api/login":
                return httpx.Response(200, json=_LOGIN_OK)
            if request.url.path == "/v1/configuration/showcommand":
                return httpx.Response(200, json=fixture_body, headers={"content-type": "application/json"})
            return httpx.Response(404, json={})

        _install_mock_transport(client, handler)
        info = await client.health_check()
        assert info["hostname"] == "conductor-lab-01"
        assert "ArubaOS" in info["version"]
        assert "raw" in info
        await client._http.aclose()


class TestAOS8ClientShutdown:
    async def test_aclose_calls_logout_endpoint(self):
        client = AOS8Client(_make_secrets())
        paths: list[str] = []

        def handler(request):
            paths.append(request.url.path)
            if request.url.path == "/v1/api/login":
                return httpx.Response(200, json=_LOGIN_OK)
            if request.url.path == "/v1/api/logout":
                return httpx.Response(200, json={"_global_result": {"status": "0"}})
            return httpx.Response(200, json={"_global_result": {"status": "0"}, "ok": True})

        _install_mock_transport(client, handler)
        await client._ensure_token()
        await client.aclose()
        assert "/v1/api/logout" in paths

    async def test_aclose_swallows_logout_error(self, loguru_capture):
        client = AOS8Client(_make_secrets())

        def handler(request):
            if request.url.path == "/v1/api/login":
                return httpx.Response(200, json=_LOGIN_OK)
            if request.url.path == "/v1/api/logout":
                raise httpx.ConnectError("conductor unreachable")
            return httpx.Response(200, json={"_global_result": {"status": "0"}})

        _install_mock_transport(client, handler)
        await client._ensure_token()
        await client.aclose()  # MUST NOT raise
        assert any("WARNING" in m and "logout" in m.lower() for m in loguru_capture)
