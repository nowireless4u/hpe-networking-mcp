"""Generated GreenLake tools — DO NOT EDIT BY HAND.

Generated from the vendored spec ``vendor/greenlake/object-storage.json`` by the
maintainer-local GreenLake generator. These modules are committed and are the
runtime source of truth; regeneration is a release-time maintainer workflow
(the generator is intentionally not committed — see ``.gitignore``).

Service: ``object-storage``   Tag: ``groups``   Operations: 5
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
    name="greenlake_delete_object_storage_v1alpha1_devtype7_storage_systems_system_id_groups_group_id",
    description="DELETE /object-storage/v1alpha1/devtype7-storage-systems/{systemId}/groups/{groupId}\n\nDeviceType7DeleteGroupById\n\nDelete group from HPE Alletra Storage MP X10000 ObjectStore",
    capability=Capability.WRITE_DELETE,
)
async def greenlake_delete_object_storage_v1alpha1_devtype7_storage_systems_system_id_groups_group_id(
    ctx: Context,
    systemId: Annotated[str, Field(description="A unique identifier assigned to each object service device")],
    groupId: Annotated[str, Field(description="A unique identifier assigned to each group created in the ObjectStore")],
) -> Any:
    path = f"/object-storage/v1alpha1/devtype7-storage-systems/{path_seg(systemId)}/groups/{path_seg(groupId)}"
    return await greenlake_request(
        ctx,
        "DELETE",
        path,
    )


@tool(
    name="greenlake_get_object_storage_v1alpha1_devtype7_storage_systems_system_id_groups",
    description="GET /object-storage/v1alpha1/devtype7-storage-systems/{systemId}/groups\n\nDeviceType7ListGroups\n\nGet all groups for HPE Alletra Storage MP X10000 ObjectStore",
    capability=Capability.READ,
)
async def greenlake_get_object_storage_v1alpha1_devtype7_storage_systems_system_id_groups(
    ctx: Context,
    systemId: Annotated[str, Field(description="A unique identifier assigned to each object service device")],
    limit: Annotated[int | None, Field(default=None, description="Number of items to return at a time")] = None,
    offset: Annotated[
        int | None, Field(default=None, description="The offset of the first item in the collection to return")
    ] = None,
    select: Annotated[
        str | None,
        Field(
            default=None,
            description="A query to retrieve only the specified parameters. Use . to denote nested fields.",
        ),
    ] = None,
    filter: Annotated[str | None, Field(default=None, description="oData query to filter bucket by Key.")] = None,
    sort: Annotated[
        str | None,
        Field(
            default=None,
            description="A list of properties defining the sort order. This takes a single property name followed by the direction to sort in, separated by a space. The supported properties are `systemUid` and `generation`. If not specified, the default behaviour is to sort by `generation`. The supported directions are `asc` and `desc` for ascending and descending respectively.",
        ),
    ] = None,
) -> Any:
    path = f"/object-storage/v1alpha1/devtype7-storage-systems/{path_seg(systemId)}/groups"
    query_params: dict[str, Any] = {}
    if limit is not None:
        query_params["limit"] = limit
    if offset is not None:
        query_params["offset"] = offset
    if select is not None:
        query_params["select"] = select
    if filter is not None:
        query_params["filter"] = filter
    if sort is not None:
        query_params["sort"] = sort
    return await greenlake_request(
        ctx,
        "GET",
        path,
        query_params=query_params or None,
    )


@tool(
    name="greenlake_get_object_storage_v1alpha1_devtype7_storage_systems_system_id_groups_group_id",
    description="GET /object-storage/v1alpha1/devtype7-storage-systems/{systemId}/groups/{groupId}\n\nDeviceType7GetGroupById\n\nGet single group details for HPE Alletra Storage MP X10000 ObjectStore",
    capability=Capability.READ,
)
async def greenlake_get_object_storage_v1alpha1_devtype7_storage_systems_system_id_groups_group_id(
    ctx: Context,
    groupId: Annotated[str, Field(description="A unique identifier assigned to each group created in the ObjectStore")],
    systemId: Annotated[str, Field(description="A unique identifier assigned to each object service device")],
    select: Annotated[
        str | None,
        Field(
            default=None,
            description="A query to retrieve only the specified parameters. Use . to denote nested fields.",
        ),
    ] = None,
) -> Any:
    path = f"/object-storage/v1alpha1/devtype7-storage-systems/{path_seg(systemId)}/groups/{path_seg(groupId)}"
    query_params: dict[str, Any] = {}
    if select is not None:
        query_params["select"] = select
    return await greenlake_request(
        ctx,
        "GET",
        path,
        query_params=query_params or None,
    )


@tool(
    name="greenlake_post_object_storage_v1alpha1_devtype7_storage_systems_system_id_groups",
    description="POST /object-storage/v1alpha1/devtype7-storage-systems/{systemId}/groups\n\nDeviceType7CreateGroup\n\nCreate new group in HPE Alletra Storage MP X10000 ObjectStore",
    capability=Capability.WRITE,
)
async def greenlake_post_object_storage_v1alpha1_devtype7_storage_systems_system_id_groups(
    ctx: Context,
    systemId: Annotated[str, Field(description="A unique identifier assigned to each object service device")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request body")] = None,
) -> Any:
    path = f"/object-storage/v1alpha1/devtype7-storage-systems/{path_seg(systemId)}/groups"
    return await greenlake_request(
        ctx,
        "POST",
        path,
        body=body,
    )


@tool(
    name="greenlake_put_object_storage_v1alpha1_devtype7_storage_systems_system_id_groups_group_id",
    description="PUT /object-storage/v1alpha1/devtype7-storage-systems/{systemId}/groups/{groupId}\n\nDeviceType7UpdateGroupById\n\nUpdate group details in HPE Alletra Storage MP X10000 ObjectStore",
    capability=Capability.WRITE,
)
async def greenlake_put_object_storage_v1alpha1_devtype7_storage_systems_system_id_groups_group_id(
    ctx: Context,
    systemId: Annotated[str, Field(description="A unique identifier assigned to each object service device")],
    groupId: Annotated[str, Field(description="A unique identifier assigned to each group created in the ObjectStore")],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    path = f"/object-storage/v1alpha1/devtype7-storage-systems/{path_seg(systemId)}/groups/{path_seg(groupId)}"
    return await greenlake_request(
        ctx,
        "PUT",
        path,
        body=body,
    )
