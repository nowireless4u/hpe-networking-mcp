"""Unit tests for ClearPassClient — the pyclearpass-compatible async replacement.

Pins the response contract the ~142 ClearPass tools rely on: decoded JSON
with raw-text fallback, raw bytes for non-JSON accepts, error bodies
RETURNED (never raised), and the 401/403 → refresh-once → replay flow that
previously lived in the ``_send_request`` monkey-patch.
"""

from __future__ import annotations

import json

import httpx
import pytest

from hpe_networking_mcp.config import ClearPassSecrets
from hpe_networking_mcp.platforms._common.auth import TokenResult
from hpe_networking_mcp.platforms.clearpass.client import (
    ClearPassAuthError,
    ClearPassClient,
    create_client,
)


def _make_secrets(**overrides) -> ClearPassSecrets:
    base = {
        "server": "https://clearpass.example.test:443/api",
        "client_id": "cp-client-id",
        "client_secret": "cp-client-secret",
        "verify_ssl": True,
    }
    base.update(overrides)
    return ClearPassSecrets(**base)


def _make_client(handler, token: str = "cp-token") -> ClearPassClient:
    client = ClearPassClient(_make_secrets())
    client._http = httpx.AsyncClient(
        base_url="https://clearpass.example.test:443/api",
        transport=httpx.MockTransport(handler),
    )
    client._tokens.prime(token, expires_in=28800)
    return client


@pytest.mark.unit
class TestNoPyclearpassAnywhere:
    """The pyclearpass SDK was removed — no module under src/ may import it."""

    def test_no_pyclearpass_imports_in_src(self):
        import ast
        import pathlib

        import hpe_networking_mcp

        root = pathlib.Path(hpe_networking_mcp.__file__).parent
        offenders: list[str] = []
        for path in root.rglob("*.py"):
            tree = ast.parse(path.read_text())
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    if any(a.name.split(".")[0] == "pyclearpass" for a in node.names):
                        offenders.append(f"{path}:{node.lineno}")
                elif isinstance(node, ast.ImportFrom) and node.module and node.module.split(".")[0] == "pyclearpass":
                    offenders.append(f"{path}:{node.lineno}")
        assert not offenders, f"pyclearpass imports found (SDK was removed): {offenders}"


@pytest.mark.unit
class TestRequestContract:
    async def test_json_response_decoded(self):
        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(200, json={"items": [{"id": 1}]})

        client = _make_client(handler)
        body = await client.request("get", "/guest")
        assert body == {"items": [{"id": 1}]}
        await client.aclose()

    async def test_non_json_text_falls_back_to_raw_text(self):
        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(200, text="plain text payload")

        client = _make_client(handler)
        body = await client.request("get", "/guest")
        assert body == "plain text payload"
        await client.aclose()

    async def test_non_json_accept_returns_bytes(self):
        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(200, content=b"\x00\x01CERTDATA")

        client = _make_client(handler)
        body = await client.request("get", "/cert-file", accept="application/octet-stream")
        assert body == b"\x00\x01CERTDATA"
        await client.aclose()

    async def test_error_bodies_returned_not_raised(self):
        """pyclearpass parity: a 404 body comes back as a dict, no exception."""

        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(404, json={"status": 404, "title": "Not Found", "detail": "no such guest"})

        client = _make_client(handler)
        body = await client.request("get", "/guest/999")
        assert body["status"] == 404
        assert body["title"] == "Not Found"
        await client.aclose()

    async def test_bearer_and_accept_headers_sent(self):
        captured: list[httpx.Request] = []

        def handler(request: httpx.Request) -> httpx.Response:
            captured.append(request)
            return httpx.Response(200, json={})

        client = _make_client(handler, token="tok-abc")
        await client.request("get", "/guest")
        assert captured[0].headers["Authorization"] == "Bearer tok-abc"
        assert captured[0].headers["accept"] == "application/json"
        await client.aclose()

    async def test_empty_string_params_and_body_keys_dropped(self):
        """pyclearpass parity: '' query params and '' top-level body keys never reach the API."""
        captured: list[httpx.Request] = []

        def handler(request: httpx.Request) -> httpx.Response:
            captured.append(request)
            return httpx.Response(200, json={})

        client = _make_client(handler)
        await client.request(
            "post",
            "/guest",
            params={"change_of_authorization": "", "limit": 10},
            json_body={"username": "visitor@example.com", "notes": "", "role_id": 2},
        )
        request = captured[0]
        assert "change_of_authorization" not in request.url.params
        assert request.url.params.get("limit") == "10"
        assert json.loads(request.content) == {"username": "visitor@example.com", "role_id": 2}
        await client.aclose()

    async def test_dict_param_json_encoded(self):
        """pyclearpass parity: dict-valued query params (filter) travel as compact JSON."""
        captured: list[httpx.Request] = []

        def handler(request: httpx.Request) -> httpx.Response:
            captured.append(request)
            return httpx.Response(200, json={})

        client = _make_client(handler)
        await client.request("get", "/guest", params={"filter": {"username": "visitor@example.com"}})
        assert captured[0].url.params.get("filter") == '{"username":"visitor@example.com"}'
        await client.aclose()

    async def test_params_stripped_and_body_passed(self):
        captured: list[httpx.Request] = []

        def handler(request: httpx.Request) -> httpx.Response:
            captured.append(request)
            return httpx.Response(200, json={})

        client = _make_client(handler)
        await client.request(
            "post",
            "/guest",
            params={"limit": 25, "filter": None},
            json_body={"username": "visitor@example.com"},
        )
        request = captured[0]
        assert request.url.params.get("limit") == "25"
        assert "filter" not in request.url.params
        assert json.loads(request.content) == {"username": "visitor@example.com"}
        await client.aclose()


