"""Shared async token lifecycle for all platform clients.

Extracted from the two proven in-tree implementations (UXI's OAuth2
client-credentials flow and Apstra's login-session flow) so every platform
shares one lifecycle instead of maintaining its own token manager:

* ``AsyncTokenManager`` owns the cached token, its expiry, and an
  ``asyncio.Lock`` with double-checked locking so concurrent callers
  trigger exactly one acquisition.
* The *fetch strategy* is a coroutine the platform supplies — what request
  acquires a token is per-platform; when to run it is shared:

  - OAuth2 client-credentials → ``oauth2_client_credentials(...)`` builds
    the fetcher (UXI, GreenLake, Central, ClearPass).
  - Login-session endpoints → the platform passes its own login coroutine
    returning a :class:`TokenResult` with ``expires_in=None`` (Apstra, AOS 8).
  - Static tokens → ``AsyncTokenManager.static(...)`` (Mist, Axis).

How the credential is *attached* to requests (bearer header, custom header,
cookie + query param) stays in the platform client; the manager only owns
acquisition, caching, and invalidation.

Sharing note: managers are per-client by default. When two platforms accept
tokens from the same issuer and credential set, construct one manager and
pass it to both clients — the lock and cache then serve both platforms.
"""

from __future__ import annotations

import asyncio
import time
from collections.abc import Awaitable, Callable
from dataclasses import dataclass

import httpx
from loguru import logger

from hpe_networking_mcp.utils.logging import mask_secret

_DEFAULT_EXPIRY_BUFFER_SECS = 60.0
_DEFAULT_AUTH_TIMEOUT = 10.0

TokenFetcher = Callable[[], Awaitable["TokenResult"]]


class AuthError(RuntimeError):
    """Raised when token acquisition fails in a way the platform can't retry.

    Platform-specific auth errors (e.g. ``ApstraAuthError``) subclass this so
    call sites can catch either the platform flavor or the shared base.
    """


@dataclass(frozen=True)
class TokenResult:
    """Outcome of one token acquisition.

    Args:
        token: The acquired credential value.
        expires_in: Seconds until expiry, or ``None`` for tokens with no
            known lifetime (login-session tokens live until a 401 forces
            re-login; static tokens never expire).
    """

    token: str
    expires_in: float | None = None


