"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``scripts/_mist_generator.py`` from
``vendor/mist/mist_openapi.json``. Regenerate via:

    uv run python scripts/regenerate_mist_tools.py

Tag: ``Orgs Alarm Templates``
Operations in this file: 8
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
    name="mist_create_org_alarm_template",
    description="POST /api/v1/orgs/{org_id}/alarmtemplates\n\ncreateOrgAlarmTemplate\n\nCreate an organization alarm template that defines default delivery settings and per-alarm rule overrides.\nAvailable rules can be found in [List Alarm Definitions](/#operations/listAlarmDefinitions)\n\nThe `delivery` object is only required when it differs from the template delivery settings.\nTo assign an Alarm template to a site, use the [Update Site](/#operations/updateSiteInfo) endpoint and specify the Alarm template ID in the `alarmtemplate_id` field of the request body.",
    capability=Capability.WRITE,
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
    description="DELETE /api/v1/orgs/{org_id}/alarmtemplates/{alarmtemplate_id}\n\ndeleteOrgAlarmTemplate\n\nDelete an organization alarm template by template ID from this organization.",
    capability=Capability.WRITE_DELETE,
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
    description="GET /api/v1/orgs/{org_id}/alarmtemplates/{alarmtemplate_id}\n\ngetOrgAlarmTemplate\n\nReturn one organization alarm template, including default delivery settings and per-alarm rule overrides.",
    capability=Capability.READ,
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
    description="GET /api/v1/orgs/{org_id}/alarmtemplates\n\nlistOrgAlarmTemplates\n\nList alarm templates defined for the organization, including default delivery settings and per-alarm rule configuration.",
    capability=Capability.READ,
)
async def mist_list_org_alarm_templates(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    limit: Annotated[int, Field(description="Maximum number of results to return per page")] = 100,
    page: Annotated[
        int, Field(description="Select the page number to return when using page-based pagination; starts at `1`")
    ] = 1,
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
    description="GET /api/v1/orgs/{org_id}/alarmtemplates/suppress\n\nlistOrgSuppressedAlarms\n\nList alarm suppression entries currently configured for this organization, optionally filtered by organization-wide or site-specific scope.",
    capability=Capability.READ,
)
async def mist_list_org_suppressed_alarms(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    scope: Annotated[Any | None, Field(description="Filter results by scope. enum: `org`, `site`")] = None,
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
    description="POST /api/v1/orgs/{org_id}/alarmtemplates/suppress\n\nsuppressOrgAlarm\n\nCreate or schedule an alarm suppression window for the organization or selected sites, for example during planned maintenance.",
    capability=Capability.WRITE,
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
    description="DELETE /api/v1/orgs/{org_id}/alarmtemplates/suppress\n\nunsuppressOrgSuppressedAlarms\n\nRemove alarm suppression entries currently configured for this organization.",
    capability=Capability.WRITE_DELETE,
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
    description="PUT /api/v1/orgs/{org_id}/alarmtemplates/{alarmtemplate_id}\n\nupdateOrgAlarmTemplate\n\nUpdate an organization alarm template's default delivery settings or per-alarm rule overrides.",
    capability=Capability.WRITE,
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
