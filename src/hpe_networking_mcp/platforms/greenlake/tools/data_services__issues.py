"""Generated GreenLake tools — DO NOT EDIT BY HAND.

Generated from the vendored spec ``vendor/greenlake/data-services.json`` by the
maintainer-local GreenLake generator. These modules are committed and are the
runtime source of truth; regeneration is a release-time maintainer workflow
(the generator is intentionally not committed — see ``.gitignore``).

Service: ``data-services``   Tag: ``issues``   Operations: 4
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
    name="greenlake_get_data_services_v1beta1_issues",
    description="GET /data-services/v1beta1/issues\n\nListIssues\n\nList active issues",
    capability=Capability.READ,
)
async def greenlake_get_data_services_v1beta1_issues(
    ctx: Context,
    offset: Annotated[
        int | None,
        Field(
            default=None,
            description="Use offset in conjunction with limit for paging. The offset is the number of items from the beginning of the result set to the first item included in the response.",
        ),
    ] = None,
    limit: Annotated[
        int | None,
        Field(
            default=None,
            description="Use limit in conjunction with offset for paging. The limit is the maximum number of items to include in the response.",
        ),
    ] = None,
    filter: Annotated[
        str | None,
        Field(
            default=None,
            description="The expression used to filter responses. You can filter on the following properties: `issueType`, `severity`, `category`, `state`, `createdAt`, `services`,  `sourceResourceId`, `sourceResourceType`. You can combine multiple comparison operators using “and”. The returned set of resources must match the criteria in the filter query parameter A comparison compares a property name to a literal. The comparisons supported are the following: “eq” : Is a property equal to value. Valid for number, boolean and string properties. “gt” : Is a property greater than a value. Valid for number or string timestamp properties. “lt” : Is a property less than a value. Valid for number or string timestamp properties “in” : Is a value in a property. The property is an array of number, boolean or string properties. \"contains\": Is a substring value that is equal to a portion of the property value. Valid for strings. Syntax:  “eq” : filter=\\<property> eq \\<value> {host:port}/data-services/v1beta1/issues?filter=\\<property> eq \\<value> “gt” : filter=\\<property> gt \\<value> {host:port}/data-services/v1beta1/issues?filter=\\<property> gt \\<value> “lt” : filter=\\<property> lt \\<value> {host:port}/data-services/v1beta1/issues?filter=\\<property> lt \\<value> “in” : filter=\\<property> in \\<value> {host:port}/data-services/v1beta1/issues?filter=\\<property> in \\<value> “contains” : filter=contains(property,value) {host:port}/data-services/v1beta1/issues?filter=contains(property,value) * Can use and to add more filter inputs {host:port}/data-services/v1beta1/issues?filter=\\<property1> eq \\<value1> and \\<property2> lt \\<value2>  * To filter multiple values on one property e.g. filter=severity in ('CRITICAL','WARNING') {host:port}/data-services/v1beta1/issues?filter=severity%20in%20CRITICAL%2CWARNING Examples: GET /data-services/v1beta1/issues?filter=issueType eq 'ISSUE' GET /data-services/v1beta1/issues?filter=issueType eq 'ISSUE' & state eq 'CREATED' GET /data-services/v1beta1/issues?filter=contains(sourceResourceType,'orchestrator') GET /data-services/v1beta1/issues?filter='data-ops-manager' in services Filters are supported on following attributes: issueType, severity, category, state, createdAt, services, sourceResourceId, sourceResourceType",
        ),
    ] = None,
    sort: Annotated[
        str | None,
        Field(
            default=None,
            description="resource property to sort, with an order appended Order may only be either “asc” (ascending) or “desc” (descending)",
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
        "/data-services/v1beta1/issues",
        query_params=query_params or None,
    )


@tool(
    name="greenlake_get_data_services_v1beta1_issues_id",
    description="GET /data-services/v1beta1/issues/{id}\n\nGetIssue\n\nGet a singular issue",
    capability=Capability.READ,
)
async def greenlake_get_data_services_v1beta1_issues_id(
    ctx: Context,
    id: Annotated[str, Field(description="The UUID of the issue")],
    select: Annotated[
        str | None,
        Field(
            default=None,
            description='Limits the properties returned with a resource or collection-level GET. Specify a comma-separated list of properties. (e.g.: "?select=id,type,customerId,services,createdAt,lastOccurredAt,generation,resourceUri")',
        ),
    ] = None,
) -> Any:
    path = f"/data-services/v1beta1/issues/{path_seg(id)}"
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
    name="greenlake_get_data_services_v1beta1_issues_metadata",
    description="GET /data-services/v1beta1/issues-metadata\n\nGetIssuesMetadata\n\nReturns all the supported Issues metadata relevant to the UI and API clients",
    capability=Capability.READ,
)
async def greenlake_get_data_services_v1beta1_issues_metadata(
    ctx: Context,
    offset: Annotated[
        int | None,
        Field(default=None, description="The number of items to skip before starting to collect the result set"),
    ] = None,
    limit: Annotated[int | None, Field(default=None, description="The numbers of items to return")] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if offset is not None:
        query_params["offset"] = offset
    if limit is not None:
        query_params["limit"] = limit
    return await greenlake_request(
        ctx,
        "GET",
        "/data-services/v1beta1/issues-metadata",
        query_params=query_params or None,
    )


@tool(
    name="greenlake_patch_data_services_v1beta1_issues_id",
    description="PATCH /data-services/v1beta1/issues/{id}\n\nPatchIssue\n\nChanges the attributes of an existing Issue object",
    capability=Capability.WRITE,
)
async def greenlake_patch_data_services_v1beta1_issues_id(
    ctx: Context,
    id: Annotated[str, Field(description="The UUID of the issue")],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    path = f"/data-services/v1beta1/issues/{path_seg(id)}"
    return await greenlake_request(
        ctx,
        "PATCH",
        path,
        body=body,
    )
