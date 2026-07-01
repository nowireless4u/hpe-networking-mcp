"""Generated GreenLake tools — DO NOT EDIT BY HAND.

Generated from the vendored spec ``vendor/greenlake/wellness.json`` by the
maintainer-local GreenLake generator. These modules are committed and are the
runtime source of truth; regeneration is a release-time maintainer workflow
(the generator is intentionally not committed — see ``.gitignore``).

Service: ``wellness``   Tag: ``support_cases``   Operations: 3
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
    name="greenlake_get_wellness_v2_support_cases",
    description="GET /wellness/v2/support-cases\n\ngetSupportCases\n\nGet a list of support cases",
    capability=Capability.READ,
)
async def greenlake_get_wellness_v2_support_cases(
    ctx: Context,
    filter: Annotated[
        str | None,
        Field(
            default=None,
            description="The `filter` query parameter is used to filter a set of resources. The returned set of resources matches the criteria in the filter query parameter. The value of the filter query parameter is a subset of [OData V4](https://www.odata.org/documentation/) filter expressions consisting of simple comparison operations joined by logical operators.  | Class | Supported | |---|---| | Types | string, timestamp, guid | | Comparison | `eq`, `ne`, `gt`, `ge`, `lt`, `le`, `in` | | Logical Expressions | `and` | | Functions | `contains()`, `startswith()`, `endswith()` |  The following examples are not an exhaustive list of all possible filtering options.",
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
        int | None, Field(default=None, description="Specifies the number of support cases to be returned.")
    ] = None,
    next: Annotated[
        str | None,
        Field(
            default=None,
            description="Specifies the event ID, which acts as the pagination cursor for the next page of support cases.",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if filter is not None:
        query_params["filter"] = filter
    if select is not None:
        query_params["select"] = select
    if limit is not None:
        query_params["limit"] = limit
    if next is not None:
        query_params["next"] = next
    return await greenlake_request(
        ctx,
        "GET",
        "/wellness/v2/support-cases",
        query_params=query_params or None,
    )


@tool(
    name="greenlake_get_wellness_v2_support_cases_id",
    description="GET /wellness/v2/support-cases/{id}\n\ngetSupportCase\n\nGet support case with specific ID",
    capability=Capability.READ,
)
async def greenlake_get_wellness_v2_support_cases_id(
    ctx: Context,
    id: Annotated[str, Field(description="The support case ID.")],
) -> Any:
    path = f"/wellness/v2/support-cases/{path_seg(id)}"
    return await greenlake_request(
        ctx,
        "GET",
        path,
    )


@tool(
    name="greenlake_post_wellness_v2_support_cases",
    description="POST /wellness/v2/support-cases\n\ncreateSupportCase\n\nCreate a support case",
    capability=Capability.WRITE,
)
async def greenlake_post_wellness_v2_support_cases(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await greenlake_request(
        ctx,
        "POST",
        "/wellness/v2/support-cases",
        body=body,
    )
