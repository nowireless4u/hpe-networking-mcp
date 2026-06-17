"""Generated EdgeConnect tools — DO NOT EDIT BY HAND.

Generated from ``vendor/edgeconnect/EdgeConnect-9-7-REST-API.json`` by the
maintainer-local EdgeConnect generator. These generated modules are committed
and are the runtime source of truth; regeneration is a release-time maintainer
workflow (the generator is intentionally not committed — see ``.gitignore``).

Tag: ``overlays``
Operations in this file: 10
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
    name="edgeconnect_delete_gms_overlays_config",
    description="DELETE /gms/overlays/config\n\ndeleteExistingOverlay322\n\nDelete an overlay configuration",
    capability=Capability.WRITE_DELETE,
)
async def edgeconnect_delete_gms_overlays_config(
    ctx: Context,
    overlayId: Annotated[
        str, Field(description="The unique identifier of the overlay to delete. Must be a valid existing overlay ID.")
    ],
) -> Any:
    query_params: dict[str, Any] = {}
    if overlayId is not None:
        query_params["overlayId"] = overlayId
    return await edgeconnect_request(
        ctx,
        "DELETE",
        "/gms/overlays/config",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_gms_overlays_config",
    description="GET /gms/overlays/config\n\ngetOverlay323\n\nGet overlay configurations",
    capability=Capability.READ,
)
async def edgeconnect_get_gms_overlays_config(
    ctx: Context,
    overlayId: Annotated[
        int | None,
        Field(
            default=None,
            description="Unique identifier of a specific overlay to retrieve. When omitted, all overlays are returned.",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if overlayId is not None:
        query_params["overlayId"] = overlayId
    return await edgeconnect_request(
        ctx,
        "GET",
        "/gms/overlays/config",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_gms_overlays_config_max_num_of_overlays",
    description="GET /gms/overlays/config/maxNumOfOverlays\n\ngetMaxNumberOfOverlays316\n\nGet maximum overlay limit",
    capability=Capability.READ,
)
async def edgeconnect_get_gms_overlays_config_max_num_of_overlays(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/gms/overlays/config/maxNumOfOverlays",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_gms_overlays_config_regions",
    description="GET /gms/overlays/config/regions\n\nGetRegionalOverlay320\n\nGet regional overlay configurations",
    capability=Capability.READ,
)
async def edgeconnect_get_gms_overlays_config_regions(
    ctx: Context,
    overlayId: Annotated[
        int | None,
        Field(
            default=None,
            description="Unique identifier of the overlay to retrieve. Must be provided together with regionId to fetch a specific regional configuration.",
        ),
    ] = None,
    regionId: Annotated[
        int | None,
        Field(
            default=None,
            description="Region identifier for the overlay configuration. Use 0 for global configuration, or a positive integer for regional configurations. Must be provided together with overlayId.",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if overlayId is not None:
        query_params["overlayId"] = overlayId
    if regionId is not None:
        query_params["regionId"] = regionId
    return await edgeconnect_request(
        ctx,
        "GET",
        "/gms/overlays/config/regions",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_gms_overlays_priority",
    description="GET /gms/overlays/priority\n\ngetOverlayPriorityMap325\n\nGet overlay priority order mapping",
    capability=Capability.READ,
)
async def edgeconnect_get_gms_overlays_priority(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/gms/overlays/priority",
        query_params=None,
    )


@tool(
    name="edgeconnect_post_gms_overlays_config",
    description="POST /gms/overlays/config\n\naddNewOverlay315\n\nCreate a new overlay configuration",
    capability=Capability.WRITE,
)
async def edgeconnect_post_gms_overlays_config(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/gms/overlays/config",
        query_params=None,
        body=body,
    )


@tool(
    name="edgeconnect_post_gms_overlays_config_regions",
    description="POST /gms/overlays/config/regions\n\nPostAllRegionalOverlays318\n\nCreate batch regional overlay configurations",
    capability=Capability.WRITE,
)
async def edgeconnect_post_gms_overlays_config_regions(
    ctx: Context,
    body: Annotated[list[Any], Field(description="Request body (required)")],
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/gms/overlays/config/regions",
        query_params=None,
        body=body,
    )


@tool(
    name="edgeconnect_post_gms_overlays_priority",
    description="POST /gms/overlays/priority\n\nsaveOverlayPriority326\n\nUpdate overlay priority order",
    capability=Capability.WRITE,
)
async def edgeconnect_post_gms_overlays_priority(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/gms/overlays/priority",
        query_params=None,
        body=body,
    )


@tool(
    name="edgeconnect_put_gms_overlays_config",
    description="PUT /gms/overlays/config\n\nupdateExistingOverlay324\n\nUpdate an existing overlay configuration",
    capability=Capability.WRITE,
)
async def edgeconnect_put_gms_overlays_config(
    ctx: Context,
    overlayId: Annotated[
        int, Field(description="Unique identifier of the overlay to update. Must reference an existing overlay ID.")
    ],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    query_params: dict[str, Any] = {}
    if overlayId is not None:
        query_params["overlayId"] = overlayId
    return await edgeconnect_request(
        ctx,
        "PUT",
        "/gms/overlays/config",
        query_params=query_params or None,
        body=body,
    )


@tool(
    name="edgeconnect_put_gms_overlays_config_regions",
    description="PUT /gms/overlays/config/regions\n\nModifyRegionalOverlay321\n\nUpdate regional overlay configurations",
    capability=Capability.WRITE,
)
async def edgeconnect_put_gms_overlays_config_regions(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await edgeconnect_request(
        ctx,
        "PUT",
        "/gms/overlays/config/regions",
        query_params=None,
        body=body,
    )
