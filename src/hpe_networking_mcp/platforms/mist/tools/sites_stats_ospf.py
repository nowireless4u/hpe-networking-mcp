"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``scripts/_mist_generator.py`` from
``vendor/mist/mist_openapi.json``. Regenerate via:

    uv run python scripts/regenerate_mist_tools.py

Tag: ``Sites Stats - Ospf``
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
    name="mist_count_site_ospf_stats",
    description="GET /api/v1/sites/{site_id}/stats/ospf_peers/count\n\ncountOrgOspfStats\n\nCount OSPF peer statistics for a site, optionally grouped by the `distinct` field and filtered by time range. Use [Count Org OSPF Stats](/#operations/countOrgOspfStats) to count OSPF peer statistics across the organization.",
    capability=Capability.READ,
)
async def mist_count_site_ospf_stats(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    distinct: Annotated[
        Any | None,
        Field(
            description="Field used to group this count response. enum: `site_id`, `org_id`, `mac`, `peer_ip`, `port_id`, `state`, `vrf_name`"
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
    description="GET /api/v1/sites/{site_id}/stats/ospf_peers/search\n\nsearchSiteOspfStats\n\nSearch OSPF peer statistics for a site with filters for device, VRF, peer IP, and time range. Use [Search Org OSPF Stats](/#operations/searchOrgOspfStats) to search OSPF peer statistics across the organization.",
    capability=Capability.READ,
)
async def mist_search_site_ospf_stats(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    mac: Annotated[str | None, Field(description="Filter results by MAC address")] = None,
    vrf_name: Annotated[str | None, Field(description="Filter peer results by VRF name")] = None,
    peer_ip: Annotated[str | None, Field(description="Filter peer results by peer IP address")] = None,
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
