"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``scripts/_mist_generator.py`` from
``vendor/mist/mist_openapi.json``. Regenerate via:

    uv run python scripts/regenerate_mist_tools.py

Tag: ``Orgs Stats - Marvis Clients``
Operations in this file: 2
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
    name="mist_count_org_marvis_clients_stats",
    description="GET /api/v1/orgs/{org_id}/stats/marvisclients/count\n\ncountOrgMarvisClientsStats\n\nCount Marvis Client stats records by a distinct field.",
    capability=Capability.READ,
)
async def mist_count_org_marvis_clients_stats(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    distinct: Annotated[
        str,
        Field(
            description="Field to count by. enum: `device_id`, `wifi_mac`, `wifi_ip`, `hostname`, `model`, `mfg`, `serial`, `os_type`, `os_version`"
        ),
    ] = "os_type",
    device_id: Annotated[str | None, Field(description="Filter by Marvis Client installation device UUID")] = None,
    wifi_mac: Annotated[str | None, Field(description="Filter by device Wi-Fi MAC address")] = None,
    wifi_ip: Annotated[str | None, Field(description="Filter by device Wi-Fi IP address")] = None,
    hostname: Annotated[str | None, Field(description="Filter by device hostname")] = None,
    model: Annotated[str | None, Field(description="Filter by device model")] = None,
    mfg: Annotated[str | None, Field(description="Filter by device manufacturer")] = None,
    serial: Annotated[str | None, Field(description="Filter by device serial number")] = None,
    os_type: Annotated[str | None, Field(description="Filter by device OS type or platform")] = None,
    os_version: Annotated[str | None, Field(description="Filter by device OS version")] = None,
    limit: Annotated[int, Field(description="Maximum number of results to return per page")] = 100,
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
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/orgs/{org_id}/stats/marvisclients/count",
        path_params={"org_id": org_id},
        query_params={
            "distinct": distinct,
            "device_id": device_id,
            "wifi_mac": wifi_mac,
            "wifi_ip": wifi_ip,
            "hostname": hostname,
            "model": model,
            "mfg": mfg,
            "serial": serial,
            "os_type": os_type,
            "os_version": os_version,
            "limit": limit,
            "start": start,
            "end": end,
            "duration": duration,
        },
        body=None,
    )


@_mcp_tool(
    name="mist_search_org_marvis_clients_stats",
    description="GET /api/v1/orgs/{org_id}/stats/marvisclients/search\n\nsearchOrgMarvisClientsStats\n\nSearch Marvis Client stats records across the organization.",
    capability=Capability.READ,
)
async def mist_search_org_marvis_clients_stats(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    device_id: Annotated[str | None, Field(description="Filter by Marvis Client installation device UUID")] = None,
    wifi_mac: Annotated[str | None, Field(description="Filter by device Wi-Fi MAC address")] = None,
    wifi_ip: Annotated[str | None, Field(description="Filter by device Wi-Fi IP address")] = None,
    hostname: Annotated[str | None, Field(description="Filter by device hostname")] = None,
    model: Annotated[str | None, Field(description="Filter by device model")] = None,
    mfg: Annotated[str | None, Field(description="Filter by device manufacturer")] = None,
    serial: Annotated[str | None, Field(description="Filter by device serial number")] = None,
    os_type: Annotated[str | None, Field(description="Filter by device OS type or platform")] = None,
    os_version: Annotated[str | None, Field(description="Filter by device OS version")] = None,
    limit: Annotated[int, Field(description="Maximum number of results to return per page")] = 100,
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
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/orgs/{org_id}/stats/marvisclients/search",
        path_params={"org_id": org_id},
        query_params={
            "device_id": device_id,
            "wifi_mac": wifi_mac,
            "wifi_ip": wifi_ip,
            "hostname": hostname,
            "model": model,
            "mfg": mfg,
            "serial": serial,
            "os_type": os_type,
            "os_version": os_version,
            "limit": limit,
            "start": start,
            "end": end,
            "duration": duration,
        },
        body=None,
    )
