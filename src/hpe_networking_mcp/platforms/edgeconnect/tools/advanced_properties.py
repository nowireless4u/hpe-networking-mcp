"""Generated EdgeConnect tools — DO NOT EDIT BY HAND.

Emitted by ``scripts/generate_edgeconnect_tools.py`` from
``vendor/edgeconnect/EdgeConnect-9-7-REST-API.json``. Regenerate via:

    uv run python scripts/generate_edgeconnect_tools.py

Tag: ``advancedProperties``
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
    name="edgeconnect_get_gms_advanced_properties",
    description="GET /gms/advancedProperties\n\nGetAdvProp243\n\nGet Orchestrator advanced properties",
    capability=Capability.READ,
)
async def edgeconnect_get_gms_advanced_properties(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/gms/advancedProperties",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_gms_advanced_properties_metadata",
    description="GET /gms/advancedProperties/metadata\n\nGetAdvProp245\n\nGet metadata for all Orchestrator advanced properties",
    capability=Capability.READ,
)
async def edgeconnect_get_gms_advanced_properties_metadata(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/gms/advancedProperties/metadata",
        query_params=None,
    )


@tool(
    name="edgeconnect_put_gms_advanced_properties",
    description="PUT /gms/advancedProperties\n\nPostAdvProp244\n\nUpdate Orchestrator advanced properties",
    capability=Capability.WRITE,
)
async def edgeconnect_put_gms_advanced_properties(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await edgeconnect_request(
        ctx,
        "PUT",
        "/gms/advancedProperties",
        query_params=None,
        body=body,
    )
