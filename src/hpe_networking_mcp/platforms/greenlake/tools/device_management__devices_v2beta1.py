"""Generated GreenLake tools — DO NOT EDIT BY HAND.

Generated from the vendored spec ``vendor/greenlake/device-management.json`` by the
maintainer-local GreenLake generator. These modules are committed and are the
runtime source of truth; regeneration is a release-time maintainer workflow
(the generator is intentionally not committed — see ``.gitignore``).

Service: ``device-management``   Tag: ``devices_v2beta1``   Operations: 5
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
    name="greenlake_get_devices_v2beta1_devices",
    description="GET /devices/v2beta1/devices\n\ngetDevicesV2beta1\n\nGet all devices in a workspace",
    capability=Capability.READ,
)
async def greenlake_get_devices_v2beta1_devices(
    ctx: Context,
    filter: Annotated[
        str | None,
        Field(
            default=None,
            description="Filter expressions consisting of simple comparison operations joined by logical operators.<br> | CLASS               |   EXAMPLES                                         | |---------------------|----------------------------------------------------| | Types               | integer, decimal, timestamp, string, boolean, null | | Comparison          | eq, ne, gt, ge, lt, le, in                         | | Logical Expressions | and, or, not                                       |  The following examples are not an exhaustive list of all possible filtering options.",
        ),
    ] = None,
    sort: Annotated[
        str | None,
        Field(
            default=None,
            description="A comma separated list of sort expressions. A sort expression is a property name optionally followed by a direction indicator `asc` or `desc`. The default is ascending order.",
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
        Field(
            default=None,
            description="Specifies the number of results to be returned. The default value is 100 and the maximum is 500.",
        ),
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
        "/devices/v2beta1/devices",
        query_params=query_params or None,
    )


@tool(
    name="greenlake_get_devices_v2beta1_devices_group",
    description="GET /devices/v2beta1/devices/group\n\ngroupByDevicesV2beta1\n\nGet all devices grouped by given attribute",
    capability=Capability.READ,
)
async def greenlake_get_devices_v2beta1_devices_group(
    ctx: Context,
    group_by: Annotated[
        str,
        Field(
            description="The grouping operation supports the following fields: `make`, `source`, `category`, `manufacturedDate`, `currentSupportLevelEndDate`, `billingAccountId`, `billingTier`, `deviceType`, `ownership`, `isFlex` and `model`. `currentSupportLevelEndDate` groups on `warranty.currentSupportLevel.endDate` and uses that nested date value."
        ),
    ],
    filter: Annotated[
        str | None,
        Field(
            default=None,
            description="The filter expressions that are used to narrow down the devices before grouping. Combine multiple conditions using `and` or `or`. The following examples are not an exhaustive list of all possible filtering options.",
        ),
    ] = None,
    lower_threshold: Annotated[
        str | None,
        Field(
            default=None,
            description="Lower bound for date-based grouping.<br><br> Applies only when `group-by` is a date field (`manufacturedDate` or `currentSupportLevelEndDate`).<br> Includes devices where the grouped date is greater than or equal to this value.<br> Use with `upper-threshold` to group results into four buckets: `less_than_lower`, `lower_to_upper`, `greater_than_upper`, `missing`.<br>",
        ),
    ] = None,
    upper_threshold: Annotated[
        str | None,
        Field(
            default=None,
            description="Upper bound for date-based grouping.<br><br> Applies only when `group-by` is a date field (`manufacturedDate` or `currentSupportLevelEndDate`).<br> Includes devices where the grouped date is less than or equal to this value.<br> Use with `lower-threshold` to group results into four buckets: `less_than_lower`, `lower_to_upper`, `greater_than_upper`, `missing`.<br>",
        ),
    ] = None,
    select: Annotated[
        str | None,
        Field(
            default=None,
            description="Returns distinct values for the specified field, without counts.<br> Use this as a distinct-only variant of `group-by` (for example, get unique `make` values).<br> Value for select field should be the same as group-by field. For example, if you are grouping by `make`, then `select` should also be `make` to get distinct makes in the response.<br> Supports the same fields as `group-by`.<br>",
        ),
    ] = None,
    offset: Annotated[
        int | None, Field(default=None, description="Zero-based resource offset to start the response from.")
    ] = None,
    limit: Annotated[
        int | None, Field(default=None, description="Number of entities to return. Maximum of 100.")
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if group_by is not None:
        query_params["group-by"] = group_by
    if filter is not None:
        query_params["filter"] = filter
    if lower_threshold is not None:
        query_params["lower-threshold"] = lower_threshold
    if upper_threshold is not None:
        query_params["upper-threshold"] = upper_threshold
    if select is not None:
        query_params["select"] = select
    if offset is not None:
        query_params["offset"] = offset
    if limit is not None:
        query_params["limit"] = limit
    return await greenlake_request(
        ctx,
        "GET",
        "/devices/v2beta1/devices/group",
        query_params=query_params or None,
    )


@tool(
    name="greenlake_get_devices_v2beta1_devices_id",
    description="GET /devices/v2beta1/devices/{id}\n\ngetDeviceByIdV2Beta1\n\nGet device information",
    capability=Capability.READ,
)
async def greenlake_get_devices_v2beta1_devices_id(
    ctx: Context,
    id: Annotated[str, Field(description="path parameter 'id'")],
) -> Any:
    path = f"/devices/v2beta1/devices/{path_seg(id)}"
    return await greenlake_request(
        ctx,
        "GET",
        path,
    )


@tool(
    name="greenlake_patch_devices_v2beta1_devices",
    description="PATCH /devices/v2beta1/devices\n\npatchDevicesV2beta1\n\nUpdate devices",
    capability=Capability.WRITE,
)
async def greenlake_patch_devices_v2beta1_devices(
    ctx: Context,
    id: Annotated[
        list[str], Field(description="Array of device resource IDs. Maximum twenty five devices per request.")
    ],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
    dry_run: Annotated[
        bool | None,
        Field(
            default=None,
            description="The `dry-run` query parameter is used to perform the resource update operation (`POST`, `PUT`, `PATCH`, `DELETE`) and return a response as if the operation had completed, but without actually creating, updating, or deleting the resource. This allows you to test if the request would succeed before making the change. If set to `true`, the request is validated but not executed.",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if id is not None:
        query_params["id"] = id
    if dry_run is not None:
        query_params["dry-run"] = dry_run
    return await greenlake_request(
        ctx,
        "PATCH",
        "/devices/v2beta1/devices",
        query_params=query_params or None,
        body=body,
    )


@tool(
    name="greenlake_post_devices_v2beta1_devices",
    description="POST /devices/v2beta1/devices\n\npostDevicesV2beta1\n\nAdd devices",
    capability=Capability.WRITE,
)
async def greenlake_post_devices_v2beta1_devices(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
    dry_run: Annotated[
        bool | None,
        Field(
            default=None,
            description="The `dry-run` query parameter is used to perform the resource update operation (`POST`, `PUT`, `PATCH`, `DELETE`) and return a response as if the operation had completed, but without actually creating, updating, or deleting the resource. This allows you to test if the request would succeed before making the change. If set to `true`, the request is validated but not executed.",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if dry_run is not None:
        query_params["dry-run"] = dry_run
    return await greenlake_request(
        ctx,
        "POST",
        "/devices/v2beta1/devices",
        query_params=query_params or None,
        body=body,
    )
