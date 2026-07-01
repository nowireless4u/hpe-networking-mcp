"""Generated GreenLake tools — DO NOT EDIT BY HAND.

Generated from the vendored spec ``vendor/greenlake/object-storage.json`` by the
maintainer-local GreenLake generator. These modules are committed and are the
runtime source of truth; regeneration is a release-time maintainer workflow
(the generator is intentionally not committed — see ``.gitignore``).

Service: ``object-storage``   Tag: ``access_policies``   Operations: 6
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
    name="greenlake_delete_object_storage_v1alpha1_devtype7_storage_systems_system_id_access_policies_policy_id",
    description="DELETE /object-storage/v1alpha1/devtype7-storage-systems/{systemId}/access-policies/{policyId}\n\nDeviceType7DeleteAccessPolicyById\n\nDelete HPE Alletra Storage MP X10000 ObjectStore access policy",
    capability=Capability.WRITE_DELETE,
)
async def greenlake_delete_object_storage_v1alpha1_devtype7_storage_systems_system_id_access_policies_policy_id(
    ctx: Context,
    systemId: Annotated[str, Field(description="A unique identifier assigned to each object service device")],
    policyId: Annotated[
        str, Field(description="A unique identifier assigned to each access policy created in the ObjectStore")
    ],
) -> Any:
    path = (
        f"/object-storage/v1alpha1/devtype7-storage-systems/{path_seg(systemId)}/access-policies/{path_seg(policyId)}"
    )
    return await greenlake_request(
        ctx,
        "DELETE",
        path,
    )


@tool(
    name="greenlake_get_object_storage_v1alpha1_devtype7_storage_systems_system_id_access_policies",
    description="GET /object-storage/v1alpha1/devtype7-storage-systems/{systemId}/access-policies\n\nDeviceType7ListAccessPolicies\n\nGet all access policies for HPE Alletra Storage MP X10000 ObjectStore",
    capability=Capability.READ,
)
async def greenlake_get_object_storage_v1alpha1_devtype7_storage_systems_system_id_access_policies(
    ctx: Context,
    systemId: Annotated[str, Field(description="A unique identifier assigned to each object service device")],
    filter: Annotated[str | None, Field(default=None, description="oData query to filter bucket by Key.")] = None,
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
    sort: Annotated[
        str | None,
        Field(
            default=None,
            description="A list of properties defining the sort order. This takes a single property name followed by the direction to sort in, separated by a space. The supported properties are `id`, `systemUid` and `generation`. If not specified, the default behaviour is to sort by `generation`. The supported directions are `asc` and `desc` for ascending and descending respectively.",
        ),
    ] = None,
) -> Any:
    path = f"/object-storage/v1alpha1/devtype7-storage-systems/{path_seg(systemId)}/access-policies"
    query_params: dict[str, Any] = {}
    if filter is not None:
        query_params["filter"] = filter
    if limit is not None:
        query_params["limit"] = limit
    if offset is not None:
        query_params["offset"] = offset
    if select is not None:
        query_params["select"] = select
    if sort is not None:
        query_params["sort"] = sort
    return await greenlake_request(
        ctx,
        "GET",
        path,
        query_params=query_params or None,
    )


@tool(
    name="greenlake_get_object_storage_v1alpha1_devtype7_storage_systems_system_id_access_policies_policy_id",
    description="GET /object-storage/v1alpha1/devtype7-storage-systems/{systemId}/access-policies/{policyId}\n\nDeviceType7GetAccessPolicyById\n\nGet single HPE Alletra Storage MP X10000 ObjectStore access policy",
    capability=Capability.READ,
)
async def greenlake_get_object_storage_v1alpha1_devtype7_storage_systems_system_id_access_policies_policy_id(
    ctx: Context,
    systemId: Annotated[str, Field(description="A unique identifier assigned to each object service device")],
    policyId: Annotated[
        str, Field(description="A unique identifier assigned to each access policy created in the ObjectStore")
    ],
    select: Annotated[
        str | None,
        Field(
            default=None,
            description="A query to retrieve only the specified parameters. Use . to denote nested fields.",
        ),
    ] = None,
) -> Any:
    path = (
        f"/object-storage/v1alpha1/devtype7-storage-systems/{path_seg(systemId)}/access-policies/{path_seg(policyId)}"
    )
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
    name="greenlake_post_object_storage_v1alpha1_devtype7_storage_systems_system_id_access_policies",
    description="POST /object-storage/v1alpha1/devtype7-storage-systems/{systemId}/access-policies\n\nDeviceType7CreateAccessPolicy\n\nCreate new access policy for HPE Alletra Storage MP X10000 ObjectStore",
    capability=Capability.WRITE,
)
async def greenlake_post_object_storage_v1alpha1_devtype7_storage_systems_system_id_access_policies(
    ctx: Context,
    systemId: Annotated[str, Field(description="A unique identifier assigned to each object service device")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request body")] = None,
) -> Any:
    path = f"/object-storage/v1alpha1/devtype7-storage-systems/{path_seg(systemId)}/access-policies"
    return await greenlake_request(
        ctx,
        "POST",
        path,
        body=body,
    )


@tool(
    name="greenlake_put_object_storage_v1alpha1_devtype7_storage_systems_system_id_access_policies_policy_id",
    description="PUT /object-storage/v1alpha1/devtype7-storage-systems/{systemId}/access-policies/{policyId}\n\nDeviceType7UpdateAccessPolicyById\n\nUpdate HPE Alletra Storage MP X10000 ObjectStore access policy",
    capability=Capability.WRITE,
)
async def greenlake_put_object_storage_v1alpha1_devtype7_storage_systems_system_id_access_policies_policy_id(
    ctx: Context,
    systemId: Annotated[str, Field(description="A unique identifier assigned to each object service device")],
    policyId: Annotated[
        str, Field(description="A unique identifier assigned to each access policy created in the ObjectStore")
    ],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    path = (
        f"/object-storage/v1alpha1/devtype7-storage-systems/{path_seg(systemId)}/access-policies/{path_seg(policyId)}"
    )
    return await greenlake_request(
        ctx,
        "PUT",
        path,
        body=body,
    )


@tool(
    name="greenlake_put_object_storage_v1alpha1_devtype7_storage_systems_system_id_apply_policy",
    description="PUT /object-storage/v1alpha1/devtype7-storage-systems/{systemId}/apply-policy\n\nApplyPolicy\n\nApply policy to existing user or group in HPE Alletra Storage MP X10000 ObjectStore",
    capability=Capability.WRITE,
)
async def greenlake_put_object_storage_v1alpha1_devtype7_storage_systems_system_id_apply_policy(
    ctx: Context,
    systemId: Annotated[str, Field(description="A unique identifier assigned to each object service device")],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    path = f"/object-storage/v1alpha1/devtype7-storage-systems/{path_seg(systemId)}/apply-policy"
    return await greenlake_request(
        ctx,
        "PUT",
        path,
        body=body,
    )
