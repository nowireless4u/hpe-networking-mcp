"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``scripts/_mist_generator.py`` from
``vendor/mist/mist_openapi.json``. Regenerate via:

    uv run python scripts/regenerate_mist_tools.py

Tag: ``Orgs EVPN Topologies``
Operations in this file: 5
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
    name="mist_create_org_evpn_topology",
    description="POST /api/v1/orgs/{org_id}/evpn_topologies\n\ncreateOrgEvpnTopology\n\nWhile all the `evpn_id` / `downlink_ips` can be specified by hand, the easiest way is to call the `build_vpn_topology` API, allowing you to examine the diff, and update it yourself. You can also simply call it with `overwrite=true` which will apply the updates for you.\n\n**Notes:**\n1. You can use `core` / `distribution` / `access` to create a CLOS topology\n2. You can also use `core` / `distribution` to form a 2-tier EVPN topology where ESI-Lag is configured distribution to connect to access switches\n3. In a small/medium campu...",
    capability=Capability.WRITE,
)
async def mist_create_org_evpn_topology(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    body: Annotated[
        dict[str, Any] | None,
        Field(default=None, description="Request body for POST /api/v1/orgs/{org_id}/evpn_topologies"),
    ] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/orgs/{org_id}/evpn_topologies",
        path_params={"org_id": org_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_delete_org_evpn_topology",
    description="DELETE /api/v1/orgs/{org_id}/evpn_topologies/{evpn_topology_id}\n\ndeleteOrgEvpnTopology\n\nDelete an EVPN topology from the organization by topology ID.",
    capability=Capability.WRITE_DELETE,
)
async def mist_delete_org_evpn_topology(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    evpn_topology_id: Annotated[str, Field(description="path parameter 'evpn_topology_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "DELETE",
        "/api/v1/orgs/{org_id}/evpn_topologies/{evpn_topology_id}",
        path_params={"org_id": org_id, "evpn_topology_id": evpn_topology_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_get_org_evpn_topology",
    description="GET /api/v1/orgs/{org_id}/evpn_topologies/{evpn_topology_id}\n\ngetOrgEvpnTopology\n\nRetrieve the switch roles, links, and generation options for a specific EVPN topology.",
    capability=Capability.READ,
)
async def mist_get_org_evpn_topology(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    evpn_topology_id: Annotated[str, Field(description="path parameter 'evpn_topology_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/orgs/{org_id}/evpn_topologies/{evpn_topology_id}",
        path_params={"org_id": org_id, "evpn_topology_id": evpn_topology_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_list_org_evpn_topologies",
    description="GET /api/v1/orgs/{org_id}/evpn_topologies\n\nlistOrgEvpnTopologies\n\nList EVPN topology records in the organization, optionally filtering for org-level, site-level, or all topologies with `for_site`.",
    capability=Capability.READ,
)
async def mist_list_org_evpn_topologies(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    for_site: Annotated[
        Any | None, Field(description="Filter for org/site level EVPN topologies. enum: `any`, `false`, `true`")
    ] = None,
    limit: Annotated[int, Field(description="Maximum number of results to return per page")] = 100,
    page: Annotated[
        int, Field(description="Select the page number to return when using page-based pagination; starts at `1`")
    ] = 1,
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/orgs/{org_id}/evpn_topologies",
        path_params={"org_id": org_id},
        query_params={"for_site": for_site, "limit": limit, "page": page},
        body=None,
    )


@_mcp_tool(
    name="mist_update_org_evpn_topology",
    description="PUT /api/v1/orgs/{org_id}/evpn_topologies/{evpn_topology_id}\n\nupdateOrgEvpnTopology\n\nUpdate an EVPN topology, including switch membership, switch roles, links, and generation options.",
    capability=Capability.WRITE,
)
async def mist_update_org_evpn_topology(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    evpn_topology_id: Annotated[str, Field(description="path parameter 'evpn_topology_id'")],
    body: Annotated[
        dict[str, Any] | None,
        Field(
            default=None, description="Request body for PUT /api/v1/orgs/{org_id}/evpn_topologies/{evpn_topology_id}"
        ),
    ] = None,
) -> Any:
    return await mist_request(
        ctx,
        "PUT",
        "/api/v1/orgs/{org_id}/evpn_topologies/{evpn_topology_id}",
        path_params={"org_id": org_id, "evpn_topology_id": evpn_topology_id},
        query_params=None,
        body=body,
    )
