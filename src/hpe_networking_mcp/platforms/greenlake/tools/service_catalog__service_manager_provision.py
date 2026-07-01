"""Generated GreenLake tools — DO NOT EDIT BY HAND.

Generated from the vendored spec ``vendor/greenlake/service-catalog__service-catalog-v1beta1-service-catalog-v1.json`` by the
maintainer-local GreenLake generator. These modules are committed and are the
runtime source of truth; regeneration is a release-time maintainer workflow
(the generator is intentionally not committed — see ``.gitignore``).

Service: ``service-catalog``   Tag: ``service_manager_provision``   Operations: 4
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
    name="greenlake_delete_service_catalog_v1_service_manager_provisions_id",
    description="DELETE /service-catalog/v1/service-manager-provisions/{id}\n\ndelete_service_manager_provision_v1\n\nDelete a service manager provision entry",
    capability=Capability.WRITE_DELETE,
)
async def greenlake_delete_service_catalog_v1_service_manager_provisions_id(
    ctx: Context,
    id: Annotated[str, Field(description="Service manager provision ID")],
) -> Any:
    path = f"/service-catalog/v1/service-manager-provisions/{path_seg(id)}"
    return await greenlake_request(
        ctx,
        "DELETE",
        path,
    )


@tool(
    name="greenlake_get_service_catalog_v1_service_manager_provisions",
    description="GET /service-catalog/v1/service-manager-provisions\n\nget_service_manager_provisions_v1\n\nGet service manager provisions",
    capability=Capability.READ,
)
async def greenlake_get_service_catalog_v1_service_manager_provisions(
    ctx: Context,
    offset: Annotated[
        int | None, Field(default=None, description="Zero-based resource offset to start the response from.")
    ] = None,
    limit: Annotated[int | None, Field(default=None, description="The maximum number of records to return.")] = None,
    filter: Annotated[str | None, Field(default=None, description="query parameter 'filter'")] = None,
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
        "/service-catalog/v1/service-manager-provisions",
        query_params=query_params or None,
    )


@tool(
    name="greenlake_get_service_catalog_v1_service_manager_provisions_id",
    description="GET /service-catalog/v1/service-manager-provisions/{id}\n\nget_service_manager_provision_v1\n\nGet a specific service manager provision entry",
    capability=Capability.READ,
)
async def greenlake_get_service_catalog_v1_service_manager_provisions_id(
    ctx: Context,
    id: Annotated[str, Field(description="Service manager provision ID")],
) -> Any:
    path = f"/service-catalog/v1/service-manager-provisions/{path_seg(id)}"
    return await greenlake_request(
        ctx,
        "GET",
        path,
    )


@tool(
    name="greenlake_post_service_catalog_v1_service_manager_provisions",
    description="POST /service-catalog/v1/service-manager-provisions\n\ncreate_service_manager_provision\n\nProvision a service manager in a given region",
    capability=Capability.WRITE,
)
async def greenlake_post_service_catalog_v1_service_manager_provisions(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await greenlake_request(
        ctx,
        "POST",
        "/service-catalog/v1/service-manager-provisions",
        body=body,
    )
