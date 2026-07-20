"""Generated GreenLake tools — DO NOT EDIT BY HAND.

Generated from the vendored spec ``vendor/greenlake/service-catalog__service-registry-v1beta1-service-catalog-v1beta1-nbapi.json`` by the
maintainer-local GreenLake generator. These modules are committed and are the
runtime source of truth; regeneration is a release-time maintainer workflow
(the generator is intentionally not committed — see ``.gitignore``).

Service: ``service-catalog``   Tag: ``service_offer_regions``   Operations: 2
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
    name="greenlake_get_service_catalog_v1beta1_service_offer_regions",
    description="GET /service-catalog/v1beta1/service-offer-regions\n\ngetServiceOfferRegions\n\nGet service offer regions",
    capability=Capability.READ,
)
async def greenlake_get_service_catalog_v1beta1_service_offer_regions(
    ctx: Context,
    next: Annotated[
        str | None,
        Field(default=None, description="Specifies the pagination cursor for the next page of service offer regions."),
    ] = None,
    limit: Annotated[
        int | None, Field(default=None, description="Specifies the number of results to be returned.")
    ] = None,
    filter: Annotated[
        str | None,
        Field(
            default=None,
            description="The `filter` query parameter is used to filter the set of resources returned in a `GET` request. The returned set of resources must match the criteria in the filter query parameter.<br><br> The value of the `filter` query parameter is a subset of [OData 4.0](https://www.odata.org/documentation/) filter expressions consisting of simple comparison operations joined by logical operators.<br><br>**Supported fields**: `serviceOfferId`, `status`, and `region`.<br>**Supported operand**: `eq`<br>**Supported operations**: `and`",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if next is not None:
        query_params["next"] = next
    if limit is not None:
        query_params["limit"] = limit
    if filter is not None:
        query_params["filter"] = filter
    return await greenlake_request(
        ctx,
        "GET",
        "/service-catalog/v1beta1/service-offer-regions",
        query_params=query_params or None,
    )


@tool(
    name="greenlake_get_service_catalog_v1beta1_service_offer_regions_id",
    description="GET /service-catalog/v1beta1/service-offer-regions/{id}\n\ngetServiceOfferRegion\n\nGet service offer region",
    capability=Capability.READ,
)
async def greenlake_get_service_catalog_v1beta1_service_offer_regions_id(
    ctx: Context,
    id: Annotated[str, Field(description="The unique service offer region ID.")],
) -> Any:
    path = f"/service-catalog/v1beta1/service-offer-regions/{path_seg(id)}"
    return await greenlake_request(
        ctx,
        "GET",
        path,
    )
