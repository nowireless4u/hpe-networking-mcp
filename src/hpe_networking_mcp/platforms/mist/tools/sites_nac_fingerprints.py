"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``scripts/_mist_generator.py`` from
``vendor/mist/mist_openapi.json``. Regenerate via:

    uv run python scripts/regenerate_mist_tools.py

Tag: ``Sites NAC Fingerprints``
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
    name="mist_count_site_client_fingerprints",
    description="GET /api/v1/sites/{site_id}/insights/fingerprints/count\n\ncountSiteClientFingerprints\n\nCount Client Fingerprints",
    capability=Capability.READ,
)
async def mist_count_site_client_fingerprints(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    distinct: Annotated[
        Any | None,
        Field(description="Field used to group this count response. enum: `family`, `model`, `os`, `os_type`"),
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
    duration: Annotated[
        str, Field(description="Time range duration for the query, using relative units such as `10m`, `7d`, or `2w`")
    ] = "1d",
    limit: Annotated[int, Field(description="Maximum number of results to return per page")] = 100,
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/sites/{site_id}/insights/fingerprints/count",
        path_params={"site_id": site_id},
        query_params={"distinct": distinct, "start": start, "end": end, "duration": duration, "limit": limit},
        body=None,
    )


@_mcp_tool(
    name="mist_search_site_client_fingerprints",
    description="GET /api/v1/sites/{site_id}/insights/fingerprints/search\n\nsearchSiteClientFingerprints\n\nSearch Client Fingerprints",
    capability=Capability.READ,
)
async def mist_search_site_client_fingerprints(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    family: Annotated[str | None, Field(description="Device Category of the client device")] = None,
    client_type: Annotated[
        Any | None, Field(description="Filter results by client type. enum: `wireless`, `wired`, `vty`")
    ] = None,
    model: Annotated[str | None, Field(description="Filter results by device model")] = None,
    mfg: Annotated[str | None, Field(description="Manufacturer name of the client device")] = None,
    os: Annotated[str | None, Field(description="Operating System name and version of the client device")] = None,
    os_type: Annotated[str | None, Field(description="Operating system name of the client device")] = None,
    mac: Annotated[str | None, Field(description="Filter results by MAC address")] = None,
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
    interval: Annotated[
        str | None,
        Field(
            description="Aggregation works by giving a time range plus interval (e.g. 1d, 1h, 10m) where aggregation function would be applied to."
        ),
    ] = None,
    sort: Annotated[
        str, Field(description="On which field the list should be sorted, -prefix represents DESC order.")
    ] = "wxid",
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
        "/api/v1/sites/{site_id}/insights/fingerprints/search",
        path_params={"site_id": site_id},
        query_params={
            "family": family,
            "client_type": client_type,
            "model": model,
            "mfg": mfg,
            "os": os,
            "os_type": os_type,
            "mac": mac,
            "limit": limit,
            "start": start,
            "end": end,
            "duration": duration,
            "interval": interval,
            "sort": sort,
            "search_after": search_after,
        },
        body=None,
    )
