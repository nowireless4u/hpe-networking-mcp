"""Generated GreenLake tools — DO NOT EDIT BY HAND.

Generated from the vendored spec ``vendor/greenlake/data-services.json`` by the
maintainer-local GreenLake generator. These modules are committed and are the
runtime source of truth; regeneration is a release-time maintainer workflow
(the generator is intentionally not committed — see ``.gitignore``).

Service: ``data-services``   Tag: ``dual_auth_operations``   Operations: 3
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
    name="greenlake_get_data_services_v1beta1_dual_auth_operations",
    description="GET /data-services/v1beta1/dual-auth-operations\n\nDualAuthOperationsList\n\nList Dual Authorization operations",
    capability=Capability.READ,
)
async def greenlake_get_data_services_v1beta1_dual_auth_operations(
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
            description="The expression to use for filtering responses. The following comparisons are supported: “eq” : Valid for number, boolean and string properties. “gt” :  Valid for number or string timestamp properties. “lt” :  Valid for number or string timestamp properties “in” : Valid for an array of strings Syntax: “eq” : filter=\\<property> eq \\<value> {host:port}/data-services/v1beta1/dual-auth-operations?filter=\\<property> eq \\<value> “gt” : filter=\\<property> gt \\<value> {host:port}/data-services/v1beta1/dual-auth-operations?filter=\\<property> gt \\<value> “lt” : filter=\\<property> lt \\<value> {host:port}/data-services/v1beta1/dual-auth-operations?filter=\\<property> lt \\<value> “in” : filter=\\<property> in \\<value> {host:port}/data-services/v1beta1/dual-auth-operations?filter=\\<property> in \\<value> * Use \"and\" to combine filter inputs {host:port}/data-services/v1beta1/dual-auth-operations?filter=\\<property1> eq \\<value1> and \\<property2> lt \\<value2> * To filter multiple values on one property e.g. filter=resourceType in ('foo','bar') {host:port}/data-services/v1beta1/dual-auth-operations?filter=foo%bar%20in%20resourceType Examples: GET /data-services/v1beta1/dual-auth-operations?filter=resourceType eq 'ISSUE' GET /data-services/v1beta1/dual-auth-operations?filter=resourceType eq 'ISSUE' and state eq 'CREATED' GET /data-services/v1beta1/dual-auth-operations?filter=relatedObjectType in ('NIMBLE-VOLUME') Filters are supported on following attributes: resourceUri, resourceName, resourceType, requestedOperation, operationDescription, requestedByUri, requestedByEmail, requestedAt, customerId, checkedByUri, checkedByEmail, checkedAt, sourceServiceExternalName, state",
        ),
    ] = None,
    sort: Annotated[
        str | None,
        Field(
            default=None,
            description='The property to sort by followed by a direction indicator ("asc" or "desc"). If no direction indicator is specified the default order is ascending.',
        ),
    ] = None,
    select: Annotated[
        str | None,
        Field(
            default=None,
            description="Limits the properties returned with a resource or collection-level GET. Specify a comma-separated list of properties. If this is omitted, all properties are returned.",
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
        "/data-services/v1beta1/dual-auth-operations",
        query_params=query_params or None,
    )


@tool(
    name="greenlake_get_data_services_v1beta1_dual_auth_operations_id",
    description="GET /data-services/v1beta1/dual-auth-operations/{id}\n\nDualAuthOperationGet\n\nGet Dual Authorization operation by Id",
    capability=Capability.READ,
)
async def greenlake_get_data_services_v1beta1_dual_auth_operations_id(
    ctx: Context,
    id: Annotated[str, Field(description="the ID of the operation")],
) -> Any:
    path = f"/data-services/v1beta1/dual-auth-operations/{path_seg(id)}"
    return await greenlake_request(
        ctx,
        "GET",
        path,
    )


@tool(
    name="greenlake_patch_data_services_v1beta1_dual_auth_operations_id",
    description="PATCH /data-services/v1beta1/dual-auth-operations/{id}\n\nDualAuthOperationUpdate\n\nChanges the value of the given Dual Authorization operation. Approve/Deny the pending operation by changing its state in DB",
    capability=Capability.WRITE,
)
async def greenlake_patch_data_services_v1beta1_dual_auth_operations_id(
    ctx: Context,
    id: Annotated[str, Field(description="the ID of the operation")],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    path = f"/data-services/v1beta1/dual-auth-operations/{path_seg(id)}"
    return await greenlake_request(
        ctx,
        "PATCH",
        path,
        body=body,
    )
