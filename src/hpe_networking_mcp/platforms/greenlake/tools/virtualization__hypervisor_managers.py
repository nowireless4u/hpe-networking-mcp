"""Generated GreenLake tools — DO NOT EDIT BY HAND.

Generated from the vendored spec ``vendor/greenlake/virtualization.json`` by the
maintainer-local GreenLake generator. These modules are committed and are the
runtime source of truth; regeneration is a release-time maintainer workflow
(the generator is intentionally not committed — see ``.gitignore``).

Service: ``virtualization``   Tag: ``hypervisor_managers``   Operations: 5
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
    name="greenlake_get_virtualization_v1beta1_hypervisor_managers",
    description="GET /virtualization/v1beta1/hypervisor-managers\n\nHypervisorManagerList\n\nGet all registered hypervisor managers.",
    capability=Capability.READ,
)
async def greenlake_get_virtualization_v1beta1_hypervisor_managers(
    ctx: Context,
    offset: Annotated[
        int | None,
        Field(default=None, description="The number of items to skip before starting to collect the result set"),
    ] = None,
    limit: Annotated[int | None, Field(default=None, description="The numbers of items to return")] = None,
    filter: Annotated[
        str | None,
        Field(
            default=None,
            description='The filter query parameter is used to filter the set of resources returned in the response. The returned set of resources must match the criteria in the filter query parameter.  A comparison compares a property name to a literal. The comparisons supported are the following: * “eq” : Is a property equal to value. Valid for number, boolean and string properties. * “ne” : Is a property not equal to value. Valid for number, boolean and string properties. * “gt” : Is a property greater than a value. Valid for number or string timestamp properties. * “lt” : Is a property less than a value. Valid for number or string timestamp properties * “in” : Is a value in a property (that is an array of strings)  Examples: * GET /virtualization/v1beta1/hypervisor-managers?filter="hypervisorManagerType eq VMWARE_VCENTER" * GET /virtualization/v1beta1/hypervisor-managers?filter="hypervisorManagerType eq VMWARE_VCENTER and status eq ERROR"  Filters are supported on the following attributes: * hypervisorManagerType * state * status * releaseVersion * createdAt * name * services * dataOrchestratorInfo/id * username * networkAddress * displayName',
        ),
    ] = None,
    sort: Annotated[
        str | None,
        Field(
            default=None,
            description='A comma separated list of properties to sort by, followed by a direction indicator ("asc" or "desc"). If no direction indicator is specified, the default order is ascending.',
        ),
    ] = None,
    select: Annotated[
        str | None,
        Field(
            default=None,
            description="The select query parameter is used to limit the properties returned with a resource or collection-level GET. Multiple properties can be listed to be returned. The server must only return the set of properties requested by the client. The property “select” is the name of the select query parameter; its value is the list of properties to return separated by commas.",
        ),
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
        "/virtualization/v1beta1/hypervisor-managers",
        query_params=query_params or None,
    )


@tool(
    name="greenlake_get_virtualization_v1beta1_hypervisor_managers_hypervisor_id",
    description="GET /virtualization/v1beta1/hypervisor-managers/{hypervisor-id}\n\nHypervisorManager\n\nGet a hypervisor manager resource identified by {hypervisor-id}.",
    capability=Capability.READ,
)
async def greenlake_get_virtualization_v1beta1_hypervisor_managers_hypervisor_id(
    ctx: Context,
    hypervisor_id: Annotated[str, Field(description="path parameter 'hypervisor-id'")],
) -> Any:
    path = f"/virtualization/v1beta1/hypervisor-managers/{path_seg(hypervisor_id)}"
    return await greenlake_request(
        ctx,
        "GET",
        path,
    )


@tool(
    name="greenlake_get_virtualization_v1beta1_hypervisor_managers_hypervisor_id_hypervisor_library_images",
    description="GET /virtualization/v1beta1/hypervisor-managers/{hypervisor-id}/hypervisor-library-images\n\nListVirtualMachineImages\n\nGet all virtual machine images from the hypervisor library.",
    capability=Capability.READ,
)
async def greenlake_get_virtualization_v1beta1_hypervisor_managers_hypervisor_id_hypervisor_library_images(
    ctx: Context,
    hypervisor_id: Annotated[str, Field(description="path parameter 'hypervisor-id'")],
    offset: Annotated[
        int | None,
        Field(default=None, description="The number of items to skip before starting to collect the result set"),
    ] = None,
    limit: Annotated[int | None, Field(default=None, description="The numbers of items to return")] = None,
    filter: Annotated[
        str | None,
        Field(
            default=None,
            description='The filter query parameter is used to filter the set of resources returned in the response. The returned set of resources must match the criteria in the filter query parameter.  A comparison compares a property name to a literal. The following comparisons are supported: * “eq” : Is a property equal to value. Valid for number, boolean and string properties. * “gt” : Is a property greater than a value. Valid for number or string timestamp properties. * “lt” : Is a property less than a value. Valid for number or string timestamp properties * “in” : Is a value in a property (that is an array of strings)  Examples: * GET /api/v1/hypervisor-managers/{hypervisor-id}/hypervisor-library-images?filter="filetype eq OVF"  Filters are supported on the following attributes: * fileType * name * services * sizeInBytes * subscribed',
        ),
    ] = None,
    sort: Annotated[
        str | None,
        Field(
            default=None,
            description='A comma separated list of properties to sort by, followed by a direction indicator ("asc" or "desc"). If no direction indicator is specified, the default order is ascending.',
        ),
    ] = None,
    select: Annotated[
        str | None,
        Field(
            default=None,
            description="The select query parameter is used to limit the properties returned with a resource or collection-level GET. Multiple properties can be listed to be returned. The server must only return the set of properties requested by the client. The property “select” is the name of the select query parameter; its value is the list of properties to return separated by commas.",
        ),
    ] = None,
) -> Any:
    path = f"/virtualization/v1beta1/hypervisor-managers/{path_seg(hypervisor_id)}/hypervisor-library-images"
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
        path,
        query_params=query_params or None,
    )


@tool(
    name="greenlake_get_virtualization_v1beta1_hypervisor_managers_hypervisor_id_hypervisor_library_images_hypervisor_library_image_id",
    description="GET /virtualization/v1beta1/hypervisor-managers/{hypervisor-id}/hypervisor-library-images/{hypervisor-library-image-id}\n\nGetVirtualMachineImage\n\nGet a hypervisor library image identified by {hypervisor-library-image-id}",
    capability=Capability.READ,
)
async def greenlake_get_virtualization_v1beta1_hypervisor_managers_hypervisor_id_hypervisor_library_images_hypervisor_library_image_id(
    ctx: Context,
    hypervisor_id: Annotated[str, Field(description="path parameter 'hypervisor-id'")],
    hypervisor_library_image_id: Annotated[str, Field(description="path parameter 'hypervisor-library-image-id'")],
) -> Any:
    path = f"/virtualization/v1beta1/hypervisor-managers/{path_seg(hypervisor_id)}/hypervisor-library-images/{path_seg(hypervisor_library_image_id)}"
    return await greenlake_request(
        ctx,
        "GET",
        path,
    )


@tool(
    name="greenlake_post_virtualization_v1beta1_hypervisor_managers_hypervisor_id_refresh",
    description="POST /virtualization/v1beta1/hypervisor-managers/{hypervisor-id}/refresh\n\nHypervisorRefresh\n\nRefresh the specified hypervisor manager",
    capability=Capability.WRITE,
)
async def greenlake_post_virtualization_v1beta1_hypervisor_managers_hypervisor_id_refresh(
    ctx: Context,
    hypervisor_id: Annotated[str, Field(description="path parameter 'hypervisor-id'")],
) -> Any:
    path = f"/virtualization/v1beta1/hypervisor-managers/{path_seg(hypervisor_id)}/refresh"
    return await greenlake_request(
        ctx,
        "POST",
        path,
    )
