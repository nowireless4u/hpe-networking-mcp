"""Mist HTTP client — direct httpx, replaces the ``mistapi`` SDK.

The ``mistapi`` Python SDK was a ~10-line wrapper around the Mist REST API
(auth header injection + a `getSelf` helper). The spec-driven generator
emits tool functions that call into ``mist_request`` here directly, so
the SDK dependency was redundant. See issue #304.

The client is constructed in ``server.lifespan`` from the operator's Mist
host + API token, stashed on ``ctx.lifespan_context["mist_client"]``, and
consumed by every generated Mist tool via ``mist_request(ctx, ...)``.

Org-id validation, pagination-header detection, and error shaping that
used to live on ``mistapi.APIResponse`` are reimplemented here against
``httpx.Response``.
"""

from __future__ import annotations

import contextlib
import json as _json
from typing import Any

import httpx
from fastmcp import Context
from fastmcp.exceptions import ToolError
from loguru import logger

# Status code → human-friendly message used in ToolError responses when the
# server doesn't return a useful detail body.
_STATUS_MESSAGES: dict[int, str] = {
    400: "Bad Request. The API endpoint exists but its syntax/payload is incorrect, detail may be given",
    401: "Unauthorized",
    403: "Permission Denied",
    404: "Not found. The API endpoint doesn't exist or resource doesn't exist",
    429: "Too Many Requests. The API Token used for the request reached the 5000 API Calls per hour threshold",
}


def build_mist_client(host: str, api_token: str) -> httpx.AsyncClient:
    """Construct the httpx AsyncClient stashed on the lifespan context.

    Args:
        host: Mist API host (e.g. ``api.mist.com``, ``api.eu.mist.com``,
            ``api.gc1.mist.com``).
        api_token: Long-lived Mist API token. Sent in the ``Authorization``
            header as ``Token <value>`` per Mist's docs.

    Returns:
        Configured ``httpx.AsyncClient`` with base URL + auth header set.
    """
    base_url = host if host.startswith("http") else f"https://{host}"
    return httpx.AsyncClient(
        base_url=base_url,
        headers={
            "Authorization": f"Token {api_token}",
            "Accept": "application/json",
            "User-Agent": "hpe-networking-mcp/3 (https://github.com/nowireless4u/hpe-networking-mcp)",
        },
        timeout=httpx.Timeout(30.0, connect=10.0),
    )


def _validate_org_id(ctx: Context, org_id: Any) -> str:
    """Guard against the AI passing the wrong org_id.

    The lifespan handler caches the token's actual ``org_id`` at startup
    via ``getSelf``. If the AI passes a different value, raise a
    ``ToolError`` with the correct id so it can self-correct without
    burning an extra API round-trip.

    Returns the string form of the validated id. ``None`` / missing
    cached id is allowed (we don't have one to compare against).
    """
    correct = ctx.lifespan_context.get("mist_org_id")
    if correct and str(org_id) != str(correct):
        raise ToolError(
            f"Wrong org_id '{org_id}'. The correct org_id for this "
            f"API token is '{correct}'. Use this org_id for all Mist "
            f"API calls."
        )
    return str(org_id)


def _strip_none(d: dict[str, Any]) -> dict[str, Any]:
    """Drop keys whose value is ``None`` (httpx serializes them as the
    string ``"None"`` in query strings, which Mist rejects).
    """
    return {k: v for k, v in d.items() if v is not None}


def _decode_pagination(response: httpx.Response, body: Any) -> Any:
    """Inject ``has_more`` / ``next`` / ``total`` metadata when present.

    Mist's pagination contract:
    * ``X-Page-Total`` header gives total result count when paginating.
    * ``X-Next-Page`` header (or response ``next`` field) gives the next
      page URL when more results exist.

    Returns the body unchanged when no pagination signals exist; otherwise
    returns a dict / list with the metadata fields added so the AI can
    detect "there are more results to fetch."
    """
    next_url = response.headers.get("X-Next-Page")
    total: int | None = None
    if "X-Page-Total" in response.headers:
        with contextlib.suppress(ValueError):
            total = int(response.headers["X-Page-Total"])

    if next_url:
        if isinstance(body, list):
            wrapped: dict[str, Any] = {"results": body, "next": next_url, "has_more": True}
            if total is not None:
                wrapped["total"] = total
            return wrapped
        if isinstance(body, dict):
            body = dict(body)
            body["next"] = next_url
            body["has_more"] = True
            if total is not None and "total" not in body:
                body["total"] = total
            return body
    elif isinstance(body, dict):
        body = dict(body)
        body["has_more"] = False
    return body