class AsyncTokenManager:
    """Cached-token lifecycle with double-checked locking.

    Usage in a platform client::

        self._tokens = AsyncTokenManager(fetch, name="uxi", expiry_buffer=60.0)
        ...
        token = await self._tokens.get_token()      # cached or fetched
        ...
        self._tokens.invalidate()                   # e.g. after a 401
        token = await self._tokens.refresh()        # force re-acquisition
    """

    def __init__(
        self,
        fetch: TokenFetcher,
        *,
        name: str,
        expiry_buffer: float = _DEFAULT_EXPIRY_BUFFER_SECS,
    ) -> None:
        """
        Args:
            fetch: Coroutine performing one token acquisition.
            name: Platform label used in log lines.
            expiry_buffer: Seconds before expiry at which a token counts as
                stale and is proactively re-fetched.
        """
        self._fetch = fetch
        self._name = name
        self._buffer = expiry_buffer
        self._token: str | None = None
        self._expires_at: float | None = None  # Unix timestamp; None = no expiry
        self._lock = asyncio.Lock()

    @classmethod
    def static(cls, token: str, *, name: str) -> AsyncTokenManager:
        """Build a manager for a fixed, never-refreshed token.

        Raises:
            AuthError: If ``token`` is empty — same guard as the fetch path,
                so a missing secret fails loudly at construction instead of
                producing requests with a blank credential.
        """
        if not token:
            raise AuthError(f"{name}: static token is empty")

        async def fetch() -> TokenResult:
            return TokenResult(token)

        manager = cls(fetch, name=name)
        manager.prime(token)
        return manager

    @property
    def token(self) -> str | None:
        """The cached token, or ``None`` if not yet acquired / invalidated."""
        return self._token

    @property
    def expires_at(self) -> float | None:
        """Unix timestamp the cached token expires at, or ``None`` for no expiry."""
        return self._expires_at

    def prime(self, token: str, expires_in: float | None = None) -> None:
        """Seed the cache directly (static tokens, tests).

        Raises:
            AuthError: If ``token`` is empty — an empty cached token would
                pass ``_is_fresh()`` and be sent as a blank credential.
        """
        if not token:
            raise AuthError(f"{self._name}: cannot prime with an empty token")
        self._token = token
        self._expires_at = time.time() + expires_in if expires_in is not None else None

    def invalidate(self) -> None:
        """Drop the cached token so the next ``get_token()`` re-fetches."""
        self._token = None
        self._expires_at = None

    def _is_fresh(self) -> bool:
        if self._token is None:
            return False
        if self._expires_at is None:
            return True
        return time.time() + self._buffer < self._expires_at

    async def get_token(self) -> str:
        """Return the cached token, acquiring one under the lock if stale."""
        if self._is_fresh():
            assert self._token is not None
            return self._token
        async with self._lock:
            # Re-check inside the lock — another coroutine may have fetched.
            if not self._is_fresh():
                await self._fetch_locked()
        if self._token is None:  # guard: assert is stripped under python -O
            raise AuthError(f"{self._name}: token fetch succeeded but no token is cached")
        return self._token

    async def refresh(self) -> str:
        """Force re-acquisition under the lock (e.g. after a 401) and return it."""
        async with self._lock:
            self.invalidate()
            await self._fetch_locked()
        if self._token is None:
            raise AuthError(f"{self._name}: token refresh succeeded but no token is cached")
        return self._token

    async def _fetch_locked(self) -> None:
        """Run the fetch strategy and cache its result. Caller holds the lock."""
        result = await self._fetch()
        if not result.token:
            raise AuthError(f"{self._name}: fetch strategy returned an empty token")
        self._token = result.token
        self._expires_at = time.time() + result.expires_in if result.expires_in is not None else None


def oauth2_client_credentials(
    token_url: str,
    client_id: str,
    client_secret: str,
    *,
    name: str,
    timeout: float = _DEFAULT_AUTH_TIMEOUT,
    default_expires_in: float = 3600.0,
    _client_factory: Callable[[], httpx.AsyncClient] | None = None,
) -> TokenFetcher:
    """Build a fetch strategy for the OAuth2 client-credentials grant.

    Extracted from the UXI client. Each fetch uses a fresh
    ``httpx.AsyncClient`` with NO base_url so the SSO hostname always
    resolves correctly regardless of the API client's base URL.

    Args:
        token_url: Absolute token-endpoint URL.
        client_id: OAuth2 client id.
        client_secret: OAuth2 client secret.
        name: Platform label used in log lines.
        timeout: Token request timeout in seconds.
        default_expires_in: Expiry to assume when the response omits
            ``expires_in``.
        _client_factory: Test hook — supplies the ``httpx.AsyncClient`` used
            for the token POST (e.g. one carrying a ``MockTransport``).

    Returns:
        A coroutine suitable as :class:`AsyncTokenManager`'s ``fetch``.

    Raises:
        httpx.HTTPStatusError: (from the fetcher) on a non-2xx token response.
        AuthError: (from the fetcher) when the response lacks ``access_token``.
    """
    factory = _client_factory or (lambda: httpx.AsyncClient(timeout=timeout))

    async def fetch() -> TokenResult:
        logger.info("{}: requesting new access token (client_id: {})", name, mask_secret(client_id))
        async with factory() as auth_http:
            response = await auth_http.post(
                token_url,
                data={
                    "grant_type": "client_credentials",
                    "client_id": client_id,
                    "client_secret": client_secret,
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
        response.raise_for_status()
        body = response.json()
        token = body.get("access_token")
        if not token:
            raise AuthError(f"{name}: token response is missing 'access_token'")
        expires_in = float(body.get("expires_in", default_expires_in))
        logger.info("{}: token acquired (expires_in={}s)", name, expires_in)
        return TokenResult(token=token, expires_in=expires_in)

    return fetch
