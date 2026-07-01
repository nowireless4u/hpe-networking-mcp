"""Generated GreenLake tools — DO NOT EDIT BY HAND.

Generated from the vendored spec ``vendor/greenlake/data-services.json`` by the
maintainer-local GreenLake generator. These modules are committed and are the
runtime source of truth; regeneration is a release-time maintainer workflow
(the generator is intentionally not committed — see ``.gitignore``).

Service: ``data-services``   Tag: ``settings``   Operations: 3
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
    name="greenlake_get_data_services_v1beta1_settings",
    description="GET /data-services/v1beta1/settings\n\nSettingsList\n\nList settings for the current account.",
    capability=Capability.READ,
)
async def greenlake_get_data_services_v1beta1_settings(
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
            description="The expression to use for filtering responses. You can filter on the following properties: customerId, id, name, possibleValues, currentValue, settingDescription, lastUpdatedBy, lastUpdatedAt, externalApplicationName. You can combine multiple comparison operators using AND. The comparisons supported are the following: “eq” : Valid for number, boolean and string properties. “gt” : Valid for number or string timestamp properties. “lt” :  Valid for number or string timestamp properties “in” : Valid for an array of strings Syntax: “eq” : filter=\\<property> eq \\<value> {host:port}/data-services/v1beta1/settings?filter=\\<property> eq \\<value> “gt” : filter=\\<property> gt \\<value> {host:port}/data-services/v1beta1/settings?filter=\\<property> gt \\<value> “lt” : filter=\\<property> lt \\<value> {host:port}/data-services/v1beta1/settings?filter=\\<property> lt \\<value> “in” : filter=\\<property> in \\<value> {host:port}/data-services/v1beta1/settings?filter=\\<property> in \\<value> * Use AND to filter on multiple properties: {host:port}/data-services/v1beta1/settings?filter=\\<property1> eq \\<value1> and \\<property2> lt \\<value2> * To filter multiple values on one property e.g. filter=name in ('foo','bar') {host:port}/data-services/v1beta1/settings?filter=foo%bar%20in%20severity Examples: GET /data-services/v1beta1/settings?filter=name eq 'SETTINGNAME' GET /data-services/v1beta1/settings?filter=name eq 'SETTINGNAME' and lastUpdatedBy eq 'CREATED' GET /data-services/v1beta1/settings?filter=relatedObjectType in ('NIMBLE-VOLUME') Filters are supported on following attributes: customerId, id, name, possibleValues, currentValue, settingDescription, lastUpdatedBy, lastUpdatedAt, externalApplicationName",
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
            description="A comma-separated list of properties to include in response. If this is omitted, all properties are returned.",
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
        "/data-services/v1beta1/settings",
        query_params=query_params or None,
    )


@tool(
    name="greenlake_get_data_services_v1beta1_settings_id",
    description="GET /data-services/v1beta1/settings/{id}\n\nSettingGet\n\nReturns setting with given Id",
    capability=Capability.READ,
)
async def greenlake_get_data_services_v1beta1_settings_id(
    ctx: Context,
    id: Annotated[str, Field(description="The ID of the setting")],
) -> Any:
    path = f"/data-services/v1beta1/settings/{path_seg(id)}"
    return await greenlake_request(
        ctx,
        "GET",
        path,
    )


@tool(
    name="greenlake_patch_data_services_v1beta1_settings_id",
    description="PATCH /data-services/v1beta1/settings/{id}\n\nSettingUpdate\n\nUpdate a setting",
    capability=Capability.WRITE,
)
async def greenlake_patch_data_services_v1beta1_settings_id(
    ctx: Context,
    id: Annotated[str, Field(description="The ID of the setting")],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    path = f"/data-services/v1beta1/settings/{path_seg(id)}"
    return await greenlake_request(
        ctx,
        "PATCH",
        path,
        body=body,
    )
