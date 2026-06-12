"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``scripts/_mist_generator.py`` from
``vendor/mist/mist_openapi.json``. Regenerate via:

    uv run python scripts/regenerate_mist_tools.py

Tag: ``Orgs MxEdges``
Operations in this file: 22
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
    name="mist_add_org_mx_edge_image",
    description="POST /api/v1/orgs/{org_id}/mxedges/{mxedge_id}/image/{image_number}\n\naddOrgMxEdgeImage\n\nUpload and attach an image file to a Mist Edge appliance. A Mist Edge can have up to three image attachments.",
    capability=Capability.WRITE,
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
    description="POST /api/v1/orgs/{org_id}/mxedges/assign\n\nassignOrgMxEdgeToSite\n\nAssign one or more Mist Edge appliances from the organization to a site by Mist Edge ID and site ID.",
    capability=Capability.WRITE,
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
    description="POST /api/v1/orgs/{org_id}/mxedges/{mxedge_id}/services/tunterm/bounce_port\n\nbounceOrgMxEdgeDataPorts\n\nBounce one or more TunTerm data ports on a Mist Edge, optionally setting the hold time between port bounces.",
    capability=Capability.WRITE,
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
    description="POST /api/v1/orgs/{org_id}/mxedges/claim\n\nclaimOrgMxEdge\n\nClaim one or more Mist Edge appliances into the organization using their claim codes.",
    capability=Capability.WRITE,
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
    description="POST /api/v1/orgs/{org_id}/mxedges/{mxedge_id}/services/{name}/{action}\n\ncontrolOrgMxEdgeServices\n\nStart, stop, or restart a named Mist Edge service such as `tunterm`, `mxagent`, or `radsecproxy`.",
    capability=Capability.WRITE,
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
    description="GET /api/v1/orgs/{org_id}/mxedges/count\n\ncountOrgMxEdges\n\nCount organization Mist Edge records, optionally grouped by `distinct` and filtered by Mist Edge, cluster, site, model, distro, tunnel termination version, and time range.",
    capability=Capability.READ,
)
async def mist_count_org_mx_edges(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    distinct: Annotated[
        Any | None,
        Field(
            description="Field used to group this count response. enum: `distro`, `model`, `mxcluster_id`, `site_id`, `tunterm_version`"
        ),
    ] = None,
    mxedge_id: Annotated[str | None, Field(description="Filter results by Mist Edge identifier")] = None,
    site_id: Annotated[str | None, Field(description="Mist edge site id")] = None,
    mxcluster_id: Annotated[str | None, Field(description="Mist edge cluster id")] = None,
    model: Annotated[str | None, Field(description="Filter results by device model")] = None,
    distro: Annotated[str | None, Field(description="Debian code name (buster, bullseye)")] = None,
    tunterm_version: Annotated[str | None, Field(description="Filter results by tunnel termination version")] = None,
    sort: Annotated[str | None, Field(description="Field used to sort results")] = None,
    stats: Annotated[bool | None, Field(description="Whether to return device stats, default is false")] = None,
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
    description="GET /api/v1/orgs/{org_id}/mxedges/events/count\n\ncountOrgSiteMxEdgeEvents\n\nCount Mist Edge event records across the organization, optionally grouped by `distinct` and filtered by Mist Edge, cluster, event type, service, and time range.",
    capability=Capability.READ,
)
async def mist_count_org_site_mx_edge_events(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
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
    description="POST /api/v1/orgs/{org_id}/mxedges\n\ncreateOrgMxEdge\n\nCreate a Mist Edge appliance configuration in the organization, including cluster assignment, management, services, and tunnel termination settings.",
    capability=Capability.WRITE,
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
    description="DELETE /api/v1/orgs/{org_id}/mxedges/{mxedge_id}\n\ndeleteOrgMxEdge\n\nDelete a Mist Edge appliance record from the organization by Mist Edge ID.",
    capability=Capability.WRITE_DELETE,
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
    description="DELETE /api/v1/orgs/{org_id}/mxedges/{mxedge_id}/image/{image_number}\n\ndeleteOrgMxEdgeImage\n\nDelete a numbered image attachment from a Mist Edge appliance.",
    capability=Capability.WRITE_DELETE,
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
    description="POST /api/v1/orgs/{org_id}/mxedges/{mxedge_id}/services/tunterm/disconnect_aps\n\ndisconnectOrgMxEdgeTuntermAps\n\nDisconnect specific APs from the Mist Edge TunTerm service by AP MAC address.",
    capability=Capability.WRITE,
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
    description="GET /api/v1/orgs/{org_id}/mxedges/{mxedge_id}\n\ngetOrgMxEdge\n\nRetrieve configuration and registration details for a specific Mist Edge appliance in the organization.",
    capability=Capability.READ,
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
    description="GET /api/v1/orgs/{org_id}/mxedges/versions\n\ngetOrgMxEdgeUpgradeInfo\n\nRetrieve available Mist Edge package versions by upgrade channel and distro.",
    capability=Capability.READ,
)
async def mist_get_org_mx_edge_upgrade_info(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    channel: Annotated[
        Any | None,
        Field(description="Upgrade channel used to filter available versions. enum: `alpha`, `beta`, `stable`"),
    ] = None,
    distro: Annotated[str | None, Field(description="Filter results by distro")] = None,
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
    description="GET /api/v1/orgs/{org_id}/mxedges/{mxedge_id}/vm_params\n\ngetOrgMxEdgeVmParams\n\nRetrieve VM deployment parameters for a Mist Edge, including model, optional name, and base64 user data.",
    capability=Capability.READ,
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
    description="GET /api/v1/orgs/{org_id}/mxedges\n\nlistOrgMxEdges\n\nList Mist Edge appliances in the organization, optionally filtering for org-level, site-level, or all Mist Edges with `for_site`.",
    capability=Capability.READ,
)
async def mist_list_org_mx_edges(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    for_site: Annotated[
        Any | None, Field(description="Filter for org/site level Mist Edges. enum: `any`, `false`, `true`")
    ] = None,
    limit: Annotated[int, Field(description="Maximum number of results to return per page")] = 100,
    page: Annotated[
        int, Field(description="Select the page number to return when using page-based pagination; starts at `1`")
    ] = 1,
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
    description="POST /api/v1/orgs/{org_id}/mxedges/{mxedge_id}/restart\n\nrestartOrgMxEdge\n\nRestart the registration workflow for a Mist Edge replacement by disconnecting the currently registered appliance so another Mist Edge can register.",
    capability=Capability.WRITE,
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
    description="GET /api/v1/orgs/{org_id}/mxedges/events/search\n\nsearchOrgMistEdgeEvents\n\nSearch Mist Edge event records across the organization with filters for Mist Edge, cluster, event type, service, component, and time range.",
    capability=Capability.READ,
)
async def mist_search_org_mist_edge_events(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    mxedge_id: Annotated[str | None, Field(description="Filter results by Mist Edge identifier")] = None,
    mxcluster_id: Annotated[str | None, Field(description="Mist edge cluster id")] = None,
    type: Annotated[
        str | None, Field(description="See [List Device Events Definitions](/#operations/listDeviceEventsDefinitions)")
    ] = None,
    service: Annotated[str | None, Field(description="Filter results by service name")] = None,
    component: Annotated[str | None, Field(description="Filter results by component name")] = None,
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
    description="GET /api/v1/orgs/{org_id}/mxedges/search\n\nsearchOrgMxEdges\n\nSearch organization Mist Edge records with filters for hostname, Mist Edge, cluster, site, model, distro, tunnel termination version, and time range.",
    capability=Capability.READ,
)
async def mist_search_org_mx_edges(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    hostname: Annotated[
        str | None,
        Field(
            description="Partial / full Device hostname. Use `prefix*` for prefix search or `*substring*` for contains search (e.g. `my-london*` and `*london*` match `my-london-1`). Suffix-only wildcards (e.g. `*london-1`) are not supported. Accepts multiple com..."
        ),
    ] = None,
    mxedge_id: Annotated[
        str | None,
        Field(description="Filter results by Mist Edge identifier. Accepts multiple comma-separated values."),
    ] = None,
    mxcluster_id: Annotated[
        str | None, Field(description="Mist edge cluster id. Accepts multiple comma-separated values.")
    ] = None,
    model: Annotated[
        str | None,
        Field(
            description="Partial / full Device model. Use `prefix*` for prefix search or `*substring*` for contains search (e.g. `AP4*` and `*P4*` match `AP43`). Suffix-only wildcards (e.g. `*43`) are not supported. Accepts multiple comma-separated values."
        ),
    ] = None,
    distro: Annotated[str | None, Field(description="Debian code name (buster, bullseye)")] = None,
    tunterm_version: Annotated[str | None, Field(description="Filter results by tunnel termination version")] = None,
    site_id: Annotated[str | None, Field(description="Mist edge site id")] = None,
    stats: Annotated[bool | None, Field(description="Whether to return device stats, default is false")] = None,
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
    description="POST /api/v1/orgs/{org_id}/mxedges/unassign\n\nunassignOrgMxEdgeFromSite\n\nUnassign one or more Mist Edge appliances from their current site while keeping them in the organization.",
    capability=Capability.WRITE,
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
    description="POST /api/v1/orgs/{org_id}/mxedges/{mxedge_id}/unregister\n\nunregisterOrgMxEdge\n\nUnregister a Mist Edge during a replacement workflow by disconnecting the currently registered appliance so another Mist Edge can register.",
    capability=Capability.WRITE,
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
    description="PUT /api/v1/orgs/{org_id}/mxedges/{mxedge_id}\n\nupdateOrgMxEdge\n\nUpdate a Mist Edge appliance configuration, including model, name, management IP, services, and tunnel termination settings.",
    capability=Capability.WRITE,
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
    description="POST /api/v1/orgs/{org_id}/mxedges/{mxedge_id}/support\n\nuploadOrgMxEdgeSupportFiles\n\nTrigger upload of support files from a Mist Edge for troubleshooting.",
    capability=Capability.WRITE,
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
