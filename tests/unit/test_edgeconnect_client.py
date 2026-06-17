"""Unit tests for EdgeConnectClient — API-key vs session auth, CSRF, source param, 401 retry.

Mocks the transport on the persistent ``client._http`` (preserving the logging
event hooks — see issue #233) rather than replacing the AsyncClient.
"""

from __future__ import annotations

import inspect

import httpx
import pytest
from fastmcp.exceptions import ToolError

from hpe_networking_mcp.config import EdgeConnectSecrets
from hpe_networking_mcp.platforms.edgeconnect.client import EdgeConnectClient


def _api_key_secrets(**overrides) -> EdgeConnectSecrets:
    base = {"host": "orch.example.com", "api_key": "test-api-key", "verify_ssl": False}
    base.update(overrides)
    return EdgeConnectSecrets(**base)


def _user_pass_secrets(**overrides) -> EdgeConnectSecrets:
    base = {
        "host": "orch.example.com",
        "user": "api-admin",
        "password": "secret",
        "verify_ssl": False,
    }
    base.update(overrides)
    return EdgeConnectSecrets(**base)


def _install_mock_transport(client: EdgeConnectClient, handler) -> list[httpx.Request]:
    """Swap only the transport on the persistent client (keeps event hooks, #233)."""
    calls: list[httpx.Request] = []

    def _wrapper(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        return handler(request)

    client._http._transport = httpx.MockTransport(_wrapper)
    return calls


@pytest.mark.unit
class TestNoSdkImport:
    def test_pyedgeconnect_not_imported(self):
        from hpe_networking_mcp.platforms.edgeconnect import client as client_module

        src = inspect.getsource(client_module)
        # The SDK name appears in prose comments, but never as an import.
        assert "import pyedgeconnect" not in src
        assert "from pyedgeconnect" not in src


@pytest.mark.unit
class TestBaseUrl:
    def test_base_url_includes_gms_rest(self):
        client = EdgeConnectClient(_api_key_secrets())
        assert str(client._http.base_url).rstrip("/") == "https://orch.example.com/gms/rest"


@pytest.mark.unit
class TestApiKeyAuth:
    async def test_api_key_sets_header_and_skips_login(self):
        client = EdgeConnectClient(_api_key_secrets())

        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(200, json={"ok": True})

        calls = _install_mock_transport(client, handler)
        await client.request("GET", "/appliance")

        assert all(c.url.path != "/gms/rest/authentication/login" for c in calls)
        req = calls[-1]
        assert req.headers["X-Auth-Token"] == "test-api-key"
        # source param is always injected
        assert "source=menu_rest_apis_id" in str(req.url)


@pytest.mark.unit
class TestSessionAuth:
    async def test_login_captures_csrf_and_sets_header(self):
        client = EdgeConnectClient(_user_pass_secrets())

        def handler(request: httpx.Request) -> httpx.Response:
            if request.url.path.endswith("/authentication/login"):
                return httpx.Response(
                    200,
                    json={"ok": True},
                    headers={"set-cookie": "orchCsrfToken=csrf123; Path=/"},
                )
            return httpx.Response(200, json={"ok": True})

        calls = _install_mock_transport(client, handler)
        await client.request("GET", "/appliance")

        login_calls = [c for c in calls if c.url.path.endswith("/authentication/login")]
        assert len(login_calls) == 1
        # the data request carries the captured CSRF token as a header
        data_req = [c for c in calls if c.url.path.endswith("/appliance")][-1]
        assert data_req.headers.get("X-XSRF-TOKEN") == "csrf123"

    async def test_401_triggers_relogin_once(self):
        client = EdgeConnectClient(_user_pass_secrets())
        login_count = 0
        data_attempts = 0

        def handler(request: httpx.Request) -> httpx.Response:
            nonlocal login_count, data_attempts
            if request.url.path.endswith("/authentication/login"):
                login_count += 1
                return httpx.Response(200, json={"ok": True})
            data_attempts += 1
            # first data call 401s, second succeeds
            if data_attempts == 1:
                return httpx.Response(401, json={"error": "expired"})
            return httpx.Response(200, json={"ok": True})

        _install_mock_transport(client, handler)
        await client.request("GET", "/appliance")

        assert login_count == 2  # initial + one re-login on 401
        assert data_attempts == 2


@pytest.mark.unit
class TestBodyEncoding:
    """Non-JSON bodies must be sent with the right Content-Type, not JSON-encoded."""

    def _client(self):
        return EdgeConnectClient(_api_key_secrets())

    async def test_json_body_default(self):
        client = self._client()
        calls = _install_mock_transport(client, lambda r: httpx.Response(200, json={}))
        await client.request("POST", "/x", json_body={"a": 1})
        req = calls[-1]
        assert "application/json" in req.headers["content-type"]
        assert req.content == b'{"a": 1}' or b'"a"' in req.content

    async def test_text_body_sends_text_plain_unquoted(self):
        client = self._client()
        calls = _install_mock_transport(client, lambda r: httpx.Response(200, json={}))
        await client.request("POST", "/appliance/discovered/deny", json_body="a comment", body_mode="text")
        req = calls[-1]
        assert req.headers["content-type"] == "text/plain"
        assert req.content == b"a comment"  # raw, not JSON-quoted ("a comment")

    async def test_form_body_urlencoded(self):
        client = self._client()
        calls = _install_mock_transport(client, lambda r: httpx.Response(200, json={}))
        await client.request("POST", "/authentication/saml2/consume", json_body={"SAMLResponse": "x"}, body_mode="form")
        req = calls[-1]
        assert "application/x-www-form-urlencoded" in req.headers["content-type"]
        assert b"SAMLResponse=x" in req.content

    async def test_multipart_unsupported_raises(self):
        client = self._client()
        _install_mock_transport(client, lambda r: httpx.Response(200, json={}))
        with pytest.raises(ToolError):
            await client.request("POST", "/brandCustomization/image", json_body={"f": 1}, body_mode="multipart")
