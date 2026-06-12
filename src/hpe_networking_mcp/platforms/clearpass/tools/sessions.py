"""ClearPass session read tools."""

from __future__ import annotations

from fastmcp import Context
from fastmcp.exceptions import ToolError

from hpe_networking_mcp.platforms._common.annotations import Capability
from hpe_networking_mcp.platforms.clearpass._registry import tool
from hpe_networking_mcp.platforms.clearpass.client import get_clearpass_client
from hpe_networking_mcp.platforms.clearpass.utils import clearpass_get


@tool(capability=Capability.READ)
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
        client = await get_clearpass_client()
        if session_id:
            return await client.request("get", f"/session/{session_id}")
        params = [
            f"filter={filter}" if filter else "",
            f"sort={sort}" if sort else "",
            f"offset={offset}",
            f"limit={limit}",
            f"calculate_count={'true' if calculate_count else 'false'}",
        ]
        query = "?" + "&".join(p for p in params if p)
        return await clearpass_get(client, "/session" + query)
    except ToolError:
        raise
    except Exception as e:
        raise ToolError({"status_code": 502, "message": f"Error fetching sessions: {e}"}) from e


@tool(capability=Capability.READ)
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
        client = await get_clearpass_client()
        return await client.request("get", f"/session-action/{action_id}")
    except ToolError:
        raise
    except Exception as e:
        raise ToolError({"status_code": 502, "message": f"Error fetching session action status: {e}"}) from e


@tool(capability=Capability.READ)
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
        client = await get_clearpass_client()
        return await client.request("get", f"/session/{session_id}/reauthorize")
    except ToolError:
        raise
    except Exception as e:
        raise ToolError({"status_code": 502, "message": f"Error fetching reauthorization profiles: {e}"}) from e
