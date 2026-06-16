"""Generated EdgeConnect tools — DO NOT EDIT BY HAND.

Emitted by ``scripts/generate_edgeconnect_tools.py`` from
``vendor/edgeconnect/EdgeConnect-9-7-REST-API.json``. Regenerate via:

    uv run python scripts/generate_edgeconnect_tools.py

Tag: ``upgradeAppliances``
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
    name="edgeconnect_post_upgrade_appliances",
    description="POST /upgradeAppliances\n\nupgradeAppliances905\n\nUpgrade EdgeConnect appliances with ECOS firmware",
    capability=Capability.WRITE,
)
async def edgeconnect_post_upgrade_appliances(
    ctx: Context,
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request body")] = None,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/upgradeAppliances",
        query_params=None,
        body=body,
    )


@tool(
    name="edgeconnect_post_validate_appliance_upgrade",
    description="POST /validateApplianceUpgrade\n\nvalidateApplianceUpgrade915\n\nValidate ECOS firmware upgrade compatibility for appliances",
    capability=Capability.WRITE,
)
async def edgeconnect_post_validate_appliance_upgrade(
    ctx: Context,
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request body")] = None,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/validateApplianceUpgrade",
        query_params=None,
        body=body,
    )
