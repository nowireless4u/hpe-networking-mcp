"""ClearPass API session factory and helpers.

Unlike pycentral (single connection object), pyclearpass requires instantiating
each API class independently — every class inherits ClearPassAPILogin.

ClearPass OAuth2 tokens expire after 8 hours (28800s). pyclearpass only
re-auths when its cached ``api_token`` is empty, so once the token ages out
every subsequent call returns 403 Forbidden. We fix that by wrapping
``_send_request`` on each API instance with a pycentral-style retry: on an
auth failure, invalidate the cached token, fetch a fresh one, and replay the
original request exactly once.
"""

from __future__ import annotations

from typing import Any

import httpx
from fastmcp.exceptions import ToolError
from fastmcp.server.dependencies import get_context
from loguru import logger
from pyclearpass.common import ClearPassAPILogin

from hpe_networking_mcp.config import ClearPassSecrets
from hpe_networking_mcp.utils.logging import mask_secret

# ClearPass returns both 401 (invalid token) and 403 (insufficient perms /
# expired client-credentials token). We retry on either since a stale token
# surfaces as 403 in practice.
_AUTH_ERROR_STATUSES = frozenset({401, 403})


class ClearPassAuthError(RuntimeError):
    """Raised when OAuth2 client-credentials authentication fails."""


class ClearPassTokenManager:
    """Acquires and caches ClearPass OAuth2 access tokens.

    The token is held until :meth:`invalidate` is called, at which point the
    next :meth:`get_token` will fetch a fresh one from ``/oauth``.
    """

    def __init__(self, config: ClearPassSecrets) -> None:
        self._config = config
        self._token: str | None = None

    def get_token(self) -> str:
        """Return the cached token, fetching a new one if none is held."""
        if self._token is None:
            self._refresh()
        assert self._token is not None
        return self._token

    def invalidate(self) -> None:
        """Drop the cached token so the next ``get_token`` refreshes."""
        self._token = None

    def _refresh(self) -> None:
        """Acquire a fresh access token via the client-credentials grant."""
        url = f"{self._config.server}/oauth"
        payload = {
            "grant_type": "client_credentials",
            "client_id": self._config.client_id,
            "client_secret": self._config.client_secret,
        }
        logger.info("ClearPass: requesting new OAuth2 access token")
        try:
            response = httpx.post(
                url,
                json=payload,
                verify=self._config.verify_ssl,
                timeout=30.0,
            )
        except httpx.HTTPError as e:
            raise ClearPassAuthError(f"ClearPass OAuth2 request failed: {e}") from e

        if response.status_code != 200:
            raise ClearPassAuthError(f"ClearPass OAuth2 failed with HTTP {response.status_code}: {response.text[:200]}")

        try:
            data = response.json()
        except ValueError as e:
            raise ClearPassAuthError(f"ClearPass OAuth2 returned non-JSON body: {response.text[:200]}") from e

        token = data.get("access_token")
        if not token:
            detail = data.get("detail") or data.get("error_description") or data
            raise ClearPassAuthError(f"ClearPass OAuth2 response missing access_token: {detail}")

        self._token = token
        logger.info("ClearPass: obtained token {}", mask_secret(token))


def _is_auth_error(response: Any) -> bool:
    """Detect a 401/403 auth-failure payload from pyclearpass.

    pyclearpass returns decoded dicts for JSON responses and raw text/bytes
    otherwise. Error bodies look like::

        {"type": "...", "title": "Forbidden", "status": 403, "detail": "Forbidden"}
    """
    if not isinstance(response, dict):
        return False
    status = response.get("status")
    return isinstance(status, int) and status in _AUTH_ERROR_STATUSES


_TOKEN_MANAGER_ATTR = "_hpe_token_manager"  # nosec B105 — attribute name, not a credential
_PATCH_MARKER = "_hpe_auth_retry_patched"


