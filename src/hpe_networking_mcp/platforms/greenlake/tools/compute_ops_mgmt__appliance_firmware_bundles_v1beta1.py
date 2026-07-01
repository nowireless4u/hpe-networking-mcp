"""Generated GreenLake tools — DO NOT EDIT BY HAND.

Generated from the vendored spec ``vendor/greenlake/compute-ops-mgmt.json`` by the
maintainer-local GreenLake generator. These modules are committed and are the
runtime source of truth; regeneration is a release-time maintainer workflow
(the generator is intentionally not committed — see ``.gitignore``).

Service: ``compute-ops-mgmt``   Tag: ``appliance_firmware_bundles_v1beta1``   Operations: 2
"""

# ruff: noqa: E501, N803
from __future__ import annotations

from typing import Annotated, Any

from fastmcp import Context
from pydantic import Field

from hpe_networking_mcp.platforms._common.annotations import Capability
from hpe_networking_mcp.platforms._common.url import path_seg
from hpe_networking_mcp.platforms.greenlake._registry import tool
from hpe_networking_mcp.platforms.greenlake.client import greenlake_request


@tool(
    name="greenlake_get_compute_ops_mgmt_v1beta1_appliance_firmware_bundles",
    description="GET /compute-ops-mgmt/v1beta1/appliance-firmware-bundles\n\nget_v1beta1_appliance_firmware_bundles\n\nList all appliance firmware bundles",
    capability=Capability.READ,
)
async def greenlake_get_compute_ops_mgmt_v1beta1_appliance_firmware_bundles(
    ctx: Context,
    offset: Annotated[
        int | None, Field(default=None, description="Zero-based resource offset to start the response from")
    ] = None,
    limit: Annotated[int | None, Field(default=None, description="The maximum number of records to return.")] = None,
    sort: Annotated[
        str | None,
        Field(
            default=None,
            description="The order in which to return the resources in the collection.  The value of the sort query parameter is a comma separated list of sort expressions.  Each sort expression is a property name optionally followed by a direction indicator asc (ascending) or desc  (descending).  The first sort expression in the list defines the primary sort order, the second defines the secondary sort order,  and so on. If a direciton indicator is omitted the default direction is ascending.",
        ),
    ] = None,
    filter: Annotated[
        str | None,
        Field(
            default=None,
            description="Limit the resources operated on by an endpoint or when used with a multiple-GET endpoint, return only the subset of resources that match the filter. The filter grammar is a subset of OData 4.0.  NOTE: The filter query parameter must use [URL encoding](https://en.wikipedia.org/wiki/URL_encoding). Most clients do this automatically with inputs provided to them specifically as query parameters. Encoding must be done manually for any query parameters provided as part of the URL.   The reserved characters `!` `#` `$` `&` `'` `(` `)` `*` `+` `,` `/` `:` `;` `=` `?` `@` `[` `]` must be encoded with percent encoded equivalents. Server IDs contain a `+`, which must be encoded as `%2B`.   For example: the value `P06760-B21+2M212504P8` must be encoded as `P06760-B21%2B2M212504P8` when it is used in a query parameter.  | CLASS     |  EXAMPLES                                          | |-----------|----------------------------------------------------| | Types     | integer, decimal, timestamp, string, boolean, null | | Operations| eq, ne, gt, ge, lt, le, in                         | | Logic     | and, or, not                                       |  Appliance firmware can be filtered by:   - applianceVersion    - applianceType  The following examples are not an exhaustive list of all possible filtering options.",
        ),
    ] = None,
    displayAppliances: Annotated[
        bool | None,
        Field(
            default=None,
            description="Populate the applicableAppliances list in the response with all appliances which are eligible to be upgraded to that appliance firmware. This behavior is supported only when the request is provided with applianceType filter and limited to one appliance firmware bundle.",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if offset is not None:
        query_params["offset"] = offset
    if limit is not None:
        query_params["limit"] = limit
    if sort is not None:
        query_params["sort"] = sort
    if filter is not None:
        query_params["filter"] = filter
    if displayAppliances is not None:
        query_params["displayAppliances"] = displayAppliances
    return await greenlake_request(
        ctx,
        "GET",
        "/compute-ops-mgmt/v1beta1/appliance-firmware-bundles",
        query_params=query_params or None,
    )


@tool(
    name="greenlake_get_compute_ops_mgmt_v1beta1_appliance_firmware_bundles_id",
    description="GET /compute-ops-mgmt/v1beta1/appliance-firmware-bundles/{id}\n\nget_v1beta1_appliance_firmware_bundle_by_id\n\nGet an appliance firmware bundle by ID",
    capability=Capability.READ,
)
async def greenlake_get_compute_ops_mgmt_v1beta1_appliance_firmware_bundles_id(
    ctx: Context,
    id: Annotated[str, Field(description="Unique Appliance firmware bundle identifier")],
) -> Any:
    path = f"/compute-ops-mgmt/v1beta1/appliance-firmware-bundles/{path_seg(id)}"
    return await greenlake_request(
        ctx,
        "GET",
        path,
    )
