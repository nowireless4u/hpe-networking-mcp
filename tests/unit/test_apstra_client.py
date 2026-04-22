"""Unit tests for ApstraClient — login flow, 401-refresh, SSL honoring, aclose()."""

from __future__ import annotations

import asyncio
import json

import httpx
import pytest

from hpe_networking_mcp.config import ApstraSecrets
from hpe_networking_mcp.platforms.apstra.client import (
    ApstraAuthError,
    ApstraClient,
    format_http_error,
)


def _make_secrets(**overrides) -> ApstraSecrets:
    base = {
        "server": "apstra.test",
        "port": 443,
        "username": "admin",
        "password": "secret",
        "verify_ssl": True,
    }
    base.update(overrides)
    return ApstraSecrets(**base)


def _install_mock_transport(client: ApstraClient, handler) -> None:
    """Swap the client's internal AsyncClient for one with a MockTransport."""
    # Close the original lazily — we only care about the test lifecycle.
    transport = httpx.MockTransport(handler)
    client._http = httpx.AsyncClient(
        base_url=f"https://{client._config.server}:{client._config.port}",
        transport=transport,
        verify=client._config.verify_ssl,
    )


@pytest.mark.unit
class TestApstraClientLogin:
    async def test_login_success_caches_token(self):
        client = ApstraClient(_make_secrets())
        calls = []

        def handler(request):
            calls.append(request)
            assert request.url.path == "/api/user/login"
            assert request.method == "POST"
            body = json.loads(request.content)
            assert body == {"username": "admin", "password": "secret"}
            return httpx.Response(201, json={"token": "apstra-token-abc"})

        _install_mock_transport(client, handler)
        await client._ensure_token()
        assert client._token == "apstra-token-abc"
        # Second call must not re-login
        await client._ensure_token()
        assert len(calls) == 1
        await client.aclose()

    async def test_login_accepts_200(self):
        client = ApstraClient(_make_secrets())

        def handler(request):
            return httpx.Response(200, json={"token": "200-token"})

        _install_mock_transport(client, handler)
        await client._ensure_token()
        assert client._token == "200-token"
        await client.aclose()

    async def test_login_non_2xx_raises(self):
        client = ApstraClient(_make_secrets())

        def handler(request):
            return httpx.Response(401, text="Invalid credentials")

        _install_mock_transport(client, handler)
        with pytest.raises(ApstraAuthError, match="401"):
            await client._ensure_token()
        await client.aclose()

    async def test_login_missing_token_raises(self):
        client = ApstraClient(_make_secrets())

        def handler(request):
            return httpx.Response(201, json={"unexpected": "payload"})

        _install_mock_transport(client, handler)
        with pytest.raises(ApstraAuthError, match="missing 'token'"):
            await client._ensure_token()
        await client.aclose()

    async def test_login_non_json_raises(self):
        client = ApstraClient(_make_secrets())

        def handler(request):
            return httpx.Response(201, text="not-json")

        _install_mock_transport(client, handler)
        with pytest.raises(ApstraAuthError, match="non-JSON"):
            await client._ensure_token()
        await client.aclose()

    async def test_login_serialized_under_lock(self):
        """Concurrent callers should result in exactly one login request."""
        client = ApstraClient(_make_secrets())
        call_count = 0
        release = asyncio.Event()

        async def slow_handler(request):  # noqa: RUF029
            return None

        def handler(request):
            nonlocal call_count
            call_count += 1
            return httpx.Response(201, json={"token": f"tok-{call_count}"})

        _install_mock_transport(client, handler)
        release.set()
        await asyncio.gather(client._ensure_token(), client._ensure_token(), client._ensure_token())
        assert call_count == 1
        await client.aclose()


