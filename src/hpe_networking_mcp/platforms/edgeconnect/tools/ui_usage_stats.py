"""Generated EdgeConnect tools — DO NOT EDIT BY HAND.

Emitted by ``scripts/generate_edgeconnect_tools.py`` from
``vendor/edgeconnect/EdgeConnect-9-7-REST-API.json``. Regenerate via:

    uv run python scripts/generate_edgeconnect_tools.py

Tag: ``uiUsageStats``
Operations in this file: 1
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
    name="edgeconnect_post_ui_usage_stats",
    description="POST /uiUsageStats\n\nuiUsageStats904\n\nIncrement UI feature usage counter",
    capability=Capability.WRITE,
)
async def edgeconnect_post_ui_usage_stats(
    ctx: Context,
    uiName: Annotated[
        str,
        Field(
            description="Unique identifier for the UI feature, dialog, or tab being tracked. Must be a non-empty string representing the UI element name."
        ),
    ],
) -> Any:
    query_params: dict[str, Any] = {}
    if uiName is not None:
        query_params["uiName"] = uiName
    return await edgeconnect_request(
        ctx,
        "POST",
        "/uiUsageStats",
        query_params=query_params or None,
    )