def _install_class_auth_retry() -> None:
    """Patch :meth:`ClearPassAPILogin._send_request` once with refresh-on-auth-error.

    pyclearpass API methods invoke ``ClearPassAPILogin._send_request(self, ...)``
    directly against the class rather than the instance, so instance-level
    monkey-patches never fire. We wrap the class method once at import time;
    the wrapper looks up the token manager attached to each instance by
    :func:`create_api_client` and uses it to refresh on 401/403.
    """
    if getattr(ClearPassAPILogin, _PATCH_MARKER, False):
        return

    original = ClearPassAPILogin._send_request

    def send_with_retry(
        self: ClearPassAPILogin,
        url: str,
        method: str,
        query: str = "",
        content_response_type: str = "application/json",
    ) -> Any:
        response = original(self, url, method, query, content_response_type)
        if not _is_auth_error(response):
            return response

        token_manager: ClearPassTokenManager | None = getattr(self, _TOKEN_MANAGER_ATTR, None)
        if token_manager is None:
            return response

        logger.info(
            "ClearPass: auth error on {} {} — refreshing token and retrying once",
            method.upper(),
            url,
        )
        token_manager.invalidate()
        try:
            self.api_token = token_manager.get_token()
        except ClearPassAuthError as e:
            logger.warning("ClearPass: token refresh failed — {}", e)
            return response
        return original(self, url, method, query, content_response_type)

    ClearPassAPILogin._send_request = send_with_retry  # type: ignore[method-assign]
    ClearPassAPILogin._hpe_auth_retry_patched = True  # type: ignore[attr-defined]


_install_class_auth_retry()


def create_api_client[T: ClearPassAPILogin](
    api_class: type[T],
    config: ClearPassSecrets,
    token_manager: ClearPassTokenManager,
) -> T:
    """Create a pyclearpass API client wired up with the shared token manager.

    The returned instance:
      * uses the token manager's currently cached token
      * honours ``config.verify_ssl`` (pyclearpass hardcodes ``False``)
      * automatically refreshes the token and retries once on 401/403
        (via the class-level :func:`_install_class_auth_retry` patch)

    Args:
        api_class: Any pyclearpass API class (e.g. ``ApiIdentities``).
        config: ClearPass connection details from Docker secrets.
        token_manager: Shared token manager for refresh-on-auth-error.

    Returns:
        Configured API class instance ready for calls.
    """
    instance = api_class(server=config.server, api_token=token_manager.get_token())
    instance.verify_ssl = config.verify_ssl
    setattr(instance, _TOKEN_MANAGER_ATTR, token_manager)
    return instance


async def get_clearpass_session[T: ClearPassAPILogin](api_class: type[T]) -> T:
    """Get a pyclearpass API client from the lifespan context.

    Usage in tools::

        from pyclearpass.api_identities import ApiIdentities
        client = await get_clearpass_session(ApiIdentities)
        result = client.get_guest_by_guest_id(guest_id="42")

    Args:
        api_class: The pyclearpass API class to instantiate.

    Returns:
        Configured API client instance with auth-retry installed.

    Raises:
        ToolError: If ClearPass is not configured or token acquisition fails.
    """
    ctx = get_context()
    config: ClearPassSecrets | None = ctx.lifespan_context.get("clearpass_config")
    token_manager: ClearPassTokenManager | None = ctx.lifespan_context.get("clearpass_token_manager")

    if config is None or token_manager is None:
        raise ToolError(
            {
                "status_code": 503,
                "message": "ClearPass API session not available. Check your ClearPass credentials.",
            }
        )

    try:
        token = token_manager.get_token()
    except ClearPassAuthError as e:
        raise ToolError(
            {
                "status_code": 503,
                "message": f"ClearPass token refresh failed: {e}",
            }
        ) from e

    logger.debug(
        "ClearPass API request — server: {}, token: {}",
        config.server,
        mask_secret(token),
    )
    return create_api_client(api_class, config, token_manager)
