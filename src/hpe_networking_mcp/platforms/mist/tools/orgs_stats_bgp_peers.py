"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``scripts/_mist_generator.py``
from ``vendor/mist_openapi.json``. Regenerate via:

    uv run python scripts/regenerate_mist_tools.py

Tag: ``Orgs Stats - BGP Peers``
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
    name="mist_count_org_bgp_stats",
    description="GET /api/v1/orgs/{org_id}/stats/bgp_peers/count\n\ncountOrgBgpStats\n\nCount by Distinct Attributes of Org BGP Stats",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_count_org_bgp_stats(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    state: Annotated[str | None, Field(description="query parameter 'state'")] = None,
    distinct: Annotated[str | None, Field(description="query parameter 'distinct'")] = None,
    limit: Annotated[int, Field(description="query parameter 'limit'")] = 100,
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
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_search_org_bgp_stats(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    mac: Annotated[str | None, Field(description="query parameter 'mac'")] = None,
    neighbor_mac: Annotated[str | None, Field(description="query parameter 'neighbor_mac'")] = None,
    site_id: Annotated[str | None, Field(description="query parameter 'site_id'")] = None,
    vrf_name: Annotated[str | None, Field(description="query parameter 'vrf_name'")] = None,
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
