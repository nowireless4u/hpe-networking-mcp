"""Generated GreenLake tools — DO NOT EDIT BY HAND.

Generated from the vendored spec ``vendor/greenlake/device-management.json`` by the
maintainer-local GreenLake generator. These modules are committed and are the
runtime source of truth; regeneration is a release-time maintainer workflow
(the generator is intentionally not committed — see ``.gitignore``).

Service: ``device-management``   Tag: ``devices_v1beta1``   Operations: 5
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
    name="greenlake_get_devices_v1beta1_async_operations_id",
    description="GET /devices/v1beta1/async-operations/{id}\n\ngetDevicesAsyncOperationResource\n\nGet progress or status of async operations in devices",
    capability=Capability.READ,
)
async def greenlake_get_devices_v1beta1_async_operations_id(
    ctx: Context,
    id: Annotated[str, Field(description="The unique identifier of an asynchronous API operation.")],
) -> Any:
    path = f"/devices/v1beta1/async-operations/{path_seg(id)}"
    return await greenlake_request(
        ctx,
        "GET",
        path,
    )


@tool(
    name="greenlake_get_devices_v1beta1_devices",
    description="GET /devices/v1beta1/devices\n\ngetDevices\n\nGet all devices in a workspace",
    capability=Capability.READ,
)
async def greenlake_get_devices_v1beta1_devices(
    ctx: Context,
    filter: Annotated[
        str | None,
        Field(
            default=None,
            description="Filter expressions consisting of simple comparison operations joined by logical operators.<br> | CLASS               |   EXAMPLES                                         | |---------------------|----------------------------------------------------| | Types               | integer, decimal, timestamp, string, boolean, null | | Comparison          | eq, ne, gt, ge, lt, le, in                         | | Logical Expressions | and, or, not                                       |  The following examples are not an exhaustive list of all possible filtering options.",
        ),
    ] = None,
    filter_tags: Annotated[
        str | None,
        Field(
            default=None,
            description="Filter expressions consisting of simple comparison operations joined by logical operators to be applied on the assigned tags or their values.<br> | CLASS               |   EXAMPLES      | |---------------------|-----------------| | Types               | string          | | Comparison          | eq, ne, in      | | Logical Expressions | and, or, not    |",
        ),
    ] = None,
    sort: Annotated[
        str | None,
        Field(
            default=None,
            description="A comma separated list of sort expressions. A sort expression is a property name optionally followed by a direction indicator 'asc' or 'desc'. The default is ascending order.",
        ),
    ] = None,
    select: Annotated[
        list[str] | None,
        Field(
            default=None,
            description="A comma separated list of select properties to display in the response. The default is that all properties are returned.",
        ),
    ] = None,
    limit: Annotated[
        int | None,
        Field(default=None, description="Specifies the number of results to be returned. The default value is 2000."),
    ] = None,
    offset: Annotated[
        int | None,
        Field(
            default=None,
            description="Specifies the zero-based resource offset to start the response from. The default value is 0.",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if filter is not None:
        query_params["filter"] = filter
    if filter_tags is not None:
        query_params["filter-tags"] = filter_tags
    if sort is not None:
        query_params["sort"] = sort
    if select is not None:
        query_params["select"] = select
    if limit is not None:
        query_params["limit"] = limit
    if offset is not None:
        query_params["offset"] = offset
    return await greenlake_request(
        ctx,
        "GET",
        "/devices/v1beta1/devices",
        query_params=query_params or None,
    )


@tool(
    name="greenlake_get_devices_v1beta1_devices_id",
    description="GET /devices/v1beta1/devices/{id}\n\ngetDeviceById\n\nGet device information",
    capability=Capability.READ,
)
async def greenlake_get_devices_v1beta1_devices_id(
    ctx: Context,
    id: Annotated[str, Field(description="path parameter 'id'")],
) -> Any:
    path = f"/devices/v1beta1/devices/{path_seg(id)}"
    return await greenlake_request(
        ctx,
        "GET",
        path,
    )


@tool(
    name="greenlake_patch_devices_v1beta1_devices",
    description="PATCH /devices/v1beta1/devices\n\npatchDevices\n\nUpdate devices",
    capability=Capability.WRITE,
)
async def greenlake_patch_devices_v1beta1_devices(
    ctx: Context,
    id: Annotated[list[str], Field(description="Array of device resource IDs. Maximum five devices per request.")],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    query_params: dict[str, Any] = {}
    if id is not None:
        query_params["id"] = id
    return await greenlake_request(
        ctx,
        "PATCH",
        "/devices/v1beta1/devices",
        query_params=query_params or None,
        body=body,
    )


@tool(
    name="greenlake_post_devices_v1beta1_devices",
    description="POST /devices/v1beta1/devices\n\npostDevices\n\nAdd devices",
    capability=Capability.WRITE,
)
async def greenlake_post_devices_v1beta1_devices(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await greenlake_request(
        ctx,
        "POST",
        "/devices/v1beta1/devices",
        body=body,
    )
