"""Generated EdgeConnect tools — DO NOT EDIT BY HAND.

Generated from ``vendor/edgeconnect/EdgeConnect-9-7-REST-API.json`` by the
maintainer-local EdgeConnect generator. These generated modules are committed
and are the runtime source of truth; regeneration is a release-time maintainer
workflow (the generator is intentionally not committed — see ``.gitignore``).

Tag: ``availabilityTimeSettings``
Operations in this file: 2
"""

# ruff: noqa: E501
from __future__ import annotations

from typing import Annotated, Any

from fastmcp import Context
from pydantic import Field

from hpe_networking_mcp.platforms._common.annotations import Capability
from hpe_networking_mcp.platforms.edgeconnect._registry import tool
from hpe_networking_mcp.platforms.edgeconnect.client import edgeconnect_request


@tool(
    name="edgeconnect_post_stats_config_appliance_business_hours",
    description="POST /stats/config/applianceBusinessHours\n\navailabilityTimeSettingsPost1\n\nConfigure appliance business hours for KPI availability calculations",
    capability=Capability.WRITE,
)
async def edgeconnect_post_stats_config_appliance_business_hours(
    ctx: Context,
    body: Annotated[list[Any], Field(description="Request body (required)")],
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/stats/config/applianceBusinessHours",
        query_params=None,
        body=body,
    )


@tool(
    name="edgeconnect_post_stats_config_appliance_business_hours_get",
    description="POST /stats/config/applianceBusinessHours/get\n\navailabilityTimeSettingsGet1\n\nRetrieve business hour configurations for appliances",
    capability=Capability.WRITE,
)
async def edgeconnect_post_stats_config_appliance_business_hours_get(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/stats/config/applianceBusinessHours/get",
        query_params=None,
        body=body,
    )
