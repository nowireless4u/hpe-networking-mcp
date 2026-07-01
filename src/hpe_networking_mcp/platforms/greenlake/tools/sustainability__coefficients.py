"""Generated GreenLake tools — DO NOT EDIT BY HAND.

Generated from the vendored spec ``vendor/greenlake/sustainability.json`` by the
maintainer-local GreenLake generator. These modules are committed and are the
runtime source of truth; regeneration is a release-time maintainer workflow
(the generator is intentionally not committed — see ``.gitignore``).

Service: ``sustainability``   Tag: ``coefficients``   Operations: 3
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
    name="greenlake_get_sustainability_insight_ctr_v1beta1_coefficients",
    description="GET /sustainability-insight-ctr/v1beta1/coefficients\n\ngetCoefficients\n\nGet all cost and co2 coefficients",
    capability=Capability.READ,
)
async def greenlake_get_sustainability_insight_ctr_v1beta1_coefficients(
    ctx: Context,
    offset: Annotated[
        int | None, Field(default=None, description="Zero-based resource offset to start the response from.")
    ] = None,
    limit: Annotated[int | None, Field(default=None, description="Number of entities to return.")] = None,
    filter: Annotated[
        str | None,
        Field(
            default=None,
            description='Limit the coefficients operated on by this endpoint, returning only the subset of entities that match the filter. The filter grammar is a subset of OData 4.0 supporting "eq" operator only. Coefficients can be filtered by: - locationId',
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
    return await greenlake_request(
        ctx,
        "GET",
        "/sustainability-insight-ctr/v1beta1/coefficients",
        query_params=query_params or None,
    )


@tool(
    name="greenlake_get_sustainability_insight_ctr_v1beta1_coefficients_id",
    description="GET /sustainability-insight-ctr/v1beta1/coefficients/{id}\n\ngetCoefficient\n\nGet a single cost and co2 coefficient for an id",
    capability=Capability.READ,
)
async def greenlake_get_sustainability_insight_ctr_v1beta1_coefficients_id(
    ctx: Context,
    id: Annotated[str, Field(description="UUID of the coefficient mapping")],
) -> Any:
    path = f"/sustainability-insight-ctr/v1beta1/coefficients/{path_seg(id)}"
    return await greenlake_request(
        ctx,
        "GET",
        path,
    )


@tool(
    name="greenlake_post_sustainability_insight_ctr_v1beta1_coefficients",
    description="POST /sustainability-insight-ctr/v1beta1/coefficients\n\naddCoefficients\n\nCreate cost and co2 coefficients for a location",
    capability=Capability.WRITE,
)
async def greenlake_post_sustainability_insight_ctr_v1beta1_coefficients(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await greenlake_request(
        ctx,
        "POST",
        "/sustainability-insight-ctr/v1beta1/coefficients",
        body=body,
    )
