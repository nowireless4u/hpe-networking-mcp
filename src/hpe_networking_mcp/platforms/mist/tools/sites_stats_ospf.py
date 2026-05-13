"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``hpe_networking_mcp.platforms.mist._generator``
from ``vendor/mist_openapi.json``. Regenerate via:

    uv run python -m hpe_networking_mcp.platforms.mist.regenerate

Tag: ``Sites Stats - Ospf``
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
    name="mist_count_site_ospf_stats",
    description="GET /api/v1/sites/{site_id}/stats/ospf_peers/count\n\ncountOrgOspfStats\n\nCount by Distinct Attributes of OSPF peers stats",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_count_site_ospf_stats(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    distinct: Annotated[Any | None, Field(description="query parameter 'distinct'")] = None,
    start: Annotated[
        str | None, Field(description='Start time (epoch timestamp in seconds, or relative string like "-1d", "-1w")')
    ] = None,
    end: Annotated[
        str | None,
        Field(description='End time (epoch timestamp in seconds, or relative string like "-1d", "-2h", "now")'),
    ] = None,
    limit: Annotated[int, Field(description="query parameter 'limit'")] = 100,
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
        "/api/v1/sites/{site_id}/stats/ospf_peers/count",
        path_params={"site_id": site_id},
        query_params={
            "distinct": distinct,
            "start": start,
            "end": end,
            "limit": limit,
            "sort": sort,
            "search_after": search_after,
        },
        body=None,
    )


@_mcp_tool(
    name="mist_search_site_ospf_stats",
    description="GET /api/v1/sites/{site_id}/stats/ospf_peers/search\n\nsearchSiteOspfStats\n\nSearch OSPF Neighbor Stats",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_search_site_ospf_stats(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    mac: Annotated[str | None, Field(description="query parameter 'mac'")] = None,
    vrf_name: Annotated[str | None, Field(description="query parameter 'vrf_name'")] = None,
    peer_ip: Annotated[str | None, Field(description="query parameter 'peer_ip'")] = None,
    start: Annotated[
        str | None, Field(description='Start time (epoch timestamp in seconds, or relative string like "-1d", "-1w")')
    ] = None,
    end: Annotated[
        str | None,
        Field(description='End time (epoch timestamp in seconds, or relative string like "-1d", "-2h", "now")'),
    ] = None,
    limit: Annotated[int, Field(description="query parameter 'limit'")] = 100,
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
        "/api/v1/sites/{site_id}/stats/ospf_peers/search",
        path_params={"site_id": site_id},
        query_params={
            "mac": mac,
            "vrf_name": vrf_name,
            "peer_ip": peer_ip,
            "start": start,
            "end": end,
            "limit": limit,
            "sort": sort,
            "search_after": search_after,
        },
        body=None,
    )
