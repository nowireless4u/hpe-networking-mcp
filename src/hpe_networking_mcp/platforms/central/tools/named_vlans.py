"""Aruba Central named VLAN configuration tools.

Provides read access to Central's named VLAN definitions.
Named VLANs map a human-readable name to a VLAN ID, optionally
via an alias reference.
"""

from fastmcp import Context

from hpe_networking_mcp.platforms.central._registry import tool
from hpe_networking_mcp.platforms.central.tools import READ_ONLY
from hpe_networking_mcp.platforms.central.utils import retry_central_command


@tool(annotations=READ_ONLY)
async def central_get_named_vlans(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """
    Get named VLAN configurations from Aruba Central.

    Named VLANs map a human-readable name (e.g. "USER-VLAN") to a
    VLAN ID. The VLAN ID may be configured directly or via an alias.
    Use this to resolve a named VLAN from a WLAN profile's vlan-name
    field to its actual VLAN ID.

    Parameters:
        name: Specific named VLAN to retrieve. If omitted, returns all named VLANs.

    Returns:
        Single named VLAN dict if name specified, or list of all named VLANs.
    """
    conn = ctx.lifespan_context["central_conn"]
    api_path = f"network-config/v1alpha1/named-vlan/{name}" if name else "network-config/v1alpha1/named-vlan"

    response = retry_central_command(
        central_conn=conn,
        api_method="GET",
        api_path=api_path,
    )
    return response.get("msg", {})
