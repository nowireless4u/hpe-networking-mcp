"""Generated GreenLake tools — DO NOT EDIT BY HAND.

Generated from the vendored spec ``vendor/greenlake/virtualization.json`` by the
maintainer-local GreenLake generator. These modules are committed and are the
runtime source of truth; regeneration is a release-time maintainer workflow
(the generator is intentionally not committed — see ``.gitignore``).

Service: ``virtualization``   Tag: ``hypervisor_clusters``   Operations: 2
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
    name="greenlake_get_virtualization_v1beta1_hypervisor_clusters",
    description="GET /virtualization/v1beta1/hypervisor-clusters\n\nHypervisorClusterList\n\nGet all clusters across registered hypervisor managers.",
    capability=Capability.READ,
)
async def greenlake_get_virtualization_v1beta1_hypervisor_clusters(
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
            description='The filter query parameter is used to filter the set of resources returned in the response. The returned set of resources must match the criteria in the filter query parameter.  A comparison compares a property name to a literal. The following comparisons are supported: * “eq” : Is a property equal to value. Valid for number, boolean and string properties. * “ne” : Is a property not equal to value. Valid for number, boolean and string properties. * “gt” : Is a property greater than a value. Valid for number or string timestamp properties. * “lt” : Is a property less than a value. Valid for number or string timestamp properties * “in” : Is a value in a property (that is an array of strings)  Examples: * GET /virtualization/v1beta1/hypervisor-clusters?filter="clusterType eq ESX_CLUSTER" * GET /virtualization/v1beta1/hypervisor-clusters?filter="clusterType eq ESX_CLUSTER and status eq ERROR"  Filters are supported on the following attributes: * clusterType * id * state * hypervisorManagerInfo/name * hypervisorManagerInfo/displayName * hypervisorManagerInfo/id * status * createdAt * hciClusterUuid * name * services * displayName * appInfo/vmware/moref',
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
        "/virtualization/v1beta1/hypervisor-clusters",
        query_params=query_params or None,
    )


@tool(
    name="greenlake_get_virtualization_v1beta1_hypervisor_clusters_cluster_id",
    description="GET /virtualization/v1beta1/hypervisor-clusters/{cluster-id}\n\nHypervisorCluster\n\nGet a hypervisor cluster resource identified by {cluster-id}",
    capability=Capability.READ,
)
async def greenlake_get_virtualization_v1beta1_hypervisor_clusters_cluster_id(
    ctx: Context,
    cluster_id: Annotated[str, Field(description="path parameter 'cluster-id'")],
) -> Any:
    path = f"/virtualization/v1beta1/hypervisor-clusters/{path_seg(cluster_id)}"
    return await greenlake_request(
        ctx,
        "GET",
        path,
    )
