"""Shared helpers for AOS8 tool modules.

Every showcommand response from AOS8 includes ``_meta`` (column-name schema)
and ``_global_result`` (status envelope already validated by ``AOS8Client``).
Both are infrastructure noise that AI clients do not need; ``strip_meta``
removes them. ``run_show`` and ``get_object`` provide the two HTTP-call
shapes used across every read tool, and ``format_aos8_error`` renders
exceptions into a consistent, AI-friendly string.
"""

from __future__ import annotations

from typing import Any

import httpx

from hpe_networking_mcp.platforms.aos8.client import (
    AOS8APIError,
    AOS8AuthError,
    AOS8Client,
)

__all__ = ["strip_meta", "run_show", "get_object", "post_object", "format_aos8_error"]


def strip_meta(body: Any) -> Any:
    """Remove AOS8 ``_meta`` and ``_global_result`` keys from a response body.

    Args:
        body: Parsed JSON response body. May be a dict, list, or scalar.

    Returns:
        New dict with ``_meta`` and ``_global_result`` removed when ``body``
        is a dict; otherwise returns ``body`` unchanged.
    """
    if not isinstance(body, dict):
        return body
    return {k: v for k, v in body.items() if k not in ("_meta", "_global_result")}


async def run_show(
    client: AOS8Client,
    command: str,
    *,
    config_path: str | None = None,
) -> Any:
    """Execute an AOS8 show command and return the cleaned JSON body.

    Args:
        client: ``AOS8Client`` from ``ctx.lifespan_context["aos8_client"]``.
        command: Full show command string (e.g. ``"show ap database"``).
        config_path: Optional hierarchy node (e.g. ``"/md"``); included in
            query params only when not ``None``.

    Returns:
        Parsed JSON body with ``_meta`` and ``_global_result`` stripped.
    """
    params: dict[str, Any] = {"command": command}
    if config_path is not None:
        params["config_path"] = config_path
    response = await client.request("GET", "/v1/configuration/showcommand", params=params)
    return strip_meta(response.json())


async def get_object(
    client: AOS8Client,
    object_path: str,
    *,
    config_path: str = "/md",
) -> Any:
    """Fetch a configuration object via ``/v1/configuration/object/<path>``.

    Args:
        client: ``AOS8Client`` instance.
        object_path: Object name (e.g. ``"ssid_prof"``, ``"ap_group"``).
        config_path: Hierarchy node; defaults to ``"/md"``.

    Returns:
        Parsed JSON body with ``_meta`` and ``_global_result`` stripped.
    """
    response = await client.request(
        "GET",
        f"/v1/configuration/object/{object_path}",
        params={"config_path": config_path},
    )
    return strip_meta(response.json())


async def post_object(
    client: AOS8Client,
    object_name: str,
    body: dict[str, Any],
    *,
    config_path: str | None = None,
) -> Any:
    """POST a configuration or operational object to AOS8.

    AOS8 routes most object writes through ``/v1/configuration/object``;
    the object type is identified by the top-level body key. Operational
    endpoints (``apboot``, ``aaa_user_delete``) use the same generic path
    and rely on the body key. ``write_memory`` uses a dedicated path
    and is NOT routed through this helper.

    Args:
        client: ``AOS8Client`` from ``ctx.lifespan_context["aos8_client"]``.
        object_name: Tool-side identifier; used only for diagnostic context.
        body: Pre-wrapped POST body (e.g. ``{"ssid_prof": {...}}``).
        config_path: Hierarchy node. Required for config-object writes;
            may be omitted for operational endpoints.

    Returns:
        Parsed JSON body with ``_meta`` and ``_global_result`` removed.

    Raises:
        AOS8APIError, AOS8AuthError, httpx.HTTPError: per ``AOS8Client.request``.
    """
    params: dict[str, Any] | None = {"config_path": config_path} if config_path is not None else None
    response = await client.request(
        "POST",
        "/v1/configuration/object",
        params=params,
        json_body=body,
    )
    return strip_meta(response.json())


def format_aos8_error(exc: BaseException, action: str) -> str:
    """Render an AOS8 exception as a tool-friendly error message.

    Args:
        exc: The exception caught at the tool boundary.
        action: Short verb phrase describing what was being attempted
            (e.g. ``"list controllers"``).

    Returns:
        Human-readable error string suitable for returning to the AI client.
    """
    if isinstance(exc, AOS8AuthError):
        return f"AOS8 authentication failed while attempting to {action}: {exc}"
    if isinstance(exc, AOS8APIError):
        return f"AOS8 API error while attempting to {action}: {exc}"
    if isinstance(exc, httpx.HTTPStatusError):
        return f"AOS8 HTTP {exc.response.status_code} while attempting to {action}: {exc}"
    if isinstance(exc, httpx.HTTPError):
        return f"AOS8 transport error while attempting to {action}: {exc}"
    return f"Unexpected error while attempting to {action}: {exc}"
