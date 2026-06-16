"""Generated EdgeConnect tools — DO NOT EDIT BY HAND.

Emitted by ``scripts/generate_edgeconnect_tools.py`` from
``vendor/edgeconnect/EdgeConnect-9-7-REST-API.json``. Regenerate via:

    uv run python scripts/generate_edgeconnect_tools.py

Tag: ``haGroups``
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
    name="edgeconnect_get_ha_groups",
    description="GET /haGroups\n\nhaGroupsGet\n\nRetrieve all HA groups",
    capability=Capability.READ,
)
async def edgeconnect_get_ha_groups(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/haGroups",
        query_params=None,
    )


@tool(
    name="edgeconnect_post_ha_groups",
    description="POST /haGroups\n\nhaGroupsPost\n\nSave or update HA groups configuration",
    capability=Capability.WRITE,
)
async def edgeconnect_post_ha_groups(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/haGroups",
        query_params=None,
        body=body,
    )
