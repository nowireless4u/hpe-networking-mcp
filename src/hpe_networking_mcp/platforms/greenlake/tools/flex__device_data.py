"""Generated GreenLake tools — DO NOT EDIT BY HAND.

Generated from the vendored spec ``vendor/greenlake/flex.json`` by the
maintainer-local GreenLake generator. These modules are committed and are the
runtime source of truth; regeneration is a release-time maintainer workflow
(the generator is intentionally not committed — see ``.gitignore``).

Service: ``flex``   Tag: ``device_data``   Operations: 2
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
    name="greenlake_get_flex_v1beta1_devices",
    description="GET /flex/v1beta1/devices\n\ngetDevices\n\nGet and search for Device",
    capability=Capability.READ,
)
async def greenlake_get_flex_v1beta1_devices(
    ctx: Context,
    filter: Annotated[
        str | None,
        Field(
            default=None,
            description="Filter expressions consisting of simple comparison operations joined by logical operators. <br> For the v1beta1 API, the following fields are supported for filtering under the [ODATA specification](https://www.odata.org/documentation/):   * `id`   * `macAddress`   * `serialNumber`   * `resourceId`   * `partNumber`   * `name`   * `type`   * `model`   * `make`   * `billingAccountName`   * `billingTier` <br>",
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
            description="Comma separated list of fields to be sorted by in the response. The default sorting order is by resourceId in ascending order.",
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
        "/flex/v1beta1/devices",
        query_params=query_params or None,
    )


@tool(
    name="greenlake_get_flex_v1beta1_devices_id",
    description="GET /flex/v1beta1/devices/{id}\n\ngetDevice\n\nGet a single device by device resource ID",
    capability=Capability.READ,
)
async def greenlake_get_flex_v1beta1_devices_id(
    ctx: Context,
    id: Annotated[str, Field(description="path parameter 'id'")],
) -> Any:
    path = f"/flex/v1beta1/devices/{path_seg(id)}"
    return await greenlake_request(
        ctx,
        "GET",
        path,
    )
