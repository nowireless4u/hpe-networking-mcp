"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``scripts/_mist_generator.py`` from
``vendor/mist/mist_openapi.json``. Regenerate via:

    uv run python scripts/regenerate_mist_tools.py

Tag: ``Orgs MxTunnels``
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
    name="mist_create_org_mx_tunnel",
    description="POST /api/v1/orgs/{org_id}/mxtunnels\n\ncreateOrgMxTunnel\n\nCreate an organization Mist Tunnel configuration, including hosting Mist Edge clusters, VLANs, heartbeat settings, and optional IPsec settings.",
    capability=Capability.WRITE,
)
async def mist_create_org_mx_tunnel(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request Body")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/orgs/{org_id}/mxtunnels",
        path_params={"org_id": org_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_delete_org_mx_tunnel",
    description="DELETE /api/v1/orgs/{org_id}/mxtunnels/{mxtunnel_id}\n\ndeleteOrgMxTunnel\n\nDelete an organization Mist Tunnel configuration by Mist Tunnel ID.",
    capability=Capability.WRITE_DELETE,
)
async def mist_delete_org_mx_tunnel(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    mxtunnel_id: Annotated[str, Field(description="path parameter 'mxtunnel_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "DELETE",
        "/api/v1/orgs/{org_id}/mxtunnels/{mxtunnel_id}",
        path_params={"org_id": org_id, "mxtunnel_id": mxtunnel_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_get_org_mx_tunnel",
    description="GET /api/v1/orgs/{org_id}/mxtunnels/{mxtunnel_id}\n\ngetOrgMxTunnel\n\nRetrieve configuration details for a specific organization Mist Tunnel, including cluster, VLAN, heartbeat, IPsec, and preemption settings.",
    capability=Capability.READ,
)
async def mist_get_org_mx_tunnel(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    mxtunnel_id: Annotated[str, Field(description="path parameter 'mxtunnel_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/orgs/{org_id}/mxtunnels/{mxtunnel_id}",
        path_params={"org_id": org_id, "mxtunnel_id": mxtunnel_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_list_org_mx_tunnels",
    description="GET /api/v1/orgs/{org_id}/mxtunnels\n\nlistOrgMxTunnels\n\nList organization Mist Tunnel configurations used to carry AP user VLANs to Mist Edge clusters.",
    capability=Capability.READ,
)
async def mist_list_org_mx_tunnels(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    limit: Annotated[int, Field(description="Maximum number of results to return per page")] = 100,
    page: Annotated[
        int, Field(description="Select the page number to return when using page-based pagination; starts at `1`")
    ] = 1,
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/orgs/{org_id}/mxtunnels",
        path_params={"org_id": org_id},
        query_params={"limit": limit, "page": page},
        body=None,
    )


@_mcp_tool(
    name="mist_update_org_mx_tunnel",
    description="PUT /api/v1/orgs/{org_id}/mxtunnels/{mxtunnel_id}\n\nupdateOrgMxTunnel\n\nUpdate an organization Mist Tunnel configuration, including cluster membership, VLANs, heartbeat settings, IPsec, and preemption behavior.",
    capability=Capability.WRITE,
)
async def mist_update_org_mx_tunnel(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    mxtunnel_id: Annotated[str, Field(description="path parameter 'mxtunnel_id'")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request Body")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "PUT",
        "/api/v1/orgs/{org_id}/mxtunnels/{mxtunnel_id}",
        path_params={"org_id": org_id, "mxtunnel_id": mxtunnel_id},
        query_params=None,
        body=body,
    )
