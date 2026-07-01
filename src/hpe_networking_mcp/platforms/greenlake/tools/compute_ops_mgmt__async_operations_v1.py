"""Generated GreenLake tools — DO NOT EDIT BY HAND.

Generated from the vendored spec ``vendor/greenlake/compute-ops-mgmt.json`` by the
maintainer-local GreenLake generator. These modules are committed and are the
runtime source of truth; regeneration is a release-time maintainer workflow
(the generator is intentionally not committed — see ``.gitignore``).

Service: ``compute-ops-mgmt``   Tag: ``async_operations_v1``   Operations: 3
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
    name="greenlake_get_compute_ops_mgmt_v1_async_operations",
    description="GET /compute-ops-mgmt/v1/async-operations\n\nget_v1_async_operations\n\nList all async operations",
    capability=Capability.READ,
)
async def greenlake_get_compute_ops_mgmt_v1_async_operations(
    ctx: Context,
    limit: Annotated[int | None, Field(default=None, description="The maximum number of records to return.")] = None,
    next: Annotated[
        str | None, Field(default=None, description="The pagination cursor for the next page of resources.")
    ] = None,
    filter: Annotated[
        str | None,
        Field(
            default=None,
            description="Limit the resources operated on by an endpoint or when used with a multiple-GET endpoint, return only the subset of resources that match the filter. The filter grammar is a subset of OData 4.0.  NOTE: The filter query parameter must use [URL encoding](https://en.wikipedia.org/wiki/URL_encoding). Most clients do this automatically with inputs provided to them specifically as query parameters. Encoding must be done manually for any query parameters provided as part of the URL.   The reserved characters `!` `#` `$` `&` `'` `(` `)` `*` `+` `,` `/` `:` `;` `=` `?` `@` `[` `]` must be encoded with percent encoded equivalents. Server IDs contain a `+`, which must be encoded as `%2B`.   For example: the value `P06760-B21+2M212504P8` must be encoded as `P06760-B21%2B2M212504P8` when it is used in a query parameter.  | CLASS     |  EXAMPLES                                          | |-----------|----------------------------------------------------| | Types     | integer, decimal, timestamp, string, boolean, null | | Operations| eq, ne, gt, ge, lt, le, in                         | | Logic     | and, or, not                                       |  Async Operations can be filtered by: - createdAt - endedAt - error - generation - id - logMessages - progressPercent - recommendations - results - sourceResourceUri - startedAt - state - updatedAt  The following examples are not an exhaustive list of all possible filtering options.",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if limit is not None:
        query_params["limit"] = limit
    if next is not None:
        query_params["next"] = next
    if filter is not None:
        query_params["filter"] = filter
    return await greenlake_request(
        ctx,
        "GET",
        "/compute-ops-mgmt/v1/async-operations",
        query_params=query_params or None,
    )


@tool(
    name="greenlake_get_compute_ops_mgmt_v1_async_operations_id",
    description="GET /compute-ops-mgmt/v1/async-operations/{id}\n\nget_v1_async_operations_by_id\n\nRetrieve an async operation by ID",
    capability=Capability.READ,
)
async def greenlake_get_compute_ops_mgmt_v1_async_operations_id(
    ctx: Context,
    id: Annotated[str, Field(description="The ID of the async operation")],
) -> Any:
    path = f"/compute-ops-mgmt/v1/async-operations/{path_seg(id)}"
    return await greenlake_request(
        ctx,
        "GET",
        path,
    )


@tool(
    name="greenlake_post_compute_ops_mgmt_v1_async_operations_id_cancel",
    description="POST /compute-ops-mgmt/v1/async-operations/{id}/cancel\n\ncancel_v1_async_operation_by_id\n\nCancel an async operation by ID",
    capability=Capability.WRITE,
)
async def greenlake_post_compute_ops_mgmt_v1_async_operations_id_cancel(
    ctx: Context,
    id: Annotated[str, Field(description="The ID of the async operation")],
    Content_Type: Annotated[
        str,
        Field(
            description="Content-Type header must designate 'application/json' in order for the request to be performed."
        ),
    ],
    Tenant_Acid: Annotated[
        str | None,
        Field(
            default=None,
            description="Tenant-Acid header can be used by an MSP workspace to make API calls on behalf of their tenant by specifying the tenant's application customer ID.  In order to make such an API call, the Bearer token must belong to an MSP workspace and this header value must be the application customer ID of a tenant within the MSP workspace. Use the `/compute-ops-mgmt/v1beta1/accounts` API to determine the application customer IDs for your tenant accounts.",
        ),
    ] = None,
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request body")] = None,
) -> Any:
    path = f"/compute-ops-mgmt/v1/async-operations/{path_seg(id)}/cancel"
    header_params: dict[str, str] = {}
    if Content_Type is not None:
        header_params["Content-Type"] = str(Content_Type)
    if Tenant_Acid is not None:
        header_params["Tenant-Acid"] = str(Tenant_Acid)
    return await greenlake_request(
        ctx,
        "POST",
        path,
        header_params=header_params or None,
        body=body,
    )
