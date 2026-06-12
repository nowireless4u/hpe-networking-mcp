"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``scripts/_mist_generator.py`` from
``vendor/mist/mist_openapi.json``. Regenerate via:

    uv run python scripts/regenerate_mist_tools.py

Tag: ``Orgs Networks``
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
    name="mist_create_org_network",
    description="POST /api/v1/orgs/{org_id}/networks\n\ncreateOrgNetwork\n\nCreate an organization network definition with subnet, gateway,\nVLAN, access, NAT, multicast, tenant, and VPN access settings used for service\nroutes and gateway or network template configuration.\n\n\nNetworks can be used\n- in the gateway configuration to define Layer 3 network settings and policies for traffic entering or leaving the gateway through a specific interface, such as a corporate LAN, guest Wi-Fi, or DMZ network.\n- in the service policies to allow or deny traffic matching the network or to apply specific inspection settings or...",
    capability=Capability.WRITE,
)
async def mist_create_org_network(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    body: Annotated[
        dict[str, Any] | None, Field(default=None, description="Request body for POST /api/v1/orgs/{org_id}/networks")
    ] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/orgs/{org_id}/networks",
        path_params={"org_id": org_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_delete_org_network",
    description="DELETE /api/v1/orgs/{org_id}/networks/{network_id}\n\ndeleteOrgNetwork\n\nDelete an organization network definition by network ID so it can no longer be referenced by gateway or network template configuration.",
    capability=Capability.WRITE_DELETE,
)
async def mist_delete_org_network(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    network_id: Annotated[str, Field(description="path parameter 'network_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "DELETE",
        "/api/v1/orgs/{org_id}/networks/{network_id}",
        path_params={"org_id": org_id, "network_id": network_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_get_org_network",
    description="GET /api/v1/orgs/{org_id}/networks/{network_id}\n\ngetOrgNetwork\n\nRetrieve details for a specific organization network, including subnet, gateway, VLAN, access, NAT, multicast, tenant, and VPN access settings.",
    capability=Capability.READ,
)
async def mist_get_org_network(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    network_id: Annotated[str, Field(description="path parameter 'network_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/orgs/{org_id}/networks/{network_id}",
        path_params={"org_id": org_id, "network_id": network_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_list_org_networks",
    description="GET /api/v1/orgs/{org_id}/networks\n\nlistOrgNetworks\n\nList organization-level Layer 3 network definitions used for service routes and gateway or network template configuration.",
    capability=Capability.READ,
)
async def mist_list_org_networks(
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
        "/api/v1/orgs/{org_id}/networks",
        path_params={"org_id": org_id},
        query_params={"limit": limit, "page": page},
        body=None,
    )


@_mcp_tool(
    name="mist_update_org_network",
    description="PUT /api/v1/orgs/{org_id}/networks/{network_id}\n\nupdateOrgNetwork\n\nUpdate an organization network definition, including subnet, gateway, VLAN, access, NAT, multicast, tenant, and VPN access settings.",
    capability=Capability.WRITE,
)
async def mist_update_org_network(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    network_id: Annotated[str, Field(description="path parameter 'network_id'")],
    body: Annotated[
        dict[str, Any] | None,
        Field(default=None, description="Request body for PUT /api/v1/orgs/{org_id}/networks/{network_id}"),
    ] = None,
) -> Any:
    return await mist_request(
        ctx,
        "PUT",
        "/api/v1/orgs/{org_id}/networks/{network_id}",
        path_params={"org_id": org_id, "network_id": network_id},
        query_params=None,
        body=body,
    )
