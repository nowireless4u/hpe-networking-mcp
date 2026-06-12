"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``scripts/_mist_generator.py`` from
``vendor/mist/mist_openapi.json``. Regenerate via:

    uv run python scripts/regenerate_mist_tools.py

Tag: ``Sites Skyatp``
Operations in this file: 2
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
    name="mist_count_site_skyatp_events",
    description="GET /api/v1/sites/{site_id}/skyatp/events/count\n\ncountSiteSkyatpEvents\n\nCount by Distinct Attributes of Skyatp Events (WIP)",
    capability=Capability.READ,
)
async def mist_count_site_skyatp_events(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    distinct: Annotated[
        Any | None,
        Field(description="Field used to group this count response. enum: `device_mac`, `mac`, `threat_level`, `type`"),
    ] = None,
    type: Annotated[str | None, Field(description="Event type, e.g. cc, fs, mw")] = None,
    mac: Annotated[str | None, Field(description="Filter results by MAC address")] = None,
    device_mac: Annotated[str | None, Field(description="Filter results by device MAC address")] = None,
    threat_level: Annotated[int | None, Field(description="Filter results by threat level")] = None,
    ip: Annotated[str | None, Field(description="Filter results by IPv4 address")] = None,
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
    capability=Capability.READ,
)
async def mist_search_site_skyatp_events(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    type: Annotated[str | None, Field(description="Event type, e.g. cc, fs, mw")] = None,
    mac: Annotated[str | None, Field(description="Filter results by MAC address")] = None,
    device_mac: Annotated[str | None, Field(description="Filter results by device MAC address")] = None,
    threat_level: Annotated[int | None, Field(description="Filter results by threat level")] = None,
    ip: Annotated[str | None, Field(description="Filter results by IPv4 address")] = None,
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