def _raise_for_status(response: httpx.Response) -> None:
    """Convert non-2xx responses to ``ToolError`` with structured details.

    Mist returns useful error bodies on 4xx/5xx; surface them to the AI.
    For 403, include the standard hint about `mist_get_self_account_info`
    being the canonical org_id source.
    """
    if response.status_code < 400:
        return

    detail: Any
    try:
        detail = response.json()
    except (ValueError, _json.JSONDecodeError):
        detail = response.text or _STATUS_MESSAGES.get(response.status_code, "Unknown error")

    logger.error("Mist API HTTP {} — {}", response.status_code, detail)

    if response.status_code == 403:
        raise ToolError(
            {
                "status_code": 403,
                "message": (
                    "Permission Denied. This usually means you are using a "
                    "tool with an invalid id (e.g. org_id, site_id). Make "
                    "sure to retrieve them from another tool (e.g. use "
                    "`mist_get_self_account_info` to retrieve the correct "
                    "org_id)."
                ),
            }
        )

    raise ToolError(
        {
            "status_code": response.status_code,
            "message": (_json.dumps(detail) if not isinstance(detail, str) else detail),
        }
    )


async def mist_request(
    ctx: Context,
    method: str,
    path: str,
    *,
    path_params: dict[str, Any] | None = None,
    query_params: dict[str, Any] | None = None,
    body: dict[str, Any] | list[Any] | None = None,
) -> Any:
    """Issue one Mist API request from a generated tool.

    Args:
        ctx: FastMCP tool-invocation context (carries the httpx client +
            cached org_id).
        method: HTTP verb (``GET`` / ``POST`` / ``PUT`` / ``PATCH`` /
            ``DELETE``).
        path: URL template with ``{name}`` placeholders for path params
            (e.g. ``"/api/v1/orgs/{org_id}/sites"``).
        path_params: Values to substitute into ``path``'s placeholders.
            When the dict contains ``org_id``, the value is validated
            against the cached token org_id.
        query_params: Query-string parameters. ``None`` values are
            stripped before sending.
        body: JSON body for write methods. Ignored for ``GET`` /
            ``DELETE``.

    Returns:
        Parsed JSON response body. List responses are wrapped with
        pagination metadata when ``X-Next-Page`` / ``X-Page-Total``
        headers indicate more results exist.

    Raises:
        ToolError: On non-2xx responses or transport-level failures.
            Structured shape: ``{"status_code": int, "message": str}``.
    """
    client: httpx.AsyncClient | None = ctx.lifespan_context.get("mist_client")
    if client is None:
        raise ToolError(
            {
                "status_code": 503,
                "message": "Mist API client not available. Check your Mist credentials.",
            }
        )

    # Path-param substitution (and org_id validation when present).
    substituted = path
    if path_params:
        for name, value in path_params.items():
            if name == "org_id":
                value = _validate_org_id(ctx, value)
            substituted = substituted.replace("{" + name + "}", str(value))

    clean_query = _strip_none(query_params or {})
    request_kwargs: dict[str, Any] = {"params": clean_query} if clean_query else {}
    if body is not None and method.upper() not in ("GET", "DELETE"):
        request_kwargs["json"] = body

    try:
        response = await client.request(method, substituted, **request_kwargs)
    except httpx.HTTPError as exc:
        raise ToolError(
            {
                "status_code": 503,
                "message": f"Mist API call failed: {type(exc).__name__}: {exc}",
            }
        ) from exc

    _raise_for_status(response)

    if response.status_code == 204 or not response.content:
        return {"has_more": False}

    try:
        parsed = response.json()
    except (ValueError, _json.JSONDecodeError):
        return {"raw": response.text, "has_more": False}

    return _decode_pagination(response, parsed)


async def resolve_org_id_from_self(client: httpx.AsyncClient) -> str | None:
    """One-shot ``getSelf`` lookup used at lifespan startup.

    Returns the org_id from the token's first ``privileges`` entry whose
    ``scope == 'org'``, or ``None`` if the call fails or no org-scope
    privilege exists. Doesn't raise — the lifespan handler logs the
    failure and continues with degraded state.
    """
    try:
        response = await client.get("/api/v1/self")
    except httpx.HTTPError as exc:
        logger.warning("Mist getSelf failed at lifespan startup — {}", exc)
        return None
    if response.status_code != 200:
        logger.warning(
            "Mist getSelf returned HTTP {} at lifespan startup — {}",
            response.status_code,
            response.text[:200],
        )
        return None
    body = response.json()
    privileges = body.get("privileges", [])
    org_privs = [p for p in privileges if p.get("scope") == "org"]
    if not org_privs:
        return None
    return org_privs[0].get("org_id")
