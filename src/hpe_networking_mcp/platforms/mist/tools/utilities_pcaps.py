"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``hpe_networking_mcp.platforms.mist._generator``
from ``vendor/mist_openapi.json``. Regenerate via:

    uv run python -m hpe_networking_mcp.platforms.mist.regenerate

Tag: ``Utilities PCAPs``
Operations in this file: 9
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
    name="mist_get_org_capturing_status",
    description="GET /api/v1/orgs/{org_id}/pcaps/capture\n\ngetOrgCapturingStatus\n\nGet Org Capturing status",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_get_org_capturing_status(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/orgs/{org_id}/pcaps/capture",
        path_params={"org_id": org_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_get_site_capturing_status",
    description="GET /api/v1/sites/{site_id}/pcaps/capture\n\ngetSiteCapturingStatus\n\nGet Capturing status",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_get_site_capturing_status(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/sites/{site_id}/pcaps/capture",
        path_params={"site_id": site_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_list_org_packet_captures",
    description="GET /api/v1/orgs/{org_id}/pcaps\n\nlistOrgPacketCaptures\n\nGet List of Org Packet Captures",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_list_org_packet_captures(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
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
        "/api/v1/orgs/{org_id}/pcaps",
        path_params={"org_id": org_id},
        query_params={"start": start, "end": end, "duration": duration, "limit": limit, "page": page},
        body=None,
    )


@_mcp_tool(
    name="mist_list_site_packet_captures",
    description="GET /api/v1/sites/{site_id}/pcaps\n\nlistSitePacketCaptures\n\nGet List of Site Packet Captures",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_list_site_packet_captures(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    client_mac: Annotated[str | None, Field(description="Optional client mac filter")] = None,
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
        "/api/v1/sites/{site_id}/pcaps",
        path_params={"site_id": site_id},
        query_params={
            "client_mac": client_mac,
            "start": start,
            "end": end,
            "duration": duration,
            "limit": limit,
            "page": page,
        },
        body=None,
    )


@_mcp_tool(
    name="mist_start_org_packet_capture",
    description='POST /api/v1/orgs/{org_id}/pcaps/capture\n\nstartOrgPacketCapture\n\nInitiate a Packet Capture\n\n**NOTE**: For packet captures of org level Mist Edges only. Use [Start Site Packet Capture](/#operations/startSitePacketCapture) for site level Mist Edges. \n\nThe output will be available through websocket. As there can be multiple commands issued against the same AP at the same time and the output all goes through the same websocket stream, session is introduced for demux.\n\n#### Subscribe to Device Command outputs\n`WS /api-ws/v1/stream`\n\n```json\n{\n    "subscribe": "/orgs/:org_id/pcaps"\n}\n```\n#### Res...',
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_start_org_packet_capture(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request Body")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/orgs/{org_id}/pcaps/capture",
        path_params={"org_id": org_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_start_site_packet_capture",
    description='POST /api/v1/sites/{site_id}/pcaps/capture\n\nstartSitePacketCapture\n\nInitiate a Site Packet Capture\n\nThe output will be available through websocket. As there can be multiple commands issued against the same AP at the same time and the output all goes through the same websocket stream, session is introduced for demux.\n\n#### Subscribe to Device Command outputs\n`WS /api-ws/v1/stream`\n\n```json\n{\n    "subscribe": "/sites/{site_id}/pcaps"\n}\n```\n#### Response (MxEdge)\n```json\n{\n    "event": "data"\n    "channel": "/sites/{site_id}/pcaps"\n    "data": {\n         "capture_id": "6b1be4fb-b239-44d9-9d3b-...',
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_start_site_packet_capture(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request Body")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/sites/{site_id}/pcaps/capture",
        path_params={"site_id": site_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_stop_org_packet_capture",
    description="DELETE /api/v1/orgs/{org_id}/pcaps/capture\n\nstopOrgPacketCapture\n\nStop current Org capture",
    tags={"mist", "mist_write", "mist_write_delete"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=True),
)
async def mist_stop_org_packet_capture(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "DELETE",
        "/api/v1/orgs/{org_id}/pcaps/capture",
        path_params={"org_id": org_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_stop_site_packet_capture",
    description="DELETE /api/v1/sites/{site_id}/pcaps/capture\n\nstopSitePacketCapture\n\nStop current capture",
    tags={"mist", "mist_write", "mist_write_delete"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=True),
)
async def mist_stop_site_packet_capture(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "DELETE",
        "/api/v1/sites/{site_id}/pcaps/capture",
        path_params={"site_id": site_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_update_site_packet_capture",
    description="PUT /api/v1/sites/{site_id}/pcaps/{pcap_id}\n\nupdateSitePacketCapture\n\nUpdate or add notes to a completed packet capture",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_update_site_packet_capture(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    pcap_id: Annotated[str, Field(description="path parameter 'pcap_id'")],
    body: Annotated[
        dict[str, Any] | None,
        Field(default=None, description="Request body for PUT /api/v1/sites/{site_id}/pcaps/{pcap_id}"),
    ] = None,
) -> Any:
    return await mist_request(
        ctx,
        "PUT",
        "/api/v1/sites/{site_id}/pcaps/{pcap_id}",
        path_params={"site_id": site_id, "pcap_id": pcap_id},
        query_params=None,
        body=body,
    )
