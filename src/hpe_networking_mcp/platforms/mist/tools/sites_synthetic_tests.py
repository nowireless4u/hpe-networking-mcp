"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``scripts/_mist_generator.py`` from
``vendor/mist_openapi.json``. Regenerate via:

    uv run python scripts/regenerate_mist_tools.py

Tag: ``Sites Synthetic Tests``
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
    name="mist_get_site_device_synthetic_test",
    description="GET /api/v1/sites/{site_id}/devices/{device_id}/synthetic_test\n\ngetSiteDeviceSyntheticTest\n\nGet Device Synthetic Test",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_get_site_device_synthetic_test(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    device_id: Annotated[str, Field(description="path parameter 'device_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/sites/{site_id}/devices/{device_id}/synthetic_test",
        path_params={"site_id": site_id, "device_id": device_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_search_site_synthetic_test",
    description="GET /api/v1/sites/{site_id}/synthetic_test/search\n\nsearchSiteSyntheticTest\n\nSearch Site Synthetic Testing",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_search_site_synthetic_test(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    mac: Annotated[str | None, Field(description="Device MAC Address")] = None,
    port_id: Annotated[str | None, Field(description="Port_id used to run the test (for SSR only)")] = None,
    vlan_id: Annotated[str | None, Field(description="VLAN ID")] = None,
    by: Annotated[str | None, Field(description="Entity who triggers the test")] = None,
    reason: Annotated[str | None, Field(description="Test failure reason")] = None,
    type: Annotated[Any | None, Field(description="Synthetic test type")] = None,
    protocol: Annotated[Any | None, Field(description="Connectivity protocol")] = None,
    tenant: Annotated[str | None, Field(description="Tenant network in which lan_connectivity test was run")] = None,
    limit: Annotated[int, Field(description="query parameter 'limit'")] = 100,
    start: Annotated[
        str | None, Field(description='Start time (epoch timestamp in seconds, or relative string like "-1d", "-1w")')
    ] = None,
    end: Annotated[
        str | None,
        Field(description='End time (epoch timestamp in seconds, or relative string like "-1d", "-2h", "now")'),
    ] = None,
    duration: Annotated[str, Field(description="Duration like 7d, 2w")] = "1d",
    search_after: Annotated[
        str | None,
        Field(
            description="Pagination cursor for retrieving subsequent pages of results. This value is automatically populated by Mist in the `next` URL from the previous response and should not be manually constructed."
        ),
    ] = None,
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/sites/{site_id}/synthetic_test/search",
        path_params={"site_id": site_id},
        query_params={
            "mac": mac,
            "port_id": port_id,
            "vlan_id": vlan_id,
            "by": by,
            "reason": reason,
            "type": type,
            "protocol": protocol,
            "tenant": tenant,
            "limit": limit,
            "start": start,
            "end": end,
            "duration": duration,
            "search_after": search_after,
        },
        body=None,
    )


@_mcp_tool(
    name="mist_start_site_switch_radius_synthetic_test",
    description='POST /api/v1/sites/{site_id}/devices/{device_id}/check_radius_server\n\ntriggerSiteSwitchRadiusSyntheticTest\n\nPing test from the AP to confirm \'reachability\' of the Radius server. \n\nUtilize Juniper EX switch(to which an AP is connected to) radius test capabilities to get details on the Radius Server \'availability\'.\n\n\n\n#### Subscribe to Device Command outputs\n\n`WS /api-ws/v1/stream`\n\n\n```json\n{\n    "subscribe": "/sites/{site_id}/devices/{device_id}/cmd"\n}\n```\n\n#### Example output from ws stream\n\n```json\n{\n  "event": "data",\n  "channel": "/sites/d6fb4f96-3ba4-4cf5-8af2-a8d7b85087ac/devices/0000...',
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_start_site_switch_radius_synthetic_test(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    device_id: Annotated[str, Field(description="path parameter 'device_id'")],
    body: Annotated[
        dict[str, Any] | None,
        Field(
            default=None,
            description="Request body for POST /api/v1/sites/{site_id}/devices/{device_id}/check_radius_server",
        ),
    ] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/sites/{site_id}/devices/{device_id}/check_radius_server",
        path_params={"site_id": site_id, "device_id": device_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_trigger_site_device_synthetic_test",
    description="POST /api/v1/sites/{site_id}/devices/{device_id}/synthetic_test\n\ntriggerSiteDeviceSyntheticTest\n\nTrigger Device Synthetic Test",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_trigger_site_device_synthetic_test(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    device_id: Annotated[str, Field(description="path parameter 'device_id'")],
    body: Annotated[
        dict[str, Any] | None,
        Field(
            default=None, description="Request body for POST /api/v1/sites/{site_id}/devices/{device_id}/synthetic_test"
        ),
    ] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/sites/{site_id}/devices/{device_id}/synthetic_test",
        path_params={"site_id": site_id, "device_id": device_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_trigger_site_synthetic_test",
    description="POST /api/v1/sites/{site_id}/synthetic_test\n\ntriggerSiteSyntheticTest\n\nTrigger Synthetic Testing",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_trigger_site_synthetic_test(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    body: Annotated[
        dict[str, Any] | None,
        Field(default=None, description="Request body for POST /api/v1/sites/{site_id}/synthetic_test"),
    ] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/sites/{site_id}/synthetic_test",
        path_params={"site_id": site_id},
        query_params=None,
        body=body,
    )
