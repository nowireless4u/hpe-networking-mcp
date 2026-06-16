"""Generated EdgeConnect tools — DO NOT EDIT BY HAND.

Emitted by ``scripts/generate_edgeconnect_tools.py`` from
``vendor/edgeconnect/EdgeConnect-9-7-REST-API.json``. Regenerate via:

    uv run python scripts/generate_edgeconnect_tools.py

Tag: ``gmsWizard``
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
    name="edgeconnect_get_gms_wizard",
    description="GET /gms/wizard\n\ngetGMSWizard358\n\nRetrieve the Getting Started Wizard configuration",
    capability=Capability.READ,
)
async def edgeconnect_get_gms_wizard(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/gms/wizard",
        query_params=None,
    )


@tool(
    name="edgeconnect_post_gms_wizard",
    description="POST /gms/wizard\n\npostGMSWizard359\n\nCreate or update Getting Started Wizard configuration",
    capability=Capability.WRITE,
)
async def edgeconnect_post_gms_wizard(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/gms/wizard",
        query_params=None,
        body=body,
    )
