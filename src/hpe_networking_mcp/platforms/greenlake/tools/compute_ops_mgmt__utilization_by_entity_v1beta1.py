"""Generated GreenLake tools — DO NOT EDIT BY HAND.

Generated from the vendored spec ``vendor/greenlake/compute-ops-mgmt.json`` by the
maintainer-local GreenLake generator. These modules are committed and are the
runtime source of truth; regeneration is a release-time maintainer workflow
(the generator is intentionally not committed — see ``.gitignore``).

Service: ``compute-ops-mgmt``   Tag: ``utilization_by_entity_v1beta1``   Operations: 1
"""

# ruff: noqa: E501, N803
from __future__ import annotations

from typing import Annotated, Any

from fastmcp import Context
from pydantic import Field

from hpe_networking_mcp.platforms._common.annotations import Capability
from hpe_networking_mcp.platforms.greenlake._registry import tool
from hpe_networking_mcp.platforms.greenlake.client import greenlake_request


@tool(
    name="greenlake_get_compute_ops_mgmt_v1beta1_utilization_by_entity",
    description="GET /compute-ops-mgmt/v1beta1/utilization-by-entity\n\nget_utilization_by_entity\n\nRetrieve utilization data by entity",
    capability=Capability.READ,
)
async def greenlake_get_compute_ops_mgmt_v1beta1_utilization_by_entity(
    ctx: Context,
    start_date: Annotated[str, Field(description="Start date for utilization data retrieval.")],
    end_date: Annotated[str, Field(description="End date for utilization data retrieval.")],
    resource_uri: Annotated[
        str,
        Field(
            description="URI of the resource for which utilization data is to be retrieved. This can be a server, filter or group URI."
        ),
    ],
    metric_type: Annotated[str, Field(description="The metric type for which utilization data is to be retrieved.")],
    excluded_servers: Annotated[
        bool | None,
        Field(
            default=None,
            description="When it is set to true, the response will have details of servers which do not have utilization data available.",
        ),
    ] = None,
    filter_tags: Annotated[
        str | None,
        Field(
            default=None,
            description="Limit the resources operated on by tags or return only the subset of resources that match all the filter tags.",
        ),
    ] = None,
    sort: Annotated[
        str | None,
        Field(
            default=None,
            description="The order in which to return the resources in the collection. Sort expression is a property name, followed by `asc` (ascending) or `desc` (descending).",
        ),
    ] = None,
    offset: Annotated[
        int | None, Field(default=None, description="Zero-based resource offset to start the response from")
    ] = None,
    limit: Annotated[int | None, Field(default=None, description="The maximum number of records to return.")] = None,
    Tenant_Acid: Annotated[
        str | None,
        Field(
            default=None,
            description="Tenant-Acid header can be used by an MSP workspace to make API calls on behalf of their tenant by specifying the tenant's application customer ID.  In order to make such an API call, the Bearer token must belong to an MSP workspace and this header value must be the application customer ID of a tenant within the MSP workspace. Use the `/compute-ops-mgmt/v1beta1/accounts` API to determine the application customer IDs for your tenant accounts.",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if start_date is not None:
        query_params["start-date"] = start_date
    if end_date is not None:
        query_params["end-date"] = end_date
    if excluded_servers is not None:
        query_params["excluded-servers"] = excluded_servers
    if resource_uri is not None:
        query_params["resource-uri"] = resource_uri
    if metric_type is not None:
        query_params["metric-type"] = metric_type
    if filter_tags is not None:
        query_params["filter-tags"] = filter_tags
    if sort is not None:
        query_params["sort"] = sort
    if offset is not None:
        query_params["offset"] = offset
    if limit is not None:
        query_params["limit"] = limit
    header_params: dict[str, str] = {}
    if Tenant_Acid is not None:
        header_params["Tenant-Acid"] = str(Tenant_Acid)
    return await greenlake_request(
        ctx,
        "GET",
        "/compute-ops-mgmt/v1beta1/utilization-by-entity",
        query_params=query_params or None,
        header_params=header_params or None,
    )
