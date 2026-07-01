"""Generated GreenLake tools — DO NOT EDIT BY HAND.

Generated from the vendored spec ``vendor/greenlake/sustainability.json`` by the
maintainer-local GreenLake generator. These modules are committed and are the
runtime source of truth; regeneration is a release-time maintainer workflow
(the generator is intentionally not committed — see ``.gitignore``).

Service: ``sustainability``   Tag: ``datasources``   Operations: 2
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
    name="greenlake_get_sustainability_insight_ctr_v1beta1_datasources",
    description="GET /sustainability-insight-ctr/v1beta1/datasources\n\ngetDatasources\n\nGet all information for SIC data sources.",
    capability=Capability.READ,
)
async def greenlake_get_sustainability_insight_ctr_v1beta1_datasources(
    ctx: Context,
) -> Any:
    return await greenlake_request(
        ctx,
        "GET",
        "/sustainability-insight-ctr/v1beta1/datasources",
    )


@tool(
    name="greenlake_get_sustainability_insight_ctr_v1beta1_datasources_id",
    description="GET /sustainability-insight-ctr/v1beta1/datasources/{id}\n\ngetDatasource\n\nGet information for a SIC data source.",
    capability=Capability.READ,
)
async def greenlake_get_sustainability_insight_ctr_v1beta1_datasources_id(
    ctx: Context,
    id: Annotated[str, Field(description="ID of the data source")],
) -> Any:
    path = f"/sustainability-insight-ctr/v1beta1/datasources/{path_seg(id)}"
    return await greenlake_request(
        ctx,
        "GET",
        path,
    )
