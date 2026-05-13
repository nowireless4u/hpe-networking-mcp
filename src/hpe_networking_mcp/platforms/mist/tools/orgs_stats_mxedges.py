"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``hpe_networking_mcp.platforms.mist._generator``
from ``vendor/mist_openapi.json``. Regenerate via:

    uv run python -m hpe_networking_mcp.platforms.mist.regenerate

Tag: ``Orgs Stats - MxEdges``
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
    name="mist_get_org_mx_edge_stats",
    description="GET /api/v1/orgs/{org_id}/stats/mxedges/{mxedge_id}\n\ngetOrgMxEdgeStats\n\nGet Org MxEdge Details Stats",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_get_org_mx_edge_stats(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    mxedge_id: Annotated[str, Field(description="path parameter 'mxedge_id'")],
    for_site: Annotated[bool, Field(description="query parameter 'for_site'")] = False,
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
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_list_org_mx_edges_stats(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    for_site: Annotated[Any | None, Field(description="Filter for site level mist edges")] = None,
    start: Annotated[
        str | None, Field(description='Start time (epoch timestamp in seconds, or relative string like "-1d", "-1w")')
    ] = None,
    end: Annotated[
        str | None,
        Field(description='End time (epoch timestamp in seconds, or relative string like "-1d", "-2h", "now")'),
    ] = None,
    duration: Annotated[str, Field(description="Duration like 7d, 2w")] = "1d",
    limit: Annotated[int, Field(description="query parameter 'limit'")] = 100,
    page: Annotated[int, Field(description="query parameter 'page'")] = 1,
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
