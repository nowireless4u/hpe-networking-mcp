"""Generated EdgeConnect tools — DO NOT EDIT BY HAND.

Generated from ``vendor/edgeconnect/EdgeConnect-9-7-REST-API.json`` by the
maintainer-local EdgeConnect generator. These generated modules are committed
and are the runtime source of truth; regeneration is a release-time maintainer
workflow (the generator is intentionally not committed — see ``.gitignore``).

Tag: ``gmsStatsCollection``
Operations in this file: 3
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
    name="edgeconnect_get_gms_stats_collection_2",
    description="GET /gms/statsCollection\n\ngetStatsCollection\n\nGet statistics collection configuration",
    capability=Capability.READ,
)
async def edgeconnect_get_gms_stats_collection_2(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/gms/statsCollection",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_gms_stats_collection_default",
    description="GET /gms/statsCollection/default\n\ngetDefaultStatsCollection\n\nGet default statistics collection configuration",
    capability=Capability.READ,
)
async def edgeconnect_get_gms_stats_collection_default(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/gms/statsCollection/default",
        query_params=None,
    )


@tool(
    name="edgeconnect_post_gms_stats_collection",
    description="POST /gms/statsCollection\n\nsetStatsCollection\n\nUpdate statistics collection configuration",
    capability=Capability.WRITE,
)
async def edgeconnect_post_gms_stats_collection(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/gms/statsCollection",
        query_params=None,
        body=body,
    )
