"""Generated EdgeConnect tools — DO NOT EDIT BY HAND.

Emitted by ``scripts/generate_edgeconnect_tools.py`` from
``vendor/edgeconnect/EdgeConnect-9-7-REST-API.json``. Regenerate via:

    uv run python scripts/generate_edgeconnect_tools.py

Tag: ``internalSubnets``
Operations in this file: 2
"""

from __future__ import annotations

from typing import Annotated, Any

from fastmcp import Context
from pydantic import Field

from hpe_networking_mcp.platforms._common.annotations import Capability
from hpe_networking_mcp.platforms.edgeconnect._registry import tool
from hpe_networking_mcp.platforms.edgeconnect.client import edgeconnect_request


@tool(
    name="edgeconnect_get_gms_internal_subnets2",
    description="GET /gms/internalSubnets2\n\ngetInternalSubnets290\n\nRetrieve internal subnets configuration",
    capability=Capability.READ,
)
async def edgeconnect_get_gms_internal_subnets2(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/gms/internalSubnets2",
        query_params=None,
    )


@tool(
    name="edgeconnect_post_gms_internal_subnets2",
    description="POST /gms/internalSubnets2\n\nsaveInternalSubnets2\n\nSave internal subnets configuration",
    capability=Capability.WRITE,
)
async def edgeconnect_post_gms_internal_subnets2(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/gms/internalSubnets2",
        query_params=None,
        body=body,
    )
