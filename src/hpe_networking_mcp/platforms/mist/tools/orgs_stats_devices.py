"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``scripts/_mist_generator.py`` from
``vendor/mist/mist_openapi.json``. Regenerate via:

    uv run python scripts/regenerate_mist_tools.py

Tag: ``Orgs Stats - Devices``
Operations in this file: 1
"""

# ruff: noqa: E501

from __future__ import annotations

from typing import Annotated, Any

from fastmcp import Context
from pydantic import Field

from hpe_networking_mcp.platforms._common.annotations import Capability
from hpe_networking_mcp.platforms.mist._client import mist_request
from hpe_networking_mcp.platforms.mist._registry import tool as _mcp_tool


@_mcp_tool(
    name="mist_list_org_devices_stats",
    description="GET /api/v1/orgs/{org_id}/stats/devices\n\nlistOrgDevicesStats\n\nGet List of Org Devices stats\nThis API renders some high-level device stats, pagination is assumed and returned in response header (as the response is an array)",
    capability=Capability.READ,
)
async def mist_list_org_devices_stats(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    type: Annotated[
        Any | None,
        Field(
            description="Filter results by one device type. Use a single value; comma-separated values are not supported. enum: `all`, `ap`, `gateway`, `switch`"
        ),
    ] = None,
    status: Annotated[
        str | None,
        Field(
            description="Filter results by status. enum: `all`, `connected`, `disconnected`. Accepts multiple comma-separated values."
        ),
    ] = None,
    site_id: Annotated[
        str | None, Field(description="Filter results by site identifier. Accepts multiple comma-separated values.")
    ] = None,
    mac: Annotated[
        str | None, Field(description="Filter results by MAC address. Accepts multiple comma-separated values.")
    ] = None,
    evpntopo_id: Annotated[str | None, Field(description="Filter results by evpntopo id")] = None,
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
        str | None,
        Field(
            description="Lower bound of the time range, as an epoch timestamp in seconds or a relative value such as `-1d` or `-1w`"
        ),
    ] = None,
    end: Annotated[
        str | None,
        Field(
            description="Upper bound of the time range, as an epoch timestamp in seconds or a relative value such as `-1d`, `-2h`, or `now`"
        ),
    ] = None,
    duration: Annotated[
        str, Field(description="Time range duration for the query, using relative units such as `10m`, `7d`, or `2w`")
    ] = "1d",
    limit: Annotated[int, Field(description="Maximum number of results to return per page")] = 100,
    page: Annotated[
        int, Field(description="Select the page number to return when using page-based pagination; starts at `1`")
    ] = 1,
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
