"""Generated GreenLake tools — DO NOT EDIT BY HAND.

Generated from the vendored spec ``vendor/greenlake/authorization__groups-v1beta1-external-groups-v1beta1.json`` by the
maintainer-local GreenLake generator. These modules are committed and are the
runtime source of truth; regeneration is a release-time maintainer workflow
(the generator is intentionally not committed — see ``.gitignore``).

Service: ``authorization``   Tag: ``groups``   Operations: 9
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
    name="greenlake_delete_workspaces_v1beta1_groups_group_id",
    description="DELETE /workspaces/v1beta1/groups/{groupId}\n\nremoveGroupV2\n\nDelete the workspace group",
    capability=Capability.WRITE_DELETE,
)
async def greenlake_delete_workspaces_v1beta1_groups_group_id(
    ctx: Context,
    groupId: Annotated[str, Field(description="HPE GreenLake group ID")],
) -> Any:
    path = f"/workspaces/v1beta1/groups/{path_seg(groupId)}"
    return await greenlake_request(
        ctx,
        "DELETE",
        path,
    )


@tool(
    name="greenlake_delete_workspaces_v1beta1_groups_group_id_group_workspaces_group_workspace_id",
    description="DELETE /workspaces/v1beta1/groups/{groupId}/group-workspaces/{groupWorkspaceId}\n\ndeleteWorkspaceFromGroup\n\nRemove a workspace from the workspace group",
    capability=Capability.WRITE_DELETE,
)
async def greenlake_delete_workspaces_v1beta1_groups_group_id_group_workspaces_group_workspace_id(
    ctx: Context,
    groupId: Annotated[str, Field(description="HPE GreenLake unique group ID")],
    groupWorkspaceId: Annotated[
        str, Field(description="HPE GreenLake unique resource ID for this workspace belonging to the group")
    ],
) -> Any:
    path = f"/workspaces/v1beta1/groups/{path_seg(groupId)}/group-workspaces/{path_seg(groupWorkspaceId)}"
    return await greenlake_request(
        ctx,
        "DELETE",
        path,
    )


@tool(
    name="greenlake_get_workspaces_v1beta1_groups",
    description="GET /workspaces/v1beta1/groups\n\ngetGroupsV2\n\nList of Paginated workspace groups",
    capability=Capability.READ,
)
async def greenlake_get_workspaces_v1beta1_groups(
    ctx: Context,
    offset: Annotated[
        int | None, Field(default=None, description="The starting offset from which to begin retrieving items")
    ] = None,
    limit: Annotated[
        int | None,
        Field(
            default=None, description="Specifies the number of query results to be returned in a query response page"
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if offset is not None:
        query_params["offset"] = offset
    if limit is not None:
        query_params["limit"] = limit
    return await greenlake_request(
        ctx,
        "GET",
        "/workspaces/v1beta1/groups",
        query_params=query_params or None,
    )


@tool(
    name="greenlake_get_workspaces_v1beta1_groups_group_id",
    description="GET /workspaces/v1beta1/groups/{groupId}\n\nfetchGroupV2\n\nGet the workspace group details",
    capability=Capability.READ,
)
async def greenlake_get_workspaces_v1beta1_groups_group_id(
    ctx: Context,
    groupId: Annotated[str, Field(description="HPE GreenLake unique group ID")],
) -> Any:
    path = f"/workspaces/v1beta1/groups/{path_seg(groupId)}"
    return await greenlake_request(
        ctx,
        "GET",
        path,
    )


@tool(
    name="greenlake_get_workspaces_v1beta1_groups_group_id_group_workspaces",
    description="GET /workspaces/v1beta1/groups/{groupId}/group-workspaces\n\nlistGroupWorkspaces\n\nList of paginated workspaces associated with the group ID",
    capability=Capability.READ,
)
async def greenlake_get_workspaces_v1beta1_groups_group_id_group_workspaces(
    ctx: Context,
    groupId: Annotated[str, Field(description="HPE GreenLake group ID")],
    limit: Annotated[
        int | None,
        Field(
            default=None, description="Specifies the number of query results to be returned in a query response page"
        ),
    ] = None,
    offset: Annotated[
        int | None, Field(default=None, description="The starting offset from which to begin retrieving items")
    ] = None,
) -> Any:
    path = f"/workspaces/v1beta1/groups/{path_seg(groupId)}/group-workspaces"
    query_params: dict[str, Any] = {}
    if limit is not None:
        query_params["limit"] = limit
    if offset is not None:
        query_params["offset"] = offset
    return await greenlake_request(
        ctx,
        "GET",
        path,
        query_params=query_params or None,
    )


@tool(
    name="greenlake_get_workspaces_v1beta1_groups_group_id_group_workspaces_group_workspace_id",
    description="GET /workspaces/v1beta1/groups/{groupId}/group-workspaces/{groupWorkspaceId}\n\ngetGroupWorkspace\n\nGet the workspace details",
    capability=Capability.READ,
)
async def greenlake_get_workspaces_v1beta1_groups_group_id_group_workspaces_group_workspace_id(
    ctx: Context,
    groupId: Annotated[str, Field(description="HPE GreenLake unique group ID")],
    groupWorkspaceId: Annotated[
        str, Field(description="HPE GreenLake unique resource ID for this workspace belonging to the group")
    ],
) -> Any:
    path = f"/workspaces/v1beta1/groups/{path_seg(groupId)}/group-workspaces/{path_seg(groupWorkspaceId)}"
    return await greenlake_request(
        ctx,
        "GET",
        path,
    )


@tool(
    name="greenlake_post_workspaces_v1beta1_groups",
    description="POST /workspaces/v1beta1/groups\n\ncreateNewGroupV2\n\nCreate a workspace group",
    capability=Capability.WRITE,
)
async def greenlake_post_workspaces_v1beta1_groups(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await greenlake_request(
        ctx,
        "POST",
        "/workspaces/v1beta1/groups",
        body=body,
    )


@tool(
    name="greenlake_post_workspaces_v1beta1_groups_group_id_group_workspaces",
    description="POST /workspaces/v1beta1/groups/{groupId}/group-workspaces\n\naddWorkspaceToGroup\n\nAdd a workspace to the group",
    capability=Capability.WRITE,
)
async def greenlake_post_workspaces_v1beta1_groups_group_id_group_workspaces(
    ctx: Context,
    groupId: Annotated[str, Field(description="HPE GreenLake unique group ID")],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    path = f"/workspaces/v1beta1/groups/{path_seg(groupId)}/group-workspaces"
    return await greenlake_request(
        ctx,
        "POST",
        path,
        body=body,
    )


@tool(
    name="greenlake_put_workspaces_v1beta1_groups_group_id",
    description="PUT /workspaces/v1beta1/groups/{groupId}\n\nputGroupV2\n\nUpdate workspace group details",
    capability=Capability.WRITE,
)
async def greenlake_put_workspaces_v1beta1_groups_group_id(
    ctx: Context,
    groupId: Annotated[str, Field(description="HPE GreenLake unique group ID")],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    path = f"/workspaces/v1beta1/groups/{path_seg(groupId)}"
    return await greenlake_request(
        ctx,
        "PUT",
        path,
        body=body,
    )
