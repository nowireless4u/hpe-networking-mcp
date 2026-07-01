"""Generated GreenLake tools — DO NOT EDIT BY HAND.

Generated from the vendored spec ``vendor/greenlake/service-catalog__service-registry-v1beta1-service-catalog-v1alpha1.json`` by the
maintainer-local GreenLake generator. These modules are committed and are the
runtime source of truth; regeneration is a release-time maintainer workflow
(the generator is intentionally not committed — see ``.gitignore``).

Service: ``service-catalog``   Tag: ``service_status``   Operations: 1
"""

# ruff: noqa: E501
from __future__ import annotations

from typing import Any

from fastmcp import Context

from hpe_networking_mcp.platforms._common.annotations import Capability
from hpe_networking_mcp.platforms.greenlake._registry import tool
from hpe_networking_mcp.platforms.greenlake.client import greenlake_request


@tool(
    name="greenlake_get_service_catalog_v1alpha1_health_service_registry",
    description="GET /service-catalog/v1alpha1/health/service-registry\n\ngetServiceRegistryHealth\n\nGet Status of service",
    capability=Capability.READ,
)
async def greenlake_get_service_catalog_v1alpha1_health_service_registry(
    ctx: Context,
) -> Any:
    return await greenlake_request(
        ctx,
        "GET",
        "/service-catalog/v1alpha1/health/service-registry",
    )
