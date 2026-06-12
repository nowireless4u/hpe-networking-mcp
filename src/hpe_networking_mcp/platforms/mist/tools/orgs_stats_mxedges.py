"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``scripts/_mist_generator.py`` from
``vendor/mist/mist_openapi.json``. Regenerate via:

    uv run python scripts/regenerate_mist_tools.py

Tag: ``Orgs Stats - MxEdges``
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
    name="mist_get_org_mx_edge_stats",
    description="GET /api/v1/orgs/{org_id}/stats/mxedges/{mxedge_id}\n\ngetOrgMxEdgeStats\n\nGet Org MxEdge Details Stats",
    capability=Capability.READ,
)
async def mist_get_org_mx_edge_stats(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    mxedge_id: Annotated[str, Field(description="path parameter 'mxedge_id'")],
    for_site: Annotated[bool, Field(description="Filter results by whether the object is scoped to a site")] = False,
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/orgs/{org_id}/stats/mxedges/{mxedge_id}",
        path_params={"org_id": org_id, "mxedge_id": mxedge_id},
        query_params={"for_site": for_site},
        body=None,
    )


@_mcp_tool(
    name="mist_list_org_mx_edges_stats",
    description="GET /api/v1/orgs/{org_id}/stats/mxedges\n\nlistOrgMxEdgesStats\n\nGet List of Org MxEdge Stats",
    capability=Capability.READ,
)
async def mist_list_org_mx_edges_stats(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    for_site: Annotated[
        Any | None, Field(description="Filter for site level Mist Edges. enum: `any`, `true`, `false`")
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
    page: Annotated[
        int, Field(description="Select the page number to return when using page-based pagination; starts at `1`")
    ] = 1,
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/orgs/{org_id}/stats/mxedges",
        path_params={"org_id": org_id},
        query_params={
            "for_site": for_site,
            "start": start,
            "end": end,
            "duration": duration,
            "limit": limit,
            "page": page,
        },
        body=None,
    )
