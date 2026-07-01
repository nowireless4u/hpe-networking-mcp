"""Generated GreenLake tools — DO NOT EDIT BY HAND.

Generated from the vendored spec ``vendor/greenlake/compute-ops-mgmt.json`` by the
maintainer-local GreenLake generator. These modules are committed and are the
runtime source of truth; regeneration is a release-time maintainer workflow
(the generator is intentionally not committed — see ``.gitignore``).

Service: ``compute-ops-mgmt``   Tag: ``schedules_v1beta2``   Operations: 7
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
    name="greenlake_delete_compute_ops_mgmt_v1beta2_schedules_id",
    description="DELETE /compute-ops-mgmt/v1beta2/schedules/{id}\n\ndelete_v1beta2_schedule\n\nDelete a schedule",
    capability=Capability.WRITE_DELETE,
)
async def greenlake_delete_compute_ops_mgmt_v1beta2_schedules_id(
    ctx: Context,
    id: Annotated[str, Field(description="Schedule ID")],
    Tenant_Acid: Annotated[
        str | None,
        Field(
            default=None,
            description="Tenant-Acid header can be used by an MSP workspace to make API calls on behalf of their tenant by specifying the tenant's application customer ID.  In order to make such an API call, the Bearer token must belong to an MSP workspace and this header value must be the application customer ID of a tenant within the MSP workspace. Use the `/compute-ops-mgmt/v1beta1/accounts` API to determine the application customer IDs for your tenant accounts.",
        ),
    ] = None,
) -> Any:
    path = f"/compute-ops-mgmt/v1beta2/schedules/{path_seg(id)}"
    header_params: dict[str, str] = {}
    if Tenant_Acid is not None:
        header_params["Tenant-Acid"] = str(Tenant_Acid)
    return await greenlake_request(
        ctx,
        "DELETE",
        path,
        header_params=header_params or None,
    )


@tool(
    name="greenlake_get_compute_ops_mgmt_v1beta2_schedules",
    description="GET /compute-ops-mgmt/v1beta2/schedules\n\nget_v1beta2_schedules\n\nList all schedules",
    capability=Capability.READ,
)
async def greenlake_get_compute_ops_mgmt_v1beta2_schedules(
    ctx: Context,
    offset: Annotated[
        int | None, Field(default=None, description="Zero-based resource offset to start the response from")
    ] = None,
    limit: Annotated[int | None, Field(default=None, description="The maximum number of records to return.")] = None,
    filter: Annotated[
        str | None,
        Field(
            default=None,
            description="Limit the resources operated on by an endpoint or when used with a multiple-GET endpoint, return only the subset of resources that match the filter. The filter grammar is a subset of OData 4.0.  NOTE: The filter query parameter must use [URL encoding](https://en.wikipedia.org/wiki/URL_encoding). Most clients do this automatically with inputs provided to them specifically as query parameters. Encoding must be done manually for any query parameters provided as part of the URL.   The reserved characters `!` `#` `$` `&` `'` `(` `)` `*` `+` `,` `/` `:` `;` `=` `?` `@` `[` `]` must be encoded with percent encoded equivalents. Server IDs contain a `+`, which must be encoded as `%2B`.   For example: the value `P06760-B21+2M212504P8` must be encoded as `P06760-B21%2B2M212504P8` when it is used in a query parameter.  | CLASS     |  EXAMPLES                                          | |-----------|----------------------------------------------------| | Types     | integer, decimal, timestamp, string, boolean, null | | Operations| eq, ne, gt, ge, lt, le, in                         | | Logic     | and, or, not                                       |  Schedules can be filtered by: - createdAt - generation - historyUri - id - nextStartAt - operation/body - operation/headers - operation/method - operation/query - operation/timeoutInSec - operation/type - operation/uri - resourceUri - schedule/intervalInSec - schedule/startAt - type - updatedAt  The following examples are not an exhaustive list of all possible filtering options.",
        ),
    ] = None,
    sort: Annotated[
        str | None,
        Field(
            default=None,
            description="The order in which to return the resources in the collection.  The value of the sort query parameter is a comma separated list of sort expressions.  Each sort expression is a property name optionally followed by a direction indicator asc (ascending) or desc  (descending).  The first sort expression in the list defines the primary sort order, the second defines the secondary sort order,  and so on. If a direciton indicator is omitted the default direction is ascending.",
        ),
    ] = None,
    select: Annotated[
        str | None,
        Field(
            default=None,
            description="Limit the properties of the resource returned in a successful response.  When applied to write operations, `select` controls only the properties that are returned, not which properties are operated on. All properties are returned if the `select` parameter is omitted.  The value of the `select` query parameter is a comma separated list of properties to include in the response. Nested properties use `/` as a separator, e.g. `select=interfaces/name` selects the `name` property within an `interfaces` object.  For operations that return paginated collections, `select` operates on the resources in the collection. The pagination properties like `count` and `items` are always included even when `select` is specified.",
        ),
    ] = None,
    Tenant_Acid: Annotated[
        str | None,
        Field(
            default=None,
            description="Tenant-Acid header can be used by an MSP workspace to make API calls on behalf of their tenant by specifying the tenant's application customer ID.  In order to make such an API call, the Bearer token must belong to an MSP workspace and this header value must be the application customer ID of a tenant within the MSP workspace. Use the `/compute-ops-mgmt/v1beta1/accounts` API to determine the application customer IDs for your tenant accounts.",
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
    header_params: dict[str, str] = {}
    if Tenant_Acid is not None:
        header_params["Tenant-Acid"] = str(Tenant_Acid)
    return await greenlake_request(
        ctx,
        "GET",
        "/compute-ops-mgmt/v1beta2/schedules",
        query_params=query_params or None,
        header_params=header_params or None,
    )


@tool(
    name="greenlake_get_compute_ops_mgmt_v1beta2_schedules_id",
    description="GET /compute-ops-mgmt/v1beta2/schedules/{id}\n\nget_v1beta2_schedule\n\nGet a schedule",
    capability=Capability.READ,
)
async def greenlake_get_compute_ops_mgmt_v1beta2_schedules_id(
    ctx: Context,
    id: Annotated[str, Field(description="Schedule ID")],
    select: Annotated[
        str | None,
        Field(
            default=None,
            description="Limit the properties of the resource returned in a successful response.  When applied to write operations, `select` controls only the properties that are returned, not which properties are operated on. All properties are returned if the `select` parameter is omitted.  The value of the `select` query parameter is a comma separated list of properties to include in the response. Nested properties use `/` as a separator, e.g. `select=interfaces/name` selects the `name` property within an `interfaces` object.  For operations that return paginated collections, `select` operates on the resources in the collection. The pagination properties like `count` and `items` are always included even when `select` is specified.",
        ),
    ] = None,
    Tenant_Acid: Annotated[
        str | None,
        Field(
            default=None,
            description="Tenant-Acid header can be used by an MSP workspace to make API calls on behalf of their tenant by specifying the tenant's application customer ID.  In order to make such an API call, the Bearer token must belong to an MSP workspace and this header value must be the application customer ID of a tenant within the MSP workspace. Use the `/compute-ops-mgmt/v1beta1/accounts` API to determine the application customer IDs for your tenant accounts.",
        ),
    ] = None,
) -> Any:
    path = f"/compute-ops-mgmt/v1beta2/schedules/{path_seg(id)}"
    query_params: dict[str, Any] = {}
    if select is not None:
        query_params["select"] = select
    header_params: dict[str, str] = {}
    if Tenant_Acid is not None:
        header_params["Tenant-Acid"] = str(Tenant_Acid)
    return await greenlake_request(
        ctx,
        "GET",
        path,
        query_params=query_params or None,
        header_params=header_params or None,
    )


@tool(
    name="greenlake_get_compute_ops_mgmt_v1beta2_schedules_id_history",
    description="GET /compute-ops-mgmt/v1beta2/schedules/{id}/history\n\nget_v1beta2_schedule_history\n\nList all history of a schedule",
    capability=Capability.READ,
)
async def greenlake_get_compute_ops_mgmt_v1beta2_schedules_id_history(
    ctx: Context,
    id: Annotated[str, Field(description="Schedule ID")],
    offset: Annotated[
        int | None, Field(default=None, description="Zero-based resource offset to start the response from")
    ] = None,
    limit: Annotated[int | None, Field(default=None, description="The maximum number of records to return.")] = None,
    filter: Annotated[
        str | None,
        Field(
            default=None,
            description="Limit the resources operated on by an endpoint or when used with a multiple-GET endpoint, return only the subset of resources that match the filter. The filter grammar is a subset of OData 4.0.  NOTE: The filter query parameter must use [URL encoding](https://en.wikipedia.org/wiki/URL_encoding). Most clients do this automatically with inputs provided to them specifically as query parameters. Encoding must be done manually for any query parameters provided as part of the URL.   The reserved characters `!` `#` `$` `&` `'` `(` `)` `*` `+` `,` `/` `:` `;` `=` `?` `@` `[` `]` must be encoded with percent encoded equivalents. Server IDs contain a `+`, which must be encoded as `%2B`.   For example: the value `P06760-B21+2M212504P8` must be encoded as `P06760-B21%2B2M212504P8` when it is used in a query parameter.  | CLASS     |  EXAMPLES                                          | |-----------|----------------------------------------------------| | Types     | integer, decimal, timestamp, string, boolean, null | | Operations| eq, ne, gt, ge, lt, le, in                         | | Logic     | and, or, not                                       |  Schedules can be filtered by: - createdAt - generation - historyUri - id - nextStartAt - operation/body - operation/headers - operation/method - operation/query - operation/timeoutInSec - operation/type - operation/uri - resourceUri - schedule/intervalInSec - schedule/startAt - type - updatedAt  The following examples are not an exhaustive list of all possible filtering options.",
        ),
    ] = None,
    sort: Annotated[
        str | None,
        Field(
            default=None,
            description="The order in which to return the resources in the collection.  The value of the sort query parameter is a comma separated list of sort expressions.  Each sort expression is a property name optionally followed by a direction indicator asc (ascending) or desc  (descending).  The first sort expression in the list defines the primary sort order, the second defines the secondary sort order,  and so on. If a direciton indicator is omitted the default direction is ascending.",
        ),
    ] = None,
    select: Annotated[
        str | None,
        Field(
            default=None,
            description="Limit the properties of the resource returned in a successful response.  When applied to write operations, `select` controls only the properties that are returned, not which properties are operated on. All properties are returned if the `select` parameter is omitted.  The value of the `select` query parameter is a comma separated list of properties to include in the response. Nested properties use `/` as a separator, e.g. `select=interfaces/name` selects the `name` property within an `interfaces` object.  For operations that return paginated collections, `select` operates on the resources in the collection. The pagination properties like `count` and `items` are always included even when `select` is specified.",
        ),
    ] = None,
    Tenant_Acid: Annotated[
        str | None,
        Field(
            default=None,
            description="Tenant-Acid header can be used by an MSP workspace to make API calls on behalf of their tenant by specifying the tenant's application customer ID.  In order to make such an API call, the Bearer token must belong to an MSP workspace and this header value must be the application customer ID of a tenant within the MSP workspace. Use the `/compute-ops-mgmt/v1beta1/accounts` API to determine the application customer IDs for your tenant accounts.",
        ),
    ] = None,
) -> Any:
    path = f"/compute-ops-mgmt/v1beta2/schedules/{path_seg(id)}/history"
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
    header_params: dict[str, str] = {}
    if Tenant_Acid is not None:
        header_params["Tenant-Acid"] = str(Tenant_Acid)
    return await greenlake_request(
        ctx,
        "GET",
        path,
        query_params=query_params or None,
        header_params=header_params or None,
    )


@tool(
    name="greenlake_get_compute_ops_mgmt_v1beta2_schedules_id_history_history_id",
    description="GET /compute-ops-mgmt/v1beta2/schedules/{id}/history/{history-id}\n\nget_v1beta2_schedule_history_entry\n\nGet a history resource",
    capability=Capability.READ,
)
async def greenlake_get_compute_ops_mgmt_v1beta2_schedules_id_history_history_id(
    ctx: Context,
    id: Annotated[str, Field(description="Schedule ID")],
    history_id: Annotated[str, Field(description="History ID")],
    select: Annotated[
        str | None,
        Field(
            default=None,
            description="Limit the properties of the resource returned in a successful response.  When applied to write operations, `select` controls only the properties that are returned, not which properties are operated on. All properties are returned if the `select` parameter is omitted.  The value of the `select` query parameter is a comma separated list of properties to include in the response. Nested properties use `/` as a separator, e.g. `select=interfaces/name` selects the `name` property within an `interfaces` object.  For operations that return paginated collections, `select` operates on the resources in the collection. The pagination properties like `count` and `items` are always included even when `select` is specified.",
        ),
    ] = None,
    Tenant_Acid: Annotated[
        str | None,
        Field(
            default=None,
            description="Tenant-Acid header can be used by an MSP workspace to make API calls on behalf of their tenant by specifying the tenant's application customer ID.  In order to make such an API call, the Bearer token must belong to an MSP workspace and this header value must be the application customer ID of a tenant within the MSP workspace. Use the `/compute-ops-mgmt/v1beta1/accounts` API to determine the application customer IDs for your tenant accounts.",
        ),
    ] = None,
) -> Any:
    path = f"/compute-ops-mgmt/v1beta2/schedules/{path_seg(id)}/history/{path_seg(history_id)}"
    query_params: dict[str, Any] = {}
    if select is not None:
        query_params["select"] = select
    header_params: dict[str, str] = {}
    if Tenant_Acid is not None:
        header_params["Tenant-Acid"] = str(Tenant_Acid)
    return await greenlake_request(
        ctx,
        "GET",
        path,
        query_params=query_params or None,
        header_params=header_params or None,
    )


@tool(
    name="greenlake_patch_compute_ops_mgmt_v1beta2_schedules_id",
    description="PATCH /compute-ops-mgmt/v1beta2/schedules/{id}\n\npatch_v1beta2_schedule\n\nUpdate a schedule",
    capability=Capability.WRITE,
)
async def greenlake_patch_compute_ops_mgmt_v1beta2_schedules_id(
    ctx: Context,
    id: Annotated[str, Field(description="Schedule ID")],
    Content_Type: Annotated[
        str,
        Field(
            description="Content-Type header must designate 'application/merge-patch+json' in order for the request to be performed."
        ),
    ],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
    select: Annotated[
        str | None,
        Field(
            default=None,
            description="Limit the properties of the resource returned in a successful response.  When applied to write operations, `select` controls only the properties that are returned, not which properties are operated on. All properties are returned if the `select` parameter is omitted.  The value of the `select` query parameter is a comma separated list of properties to include in the response. Nested properties use `/` as a separator, e.g. `select=interfaces/name` selects the `name` property within an `interfaces` object.  For operations that return paginated collections, `select` operates on the resources in the collection. The pagination properties like `count` and `items` are always included even when `select` is specified.",
        ),
    ] = None,
    If_Match: Annotated[
        str | None,
        Field(
            default=None,
            description='Value which must match the "generation" property of the resource in order for the request to be performed.',
        ),
    ] = None,
    Tenant_Acid: Annotated[
        str | None,
        Field(
            default=None,
            description="Tenant-Acid header can be used by an MSP workspace to make API calls on behalf of their tenant by specifying the tenant's application customer ID.  In order to make such an API call, the Bearer token must belong to an MSP workspace and this header value must be the application customer ID of a tenant within the MSP workspace. Use the `/compute-ops-mgmt/v1beta1/accounts` API to determine the application customer IDs for your tenant accounts.",
        ),
    ] = None,
) -> Any:
    path = f"/compute-ops-mgmt/v1beta2/schedules/{path_seg(id)}"
    query_params: dict[str, Any] = {}
    if select is not None:
        query_params["select"] = select
    header_params: dict[str, str] = {}
    if If_Match is not None:
        header_params["If-Match"] = str(If_Match)
    if Content_Type is not None:
        header_params["Content-Type"] = str(Content_Type)
    if Tenant_Acid is not None:
        header_params["Tenant-Acid"] = str(Tenant_Acid)
    return await greenlake_request(
        ctx,
        "PATCH",
        path,
        query_params=query_params or None,
        header_params=header_params or None,
        body=body,
    )


@tool(
    name="greenlake_post_compute_ops_mgmt_v1beta2_schedules",
    description="POST /compute-ops-mgmt/v1beta2/schedules\n\ncreate_v1beta2_schedule\n\nCreate a schedule",
    capability=Capability.WRITE,
)
async def greenlake_post_compute_ops_mgmt_v1beta2_schedules(
    ctx: Context,
    Content_Type: Annotated[
        str,
        Field(
            description="Content-Type header must designate 'application/json' in order for the request to be performed."
        ),
    ],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
    select: Annotated[
        str | None,
        Field(
            default=None,
            description="Limit the properties of the resource returned in a successful response.  When applied to write operations, `select` controls only the properties that are returned, not which properties are operated on. All properties are returned if the `select` parameter is omitted.  The value of the `select` query parameter is a comma separated list of properties to include in the response. Nested properties use `/` as a separator, e.g. `select=interfaces/name` selects the `name` property within an `interfaces` object.  For operations that return paginated collections, `select` operates on the resources in the collection. The pagination properties like `count` and `items` are always included even when `select` is specified.",
        ),
    ] = None,
    Idempotency_Key: Annotated[
        str | None,
        Field(
            default=None,
            description="A unique value generated by the client which the server uses to recognize subsequent retries of the same request.",
        ),
    ] = None,
    Tenant_Acid: Annotated[
        str | None,
        Field(
            default=None,
            description="Tenant-Acid header can be used by an MSP workspace to make API calls on behalf of their tenant by specifying the tenant's application customer ID.  In order to make such an API call, the Bearer token must belong to an MSP workspace and this header value must be the application customer ID of a tenant within the MSP workspace. Use the `/compute-ops-mgmt/v1beta1/accounts` API to determine the application customer IDs for your tenant accounts.",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if select is not None:
        query_params["select"] = select
    header_params: dict[str, str] = {}
    if Idempotency_Key is not None:
        header_params["Idempotency-Key"] = str(Idempotency_Key)
    if Content_Type is not None:
        header_params["Content-Type"] = str(Content_Type)
    if Tenant_Acid is not None:
        header_params["Tenant-Acid"] = str(Tenant_Acid)
    return await greenlake_request(
        ctx,
        "POST",
        "/compute-ops-mgmt/v1beta2/schedules",
        query_params=query_params or None,
        header_params=header_params or None,
        body=body,
    )
