"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``scripts/_mist_generator.py`` from
``vendor/mist_openapi.json``. Regenerate via:

    uv run python scripts/regenerate_mist_tools.py

Tag: ``Orgs Stats - Devices``
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
    name="mist_list_org_devices_stats",
    description="GET /api/v1/orgs/{org_id}/stats/devices\n\nlistOrgDevicesStats\n\nGet List of Org Devices stats\nThis API renders some high-level device stats, pagination is assumed and returned in response header (as the response is an array)",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_list_org_devices_stats(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    type: Annotated[Any | None, Field(description="query parameter 'type'")] = None,
    status: Annotated[Any | None, Field(description="query parameter 'status'")] = None,
    site_id: Annotated[str | None, Field(description="query parameter 'site_id'")] = None,
    mac: Annotated[str | None, Field(description="query parameter 'mac'")] = None,
    evpntopo_id: Annotated[str | None, Field(description="EVPN Topology ID")] = None,
    evpn_unused: Annotated[
        str | None,
        Field(
            description="If `evpn_unused`==`true`, find EVPN eligible switches which don’t belong to any EVPN Topology yet"
        ),
    ] = None,
    fields: Annotated[
        str | None,
        Field(description="List of additional fields requests, comma separated, or `fields=*` for all of them"),
    ] = None,
    start: Annotated[
        str | None, Field(description='Start time (epoch timestamp in seconds, or relative string like "-1d", "-1w")')
    ] = None,
    end: Annotated[
        str | None,
        Field(description='End time (epoch timestamp in seconds, or relative string like "-1d", "-2h", "now")'),
    ] = None,
    duration: Annotated[str, Field(description="Duration like 7d, 2w")] = "1d",
    limit: Annotated[int, Field(description="query parameter 'limit'")] = 100,
    page: Annotated[int, Field(description="query parameter 'page'")] = 1,
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/orgs/{org_id}/stats/devices",
        path_params={"org_id": org_id},
        query_params={
            "type": type,
            "status": status,
            "site_id": site_id,
            "mac": mac,
            "evpntopo_id": evpntopo_id,
            "evpn_unused": evpn_unused,
            "fields": fields,
            "start": start,
            "end": end,
            "duration": duration,
            "limit": limit,
            "page": page,
        },
        body=None,
    )
