"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``scripts/_mist_generator.py`` from
``vendor/mist/mist_openapi.json``. Regenerate via:

    uv run python scripts/regenerate_mist_tools.py

Tag: ``Orgs Clients - Marvis``
Operations in this file: 4
"""

# ruff: noqa: E501

from __future__ import annotations

from typing import Annotated, Any

from fastmcp import Context
from pydantic import Field

from hpe_networking_mcp.platforms._common.annotations import Capability
from hpe_networking_mcp.platforms.mist._client import mist_request
from hpe_networking_mcp.platforms.mist._registry import tool as _mcp_tool


@_mcp_tool(
    name="mist_count_org_marvis_client_events",
    description="GET /api/v1/orgs/{org_id}/marvisclients/events/count\n\ncountOrgMarvisClientEvents\n\nCount Marvis Client events by a distinct field.",
    capability=Capability.READ,
)
async def mist_count_org_marvis_client_events(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    distinct: Annotated[
        str,
        Field(
            description="Field to count by. enum: `type`, `device_id`, `wifi_mac`, `wifi_ip`, `hostname`, `ssid`, `bssid`, `channel`, `pre_bssid`, `pre_channel`"
        ),
    ] = "type",
    type: Annotated[str | None, Field(description="Filter by event type")] = None,
    device_id: Annotated[str | None, Field(description="Filter by Marvis Client installation device UUID")] = None,
    wifi_mac: Annotated[str | None, Field(description="Filter by device Wi-Fi MAC address")] = None,
    wifi_ip: Annotated[str | None, Field(description="Filter by device Wi-Fi IP address")] = None,
    hostname: Annotated[str | None, Field(description="Filter by device hostname")] = None,
    ssid: Annotated[str | None, Field(description="Filter by SSID involved in roam events")] = None,
    bssid: Annotated[str | None, Field(description="Filter by BSSID the client roamed to")] = None,
    channel: Annotated[str | None, Field(description="Filter by channel the client roamed to")] = None,
    pre_bssid: Annotated[str | None, Field(description="Filter by BSSID the client roamed from")] = None,
    pre_channel: Annotated[str | None, Field(description="Filter by channel the client roamed from")] = None,
    limit: Annotated[int, Field(description="Maximum number of results to return per page")] = 100,
    start: Annotated[
        str | None,
        Field(
            description="Lower bound of the time range, as an epoch timestamp in seconds or a relative value such as `-1d` or `-1w`"
        ),
    ] = None,
    end: Annotated[
        str | None,
        Field(
            description="Upper bound of the time range, as an epoch timestamp in seconds or a relative value such as `-1d`, `-2h`, or `now`"
        ),
    ] = None,
    duration: Annotated[
        str, Field(description="Time range duration for the query, using relative units such as `10m`, `7d`, or `2w`")
    ] = "1d",
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/orgs/{org_id}/marvisclients/events/count",
        path_params={"org_id": org_id},
        query_params={
            "distinct": distinct,
            "type": type,
            "device_id": device_id,
            "wifi_mac": wifi_mac,
            "wifi_ip": wifi_ip,
            "hostname": hostname,
            "ssid": ssid,
            "bssid": bssid,
            "channel": channel,
            "pre_bssid": pre_bssid,
            "pre_channel": pre_channel,
            "limit": limit,
            "start": start,
            "end": end,
            "duration": duration,
        },
        body=None,
    )


@_mcp_tool(
    name="mist_delete_org_marvis_client",
    description="DELETE /api/v1/orgs/{org_id}/stats/marvisclients\n\ndeleteOrgMarvisClient\n\nDelete Marvis Client",
    capability=Capability.WRITE_DELETE,
)
async def mist_delete_org_marvis_client(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "DELETE",
        "/api/v1/orgs/{org_id}/stats/marvisclients",
        path_params={"org_id": org_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_get_org_marvis_client_insights",
    description="GET /api/v1/orgs/{org_id}/insights/marvisclient/{marvisclient_id}/marvisclient-metrics\n\ngetOrgMarvisClientInsights\n\nReturn time-series metrics for a specific Marvis Client device. For the full list of supported metric field names and example values, refer to [List Insight Metrics](/#operations/listInsightMetrics) under `/api/v1/const/insight_metrics`.",
    capability=Capability.READ,
)
async def mist_get_org_marvis_client_insights(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    marvisclient_id: Annotated[str, Field(description="Marvis Client device UUID")],
    duration: Annotated[
        str, Field(description="Time range duration for the query, using relative units such as `10m`, `7d`, or `2w`")
    ] = "1d",
    interval: Annotated[
        str | None,
        Field(
            description="Aggregation works by giving a time range plus interval (e.g. 1d, 1h, 10m) where aggregation function would be applied to."
        ),
    ] = None,
    start: Annotated[
        str | None,
        Field(
            description="Lower bound of the time range, as an epoch timestamp in seconds or a relative value such as `-1d` or `-1w`"
        ),
    ] = None,
    end: Annotated[
        str | None,
        Field(
            description="Upper bound of the time range, as an epoch timestamp in seconds or a relative value such as `-1d`, `-2h`, or `now`"
        ),
    ] = None,
    limit: Annotated[int, Field(description="Maximum number of results to return per page")] = 100,
    page: Annotated[
        int, Field(description="Select the page number to return when using page-based pagination; starts at `1`")
    ] = 1,
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/orgs/{org_id}/insights/marvisclient/{marvisclient_id}/marvisclient-metrics",
        path_params={"org_id": org_id, "marvisclient_id": marvisclient_id},
        query_params={
            "duration": duration,
            "interval": interval,
            "start": start,
            "end": end,
            "limit": limit,
            "page": page,
        },
        body=None,
    )


@_mcp_tool(
    name="mist_search_org_marvis_client_events",
    description="GET /api/v1/orgs/{org_id}/marvisclients/events/search\n\nsearchOrgMarvisClientEvents\n\nSearch Marvis Client events across the organization.",
    capability=Capability.READ,
)
async def mist_search_org_marvis_client_events(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    type: Annotated[str | None, Field(description="Filter by event type")] = None,
    device_id: Annotated[str | None, Field(description="Filter by Marvis Client installation device UUID")] = None,
    wifi_mac: Annotated[str | None, Field(description="Filter by device Wi-Fi MAC address")] = None,
    wifi_ip: Annotated[str | None, Field(description="Filter by device Wi-Fi IP address")] = None,
    hostname: Annotated[str | None, Field(description="Filter by device hostname")] = None,
    ssid: Annotated[str | None, Field(description="Filter by SSID involved in roam events")] = None,
    bssid: Annotated[str | None, Field(description="Filter by BSSID the client roamed to")] = None,
    channel: Annotated[str | None, Field(description="Filter by channel the client roamed to")] = None,
    pre_bssid: Annotated[str | None, Field(description="Filter by BSSID the client roamed from")] = None,
    pre_channel: Annotated[str | None, Field(description="Filter by channel the client roamed from")] = None,
    limit: Annotated[int, Field(description="Maximum number of results to return per page")] = 100,
    start: Annotated[
        str | None,
        Field(
            description="Lower bound of the time range, as an epoch timestamp in seconds or a relative value such as `-1d` or `-1w`"
        ),
    ] = None,
    end: Annotated[
        str | None,
        Field(
            description="Upper bound of the time range, as an epoch timestamp in seconds or a relative value such as `-1d`, `-2h`, or `now`"
        ),
    ] = None,
    duration: Annotated[
        str, Field(description="Time range duration for the query, using relative units such as `10m`, `7d`, or `2w`")
    ] = "1d",
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/orgs/{org_id}/marvisclients/events/search",
        path_params={"org_id": org_id},
        query_params={
            "type": type,
            "device_id": device_id,
            "wifi_mac": wifi_mac,
            "wifi_ip": wifi_ip,
            "hostname": hostname,
            "ssid": ssid,
            "bssid": bssid,
            "channel": channel,
            "pre_bssid": pre_bssid,
            "pre_channel": pre_channel,
            "limit": limit,
            "start": start,
            "end": end,
            "duration": duration,
        },
        body=None,
    )
