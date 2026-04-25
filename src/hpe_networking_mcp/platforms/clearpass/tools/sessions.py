"""ClearPass session read tools."""

from __future__ import annotations

from fastmcp import Context

from hpe_networking_mcp.platforms.clearpass._registry import tool
from hpe_networking_mcp.platforms.clearpass.client import get_clearpass_session
from hpe_networking_mcp.platforms.clearpass.tools import READ_ONLY


@tool(annotations=READ_ONLY)
async def clearpass_get_sessions(
    ctx: Context,
    session_id: str | None = None,
    filter: str | None = None,
    sort: str | None = None,
    offset: int = 0,
    limit: int = 25,
    calculate_count: bool = False,
) -> dict | str:
    """Get ClearPass active sessions.

    If session_id is provided, returns a single session record.
    Otherwise returns a paginated list of active sessions.

    Args:
        session_id: Session ID for single-item lookup.
        filter: JSON filter expression (ClearPass REST API syntax).
        sort: Sort order (e.g. "+acctstarttime" or "-nasipaddress").
        offset: Pagination offset (default 0).
        limit: Max results per page (default 25).
    """
    try:
        from pyclearpass.api_sessioncontrol import ApiSessionControl

        client = await get_clearpass_session(ApiSessionControl)
        if session_id:
            return client.get_session_by_id(id=session_id)
        params = [
            f"filter={filter}" if filter else "",
            f"sort={sort}" if sort else "",
            f"offset={offset}",
            f"limit={limit}",
            f"calculate_count={'true' if calculate_count else 'false'}",
        ]
        query = "?" + "&".join(p for p in params if p)
        return client._send_request("/session" + query, "get")
    except Exception as e:
        return f"Error fetching sessions: {e}"


@tool(annotations=READ_ONLY)
async def clearpass_get_session_action_status(
    ctx: Context,
    action_id: str,
) -> dict | str:
    """Get the status of a ClearPass session action (e.g. disconnect or CoA).

    Returns the current status and result of a previously initiated session
    action such as disconnect, reauthorize, or Change of Authorization (CoA).

    Args:
        action_id: The action ID returned from a session action request.
    """
    try:
        from pyclearpass.api_sessioncontrol import ApiSessionControl

        client = await get_clearpass_session(ApiSessionControl)
        return client.get_session_action_by_action_id(action_id=action_id)
    except Exception as e:
        return f"Error fetching session action status: {e}"


@tool(annotations=READ_ONLY)
async def clearpass_get_reauth_profiles(
    ctx: Context,
    session_id: str,
) -> dict | str:
    """Get available reauthorization profiles for a ClearPass session.

    Returns the reauthorization options available for the specified session,
    including the enforcement profiles that can be applied.

    Args:
        session_id: Session ID to retrieve reauthorization profiles for.
    """
    try:
        from pyclearpass.api_sessioncontrol import ApiSessionControl

        client = await get_clearpass_session(ApiSessionControl)
        return client.get_session_by_id_reauthorize(id=session_id)
    except Exception as e:
        return f"Error fetching reauthorization profiles: {e}"
