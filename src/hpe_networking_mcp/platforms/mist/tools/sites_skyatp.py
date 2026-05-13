"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``hpe_networking_mcp.platforms.mist._generator``
from ``vendor/mist_openapi.json``. Regenerate via:

    uv run python -m hpe_networking_mcp.platforms.mist.regenerate

Tag: ``Sites Skyatp``
Operations in this file: 2
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
    name="mist_count_site_skyatp_events",
    description="GET /api/v1/sites/{site_id}/skyatp/events/count\n\ncountSiteSkyatpEvents\n\nCount by Distinct Attributes of Skyatp Events (WIP)",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_count_site_skyatp_events(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    distinct: Annotated[Any | None, Field(description="query parameter 'distinct'")] = None,
    type: Annotated[str | None, Field(description="Event type, e.g. cc, fs, mw")] = None,
    mac: Annotated[str | None, Field(description="Client MAC")] = None,
    device_mac: Annotated[str | None, Field(description="Device MAC")] = None,
    threat_level: Annotated[int | None, Field(description="Threat level")] = None,
    ip: Annotated[str | None, Field(description="query parameter 'ip'")] = None,
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
        "/api/v1/sites/{site_id}/skyatp/events/count",
        path_params={"site_id": site_id},
        query_params={
            "distinct": distinct,
            "type": type,
            "mac": mac,
            "device_mac": device_mac,
            "threat_level": threat_level,
            "ip": ip,
            "start": start,
            "end": end,
            "duration": duration,
            "limit": limit,
        },
        body=None,
    )


@_mcp_tool(
    name="mist_search_site_skyatp_events",
    description="GET /api/v1/sites/{site_id}/skyatp/events/search\n\nsearchSiteSkyatpEvents\n\nSearch Skyatp Events (WIP)",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_search_site_skyatp_events(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    type: Annotated[str | None, Field(description="Event type, e.g. cc, fs, mw")] = None,
    mac: Annotated[str | None, Field(description="Client MAC")] = None,
    device_mac: Annotated[str | None, Field(description="Device MAC")] = None,
    threat_level: Annotated[int | None, Field(description="Threat level")] = None,
    ip: Annotated[str | None, Field(description="query parameter 'ip'")] = None,
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
        "/api/v1/sites/{site_id}/skyatp/events/search",
        path_params={"site_id": site_id},
        query_params={
            "type": type,
            "mac": mac,
            "device_mac": device_mac,
            "threat_level": threat_level,
            "ip": ip,
            "limit": limit,
            "start": start,
            "end": end,
            "duration": duration,
            "sort": sort,
            "search_after": search_after,
        },
        body=None,
    )
