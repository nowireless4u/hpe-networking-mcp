"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``scripts/_mist_generator.py``
from ``vendor/mist_openapi.json``. Regenerate via:

    uv run python scripts/regenerate_mist_tools.py

Tag: ``Constants Models``
Operations in this file: 4
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
    name="mist_get_gateway_default_config",
    description="GET /api/v1/const/default_gateway_config\n\ngetGatewayDefaultConfig\n\nGenerate Default Gateway Config",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_get_gateway_default_config(
    ctx: Context,
    model: Annotated[
        str, Field(description="Model the default gateway config is intended (as the default LAN/WAN port can differ)")
    ],
    ha: Annotated[str | None, Field(description="Whether the config is intended for HA")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/const/default_gateway_config",
        path_params=None,
        query_params={"model": model, "ha": ha},
        body=None,
    )


@_mcp_tool(
    name="mist_list_device_models",
    description="GET /api/v1/const/device_models\n\nlistDeviceModels\n\nGet list of AP device models for the Mist Site",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_list_device_models(
    ctx: Context,
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/const/device_models",
        path_params=None,
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_list_mx_edge_models",
    description="GET /api/v1/const/mxedge_models\n\nlistMxEdgeModels\n\nGet List of available Mx Edge models",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_list_mx_edge_models(
    ctx: Context,
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/const/mxedge_models",
        path_params=None,
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_list_supported_other_device_models",
    description="GET /api/v1/const/otherdevice_models\n\nlistSupportedOtherDeviceModels\n\nSupported OtherDevice Models",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_list_supported_other_device_models(
    ctx: Context,
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/const/otherdevice_models",
        path_params=None,
        query_params=None,
        body=None,
    )
