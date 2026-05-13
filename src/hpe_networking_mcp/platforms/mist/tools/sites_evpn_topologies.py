"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``hpe_networking_mcp.platforms.mist._generator``
from ``vendor/mist_openapi.json``. Regenerate via:

    uv run python -m hpe_networking_mcp.platforms.mist.regenerate

Tag: ``Sites EVPN Topologies``
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
    name="mist_create_site_evpn_topology",
    description="POST /api/v1/sites/{site_id}/evpn_topologies\n\ncreateSiteEvpnTopology\n\nWhile all the `evpn_id` / `downlink_ips` can be specified by hand, the easiest way is to call the `build_vpn_topology` API, allowing you to examine the diff, and update it yourself. You can also simply call it with `overwrite=true` which will apply the updates for you.\n\n**Notes:**\n1. You can use `core` / `distribution` / `access` to create a CLOS topology\n2. You can also use `core` / `distribution` to form a 2-tier EVPN topology where ESI-Lag is configured distribution to connect to access switches\n3. In a small/medium ca...",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_create_site_evpn_topology(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    body: Annotated[
        dict[str, Any] | None,
        Field(default=None, description="Request body for POST /api/v1/sites/{site_id}/evpn_topologies"),
    ] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/sites/{site_id}/evpn_topologies",
        path_params={"site_id": site_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_delete_site_evpn_topology",
    description="DELETE /api/v1/sites/{site_id}/evpn_topologies/{evpn_topology_id}\n\ndeleteSiteEvpnTopology\n\nDelete the site EVPN Topology",
    tags={"mist", "mist_write", "mist_write_delete"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=True),
)
async def mist_delete_site_evpn_topology(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    evpn_topology_id: Annotated[str, Field(description="path parameter 'evpn_topology_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "DELETE",
        "/api/v1/sites/{site_id}/evpn_topologies/{evpn_topology_id}",
        path_params={"site_id": site_id, "evpn_topology_id": evpn_topology_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_get_site_evpn_topology",
    description="GET /api/v1/sites/{site_id}/evpn_topologies/{evpn_topology_id}\n\ngetSiteEvpnTopology\n\nGet One EVPN Topology Detail",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_get_site_evpn_topology(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    evpn_topology_id: Annotated[str, Field(description="path parameter 'evpn_topology_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/sites/{site_id}/evpn_topologies/{evpn_topology_id}",
        path_params={"site_id": site_id, "evpn_topology_id": evpn_topology_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_list_site_evpn_topologies",
    description="GET /api/v1/sites/{site_id}/evpn_topologies\n\nlistSiteEvpnTopologies\n\nGet the existing EVPN topology",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_list_site_evpn_topologies(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    limit: Annotated[int, Field(description="query parameter 'limit'")] = 100,
    page: Annotated[int, Field(description="query parameter 'page'")] = 1,
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/sites/{site_id}/evpn_topologies",
        path_params={"site_id": site_id},
        query_params={"limit": limit, "page": page},
        body=None,
    )


@_mcp_tool(
    name="mist_update_site_evpn_topology",
    description="PUT /api/v1/sites/{site_id}/evpn_topologies/{evpn_topology_id}\n\nupdateSiteEvpnTopology\n\nUpdate the EVPN Topology",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_update_site_evpn_topology(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    evpn_topology_id: Annotated[str, Field(description="path parameter 'evpn_topology_id'")],
    body: Annotated[
        dict[str, Any] | None,
        Field(
            default=None, description="Request body for PUT /api/v1/sites/{site_id}/evpn_topologies/{evpn_topology_id}"
        ),
    ] = None,
) -> Any:
    return await mist_request(
        ctx,
        "PUT",
        "/api/v1/sites/{site_id}/evpn_topologies/{evpn_topology_id}",
        path_params={"site_id": site_id, "evpn_topology_id": evpn_topology_id},
        query_params=None,
        body=body,
    )
