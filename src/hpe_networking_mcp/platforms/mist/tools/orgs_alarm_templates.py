"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``hpe_networking_mcp.platforms.mist._generator``
from ``vendor/mist_openapi.json``. Regenerate via:

    uv run python -m hpe_networking_mcp.platforms.mist.regenerate

Tag: ``Orgs Alarm Templates``
Operations in this file: 8
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
    name="mist_create_org_alarm_template",
    description="POST /api/v1/orgs/{org_id}/alarmtemplates\n\ncreateOrgAlarmTemplate\n\nAvailable rules can be found in [List Alarm Definitions#](/#operations/listAlarmDefinitions)\n\nThe delivery dict is only required if different from the template delivery settings.",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_create_org_alarm_template(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request Body")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/orgs/{org_id}/alarmtemplates",
        path_params={"org_id": org_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_delete_org_alarm_template",
    description="DELETE /api/v1/orgs/{org_id}/alarmtemplates/{alarmtemplate_id}\n\ndeleteOrgAlarmTemplate\n\nDelete Org Alarm Template",
    tags={"mist", "mist_write", "mist_write_delete"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=True),
)
async def mist_delete_org_alarm_template(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    alarmtemplate_id: Annotated[str, Field(description="path parameter 'alarmtemplate_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "DELETE",
        "/api/v1/orgs/{org_id}/alarmtemplates/{alarmtemplate_id}",
        path_params={"org_id": org_id, "alarmtemplate_id": alarmtemplate_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_get_org_alarm_template",
    description="GET /api/v1/orgs/{org_id}/alarmtemplates/{alarmtemplate_id}\n\ngetOrgAlarmTemplate\n\nGet Org Alarm Template Details",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_get_org_alarm_template(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    alarmtemplate_id: Annotated[str, Field(description="path parameter 'alarmtemplate_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/orgs/{org_id}/alarmtemplates/{alarmtemplate_id}",
        path_params={"org_id": org_id, "alarmtemplate_id": alarmtemplate_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_list_org_alarm_templates",
    description="GET /api/v1/orgs/{org_id}/alarmtemplates\n\nlistOrgAlarmTemplates\n\nGet List of Org Alarm Templates",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_list_org_alarm_templates(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    limit: Annotated[int, Field(description="query parameter 'limit'")] = 100,
    page: Annotated[int, Field(description="query parameter 'page'")] = 1,
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/orgs/{org_id}/alarmtemplates",
        path_params={"org_id": org_id},
        query_params={"limit": limit, "page": page},
        body=None,
    )


@_mcp_tool(
    name="mist_list_org_suppressed_alarms",
    description="GET /api/v1/orgs/{org_id}/alarmtemplates/suppress\n\nlistOrgSuppressedAlarms\n\nGet List of Org Alarms Currently Suppressed",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_list_org_suppressed_alarms(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    scope: Annotated[Any | None, Field(description="Returns both scopes if not specified")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/orgs/{org_id}/alarmtemplates/suppress",
        path_params={"org_id": org_id},
        query_params={"scope": scope},
        body=None,
    )


@_mcp_tool(
    name="mist_suppress_org_alarm",
    description="POST /api/v1/orgs/{org_id}/alarmtemplates/suppress\n\nsuppressOrgAlarm\n\nIn certain situations, for example, scheduled maintenance, you may want to suspend alarms to be triggered against Sites for a period of time.",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_suppress_org_alarm(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    body: Annotated[
        dict[str, Any] | None,
        Field(default=None, description="Request body for POST /api/v1/orgs/{org_id}/alarmtemplates/suppress"),
    ] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/orgs/{org_id}/alarmtemplates/suppress",
        path_params={"org_id": org_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_unsuppress_org_suppressed_alarms",
    description="DELETE /api/v1/orgs/{org_id}/alarmtemplates/suppress\n\nunsuppressOrgSuppressedAlarms\n\nUn-Suppress Suppressed Alarms",
    tags={"mist", "mist_write", "mist_write_delete"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=True),
)
async def mist_unsuppress_org_suppressed_alarms(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "DELETE",
        "/api/v1/orgs/{org_id}/alarmtemplates/suppress",
        path_params={"org_id": org_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_update_org_alarm_template",
    description="PUT /api/v1/orgs/{org_id}/alarmtemplates/{alarmtemplate_id}\n\nupdateOrgAlarmTemplate\n\nUpdate Org Alarm Template",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_update_org_alarm_template(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    alarmtemplate_id: Annotated[str, Field(description="path parameter 'alarmtemplate_id'")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request Body")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "PUT",
        "/api/v1/orgs/{org_id}/alarmtemplates/{alarmtemplate_id}",
        path_params={"org_id": org_id, "alarmtemplate_id": alarmtemplate_id},
        query_params=None,
        body=body,
    )
