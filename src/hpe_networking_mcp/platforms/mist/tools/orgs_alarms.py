"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``scripts/_mist_generator.py``
from ``vendor/mist_openapi.json``. Regenerate via:

    uv run python scripts/regenerate_mist_tools.py

Tag: ``Orgs Alarms``
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
    name="mist_ack_org_alarm",
    description="POST /api/v1/orgs/{org_id}/alarms/{alarm_id}/ack\n\nackOrgAlarm\n\nAck Org Alarm",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_ack_org_alarm(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    alarm_id: Annotated[str, Field(description="path parameter 'alarm_id'")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request Body")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/orgs/{org_id}/alarms/{alarm_id}/ack",
        path_params={"org_id": org_id, "alarm_id": alarm_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_ack_org_all_alarms",
    description="POST /api/v1/orgs/{org_id}/alarms/ack_all\n\nackOrgAllAlarms\n\nAck all Org Alarms\n\n**N.B.**: Batch size for multiple alarm ack and unack has to be less or or equal to 1000.",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_ack_org_all_alarms(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    body: Annotated[
        dict[str, Any] | None,
        Field(default=None, description="Request body for POST /api/v1/orgs/{org_id}/alarms/ack_all"),
    ] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/orgs/{org_id}/alarms/ack_all",
        path_params={"org_id": org_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_ack_org_multiple_alarms",
    description="POST /api/v1/orgs/{org_id}/alarms/ack\n\nackOrgMultipleAlarms\n\nAck multiple Org Alarms",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_ack_org_multiple_alarms(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request Body")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/orgs/{org_id}/alarms/ack",
        path_params={"org_id": org_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_count_org_alarms",
    description="GET /api/v1/orgs/{org_id}/alarms/count\n\ncountOrgAlarms\n\nCount by Distinct Attributes of Org Alarms",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_count_org_alarms(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    distinct: Annotated[str | None, Field(description="query parameter 'distinct'")] = None,
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
        "/api/v1/orgs/{org_id}/alarms/count",
        path_params={"org_id": org_id},
        query_params={"distinct": distinct, "start": start, "end": end, "duration": duration, "limit": limit},
        body=None,
    )


@_mcp_tool(
    name="mist_search_org_alarms",
    description="GET /api/v1/orgs/{org_id}/alarms/search\n\nsearchOrgAlarms\n\nSearch Org Alarms",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_search_org_alarms(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    site_id: Annotated[str | None, Field(description="Site ID")] = None,
    group: Annotated[
        Any | None,
        Field(
            description="Alarm group. enum: `infrastructure`, `marvis`, `security`. \nThe `marvis` group is used to retrieve AI-driven network issue detections. \nKnown Marvis alarm types include: `bad_cable`, `bad_wan_uplink`, `dns_failure`, \n`arp_failure`, `auth..."
        ),
    ] = None,
    severity: Annotated[
        Any | None, Field(description="Severity of the alarm. enum: `critical`, `info`, `warn`")
    ] = None,
    type: Annotated[
        str | None,
        Field(
            description="Type of the alarm. Accepts multiple values separated by comma. Use [List Alarm Definitions](/#operations/listAlarmDefinitions) to get the list of possible alarm types."
        ),
    ] = None,
    ack_admin_name: Annotated[
        str | None,
        Field(description="Name of the admins who have acked the alarms; accepts multiple values separated by comma"),
    ] = None,
    acked: Annotated[bool | None, Field(description="query parameter 'acked'")] = None,
    start: Annotated[
        str | None, Field(description='Start time (epoch timestamp in seconds, or relative string like "-1d", "-1w")')
    ] = None,
    end: Annotated[
        str | None,
        Field(description='End time (epoch timestamp in seconds, or relative string like "-1d", "-2h", "now")'),
    ] = None,
    duration: Annotated[str, Field(description="Duration like 7d, 2w")] = "1d",
    limit: Annotated[int, Field(description="query parameter 'limit'")] = 100,
    sort: Annotated[
        str, Field(description="On which field the list should be sorted, -prefix represents DESC order")
    ] = "timestamp",
    search_after: Annotated[
        str | None,
        Field(
            description="Pagination cursor for retrieving subsequent pages of results. This value is automatically populated by Mist in the `next` URL from the previous response and should not be manually constructed."
        ),
    ] = None,
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/orgs/{org_id}/alarms/search",
        path_params={"org_id": org_id},
        query_params={
            "site_id": site_id,
            "group": group,
            "severity": severity,
            "type": type,
            "ack_admin_name": ack_admin_name,
            "acked": acked,
            "start": start,
            "end": end,
            "duration": duration,
            "limit": limit,
            "sort": sort,
            "search_after": search_after,
        },
        body=None,
    )


@_mcp_tool(
    name="mist_subscribe_org_alarms_reports",
    description="POST /api/v1/orgs/{org_id}/subscriptions\n\nsubscribeOrgAlarmsReports\n\nSubscribe to Org Alarms/Reports\nSubscriptions define how Org Alarms/Reports are delivered to whom",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_subscribe_org_alarms_reports(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/orgs/{org_id}/subscriptions",
        path_params={"org_id": org_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_unack_org_all_alarms",
    description="POST /api/v1/orgs/{org_id}/alarms/unack_all\n\nunackOrgAllAlarms\n\nUnack all Org Alarms\n\n**N.B.**: Batch size for multiple alarm ack and unack has to be less or or equal to 1000.",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_unack_org_all_alarms(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request Body")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/orgs/{org_id}/alarms/unack_all",
        path_params={"org_id": org_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_unack_org_multiple_alarms",
    description="POST /api/v1/orgs/{org_id}/alarms/unack\n\nunackOrgMultipleAlarms\n\nUnack multiple Org Alarms",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_unack_org_multiple_alarms(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request Body")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/orgs/{org_id}/alarms/unack",
        path_params={"org_id": org_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_unsubscribe_org_alarms_reports",
    description="DELETE /api/v1/orgs/{org_id}/subscriptions\n\nunsubscribeOrgAlarmsReports\n\nUnsubscribe from Org Alarms/Reports\nSubscriptions define how Org Alarms/Reports are delivered to whom",
    tags={"mist", "mist_write", "mist_write_delete"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=True),
)
async def mist_unsubscribe_org_alarms_reports(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "DELETE",
        "/api/v1/orgs/{org_id}/subscriptions",
        path_params={"org_id": org_id},
        query_params=None,
        body=None,
    )
