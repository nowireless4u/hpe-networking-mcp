"""AOS8 alerts / events / audit-trail read tools (READ-13..15).

These tools wrap the ``showcommand`` endpoint via the shared ``run_show``
helper, which strips the ``_meta`` and ``_global_result`` envelopes before
returning the body to the AI client.

``aos8_get_alarms`` and ``aos8_get_events`` accept an optional
``config_path`` (default ``"/md"``) so the caller can target a specific
Mobility Conductor branch or managed-device node. ``aos8_get_audit_trail``
intentionally does NOT accept ``config_path`` — the audit trail is a
controller-wide log and the AOS8 ``show audit-trail`` command does not
take a hierarchy parameter.
"""

from __future__ import annotations

from typing import Any

from fastmcp import Context

from hpe_networking_mcp.platforms.aos8._registry import tool
from hpe_networking_mcp.platforms.aos8.tools import READ_ONLY
from hpe_networking_mcp.platforms.aos8.tools._helpers import (
    format_aos8_error,
    run_show,
)

__all__ = [
    "aos8_get_alarms",
    "aos8_get_audit_trail",
    "aos8_get_events",
]


@tool(name="aos8_get_alarms", annotations=READ_ONLY)
async def aos8_get_alarms(ctx: Context, config_path: str = "/md") -> dict[str, Any] | str:
    """List active alarms reported by the AOS8 controller.

    Args:
        ctx: FastMCP request context; ``ctx.lifespan_context["aos8_client"]``
            must hold an authenticated ``AOS8Client``.
        config_path: Hierarchy node to query (e.g. ``"/md"``, ``"/md/branch1"``).
            Defaults to ``"/md"``.

    Returns:
        Parsed JSON body with ``_meta`` and ``_global_result`` stripped, or a
        formatted error string when the API call fails.
    """
    client = ctx.lifespan_context["aos8_client"]
    try:
        return await run_show(client, "show alarms", config_path=config_path)
    except Exception as exc:  # noqa: BLE001
        return format_aos8_error(exc, "list alarms")


@tool(name="aos8_get_audit_trail", annotations=READ_ONLY)
async def aos8_get_audit_trail(ctx: Context) -> dict[str, Any] | str:
    """Fetch the AOS8 controller-wide audit trail.

    Args:
        ctx: FastMCP request context; ``ctx.lifespan_context["aos8_client"]``
            must hold an authenticated ``AOS8Client``.

    Returns:
        Parsed JSON body with ``_meta`` and ``_global_result`` stripped, or a
        formatted error string when the API call fails.
    """
    client = ctx.lifespan_context["aos8_client"]
    try:
        return await run_show(client, "show audit-trail")
    except Exception as exc:  # noqa: BLE001
        return format_aos8_error(exc, "fetch audit trail")


@tool(name="aos8_get_events", annotations=READ_ONLY)
async def aos8_get_events(ctx: Context, config_path: str = "/md") -> dict[str, Any] | str:
    """Fetch recent events logged by the AOS8 controller.

    Args:
        ctx: FastMCP request context; ``ctx.lifespan_context["aos8_client"]``
            must hold an authenticated ``AOS8Client``.
        config_path: Hierarchy node to query (e.g. ``"/md"``, ``"/md/branch1"``).
            Defaults to ``"/md"``.

    Returns:
        Parsed JSON body with ``_meta`` and ``_global_result`` stripped, or a
        formatted error string when the API call fails.
    """
    client = ctx.lifespan_context["aos8_client"]
    try:
        return await run_show(client, "show events", config_path=config_path)
    except Exception as exc:  # noqa: BLE001
        return format_aos8_error(exc, "fetch events")
