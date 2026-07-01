"""Generated GreenLake tools — DO NOT EDIT BY HAND.

Generated from the vendored spec ``vendor/greenlake/identity__identity-v1-nb-openapi-identity.json`` by the
maintainer-local GreenLake generator. These modules are committed and are the
runtime source of truth; regeneration is a release-time maintainer workflow
(the generator is intentionally not committed — see ``.gitignore``).

Service: ``identity``   Tag: ``nb_api_user``   Operations: 5
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
    name="greenlake_delete_identity_v1_users_id",
    description="DELETE /identity/v1/users/{id}\n\ndisassociate_platform_user_identity_v1_users__id__delete\n\nDisassociate a user",
    capability=Capability.WRITE_DELETE,
)
async def greenlake_delete_identity_v1_users_id(
    ctx: Context,
    id: Annotated[str, Field(description="The unique identifier of the user to be deleted.")],
) -> Any:
    path = f"/identity/v1/users/{path_seg(id)}"
    return await greenlake_request(
        ctx,
        "DELETE",
        path,
    )


@tool(
    name="greenlake_get_identity_v1_users",
    description="GET /identity/v1/users\n\nget_users_identity_v1_users_get\n\nGet users",
    capability=Capability.READ,
)
async def greenlake_get_identity_v1_users(
    ctx: Context,
    filter: Annotated[
        str | None,
        Field(
            default=None,
            description="Filter data using a subset of OData 4.0 and return only the subset of resources that match the filter.  Supported classes and examples include: - **Types**: timestamp, string - **Comparison**: eq, ne, gt, ge, lt - **Logical Expressions**: and, or, not  The Get users API can be filtered by: - id - username - firstName - lastName - userStatus - createdAt - updatedAt - lastLogin  userStatus can be one of the following: - UNVERIFIED - VERIFIED - BLOCKED - DELETE_IN_PROGRESS - DELETED - SUSPENDED  **Note**: The userStatus filter is case-sensitive.",
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
            description="Specify the maximum number of entries per page. NOTE: The maximum value accepted is 600.",
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
        "/identity/v1/users",
        query_params=query_params or None,
    )


@tool(
    name="greenlake_get_identity_v1_users_id",
    description="GET /identity/v1/users/{id}\n\nget_user_detailed_identity_v1_users__id__get\n\nGet a user",
    capability=Capability.READ,
)
async def greenlake_get_identity_v1_users_id(
    ctx: Context,
    id: Annotated[str, Field(description="The unique identifier of the user.")],
) -> Any:
    path = f"/identity/v1/users/{path_seg(id)}"
    return await greenlake_request(
        ctx,
        "GET",
        path,
    )


@tool(
    name="greenlake_post_identity_v1_users",
    description="POST /identity/v1/users\n\ninvite_user_to_account_identity_v1_users_post\n\nInvite a user",
    capability=Capability.WRITE,
)
async def greenlake_post_identity_v1_users(
    ctx: Context,
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request body")] = None,
) -> Any:
    return await greenlake_request(
        ctx,
        "POST",
        "/identity/v1/users",
        body=body,
    )


@tool(
    name="greenlake_put_identity_v1_users_id",
    description="PUT /identity/v1/users/{id}\n\nupdate_user_preferences_identity_v1_users__id__put\n\nUpdate a user",
    capability=Capability.WRITE,
)
async def greenlake_put_identity_v1_users_id(
    ctx: Context,
    id: Annotated[str, Field(description="The unique identifier of the user to be updated.")],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    path = f"/identity/v1/users/{path_seg(id)}"
    return await greenlake_request(
        ctx,
        "PUT",
        path,
        body=body,
    )
