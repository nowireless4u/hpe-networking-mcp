"""Generated EdgeConnect tools — DO NOT EDIT BY HAND.

Emitted by ``scripts/generate_edgeconnect_tools.py`` from
``vendor/edgeconnect/EdgeConnect-9-7-REST-API.json``. Regenerate via:

    uv run python scripts/generate_edgeconnect_tools.py

Tag: ``overlayManagerProperties``
Operations in this file: 3
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
    name="edgeconnect_get_overlay_manager_properties",
    description="GET /overlayManagerProperties\n\ngetOverlayMngProps491\n\nRetrieve overlay manager properties",
    capability=Capability.READ,
)
async def edgeconnect_get_overlay_manager_properties(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/overlayManagerProperties",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_overlay_manager_properties_default",
    description="GET /overlayManagerProperties/default\n\ngetOverlayMngPropsDefault493\n\nRetrieve factory default overlay manager properties",
    capability=Capability.READ,
)
async def edgeconnect_get_overlay_manager_properties_default(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/overlayManagerProperties/default",
        query_params=None,
    )


@tool(
    name="edgeconnect_post_overlay_manager_properties",
    description="POST /overlayManagerProperties\n\nsetOverlayMngProps492\n\nUpdate overlay manager properties",
    capability=Capability.WRITE,
)
async def edgeconnect_post_overlay_manager_properties(
    ctx: Context,
    isOrchestratorSetting: Annotated[
        bool | None,
        Field(
            default=None,
            description="Skip tunnel settings validation when true. Use for orchestrator-only settings (polling, enable flags).",
        ),
    ] = None,
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request body")] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if isOrchestratorSetting is not None:
        query_params["isOrchestratorSetting"] = isOrchestratorSetting
    return await edgeconnect_request(
        ctx,
        "POST",
        "/overlayManagerProperties",
        query_params=query_params or None,
        body=body,
    )
