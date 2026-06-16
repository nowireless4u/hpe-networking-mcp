"""Generated EdgeConnect tools — DO NOT EDIT BY HAND.

Emitted by ``scripts/generate_edgeconnect_tools.py`` from
``vendor/edgeconnect/EdgeConnect-9-7-REST-API.json``. Regenerate via:

    uv run python scripts/generate_edgeconnect_tools.py

Tag: ``maintenanceMode``
Operations in this file: 2
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
    name="edgeconnect_get_maintenance_mode",
    description="GET /maintenanceMode\n\nGetMaintenanceMode458\n\nGet maintenance mode appliances",
    capability=Capability.READ,
)
async def edgeconnect_get_maintenance_mode(
    ctx: Context,
    If_None_Match: Annotated[
        str | None,
        Field(
            default=None,
            description="ETag value from a previous response for cache validation. If matched, returns 304 Not Modified.",
        ),
    ] = None,
) -> Any:
    header_params: dict[str, Any] = {}
    if If_None_Match is not None:
        header_params["If-None-Match"] = If_None_Match
    return await edgeconnect_request(
        ctx,
        "GET",
        "/maintenanceMode",
        query_params=None,
        header_params=header_params or None,
    )


@tool(
    name="edgeconnect_post_maintenance_mode",
    description="POST /maintenanceMode\n\nSetMaintenanceMode459\n\nConfigure appliance maintenance mode",
    capability=Capability.WRITE,
)
async def edgeconnect_post_maintenance_mode(
    ctx: Context,
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request body")] = None,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/maintenanceMode",
        query_params=None,
        body=body,
    )
