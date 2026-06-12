"""ClearPass audit and insight write tools (alerts, reports, system events)."""

from __future__ import annotations

from typing import Annotated

from fastmcp import Context
from fastmcp.exceptions import ToolError
from pydantic import Field

from hpe_networking_mcp.platforms._common.annotations import Capability
from hpe_networking_mcp.platforms._common.url import path_seg
from hpe_networking_mcp.platforms.clearpass._registry import tool
from hpe_networking_mcp.platforms.clearpass.client import ClearPassClient, get_clearpass_client

_ALERT_ACTIONS = ("create", "update", "delete", "enable", "disable", "mute", "unmute")
_REPORT_ACTIONS = ("create", "delete", "enable", "disable", "run")


@tool(capability=Capability.WRITE_DELETE)
async def clearpass_manage_insight_alert(
    ctx: Context,
    action_type: Annotated[
        str,
        Field(description="Action: 'create', 'update', 'delete', 'enable', 'disable', 'mute', or 'unmute'."),
    ],
    payload: Annotated[dict, Field(description="Alert config payload. For delete/enable/disable/mute/unmute: {}.")],
    alert_id: Annotated[str | None, Field(description="Alert ID (required for all actions except create).")] = None,
    confirmed: Annotated[
        bool,
        Field(
            description="Fallback confirmation flag — honored only when the client cannot show a "
            "confirmation prompt (the universal gate prompts otherwise)."
        ),
    ] = False,
) -> dict | str:
    """Create, update, delete, enable, disable, mute, or unmute a ClearPass Insight alert.

    Insight alerts trigger notifications when specified conditions are met in ClearPass
    authentication or system data.

    Args:
        action_type: Operation to perform on the alert.
        payload: JSON config body. Required for create/update. Empty dict for other actions.
        alert_id: Alert ID. Required for all actions except create.
        confirmed: Fallback confirmation flag — honored only when the client cannot show a
            confirmation prompt (the universal gate prompts otherwise).
    """
    if action_type not in _ALERT_ACTIONS:
        raise ToolError(
            {
                "status_code": 400,
                "message": f"Invalid action_type '{action_type}'. Must be one of: {', '.join(_ALERT_ACTIONS)}.",
            }
        )

    try:
        client = await get_clearpass_client()
        return await _execute_alert_action(client, action_type, payload, alert_id)
    except ToolError:
        raise
    except Exception as e:
        raise ToolError({"status_code": 502, "message": f"Error managing insight alert: {e}"}) from e


async def _execute_alert_action(
    client: ClearPassClient, action_type: str, payload: dict, alert_id: str | None
) -> dict | str:
    """Execute the resolved insight alert action.

    Args:
        client: ClearPass API client.
        action_type: Alert operation to perform.
        payload: Configuration payload.
        alert_id: Alert ID for non-create actions.

    Returns:
        API response dict or error string.
    """
    if action_type == "create":
        return await client.request("post", "/alert", json_body=payload)
    if not alert_id:
        raise ToolError({"status_code": 400, "message": "alert_id is required for this action."})
    if action_type == "update":
        return await client.request("patch", f"/alert/{path_seg(alert_id)}", json_body=payload)
    if action_type == "delete":
        return await client.request("delete", f"/alert/{path_seg(alert_id)}")
    if action_type == "enable":
        return await client.request("patch", f"/alert/{path_seg(alert_id)}/enable")
    if action_type == "disable":
        return await client.request("patch", f"/alert/{path_seg(alert_id)}/disable")
    if action_type == "mute":
        return await client.request("patch", f"/alert/{path_seg(alert_id)}/mute", json_body={})
    if action_type == "unmute":
        return await client.request("patch", f"/alert/{path_seg(alert_id)}/unmute", json_body={})
    raise ToolError({"status_code": 500, "message": f"Unhandled action_type: {action_type}"})


