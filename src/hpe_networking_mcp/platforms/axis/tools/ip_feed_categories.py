"""Axis IP-feed category read tools (``/IpCategoriesFeed``)."""

from __future__ import annotations

from typing import Any

from fastmcp import Context

from hpe_networking_mcp.platforms.axis._registry import tool
from hpe_networking_mcp.platforms.axis.client import format_http_error, get_axis_client
from hpe_networking_mcp.platforms.axis.tools import READ_ONLY


@tool(annotations=READ_ONLY)
async def axis_get_ip_feed_categories(
    ctx: Context,
    ip_feed_category_id: str | None = None,
    page_number: int = 1,
    page_size: int = 50,
) -> dict[str, Any] | str:
    """Get Axis IP-feed categories.

    Threat-intel IP feeds maintained by Axis (vs. customer-defined feeds
    in ``axis_get_custom_ip_categories``).

    Args:
        ip_feed_category_id: GUID for single-item lookup.
        page_number: 1-indexed page number for list calls.
        page_size: Items per page for list calls.
    """
    try:
        client = await get_axis_client()
        if ip_feed_category_id:
            return await client.get_json(f"/IpCategoriesFeed/{ip_feed_category_id}")
        return await client.get_paged("/IpCategoriesFeed", page_number=page_number, page_size=page_size)
    except Exception as e:
        return f"Error fetching IP feed categories: {format_http_error(e)}"
