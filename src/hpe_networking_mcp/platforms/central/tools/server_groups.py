"""Aruba Central server group configuration tools.

Provides read access to Central's RADIUS/auth server groups.
Server groups are named references used in WLAN profiles for
authentication and accounting servers.
"""

from fastmcp import Context

from hpe_networking_mcp.platforms.central._registry import tool
from hpe_networking_mcp.platforms.central.tools import READ_ONLY
from hpe_networking_mcp.platforms.central.utils import retry_central_command


@tool(annotations=READ_ONLY)
async def central_get_server_groups(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """
    Get RADIUS/auth server group configurations from Aruba Central.

    Server groups define collections of RADIUS servers used by WLAN
    profiles for authentication and accounting. Use this to resolve
    a server group name (from a WLAN profile's auth-server-group field)
    to its actual server IP addresses and settings.

    Parameters:
        name: Specific server group name to retrieve. If omitted, returns all groups.

    Returns:
        Single server group dict if name specified, or list of all groups.
    """
    conn = ctx.lifespan_context["central_conn"]
    api_path = f"network-config/v1alpha1/server-groups/{name}" if name else "network-config/v1alpha1/server-groups"

    response = retry_central_command(
        central_conn=conn,
        api_method="GET",
        api_path=api_path,
    )
    return response.get("msg", {})
