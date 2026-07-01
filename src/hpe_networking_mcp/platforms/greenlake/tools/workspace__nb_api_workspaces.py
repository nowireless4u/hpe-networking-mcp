"""Generated GreenLake tools — DO NOT EDIT BY HAND.

Generated from the vendored spec ``vendor/greenlake/workspace__workspace-management-v1-nb-openapi-workspace.json`` by the
maintainer-local GreenLake generator. These modules are committed and are the
runtime source of truth; regeneration is a release-time maintainer workflow
(the generator is intentionally not committed — see ``.gitignore``).

Service: ``workspace``   Tag: ``nb_api_workspaces``   Operations: 6
"""

# ruff: noqa: E501, N803
from __future__ import annotations

from typing import Annotated, Any

from fastmcp import Context
from pydantic import Field

from hpe_networking_mcp.platforms._common.annotations import Capability
from hpe_networking_mcp.platforms._common.url import path_seg
from hpe_networking_mcp.platforms.greenlake._registry import tool
from hpe_networking_mcp.platforms.greenlake.client import greenlake_request


@tool(
    name="greenlake_delete_workspaces_v1_msp_tenants_tenant_id",
    description="DELETE /workspaces/v1/msp-tenants/{tenantId}\n\nremove_tenant_workspaces_v1_msp_tenants__tenantId__delete\n\nDelete a managed service tenant",
    capability=Capability.WRITE_DELETE,
)
async def greenlake_delete_workspaces_v1_msp_tenants_tenant_id(
    ctx: Context,
    tenantId: Annotated[str, Field(description="The workspace ID for the tenant you want to delete.")],
) -> Any:
    path = f"/workspaces/v1/msp-tenants/{path_seg(tenantId)}"
    return await greenlake_request(
        ctx,
        "DELETE",
        path,
    )


@tool(
    name="greenlake_get_workspaces_v1_msp_tenants",
    description="GET /workspaces/v1/msp-tenants\n\nget_tenants_workspaces_v1_msp_tenants_get\n\nGet list of MSP Tenants",
    capability=Capability.READ,
)
async def greenlake_get_workspaces_v1_msp_tenants(
    ctx: Context,
    filter: Annotated[
        str | None,
        Field(
            default=None,
            description="Filter data using a subset of OData 4.0 and return only the subset of resources that match the filter.  Get list of MSP Tenants API can be filtered by: - id - createdAt - updatedAt - workspaceName - createdBy - inventoryOwnership",
        ),
    ] = None,
    offset: Annotated[
        int | None,
        Field(
            default=None,
            description="Specify pagination offset. An offset argument defines how many pages to skip before returning results.",
        ),
    ] = None,
    limit: Annotated[
        int | None,
        Field(
            default=None,
            description="Specify the maximum number of entries per page. NOTE: The maximum value accepted is 300.",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if filter is not None:
        query_params["filter"] = filter
    if offset is not None:
        query_params["offset"] = offset
    if limit is not None:
        query_params["limit"] = limit
    return await greenlake_request(
        ctx,
        "GET",
        "/workspaces/v1/msp-tenants",
        query_params=query_params or None,
    )


@tool(
    name="greenlake_get_workspaces_v1_workspaces_workspace_id",
    description="GET /workspaces/v1/workspaces/{workspaceId}\n\nget_workspace_workspaces_v1_workspaces__workspaceId__get\n\nGet workspace information",
    capability=Capability.READ,
)
async def greenlake_get_workspaces_v1_workspaces_workspace_id(
    ctx: Context,
    workspaceId: Annotated[str, Field(description="The unique identifier of the workspace.")],
) -> Any:
    path = f"/workspaces/v1/workspaces/{path_seg(workspaceId)}"
    return await greenlake_request(
        ctx,
        "GET",
        path,
    )


@tool(
    name="greenlake_get_workspaces_v1_workspaces_workspace_id_contact",
    description="GET /workspaces/v1/workspaces/{workspaceId}/contact\n\nget_workspace_detailed_info_workspaces_v1_workspaces__workspaceId__contact_get\n\nGet detailed workspace information",
    capability=Capability.READ,
)
async def greenlake_get_workspaces_v1_workspaces_workspace_id_contact(
    ctx: Context,
    workspaceId: Annotated[str, Field(description="The unique identifier of the workspace.")],
) -> Any:
    path = f"/workspaces/v1/workspaces/{path_seg(workspaceId)}/contact"
    return await greenlake_request(
        ctx,
        "GET",
        path,
    )


@tool(
    name="greenlake_post_workspaces_v1_msp_tenants",
    description="POST /workspaces/v1/msp-tenants\n\ncreate_tenant_workspaces_v1_msp_tenants_post\n\nCreate MSP customer workspace",
    capability=Capability.WRITE,
)
async def greenlake_post_workspaces_v1_msp_tenants(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await greenlake_request(
        ctx,
        "POST",
        "/workspaces/v1/msp-tenants",
        body=body,
    )


@tool(
    name="greenlake_put_workspaces_v1_msp_tenants_tenant_id",
    description="PUT /workspaces/v1/msp-tenants/{tenantId}\n\nupdate_tenant_api_workspaces_v1_msp_tenants__tenantId__put\n\nUpdate managed service tenant",
    capability=Capability.WRITE,
)
async def greenlake_put_workspaces_v1_msp_tenants_tenant_id(
    ctx: Context,
    tenantId: Annotated[str, Field(description="The unique ID of the tenant.")],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    path = f"/workspaces/v1/msp-tenants/{path_seg(tenantId)}"
    return await greenlake_request(
        ctx,
        "PUT",
        path,
        body=body,
    )
