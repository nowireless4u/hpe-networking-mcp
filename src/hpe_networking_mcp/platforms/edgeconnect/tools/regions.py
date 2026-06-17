"""Generated EdgeConnect tools — DO NOT EDIT BY HAND.

Generated from ``vendor/edgeconnect/EdgeConnect-9-7-REST-API.json`` by the
maintainer-local EdgeConnect generator. These generated modules are committed
and are the runtime source of truth; regeneration is a release-time maintainer
workflow (the generator is intentionally not committed — see ``.gitignore``).

Tag: ``regions``
Operations in this file: 8
"""

# ruff: noqa: E501, N803
from __future__ import annotations

from typing import Annotated, Any

from fastmcp import Context
from pydantic import Field

from hpe_networking_mcp.platforms._common.annotations import Capability
from hpe_networking_mcp.platforms.edgeconnect._registry import tool
from hpe_networking_mcp.platforms.edgeconnect.client import edgeconnect_request


@tool(
    name="edgeconnect_delete_regions",
    description="DELETE /regions\n\nregionDelete527\n\nDelete a region by ID",
    capability=Capability.WRITE_DELETE,
)
async def edgeconnect_delete_regions(
    ctx: Context,
    regionId: Annotated[
        int,
        Field(
            description="Unique identifier of the region to delete. Must be a non-zero value as the default region (ID 0) cannot be deleted."
        ),
    ],
) -> Any:
    query_params: dict[str, Any] = {}
    if regionId is not None:
        query_params["regionId"] = regionId
    return await edgeconnect_request(
        ctx,
        "DELETE",
        "/regions",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_regions",
    description="GET /regions\n\nregionSingleGet528\n\nGet regions",
    capability=Capability.READ,
)
async def edgeconnect_get_regions(
    ctx: Context,
    regionId: Annotated[
        int | None,
        Field(
            default=None,
            description="Unique region identifier. When omitted, returns all regions. When provided, returns only the specified region.",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if regionId is not None:
        query_params["regionId"] = regionId
    return await edgeconnect_request(
        ctx,
        "GET",
        "/regions",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_regions_appliances",
    description="GET /regions/appliances\n\nregionAssociationGET524\n\nGet region associations for appliances",
    capability=Capability.READ,
)
async def edgeconnect_get_regions_appliances(
    ctx: Context,
    nePk: Annotated[
        str | None,
        Field(
            default=None,
            description="Network Element Primary Key - unique appliance identifier assigned by Orchestrator. Format: '<id>.NE' (e.g., '0.NE', '10.NE'). When omitted, results are returned for all appliances.",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if nePk is not None:
        query_params["nePk"] = nePk
    return await edgeconnect_request(
        ctx,
        "GET",
        "/regions/appliances",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_regions_appliances_region_id",
    description="GET /regions/appliances/regionId\n\nregionAssociationGET525\n\nGet all appliances associated with a region",
    capability=Capability.READ,
)
async def edgeconnect_get_regions_appliances_region_id(
    ctx: Context,
    regionId: Annotated[
        int,
        Field(
            description="Unique region identifier to retrieve appliances for. Region ID 0 represents the default region."
        ),
    ],
) -> Any:
    query_params: dict[str, Any] = {}
    if regionId is not None:
        query_params["regionId"] = regionId
    return await edgeconnect_request(
        ctx,
        "GET",
        "/regions/appliances/regionId",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_post_regions",
    description="POST /regions\n\nregionPost521\n\nCreate a new region",
    capability=Capability.WRITE,
)
async def edgeconnect_post_regions(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/regions",
        query_params=None,
        body=body,
    )


@tool(
    name="edgeconnect_post_regions_appliances",
    description="POST /regions/appliances\n\nregionAssociationPost523\n\nCreate or update appliance-to-region associations",
    capability=Capability.WRITE,
)
async def edgeconnect_post_regions_appliances(
    ctx: Context,
    body: Annotated[list[Any], Field(description="Request body (required)")],
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/regions/appliances",
        query_params=None,
        body=body,
    )


@tool(
    name="edgeconnect_put_regions",
    description="PUT /regions\n\nregionPut529\n\nUpdate region name",
    capability=Capability.WRITE,
)
async def edgeconnect_put_regions(
    ctx: Context,
    regionId: Annotated[
        int, Field(description="Unique identifier of the region to update. Must reference an existing region.")
    ],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    query_params: dict[str, Any] = {}
    if regionId is not None:
        query_params["regionId"] = regionId
    return await edgeconnect_request(
        ctx,
        "PUT",
        "/regions",
        query_params=query_params or None,
        body=body,
    )


@tool(
    name="edgeconnect_put_regions_appliances",
    description="PUT /regions/appliances\n\nregionAssociationPut526\n\nUpdate region association for a single appliance",
    capability=Capability.WRITE,
)
async def edgeconnect_put_regions_appliances(
    ctx: Context,
    nePk: Annotated[
        str,
        Field(
            description="Network Element Primary Key - unique appliance identifier assigned by Orchestrator. Format: '<id>.NE' (e.g., '0.NE', '10.NE')."
        ),
    ],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    query_params: dict[str, Any] = {}
    if nePk is not None:
        query_params["nePk"] = nePk
    return await edgeconnect_request(
        ctx,
        "PUT",
        "/regions/appliances",
        query_params=query_params or None,
        body=body,
    )
