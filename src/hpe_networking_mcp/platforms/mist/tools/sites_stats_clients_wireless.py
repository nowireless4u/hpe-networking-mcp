"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``scripts/_mist_generator.py`` from
``vendor/mist/mist_openapi.json``. Regenerate via:

    uv run python scripts/regenerate_mist_tools.py

Tag: ``Sites Stats - Clients Wireless``
Operations in this file: 4
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
    name="mist_get_site_wireless_client_stats",
    description="GET /api/v1/sites/{site_id}/stats/clients/{client_mac}\n\ngetSiteWirelessClientStats\n\nGet Site Client Stats Details",
    capability=Capability.READ,
)
async def mist_get_site_wireless_client_stats(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    client_mac: Annotated[str, Field(description="path parameter 'client_mac'")],
    wired: Annotated[bool, Field(description="Filter results by whether the client is wired")] = False,
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/sites/{site_id}/stats/clients/{client_mac}",
        path_params={"site_id": site_id, "client_mac": client_mac},
        query_params={"wired": wired},
        body=None,
    )


@_mcp_tool(
    name="mist_get_site_wireless_clients_stats_by_map",
    description="GET /api/v1/sites/{site_id}/stats/maps/{map_id}/clients\n\ngetSiteWirelessClientsStatsByMap\n\nGet Site Clients Stats By Map",
    capability=Capability.READ,
)
async def mist_get_site_wireless_clients_stats_by_map(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    map_id: Annotated[str, Field(description="path parameter 'map_id'")],
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
        "/api/v1/sites/{site_id}/stats/maps/{map_id}/clients",
        path_params={"site_id": site_id, "map_id": map_id},
        query_params={"start": start, "end": end, "duration": duration, "limit": limit, "page": page},
        body=None,
    )


@_mcp_tool(
    name="mist_list_site_unconnected_client_stats",
    description="GET /api/v1/sites/{site_id}/stats/maps/{map_id}/unconnected_clients\n\nlistSiteUnconnectedClientStats\n\nGet List of Site Unconnected Client Location",
    capability=Capability.READ,
)
async def mist_list_site_unconnected_client_stats(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    map_id: Annotated[str, Field(description="path parameter 'map_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/sites/{site_id}/stats/maps/{map_id}/unconnected_clients",
        path_params={"site_id": site_id, "map_id": map_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_list_site_wireless_clients_stats",
    description="GET /api/v1/sites/{site_id}/stats/clients\n\nlistSiteWirelessClientsStats\n\nGet List of Site All Clients Stats Details",
    capability=Capability.READ,
)
async def mist_list_site_wireless_clients_stats(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    wired: Annotated[bool, Field(description="Filter results by whether the client is wired")] = False,
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
        "/api/v1/sites/{site_id}/stats/clients",
        path_params={"site_id": site_id},
        query_params={"wired": wired, "limit": limit, "start": start, "end": end, "duration": duration},
        body=None,
    )
