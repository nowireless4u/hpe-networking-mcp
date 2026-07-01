"""Generated GreenLake tools — DO NOT EDIT BY HAND.

Generated from the vendored spec ``vendor/greenlake/service-catalog__service-registry-v1beta1-service-catalog-v1alpha1.json`` by the
maintainer-local GreenLake generator. These modules are committed and are the
runtime source of truth; regeneration is a release-time maintainer workflow
(the generator is intentionally not committed — see ``.gitignore``).

Service: ``service-catalog``   Tag: ``unredacted_service_offer_regions``   Operations: 2
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
    name="greenlake_get_service_catalog_v1alpha1_unredacted_service_offer_regions",
    description="GET /service-catalog/v1alpha1/unredacted-service-offer-regions\n\ngetUnredactedServiceOfferRegions\n\nGet Unredacted Service Offer Regions",
    capability=Capability.READ,
)
async def greenlake_get_service_catalog_v1alpha1_unredacted_service_offer_regions(
    ctx: Context,
    next: Annotated[
        str | None,
        Field(default=None, description="Specifies the start-id for the next page of service offer regions."),
    ] = None,
    limit: Annotated[int | None, Field(default=None, description="Number of entries per page")] = None,
    service_offer_id: Annotated[
        str | None, Field(default=None, description="Get service offer regions of a service offer ID")
    ] = None,
    region: Annotated[str | None, Field(default=None, description="Get service offer regions by region")] = None,
    status: Annotated[str | None, Field(default=None, description="Get service offer regions by status")] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if next is not None:
        query_params["next"] = next
    if limit is not None:
        query_params["limit"] = limit
    if service_offer_id is not None:
        query_params["service_offer_id"] = service_offer_id
    if region is not None:
        query_params["region"] = region
    if status is not None:
        query_params["status"] = status
    return await greenlake_request(
        ctx,
        "GET",
        "/service-catalog/v1alpha1/unredacted-service-offer-regions",
        query_params=query_params or None,
    )


@tool(
    name="greenlake_get_service_catalog_v1alpha1_unredacted_service_offer_regions_id",
    description="GET /service-catalog/v1alpha1/unredacted-service-offer-regions/{id}\n\ngetUnredactedServiceOfferRegion\n\nGet Unredacted Service Offer Region",
    capability=Capability.READ,
)
async def greenlake_get_service_catalog_v1alpha1_unredacted_service_offer_regions_id(
    ctx: Context,
    id: Annotated[str, Field(description="Get service offer regions of a service offer region id")],
) -> Any:
    path = f"/service-catalog/v1alpha1/unredacted-service-offer-regions/{path_seg(id)}"
    return await greenlake_request(
        ctx,
        "GET",
        path,
    )
