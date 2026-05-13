"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``hpe_networking_mcp.platforms.mist._generator``
from ``vendor/mist_openapi.json``. Regenerate via:

    uv run python -m hpe_networking_mcp.platforms.mist.regenerate

Tag: ``Constants Events``
Operations in this file: 7
"""

# ruff: noqa: E501

from __future__ import annotations

from typing import Any

from fastmcp import Context
from mcp.types import ToolAnnotations

from hpe_networking_mcp.platforms.mist._client import mist_request
from hpe_networking_mcp.platforms.mist._registry import tool as _mcp_tool


@_mcp_tool(
    name="mist_list_alarm_definitions",
    description="GET /api/v1/const/alarm_defs\n\nlistAlarmDefinitions\n\nGet List of brief definitions of all the supported alarm types. The example field contains an example payload as you would receive in the alarm webhook output.\nHA cluster node names will be specified in the `node` field, if applicable.",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_list_alarm_definitions(
    ctx: Context,
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/const/alarm_defs",
        path_params=None,
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_list_client_events_definitions",
    description="GET /api/v1/const/client_events\n\nlistClientEventsDefinitions\n\nGet List of List of available Client Events",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_list_client_events_definitions(
    ctx: Context,
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/const/client_events",
        path_params=None,
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_list_device_events_definitions",
    description="GET /api/v1/const/device_events\n\nlistDeviceEventsDefinitions\n\nGet list of available Device Events",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_list_device_events_definitions(
    ctx: Context,
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/const/device_events",
        path_params=None,
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_list_mx_edge_events_definitions",
    description="GET /api/v1/const/mxedge_events\n\nlistMxEdgeEventsDefinitions\n\nGet List of available MX Edge Events",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_list_mx_edge_events_definitions(
    ctx: Context,
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/const/mxedge_events",
        path_params=None,
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_list_nac_events_definitions",
    description="GET /api/v1/const/nac_events\n\nlistNacEventsDefinitions\n\nGet List of List of available NAC Client Events",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_list_nac_events_definitions(
    ctx: Context,
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/const/nac_events",
        path_params=None,
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_list_other_device_events_definitions",
    description="GET /api/v1/const/otherdevice_events\n\nlistOtherDeviceEventsDefinitions\n\nSupported Events Type",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_list_other_device_events_definitions(
    ctx: Context,
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/const/otherdevice_events",
        path_params=None,
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_list_system_events_definitions",
    description="GET /api/v1/const/system_events\n\nlistSystemEventsDefinitions\n\nGet List of List of available System Events",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_list_system_events_definitions(
    ctx: Context,
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/const/system_events",
        path_params=None,
        query_params=None,
        body=None,
    )
