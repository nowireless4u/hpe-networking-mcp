"""Generated GreenLake tools — DO NOT EDIT BY HAND.

Generated from the vendored spec ``vendor/greenlake/wellness.json`` by the
maintainer-local GreenLake generator. These modules are committed and are the
runtime source of truth; regeneration is a release-time maintainer workflow
(the generator is intentionally not committed — see ``.gitignore``).

Service: ``wellness``   Tag: ``async_operations``   Operations: 2
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
    name="greenlake_get_wellness_v2_async_operations",
    description="GET /wellness/v2/async-operations\n\ngetAllAsyncOperations\n\nGet a list of asynchronous operations",
    capability=Capability.READ,
)
async def greenlake_get_wellness_v2_async_operations(
    ctx: Context,
    filter: Annotated[
        str | None,
        Field(
            default=None,
            description="The `filter` query parameter is used to filter a set of resources. The returned set of resources matches the criteria in the filter query parameter. The value of the filter query parameter is a subset of [OData V4](https://www.odata.org/documentation/) filter expressions consisting of simple comparison operations joined by logical operators.",
        ),
    ] = None,
    limit: Annotated[
        int | None, Field(default=None, description="Specifies the number of asynchronous operations to be returned.")
    ] = None,
    next: Annotated[
        str | None,
        Field(
            default=None,
            description="Specifies the ID, which acts as the pagination cursor for the next page of asynchronous operations.",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if filter is not None:
        query_params["filter"] = filter
    if limit is not None:
        query_params["limit"] = limit
    if next is not None:
        query_params["next"] = next
    return await greenlake_request(
        ctx,
        "GET",
        "/wellness/v2/async-operations",
        query_params=query_params or None,
    )


@tool(
    name="greenlake_get_wellness_v2_async_operations_id",
    description="GET /wellness/v2/async-operations/{id}\n\ngetAsyncOperation\n\nGet asynchronous operation details",
    capability=Capability.READ,
)
async def greenlake_get_wellness_v2_async_operations_id(
    ctx: Context,
    id: Annotated[str, Field(description="The asynchronous operation `id` returned in an ansychronous API response.")],
) -> Any:
    path = f"/wellness/v2/async-operations/{path_seg(id)}"
    return await greenlake_request(
        ctx,
        "GET",
        path,
    )
