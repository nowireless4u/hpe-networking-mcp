"""Generated GreenLake tools — DO NOT EDIT BY HAND.

Generated from the vendored spec ``vendor/greenlake/scim.json`` by the
maintainer-local GreenLake generator. These modules are committed and are the
runtime source of truth; regeneration is a release-time maintainer workflow
(the generator is intentionally not committed — see ``.gitignore``).

Service: ``scim``   Tag: ``scim_v2beta1``   Operations: 12
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
    name="greenlake_delete_identity_v2beta1_scim_v2_groups_group_id",
    description="DELETE /identity/v2beta1/scim/v2/Groups/{groupId}\n\ndeleteGroupSCIM\n\nDelete a user group",
    capability=Capability.WRITE_DELETE,
)
async def greenlake_delete_identity_v2beta1_scim_v2_groups_group_id(
    ctx: Context,
    groupId: Annotated[
        str,
        Field(
            description="The HPE GreenLake user group ID. Retrieve the ID from the `CREATE Group` endpoint or the `GET Group` endpoint."
        ),
    ],
) -> Any:
    path = f"/identity/v2beta1/scim/v2/Groups/{path_seg(groupId)}"
    return await greenlake_request(
        ctx,
        "DELETE",
        path,
    )


@tool(
    name="greenlake_delete_identity_v2beta1_scim_v2_users_user_id",
    description="DELETE /identity/v2beta1/scim/v2/Users/{userId}\n\ndeleteUserSCIM\n\nDelete a user",
    capability=Capability.WRITE_DELETE,
)
async def greenlake_delete_identity_v2beta1_scim_v2_users_user_id(
    ctx: Context,
    userId: Annotated[
        str,
        Field(
            description="The HPE GreenLake global user ID. Retrieve the ID from the `CREATE User` endpoint or the `GET User` endpoint."
        ),
    ],
) -> Any:
    path = f"/identity/v2beta1/scim/v2/Users/{path_seg(userId)}"
    return await greenlake_request(
        ctx,
        "DELETE",
        path,
    )


@tool(
    name="greenlake_get_identity_v2beta1_scim_v2_extensions_groups_group_id_users",
    description="GET /identity/v2beta1/scim/v2/extensions/Groups/{groupId}/users\n\ngroupMembersSCIM\n\nList users assigned to a user group",
    capability=Capability.READ,
)
async def greenlake_get_identity_v2beta1_scim_v2_extensions_groups_group_id_users(
    ctx: Context,
    groupId: Annotated[
        str,
        Field(
            description="The HPE GreenLake user group ID. Retrieve the ID from the `CREATE Group` endpoint or the `GET Group` endpoint."
        ),
    ],
    count: Annotated[
        int | None,
        Field(
            default=None, description="Specifies the number of query results to be returned in a query response page."
        ),
    ] = None,
    startIndex: Annotated[
        int | None, Field(default=None, description="Specifies the pagination start index. Index starts at 1.")
    ] = None,
) -> Any:
    path = f"/identity/v2beta1/scim/v2/extensions/Groups/{path_seg(groupId)}/users"
    query_params: dict[str, Any] = {}
    if count is not None:
        query_params["count"] = count
    if startIndex is not None:
        query_params["startIndex"] = startIndex
    return await greenlake_request(
        ctx,
        "GET",
        path,
        query_params=query_params or None,
    )


@tool(
    name="greenlake_get_identity_v2beta1_scim_v2_extensions_users_user_id_groups",
    description="GET /identity/v2beta1/scim/v2/extensions/Users/{userId}/groups\n\nuserGroupMembersSCIM\n\nList user groups assigned to a user",
    capability=Capability.READ,
)
async def greenlake_get_identity_v2beta1_scim_v2_extensions_users_user_id_groups(
    ctx: Context,
    userId: Annotated[
        str,
        Field(
            description="The HPE GreenLake global user ID. Retrieve the ID from the `CREATE User` endpoint or the `GET User` endpoint."
        ),
    ],
    count: Annotated[
        int | None,
        Field(
            default=None, description="Specifies the number of query results to be returned in a query response page."
        ),
    ] = None,
    startIndex: Annotated[
        int | None, Field(default=None, description="Specifies the pagination start index. Index starts at 1.")
    ] = None,
) -> Any:
    path = f"/identity/v2beta1/scim/v2/extensions/Users/{path_seg(userId)}/groups"
    query_params: dict[str, Any] = {}
    if count is not None:
        query_params["count"] = count
    if startIndex is not None:
        query_params["startIndex"] = startIndex
    return await greenlake_request(
        ctx,
        "GET",
        path,
        query_params=query_params or None,
    )


@tool(
    name="greenlake_get_identity_v2beta1_scim_v2_groups",
    description="GET /identity/v2beta1/scim/v2/Groups\n\nlistGroupsSCIM\n\nList user groups",
    capability=Capability.READ,
)
async def greenlake_get_identity_v2beta1_scim_v2_groups(
    ctx: Context,
    filter: Annotated[
        str | None,
        Field(
            default=None,
            description="Return only the subset of groups that match the filter.  The filter grammar is a subset of OData 4.0. <br><br>**NOTE:** The filter query parameter must use [URL encoding](https://en.wikipedia.org/wiki/URL_encoding). Most clients do this automatically with inputs provided to them specifically as query parameters. Encoding must be done manually for any query parameters provided as part of the URL. The reserved characters `!` `#` `$` `&` `'` `(` `)` `*` `+` `,` `/` `:` `;` `=` `?` `@` `[` `]` must be encoded with percent encoded equivalents. <br><br>  **The Get Groups API filters enabled are**:  Supported filters: - `displayName` (operators: `sw`, `eq`, `co`) - `urn:ietf:params:scim:schemas:extensions:hpe-greenlake:2.0:Group:source` (operators: `eq`)",
        ),
    ] = None,
    count: Annotated[int | None, Field(default=None, description="Number of results to return in a page.")] = None,
    startIndex: Annotated[
        int | None, Field(default=None, description="Specifies the pagination start index. Index starts at 1.")
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if filter is not None:
        query_params["filter"] = filter
    if count is not None:
        query_params["count"] = count
    if startIndex is not None:
        query_params["startIndex"] = startIndex
    return await greenlake_request(
        ctx,
        "GET",
        "/identity/v2beta1/scim/v2/Groups",
        query_params=query_params or None,
    )


@tool(
    name="greenlake_get_identity_v2beta1_scim_v2_groups_group_id",
    description="GET /identity/v2beta1/scim/v2/Groups/{groupId}\n\ngetGroupSCIM\n\nGet a user group",
    capability=Capability.READ,
)
async def greenlake_get_identity_v2beta1_scim_v2_groups_group_id(
    ctx: Context,
    groupId: Annotated[
        str,
        Field(
            description="The HPE GreenLake user group ID. Retrieve the ID from the `CREATE Group` endpoint or the `GET Group` endpoint."
        ),
    ],
) -> Any:
    path = f"/identity/v2beta1/scim/v2/Groups/{path_seg(groupId)}"
    return await greenlake_request(
        ctx,
        "GET",
        path,
    )


@tool(
    name="greenlake_get_identity_v2beta1_scim_v2_users",
    description="GET /identity/v2beta1/scim/v2/Users\n\nlistUsersSCIM\n\nList users",
    capability=Capability.READ,
)
async def greenlake_get_identity_v2beta1_scim_v2_users(
    ctx: Context,
    filter: Annotated[
        str | None,
        Field(
            default=None,
            description="Return only the subset of users that match the filter.  The filter grammar is a subset of OData 4.0. <br><br>**NOTE:** The filter query parameter must use [URL encoding](https://en.wikipedia.org/wiki/URL_encoding). Most clients do this automatically with inputs provided to them specifically as query parameters. Encoding must be done manually for any query parameters provided as part of the URL. The reserved characters `!` `#` `$` `&` `'` `(` `)` `*` `+` `,` `/` `:` `;` `=` `?` `@` `[` `]` must be encoded with percent encoded equivalents. <br><br>  **The Get Users API filters enabled are**: - displayName - userName  **Supported operators**: - sw (starts with) - eq (equals) - co (contains)",
        ),
    ] = None,
    count: Annotated[
        int | None,
        Field(
            default=None, description="Specifies the number of query results to be returned in a query response page."
        ),
    ] = None,
    startIndex: Annotated[
        int | None, Field(default=None, description="Specifies the pagination start index. Index starts at 1.")
    ] = None,
    sortBy: Annotated[
        str | None, Field(default=None, description="Specifies the attribute to sort the returned results by.")
    ] = None,
    sortOrder: Annotated[str | None, Field(default=None, description="Specifies the sort order.")] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if filter is not None:
        query_params["filter"] = filter
    if count is not None:
        query_params["count"] = count
    if startIndex is not None:
        query_params["startIndex"] = startIndex
    if sortBy is not None:
        query_params["sortBy"] = sortBy
    if sortOrder is not None:
        query_params["sortOrder"] = sortOrder
    return await greenlake_request(
        ctx,
        "GET",
        "/identity/v2beta1/scim/v2/Users",
        query_params=query_params or None,
    )


@tool(
    name="greenlake_get_identity_v2beta1_scim_v2_users_user_id",
    description="GET /identity/v2beta1/scim/v2/Users/{userId}\n\ngetUserSCIM\n\nGet a user",
    capability=Capability.READ,
)
async def greenlake_get_identity_v2beta1_scim_v2_users_user_id(
    ctx: Context,
    userId: Annotated[
        str,
        Field(
            description="The HPE GreenLake global user ID. Retrieve the ID from the `CREATE User` endpoint or the `GET User` endpoint."
        ),
    ],
) -> Any:
    path = f"/identity/v2beta1/scim/v2/Users/{path_seg(userId)}"
    return await greenlake_request(
        ctx,
        "GET",
        path,
    )


@tool(
    name="greenlake_patch_identity_v2beta1_scim_v2_groups_group_id",
    description="PATCH /identity/v2beta1/scim/v2/Groups/{groupId}\n\npatchGroupSCIM\n\nUpdate user group",
    capability=Capability.WRITE,
)
async def greenlake_patch_identity_v2beta1_scim_v2_groups_group_id(
    ctx: Context,
    groupId: Annotated[
        str,
        Field(
            description="The HPE GreenLake user group ID. Retrieve the ID from the `CREATE Group` endpoint or the `GET Group` endpoint."
        ),
    ],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    path = f"/identity/v2beta1/scim/v2/Groups/{path_seg(groupId)}"
    return await greenlake_request(
        ctx,
        "PATCH",
        path,
        body=body,
    )


@tool(
    name="greenlake_patch_identity_v2beta1_scim_v2_users_user_id",
    description="PATCH /identity/v2beta1/scim/v2/Users/{userId}\n\npatchUserSCIM\n\nPatch user attributes",
    capability=Capability.WRITE,
)
async def greenlake_patch_identity_v2beta1_scim_v2_users_user_id(
    ctx: Context,
    userId: Annotated[
        str,
        Field(
            description="The HPE GreenLake global user ID. Retrieve the ID from the `CREATE User` endpoint or the `GET User` endpoint."
        ),
    ],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    path = f"/identity/v2beta1/scim/v2/Users/{path_seg(userId)}"
    return await greenlake_request(
        ctx,
        "PATCH",
        path,
        body=body,
    )


@tool(
    name="greenlake_post_identity_v2beta1_scim_v2_groups",
    description="POST /identity/v2beta1/scim/v2/Groups\n\ncreateGroupSCIM\n\nCreate a user group",
    capability=Capability.WRITE,
)
async def greenlake_post_identity_v2beta1_scim_v2_groups(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await greenlake_request(
        ctx,
        "POST",
        "/identity/v2beta1/scim/v2/Groups",
        body=body,
    )


@tool(
    name="greenlake_post_identity_v2beta1_scim_v2_users",
    description="POST /identity/v2beta1/scim/v2/Users\n\ncreateUserSCIM\n\nCreate a user",
    capability=Capability.WRITE,
)
async def greenlake_post_identity_v2beta1_scim_v2_users(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await greenlake_request(
        ctx,
        "POST",
        "/identity/v2beta1/scim/v2/Users",
        body=body,
    )
