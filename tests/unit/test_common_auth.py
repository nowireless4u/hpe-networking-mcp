"""Unit tests for the shared auth primitive (``platforms/_common/auth.py``).

The primitive is extracted from the two proven in-tree implementations:

* UXI's OAuth2 client-credentials flow (time-based expiry cache + buffer).
* Apstra's login-session flow (no expiry; token lives until a 401 forces
  re-login).

Both flows share one lifecycle: double-checked locking around a cached token,
``invalidate()`` on auth failure, and ``refresh()`` to force re-acquisition.
"""

from __future__ import annotations

import asyncio
import time

import httpx
import pytest

from hpe_networking_mcp.platforms._common.auth import (
    AsyncTokenManager,
    AuthError,
    TokenResult,
    oauth2_client_credentials,
)


def _counting_fetch(results: list[TokenResult]):
    """Build a fetch coroutine that pops results in order and counts calls."""
    calls: list[int] = []

    async def fetch() -> TokenResult:
        calls.append(1)
        return results.pop(0) if len(results) > 1 else results[0]

    return fetch, calls


@pytest.mark.unit
class TestAsyncTokenManagerLifecycle:
    async def test_first_get_token_fetches(self):
        fetch, calls = _counting_fetch([TokenResult("tok-1", expires_in=3600)])
        mgr = AsyncTokenManager(fetch, name="test")
        assert mgr.token is None
        token = await mgr.get_token()
        assert token == "tok-1"
        assert len(calls) == 1

    async def test_cached_token_not_refetched(self):
        fetch, calls = _counting_fetch([TokenResult("tok-1", expires_in=3600)])
        mgr = AsyncTokenManager(fetch, name="test")
        await mgr.get_token()
        await mgr.get_token()
        await mgr.get_token()
        assert len(calls) == 1

    async def test_no_expiry_token_lives_until_invalidated(self):
        """Login-session flavor: expires_in=None means valid until invalidated."""
        fetch, calls = _counting_fetch([TokenResult("session-tok", expires_in=None)])
        mgr = AsyncTokenManager(fetch, name="test")
        await mgr.get_token()
        assert mgr.expires_at is None
        await mgr.get_token()
        assert len(calls) == 1

    async def test_token_within_buffer_is_refetched(self):
        """UXI flavor: a token expiring inside the buffer window is stale."""
        fetch, calls = _counting_fetch([TokenResult("tok-n", expires_in=3600)])
        mgr = AsyncTokenManager(fetch, name="test", expiry_buffer=60.0)
        mgr.prime("about-to-expire", expires_in=30.0)  # 30 s < 60 s buffer
        token = await mgr.get_token()
        assert token == "tok-n"
        assert len(calls) == 1

    async def test_token_beyond_buffer_is_cached(self):
        fetch, calls = _counting_fetch([TokenResult("tok-n", expires_in=3600)])
        mgr = AsyncTokenManager(fetch, name="test", expiry_buffer=60.0)
        mgr.prime("still-good", expires_in=600.0)
        token = await mgr.get_token()
        assert token == "still-good"
        assert not calls

    async def test_invalidate_forces_refetch(self):
        fetch, calls = _counting_fetch([TokenResult("tok-1", expires_in=3600)])
        mgr = AsyncTokenManager(fetch, name="test")
        await mgr.get_token()
        mgr.invalidate()
        assert mgr.token is None
        await mgr.get_token()
        assert len(calls) == 2

    async def test_refresh_forces_refetch_and_returns_new_token(self):
        results = [TokenResult("tok-1", expires_in=3600), TokenResult("tok-2", expires_in=3600)]
        calls: list[int] = []

        async def fetch() -> TokenResult:
            calls.append(1)
            return results[len(calls) - 1]

        mgr = AsyncTokenManager(fetch, name="test")
        assert await mgr.get_token() == "tok-1"
        assert await mgr.refresh() == "tok-2"
        assert mgr.token == "tok-2"
        assert len(calls) == 2

    async def test_concurrent_get_token_fetches_once(self):
        """Double-checked locking: N concurrent callers, exactly one fetch."""
        calls: list[int] = []

        async def slow_fetch() -> TokenResult:
            calls.append(1)
            await asyncio.sleep(0.01)
            return TokenResult("tok-1", expires_in=3600)

        mgr = AsyncTokenManager(slow_fetch, name="test")
        tokens = await asyncio.gather(*(mgr.get_token() for _ in range(5)))
        assert tokens == ["tok-1"] * 5
        assert len(calls) == 1

    async def test_fetch_returning_empty_token_raises(self):
        async def fetch() -> TokenResult:
            return TokenResult("", expires_in=3600)

        mgr = AsyncTokenManager(fetch, name="test")
        with pytest.raises(AuthError, match="empty token"):
            await mgr.get_token()

    def test_prime_sets_token_and_expiry(self):
        async def fetch() -> TokenResult:  # pragma: no cover - never called
            raise AssertionError("fetch must not run")

        mgr = AsyncTokenManager(fetch, name="test")
        mgr.prime("primed", expires_in=100.0)
        assert mgr.token == "primed"
        assert mgr.expires_at is not None
        assert mgr.expires_at == pytest.approx(time.time() + 100.0, abs=5.0)

    def test_static_constructor_yields_fixed_token(self):
        mgr = AsyncTokenManager.static("fixed-tok", name="test")
        assert mgr.token == "fixed-tok"
        assert mgr.expires_at is None


