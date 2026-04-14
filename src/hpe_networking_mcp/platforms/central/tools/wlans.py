from fastmcp import Context
from pycentral.new_monitoring.aps import MonitoringAPs

from hpe_networking_mcp.platforms.central._registry import mcp
from hpe_networking_mcp.platforms.central.tools import READ_ONLY


@mcp.tool(annotations=READ_ONLY)
async def central_get_wlans(
    ctx: Context,
    site_id: str | None = None,
    serial_number: str | None = None,
    filter: str | None = None,
    sort: str | None = None,
    limit: int = 100,
) -> list[dict] | str:
    """
    List all WLANs/SSIDs configured in Aruba Central.

    Returns WLAN name, SSID profile, security type, VLAN,
    band, and status. Use site_id or serial_number to narrow
    results to a specific site or AP.

    Parameters:
        site_id: Filter WLANs by site ID. Obtain from
            central_get_site_name_id_mapping.
        serial_number: Filter WLANs served by a specific AP.
        filter: OData filter string for advanced filtering.
        sort: Sort expression (e.g., 'essid asc').
        limit: Maximum results to return (default 100).
    """
    conn = ctx.lifespan_context["central_conn"]
    try:
        kwargs: dict = {
            "central_conn": conn,
            "limit": limit,
        }
        if site_id is not None:
            kwargs["site_id"] = site_id
        if serial_number is not None:
            kwargs["serial_number"] = serial_number
        if filter is not None:
            kwargs["filter_str"] = filter
        if sort is not None:
            kwargs["sort"] = sort

        resp = MonitoringAPs.get_wlans(**kwargs)
    except Exception as e:
        return f"Error fetching WLANs: {e}"

    if isinstance(resp, dict):
        items = resp.get("items", [])
        if items:
            return items
        return "No WLANs found."
    if isinstance(resp, list):
        return resp if resp else "No WLANs found."
    return "No WLANs found."
