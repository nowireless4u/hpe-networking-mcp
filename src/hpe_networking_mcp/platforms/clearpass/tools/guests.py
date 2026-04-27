"""ClearPass guest user read tools."""

from __future__ import annotations

from fastmcp import Context

from hpe_networking_mcp.platforms.clearpass._registry import tool
from hpe_networking_mcp.platforms.clearpass.client import get_clearpass_session
from hpe_networking_mcp.platforms.clearpass.tools import READ_ONLY


@tool(annotations=READ_ONLY)
async def clearpass_get_guest_users(
    ctx: Context,
    guest_id: str | None = None,
    username: str | None = None,
    filter: str | None = None,
    sort: str | None = None,
    offset: int = 0,
    limit: int = 25,
    calculate_count: bool = False,
) -> dict | str:
    """Get a single ClearPass guest account by ID or username, OR list all guest accounts.

    Dual-mode: if `guest_id` or `username` is provided, returns ONE guest record.
    Otherwise returns a paginated LIST of all guests (use `filter`/`sort`/`offset`/`limit`).

    Args:
        guest_id: Numeric ID for single-record lookup.
        username: Guest username for single-record lookup.
        filter: JSON filter expression (ClearPass REST API syntax). List mode only.
        sort: Sort order (e.g. "+name" or "-id"). List mode only.
        offset: Pagination offset (default 0). List mode only.
        limit: Max results per page (default 25). List mode only.
    """
    try:
        from pyclearpass.api_identities import ApiIdentities

        client = await get_clearpass_session(ApiIdentities)
        if guest_id:
            return client.get_guest_by_guest_id(guest_id=guest_id)
        if username:
            return client.get_guest_username_by_username(username=username)
        params = [
            f"filter={filter}" if filter else "",
            f"sort={sort}" if sort else "",
            f"offset={offset}",
            f"limit={limit}",
            f"calculate_count={'true' if calculate_count else 'false'}",
        ]
        query = "?" + "&".join(p for p in params if p)
        return client._send_request("/guest" + query, "get")
    except Exception as e:
        return f"Error fetching guest users: {e}"
