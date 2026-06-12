"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``scripts/_mist_generator.py`` from
``vendor/mist/mist_openapi.json``. Regenerate via:

    uv run python scripts/regenerate_mist_tools.py

Tag: ``Sites MxEdges``
Operations in this file: 7
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
    name="mist_count_site_mx_edge_events",
    description="GET /api/v1/sites/{site_id}/mxedges/events/count\n\ncountSiteMxEdgeEvents\n\nCount by Distinct Attributes of Mist Edge Events",
    capability=Capability.READ,
)
async def mist_count_site_mx_edge_events(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    distinct: Annotated[
        Any | None,
        Field(
            description="Field used to group this count response. enum: `mxcluster_id`, `mxedge_id`, `package`, `type`"
        ),
    ] = None,
    mxedge_id: Annotated[str | None, Field(description="Filter results by Mist Edge identifier")] = None,
    mxcluster_id: Annotated[str | None, Field(description="Mist edge cluster id")] = None,
    type: Annotated[
        str | None, Field(description="See [List Device Events Definitions](/#operations/listDeviceEventsDefinitions)")
    ] = None,
    service: Annotated[str | None, Field(description="Filter results by service name")] = None,
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
        "/api/v1/sites/{site_id}/mxedges/events/count",
        path_params={"site_id": site_id},
        query_params={
            "distinct": distinct,
            "mxedge_id": mxedge_id,
            "mxcluster_id": mxcluster_id,
            "type": type,
            "service": service,
            "start": start,
            "end": end,
            "duration": duration,
            "limit": limit,
        },
        body=None,
    )


@_mcp_tool(
    name="mist_delete_site_mx_edge",
    description="DELETE /api/v1/sites/{site_id}/mxedges/{mxedge_id}\n\ndeleteSiteMxEdge\n\nDelete Site Mist Edge",
    capability=Capability.WRITE_DELETE,
)
async def mist_delete_site_mx_edge(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    mxedge_id: Annotated[str, Field(description="path parameter 'mxedge_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "DELETE",
        "/api/v1/sites/{site_id}/mxedges/{mxedge_id}",
        path_params={"site_id": site_id, "mxedge_id": mxedge_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_get_site_mx_edge",
    description="GET /api/v1/sites/{site_id}/mxedges/{mxedge_id}\n\ngetSiteMxEdge\n\nGet Site Mist Edge",
    capability=Capability.READ,
)
async def mist_get_site_mx_edge(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    mxedge_id: Annotated[str, Field(description="path parameter 'mxedge_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/sites/{site_id}/mxedges/{mxedge_id}",
        path_params={"site_id": site_id, "mxedge_id": mxedge_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_list_site_mx_edges",
    description="GET /api/v1/sites/{site_id}/mxedges\n\nlistSiteMxEdges\n\nList Mist Edges for a site. Use [List Org Mist Edges](/#operations/listOrgMxEdges) to retrieve Mist Edges across the organization.",
    capability=Capability.READ,
)
async def mist_list_site_mx_edges(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    limit: Annotated[int, Field(description="Maximum number of results to return per page")] = 100,
    page: Annotated[
        int, Field(description="Select the page number to return when using page-based pagination; starts at `1`")
    ] = 1,
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/sites/{site_id}/mxedges",
        path_params={"site_id": site_id},
        query_params={"limit": limit, "page": page},
        body=None,
    )


@_mcp_tool(
    name="mist_search_site_mist_edge_events",
    description="GET /api/v1/sites/{site_id}/mxedges/events/search\n\nsearchSiteMistEdgeEvents\n\nSearch Mist Edge events for a site with filters for Mist Edge, Mist Edge cluster, event type, service, component, and time range. Use [Search Org Mist Edge Events](/#operations/searchOrgMistEdgeEvents) to search Mist Edge events across the organization.",
    capability=Capability.READ,
)
async def mist_search_site_mist_edge_events(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    mxedge_id: Annotated[str | None, Field(description="Filter results by Mist Edge identifier")] = None,
    mxcluster_id: Annotated[str | None, Field(description="Mist edge cluster id")] = None,
    type: Annotated[
        str | None, Field(description="See [List Device Events Definitions](/#operations/listDeviceEventsDefinitions)")
    ] = None,
    service: Annotated[str | None, Field(description="Filter results by service name")] = None,
    component: Annotated[str | None, Field(description="Filter results by component name")] = None,
    limit: Annotated[int, Field(description="Maximum number of results to return per page")] = 10,
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
        "/api/v1/sites/{site_id}/mxedges/events/search",
        path_params={"site_id": site_id},
        query_params={
            "mxedge_id": mxedge_id,
            "mxcluster_id": mxcluster_id,
            "type": type,
            "service": service,
            "component": component,
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
    name="mist_update_site_mx_edge",
    description="PUT /api/v1/sites/{site_id}/mxedges/{mxedge_id}\n\nupdateSiteMxEdge\n\nUpdate Site Mist Edge settings",
    capability=Capability.WRITE,
)
async def mist_update_site_mx_edge(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    mxedge_id: Annotated[str, Field(description="path parameter 'mxedge_id'")],
    body: Annotated[
        dict[str, Any] | None,
        Field(default=None, description="Request body for PUT /api/v1/sites/{site_id}/mxedges/{mxedge_id}"),
    ] = None,
) -> Any:
    return await mist_request(
        ctx,
        "PUT",
        "/api/v1/sites/{site_id}/mxedges/{mxedge_id}",
        path_params={"site_id": site_id, "mxedge_id": mxedge_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_upload_site_mx_edge_support_files",
    description="POST /api/v1/sites/{site_id}/mxedges/{mxedge_id}/support\n\nuploadSiteMxEdgeSupportFiles\n\nSupport / Upload Mist Edge support files",
    capability=Capability.WRITE,
)
async def mist_upload_site_mx_edge_support_files(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    mxedge_id: Annotated[str, Field(description="path parameter 'mxedge_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/sites/{site_id}/mxedges/{mxedge_id}/support",
        path_params={"site_id": site_id, "mxedge_id": mxedge_id},
        query_params=None,
        body=None,
    )