@pytest.mark.unit
class TestBasePathJoining:
    """The configured server URL carries a path component (e.g. ``/api``).

    httpx keeps the base path as a prefix when joining request paths —
    load-bearing for every call now that raw paths go straight to httpx.
    Pins both the API-call path and the ``/oauth`` token path.
    """

    async def test_api_paths_land_under_the_base_path(self):
        captured: list[httpx.Request] = []

        def handler(request: httpx.Request) -> httpx.Response:
            captured.append(request)
            return httpx.Response(200, json={})

        client = _make_client(handler)
        await client.request("get", "/guest/42")
        assert captured[0].url.path == "/api/guest/42"
        await client.aclose()

    async def test_oauth_token_path_lands_under_the_base_path(self):
        captured: list[httpx.Request] = []

        def handler(request: httpx.Request) -> httpx.Response:
            captured.append(request)
            return httpx.Response(200, json={"access_token": "t", "expires_in": 28800})

        client = ClearPassClient(_make_secrets())
        client._http = httpx.AsyncClient(
            base_url="https://clearpass.example.test:443/api",
            transport=httpx.MockTransport(handler),
        )
        await client._fetch_token()
        assert captured[0].url.path == "/api/oauth"
        await client.aclose()


@pytest.mark.unit
class TestAuthRetry:
    async def test_403_body_refreshes_and_replays_once(self):
        calls: list[str] = []

        def handler(request: httpx.Request) -> httpx.Response:
            calls.append(request.headers["Authorization"])
            if len(calls) == 1:
                return httpx.Response(403, json={"status": 403, "title": "Forbidden", "detail": "Forbidden"})
            return httpx.Response(200, json={"ok": True})

        client = _make_client(handler, token="stale")

        async def fresh() -> TokenResult:
            return TokenResult("fresh", expires_in=28800)

        client._tokens._fetch = fresh
        body = await client.request("get", "/guest")
        assert body == {"ok": True}
        assert calls == ["Bearer stale", "Bearer fresh"]
        await client.aclose()

    async def test_second_403_returned_not_looped(self):
        count = 0

        def handler(request: httpx.Request) -> httpx.Response:
            nonlocal count
            count += 1
            return httpx.Response(403, json={"status": 403, "title": "Forbidden"})

        client = _make_client(handler)

        async def fetch() -> TokenResult:
            return TokenResult("again", expires_in=28800)

        client._tokens._fetch = fetch
        body = await client.request("get", "/guest")
        assert body["status"] == 403
        assert count == 2
        await client.aclose()

    async def test_refresh_failure_returns_original_error_body(self):
        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(403, json={"status": 403, "title": "Forbidden"})

        client = _make_client(handler)

        async def failing_fetch() -> TokenResult:
            raise ClearPassAuthError("ClearPass OAuth2 failed with HTTP 400: bad client")

        client._tokens._fetch = failing_fetch
        body = await client.request("get", "/guest")
        assert body["status"] == 403  # original error body surfaced, not an exception
        await client.aclose()


@pytest.mark.unit
class TestTokenFetch:
    async def test_oauth_post_sends_json_client_credentials(self):
        captured: list[httpx.Request] = []

        def handler(request: httpx.Request) -> httpx.Response:
            captured.append(request)
            return httpx.Response(200, json={"access_token": "fresh-tok", "expires_in": 28800})

        client = ClearPassClient(_make_secrets())
        client._http = httpx.AsyncClient(
            base_url="https://clearpass.example.test:443/api",
            transport=httpx.MockTransport(handler),
        )
        result = await client._fetch_token()
        assert result.token == "fresh-tok"
        assert result.expires_in == 28800
        request = captured[0]
        assert request.url.path.endswith("/oauth")
        assert json.loads(request.content) == {
            "grant_type": "client_credentials",
            "client_id": "cp-client-id",
            "client_secret": "cp-client-secret",
        }
        await client.aclose()

    async def test_non_200_raises_auth_error(self):
        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(400, text="invalid client")

        client = ClearPassClient(_make_secrets())
        client._http = httpx.AsyncClient(
            base_url="https://clearpass.example.test:443/api",
            transport=httpx.MockTransport(handler),
        )
        with pytest.raises(ClearPassAuthError, match="HTTP 400"):
            await client._fetch_token()
        await client.aclose()

    async def test_missing_access_token_raises_auth_error(self):
        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(200, json={"error_description": "scope rejected"})

        client = ClearPassClient(_make_secrets())
        client._http = httpx.AsyncClient(
            base_url="https://clearpass.example.test:443/api",
            transport=httpx.MockTransport(handler),
        )
        with pytest.raises(ClearPassAuthError, match="missing access_token"):
            await client._fetch_token()
        await client.aclose()

    def test_create_client_is_lazy(self):
        client = create_client(_make_secrets())
        assert client._tokens.token is None
