"""Generated GreenLake tools — DO NOT EDIT BY HAND.

Generated from the vendored spec ``vendor/greenlake/service-catalog__service-registry-v1beta1-service-catalog-v1alpha1.json`` by the
maintainer-local GreenLake generator. These modules are committed and are the
runtime source of truth; regeneration is a release-time maintainer workflow
(the generator is intentionally not committed — see ``.gitignore``).

Service: ``service-catalog``   Tag: ``media``   Operations: 8
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
    name="greenlake_delete_service_catalog_v1alpha1_service_offers_id_media_media_id",
    description="DELETE /service-catalog/v1alpha1/service-offers/{id}/media/{media-id}\n\nDelete media for service offer",
    capability=Capability.WRITE_DELETE,
)
async def greenlake_delete_service_catalog_v1alpha1_service_offers_id_media_media_id(
    ctx: Context,
    id: Annotated[str, Field(description="Service offer ID")],
    media_id: Annotated[str, Field(description="Media ID")],
    If_Match: Annotated[int, Field(description="Generation version match")],
) -> Any:
    path = f"/service-catalog/v1alpha1/service-offers/{path_seg(id)}/media/{path_seg(media_id)}"
    header_params: dict[str, str] = {}
    if If_Match is not None:
        header_params["If-Match"] = str(If_Match)
    return await greenlake_request(
        ctx,
        "DELETE",
        path,
        header_params=header_params or None,
    )


@tool(
    name="greenlake_get_service_catalog_v1alpha1_media",
    description="GET /service-catalog/v1alpha1/media\n\nGet overall media",
    capability=Capability.READ,
)
async def greenlake_get_service_catalog_v1alpha1_media(
    ctx: Context,
    category: Annotated[str, Field(description="category")],
    service_offer_id: Annotated[str | None, Field(default=None, description="Service Offer ID")] = None,
    next: Annotated[
        str | None, Field(default=None, description="Specifies the start-id for the next page of media.")
    ] = None,
    limit: Annotated[int | None, Field(default=None, description="Number of entries per page")] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if category is not None:
        query_params["category"] = category
    if service_offer_id is not None:
        query_params["service_offer_id"] = service_offer_id
    if next is not None:
        query_params["next"] = next
    if limit is not None:
        query_params["limit"] = limit
    return await greenlake_request(
        ctx,
        "GET",
        "/service-catalog/v1alpha1/media",
        query_params=query_params or None,
    )


@tool(
    name="greenlake_get_service_catalog_v1alpha1_service_offers_id_media",
    description="GET /service-catalog/v1alpha1/service-offers/{id}/media\n\nGet All media for service offer",
    capability=Capability.READ,
)
async def greenlake_get_service_catalog_v1alpha1_service_offers_id_media(
    ctx: Context,
    id: Annotated[str, Field(description="Service offer ID")],
    next: Annotated[
        str | None, Field(default=None, description="Specifies the start-id for the next page of media.")
    ] = None,
    limit: Annotated[int | None, Field(default=None, description="Number of entries per page")] = None,
) -> Any:
    path = f"/service-catalog/v1alpha1/service-offers/{path_seg(id)}/media"
    query_params: dict[str, Any] = {}
    if next is not None:
        query_params["next"] = next
    if limit is not None:
        query_params["limit"] = limit
    return await greenlake_request(
        ctx,
        "GET",
        path,
        query_params=query_params or None,
    )


@tool(
    name="greenlake_get_service_catalog_v1alpha1_service_offers_id_media_media_id",
    description="GET /service-catalog/v1alpha1/service-offers/{id}/media/{media-id}\n\nGet Single media for service offer",
    capability=Capability.READ,
)
async def greenlake_get_service_catalog_v1alpha1_service_offers_id_media_media_id(
    ctx: Context,
    id: Annotated[str, Field(description="Service offer ID")],
    media_id: Annotated[str, Field(description="Media ID")],
) -> Any:
    path = f"/service-catalog/v1alpha1/service-offers/{path_seg(id)}/media/{path_seg(media_id)}"
    return await greenlake_request(
        ctx,
        "GET",
        path,
    )


@tool(
    name="greenlake_patch_service_catalog_v1alpha1_service_offers_id_media_media_id",
    description="PATCH /service-catalog/v1alpha1/service-offers/{id}/media/{media-id}\n\nPartially update media for service offer",
    capability=Capability.WRITE,
)
async def greenlake_patch_service_catalog_v1alpha1_service_offers_id_media_media_id(
    ctx: Context,
    id: Annotated[str, Field(description="Service offer ID")],
    media_id: Annotated[str, Field(description="Media ID")],
    If_Match: Annotated[int, Field(description="Generation version match")],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    path = f"/service-catalog/v1alpha1/service-offers/{path_seg(id)}/media/{path_seg(media_id)}"
    header_params: dict[str, str] = {}
    if If_Match is not None:
        header_params["If-Match"] = str(If_Match)
    return await greenlake_request(
        ctx,
        "PATCH",
        path,
        header_params=header_params or None,
        body=body,
    )


@tool(
    name="greenlake_post_service_catalog_v1alpha1_service_offers_id_media",
    description="POST /service-catalog/v1alpha1/service-offers/{id}/media\n\nUpload logo/screenshot",
    capability=Capability.WRITE,
)
async def greenlake_post_service_catalog_v1alpha1_service_offers_id_media(
    ctx: Context,
    id: Annotated[str, Field(description="Service offer ID")],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    path = f"/service-catalog/v1alpha1/service-offers/{path_seg(id)}/media"
    return await greenlake_request(
        ctx,
        "POST",
        path,
        body=body,
    )


@tool(
    name="greenlake_post_service_catalog_v1alpha1_service_offers_id_media_media_id_uploaded",
    description="POST /service-catalog/v1alpha1/service-offers/{id}/media/{media-id}/uploaded\n\nMark file upload status as UPLOADED",
    capability=Capability.WRITE,
)
async def greenlake_post_service_catalog_v1alpha1_service_offers_id_media_media_id_uploaded(
    ctx: Context,
    id: Annotated[str, Field(description="Service offer ID")],
    media_id: Annotated[str, Field(description="Media ID")],
) -> Any:
    path = f"/service-catalog/v1alpha1/service-offers/{path_seg(id)}/media/{path_seg(media_id)}/uploaded"
    return await greenlake_request(
        ctx,
        "POST",
        path,
    )


@tool(
    name="greenlake_put_service_catalog_v1alpha1_service_offers_id_media_media_id",
    description="PUT /service-catalog/v1alpha1/service-offers/{id}/media/{media-id}\n\nUpdate media for service offer",
    capability=Capability.WRITE,
)
async def greenlake_put_service_catalog_v1alpha1_service_offers_id_media_media_id(
    ctx: Context,
    id: Annotated[str, Field(description="Service offer ID")],
    media_id: Annotated[str, Field(description="Media ID")],
    If_Match: Annotated[int, Field(description="Generation version match")],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    path = f"/service-catalog/v1alpha1/service-offers/{path_seg(id)}/media/{path_seg(media_id)}"
    header_params: dict[str, str] = {}
    if If_Match is not None:
        header_params["If-Match"] = str(If_Match)
    return await greenlake_request(
        ctx,
        "PUT",
        path,
        header_params=header_params or None,
        body=body,
    )