@pytest.mark.unit
class TestOAuth2ClientCredentials:
    """The OAuth2 fetcher extracted from UXI's `_fetch_token_locked`."""

    def _fetcher(self, handler, **kwargs):
        transport = httpx.MockTransport(handler)
        return oauth2_client_credentials(
            "https://sso.example.com/as/token.oauth2",
            "my-client-id",
            "my-client-secret",
            name="test",
            _client_factory=lambda: httpx.AsyncClient(transport=transport),
            **kwargs,
        )

    async def test_posts_client_credentials_form(self):
        captured: list[httpx.Request] = []

        def handler(request: httpx.Request) -> httpx.Response:
            captured.append(request)
            return httpx.Response(200, json={"access_token": "oauth-tok", "expires_in": 7199})

        fetch = self._fetcher(handler)
        result = await fetch()
        assert result.token == "oauth-tok"
        assert result.expires_in == 7199
        request = captured[0]
        assert request.method == "POST"
        assert request.url == "https://sso.example.com/as/token.oauth2"
        body = request.content.decode()
        assert "grant_type=client_credentials" in body
        assert "client_id=my-client-id" in body
        assert "client_secret=my-client-secret" in body

    async def test_missing_expires_in_uses_default(self):
        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(200, json={"access_token": "tok"})

        fetch = self._fetcher(handler, default_expires_in=1234.0)
        result = await fetch()
        assert result.expires_in == 1234.0

    async def test_non_2xx_raises_http_status_error(self):
        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(401, json={"error": "invalid_client"})

        fetch = self._fetcher(handler)
        with pytest.raises(httpx.HTTPStatusError):
            await fetch()

    async def test_missing_access_token_raises_auth_error(self):
        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(200, json={"token_type": "Bearer"})

        fetch = self._fetcher(handler)
        with pytest.raises(AuthError, match="access_token"):
            await fetch()


@pytest.mark.unit
class TestManagerWithOAuth2EndToEnd:
    async def test_manager_drives_oauth2_fetcher(self):
        tokens = iter(["tok-a", "tok-b"])

        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(200, json={"access_token": next(tokens), "expires_in": 3600})

        transport = httpx.MockTransport(handler)
        fetch = oauth2_client_credentials(
            "https://sso.example.com/as/token.oauth2",
            "cid",
            "csecret",
            name="e2e",
            _client_factory=lambda: httpx.AsyncClient(transport=transport),
        )
        mgr = AsyncTokenManager(fetch, name="e2e", expiry_buffer=60.0)
        assert await mgr.get_token() == "tok-a"
        assert await mgr.get_token() == "tok-a"  # cached
        mgr.invalidate()
        assert await mgr.get_token() == "tok-b"
