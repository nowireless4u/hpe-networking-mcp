"""Generated EdgeConnect tools — DO NOT EDIT BY HAND.

Emitted by ``scripts/generate_edgeconnect_tools.py`` from
``vendor/edgeconnect/EdgeConnect-9-7-REST-API.json``. Regenerate via:

    uv run python scripts/generate_edgeconnect_tools.py

Tag: ``alarm``
Operations in this file: 33
"""

# ruff: noqa: E501, N803
from __future__ import annotations

from typing import Annotated, Any

from fastmcp import Context
from pydantic import Field

from hpe_networking_mcp.platforms._common.annotations import Capability
from hpe_networking_mcp.platforms.edgeconnect._registry import tool
from hpe_networking_mcp.platforms.edgeconnect.client import edgeconnect_request


@tool(
    name="edgeconnect_delete_alarm_customization_severity",
    description="DELETE /alarm/customization/severity\n\ncustomSeverityDelete14\n\nDelete customized alarm severity configurations",
    capability=Capability.WRITE_DELETE,
)
async def edgeconnect_delete_alarm_customization_severity(
    ctx: Context,
    alarmTypeId: Annotated[
        int | None,
        Field(
            default=None,
            description="Unique identifier for a specific alarm type. If omitted, all custom severity configurations are deleted.",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if alarmTypeId is not None:
        query_params["alarmTypeId"] = alarmTypeId
    return await edgeconnect_request(
        ctx,
        "DELETE",
        "/alarm/customization/severity",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_delete_alarm_delay_email",
    description="DELETE /alarm/delayEmail\n\nalarmEmailDelayDelete20\n\nDelete alarm email delay configuration",
    capability=Capability.WRITE_DELETE,
)
async def edgeconnect_delete_alarm_delay_email(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "DELETE",
        "/alarm/delayEmail",
        query_params=None,
    )


@tool(
    name="edgeconnect_delete_alarm_reset_correlation",
    description="DELETE /alarm/resetCorrelation\n\nresetCorrelation36\n\nReset alarm correlation data",
    capability=Capability.WRITE_DELETE,
)
async def edgeconnect_delete_alarm_reset_correlation(
    ctx: Context,
    includeHistorical: Annotated[
        bool | None,
        Field(
            default=None,
            description="When true, also deletes historical correlated alarms and historical root cause alarms. When false, only current active correlation data is cleared.",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if includeHistorical is not None:
        query_params["includeHistorical"] = includeHistorical
    return await edgeconnect_request(
        ctx,
        "DELETE",
        "/alarm/resetCorrelation",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_delete_alarm_suppress",
    description="DELETE /alarm/suppress\n\ndeleteDisabledAlarmsConfig32\n\nDelete all disabled/suppressed alarm configurations",
    capability=Capability.WRITE_DELETE,
)
async def edgeconnect_delete_alarm_suppress(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "DELETE",
        "/alarm/suppress",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_alarm_alarm_config",
    description="GET /alarm/alarmConfig\n\ngetAlarmsConfig7\n\nGet alarm email notification configurations",
    capability=Capability.READ,
)
async def edgeconnect_get_alarm_alarm_config(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/alarm/alarmConfig",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_alarm_appliance_sub_alarms",
    description="GET /alarm/applianceSubAlarms\n\napplianceSubAlarm25\n\nGet appliance sub-alarms for a parent alarm instance",
    capability=Capability.READ,
)
async def edgeconnect_get_alarm_appliance_sub_alarms(
    ctx: Context,
    nePk: Annotated[
        str,
        Field(
            description="Network Element Primary Key - unique appliance identifier assigned by Orchestrator. Format: '<id>.NE' (e.g., '0.NE', '10.NE')."
        ),
    ],
    instanceId: Annotated[
        int,
        Field(
            description="Unique identifier of the parent alarm instance. Sub-alarms are child alarms grouped under this parent alarm."
        ),
    ],
) -> Any:
    query_params: dict[str, Any] = {}
    if nePk is not None:
        query_params["nePk"] = nePk
    if instanceId is not None:
        query_params["instanceId"] = instanceId
    return await edgeconnect_request(
        ctx,
        "GET",
        "/alarm/applianceSubAlarms",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_alarm_correlated_alarms",
    description="GET /alarm/correlatedAlarms\n\ngetCorrelatedAlarms\n\nRetrieve correlated alarms (active or historical)",
    capability=Capability.READ,
)
async def edgeconnect_get_alarm_correlated_alarms(
    ctx: Context,
    view: Annotated[
        str | None,
        Field(
            default=None,
            description="Filter alarms by status. 'active' returns current unresolved alarms; 'closed' returns historical resolved alarms.",
        ),
    ] = None,
    severity: Annotated[
        str | None,
        Field(
            default=None,
            description="Filter alarms by severity level. When omitted, returns alarms of all severity levels.",
        ),
    ] = None,
    maxAlarms: Annotated[
        int | None, Field(default=None, description="Maximum number of alarms to return. Must be between 1 and 100000.")
    ] = None,
    from_: Annotated[
        int | None,
        Field(
            default=None,
            description="Start time boundary for filtering alarms. Value is milliseconds since UNIX epoch (January 1, 1970).",
        ),
    ] = None,
    to: Annotated[
        int | None,
        Field(
            default=None,
            description="End time boundary for filtering alarms. Value is milliseconds since UNIX epoch (January 1, 1970).",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if view is not None:
        query_params["view"] = view
    if severity is not None:
        query_params["severity"] = severity
    if maxAlarms is not None:
        query_params["maxAlarms"] = maxAlarms
    if from_ is not None:
        query_params["from"] = from_
    if to is not None:
        query_params["to"] = to
    return await edgeconnect_request(
        ctx,
        "GET",
        "/alarm/correlatedAlarms",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_alarm_correlated_rc_alarms",
    description="GET /alarm/correlatedRcAlarms\n\ngetCorrelatedRcAlarms\n\nRetrieve correlated root cause alarms",
    capability=Capability.READ,
)
async def edgeconnect_get_alarm_correlated_rc_alarms(
    ctx: Context,
    view: Annotated[
        str | None,
        Field(
            default=None,
            description="Filter alarms by status. Use 'active' for current unresolved alarms, or 'closed' for historical/resolved alarms.",
        ),
    ] = None,
    maxAlarms: Annotated[
        int | None,
        Field(default=None, description="Maximum number of alarms to return. Limits result set size for performance."),
    ] = None,
    from_: Annotated[
        int | None,
        Field(
            default=None,
            description="Start time boundary in milliseconds since EPOCH (Unix timestamp). Filters alarms that occurred after this time.",
        ),
    ] = None,
    to: Annotated[
        int | None,
        Field(
            default=None,
            description="End time boundary in milliseconds since EPOCH (Unix timestamp). Filters alarms that occurred before this time.",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if view is not None:
        query_params["view"] = view
    if maxAlarms is not None:
        query_params["maxAlarms"] = maxAlarms
    if from_ is not None:
        query_params["from"] = from_
    if to is not None:
        query_params["to"] = to
    return await edgeconnect_request(
        ctx,
        "GET",
        "/alarm/correlatedRcAlarms",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_alarm_correlation_settings",
    description="GET /alarm/correlationSettings\n\ngetAlarmCorrelationSettings35\n\nGet alarm correlation settings",
    capability=Capability.READ,
)
async def edgeconnect_get_alarm_correlation_settings(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/alarm/correlationSettings",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_alarm_correlation_status",
    description="GET /alarm/correlationStatus\n\ngetAlarmCorrelationStatus37\n\nGet alarm correlation status",
    capability=Capability.READ,
)
async def edgeconnect_get_alarm_correlation_status(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/alarm/correlationStatus",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_alarm_count_appliance",
    description="GET /alarm/count/appliance\n\nallApplianceAlarmSummary12\n\nGet active alarm counts for appliances",
    capability=Capability.READ,
)
async def edgeconnect_get_alarm_count_appliance(
    ctx: Context,
    nePk: Annotated[
        str | None,
        Field(
            default=None,
            description="Network Element Primary Key - unique appliance identifier assigned by Orchestrator. Format: '<id>.NE' (e.g., '0.NE', '10.NE'). When omitted, results are returned for all appliances.",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if nePk is not None:
        query_params["nePk"] = nePk
    return await edgeconnect_request(
        ctx,
        "GET",
        "/alarm/count/appliance",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_alarm_customization_severity",
    description="GET /alarm/customization/severity\n\ncustomSeverityGet15\n\nRetrieve customized alarm severity configurations",
    capability=Capability.READ,
)
async def edgeconnect_get_alarm_customization_severity(
    ctx: Context,
    alarmTypeId: Annotated[
        int | None,
        Field(
            default=None,
            description="Filter by specific alarm type ID. If omitted, returns all custom severity configurations.",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if alarmTypeId is not None:
        query_params["alarmTypeId"] = alarmTypeId
    return await edgeconnect_request(
        ctx,
        "GET",
        "/alarm/customization/severity",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_alarm_delay_email",
    description="GET /alarm/delayEmail\n\nalarmEmailDelayGet21\n\nGet alarm email delay configuration",
    capability=Capability.READ,
)
async def edgeconnect_get_alarm_delay_email(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/alarm/delayEmail",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_alarm_description2",
    description="GET /alarm/description2\n\ngetAlarmDescriptions\n\nGet Orchestrator and appliance alarm descriptions",
    capability=Capability.READ,
)
async def edgeconnect_get_alarm_description2(
    ctx: Context,
    format: Annotated[
        str | None,
        Field(
            default=None, description="Output format for the alarm descriptions. Use 'csv' to download as a CSV file."
        ),
    ] = None,
    default: Annotated[
        bool | None,
        Field(
            default=None,
            description="Controls which alarm configuration to return. When true or omitted, returns default alarm descriptions. When false, returns customized alarm descriptions with user modifications.",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if format is not None:
        query_params["format"] = format
    if default is not None:
        query_params["default"] = default
    return await edgeconnect_request(
        ctx,
        "GET",
        "/alarm/description2",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_alarm_gms",
    description="GET /alarm/gms\n\ngetGmsAlarms\n\nRetrieve Orchestrator alarms with filtering options",
    capability=Capability.READ,
)
async def edgeconnect_get_alarm_gms(
    ctx: Context,
    view: Annotated[
        str | None,
        Field(
            default=None,
            description="Alarm state filter. 'active' returns current unresolved alarms, 'closed' returns historical cleared alarms, 'all' returns both active and closed alarms.",
        ),
    ] = None,
    severity: Annotated[
        str | None,
        Field(
            default=None,
            description="Filter alarms by severity level. When specified, only alarms matching the exact severity are returned. Case-insensitive.",
        ),
    ] = None,
    maxAlarms: Annotated[
        int | None, Field(default=None, description="Maximum number of alarms to return. Must be between 1 and 100000.")
    ] = None,
    from_: Annotated[
        int | None,
        Field(
            default=None,
            description="Start time boundary in milliseconds since Unix epoch (January 1, 1970 UTC). Only alarms occurring after this time are returned.",
        ),
    ] = None,
    to: Annotated[
        int | None,
        Field(
            default=None,
            description="End time boundary in milliseconds since Unix epoch. Only alarms occurring before this time are returned.",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if view is not None:
        query_params["view"] = view
    if severity is not None:
        query_params["severity"] = severity
    if maxAlarms is not None:
        query_params["maxAlarms"] = maxAlarms
    if from_ is not None:
        query_params["from"] = from_
    if to is not None:
        query_params["to"] = to
    return await edgeconnect_request(
        ctx,
        "GET",
        "/alarm/gms",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_alarm_notification",
    description="GET /alarm/notification\n\ngetAlarmNotification\n\nGet alarm notification settings",
    capability=Capability.READ,
)
async def edgeconnect_get_alarm_notification(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/alarm/notification",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_alarm_summary",
    description="GET /alarm/summary\n\ngetAlarmSummary\n\nGet alarm summary counts by severity",
    capability=Capability.READ,
)
async def edgeconnect_get_alarm_summary(
    ctx: Context,
    type: Annotated[
        str | None,
        Field(
            default=None,
            description="Filter alarm summary by source type. When omitted, returns combined totals from both Orchestrator and all accessible appliances.",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if type is not None:
        query_params["type"] = type
    return await edgeconnect_request(
        ctx,
        "GET",
        "/alarm/summary",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_alarm_suppress",
    description="GET /alarm/suppress\n\ngetAllDisabledAlarmsConfig33\n\nRetrieve all suppressed/disabled alarm configurations",
    capability=Capability.READ,
)
async def edgeconnect_get_alarm_suppress(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/alarm/suppress",
        query_params=None,
    )


@tool(
    name="edgeconnect_post_alarm_acknowledgement_appliance",
    description="POST /alarm/acknowledgement/appliance\n\nalarmAcknowledgement5\n\nAcknowledge or unacknowledge appliance alarms",
    capability=Capability.WRITE,
)
async def edgeconnect_post_alarm_acknowledgement_appliance(
    ctx: Context,
    nePk: Annotated[
        str,
        Field(
            description="Network Element Primary Key - unique appliance identifier assigned by Orchestrator. Format: '<id>.NE' (e.g., '0.NE', '10.NE')."
        ),
    ],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    query_params: dict[str, Any] = {}
    if nePk is not None:
        query_params["nePk"] = nePk
    return await edgeconnect_request(
        ctx,
        "POST",
        "/alarm/acknowledgement/appliance",
        query_params=query_params or None,
        body=body,
    )


@tool(
    name="edgeconnect_post_alarm_acknowledgement_gms",
    description="POST /alarm/acknowledgement/gms\n\ngmsAlarmAcknowledgement6\n\nAcknowledge or unacknowledge Orchestrator alarms",
    capability=Capability.WRITE,
)
async def edgeconnect_post_alarm_acknowledgement_gms(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/alarm/acknowledgement/gms",
        query_params=None,
        body=body,
    )


@tool(
    name="edgeconnect_post_alarm_alarm_config",
    description="POST /alarm/alarmConfig\n\nalarmsConfig8\n\nCreate or update alarm email notification configurations",
    capability=Capability.WRITE,
)
async def edgeconnect_post_alarm_alarm_config(
    ctx: Context,
    body: Annotated[list[Any], Field(description="Request body (required)")],
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/alarm/alarmConfig",
        query_params=None,
        body=body,
    )


@tool(
    name="edgeconnect_post_alarm_appliance",
    description="POST /alarm/appliance\n\ngetApplianceAlarms\n\nRetrieve appliance alarms for specified appliances",
    capability=Capability.WRITE,
)
async def edgeconnect_post_alarm_appliance(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
    view: Annotated[
        str | None,
        Field(
            default=None,
            description="Filter alarms by status. 'active' returns current unresolved alarms, 'closed' returns historical resolved alarms, 'all' returns both.",
        ),
    ] = None,
    severity: Annotated[
        str | None,
        Field(
            default=None,
            description="Filter alarms by severity level. When specified, only alarms of this severity are returned. Case-insensitive.",
        ),
    ] = None,
    orderBySeverity: Annotated[
        bool | None,
        Field(
            default=None,
            description="When true, results are sorted by severity level (critical first). Default is chronological order.",
        ),
    ] = None,
    maxAlarms: Annotated[
        int | None, Field(default=None, description="Maximum number of alarms to return. Must be between 1 and 100000.")
    ] = None,
    from_: Annotated[
        int | None,
        Field(
            default=None,
            description="Start time boundary in milliseconds since EPOCH (Unix timestamp * 1000). Only alarms occurring after this time are returned.",
        ),
    ] = None,
    to: Annotated[
        int | None,
        Field(
            default=None,
            description="End time boundary in milliseconds since EPOCH (Unix timestamp * 1000). Only alarms occurring before this time are returned.",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if view is not None:
        query_params["view"] = view
    if severity is not None:
        query_params["severity"] = severity
    if orderBySeverity is not None:
        query_params["orderBySeverity"] = orderBySeverity
    if maxAlarms is not None:
        query_params["maxAlarms"] = maxAlarms
    if from_ is not None:
        query_params["from"] = from_
    if to is not None:
        query_params["to"] = to
    return await edgeconnect_request(
        ctx,
        "POST",
        "/alarm/appliance",
        query_params=query_params or None,
        body=body,
    )


@tool(
    name="edgeconnect_post_alarm_clearance_appliance",
    description="POST /alarm/clearance/appliance\n\nalarmClearance10\n\nClear appliance alarms",
    capability=Capability.WRITE,
)
async def edgeconnect_post_alarm_clearance_appliance(
    ctx: Context,
    nePk: Annotated[
        str,
        Field(
            description="Network Element Primary Key - unique appliance identifier assigned by Orchestrator. Format: '<id>.NE' (e.g., '0.NE', '10.NE')."
        ),
    ],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    query_params: dict[str, Any] = {}
    if nePk is not None:
        query_params["nePk"] = nePk
    return await edgeconnect_request(
        ctx,
        "POST",
        "/alarm/clearance/appliance",
        query_params=query_params or None,
        body=body,
    )


@tool(
    name="edgeconnect_post_alarm_clearance_gms",
    description="POST /alarm/clearance/gms\n\ngmsAlarmClearance11\n\nClear Orchestrator alarms",
    capability=Capability.WRITE,
)
async def edgeconnect_post_alarm_clearance_gms(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/alarm/clearance/gms",
        query_params=None,
        body=body,
    )


@tool(
    name="edgeconnect_post_alarm_correlation_settings",
    description="POST /alarm/correlationSettings\n\nupdateAlarmCorrelationSettings36\n\nUpdate alarm correlation settings",
    capability=Capability.WRITE,
)
async def edgeconnect_post_alarm_correlation_settings(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/alarm/correlationSettings",
        query_params=None,
        body=body,
    )


@tool(
    name="edgeconnect_post_alarm_customization_severity",
    description="POST /alarm/customization/severity\n\ncustomSeverityPOST16\n\nCreate custom alarm severity configurations",
    capability=Capability.WRITE,
)
async def edgeconnect_post_alarm_customization_severity(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/alarm/customization/severity",
        query_params=None,
        body=body,
    )


@tool(
    name="edgeconnect_post_alarm_delay_email",
    description="POST /alarm/delayEmail\n\nalarmEmailDelayPost22\n\nCreate alarm email delay configuration",
    capability=Capability.WRITE,
)
async def edgeconnect_post_alarm_delay_email(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/alarm/delayEmail",
        query_params=None,
        body=body,
    )


@tool(
    name="edgeconnect_post_alarm_note_appliance",
    description="POST /alarm/note/appliance\n\nalarmNotes26\n\nCapture comments for appliance alarms",
    capability=Capability.WRITE,
)
async def edgeconnect_post_alarm_note_appliance(
    ctx: Context,
    nePk: Annotated[
        str,
        Field(
            description="Network Element Primary Key - unique appliance identifier assigned by Orchestrator. Format: '<id>.NE' (e.g., '0.NE', '10.NE')."
        ),
    ],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    query_params: dict[str, Any] = {}
    if nePk is not None:
        query_params["nePk"] = nePk
    return await edgeconnect_request(
        ctx,
        "POST",
        "/alarm/note/appliance",
        query_params=query_params or None,
        body=body,
    )


@tool(
    name="edgeconnect_post_alarm_note_gms",
    description="POST /alarm/note/gms\n\ngmsAlarmNote27\n\nCapture comments for GMS alarms",
    capability=Capability.WRITE,
)
async def edgeconnect_post_alarm_note_gms(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/alarm/note/gms",
        query_params=None,
        body=body,
    )


@tool(
    name="edgeconnect_post_alarm_notification",
    description="POST /alarm/notification\n\nsetAlarmNotification\n\nSet alarm notification settings",
    capability=Capability.WRITE,
)
async def edgeconnect_post_alarm_notification(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/alarm/notification",
        query_params=None,
        body=body,
    )


@tool(
    name="edgeconnect_post_alarm_suppress",
    description="POST /alarm/suppress\n\nupdateDisabledAlarmsConfig34\n\nEnable or disable alarm suppression for alarm types or appliances",
    capability=Capability.WRITE,
)
async def edgeconnect_post_alarm_suppress(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/alarm/suppress",
        query_params=None,
        body=body,
    )


@tool(
    name="edgeconnect_put_alarm_customization_severity",
    description="PUT /alarm/customization/severity\n\ncustomSeverityPut17\n\nUpdate existing custom alarm severity configurations",
    capability=Capability.WRITE,
)
async def edgeconnect_put_alarm_customization_severity(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await edgeconnect_request(
        ctx,
        "PUT",
        "/alarm/customization/severity",
        query_params=None,
        body=body,
    )


@tool(
    name="edgeconnect_put_alarm_delay_email",
    description="PUT /alarm/delayEmail\n\nalarmEmailDelayPut23\n\nUpdate alarm email delay configuration",
    capability=Capability.WRITE,
)
async def edgeconnect_put_alarm_delay_email(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await edgeconnect_request(
        ctx,
        "PUT",
        "/alarm/delayEmail",
        query_params=None,
        body=body,
    )
