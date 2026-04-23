"""Aruba Central alias configuration tools.

Provides read access to Central's alias system. Aliases are named
references used in WLAN profiles (e.g. SSID aliases), server groups,
and other configuration objects.
"""

from fastmcp import Context

from hpe_networking_mcp.platforms.central._registry import tool
from hpe_networking_mcp.platforms.central.tools import READ_ONLY
from hpe_networking_mcp.platforms.central.utils import retry_central_command


@tool(annotations=READ_ONLY)
async def central_get_aliases(
    ctx: Context,
    alias_name: str | None = None,
) -> dict | list | str:
    """
    Get alias configurations from Aruba Central.

    Aliases are named references used in WLAN profiles and other config
    objects. For example, SSID aliases map a profile name to the actual
    broadcasted SSID name.

    Parameters:
        alias_name: Specific alias name to retrieve. If omitted, returns all aliases.

    Returns:
        Single alias dict if alias_name specified, or list of all aliases.
    """
    conn = ctx.lifespan_context["central_conn"]
    api_path = f"network-config/v1alpha1/aliases/{alias_name}" if alias_name else "network-config/v1alpha1/aliases"

    response = retry_central_command(
        central_conn=conn,
        api_method="GET",
        api_path=api_path,
    )
    return response.get("msg", {})
