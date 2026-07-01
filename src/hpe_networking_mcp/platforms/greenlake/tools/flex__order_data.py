"""Generated GreenLake tools — DO NOT EDIT BY HAND.

Generated from the vendored spec ``vendor/greenlake/flex.json`` by the
maintainer-local GreenLake generator. These modules are committed and are the
runtime source of truth; regeneration is a release-time maintainer workflow
(the generator is intentionally not committed — see ``.gitignore``).

Service: ``flex``   Tag: ``order_data``   Operations: 2
"""

# ruff: noqa: E501
from __future__ import annotations

from typing import Annotated, Any

from fastmcp import Context
from pydantic import Field

from hpe_networking_mcp.platforms._common.annotations import Capability
from hpe_networking_mcp.platforms.greenlake._registry import tool
from hpe_networking_mcp.platforms.greenlake.client import greenlake_request


@tool(
    name="greenlake_get_flex_v1beta1_orders",
    description="GET /flex/v1beta1/orders\n\ngetOrders\n\nGet and search for orders",
    capability=Capability.READ,
)
async def greenlake_get_flex_v1beta1_orders(
    ctx: Context,
    filter: Annotated[
        str | None,
        Field(
            default=None,
            description="Filter expressions consisting of simple comparison operations joined by logical operators. <br> For the v1beta1 API, the following fields are supported for filtering under the [ODATA specification](https://www.odata.org/documentation/):   * `id`   * `billingAccountId`   * `sowId`   * `billingAccountName`   * `customerName`   * `resellerName`   * `partnerName`   * `distributorName`   * `isFlexPartner` <br>",
        ),
    ] = None,
    select: Annotated[
        str | None,
        Field(
            default=None,
            description="Comma separated list of fields to be returned in the response. If not provided, all fields will be returned. <br> All fields are supported.",
        ),
    ] = None,
    sort: Annotated[
        str | None,
        Field(
            default=None,
            description="Comma separated list of fields to be sorted by in the response. The default sorting order is by `orderEndDate` in ascending order.",
        ),
    ] = None,
    offset: Annotated[
        int | None, Field(default=None, description="Zero-based resource offset to start the response from.")
    ] = None,
    limit: Annotated[
        int | None, Field(default=None, description="Number of entities to return with a maximum of 100.")
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if filter is not None:
        query_params["filter"] = filter
    if select is not None:
        query_params["select"] = select
    if sort is not None:
        query_params["sort"] = sort
    if offset is not None:
        query_params["offset"] = offset
    if limit is not None:
        query_params["limit"] = limit
    return await greenlake_request(
        ctx,
        "GET",
        "/flex/v1beta1/orders",
        query_params=query_params or None,
    )


@tool(
    name="greenlake_get_flex_v1beta1_orders_transform",
    description="GET /flex/v1beta1/orders/transform\n\ngetOrdersTransform\n\nGet distinct transformative data for orders",
    capability=Capability.READ,
)
async def greenlake_get_flex_v1beta1_orders_transform(
    ctx: Context,
    group_by: Annotated[
        str,
        Field(
            description="Field to be grouped by. Will return unique results of that type. <br> Supported fields are:   * `sowId`   * `customerName`   * `billingAccountName`   * `billingAccountId`   * `partnerName` <br> (partnerName is a unique combined set of resellerName and distributorName)"
        ),
    ],
    filter: Annotated[
        str | None,
        Field(
            default=None,
            description="Filter expressions consisting of simple comparison operations joined by logical operators. <br> For the v1beta1 API, the following fields are supported for filtering under the [ODATA specification](https://www.odata.org/documentation/):   * `billingAccountId`   * `sowId`   * `billingAccountName`   * `customerName`   * `resellerName`   * `distributorName`   * `partnerName` <br>",
        ),
    ] = None,
    sort: Annotated[
        str | None,
        Field(
            default=None,
            description="Fields to be sorted by in the response. The default sorting order is by the group-by field in ascending order. The sort field must be one of the group-by fields, if given.",
        ),
    ] = None,
    offset: Annotated[
        int | None, Field(default=None, description="Zero-based resource offset to start the response from.")
    ] = None,
    limit: Annotated[
        int | None, Field(default=None, description="Number of entities to return with a maximum of 100.")
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if group_by is not None:
        query_params["group-by"] = group_by
    if filter is not None:
        query_params["filter"] = filter
    if sort is not None:
        query_params["sort"] = sort
    if offset is not None:
        query_params["offset"] = offset
    if limit is not None:
        query_params["limit"] = limit
    return await greenlake_request(
        ctx,
        "GET",
        "/flex/v1beta1/orders/transform",
        query_params=query_params or None,
    )
