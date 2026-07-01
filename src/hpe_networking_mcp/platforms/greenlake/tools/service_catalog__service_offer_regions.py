"""Generated GreenLake tools — DO NOT EDIT BY HAND.

Generated from the vendored spec ``vendor/greenlake/service-catalog__service-registry-v1beta1-service-catalog-v1alpha1.json`` by the
maintainer-local GreenLake generator. These modules are committed and are the
runtime source of truth; regeneration is a release-time maintainer workflow
(the generator is intentionally not committed — see ``.gitignore``).

Service: ``service-catalog``   Tag: ``service_offer_regions``   Operations: 9
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
    name="greenlake_delete_service_catalog_v1alpha1_service_offer_regions_id",
    description="DELETE /service-catalog/v1alpha1/service-offer-regions/{id}\n\ndeleteServiceOfferRegion\n\nDelete Service Offer Region",
    capability=Capability.WRITE_DELETE,
)
async def greenlake_delete_service_catalog_v1alpha1_service_offer_regions_id(
    ctx: Context,
    id: Annotated[str, Field(description="Service offer region ID")],
    If_Match: Annotated[int, Field(description="Generation version match")],
    force: Annotated[bool | None, Field(default=None, description="Specifies the force-delete action")] = None,
) -> Any:
    path = f"/service-catalog/v1alpha1/service-offer-regions/{path_seg(id)}"
    query_params: dict[str, Any] = {}
    if force is not None:
        query_params["force"] = force
    header_params: dict[str, str] = {}
    if If_Match is not None:
        header_params["If-Match"] = str(If_Match)
    return await greenlake_request(
        ctx,
        "DELETE",
        path,
        query_params=query_params or None,
        header_params=header_params or None,
    )


@tool(
    name="greenlake_get_service_catalog_v1alpha1_service_offer_regions",
    description="GET /service-catalog/v1alpha1/service-offer-regions\n\ngetServiceOfferRegions\n\nGet Service Offer Regions",
    capability=Capability.READ,
)
async def greenlake_get_service_catalog_v1alpha1_service_offer_regions(
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
        "/service-catalog/v1alpha1/service-offer-regions",
        query_params=query_params or None,
    )


@tool(
    name="greenlake_get_service_catalog_v1alpha1_service_offer_regions_id",
    description="GET /service-catalog/v1alpha1/service-offer-regions/{id}\n\ngetServiceOfferRegion\n\nRetrieve the service offer region details",
    capability=Capability.READ,
)
async def greenlake_get_service_catalog_v1alpha1_service_offer_regions_id(
    ctx: Context,
    id: Annotated[str, Field(description="Service offer Region ID")],
) -> Any:
    path = f"/service-catalog/v1alpha1/service-offer-regions/{path_seg(id)}"
    return await greenlake_request(
        ctx,
        "GET",
        path,
    )


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


@tool(
    name="greenlake_patch_service_catalog_v1alpha1_service_offer_regions_id",
    description="PATCH /service-catalog/v1alpha1/service-offer-regions/{id}\n\npathcServiceOfferRegion\n\nPartially Update Service Offer Region",
    capability=Capability.WRITE,
)
async def greenlake_patch_service_catalog_v1alpha1_service_offer_regions_id(
    ctx: Context,
    id: Annotated[str, Field(description="Service Offer Region ID")],
    If_Match: Annotated[int, Field(description="Generation version match")],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
    force: Annotated[
        bool | None,
        Field(default=None, description="Specifies the force-update action that ignores the dev_accounts list check"),
    ] = None,
) -> Any:
    path = f"/service-catalog/v1alpha1/service-offer-regions/{path_seg(id)}"
    query_params: dict[str, Any] = {}
    if force is not None:
        query_params["force"] = force
    header_params: dict[str, str] = {}
    if If_Match is not None:
        header_params["If-Match"] = str(If_Match)
    return await greenlake_request(
        ctx,
        "PATCH",
        path,
        query_params=query_params or None,
        header_params=header_params or None,
        body=body,
    )


@tool(
    name="greenlake_post_service_catalog_v1alpha1_service_offer_regions",
    description="POST /service-catalog/v1alpha1/service-offer-regions\n\ncreateServiceOfferRegion\n\nCreate Service Offer Region",
    capability=Capability.WRITE,
)
async def greenlake_post_service_catalog_v1alpha1_service_offer_regions(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await greenlake_request(
        ctx,
        "POST",
        "/service-catalog/v1alpha1/service-offer-regions",
        body=body,
    )


@tool(
    name="greenlake_post_service_catalog_v1alpha1_service_offer_regions_id_onboarded",
    description="POST /service-catalog/v1alpha1/service-offer-regions/{id}/onboarded\n\nonboardServiceOfferRegion\n\nMark Service Offer Region onboarding as complete",
    capability=Capability.WRITE,
)
async def greenlake_post_service_catalog_v1alpha1_service_offer_regions_id_onboarded(
    ctx: Context,
    id: Annotated[str, Field(description="Service Offer Region ID")],
    If_Match: Annotated[int, Field(description="Generation version match")],
) -> Any:
    path = f"/service-catalog/v1alpha1/service-offer-regions/{path_seg(id)}/onboarded"
    header_params: dict[str, str] = {}
    if If_Match is not None:
        header_params["If-Match"] = str(If_Match)
    return await greenlake_request(
        ctx,
        "POST",
        path,
        header_params=header_params or None,
    )


@tool(
    name="greenlake_put_service_catalog_v1alpha1_service_offer_regions_id",
    description="PUT /service-catalog/v1alpha1/service-offer-regions/{id}\n\nupdateServiceOfferRegion\n\nUpdate Service Offer Region",
    capability=Capability.WRITE,
)
async def greenlake_put_service_catalog_v1alpha1_service_offer_regions_id(
    ctx: Context,
    id: Annotated[str, Field(description="Service Offer Region ID")],
    If_Match: Annotated[int, Field(description="Generation version match")],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
    force: Annotated[
        bool | None,
        Field(default=None, description="Specifies the force-update action that ignores the dev_accounts list check"),
    ] = None,
) -> Any:
    path = f"/service-catalog/v1alpha1/service-offer-regions/{path_seg(id)}"
    query_params: dict[str, Any] = {}
    if force is not None:
        query_params["force"] = force
    header_params: dict[str, str] = {}
    if If_Match is not None:
        header_params["If-Match"] = str(If_Match)
    return await greenlake_request(
        ctx,
        "PUT",
        path,
        query_params=query_params or None,
        header_params=header_params or None,
        body=body,
    )
