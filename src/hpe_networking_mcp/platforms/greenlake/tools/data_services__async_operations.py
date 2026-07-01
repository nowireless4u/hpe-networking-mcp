"""Generated GreenLake tools — DO NOT EDIT BY HAND.

Generated from the vendored spec ``vendor/greenlake/data-services.json`` by the
maintainer-local GreenLake generator. These modules are committed and are the
runtime source of truth; regeneration is a release-time maintainer workflow
(the generator is intentionally not committed — see ``.gitignore``).

Service: ``data-services``   Tag: ``async_operations``   Operations: 2
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
    name="greenlake_get_data_services_v1beta1_async_operations",
    description="GET /data-services/v1beta1/async-operations\n\nListAsyncOperations\n\nReturns a list of async-operations accessible by the user",
    capability=Capability.READ,
)
async def greenlake_get_data_services_v1beta1_async_operations(
    ctx: Context,
    offset: Annotated[
        int | None,
        Field(
            default=None,
            description="The offset query parameter should be used in conjunction with limit for paging, e.g.: offset=30&&limit=10. The offset is the number of items from the beginning of the result set to the first item included in the response.",
        ),
    ] = None,
    limit: Annotated[
        int | None,
        Field(
            default=None,
            description="The limit query parameter should be used in conjunction with offset for paging, e.g.: offset=30&&limit=10. The limit is the maximum number of items to include in the response.",
        ),
    ] = None,
    filter: Annotated[str | None, Field(default=None, description="The expression to filter responses.")] = None,
    sort: Annotated[
        str | None,
        Field(
            default=None,
            description='A comma separated list of properties to sort by, followed by a direction  indicator ("asc" or "desc"). If no direction indicator is specified the  default order is ascending.',
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
        "/data-services/v1beta1/async-operations",
        query_params=query_params or None,
    )


@tool(
    name="greenlake_get_data_services_v1beta1_async_operations_id",
    description="GET /data-services/v1beta1/async-operations/{id}\n\nGetAsyncOperation\n\nReturns details of a specific async-operation",
    capability=Capability.READ,
)
async def greenlake_get_data_services_v1beta1_async_operations_id(
    ctx: Context,
    id: Annotated[str, Field(description="The UUID of the object")],
    select: Annotated[
        str | None, Field(default=None, description="A list of properties to include in the response.")
    ] = None,
) -> Any:
    path = f"/data-services/v1beta1/async-operations/{path_seg(id)}"
    query_params: dict[str, Any] = {}
    if select is not None:
        query_params["select"] = select
    return await greenlake_request(
        ctx,
        "GET",
        path,
        query_params=query_params or None,
    )