@tool(capability=Capability.WRITE_DELETE)
async def clearpass_manage_insight_report(
    ctx: Context,
    action_type: Annotated[
        str,
        Field(description="Action: 'create', 'delete', 'enable', 'disable', or 'run'."),
    ],
    payload: Annotated[dict, Field(description="Report config payload. For delete/enable/disable/run: {}.")],
    report_id: Annotated[str | None, Field(description="Report ID (required for all actions except create).")] = None,
    confirmed: Annotated[
        bool,
        Field(
            description="Fallback confirmation flag — honored only when the client cannot show a "
            "confirmation prompt (the universal gate prompts otherwise)."
        ),
    ] = False,
) -> dict | str:
    """Create, delete, enable, disable, or run a ClearPass Insight report.

    Insight reports generate analytics on authentication sessions, endpoints,
    and system health data.

    Args:
        action_type: Operation to perform on the report.
        payload: JSON config body. Required for create. Empty dict for other actions.
        report_id: Report ID. Required for all actions except create.
        confirmed: Fallback confirmation flag — honored only when the client cannot show a
            confirmation prompt (the universal gate prompts otherwise).
    """
    if action_type not in _REPORT_ACTIONS:
        raise ToolError(
            {
                "status_code": 400,
                "message": f"Invalid action_type '{action_type}'. Must be one of: {', '.join(_REPORT_ACTIONS)}.",
            }
        )

    try:
        client = await get_clearpass_client()
        return await _execute_report_action(client, action_type, payload, report_id)
    except ToolError:
        raise
    except Exception as e:
        raise ToolError({"status_code": 502, "message": f"Error managing insight report: {e}"}) from e


async def _execute_report_action(
    client: ClearPassClient, action_type: str, payload: dict, report_id: str | None
) -> dict | str:
    """Execute the resolved insight report action.

    Args:
        client: ClearPass API client.
        action_type: Report operation to perform.
        payload: Configuration payload.
        report_id: Report ID for non-create actions.

    Returns:
        API response dict or error string.
    """
    if action_type == "create":
        return await client.request("post", "/report", json_body=payload)
    if not report_id:
        raise ToolError({"status_code": 400, "message": "report_id is required for this action."})
    if action_type == "delete":
        return await client.request("delete", f"/report/{path_seg(report_id)}")
    if action_type == "enable":
        return await client.request("patch", f"/report/{path_seg(report_id)}/enable")
    if action_type == "disable":
        return await client.request("patch", f"/report/{path_seg(report_id)}/disable")
    if action_type == "run":
        return await client.request("post", f"/report/{path_seg(report_id)}/run")
    raise ToolError({"status_code": 500, "message": f"Unhandled action_type: {action_type}"})


@tool(capability=Capability.WRITE, tags={"clearpass_write_delete"})
async def clearpass_create_system_event(
    ctx: Context,
    source: Annotated[str, Field(description="Event source (e.g. 'MCP Server', 'Admin').")],
    level: Annotated[str, Field(description="Severity level: 'INFO', 'WARN', or 'ERROR'.")],
    category: Annotated[str, Field(description="Event category (e.g. 'Configuration', 'Authentication').")],
    action: Annotated[str, Field(description="Event action description (e.g. 'Policy Updated').")],
    description: Annotated[str, Field(description="Detailed event description.")],
    confirmed: Annotated[
        bool,
        Field(
            description="Fallback confirmation flag — honored only when the client cannot show a "
            "confirmation prompt (the universal gate prompts otherwise)."
        ),
    ] = False,
) -> dict | str:
    """Create a custom system event in ClearPass for audit logging.

    System events appear in the ClearPass Event Viewer and can be used for
    compliance tracking and change management.

    Args:
        source: The source system or user generating the event.
        level: Severity — 'INFO', 'WARN', or 'ERROR'.
        category: Event category for classification.
        action: Short action description.
        description: Detailed description of the event.
        confirmed: Fallback confirmation flag — honored only when the client cannot show a
            confirmation prompt (the universal gate prompts otherwise).
    """
    if level not in ("INFO", "WARN", "ERROR"):
        raise ToolError(
            {"status_code": 400, "message": f"Invalid level '{level}'. Must be 'INFO', 'WARN', or 'ERROR'."}
        )

    try:
        client = await get_clearpass_client()
        payload = {
            "source": source,
            "level": level,
            "category": category,
            "action": action,
            "description": description,
        }
        return await client.request("post", "/system-event", json_body=payload)
    except ToolError:
        raise
    except Exception as e:
        raise ToolError({"status_code": 502, "message": f"Error creating system event: {e}"}) from e
