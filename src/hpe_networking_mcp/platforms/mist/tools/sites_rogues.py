"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``hpe_networking_mcp.platforms.mist._generator``
from ``vendor/mist_openapi.json``. Regenerate via:

    uv run python -m hpe_networking_mcp.platforms.mist.regenerate

Tag: ``Sites Rogues``
Operations in this file: 5
"""

# ruff: noqa: E501

from __future__ import annotations

from typing import Annotated, Any

from fastmcp import Context
from mcp.types import ToolAnnotations
from pydantic import Field

from hpe_networking_mcp.platforms.mist._client import mist_request
from hpe_networking_mcp.platforms.mist._registry import tool as _mcp_tool


@_mcp_tool(
    name="mist_count_site_rogue_events",
    description="GET /api/v1/sites/{site_id}/rogues/events/count\n\ncountSiteRogueEvents\n\nCount by Distinct Attributes of Rogue Events",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_count_site_rogue_events(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    distinct: Annotated[Any | None, Field(description="query parameter 'distinct'")] = None,
    type: Annotated[Any | None, Field(description="query parameter 'type'")] = None,
    ssid: Annotated[str | None, Field(description="SSID of the network detected as threat")] = None,
    bssid: Annotated[str | None, Field(description="BSSID of the network detected as threat")] = None,
    ap_mac: Annotated[
        str | None, Field(description="MAC of the device that had strongest signal strength for ssid/bssid pair")
    ] = None,
    channel: Annotated[str | None, Field(description="Channel over which ap_mac heard ssid/bssid pair")] = None,
    seen_on_lan: Annotated[
        bool | None, Field(description="Whether the reporting AP see a wireless client (on LAN) connecting to it")
    ] = None,
    start: Annotated[
        str | None, Field(description='Start time (epoch timestamp in seconds, or relative string like "-1d", "-1w")')
    ] = None,
    end: Annotated[
        str | None,
        Field(description='End time (epoch timestamp in seconds, or relative string like "-1d", "-2h", "now")'),
    ] = None,
    duration: Annotated[str, Field(description="Duration like 7d, 2w")] = "1d",
    limit: Annotated[int, Field(description="query parameter 'limit'")] = 100,
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/sites/{site_id}/rogues/events/count",
        path_params={"site_id": site_id},
        query_params={
            "distinct": distinct,
            "type": type,
            "ssid": ssid,
            "bssid": bssid,
            "ap_mac": ap_mac,
            "channel": channel,
            "seen_on_lan": seen_on_lan,
            "start": start,
            "end": end,
            "duration": duration,
            "limit": limit,
        },
        body=None,
    )


@_mcp_tool(
    name="mist_get_site_rogue_ap",
    description="GET /api/v1/sites/{site_id}/rogues/{rogue_bssid}\n\ngetSiteRogueAP\n\nGet Rogue AP Details",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_get_site_rogue_ap(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    rogue_bssid: Annotated[str, Field(description="path parameter 'rogue_bssid'")],
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/sites/{site_id}/rogues/{rogue_bssid}",
        path_params={"site_id": site_id, "rogue_bssid": rogue_bssid},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_list_site_rogue_a_ps",
    description="GET /api/v1/sites/{site_id}/insights/rogues\n\nlistSiteRogueAPs\n\nGet List of Site Rogue/Neighbor APs",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_list_site_rogue_a_ps(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    type: Annotated[Any | None, Field(description="query parameter 'type'")] = None,
    limit: Annotated[int, Field(description="query parameter 'limit'")] = 100,
    start: Annotated[
        str | None, Field(description='Start time (epoch timestamp in seconds, or relative string like "-1d", "-1w")')
    ] = None,
    end: Annotated[
        str | None,
        Field(description='End time (epoch timestamp in seconds, or relative string like "-1d", "-2h", "now")'),
    ] = None,
    duration: Annotated[str, Field(description="Duration like 7d, 2w")] = "1d",
    interval: Annotated[
        str | None,
        Field(
            description="Aggregation works by giving a time range plus interval (e.g. 1d, 1h, 10m) where aggregation function would be applied to."
        ),
    ] = None,
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/sites/{site_id}/insights/rogues",
        path_params={"site_id": site_id},
        query_params={
            "type": type,
            "limit": limit,
            "start": start,
            "end": end,
            "duration": duration,
            "interval": interval,
        },
        body=None,
    )


@_mcp_tool(
    name="mist_list_site_rogue_clients",
    description="GET /api/v1/sites/{site_id}/insights/rogues/clients\n\nlistSiteRogueClients\n\nGet List of Site Rogue Clients",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_list_site_rogue_clients(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    limit: Annotated[int, Field(description="query parameter 'limit'")] = 100,
    start: Annotated[
        str | None, Field(description='Start time (epoch timestamp in seconds, or relative string like "-1d", "-1w")')
    ] = None,
    end: Annotated[
        str | None,
        Field(description='End time (epoch timestamp in seconds, or relative string like "-1d", "-2h", "now")'),
    ] = None,
    duration: Annotated[str, Field(description="Duration like 7d, 2w")] = "1d",
    interval: Annotated[
        str | None,
        Field(
            description="Aggregation works by giving a time range plus interval (e.g. 1d, 1h, 10m) where aggregation function would be applied to."
        ),
    ] = None,
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/sites/{site_id}/insights/rogues/clients",
        path_params={"site_id": site_id},
        query_params={"limit": limit, "start": start, "end": end, "duration": duration, "interval": interval},
        body=None,
    )


@_mcp_tool(
    name="mist_search_site_rogue_events",
    description="GET /api/v1/sites/{site_id}/rogues/events/search\n\nsearchSiteRogueEvents\n\nSearch Rogue Events",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_search_site_rogue_events(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    type: Annotated[Any | None, Field(description="query parameter 'type'")] = None,
    ssid: Annotated[str | None, Field(description="SSID of the network detected as threat")] = None,
    bssid: Annotated[str | None, Field(description="BSSID of the network detected as threat")] = None,
    ap_mac: Annotated[
        str | None, Field(description="MAC of the device that had strongest signal strength for ssid/bssid pair")
    ] = None,
    channel: Annotated[int | None, Field(description="Channel over which ap_mac heard ssid/bssid pair")] = None,
    seen_on_lan: Annotated[
        bool | None, Field(description="Whether the reporting AP see a wireless client (on LAN) connecting to it")
    ] = None,
    limit: Annotated[int, Field(description="query parameter 'limit'")] = 100,
    start: Annotated[
        str | None, Field(description='Start time (epoch timestamp in seconds, or relative string like "-1d", "-1w")')
    ] = None,
    end: Annotated[
        str | None,
        Field(description='End time (epoch timestamp in seconds, or relative string like "-1d", "-2h", "now")'),
    ] = None,
    duration: Annotated[str, Field(description="Duration like 7d, 2w")] = "1d",
    sort: Annotated[
        str, Field(description="On which field the list should be sorted, -prefix represents DESC order")
    ] = "timestamp",
    search_after: Annotated[
        str | None,
        Field(
            description="Pagination cursor for retrieving subsequent pages of results. This value is automatically populated by Mist in the `next` URL from the previous response and should not be manually constructed."
        ),
    ] = None,
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/sites/{site_id}/rogues/events/search",
        path_params={"site_id": site_id},
        query_params={
            "type": type,
            "ssid": ssid,
            "bssid": bssid,
            "ap_mac": ap_mac,
            "channel": channel,
            "seen_on_lan": seen_on_lan,
            "limit": limit,
            "start": start,
            "end": end,
            "duration": duration,
            "sort": sort,
            "search_after": search_after,
        },
        body=None,
    )
