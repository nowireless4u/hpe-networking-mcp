"""Central async API client (replaces the pycentral ``NewCentralBase`` SDK).

Tools obtain the client from ``ctx.lifespan_context["central_conn"]`` (via
``utils.get_central_conn``) rather than importing a global singleton.

The ``command()`` method preserves pycentral's calling convention and return
contract exactly — ``{"code": int, "msg": parsed-json-or-text, "headers":
dict}`` — so the ~660 Central tools that consume responses through
``retry_central_command`` are unaffected by the SDK removal.

Behavior intentionally mirrored from pycentral 2.0a17 ``base.py``:

* Token endpoint ``https://sso.common.cloud.hpe.com/as/token.oauth2`` with
  ``client_secret_basic`` (HTTP Basic) credentials.
* ``Authorization: Bearer <token>`` on every request; default
  ``Content-Type``/``Accept`` of ``application/json``.
* ``None``-valued query params stripped; empty-dict bodies not sent.
* One token refresh + retry on a 401 response.
* Connection limits tuned for Central (max 7 connections, 5 keep-alive).

Differences (deliberate): token acquisition is lazy and async via the shared
:class:`AsyncTokenManager` (pycentral fetched synchronously at construction),
expiry is tracked proactively from ``expires_in`` (pycentral only reacted to
401s), and transport-level retries live in ``retry_central_command`` alone
(pycentral layered 3 internal retries under our 5, multiplying worst-case
attempts).
"""

from __future__ import annotations

import contextlib
import json
from typing import Any

import httpx
from loguru import logger

from hpe_networking_mcp.config import CentralSecrets
from hpe_networking_mcp.platforms._common.auth import AsyncTokenManager, oauth2_client_credentials

_TOKEN_URL = "https://sso.common.cloud.hpe.com/as/token.oauth2"  # nosec B105 - same HPE SSO endpoint pycentral used
_REQUEST_TIMEOUT = httpx.Timeout(30.0, connect=10.0)
_AUTH_TIMEOUT = 10.0
_LIMITS = httpx.Limits(max_connections=7, max_keepalive_connections=5, keepalive_expiry=30)


class CentralClient:
    """Async HPE Aruba Networking Central API client.

    Usage in tools (unchanged from the pycentral era, plus ``await``)::

        conn = get_central_conn(ctx)
        resp = await conn.command(api_method="GET", api_path="network-monitoring/v1/aps")
        items = resp["msg"]["items"]
    """

    def __init__(self, config: CentralSecrets) -> None:
        self._config = config
        self._tokens = AsyncTokenManager(
            oauth2_client_credentials(
                _TOKEN_URL,
                config.client_id,
                config.client_secret,
                name="Central",
                auth_style="basic",
                timeout=_AUTH_TIMEOUT,
            ),
            name="Central",
        )
        self._http = httpx.AsyncClient(
            base_url=config.base_url,
            timeout=_REQUEST_TIMEOUT,
            limits=_LIMITS,
        )

    @property
    def base_url(self) -> str:
        """Return the configured Central API gateway base URL."""
        return str(self._http.base_url)

    async def aclose(self) -> None:
        """Close the underlying httpx client. Called from ``server.py:lifespan``."""
        await self._http.aclose()

    async def command(
        self,
        api_method: str,
        api_path: str,
        api_params: dict[str, Any] | None = None,
        api_data: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Execute one Central API call; pycentral-compatible return contract.

        Args:
            api_method: HTTP method (GET, POST, PUT, PATCH, DELETE).
            api_path: Endpoint path appended to the base URL
                (e.g. ``network-monitoring/v1/aps``).
            api_params: Query parameters; ``None``-valued entries are stripped.
            api_data: JSON request body; an empty/None dict sends no body.

        Returns:
            ``{"code": int, "msg": parsed JSON or raw text, "headers": dict}``.

        Raises:
            httpx.HTTPError: On transport-level failures (connect, timeout,
                protocol). Status errors are NOT raised — the status comes
                back in ``code``, exactly as pycentral behaved.
        """
        params = {k: v for k, v in (api_params or {}).items() if v is not None}
        token = await self._tokens.get_token()
        response = await self._send(api_method, api_path, params, api_data, token)
        if response.status_code == 401:
            logger.info("Central: 401 on {} {} — refreshing token once", api_method, api_path)
            token = await self._tokens.refresh()
            response = await self._send(api_method, api_path, params, api_data, token)

        msg: Any = response.text
        with contextlib.suppress(ValueError, json.JSONDecodeError):
            msg = response.json()
        return {"code": response.status_code, "msg": msg, "headers": dict(response.headers)}

    async def _send(
        self,
        method: str,
        path: str,
        params: dict[str, Any],
        body: dict[str, Any] | None,
        token: str,
    ) -> httpx.Response:
        kwargs: dict[str, Any] = {
            "headers": {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            }
        }
        if params:
            kwargs["params"] = params
        if body:
            kwargs["json"] = body
        return await self._http.request(method, path, **kwargs)

    async def health_check(self) -> bool:
        """Probe credentials + reachability with a 1-item sites-health read."""
        resp = await self.command(
            api_method="GET",
            api_path="network-monitoring/v1/sites-health",
            api_params={"limit": 1},
        )
        return isinstance(resp.get("code"), int) and 200 <= resp["code"] < 300


def create_connection(secrets: CentralSecrets) -> CentralClient:
    """Build a new :class:`CentralClient` from config secrets.

    Construction is cheap and non-blocking — the first API call triggers the
    initial token fetch (pycentral fetched synchronously in ``__init__``,
    which used to block the lifespan event loop at startup).
    """
    return CentralClient(secrets)


async def verify_connection(conn: CentralClient) -> None:
    """Verify credentials are valid by making a lightweight GET to the Central API.

    Raises:
        RuntimeError: With a clear message if the connection fails.
    """
    try:
        ok = await conn.health_check()
    except Exception as exc:
        raise RuntimeError(
            f"Central API connectivity check failed: {exc}. "
            "Check central_base_url, central_client_id, and central_client_secret secrets."
        ) from exc
    if not ok:
        raise RuntimeError(
            "Central API connectivity check failed (non-2xx response). "
            "Check central_base_url, central_client_id, and central_client_secret secrets."
        )


__all__ = ["CentralClient", "create_connection", "verify_connection"]
