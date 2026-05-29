"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``scripts/_mist_generator.py`` from
``vendor/mist_openapi.json``. Regenerate via:

    uv run python scripts/regenerate_mist_tools.py

Tag: ``Sites WAN Usages``
Operations in this file: 2
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
    name="mist_count_site_wan_usage",
    description="GET /api/v1/sites/{site_id}/wan_usages/count\n\ncountSiteWanUsage\n\nCount Site WAN Usages",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_count_site_wan_usage(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    mac: Annotated[str | None, Field(description="MAC address")] = None,
    peer_mac: Annotated[str | None, Field(description="Peer MAC address")] = None,
    port_id: Annotated[str | None, Field(description="Port ID for the device")] = None,
    peer_port_id: Annotated[str | None, Field(description="Peer Port ID for the device")] = None,
    policy: Annotated[str | None, Field(description="Policy for the wan path")] = None,
    tenant: Annotated[str | None, Field(description="Tenant network in which the packet is sent")] = None,
    path_type: Annotated[str | None, Field(description="path_type of the port")] = None,
    distinct: Annotated[Any | None, Field(description="query parameter 'distinct'")] = None,
    start: Annotated[
        str | None, Field(description='Start time (epoch timestamp in seconds, or relative string like "-1d", "-1w")')
    ] = None,
    end: Annotated[
        str | None,
        Field(description='End time (epoch timestamp in seconds, or relative string like "-1d", "-2h", "now")'),
    ] = None,
    duration: Annotated[str, Field(description="Duration like 7d, 2w")] = "1d",
    limit: Annotated[int, Field(description="query parameter 'limit'")] = 100,
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/sites/{site_id}/wan_usages/count",
        path_params={"site_id": site_id},
        query_params={
            "mac": mac,
            "peer_mac": peer_mac,
            "port_id": port_id,
            "peer_port_id": peer_port_id,
            "policy": policy,
            "tenant": tenant,
            "path_type": path_type,
            "distinct": distinct,
            "start": start,
            "end": end,
            "duration": duration,
            "limit": limit,
        },
        body=None,
    )


@_mcp_tool(
    name="mist_search_site_wan_usage",
    description="GET /api/v1/sites/{site_id}/wan_usages/search\n\nsearchSiteWanUsage\n\nSearch Site WAN Usages",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_search_site_wan_usage(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    mac: Annotated[str | None, Field(description="MAC address")] = None,
    peer_mac: Annotated[str | None, Field(description="Peer MAC address")] = None,
    port_id: Annotated[str | None, Field(description="Port ID for the device")] = None,
    peer_port_id: Annotated[str | None, Field(description="Peer Port ID for the device")] = None,
    policy: Annotated[str | None, Field(description="Policy for the wan path")] = None,
    tenant: Annotated[str | None, Field(description="Tenant network in which the packet is sent")] = None,
    path_type: Annotated[str | None, Field(description="path_type of the port")] = None,
    limit: Annotated[int, Field(description="query parameter 'limit'")] = 100,
    start: Annotated[
        str | None, Field(description='Start time (epoch timestamp in seconds, or relative string like "-1d", "-1w")')
    ] = None,
    end: Annotated[
        str | None,
        Field(description='End time (epoch timestamp in seconds, or relative string like "-1d", "-2h", "now")'),
    ] = None,
    duration: Annotated[str, Field(description="Duration like 7d, 2w")] = "1d",
    sort: Annotated[
        str, Field(description="On which field the list should be sorted, -prefix represents DESC order")
    ] = "timestamp",
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/sites/{site_id}/wan_usages/search",
        path_params={"site_id": site_id},
        query_params={
            "mac": mac,
            "peer_mac": peer_mac,
            "port_id": port_id,
            "peer_port_id": peer_port_id,
            "policy": policy,
            "tenant": tenant,
            "path_type": path_type,
            "limit": limit,
            "start": start,
            "end": end,
            "duration": duration,
            "sort": sort,
        },
        body=None,
    )
