"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``scripts/_mist_generator.py`` from
``vendor/mist/mist_openapi.json``. Regenerate via:

    uv run python scripts/regenerate_mist_tools.py

Tag: ``Utilities PCAPs``
Operations in this file: 9
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
    name="mist_get_org_capturing_status",
    description="GET /api/v1/orgs/{org_id}/pcaps/capture\n\ngetOrgCapturingStatus\n\nRetrieve the current organization packet capture status, including active capture targets and progress.",
    capability=Capability.READ,
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
    capability=Capability.READ,
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
    description="GET /api/v1/orgs/{org_id}/pcaps\n\nlistOrgPacketCaptures\n\nList organization packet capture sessions and generated capture files for the selected time range.",
    capability=Capability.READ,
)
async def mist_list_org_packet_captures(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
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
        "/api/v1/orgs/{org_id}/pcaps",
        path_params={"org_id": org_id},
        query_params={"start": start, "end": end, "duration": duration, "limit": limit, "page": page},
        body=None,
    )


@_mcp_tool(
    name="mist_list_site_packet_captures",
    description="GET /api/v1/sites/{site_id}/pcaps\n\nlistSitePacketCaptures\n\nList packet captures for a site, optionally filtered by client MAC address and time range. Use [List Org Packet Captures](/#operations/listOrgPacketCaptures) to retrieve packet captures across the organization.",
    capability=Capability.READ,
)
async def mist_list_site_packet_captures(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    client_mac: Annotated[str | None, Field(description="Optional client mac filter")] = None,
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
    description='POST /api/v1/orgs/{org_id}/pcaps/capture\n\nstartOrgPacketCapture\n\nStart an organization-level packet capture for org-level Mist Edges\n\n**NOTE**: For packet captures of org level Mist Edges only. Use [Start Site Packet Capture](/#operations/startSitePacketCapture) for site level Mist Edges. \n\nThe output will be available through websocket. As there can be multiple commands issued against the same AP at the same time and the output all goes through the same websocket stream, session is introduced for demux.\n\n#### Subscribe to Device Command outputs\n`WS /api-ws/v1/stream`\n\n```json\n{\n    "subscr...',
    capability=Capability.WRITE,
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
    capability=Capability.WRITE,
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
    description="DELETE /api/v1/orgs/{org_id}/pcaps/capture\n\nstopOrgPacketCapture\n\nStop the currently running organization packet capture and end its websocket output stream.",
    capability=Capability.WRITE_DELETE,
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
    capability=Capability.WRITE_DELETE,
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
    capability=Capability.WRITE,
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
