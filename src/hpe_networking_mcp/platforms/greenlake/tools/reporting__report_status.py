"""Generated GreenLake tools — DO NOT EDIT BY HAND.

Generated from the vendored spec ``vendor/greenlake/reporting.json`` by the
maintainer-local GreenLake generator. These modules are committed and are the
runtime source of truth; regeneration is a release-time maintainer workflow
(the generator is intentionally not committed — see ``.gitignore``).

Service: ``reporting``   Tag: ``report_status``   Operations: 2
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
    name="greenlake_get_reporting_v1_statuses",
    description="GET /reporting/v1/statuses\n\ngetReportingStatuses\n\nGet statuses of all the reports belonging to a workspace",
    capability=Capability.READ,
)
async def greenlake_get_reporting_v1_statuses(
    ctx: Context,
    filter: Annotated[str, Field(description="query parameter 'filter'")],
    sort: Annotated[
        str | None,
        Field(
            default=None,
            description="The order in which to return the resources in the collection.The value of the sort query parameter is a comma separated list of sort expressions. Each sort expression is a property name optionally followed by a direction indicator asc (ascending) or desc (descending).The first sort expression in the list defines the primary sort order, the second defines the secondary sort order, and so on. If a direction indicator is omitted the default direction is ascending.",
        ),
    ] = None,
    limit: Annotated[int | None, Field(default=None, description="The maximum number of reports to return.")] = None,
    offset: Annotated[
        int | None, Field(default=None, description="Zero-based resource offset to start the response from.")
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if filter is not None:
        query_params["filter"] = filter
    if sort is not None:
        query_params["sort"] = sort
    if limit is not None:
        query_params["limit"] = limit
    if offset is not None:
        query_params["offset"] = offset
    return await greenlake_request(
        ctx,
        "GET",
        "/reporting/v1/statuses",
        query_params=query_params or None,
    )


@tool(
    name="greenlake_get_reporting_v1_statuses_id",
    description="GET /reporting/v1/statuses/{id}\n\ngetReportingStatusById\n\nGet Report Status by ID",
    capability=Capability.READ,
)
async def greenlake_get_reporting_v1_statuses_id(
    ctx: Context,
    id: Annotated[str, Field(description="The report status identifier.")],
) -> Any:
    path = f"/reporting/v1/statuses/{path_seg(id)}"
    return await greenlake_request(
        ctx,
        "GET",
        path,
    )
