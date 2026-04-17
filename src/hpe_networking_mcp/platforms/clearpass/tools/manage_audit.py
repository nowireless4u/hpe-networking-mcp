"""ClearPass audit and insight write tools (alerts, reports, system events)."""

from __future__ import annotations

from typing import Annotated

from fastmcp import Context
from pydantic import Field

from hpe_networking_mcp.middleware.elicitation import elicitation_handler
from hpe_networking_mcp.platforms.clearpass._registry import mcp
from hpe_networking_mcp.platforms.clearpass.client import get_clearpass_session
from hpe_networking_mcp.platforms.clearpass.tools import WRITE_DELETE

_ALERT_ACTIONS = ("create", "update", "delete", "enable", "disable", "mute", "unmute")
_REPORT_ACTIONS = ("create", "delete", "enable", "disable", "run")


async def _confirm_write(ctx: Context, action: str, identifier: str | None) -> dict | None:
    """Request user confirmation for destructive audit actions.

    Args:
        ctx: FastMCP context.
        action: The operation being performed.
        identifier: Item ID for display.

    Returns:
        Error dict if declined/canceled, None if accepted.
    """
    label = identifier or "unknown"
    elicit = await elicitation_handler(
        message=f"ClearPass: {action} '{label}'. Confirm?",
        ctx=ctx,
    )
    if elicit.action == "decline":
        mode = await ctx.get_state("elicitation_mode")
        if mode == "chat_confirm":
            return {
                "status": "confirmation_required",
                "message": f"Please confirm {action} of '{label}'. "
                "Call this tool again with confirmed=true after the user confirms.",
            }
        return {"message": "Action declined by user."}
    elif elicit.action == "cancel":
        return {"message": "Action canceled by user."}
    return None


@mcp.tool(annotations=WRITE_DELETE, tags={"clearpass_write_delete"})
async def clearpass_manage_insight_alert(
    ctx: Context,
    action_type: Annotated[
        str,
        Field(description="Action: 'create', 'update', 'delete', 'enable', 'disable', 'mute', or 'unmute'."),
    ],
    payload: Annotated[dict, Field(description="Alert config payload. For delete/enable/disable/mute/unmute: {}.")],
    alert_id: Annotated[str | None, Field(description="Alert ID (required for all actions except create).")] = None,
    confirmed: Annotated[bool, Field(description="Set true after user confirms the operation.")] = False,
) -> dict | str:
    """Create, update, delete, enable, disable, mute, or unmute a ClearPass Insight alert.

    Insight alerts trigger notifications when specified conditions are met in ClearPass
    authentication or system data.

    Args:
        action_type: Operation to perform on the alert.
        payload: JSON config body. Required for create/update. Empty dict for other actions.
        alert_id: Alert ID. Required for all actions except create.
        confirmed: Set true after user confirms. Skips re-prompting.
    """
    if action_type not in _ALERT_ACTIONS:
        return f"Invalid action_type '{action_type}'. Must be one of: {', '.join(_ALERT_ACTIONS)}."

    if action_type != "create" and not confirmed:
        decline = await _confirm_write(ctx, f"{action_type} insight alert", alert_id)
        if decline:
            return decline

    try:
        from pyclearpass.api_insight import ApiInsight

        client = await get_clearpass_session(ApiInsight)
        return _execute_alert_action(client, action_type, payload, alert_id)
    except Exception as e:
        return f"Error managing insight alert: {e}"


def _execute_alert_action(client, action_type: str, payload: dict, alert_id: str | None) -> dict | str:
    """Execute the resolved insight alert action.

    Args:
        client: pyclearpass ApiInsight instance.
        action_type: Alert operation to perform.
        payload: Configuration payload.
        alert_id: Alert ID for non-create actions.

    Returns:
        API response dict or error string.
    """
    if action_type == "create":
        return client._send_request("/alert", "post", query=payload)
    if not alert_id:
        return "alert_id is required for this action."
    if action_type == "update":
        return client._send_request(f"/alert/{alert_id}", "patch", query=payload)
    if action_type == "delete":
        return client.delete_alert_by_id(id=alert_id)
    if action_type == "enable":
        return client.update_alert_by_id_enable(id=alert_id)
    if action_type == "disable":
        return client.update_alert_by_id_disable(id=alert_id)
    if action_type == "mute":
        return client._send_request(f"/alert/{alert_id}/mute", "patch", query={})
    if action_type == "unmute":
        return client._send_request(f"/alert/{alert_id}/unmute", "patch", query={})
    return f"Unhandled action_type: {action_type}"


