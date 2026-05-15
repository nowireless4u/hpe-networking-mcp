"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``scripts/_mist_generator.py``
from ``vendor/mist_openapi.json``. Regenerate via:

    uv run python scripts/regenerate_mist_tools.py

Tag: ``Sites Stats - Apps``
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
    name="mist_count_site_apps",
    description="GET /api/v1/sites/{site_id}/stats/apps/count\n\ncountSiteApps\n\nCount by Distinct Attributes of Applications",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_count_site_apps(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    distinct: Annotated[
        Any | None, Field(description="Default for wireless devices is `ap`. Default for wired devices is `device_mac`")
    ] = None,
    device_mac: Annotated[str | None, Field(description="MAC of the device")] = None,
    app: Annotated[str | None, Field(description="Application name")] = None,
    wired: Annotated[str | None, Field(description="If a device is wired or wireless. Default is False.")] = None,
    limit: Annotated[int, Field(description="query parameter 'limit'")] = 100,
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/sites/{site_id}/stats/apps/count",
        path_params={"site_id": site_id},
        query_params={"distinct": distinct, "device_mac": device_mac, "app": app, "wired": wired, "limit": limit},
        body=None,
    )