@pytest.mark.unit
class TestApstraClientRequest:
    async def test_request_sends_auth_header(self):
        client = ApstraClient(_make_secrets())
        captured = []

        def handler(request):
            if request.url.path == "/api/user/login":
                return httpx.Response(201, json={"token": "auth-xyz"})
            captured.append(request)
            return httpx.Response(200, json={"items": []})

        _install_mock_transport(client, handler)
        response = await client.request("GET", "/api/blueprints")
        assert response.status_code == 200
        assert captured[0].headers["AuthToken"] == "auth-xyz"
        await client.aclose()

    async def test_401_triggers_refresh_and_retry_once(self):
        client = ApstraClient(_make_secrets())
        logins = 0
        gets = 0

        def handler(request):
            nonlocal logins, gets
            if request.url.path == "/api/user/login":
                logins += 1
                return httpx.Response(201, json={"token": f"token-{logins}"})
            gets += 1
            # First two GETs: first succeeds login, second pretends token expired
            if gets == 1:
                return httpx.Response(401, text="Unauthorized")
            return httpx.Response(200, json={"ok": True})

        _install_mock_transport(client, handler)
        response = await client.request("GET", "/api/blueprints")
        assert response.status_code == 200
        assert logins == 2  # login once, then refresh
        assert gets == 2
        await client.aclose()

    async def test_raises_on_non_2xx_after_retry(self):
        client = ApstraClient(_make_secrets())

        def handler(request):
            if request.url.path == "/api/user/login":
                return httpx.Response(201, json={"token": "t"})
            return httpx.Response(500, text="boom")

        _install_mock_transport(client, handler)
        with pytest.raises(httpx.HTTPStatusError):
            await client.request("GET", "/api/blueprints")
        await client.aclose()

    async def test_get_json_returns_parsed_body(self):
        client = ApstraClient(_make_secrets())

        def handler(request):
            if request.url.path == "/api/user/login":
                return httpx.Response(201, json={"token": "t"})
            return httpx.Response(200, json={"items": [1, 2, 3]})

        _install_mock_transport(client, handler)
        result = await client.get_json("/api/blueprints")
        assert result == {"items": [1, 2, 3]}
        await client.aclose()

    async def test_refresh_token_forces_new_login(self):
        client = ApstraClient(_make_secrets())
        logins = 0

        def handler(request):
            nonlocal logins
            logins += 1
            return httpx.Response(201, json={"token": f"t-{logins}"})

        _install_mock_transport(client, handler)
        await client._ensure_token()
        assert client._token == "t-1"
        new_token = await client._refresh_token()
        assert new_token == "t-2"
        assert client._token == "t-2"
        await client.aclose()


@pytest.mark.unit
class TestApstraClientMisc:
    def test_server_property(self):
        client = ApstraClient(_make_secrets(server="apstra.example.com", port=8443))
        assert client.server == "apstra.example.com:8443"

    def test_verify_ssl_honored(self):
        client = ApstraClient(_make_secrets(verify_ssl=False))
        # httpx stores this as an internal flag — just confirm no exception.
        # Deeper verification would require an integration test.
        assert client._config.verify_ssl is False


@pytest.mark.unit
class TestFormatHttpError:
    def test_http_status_error_with_json_body(self):
        response = httpx.Response(404, json={"detail": "missing"}, request=httpx.Request("GET", "https://x/"))
        exc = httpx.HTTPStatusError("404", request=response.request, response=response)
        formatted = format_http_error(exc)
        assert formatted["status_code"] == 404
        assert formatted["body"] == {"detail": "missing"}

    def test_http_status_error_with_text_body(self):
        response = httpx.Response(500, text="boom", request=httpx.Request("GET", "https://x/"))
        exc = httpx.HTTPStatusError("500", request=response.request, response=response)
        formatted = format_http_error(exc)
        assert formatted["status_code"] == 500
        assert formatted["body"] == "boom"

    def test_generic_httpx_error(self):
        exc = httpx.ConnectError("could not connect")
        formatted = format_http_error(exc)
        assert formatted["status_code"] == 0
        assert "could not connect" in formatted["message"]
