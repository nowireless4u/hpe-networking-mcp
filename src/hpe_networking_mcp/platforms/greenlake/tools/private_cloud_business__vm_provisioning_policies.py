"""Generated GreenLake tools — DO NOT EDIT BY HAND.

Generated from the vendored spec ``vendor/greenlake/private-cloud-business.json`` by the
maintainer-local GreenLake generator. These modules are committed and are the
runtime source of truth; regeneration is a release-time maintainer workflow
(the generator is intentionally not committed — see ``.gitignore``).

Service: ``private-cloud-business``   Tag: ``vm_provisioning_policies``   Operations: 5
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
    name="greenlake_delete_private_cloud_business_v1beta1_vm_provisioning_policies_id",
    description="DELETE /private-cloud-business/v1beta1/vm-provisioning-policies/{id}\n\nVMProvisioningPolicyDelete\n\nDelete VM provisioning policy by policy id",
    capability=Capability.WRITE_DELETE,
)
async def greenlake_delete_private_cloud_business_v1beta1_vm_provisioning_policies_id(
    ctx: Context,
    id: Annotated[str, Field(description="Unique identifier of a VM provisioning policy")],
) -> Any:
    path = f"/private-cloud-business/v1beta1/vm-provisioning-policies/{path_seg(id)}"
    return await greenlake_request(
        ctx,
        "DELETE",
        path,
    )


@tool(
    name="greenlake_get_private_cloud_business_v1beta1_vm_provisioning_policies",
    description="GET /private-cloud-business/v1beta1/vm-provisioning-policies\n\nVMProvisioningPoliciesList\n\nGet a list of VM provisioning policies",
    capability=Capability.READ,
)
async def greenlake_get_private_cloud_business_v1beta1_vm_provisioning_policies(
    ctx: Context,
    offset: Annotated[
        int | None,
        Field(
            default=None,
            description='The number of items to omit from the beginning of the result set. Use offset in conjunction with limit for pagination.  For example,  "offset=30&limit=10" indicates the fourth page of 10 items.',
        ),
    ] = None,
    limit: Annotated[
        int | None,
        Field(
            default=None,
            description='The maximum number of items to include in the response. Use offset in conjunction with limit for pagination.  For example, "offset=30&limit=10" indicates the fourth page of 10 items.',
        ),
    ] = None,
    filter: Annotated[
        str | None,
        Field(
            default=None,
            description="An expression to filter the results. Filtering is supported with following attributes:  * name  * id   * timestamp  * clusterid  * deduplication  * allFlash  * encryption.cipher  * associatedvmid  * associatedvmname",
        ),
    ] = None,
    sort: Annotated[
        str | None,
        Field(
            default=None,
            description='A comma separated list of properties to sort by, followed by a direction indicator ("asc" or "desc").',
        ),
    ] = None,
    select: Annotated[
        str | None, Field(default=None, description="A list of properties to include in the response.")
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if offset is not None:
        query_params["offset"] = offset
    if limit is not None:
        query_params["limit"] = limit
    if filter is not None:
        query_params["filter"] = filter
    if sort is not None:
        query_params["sort"] = sort
    if select is not None:
        query_params["select"] = select
    return await greenlake_request(
        ctx,
        "GET",
        "/private-cloud-business/v1beta1/vm-provisioning-policies",
        query_params=query_params or None,
    )


@tool(
    name="greenlake_get_private_cloud_business_v1beta1_vm_provisioning_policies_id",
    description="GET /private-cloud-business/v1beta1/vm-provisioning-policies/{id}\n\nVMProvisioningPolicy\n\nGet VM provisioning policy by policy id",
    capability=Capability.READ,
)
async def greenlake_get_private_cloud_business_v1beta1_vm_provisioning_policies_id(
    ctx: Context,
    id: Annotated[str, Field(description="Unique identifier of a VM provisioning policy")],
) -> Any:
    path = f"/private-cloud-business/v1beta1/vm-provisioning-policies/{path_seg(id)}"
    return await greenlake_request(
        ctx,
        "GET",
        path,
    )


@tool(
    name="greenlake_patch_private_cloud_business_v1beta1_vm_provisioning_policies_id",
    description="PATCH /private-cloud-business/v1beta1/vm-provisioning-policies/{id}\n\nVMProvisioningPolicyEdit\n\nUpdate VM provisioning policy by policy id",
    capability=Capability.WRITE,
)
async def greenlake_patch_private_cloud_business_v1beta1_vm_provisioning_policies_id(
    ctx: Context,
    id: Annotated[str, Field(description="Unique identifier of a VM provisioning policy")],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    path = f"/private-cloud-business/v1beta1/vm-provisioning-policies/{path_seg(id)}"
    return await greenlake_request(
        ctx,
        "PATCH",
        path,
        body=body,
    )


@tool(
    name="greenlake_post_private_cloud_business_v1beta1_vm_provisioning_policies",
    description="POST /private-cloud-business/v1beta1/vm-provisioning-policies\n\nVMProvisioningPolicyCreate\n\nCreate VM provisioning policy",
    capability=Capability.WRITE,
)
async def greenlake_post_private_cloud_business_v1beta1_vm_provisioning_policies(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await greenlake_request(
        ctx,
        "POST",
        "/private-cloud-business/v1beta1/vm-provisioning-policies",
        body=body,
    )
