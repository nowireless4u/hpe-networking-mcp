"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``scripts/_mist_generator.py`` from
``vendor/mist_openapi.json``. Regenerate via:

    uv run python scripts/regenerate_mist_tools.py

Tag: ``Sites Stats - Devices``
Operations in this file: 5
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
    name="mist_get_site_all_clients_stats_by_device",
    description="GET /api/v1/sites/{site_id}/stats/devices/{device_id}/clients\n\ngetSiteAllClientsStatsByDevice\n\nGet wireless client stat by Device",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_get_site_all_clients_stats_by_device(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    device_id: Annotated[str, Field(description="path parameter 'device_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/sites/{site_id}/stats/devices/{device_id}/clients",
        path_params={"site_id": site_id, "device_id": device_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_get_site_device_stats",
    description="GET /api/v1/sites/{site_id}/stats/devices/{device_id}\n\ngetSiteDeviceStats\n\nGet Site Device Stats Details",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_get_site_device_stats(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    device_id: Annotated[str, Field(description="path parameter 'device_id'")],
    fields: Annotated[
        str | None,
        Field(description="List of additional fields requests, comma separated, or `fields=*` for all of them"),
    ] = None,
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/sites/{site_id}/stats/devices/{device_id}",
        path_params={"site_id": site_id, "device_id": device_id},
        query_params={"fields": fields},
        body=None,
    )


@_mcp_tool(
    name="mist_get_site_gateway_metrics",
    description="GET /api/v1/sites/{site_id}/stats/gateways/metrics\n\ngetSiteGatewayMetrics\n\nGet Site Gateway Metrics",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_get_site_gateway_metrics(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/sites/{site_id}/stats/gateways/metrics",
        path_params={"site_id": site_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_get_site_switches_metrics",
    description="GET /api/v1/sites/{site_id}/stats/switches/metrics\n\ngetSiteSwitchesMetrics\n\nGet version compliance metrics for managed or monitored switches",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_get_site_switches_metrics(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    type: Annotated[Any | None, Field(description="query parameter 'type'")] = None,
    scope: Annotated[Any | None, Field(description="query parameter 'scope'")] = None,
    switch_mac: Annotated[
        str | None, Field(description="Switch mac, used only with metric `type`==`active_ports_summary`")
    ] = None,
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/sites/{site_id}/stats/switches/metrics",
        path_params={"site_id": site_id},
        query_params={"type": type, "scope": scope, "switch_mac": switch_mac},
        body=None,
    )


@_mcp_tool(
    name="mist_list_site_devices_stats",
    description="GET /api/v1/sites/{site_id}/stats/devices\n\nlistSiteDevicesStats\n\nGet List of Site Devices Stats",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_list_site_devices_stats(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    type: Annotated[Any | None, Field(description="query parameter 'type'")] = None,
    status: Annotated[Any | None, Field(description="query parameter 'status'")] = None,
    limit: Annotated[int, Field(description="query parameter 'limit'")] = 100,
    page: Annotated[int, Field(description="query parameter 'page'")] = 1,
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/sites/{site_id}/stats/devices",
        path_params={"site_id": site_id},
        query_params={"type": type, "status": status, "limit": limit, "page": page},
        body=None,
    )
