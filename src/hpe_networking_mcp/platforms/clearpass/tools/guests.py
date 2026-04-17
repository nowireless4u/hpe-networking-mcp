"""ClearPass guest user read tools."""

from __future__ import annotations

from fastmcp import Context

from hpe_networking_mcp.platforms.clearpass._registry import mcp
from hpe_networking_mcp.platforms.clearpass.client import get_clearpass_session
from hpe_networking_mcp.platforms.clearpass.tools import READ_ONLY


@mcp.tool(annotations=READ_ONLY)
async def clearpass_get_guest_users(
    ctx: Context,
    guest_id: str | None = None,
    username: str | None = None,
    filter: str | None = None,
    sort: str | None = None,
    offset: int = 0,
    limit: int = 25,
) -> dict | str:
    """Get ClearPass guest user accounts.

    If guest_id or username is provided, returns a single guest account.
    Otherwise returns a paginated list of all guest accounts.

    Args:
        guest_id: Numeric ID for single-item lookup.
        username: Guest username for lookup by username.
        filter: JSON filter expression (ClearPass REST API syntax).
        sort: Sort order (e.g. "+name" or "-id").
        offset: Pagination offset (default 0).
        limit: Max results per page (default 25).
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
        ]
        query = "?" + "&".join(p for p in params if p)
        return client._send_request("/guest" + query, "get")
    except Exception as e:
        return f"Error fetching guest users: {e}"
