"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``scripts/_mist_generator.py`` from
``vendor/mist/mist_openapi.json``. Regenerate via:

    uv run python scripts/regenerate_mist_tools.py

Tag: ``Sites Stats - Calls``
Operations in this file: 5
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
    name="mist_count_site_calls",
    description="GET /api/v1/sites/{site_id}/stats/calls/count\n\ncountSiteCalls\n\nCount by Distinct Attributes of Calls",
    capability=Capability.READ,
)
async def mist_count_site_calls(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    distinct: Annotated[Any | None, Field(description="Field used to group this count response. enum: `mac`")] = None,
    rating: Annotated[int | None, Field(description='Feedback rating (e.g. "rating=1" or "rating=1,2")')] = None,
    app: Annotated[str | None, Field(description="Filter application statistics by application name")] = None,
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
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/sites/{site_id}/stats/calls/count",
        path_params={"site_id": site_id},
        query_params={"distinct": distinct, "rating": rating, "app": app, "start": start, "end": end, "limit": limit},
        body=None,
    )


@_mcp_tool(
    name="mist_get_site_calls_summary",
    description="GET /api/v1/sites/{site_id}/stats/calls/summary\n\ngetSiteCallsSummary\n\nSummarized, aggregated stats for the site calls",
    capability=Capability.READ,
)
async def mist_get_site_calls_summary(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    ap_mac: Annotated[str | None, Field(description="Filter results by AP MAC address")] = None,
    app: Annotated[str | None, Field(description="Filter results by application name")] = None,
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
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/sites/{site_id}/stats/calls/summary",
        path_params={"site_id": site_id},
        query_params={"ap_mac": ap_mac, "app": app, "start": start, "end": end},
        body=None,
    )


@_mcp_tool(
    name="mist_list_site_troubleshoot_calls",
    description="GET /api/v1/sites/{site_id}/stats/calls/troubleshoot\n\nlistSiteTroubleshootCalls\n\nSummary of calls troubleshoot by site",
    capability=Capability.READ,
)
async def mist_list_site_troubleshoot_calls(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    ap: Annotated[str | None, Field(description="Filter results by AP MAC address")] = None,
    meeting_id: Annotated[str | None, Field(description="Filter results by meeting identifier")] = None,
    mac: Annotated[str | None, Field(description="Filter results by MAC address")] = None,
    app: Annotated[str | None, Field(description="Third party app name")] = None,
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
    limit: Annotated[int, Field(description="Maximum number of results to return per page")] = 100,
    page: Annotated[
        int, Field(description="Select the page number to return when using page-based pagination; starts at `1`")
    ] = 1,
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/sites/{site_id}/stats/calls/troubleshoot",
        path_params={"site_id": site_id},
        query_params={
            "ap": ap,
            "meeting_id": meeting_id,
            "mac": mac,
            "app": app,
            "start": start,
            "end": end,
            "duration": duration,
            "limit": limit,
            "page": page,
        },
        body=None,
    )


@_mcp_tool(
    name="mist_search_site_calls",
    description="GET /api/v1/sites/{site_id}/stats/calls/search\n\nsearchSiteCalls\n\nSearch Calls",
    capability=Capability.READ,
)
async def mist_search_site_calls(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    mac: Annotated[str | None, Field(description="Filter results by MAC address")] = None,
    app: Annotated[str | None, Field(description="Third party app name")] = None,
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
        "/api/v1/sites/{site_id}/stats/calls/search",
        path_params={"site_id": site_id},
        query_params={
            "mac": mac,
            "app": app,
            "limit": limit,
            "start": start,
            "end": end,
            "duration": duration,
            "sort": sort,
            "search_after": search_after,
        },
        body=None,
    )


@_mcp_tool(
    name="mist_troubleshoot_site_call",
    description="GET /api/v1/sites/{site_id}/stats/calls/client/{client_mac}/troubleshoot\n\ntroubleshootSiteCall\n\nTroubleshoot a call",
    capability=Capability.READ,
)
async def mist_troubleshoot_site_call(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    client_mac: Annotated[str, Field(description="path parameter 'client_mac'")],
    meeting_id: Annotated[str, Field(description="Filter results by meeting identifier")],
    mac: Annotated[str | None, Field(description="Filter results by MAC address")] = None,
    app: Annotated[str | None, Field(description="Third party app name")] = None,
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
    limit: Annotated[int, Field(description="Maximum number of results to return per page")] = 100,
    page: Annotated[
        int, Field(description="Select the page number to return when using page-based pagination; starts at `1`")
    ] = 1,
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/sites/{site_id}/stats/calls/client/{client_mac}/troubleshoot",
        path_params={"site_id": site_id, "client_mac": client_mac},
        query_params={
            "meeting_id": meeting_id,
            "mac": mac,
            "app": app,
            "start": start,
            "end": end,
            "duration": duration,
            "limit": limit,
            "page": page,
        },
        body=None,
    )
