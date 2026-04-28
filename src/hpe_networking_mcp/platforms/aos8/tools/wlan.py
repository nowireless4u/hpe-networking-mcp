"""AOS8 WLAN / configuration-object read tools (READ-16..19).

Unlike the other read categories, these tools fetch hierarchical
configuration objects via ``/v1/configuration/object/<name>`` rather than
the ``showcommand`` endpoint. They route through the shared ``get_object``
helper, which strips the ``_meta`` and ``_global_result`` envelopes before
returning the body to the AI client.

All tools accept an optional ``config_path`` (default ``"/md"``) so the
caller can target a specific Mobility Conductor branch, AP-group, or
managed-device node.
"""

from __future__ import annotations

from typing import Any

from hpe_networking_mcp.platforms.aos8._registry import tool
from hpe_networking_mcp.platforms.aos8.tools import READ_ONLY
from hpe_networking_mcp.platforms.aos8.tools._helpers import (
    format_aos8_error,
    get_object,
)

__all__ = [
    "aos8_get_ssid_profiles",
    "aos8_get_virtual_aps",
    "aos8_get_ap_groups",
    "aos8_get_user_roles",
]


@tool(name="aos8_get_ssid_profiles", annotations=READ_ONLY)
async def aos8_get_ssid_profiles(ctx: Any, config_path: str = "/md") -> dict[str, Any] | str:
    """Fetch SSID profiles defined at the given configuration node.

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
        return await get_object(client, "ssid_prof", config_path=config_path)
    except Exception as exc:  # noqa: BLE001
        return format_aos8_error(exc, "fetch SSID profiles")


@tool(name="aos8_get_virtual_aps", annotations=READ_ONLY)
async def aos8_get_virtual_aps(ctx: Any, config_path: str = "/md") -> dict[str, Any] | str:
    """Fetch virtual-AP profiles defined at the given configuration node.

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
        return await get_object(client, "virtual_ap", config_path=config_path)
    except Exception as exc:  # noqa: BLE001
        return format_aos8_error(exc, "fetch virtual APs")


@tool(name="aos8_get_ap_groups", annotations=READ_ONLY)
async def aos8_get_ap_groups(ctx: Any, config_path: str = "/md") -> dict[str, Any] | str:
    """Fetch AP-group definitions at the given configuration node.

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
        return await get_object(client, "ap_group", config_path=config_path)
    except Exception as exc:  # noqa: BLE001
        return format_aos8_error(exc, "fetch AP groups")


@tool(name="aos8_get_user_roles", annotations=READ_ONLY)
async def aos8_get_user_roles(ctx: Any, config_path: str = "/md") -> dict[str, Any] | str:
    """Fetch user-role definitions at the given configuration node.

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
        return await get_object(client, "role", config_path=config_path)
    except Exception as exc:  # noqa: BLE001
        return format_aos8_error(exc, "fetch user roles")
