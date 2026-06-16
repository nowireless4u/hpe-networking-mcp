"""Generated EdgeConnect tools — DO NOT EDIT BY HAND.

Emitted by ``scripts/generate_edgeconnect_tools.py`` from
``vendor/edgeconnect/EdgeConnect-9-7-REST-API.json``. Regenerate via:

    uv run python scripts/generate_edgeconnect_tools.py

Tag: ``services``
Operations in this file: 3
"""

from __future__ import annotations

from typing import Annotated, Any

from fastmcp import Context
from pydantic import Field

from hpe_networking_mcp.platforms._common.annotations import Capability
from hpe_networking_mcp.platforms.edgeconnect._registry import tool
from hpe_networking_mcp.platforms.edgeconnect.client import edgeconnect_request


@tool(
    name="edgeconnect_get_gms_services",
    description="GET /gms/services\n\ngetServices329\n\nGet all services",
    capability=Capability.READ,
)
async def edgeconnect_get_gms_services(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/gms/services",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_gms_third_party_services",
    description="GET /gms/thirdPartyServices\n\ngetThirdPartyServices345\n\nGet all third party services",
    capability=Capability.READ,
)
async def edgeconnect_get_gms_third_party_services(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/gms/thirdPartyServices",
        query_params=None,
    )


@tool(
    name="edgeconnect_post_gms_services",
    description="POST /gms/services\n\nsaveServices330\n\nSave the service list",
    capability=Capability.WRITE,
)
async def edgeconnect_post_gms_services(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/gms/services",
        query_params=None,
        body=body,
    )
