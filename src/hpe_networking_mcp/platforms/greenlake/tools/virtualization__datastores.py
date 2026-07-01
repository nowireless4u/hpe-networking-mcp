"""Generated GreenLake tools — DO NOT EDIT BY HAND.

Generated from the vendored spec ``vendor/greenlake/virtualization.json`` by the
maintainer-local GreenLake generator. These modules are committed and are the
runtime source of truth; regeneration is a release-time maintainer workflow
(the generator is intentionally not committed — see ``.gitignore``).

Service: ``virtualization``   Tag: ``datastores``   Operations: 3
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
    name="greenlake_get_virtualization_v1beta1_datastores",
    description="GET /virtualization/v1beta1/datastores\n\nDatastoresList\n\nGet all datastores across registered hypervisor managers.",
    capability=Capability.READ,
)
async def greenlake_get_virtualization_v1beta1_datastores(
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
            description='The filter query parameter is used to filter the set of resources returned in the response. The returned set of resources must match the criteria in the filter query parameter.  A comparison compares a property name to a literal. The following comparisons are supported: * “eq” : Is a property equal to value. Valid for number, boolean and string properties. * “ne” : Is a property not equal to value. Valid for number, boolean and string properties. * “gt” : Is a property greater than a value. Valid for number or string timestamp properties. * “lt” : Is a property less than a value. Valid for number or string timestamp properties * “in” : Is a value in a property (that is an array of strings)  Examples: * GET /virtualization/v1beta1/datastores?filter="datastoreType eq VMFS" * GET /virtualization/v1beta1/datastores?filter="datastoreType eq VMFS and status eq ERROR"  Filters are supported on the following attributes: * status * state * appType * hypervisorManagerInfo/name * hypervisorManagerInfo/displayName * hypervisorManagerInfo/id * hostsInfo/id * hostsInfo/name * hostsInfo/displayName * clusterInfo/id * clusterInfo/name * clusterInfo/displayName * protectionJobInfo/protectionPolicyInfo/id * protectionJobInfo/protectionPolicyInfo/name * vmProtectionGroupsInfo/id * vmProtectionGroupsInfo/name * volumesInfo/id * volumesInfo/storageSystemInfo/id * volumesInfo/storageSystemInfo/serialNumber * volumesInfo/storageSystemInfo/name * volumesInfo/storageSystemInfo/vendorName * volumesInfo/storageFolderInfo/id * volumesInfo/storageFolderInfo/name * volumesInfo/storagePoolInfo/id * volumesInfo/storagePoolInfo/name * datastoreType * createdAt * name * services * allowedOperations * capacityInBytes * capacityFree * displayName * replicationInfo/name * replicationInfo/id * hciClusterUuid',
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
        "/virtualization/v1beta1/datastores",
        query_params=query_params or None,
    )


@tool(
    name="greenlake_get_virtualization_v1beta1_datastores_datastore_id",
    description="GET /virtualization/v1beta1/datastores/{datastore-id}\n\nDatastore\n\nGet a datastore identified by {datastore-id}",
    capability=Capability.READ,
)
async def greenlake_get_virtualization_v1beta1_datastores_datastore_id(
    ctx: Context,
    datastore_id: Annotated[str, Field(description="path parameter 'datastore-id'")],
) -> Any:
    path = f"/virtualization/v1beta1/datastores/{path_seg(datastore_id)}"
    return await greenlake_request(
        ctx,
        "GET",
        path,
    )


@tool(
    name="greenlake_post_virtualization_v1beta1_datastores",
    description="POST /virtualization/v1beta1/datastores\n\nCreateDS\n\nCreate datastore",
    capability=Capability.WRITE,
)
async def greenlake_post_virtualization_v1beta1_datastores(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await greenlake_request(
        ctx,
        "POST",
        "/virtualization/v1beta1/datastores",
        body=body,
    )
