"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``hpe_networking_mcp.platforms.mist._generator``
from ``vendor/mist_openapi.json``. Regenerate via:

    uv run python -m hpe_networking_mcp.platforms.mist.regenerate

Tag: ``Sites Devices - Wireless``
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
    name="mist_enable_site_device_zigbee_join",
    description='POST /api/v1/sites/{site_id}/devices/{device_id}/zigbee_join\n\nenableSiteDeviceZigbeeJoin\n\nAllow Zigbee end devices to join the network for a configurable duration. After the duration expires, new joins will be blocked (unless `allow_join`==`always` is configured on the device).\n\n#### Subscribe to Zigbee Join Events\n`WS /api-ws/v1/stream`\n\n```json\n{\n    "subscribe": "/sites/{site_id}/devices/{device_id}/zigbee_join"\n}\n```\n##### Example output from ws stream\n```json\n{\n    "event": "data",\n    "channel": "/sites/4ac1dcf4-9d8b-7211-65c4-057819f0862b/devices/00000000-0000-0000-1000-5c5b350e0060/...',
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_enable_site_device_zigbee_join(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    device_id: Annotated[str, Field(description="path parameter 'device_id'")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request Body")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/sites/{site_id}/devices/{device_id}/zigbee_join",
        path_params={"site_id": site_id, "device_id": device_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_get_site_device_iot_port",
    description="GET /api/v1/sites/{site_id}/devices/{device_id}/iot\n\ngetSiteDeviceIotPort\n\nReturns the current state of each enabled IoT pin configured as an output.",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_get_site_device_iot_port(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    device_id: Annotated[str, Field(description="path parameter 'device_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/sites/{site_id}/devices/{device_id}/iot",
        path_params={"site_id": site_id, "device_id": device_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_list_site_device_radio_channels",
    description="GET /api/v1/sites/{site_id}/devices/ap_channels\n\nlistSiteDeviceRadioChannels\n\nGet a list of allowed channels (per channel width)",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_list_site_device_radio_channels(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    country_code: Annotated[
        str | None,
        Field(
            description="Country code for the site (for AP config generation), in [two-character](https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2)"
        ),
    ] = None,
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/sites/{site_id}/devices/ap_channels",
        path_params={"site_id": site_id},
        query_params={"country_code": country_code},
        body=None,
    )


@_mcp_tool(
    name="mist_set_site_device_iot_port",
    description="PUT /api/v1/sites/{site_id}/devices/{device_id}/iot\n\nsetSiteDeviceIotPort\n\n**Note**: For each IoT pin referenced:\n * The pin must be enabled using the Device `iot_config` API\n * The pin must support the output direction",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_set_site_device_iot_port(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    device_id: Annotated[str, Field(description="path parameter 'device_id'")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request Body")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "PUT",
        "/api/v1/sites/{site_id}/devices/{device_id}/iot",
        path_params={"site_id": site_id, "device_id": device_id},
        query_params=None,
        body=body,
    )
