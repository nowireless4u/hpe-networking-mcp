"""Generated EdgeConnect tools — DO NOT EDIT BY HAND.

Emitted by ``scripts/generate_edgeconnect_tools.py`` from
``vendor/edgeconnect/EdgeConnect-9-7-REST-API.json``. Regenerate via:

    uv run python scripts/generate_edgeconnect_tools.py

Tag: ``restApiConfig``
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
    name="edgeconnect_get_rest_api_config",
    description="GET /restApiConfig\n\nrestApiConfigGet543\n\nRetrieve REST API configuration settings",
    capability=Capability.READ,
)
async def edgeconnect_get_rest_api_config(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/restApiConfig",
        query_params=None,
    )


@tool(
    name="edgeconnect_post_rest_api_config",
    description="POST /restApiConfig\n\nrestApiConfigPost544\n\nUpdate REST API configuration for Orchestrator-EdgeConnect communication",
    capability=Capability.WRITE,
)
async def edgeconnect_post_rest_api_config(
    ctx: Context,
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request body")] = None,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/restApiConfig",
        query_params=None,
        body=body,
    )
