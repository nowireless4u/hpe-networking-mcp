"""Generated GreenLake tools — DO NOT EDIT BY HAND.

Generated from the vendored spec ``vendor/greenlake/authorization__authz-v1beta1-external-authz-v2-config.json`` by the
maintainer-local GreenLake generator. These modules are committed and are the
runtime source of truth; regeneration is a release-time maintainer workflow
(the generator is intentionally not committed — see ``.gitignore``).

Service: ``authorization``   Tag: ``role_assignments``   Operations: 5
"""

# ruff: noqa: E501
from __future__ import annotations

from typing import Annotated, Any

from fastmcp import Context
from pydantic import Field

from hpe_networking_mcp.platforms._common.annotations import Capability
from hpe_networking_mcp.platforms._common.url import path_seg
from hpe_networking_mcp.platforms.greenlake._registry import tool
from hpe_networking_mcp.platforms.greenlake.client import greenlake_request


@tool(
    name="greenlake_delete_authorization_v1beta1_role_assignments_id",
    description="DELETE /authorization/v1beta1/role-assignments/{id}\n\ndeleteRoleAssignmentV1beta1\n\nDelete a role assignment instance by ID",
    capability=Capability.WRITE_DELETE,
)
async def greenlake_delete_authorization_v1beta1_role_assignments_id(
    ctx: Context,
    id: Annotated[str, Field(description="path parameter 'id'")],
) -> Any:
    path = f"/authorization/v1beta1/role-assignments/{path_seg(id)}"
    return await greenlake_request(
        ctx,
        "DELETE",
        path,
    )


@tool(
    name="greenlake_get_authorization_v1beta1_role_assignments",
    description="GET /authorization/v1beta1/role-assignments\n\ngetRoleAssignmentsV1beta1\n\nRetrieve all role assignments",
    capability=Capability.READ,
)
async def greenlake_get_authorization_v1beta1_role_assignments(
    ctx: Context,
    limit: Annotated[int | None, Field(default=None, description="Total number of results to be returned")] = None,
    offset: Annotated[
        int | None, Field(default=None, description="Zero-based resource offset to start the response from")
    ] = None,
    filter: Annotated[
        str | None,
        Field(
            default=None,
            description="The filter query parameter is used to filter the set of resources returned in a collection-level GET. The returned set of resources matches the criteria in the filter query parameter. <br><br>Supports `in` and `and` operators on `role`, `scope` and `principal` attributes.",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if limit is not None:
        query_params["limit"] = limit
    if offset is not None:
        query_params["offset"] = offset
    if filter is not None:
        query_params["filter"] = filter
    return await greenlake_request(
        ctx,
        "GET",
        "/authorization/v1beta1/role-assignments",
        query_params=query_params or None,
    )


@tool(
    name="greenlake_get_authorization_v1beta1_role_assignments_id",
    description="GET /authorization/v1beta1/role-assignments/{id}\n\ngetRoleAssignmentV1beta1\n\nRetrieve a role assignment instance by ID",
    capability=Capability.READ,
)
async def greenlake_get_authorization_v1beta1_role_assignments_id(
    ctx: Context,
    id: Annotated[str, Field(description="path parameter 'id'")],
) -> Any:
    path = f"/authorization/v1beta1/role-assignments/{path_seg(id)}"
    return await greenlake_request(
        ctx,
        "GET",
        path,
    )


@tool(
    name="greenlake_post_authorization_v1beta1_role_assignments",
    description="POST /authorization/v1beta1/role-assignments\n\ncreateRoleAssignmentV1beta1\n\nCreate a role assignment",
    capability=Capability.WRITE,
)
async def greenlake_post_authorization_v1beta1_role_assignments(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await greenlake_request(
        ctx,
        "POST",
        "/authorization/v1beta1/role-assignments",
        body=body,
    )


@tool(
    name="greenlake_put_authorization_v1beta1_role_assignments_id",
    description="PUT /authorization/v1beta1/role-assignments/{id}\n\nupdateRoleAssignmentV1beta1\n\nUpdate a role assignment instance by ID",
    capability=Capability.WRITE,
)
async def greenlake_put_authorization_v1beta1_role_assignments_id(
    ctx: Context,
    id: Annotated[str, Field(description="path parameter 'id'")],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    path = f"/authorization/v1beta1/role-assignments/{path_seg(id)}"
    return await greenlake_request(
        ctx,
        "PUT",
        path,
        body=body,
    )
