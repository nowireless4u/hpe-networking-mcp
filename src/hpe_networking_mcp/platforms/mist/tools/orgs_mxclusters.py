"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``scripts/_mist_generator.py`` from
``vendor/mist/mist_openapi.json``. Regenerate via:

    uv run python scripts/regenerate_mist_tools.py

Tag: ``Orgs MxClusters``
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
    name="mist_create_org_mx_edge_cluster",
    description="POST /api/v1/orgs/{org_id}/mxclusters\n\ncreateOrgMxEdgeCluster\n\nCreate a Mist Edge cluster with tunnel termination, RadSec, NAC,\nand management settings.\n\n\n**Note**: It is not recommended to combine multiple roles (tunnel termination, RadSec, NAC) on the same Mist Edge cluster",
    capability=Capability.WRITE,
)
async def mist_create_org_mx_edge_cluster(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request Body")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/orgs/{org_id}/mxclusters",
        path_params={"org_id": org_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_delete_org_mx_edge_cluster",
    description="DELETE /api/v1/orgs/{org_id}/mxclusters/{mxcluster_id}\n\ndeleteOrgMxEdgeCluster\n\nDelete a Mist Edge cluster by cluster ID, removing its cluster configuration from the organization.",
    capability=Capability.WRITE_DELETE,
)
async def mist_delete_org_mx_edge_cluster(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    mxcluster_id: Annotated[str, Field(description="path parameter 'mxcluster_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "DELETE",
        "/api/v1/orgs/{org_id}/mxclusters/{mxcluster_id}",
        path_params={"org_id": org_id, "mxcluster_id": mxcluster_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_get_org_mx_edge_cluster",
    description="GET /api/v1/orgs/{org_id}/mxclusters/{mxcluster_id}\n\ngetOrgMxEdgeCluster\n\nRetrieve configuration details for a specific Mist Edge cluster, including tunneling, RadSec, NAC, and management settings.",
    capability=Capability.READ,
)
async def mist_get_org_mx_edge_cluster(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    mxcluster_id: Annotated[str, Field(description="path parameter 'mxcluster_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/orgs/{org_id}/mxclusters/{mxcluster_id}",
        path_params={"org_id": org_id, "mxcluster_id": mxcluster_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_list_org_mx_edge_clusters",
    description="GET /api/v1/orgs/{org_id}/mxclusters\n\nlistOrgMxEdgeClusters\n\nList Mist Edge clusters in the organization, which group one or more Mist Edge devices for tunneling, RadSec, and related edge services.",
    capability=Capability.READ,
)
async def mist_list_org_mx_edge_clusters(
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
        "/api/v1/orgs/{org_id}/mxclusters",
        path_params={"org_id": org_id},
        query_params={"limit": limit, "page": page},
        body=None,
    )


@_mcp_tool(
    name="mist_update_org_mx_edge_cluster",
    description="PUT /api/v1/orgs/{org_id}/mxclusters/{mxcluster_id}\n\nupdateOrgMxEdgeCluster\n\nUpdate a Mist Edge cluster's tunneling, RadSec, NAC, and management settings.",
    capability=Capability.WRITE,
)
async def mist_update_org_mx_edge_cluster(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    mxcluster_id: Annotated[str, Field(description="path parameter 'mxcluster_id'")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request Body")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "PUT",
        "/api/v1/orgs/{org_id}/mxclusters/{mxcluster_id}",
        path_params={"org_id": org_id, "mxcluster_id": mxcluster_id},
        query_params=None,
        body=body,
    )
