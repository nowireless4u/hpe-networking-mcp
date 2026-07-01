"""Generated GreenLake tools — DO NOT EDIT BY HAND.

Generated from the vendored spec ``vendor/greenlake/tags.json`` by the
maintainer-local GreenLake generator. These modules are committed and are the
runtime source of truth; regeneration is a release-time maintainer workflow
(the generator is intentionally not committed — see ``.gitignore``).

Service: ``tags``   Tag: ``tags_v1``   Operations: 2
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
    name="greenlake_get_tags_v1_tag_resources",
    description="GET /tags/v1/tag-resources\n\ngetTagResourcesV1\n\nGet all the tagged resources for a workspace",
    capability=Capability.READ,
)
async def greenlake_get_tags_v1_tag_resources(
    ctx: Context,
    filter: Annotated[
        str | None,
        Field(
            default=None,
            description="Filter expressions consisting of simple comparison operations joined by logical operators. <br> | CLASS      |   EXAMPLES                                         | |------------|----------------------------------------------------| | Types      | string                                             | | Operations | eq                                                 | | Logic      | and, or                                            | | Properties | `id`, `resourceType`                               |  **NOTE:** Use the `filter-tags` query parameter to filter tags. <br>  The examples are not an exhaustive list of all possible filtering options.",
        ),
    ] = None,
    filter_tags: Annotated[
        str | None,
        Field(
            default=None,
            description="Filter expressions consisting of simple comparison operations applied on the assigned tags or their values. The comparison operations are case-insensitive. <br> | CLASS      |   EXAMPLES                                         | |------------|----------------------------------------------------| | Types      | string                                             | | Operations | eq, ne, contains()                                 |  **NOTE:** Logical operators are not currently supported.  <br>  The examples are not an exhaustive list of all possible filtering on tags options.",
        ),
    ] = None,
    sort: Annotated[
        str | None,
        Field(
            default=None,
            description="A comma separated list of sort expressions. A sort expression is a property name optionally followed by a direction indicator `asc` or `desc`. If no direction is provided, ascending order is followed by default. If no sort expressions are specified for this query parameter, the response will be sorted by the `createdAt` timestamp in descending order. Only `id`, `createdAt`, and `updatedAt` are supported for sorting.",
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
        Field(default=None, description="Specifies the number of results to be returned. The default value is 100."),
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
        "/tags/v1/tag-resources",
        query_params=query_params or None,
    )


@tool(
    name="greenlake_get_tags_v1_tags",
    description="GET /tags/v1/tags\n\ngetTagsV1\n\nGet tags associated to a workspace",
    capability=Capability.READ,
)
async def greenlake_get_tags_v1_tags(
    ctx: Context,
    filter: Annotated[
        str | None,
        Field(
            default=None,
            description="Filter expressions consisting of simple comparison operations joined by logical operators. <br> | CLASS      |   EXAMPLES                                         | |------------|----------------------------------------------------| | Types      | string                                             | | Operations | eq, contains()                                     | | Logic      | and, or                                            | | Properties | `id`, `key`, `value`                               |  The examples are not an exhaustive list of all possible filtering options.",
        ),
    ] = None,
    sort: Annotated[
        str | None,
        Field(
            default=None,
            description="A comma separated list of sort expressions. A sort expression is a property name optionally followed by a direction indicator 'asc' or 'desc'. If no direction is provided, ascending order is followed by  default. If no sort expressions are specified for this query parameter, the response will be sorted by the `createdAt` timestamp in descending order. `type` and `resourceCount` are not supported for sorting.",
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
        Field(default=None, description="Specifies the number of results to be returned. The default value is 100."),
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
        "/tags/v1/tags",
        query_params=query_params or None,
    )
