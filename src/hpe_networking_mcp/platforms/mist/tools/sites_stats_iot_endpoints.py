"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``scripts/_mist_generator.py`` from
``vendor/mist_openapi.json``. Regenerate via:

    uv run python scripts/regenerate_mist_tools.py

Tag: ``Sites Stats - IoT Endpoints``
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
    name="mist_search_site_iot_endpoints",
    description="GET /api/v1/sites/{site_id}/iotendpoints/search\n\nsearchSiteIotEndpoints\n\nSearch IoT Endpoints",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_search_site_iot_endpoints(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    ap_mac: Annotated[str | None, Field(description="AP MAC address")] = None,
    mac: Annotated[str | None, Field(description="Device MAC address")] = None,
    type: Annotated[str | None, Field(description="IoT endpoint type. enum: `zigbee`")] = None,
    mfg: Annotated[str | None, Field(description="Manufacturer name")] = None,
    limit: Annotated[int, Field(description="query parameter 'limit'")] = 100,
    start: Annotated[
        str | None, Field(description='Start time (epoch timestamp in seconds, or relative string like "-1d", "-1w")')
    ] = None,
    end: Annotated[
        str | None,
        Field(description='End time (epoch timestamp in seconds, or relative string like "-1d", "-2h", "now")'),
    ] = None,
    duration: Annotated[str, Field(description="Duration like 7d, 2w")] = "1d",
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/sites/{site_id}/iotendpoints/search",
        path_params={"site_id": site_id},
        query_params={
            "ap_mac": ap_mac,
            "mac": mac,
            "type": type,
            "mfg": mfg,
            "limit": limit,
            "start": start,
            "end": end,
            "duration": duration,
        },
        body=None,
    )
