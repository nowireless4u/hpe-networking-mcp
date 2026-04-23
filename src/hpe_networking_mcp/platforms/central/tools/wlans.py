from typing import Literal

from fastmcp import Context
from pycentral.new_monitoring.aps import MonitoringAPs

from hpe_networking_mcp.platforms.central._registry import tool
from hpe_networking_mcp.platforms.central.tools import READ_ONLY
from hpe_networking_mcp.platforms.central.utils import resolve_time_window, retry_central_command


@tool(annotations=READ_ONLY)
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


TIME_RANGE = Literal["last_1h", "last_6h", "last_24h", "last_7d", "last_30d", "today", "yesterday"]


@tool(annotations=READ_ONLY)
async def central_get_wlan_stats(
    ctx: Context,
    wlan_name: str,
    time_range: TIME_RANGE = "last_1h",
    start_time: str | None = None,
    end_time: str | None = None,
) -> list[dict] | str:
    """
    Get throughput trend data for a specific WLAN over a time window.

    Returns a time-series of throughput samples with timestamp, tx
    (transmitted) and rx (received) values in bits per second. Use
    this to analyze WLAN performance trends over time.

    Parameters:
        wlan_name: WLAN name (SSID) to get stats for (required).
        time_range: Predefined time window. Allowed: last_1h, last_6h,
            last_24h, last_7d, last_30d, today, yesterday.
            Ignored if both start_time and end_time are provided.
        start_time: Start of time window in RFC 3339 format
            (e.g. "2026-04-15T00:00:00.000Z"). Overrides time_range
            when combined with end_time.
        end_time: End of time window in RFC 3339 format.
            Overrides time_range when combined with start_time.
    """
    start_at, end_at = resolve_time_window(time_range, start_time, end_time)
    conn = ctx.lifespan_context["central_conn"]

    try:
        response = retry_central_command(
            central_conn=conn,
            api_method="GET",
            api_path=f"network-monitoring/v1/wlans/{wlan_name}/throughput-trends",
            api_params={"filter": f"timestamp gt {start_at} and timestamp lt {end_at}"},
        )
    except Exception as e:
        return f"Error fetching WLAN statistics: {e}"

    code = response.get("code", 0)
    if not (200 <= code < 300):
        return f"Error fetching WLAN stats (HTTP {code}): {response.get('msg')}"

    # Flatten the graph structure into a list of samples
    msg = response.get("msg", {})
    graph = msg.get("graph", {}) if isinstance(msg, dict) else {}
    keys = graph.get("keys", [])
    samples = graph.get("samples", [])

    result = []
    for sample in samples:
        data = sample.get("data", [])
        values = dict(zip(keys, data, strict=False))
        if all(v is None for v in values.values()):
            continue
        result.append(
            {
                "timestamp": sample.get("timestamp"),
                "tx": values.get("tx"),
                "rx": values.get("rx"),
            }
        )

    if not result:
        return f"No throughput data found for WLAN '{wlan_name}'."
    return result
