"""Generated GreenLake tools — DO NOT EDIT BY HAND.

Generated from the vendored spec ``vendor/greenlake/block-storage.json`` by the
maintainer-local GreenLake generator. These modules are committed and are the
runtime source of truth; regeneration is a release-time maintainer workflow
(the generator is intentionally not committed — see ``.gitignore``).

Service: ``block-storage``   Tag: ``host_initiator_groups``   Operations: 6
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
    name="greenlake_delete_block_storage_v1alpha1_host_initiator_groups_host_group_id",
    description="DELETE /block-storage/v1alpha1/host-initiator-groups/{hostGroupId}\n\nHostGroupDelete\n\nDelete a host group by {hostGroupId}",
    capability=Capability.WRITE_DELETE,
)
async def greenlake_delete_block_storage_v1alpha1_host_initiator_groups_host_group_id(
    ctx: Context,
    hostGroupId: Annotated[str, Field(description="Id of the host Group.")],
    force: Annotated[bool | None, Field(default=None, description="Forceful delete option")] = None,
) -> Any:
    path = f"/block-storage/v1alpha1/host-initiator-groups/{path_seg(hostGroupId)}"
    query_params: dict[str, Any] = {}
    if force is not None:
        query_params["force"] = force
    return await greenlake_request(
        ctx,
        "DELETE",
        path,
        query_params=query_params or None,
    )


@tool(
    name="greenlake_get_block_storage_v1alpha1_host_initiator_groups",
    description="GET /block-storage/v1alpha1/host-initiator-groups\n\nHostGroupList\n\nGet the list of host groups",
    capability=Capability.READ,
)
async def greenlake_get_block_storage_v1alpha1_host_initiator_groups(
    ctx: Context,
    filter: Annotated[str | None, Field(default=None, description="oData query to filter hostservice by Key.")] = None,
    sort: Annotated[str | None, Field(default=None, description="oData query to sort hostservice by Key.")] = None,
    limit: Annotated[int | None, Field(default=None, description="Number of items to return at a time")] = None,
    offset: Annotated[
        int | None, Field(default=None, description="The offset of the first item in the collection to return")
    ] = None,
    select: Annotated[
        str | None,
        Field(default=None, description="Query to select only the required parameters, separated by . if nested"),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if filter is not None:
        query_params["filter"] = filter
    if sort is not None:
        query_params["sort"] = sort
    if limit is not None:
        query_params["limit"] = limit
    if offset is not None:
        query_params["offset"] = offset
    if select is not None:
        query_params["select"] = select
    return await greenlake_request(
        ctx,
        "GET",
        "/block-storage/v1alpha1/host-initiator-groups",
        query_params=query_params or None,
    )


@tool(
    name="greenlake_get_block_storage_v1alpha1_host_initiator_groups_host_group_id",
    description="GET /block-storage/v1alpha1/host-initiator-groups/{hostGroupId}\n\nHostGroupGetById\n\nGet the host group details by {hostGroupId}",
    capability=Capability.READ,
)
async def greenlake_get_block_storage_v1alpha1_host_initiator_groups_host_group_id(
    ctx: Context,
    hostGroupId: Annotated[str, Field(description="Id of the host Group.")],
) -> Any:
    path = f"/block-storage/v1alpha1/host-initiator-groups/{path_seg(hostGroupId)}"
    return await greenlake_request(
        ctx,
        "GET",
        path,
    )


@tool(
    name="greenlake_get_block_storage_v1alpha1_host_initiator_groups_host_group_id_mapped_devices",
    description="GET /block-storage/v1alpha1/host-initiator-groups/{hostGroupId}/mapped-devices\n\nHostGroupMappedDevice\n\nGet details of a host group identified by {hostGroupId} across its associated systems",
    capability=Capability.READ,
)
async def greenlake_get_block_storage_v1alpha1_host_initiator_groups_host_group_id_mapped_devices(
    ctx: Context,
    hostGroupId: Annotated[str, Field(description="Id of the host Group.")],
) -> Any:
    path = f"/block-storage/v1alpha1/host-initiator-groups/{path_seg(hostGroupId)}/mapped-devices"
    return await greenlake_request(
        ctx,
        "GET",
        path,
    )


@tool(
    name="greenlake_post_block_storage_v1alpha1_host_initiator_groups",
    description="POST /block-storage/v1alpha1/host-initiator-groups\n\nHostGroupCreate\n\nCreate a host group",
    capability=Capability.WRITE,
)
async def greenlake_post_block_storage_v1alpha1_host_initiator_groups(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await greenlake_request(
        ctx,
        "POST",
        "/block-storage/v1alpha1/host-initiator-groups",
        body=body,
    )


@tool(
    name="greenlake_put_block_storage_v1alpha1_host_initiator_groups_host_group_id",
    description="PUT /block-storage/v1alpha1/host-initiator-groups/{hostGroupId}\n\nHostGroupUpdateById\n\nUpdate host group by {hostGroupId}",
    capability=Capability.WRITE,
)
async def greenlake_put_block_storage_v1alpha1_host_initiator_groups_host_group_id(
    ctx: Context,
    hostGroupId: Annotated[str, Field(description="Id of the host Group.")],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    path = f"/block-storage/v1alpha1/host-initiator-groups/{path_seg(hostGroupId)}"
    return await greenlake_request(
        ctx,
        "PUT",
        path,
        body=body,
    )
