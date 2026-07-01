"""Generated GreenLake tools — DO NOT EDIT BY HAND.

Generated from the vendored spec ``vendor/greenlake/reporting.json`` by the
maintainer-local GreenLake generator. These modules are committed and are the
runtime source of truth; regeneration is a release-time maintainer workflow
(the generator is intentionally not committed — see ``.gitignore``).

Service: ``reporting``   Tag: ``report_exports``   Operations: 2
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
    name="greenlake_get_reporting_v1_report_exports_metadata",
    description="GET /reporting/v1/report-exports-metadata\n\nReport exports metadata",
    capability=Capability.READ,
)
async def greenlake_get_reporting_v1_report_exports_metadata(
    ctx: Context,
    filter: Annotated[
        str,
        Field(
            description="Limit the resources operated on by an endpoint or when used with a multiple-GET endpoint, return only the subset of resources that match the filter. The filter grammar is a subset of OData 4.0.  **NOTE:** The filter query parameter must use [URL encoding](https://en.wikipedia.org/wiki/URL_encoding). Most clients do this automatically with inputs provided to them specifically as query parameters. Encoding must be done manually for any query parameters provided as part of the URL.   The reserved characters `!` `#` `$` `&` `'` `(` `)` `*` `+` `,` `/` `:` `;` `=` `?` `@` `[` `]` must be encoded with percent encoded equivalents.  For example: the value `P06760-B21+2M212504P8` must be encoded as `P06760-B21%2B2M212504P8` when it is used in a query parameter.  | CLASS     |  EXAMPLES                                          | |-----------|----------------------------------------------------| | Types     | integer, decimal, timestamp, string, boolean, null | | Operations| eq, ne, gt, ge, lt, le, in                         | | Logic     | and, or, not                                       |"
        ),
    ],
    select: Annotated[
        str,
        Field(
            description="The select query parameter is used to limit the properties returned for a resource. The value of the select query parameter is a comma-separated list of properties."
        ),
    ],
    sort: Annotated[
        str,
        Field(
            description="The order in which to return the resources in the collection. The value of the sort query parameter is a comma separated list of sort expressions. Each sort expression is a property name optionally followed by a direction indicator asc (ascending) or desc (descending). The first sort expression in the list defines the primary sort order, the second defines the secondary sort order, and so on. If a direction indicator is omitted, the default direction is ascending."
        ),
    ],
    limit: Annotated[int | None, Field(default=None, description="The maximum number of reports to return.")] = None,
    offset: Annotated[
        int | None, Field(default=None, description="Zero-based resource offset to start the response from.")
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if filter is not None:
        query_params["filter"] = filter
    if select is not None:
        query_params["select"] = select
    if sort is not None:
        query_params["sort"] = sort
    if limit is not None:
        query_params["limit"] = limit
    if offset is not None:
        query_params["offset"] = offset
    return await greenlake_request(
        ctx,
        "GET",
        "/reporting/v1/report-exports-metadata",
        query_params=query_params or None,
    )


@tool(
    name="greenlake_post_reporting_v1_report_exports",
    description="POST /reporting/v1/report-exports\n\nReport exports",
    capability=Capability.WRITE,
)
async def greenlake_post_reporting_v1_report_exports(
    ctx: Context,
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request body")] = None,
) -> Any:
    return await greenlake_request(
        ctx,
        "POST",
        "/reporting/v1/report-exports",
        body=body,
    )
