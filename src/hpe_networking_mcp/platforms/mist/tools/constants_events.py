"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``scripts/_mist_generator.py`` from
``vendor/mist/mist_openapi.json``. Regenerate via:

    uv run python scripts/regenerate_mist_tools.py

Tag: ``Constants Events``
Operations in this file: 7
"""

# ruff: noqa: E501

from __future__ import annotations

from typing import Any

from fastmcp import Context

from hpe_networking_mcp.platforms._common.annotations import Capability
from hpe_networking_mcp.platforms.mist._client import mist_request
from hpe_networking_mcp.platforms.mist._registry import tool as _mcp_tool


@_mcp_tool(
    name="mist_list_alarm_definitions",
    description="GET /api/v1/const/alarm_defs\n\nlistAlarmDefinitions\n\nReturn alarm type definitions used by alarm search results, alarm templates, and the `alarm` webhook topic. The `example` field shows representative webhook payload content.\nHA cluster node names are returned in the `node` field, when applicable.",
    capability=Capability.READ,
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
    description="GET /api/v1/const/client_events\n\nlistClientEventsDefinitions\n\nReturn client event definitions used by client event search and count APIs, including event keys and metadata.",
    capability=Capability.READ,
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
    description="GET /api/v1/const/device_events\n\nlistDeviceEventsDefinitions\n\nReturn device event definitions used by device event search and count APIs and the `device-events` webhook topic, including event keys and metadata.",
    capability=Capability.READ,
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
    description="GET /api/v1/const/mxedge_events\n\nlistMxEdgeEventsDefinitions\n\nReturn Mist Edge event definitions used by Mist Edge event search and count APIs, and `mexedge-events` webhook topic.",
    capability=Capability.READ,
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
    description="GET /api/v1/const/nac_events\n\nlistNacEventsDefinitions\n\nReturn NAC client event definitions used by NAC client event search and count APIs, and `nac-events` webhook topic.",
    capability=Capability.READ,
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
    description="GET /api/v1/const/otherdevice_events\n\nlistOtherDeviceEventsDefinitions\n\nReturn event definitions for other or third-party devices managed or monitored by Mist.",
    capability=Capability.READ,
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
    description="GET /api/v1/const/system_events\n\nlistSystemEventsDefinitions\n\nReturn system event definitions used by system event search APIs.",
    capability=Capability.READ,
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
