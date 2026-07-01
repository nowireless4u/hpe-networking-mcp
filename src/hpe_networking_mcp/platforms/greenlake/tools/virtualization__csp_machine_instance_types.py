"""Generated GreenLake tools — DO NOT EDIT BY HAND.

Generated from the vendored spec ``vendor/greenlake/virtualization.json`` by the
maintainer-local GreenLake generator. These modules are committed and are the
runtime source of truth; regeneration is a release-time maintainer workflow
(the generator is intentionally not committed — see ``.gitignore``).

Service: ``virtualization``   Tag: ``csp_machine_instance_types``   Operations: 2
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
    name="greenlake_get_virtualization_v1beta1_csp_machine_instance_types",
    description="GET /virtualization/v1beta1/csp-machine-instance-types\n\nCSPMachineInstanceTypeList\n\nGet a list of CSP machine instance types",
    capability=Capability.READ,
)
async def greenlake_get_virtualization_v1beta1_csp_machine_instance_types(
    ctx: Context,
    offset: Annotated[
        int | None,
        Field(
            default=None,
            description='The number of items to omit from the beginning of the result set. Use offset in conjunction with limit for pagination,  for example "offset=30&limit=10" indicates the fourth page of 10 items.',
        ),
    ] = None,
    limit: Annotated[
        int | None,
        Field(
            default=None,
            description='The maximum number of items to include in the response. Use offset in conjunction with limit for pagination,  for example "offset=30&limit=10" indicates the fourth page of 10 items.',
        ),
    ] = None,
    filter: Annotated[
        str | None,
        Field(
            default=None,
            description="An expression to filter the results.  Filtering is supported with following attributes:  * cspInfo.region  * cspInfo.freeTierEligible  * cspInfo.processorInfo.supportedArchitectures  * cspInfo.supportedVirtualizationTypes  * cspInfo.cspInfo.supportedRootDeviceTypes  * cspInfo.hypervisor  * cspInfo.ebsInfo.encryptionSupport  * cspInfo.networkInfo.enaSupport  * cspType",
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
        "/virtualization/v1beta1/csp-machine-instance-types",
        query_params=query_params or None,
    )


@tool(
    name="greenlake_get_virtualization_v1beta1_csp_machine_instance_types_id",
    description="GET /virtualization/v1beta1/csp-machine-instance-types/{id}\n\nCSPMachineInstanceTypeGet\n\nGet details of a CSP machine instance type",
    capability=Capability.READ,
)
async def greenlake_get_virtualization_v1beta1_csp_machine_instance_types_id(
    ctx: Context,
    id: Annotated[str, Field(description="Unique identifier of a CSP machine instance type")],
) -> Any:
    path = f"/virtualization/v1beta1/csp-machine-instance-types/{path_seg(id)}"
    return await greenlake_request(
        ctx,
        "GET",
        path,
    )
