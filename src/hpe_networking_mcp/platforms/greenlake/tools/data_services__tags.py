"""Generated GreenLake tools — DO NOT EDIT BY HAND.

Generated from the vendored spec ``vendor/greenlake/data-services.json`` by the
maintainer-local GreenLake generator. These modules are committed and are the
runtime source of truth; regeneration is a release-time maintainer workflow
(the generator is intentionally not committed — see ``.gitignore``).

Service: ``data-services``   Tag: ``tags``   Operations: 1
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
    name="greenlake_get_data_services_v1beta1_tags",
    description="GET /data-services/v1beta1/tags\n\nListTags\n\nGET tags",
    capability=Capability.READ,
)
async def greenlake_get_data_services_v1beta1_tags(
    ctx: Context,
    select: Annotated[
        str | None,
        Field(
            default=None,
            description="A list of properties to include in the response. Service currently only supports specification of all fields.",
        ),
    ] = None,
    filter: Annotated[
        str | None,
        Field(
            default=None,
            description='The set of tags returned in the response. The supported comparisons are:   - “eq” : Valid for number, boolean and string properties.   - “ne” : Valid for number, boolean and string properties.   - "contains"  Syntax:   - “eq” : filter=\\<property\\> eq \\<value\\>   - “ne” : filter=\\<property\\> ne \\<value\\>   - "startswith" : filter=startswith(key, \'Houston\')   - "startswith" : filter=startswith(value, \'Houston\') You can use "and" to filter on multiple fields    "filter=\\<property1\\> eq \\<value1\\> and \\<property2\\> ne \\<value2\\>" Examples:   GET /data-services/v1beta1/tags?filter=key eq Houston   GET /data-services/v1beta1/tags?filter=startswith(key, Houston) and value eq Volume Filters are supported on following attributes:   - key   - value',
        ),
    ] = None,
    sort: Annotated[
        str | None,
        Field(
            default=None,
            description='A comma separated list of properties to sort by, followed by a direction  indicator ("asc" or "desc"). Default order is ascending.  Service only supports sorting by 1 property per request. Supported fields  include: - key - value - If specified, a secondary sort by "key asc" is included to guarantee consistent paging behavior.',
        ),
    ] = None,
    offset: Annotated[
        int | None, Field(default=None, description="The number of results to skip. This is used for paging results.")
    ] = None,
    limit: Annotated[int | None, Field(default=None, description="The number of results to return.")] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if select is not None:
        query_params["select"] = select
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
        "/data-services/v1beta1/tags",
        query_params=query_params or None,
    )
