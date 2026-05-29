"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``scripts/_mist_generator.py`` from
``vendor/mist_openapi.json``. Regenerate via:

    uv run python scripts/regenerate_mist_tools.py

Tag: ``Sites WxTunnels``
Operations in this file: 5
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
    name="mist_create_site_wx_tunnel",
    description="POST /api/v1/sites/{site_id}/wxtunnels\n\ncreateSiteWxTunnel\n\nCreate Site WxLan Tunnel",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_create_site_wx_tunnel(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request Body")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/sites/{site_id}/wxtunnels",
        path_params={"site_id": site_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_delete_site_wx_tunnel",
    description="DELETE /api/v1/sites/{site_id}/wxtunnels/{wxtunnel_id}\n\ndeleteSiteWxTunnel\n\nDelete Site WxLan Tunnel",
    tags={"mist", "mist_write", "mist_write_delete"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=True),
)
async def mist_delete_site_wx_tunnel(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    wxtunnel_id: Annotated[str, Field(description="path parameter 'wxtunnel_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "DELETE",
        "/api/v1/sites/{site_id}/wxtunnels/{wxtunnel_id}",
        path_params={"site_id": site_id, "wxtunnel_id": wxtunnel_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_get_site_wx_tunnel",
    description="GET /api/v1/sites/{site_id}/wxtunnels/{wxtunnel_id}\n\ngetSiteWxTunnel\n\nGet Site WxLan tunnel Details",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_get_site_wx_tunnel(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    wxtunnel_id: Annotated[str, Field(description="path parameter 'wxtunnel_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/sites/{site_id}/wxtunnels/{wxtunnel_id}",
        path_params={"site_id": site_id, "wxtunnel_id": wxtunnel_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_list_site_wx_tunnels",
    description="GET /api/v1/sites/{site_id}/wxtunnels\n\nlistSiteWxTunnels\n\nGet List of Site WxLan Tunnels",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_list_site_wx_tunnels(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    limit: Annotated[int, Field(description="query parameter 'limit'")] = 100,
    page: Annotated[int, Field(description="query parameter 'page'")] = 1,
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/sites/{site_id}/wxtunnels",
        path_params={"site_id": site_id},
        query_params={"limit": limit, "page": page},
        body=None,
    )


@_mcp_tool(
    name="mist_update_site_wx_tunnel",
    description="PUT /api/v1/sites/{site_id}/wxtunnels/{wxtunnel_id}\n\nupdateSiteWxTunnel\n\nUpdate Site WxLan Tunnel",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_update_site_wx_tunnel(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    wxtunnel_id: Annotated[str, Field(description="path parameter 'wxtunnel_id'")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request Body")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "PUT",
        "/api/v1/sites/{site_id}/wxtunnels/{wxtunnel_id}",
        path_params={"site_id": site_id, "wxtunnel_id": wxtunnel_id},
        query_params=None,
        body=body,
    )
