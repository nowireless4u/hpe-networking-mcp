"""Generated GreenLake tools — DO NOT EDIT BY HAND.

Generated from the vendored spec ``vendor/greenlake/wellness.json`` by the
maintainer-local GreenLake generator. These modules are committed and are the
runtime source of truth; regeneration is a release-time maintainer workflow
(the generator is intentionally not committed — see ``.gitignore``).

Service: ``wellness``   Tag: ``events``   Operations: 3
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
    name="greenlake_get_wellness_v2_events",
    description="GET /wellness/v2/events\n\ngetAllEvents\n\nGet a list of wellness events",
    capability=Capability.READ,
)
async def greenlake_get_wellness_v2_events(
    ctx: Context,
    filter: Annotated[
        str | None,
        Field(
            default=None,
            description="The `filter` query parameter is used to filter a set of resources. The returned set of resources matches the criteria in the filter query parameter. The value of the filter query parameter is a subset of [OData V4](https://www.odata.org/documentation/) filter expressions consisting of simple comparison operations joined by logical operators.  | Class | Supported | |---|---| | Types | string, boolean, timestamp | | Comparison | `eq`, `ne`, `gt`, `ge`, `lt`, `le`, `in` | | Logical Expressions | `and` | | Functions | `contains()`, `startswith()`, `endswith()` |  The following examples are not an exhaustive list of all possible filtering options.",
        ),
    ] = None,
    text_search: Annotated[
        str | None,
        Field(
            default=None,
            description="Searches for wellness events that contain the given search string. A search string can include alphanumeric characters, a space character (Unicode `U+0020`) or a hyphen (-). Apart from space characters and hyphens, no other special characters are supported. Including an unsupported character might cause inaccurate results. The minimum length of a search string is 2 characters and maximum is 100 characters. When performing a search, it's important to use specific terms. A generic search term may cause the search to timeout. * `title` * `condition.category` * `condition.name` * `condition.severity` * `asset.name` * `asset.product` * `asset.serialNumber` * `status.currentStatus` * `supportCase.casenumber` * `supportCase.casestatus` * `serviceName` * `productName` <br><br>__Note:__ You can use both the `filter` and `text-search` parameters in the same query. If both are provided, the filter is applied first, and then text-search is performed on the filtered results.",
        ),
    ] = None,
    select: Annotated[
        str | None,
        Field(
            default=None,
            description="The `select` query parameter is used to limit the properties returned for support cases. The value of the `select` query parameter is a comma separated list of properties. All properties are returned if the select parameter is omitted.<br><br> __Note:__ Only the `total` property is supported.",
        ),
    ] = None,
    limit: Annotated[
        int | None, Field(default=None, description="Specifies the number of resources (wellness events) to fetch.")
    ] = None,
    next: Annotated[
        str | None,
        Field(
            default=None,
            description="The `next` parameter represents the ID of an event used as a pagination cursor to retrieve the next set of wellness events. The parameter must be a valid UUID and be a part of the response of the previous request.",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if filter is not None:
        query_params["filter"] = filter
    if text_search is not None:
        query_params["text-search"] = text_search
    if select is not None:
        query_params["select"] = select
    if limit is not None:
        query_params["limit"] = limit
    if next is not None:
        query_params["next"] = next
    return await greenlake_request(
        ctx,
        "GET",
        "/wellness/v2/events",
        query_params=query_params or None,
    )


@tool(
    name="greenlake_get_wellness_v2_events_id",
    description="GET /wellness/v2/events/{id}\n\ngetEvent\n\nGet wellness event with specific ID",
    capability=Capability.READ,
)
async def greenlake_get_wellness_v2_events_id(
    ctx: Context,
    id: Annotated[str, Field(description="The wellness event ID.")],
) -> Any:
    path = f"/wellness/v2/events/{path_seg(id)}"
    return await greenlake_request(
        ctx,
        "GET",
        path,
    )


@tool(
    name="greenlake_patch_wellness_v2_events_id",
    description="PATCH /wellness/v2/events/{id}\n\nupdateEvent\n\nUpdate wellness event with specific ID",
    capability=Capability.WRITE,
)
async def greenlake_patch_wellness_v2_events_id(
    ctx: Context,
    id: Annotated[str, Field(description="Event ID")],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    path = f"/wellness/v2/events/{path_seg(id)}"
    return await greenlake_request(
        ctx,
        "PATCH",
        path,
        body=body,
    )
