"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``scripts/_mist_generator.py`` from
``vendor/mist/mist_openapi.json``. Regenerate via:

    uv run python scripts/regenerate_mist_tools.py

Tag: ``Orgs Stats - BGP Peers``
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
    name="mist_count_org_bgp_stats",
    description="GET /api/v1/orgs/{org_id}/stats/bgp_peers/count\n\ncountOrgBgpStats\n\nCount by Distinct Attributes of Org BGP Stats",
    capability=Capability.READ,
)
async def mist_count_org_bgp_stats(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    state: Annotated[str | None, Field(description="Filter peer results by state")] = None,
    distinct: Annotated[str | None, Field(description="Field used to group this count response")] = None,
    limit: Annotated[int, Field(description="Maximum number of results to return per page")] = 100,
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/orgs/{org_id}/stats/bgp_peers/count",
        path_params={"org_id": org_id},
        query_params={"state": state, "distinct": distinct, "limit": limit},
        body=None,
    )


@_mcp_tool(
    name="mist_search_org_bgp_stats",
    description="GET /api/v1/orgs/{org_id}/stats/bgp_peers/search\n\nsearchOrgBgpStats\n\nSearch Org BGP Stats",
    capability=Capability.READ,
)
async def mist_search_org_bgp_stats(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    mac: Annotated[
        str | None, Field(description="Filter results by MAC address. Accepts multiple comma-separated values.")
    ] = None,
    neighbor_mac: Annotated[str | None, Field(description="Filter peer results by neighbor MAC address")] = None,
    site_id: Annotated[str | None, Field(description="Filter results by site identifier")] = None,
    vrf_name: Annotated[
        str | None, Field(description="Filter peer results by VRF name. Accepts multiple comma-separated values.")
    ] = None,
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
        "/api/v1/orgs/{org_id}/stats/bgp_peers/search",
        path_params={"org_id": org_id},
        query_params={
            "mac": mac,
            "neighbor_mac": neighbor_mac,
            "site_id": site_id,
            "vrf_name": vrf_name,
            "limit": limit,
            "start": start,
            "end": end,
            "duration": duration,
            "sort": sort,
            "search_after": search_after,
        },
        body=None,
    )
