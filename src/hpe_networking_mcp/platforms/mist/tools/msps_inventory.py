"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``scripts/_mist_generator.py`` from
``vendor/mist_openapi.json``. Regenerate via:

    uv run python scripts/regenerate_mist_tools.py

Tag: ``MSPs Inventory``
Operations in this file: 1
"""

# ruff: noqa: E501

from __future__ import annotations

from typing import Annotated, Any

from fastmcp import Context
from mcp.types import ToolAnnotations
from pydantic import Field

from hpe_networking_mcp.platforms.mist._client import mist_request
from hpe_networking_mcp.platforms.mist._registry import tool as _mcp_tool


@_mcp_tool(
    name="mist_get_msp_inventory_by_mac",
    description="GET /api/v1/msps/{msp_id}/inventory/{device_mac}\n\ngetMspInventoryByMac\n\nGet Inventory By device MAC address",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_get_msp_inventory_by_mac(
    ctx: Context,
    msp_id: Annotated[str, Field(description="path parameter 'msp_id'")],
    device_mac: Annotated[str, Field(description="path parameter 'device_mac'")],
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/msps/{msp_id}/inventory/{device_mac}",
        path_params={"msp_id": msp_id, "device_mac": device_mac},
        query_params=None,
        body=None,
    )
