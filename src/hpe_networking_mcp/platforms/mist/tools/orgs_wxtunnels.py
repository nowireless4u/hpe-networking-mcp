"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``scripts/_mist_generator.py`` from
``vendor/mist/mist_openapi.json``. Regenerate via:

    uv run python scripts/regenerate_mist_tools.py

Tag: ``Orgs WxTunnels``
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
    name="mist_create_org_wx_tunnel",
    description="POST /api/v1/orgs/{org_id}/wxtunnels\n\ncreateOrgWxTunnel\n\nCreate Org WxAN Tunnel",
    capability=Capability.WRITE,
)
async def mist_create_org_wx_tunnel(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request Body")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/orgs/{org_id}/wxtunnels",
        path_params={"org_id": org_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_delete_org_wx_tunnel",
    description="DELETE /api/v1/orgs/{org_id}/wxtunnels/{wxtunnel_id}\n\ndeleteOrgWxTunnel\n\nDelete Org WxLAN Tunnel",
    capability=Capability.WRITE_DELETE,
)
async def mist_delete_org_wx_tunnel(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    wxtunnel_id: Annotated[str, Field(description="path parameter 'wxtunnel_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "DELETE",
        "/api/v1/orgs/{org_id}/wxtunnels/{wxtunnel_id}",
        path_params={"org_id": org_id, "wxtunnel_id": wxtunnel_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_get_org_wx_tunnel",
    description="GET /api/v1/orgs/{org_id}/wxtunnels/{wxtunnel_id}\n\ngetOrgWxTunnel\n\nGet Org WxLAN Tunnel Details",
    capability=Capability.READ,
)
async def mist_get_org_wx_tunnel(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    wxtunnel_id: Annotated[str, Field(description="path parameter 'wxtunnel_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/orgs/{org_id}/wxtunnels/{wxtunnel_id}",
        path_params={"org_id": org_id, "wxtunnel_id": wxtunnel_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_list_org_wx_tunnels",
    description="GET /api/v1/orgs/{org_id}/wxtunnels\n\nlistOrgWxTunnels\n\nGet List of Org WxLAN Tunnels",
    capability=Capability.READ,
)
async def mist_list_org_wx_tunnels(
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
        "/api/v1/orgs/{org_id}/wxtunnels",
        path_params={"org_id": org_id},
        query_params={"limit": limit, "page": page},
        body=None,
    )


@_mcp_tool(
    name="mist_update_org_wx_tunnel",
    description="PUT /api/v1/orgs/{org_id}/wxtunnels/{wxtunnel_id}\n\nupdateOrgWxTunnel\n\nUpdate Org WxLAN Tunnel",
    capability=Capability.WRITE,
)
async def mist_update_org_wx_tunnel(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    wxtunnel_id: Annotated[str, Field(description="path parameter 'wxtunnel_id'")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request Body")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "PUT",
        "/api/v1/orgs/{org_id}/wxtunnels/{wxtunnel_id}",
        path_params={"org_id": org_id, "wxtunnel_id": wxtunnel_id},
        query_params=None,
        body=body,
    )
