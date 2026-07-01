"""Generated GreenLake tools — DO NOT EDIT BY HAND.

Generated from the vendored spec ``vendor/greenlake/service-catalog__service-catalog-v1beta1-service-catalog-v1.json`` by the
maintainer-local GreenLake generator. These modules are committed and are the
runtime source of truth; regeneration is a release-time maintainer workflow
(the generator is intentionally not committed — see ``.gitignore``).

Service: ``service-catalog``   Tag: ``service_manager``   Operations: 4
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
    name="greenlake_get_service_catalog_v1_per_region_service_managers",
    description="GET /service-catalog/v1/per-region-service-managers\n\nper_region_service_managers_v1\n\nGet service managers by region",
    capability=Capability.READ,
)
async def greenlake_get_service_catalog_v1_per_region_service_managers(
    ctx: Context,
    offset: Annotated[
        int | None, Field(default=None, description="Zero-based resource offset to start the response from.")
    ] = None,
    limit: Annotated[int | None, Field(default=None, description="The maximum number of records to return.")] = None,
    filter: Annotated[
        str | None,
        Field(
            default=None,
            description="Limit the resources operated on by an endpoint and return only the subset of resources that match the filter using an [OData V4](https://www.odata.org/documentation/) formatted filter string. Service manager by region can be filtered by `mspsupported` See examples of filtering options.",
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
        "/service-catalog/v1/per-region-service-managers",
        query_params=query_params or None,
    )


@tool(
    name="greenlake_get_service_catalog_v1_per_region_service_managers_id",
    description="GET /service-catalog/v1/per-region-service-managers/{id}\n\nservice_managers_for_a_region_v1\n\nGet service managers deployed in a specific region.",
    capability=Capability.READ,
)
async def greenlake_get_service_catalog_v1_per_region_service_managers_id(
    ctx: Context,
    id: Annotated[str, Field(description="HPE GreenLake platform defined region code.")],
) -> Any:
    path = f"/service-catalog/v1/per-region-service-managers/{path_seg(id)}"
    return await greenlake_request(
        ctx,
        "GET",
        path,
    )


@tool(
    name="greenlake_get_service_catalog_v1_service_managers",
    description="GET /service-catalog/v1/service-managers\n\nget_service_managers_v1\n\nGet service managers",
    capability=Capability.READ,
)
async def greenlake_get_service_catalog_v1_service_managers(
    ctx: Context,
    offset: Annotated[int | None, Field(default=None, description="Specify pagination offset")] = None,
    limit: Annotated[int | None, Field(default=None, description="The maximum number of records to return.")] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if offset is not None:
        query_params["offset"] = offset
    if limit is not None:
        query_params["limit"] = limit
    return await greenlake_request(
        ctx,
        "GET",
        "/service-catalog/v1/service-managers",
        query_params=query_params or None,
    )


@tool(
    name="greenlake_get_service_catalog_v1_service_managers_id",
    description="GET /service-catalog/v1/service-managers/{id}\n\nget_service_manager_v1\n\nGet a specific service manager",
    capability=Capability.READ,
)
async def greenlake_get_service_catalog_v1_service_managers_id(
    ctx: Context,
    id: Annotated[str, Field(description="Service manager ID")],
) -> Any:
    path = f"/service-catalog/v1/service-managers/{path_seg(id)}"
    return await greenlake_request(
        ctx,
        "GET",
        path,
    )
