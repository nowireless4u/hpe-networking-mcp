from typing import Literal

from fastmcp import Context

from hpe_networking_mcp.platforms.central.models import PaginatedAlerts
from hpe_networking_mcp.platforms.central.tools import READ_ONLY
from hpe_networking_mcp.platforms.central.utils import (
    FilterField,
    build_odata_filter,
    clean_alert_data,
    retry_central_command,
)

# API hard cap; limit param must not exceed this
ALERT_LIMIT = 100

ALERT_FILTER_FIELDS: dict[str, FilterField] = {
    "status": FilterField("status"),
    "device_type": FilterField("deviceType"),
    "category": FilterField("category"),
    "site_id": FilterField("siteId"),
}


def register(mcp):

    @mcp.tool(annotations=READ_ONLY)
    async def central_get_alerts(
        ctx: Context,
        site_id: str,
        status: Literal["Active", "Cleared", "Deferred"] | None = "Active",
        device_type: Literal["Access Point", "Gateway", "Switch", "Bridge"] | None = None,
        category: Literal["Clients", "System", "LAN", "WLAN", "WAN", "Cluster", "Routing", "Security"] | None = None,
        sort: str = "severity desc",
        limit: int = 50,
        cursor: int | None = None,
    ) -> PaginatedAlerts | str:
        """
        REQUIRES site_id — call central_get_sites(site_names=["<site name>"]) and extract
        site_id from the returned SiteData. Do NOT call this tool without a site_id; it will
        fail validation.

        Returns a filtered list of alerts for a specific site. Use this to drill into active
        issues by device type or category after identifying the target site.

        Results are sorted by severity descending by default (Critical first), making the most
        important alerts appear in the first page. To page through results, pass the `next_cursor`
        value from the previous response as `cursor` in the next call. When `next_cursor` is None,
        there are no more pages.

        If no alerts match the criteria, returns a message indicating so.

        Parameters:
            - site_id: Site identifier. Obtain by calling
              central_get_sites(site_names=["<name>"]) and reading site_id from the result.
            - status: "Active" (default) for unresolved alerts, "Cleared" for resolved ones.
            - device_type: Narrow to a device class — "Access Point", "Gateway", "Switch",
              or "Bridge".
            - category: Narrow to an alert domain — "Clients", "System", "LAN", "WLAN",
              "WAN", "Cluster", "Routing", or "Security".
            - sort: Sort expression (default "severity desc" — most critical first).
              Examples: "createdAt desc", "createdAt asc".
            - limit: Number of alerts per page (default 50, max 100).
            - cursor: Pagination cursor from a previous response's `next_cursor` field.
              Omit or pass None to start from the first page.

        Note: Each alert includes summary, name, category, severity, priority, status,
        deviceType, createdAt, updatedAt, updatedBy, and clearedReason.
        """
        raw_pairs = [
            ("status", status),
            ("device_type", device_type),
            ("category", category),
            ("site_id", site_id),
        ]
        pairs = [(ALERT_FILTER_FIELDS[k], v) for k, v in raw_pairs if v is not None]

        query_params: dict = {"sort": sort}
        odata = build_odata_filter(pairs)
        if odata:
            query_params["filter"] = odata

        query_params["limit"] = limit
        if cursor is not None:
            query_params["next"] = cursor

        response = retry_central_command(
            ctx.lifespan_context["central_conn"],
            api_method="GET",
            api_path="network-notifications/v1/alerts",
            api_params=query_params,
        )
        msg = response["msg"]
        raw_items = msg.get("items", [])
        if not raw_items:
            return "No alerts found matching criteria"
        return PaginatedAlerts(
            items=clean_alert_data(raw_items),
            total=msg.get("total", 0),
            next_cursor=msg.get("next"),
        )
