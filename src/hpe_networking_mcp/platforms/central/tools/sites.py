from fastmcp import Context
from pycentral.new_monitoring import MonitoringSites

from hpe_networking_mcp.platforms.central._registry import mcp
from hpe_networking_mcp.platforms.central.models import SiteData
from hpe_networking_mcp.platforms.central.tools import READ_ONLY
from hpe_networking_mcp.platforms.central.utils import (
    fetch_site_data_parallel,
    groups_to_map,
)


@mcp.tool(annotations=READ_ONLY)
async def central_get_sites(ctx: Context, site_names: list[str] | None = None) -> list[SiteData]:
    """
    Returns detailed metrics for one or more sites.

    Prefer calling with a site_names filter targeting only the sites you care about.
    Do NOT call without a filter unless the user explicitly requests data for all
    sites — returning all sites is expensive and consumes significant context.

    Recommended workflow: Call central_get_site_name_id_mapping first to get a
    lightweight overview of all sites (names, IDs, health scores). Use health scores
    and alert counts to decide which sites warrant further investigation, then call
    this tool with those specific site names.

    Parameters:
    - site_names: One or more site name to filter by. Supports exact matches.
      If omitted, all sites are returned (use sparingly or when explicitly requested).
    """
    sites_data = fetch_site_data_parallel(ctx.lifespan_context["central_conn"])
    if site_names:
        return [sites_data[name] for name in site_names if name in sites_data]
    return list(sites_data.values())


@mcp.tool(annotations=READ_ONLY)
async def central_get_site_name_id_mapping(ctx: Context) -> dict:
    """
    Returns a lightweight mapping of all site names to their IDs and health
    scores. The list is sorted by health score (lowest to highest — worst to best)
    to help quickly identify sites that may need attention. Sites with
    unknown/None health values are placed last.

    Use this before calling central_get_sites or any endpoint that requires a
    site_id. It is especially useful when the user provides a partial or ambiguous
    site name — verify the correct name here, then pass it to the appropriate tool.
    The health score also helps identify sites with issues before drilling down
    further.

    Returns a dict where each key is a site name and the value contains:
    - site_id: Unique identifier used in other API calls.
    - health: Overall health score (0-100, weighted average:
      Good=100, Fair=50, Poor=0).
    - total_devices: Total number of devices at the site.
    - total_clients: Total number of clients at the site.
    - total_alerts: Total number of alerts at the site.
    """
    sites = MonitoringSites.get_all_sites(central_conn=ctx.lifespan_context["central_conn"])
    mapping = {}
    for site in sites:
        health_obj = groups_to_map(site.get("health", {}))
        summary = None
        if all(k in health_obj for k in ["Poor", "Fair", "Good"]):
            summary = round((health_obj["Poor"] * 0) + (health_obj["Fair"] * 0.5) + (health_obj["Good"] * 1))
        mapping[site["siteName"]] = {
            "site_id": site.get("id"),
            "health": summary,
            "total_devices": site.get("devices", {}).get("total", 0),
            "total_clients": site.get("clients", {}).get("total", 0),
            "total_alerts": site.get("alerts", {}).get("total", 0),
        }
    mapping = dict(
        sorted(
            mapping.items(),
            key=lambda item: item[1]["health"] if item[1]["health"] is not None else float("inf"),
            reverse=False,
        )
    )
    return mapping