@mcp.tool(annotations=WRITE_DELETE, tags={"clearpass_write_delete"})
async def clearpass_manage_insight_report(
    ctx: Context,
    action_type: Annotated[
        str,
        Field(description="Action: 'create', 'delete', 'enable', 'disable', or 'run'."),
    ],
    payload: Annotated[dict, Field(description="Report config payload. For delete/enable/disable/run: {}.")],
    report_id: Annotated[str | None, Field(description="Report ID (required for all actions except create).")] = None,
    confirmed: Annotated[bool, Field(description="Set true after user confirms the operation.")] = False,
) -> dict | str:
    """Create, delete, enable, disable, or run a ClearPass Insight report.

    Insight reports generate analytics on authentication sessions, endpoints,
    and system health data.

    Args:
        action_type: Operation to perform on the report.
        payload: JSON config body. Required for create. Empty dict for other actions.
        report_id: Report ID. Required for all actions except create.
        confirmed: Set true after user confirms. Skips re-prompting.
    """
    if action_type not in _REPORT_ACTIONS:
        return f"Invalid action_type '{action_type}'. Must be one of: {', '.join(_REPORT_ACTIONS)}."

    if action_type != "create" and not confirmed:
        decline = await _confirm_write(ctx, f"{action_type} insight report", report_id)
        if decline:
            return decline

    try:
        from pyclearpass.api_insight import ApiInsight

        client = await get_clearpass_session(ApiInsight)
        return _execute_report_action(client, action_type, payload, report_id)
    except Exception as e:
        return f"Error managing insight report: {e}"


def _execute_report_action(client, action_type: str, payload: dict, report_id: str | None) -> dict | str:
    """Execute the resolved insight report action.

    Args:
        client: pyclearpass ApiInsight instance.
        action_type: Report operation to perform.
        payload: Configuration payload.
        report_id: Report ID for non-create actions.

    Returns:
        API response dict or error string.
    """
    if action_type == "create":
        return client._send_request("/report", "post", query=payload)
    if not report_id:
        return "report_id is required for this action."
    if action_type == "delete":
        return client.delete_report_by_id(id=report_id)
    if action_type == "enable":
        return client.update_report_by_id_enable(id=report_id)
    if action_type == "disable":
        return client.update_report_by_id_disable(id=report_id)
    if action_type == "run":
        return client.new_report_by_id_run(id=report_id)
    return f"Unhandled action_type: {action_type}"


@mcp.tool(annotations=WRITE_DELETE, tags={"clearpass_write_delete"})
async def clearpass_create_system_event(
    ctx: Context,
    source: Annotated[str, Field(description="Event source (e.g. 'MCP Server', 'Admin').")],
    level: Annotated[str, Field(description="Severity level: 'INFO', 'WARN', or 'ERROR'.")],
    category: Annotated[str, Field(description="Event category (e.g. 'Configuration', 'Authentication').")],
    action: Annotated[str, Field(description="Event action description (e.g. 'Policy Updated').")],
    description: Annotated[str, Field(description="Detailed event description.")],
    confirmed: Annotated[bool, Field(description="Set true after user confirms the operation.")] = False,
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
        confirmed: Set true after user confirms. Skips re-prompting.
    """
    if level not in ("INFO", "WARN", "ERROR"):
        return f"Invalid level '{level}'. Must be 'INFO', 'WARN', or 'ERROR'."

    if not confirmed:
        decline = await _confirm_write(ctx, "create system event", f"{source}/{action}")
        if decline:
            return decline

    try:
        from pyclearpass.api_logs import ApiLogs

        client = await get_clearpass_session(ApiLogs)
        payload = {
            "source": source,
            "level": level,
            "category": category,
            "action": action,
            "description": description,
        }
        return client._send_request("/system-event", "post", query=payload)
    except Exception as e:
        return f"Error creating system event: {e}"
