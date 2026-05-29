"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``scripts/_mist_generator.py`` from
``vendor/mist_openapi.json``. Regenerate via:

    uv run python scripts/regenerate_mist_tools.py

Tag: ``Orgs MxEdges``
Operations in this file: 22
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
    name="mist_add_org_mx_edge_image",
    description="POST /api/v1/orgs/{org_id}/mxedges/{mxedge_id}/image/{image_number}\n\naddOrgMxEdgeImage\n\nAttach up to 3 images to a mxedge",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_add_org_mx_edge_image(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    mxedge_id: Annotated[str, Field(description="path parameter 'mxedge_id'")],
    image_number: Annotated[int, Field(description="path parameter 'image_number'")],
    body: Annotated[
        dict[str, Any] | None,
        Field(
            default=None,
            description="Request body for POST /api/v1/orgs/{org_id}/mxedges/{mxedge_id}/image/{image_number}",
        ),
    ] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/orgs/{org_id}/mxedges/{mxedge_id}/image/{image_number}",
        path_params={"org_id": org_id, "mxedge_id": mxedge_id, "image_number": image_number},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_assign_org_mx_edge_to_site",
    description="POST /api/v1/orgs/{org_id}/mxedges/assign\n\nassignOrgMxEdgeToSite\n\nAssign Org MxEdge to Site",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_assign_org_mx_edge_to_site(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request Body")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/orgs/{org_id}/mxedges/assign",
        path_params={"org_id": org_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_bounce_org_mx_edge_data_ports",
    description="POST /api/v1/orgs/{org_id}/mxedges/{mxedge_id}/services/tunterm/bounce_port\n\nbounceOrgMxEdgeDataPorts\n\nBounce TunTerm Data Ports",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_bounce_org_mx_edge_data_ports(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    mxedge_id: Annotated[str, Field(description="path parameter 'mxedge_id'")],
    body: Annotated[
        dict[str, Any] | None,
        Field(
            default=None,
            description="Request body for POST /api/v1/orgs/{org_id}/mxedges/{mxedge_id}/services/tunterm/bounce_port",
        ),
    ] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/orgs/{org_id}/mxedges/{mxedge_id}/services/tunterm/bounce_port",
        path_params={"org_id": org_id, "mxedge_id": mxedge_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_claim_org_mx_edge",
    description='POST /api/v1/orgs/{org_id}/mxedges/claim\n\nclaimOrgMxEdge\n\nFor a Mist Edge in default state, it will show a random claim code like `135-546-673` which you can "claim" it into your Org',
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_claim_org_mx_edge(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request Body")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/orgs/{org_id}/mxedges/claim",
        path_params={"org_id": org_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_control_org_mx_edge_services",
    description="POST /api/v1/orgs/{org_id}/mxedges/{mxedge_id}/services/{name}/{action}\n\ncontrolOrgMxEdgeServices\n\nControl Services on a Mist Edge",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_control_org_mx_edge_services(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    mxedge_id: Annotated[str, Field(description="path parameter 'mxedge_id'")],
    name: Annotated[
        Any, Field(description="enum: `mxagent`, `mxdas`, `mxnacedge`, `mxocproxy`, `radsecproxy`, `tunterm`")
    ],
    action: Annotated[Any, Field(description="Restart or start or stop")],
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/orgs/{org_id}/mxedges/{mxedge_id}/services/{name}/{action}",
        path_params={"org_id": org_id, "mxedge_id": mxedge_id, "name": name, "action": action},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_count_org_mx_edges",
    description="GET /api/v1/orgs/{org_id}/mxedges/count\n\ncountOrgMxEdges\n\nCount by Distinct Attributes of Org Mist Edges",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_count_org_mx_edges(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    distinct: Annotated[Any | None, Field(description="query parameter 'distinct'")] = None,
    mxedge_id: Annotated[str | None, Field(description="Mist edge id")] = None,
    site_id: Annotated[str | None, Field(description="Mist edge site id")] = None,
    mxcluster_id: Annotated[str | None, Field(description="Mist edge cluster id")] = None,
    model: Annotated[str | None, Field(description="Model name")] = None,
    distro: Annotated[str | None, Field(description="Debian code name (buster, bullseye)")] = None,
    tunterm_version: Annotated[str | None, Field(description="tunterm version")] = None,
    sort: Annotated[
        str | None, Field(description="Sort options, -prefix represents DESC order, default is -last_seen")
    ] = None,
    stats: Annotated[bool | None, Field(description="Whether to return device stats, default is false")] = None,
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
        "/api/v1/orgs/{org_id}/mxedges/count",
        path_params={"org_id": org_id},
        query_params={
            "distinct": distinct,
            "mxedge_id": mxedge_id,
            "site_id": site_id,
            "mxcluster_id": mxcluster_id,
            "model": model,
            "distro": distro,
            "tunterm_version": tunterm_version,
            "sort": sort,
            "stats": stats,
            "start": start,
            "end": end,
            "duration": duration,
            "limit": limit,
        },
        body=None,
    )


@_mcp_tool(
    name="mist_count_org_site_mx_edge_events",
    description="GET /api/v1/orgs/{org_id}/mxedges/events/count\n\ncountOrgSiteMxEdgeEvents\n\nCount by Distinct Attributes of Org Mist Edge Events",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_count_org_site_mx_edge_events(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    distinct: Annotated[Any | None, Field(description="query parameter 'distinct'")] = None,
    mxedge_id: Annotated[str | None, Field(description="Mist edge id")] = None,
    mxcluster_id: Annotated[str | None, Field(description="Mist edge cluster id")] = None,
    type: Annotated[
        str | None, Field(description="See [List Device Events Definitions](/#operations/listDeviceEventsDefinitions)")
    ] = None,
    service: Annotated[str | None, Field(description="Service running on mist edge(mxagent, tunterm etc)")] = None,
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
        "/api/v1/orgs/{org_id}/mxedges/events/count",
        path_params={"org_id": org_id},
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
    name="mist_create_org_mx_edge",
    description="POST /api/v1/orgs/{org_id}/mxedges\n\ncreateOrgMxEdge\n\nCreate MxEdge",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_create_org_mx_edge(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request Body")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/orgs/{org_id}/mxedges",
        path_params={"org_id": org_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_delete_org_mx_edge",
    description="DELETE /api/v1/orgs/{org_id}/mxedges/{mxedge_id}\n\ndeleteOrgMxEdge\n\nDelete Org MxEdge",
    tags={"mist", "mist_write", "mist_write_delete"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=True),
)
async def mist_delete_org_mx_edge(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    mxedge_id: Annotated[str, Field(description="path parameter 'mxedge_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "DELETE",
        "/api/v1/orgs/{org_id}/mxedges/{mxedge_id}",
        path_params={"org_id": org_id, "mxedge_id": mxedge_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_delete_org_mx_edge_image",
    description="DELETE /api/v1/orgs/{org_id}/mxedges/{mxedge_id}/image/{image_number}\n\ndeleteOrgMxEdgeImage\n\nRemove MxEdge Image",
    tags={"mist", "mist_write", "mist_write_delete"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=True),
)
async def mist_delete_org_mx_edge_image(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    mxedge_id: Annotated[str, Field(description="path parameter 'mxedge_id'")],
    image_number: Annotated[int, Field(description="path parameter 'image_number'")],
) -> Any:
    return await mist_request(
        ctx,
        "DELETE",
        "/api/v1/orgs/{org_id}/mxedges/{mxedge_id}/image/{image_number}",
        path_params={"org_id": org_id, "mxedge_id": mxedge_id, "image_number": image_number},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_disconnect_org_mx_edge_tunterm_aps",
    description="POST /api/v1/orgs/{org_id}/mxedges/{mxedge_id}/services/tunterm/disconnect_aps\n\ndisconnectOrgMxEdgeTuntermAps\n\nDisconnect AP’s from TunTerm",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_disconnect_org_mx_edge_tunterm_aps(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    mxedge_id: Annotated[str, Field(description="path parameter 'mxedge_id'")],
    body: Annotated[
        dict[str, Any] | None,
        Field(
            default=None,
            description="Request body for POST /api/v1/orgs/{org_id}/mxedges/{mxedge_id}/services/tunterm/disconnect_aps",
        ),
    ] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/orgs/{org_id}/mxedges/{mxedge_id}/services/tunterm/disconnect_aps",
        path_params={"org_id": org_id, "mxedge_id": mxedge_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_get_org_mx_edge",
    description="GET /api/v1/orgs/{org_id}/mxedges/{mxedge_id}\n\ngetOrgMxEdge\n\nGet Org MxEdge details",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_get_org_mx_edge(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    mxedge_id: Annotated[str, Field(description="path parameter 'mxedge_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/orgs/{org_id}/mxedges/{mxedge_id}",
        path_params={"org_id": org_id, "mxedge_id": mxedge_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_get_org_mx_edge_upgrade_info",
    description="GET /api/v1/orgs/{org_id}/mxedges/versions\n\ngetOrgMxEdgeUpgradeInfo\n\nGet Mist Edge Upgrade Information",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_get_org_mx_edge_upgrade_info(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    channel: Annotated[
        Any | None, Field(description="Upgrade channel to follow, stable (default) / beta / alpha")
    ] = None,
    distro: Annotated[str | None, Field(description="Distro code name (e.g. `buster`, `bullseye`, ...)")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/orgs/{org_id}/mxedges/versions",
        path_params={"org_id": org_id},
        query_params={"channel": channel, "distro": distro},
        body=None,
    )


@_mcp_tool(
    name="mist_get_org_mx_edge_vm_params",
    description="GET /api/v1/orgs/{org_id}/mxedges/{mxedge_id}/vm_params\n\ngetOrgMxEdgeVmParams\n\nGet Mist Edge VM parameters",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_get_org_mx_edge_vm_params(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    mxedge_id: Annotated[str, Field(description="path parameter 'mxedge_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/orgs/{org_id}/mxedges/{mxedge_id}/vm_params",
        path_params={"org_id": org_id, "mxedge_id": mxedge_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_list_org_mx_edges",
    description="GET /api/v1/orgs/{org_id}/mxedges\n\nlistOrgMxEdges\n\nGet List of Org MxEdges",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_list_org_mx_edges(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    for_site: Annotated[Any | None, Field(description="Filter for org/site level mist edges")] = None,
    limit: Annotated[int, Field(description="query parameter 'limit'")] = 100,
    page: Annotated[int, Field(description="query parameter 'page'")] = 1,
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/orgs/{org_id}/mxedges",
        path_params={"org_id": org_id},
        query_params={"for_site": for_site, "limit": limit, "page": page},
        body=None,
    )


@_mcp_tool(
    name="mist_restart_org_mx_edge",
    description="POST /api/v1/orgs/{org_id}/mxedges/{mxedge_id}/restart\n\nrestartOrgMxEdge\n\nIn the case where a Mist Edge is replaced, you would need to unregister it. Which disconnects the currently the connected Mist Edge and allow another to register.",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_restart_org_mx_edge(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    mxedge_id: Annotated[str, Field(description="path parameter 'mxedge_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/orgs/{org_id}/mxedges/{mxedge_id}/restart",
        path_params={"org_id": org_id, "mxedge_id": mxedge_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_search_org_mist_edge_events",
    description="GET /api/v1/orgs/{org_id}/mxedges/events/search\n\nsearchOrgMistEdgeEvents\n\nSearch Org Mist Edge Events",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_search_org_mist_edge_events(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    mxedge_id: Annotated[str | None, Field(description="Mist edge id")] = None,
    mxcluster_id: Annotated[str | None, Field(description="Mist edge cluster id")] = None,
    type: Annotated[
        str | None, Field(description="See [List Device Events Definitions](/#operations/listDeviceEventsDefinitions)")
    ] = None,
    service: Annotated[str | None, Field(description="Service running on mist edge(mxagent, tunterm etc)")] = None,
    component: Annotated[str | None, Field(description="Component like PS1, PS2")] = None,
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
        "/api/v1/orgs/{org_id}/mxedges/events/search",
        path_params={"org_id": org_id},
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
    name="mist_search_org_mx_edges",
    description="GET /api/v1/orgs/{org_id}/mxedges/search\n\nsearchOrgMxEdges\n\nSearch Org Mist Edges",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_search_org_mx_edges(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    hostname: Annotated[
        str | None,
        Field(
            description="Partial / full Device hostname. Use `prefix*` for prefix search or `*substring*` for contains search (e.g. `my-london*` and `*london*` match `my-london-1`). Suffix-only wildcards (e.g. `*london-1`) are not supported"
        ),
    ] = None,
    mxedge_id: Annotated[str | None, Field(description="Mist edge id")] = None,
    mxcluster_id: Annotated[str | None, Field(description="Mist edge cluster id")] = None,
    model: Annotated[
        str | None,
        Field(
            description="Partial / full Device model. Use `prefix*` for prefix search or `*substring*` for contains search (e.g. `AP4*` and `*P4*` match `AP43`). Suffix-only wildcards (e.g. `*43`) are not supported"
        ),
    ] = None,
    distro: Annotated[str | None, Field(description="Debian code name (buster, bullseye)")] = None,
    tunterm_version: Annotated[str | None, Field(description="tunterm version")] = None,
    site_id: Annotated[str | None, Field(description="Mist edge site id")] = None,
    stats: Annotated[bool | None, Field(description="Whether to return device stats, default is false")] = None,
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
        "/api/v1/orgs/{org_id}/mxedges/search",
        path_params={"org_id": org_id},
        query_params={
            "hostname": hostname,
            "mxedge_id": mxedge_id,
            "mxcluster_id": mxcluster_id,
            "model": model,
            "distro": distro,
            "tunterm_version": tunterm_version,
            "site_id": site_id,
            "stats": stats,
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
    name="mist_unassign_org_mx_edge_from_site",
    description="POST /api/v1/orgs/{org_id}/mxedges/unassign\n\nunassignOrgMxEdgeFromSite\n\nUnassign Org MxEdge from Site",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_unassign_org_mx_edge_from_site(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request Body")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/orgs/{org_id}/mxedges/unassign",
        path_params={"org_id": org_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_unregister_org_mx_edge",
    description="POST /api/v1/orgs/{org_id}/mxedges/{mxedge_id}/unregister\n\nunregisterOrgMxEdge\n\nIn the case where a Mist Edge is replaced, you would need to unregister it. Which disconnects the currently the connected Mist Edge and allow another to register.",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_unregister_org_mx_edge(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    mxedge_id: Annotated[str, Field(description="path parameter 'mxedge_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/orgs/{org_id}/mxedges/{mxedge_id}/unregister",
        path_params={"org_id": org_id, "mxedge_id": mxedge_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_update_org_mx_edge",
    description="PUT /api/v1/orgs/{org_id}/mxedges/{mxedge_id}\n\nupdateOrgMxEdge\n\nUpdate Org MxEdge",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_update_org_mx_edge(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    mxedge_id: Annotated[str, Field(description="path parameter 'mxedge_id'")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request Body")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "PUT",
        "/api/v1/orgs/{org_id}/mxedges/{mxedge_id}",
        path_params={"org_id": org_id, "mxedge_id": mxedge_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_upload_org_mx_edge_support_files",
    description="POST /api/v1/orgs/{org_id}/mxedges/{mxedge_id}/support\n\nuploadOrgMxEdgeSupportFiles\n\nSupport / Upload Mist Edge support files",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_upload_org_mx_edge_support_files(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    mxedge_id: Annotated[str, Field(description="path parameter 'mxedge_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/orgs/{org_id}/mxedges/{mxedge_id}/support",
        path_params={"org_id": org_id, "mxedge_id": mxedge_id},
        query_params=None,
        body=None,
    )
