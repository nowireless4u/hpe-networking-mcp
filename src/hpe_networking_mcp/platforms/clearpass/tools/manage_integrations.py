"""ClearPass integrations write tools."""

from __future__ import annotations

from typing import Annotated

from fastmcp import Context
from fastmcp.exceptions import ToolError
from pydantic import Field

from hpe_networking_mcp.middleware.elicitation import confirm_write
from hpe_networking_mcp.platforms._common.annotations import Capability
from hpe_networking_mcp.platforms.clearpass._registry import tool
from hpe_networking_mcp.platforms.clearpass.client import get_clearpass_client


async def _confirm_write(
    ctx: Context, action_type: str, resource: str, identifier: str | None, confirmed: bool
) -> dict | None:
    """Thin wrapper over :func:`middleware.elicitation.confirm_write`.

    Kept as a local helper so existing call sites don't change; the
    shared elicitation/decline/cancel logic now lives in the middleware
    (#148).
    """
    label = identifier or "unknown"
    return await confirm_write(ctx, f"ClearPass: {action_type} {resource} '{label}'. Confirm?")


@tool(capability=Capability.WRITE_DELETE)
async def clearpass_manage_extension(
    ctx: Context,
    action_type: Annotated[str, Field(description="Action: 'start', 'stop', 'restart', or 'delete'.")],
    extension_id: Annotated[str, Field(description="Extension instance ID.")],
    confirmed: Annotated[bool, Field(description="Set true after user confirms.")] = False,
) -> dict | str:
    """Start, stop, restart, or delete a ClearPass extension instance.

    Args:
        action_type: Operation -- 'start', 'stop', 'restart', or 'delete'.
        extension_id: ID of the extension instance.
        confirmed: Set true after user confirms. Skips re-prompting.
    """
    valid = ("start", "stop", "restart", "delete")
    if action_type not in valid:
        raise ToolError(
            {"status_code": 400, "message": f"Invalid action_type '{action_type}'. Must be one of: {', '.join(valid)}."}
        )
    decline = await _confirm_write(ctx, action_type, "extension", extension_id, confirmed)
    if decline:
        return decline
    try:
        client = await get_clearpass_client()
        if action_type == "start":
            return await client.request("post", f"/extension/instance/{extension_id}/start")
        if action_type == "stop":
            return await client.request("post", f"/extension/instance/{extension_id}/stop")
        if action_type == "restart":
            return await client.request("post", f"/extension/instance/{extension_id}/restart")
        return await client.request("delete", f"/extension/instance/{extension_id}")
    except ToolError:
        raise
    except Exception as e:
        raise ToolError({"status_code": 502, "message": f"Error managing extension: {e}"}) from e


@tool(capability=Capability.WRITE_DELETE)
async def clearpass_manage_syslog_target(
    ctx: Context,
    action_type: Annotated[str, Field(description="Action: 'create', 'update', or 'delete'.")],
    payload: Annotated[dict, Field(description="Syslog target config payload. Empty dict {} for delete.")],
    syslog_target_id: Annotated[str | None, Field(description="Syslog target ID (required for update/delete).")] = None,
    name: Annotated[str | None, Field(description="Target name (alternative to ID).")] = None,
    confirmed: Annotated[bool, Field(description="Set true after user confirms.")] = False,
) -> dict | str:
    """Create, update, or delete a ClearPass syslog target.

    Args:
        action_type: Operation -- 'create', 'update', or 'delete'.
        payload: JSON config body. Required for create/update. Empty dict for delete.
        syslog_target_id: Numeric ID. Required for update/delete (or use name).
        name: Target name. Alternative to syslog_target_id.
        confirmed: Set true after user confirms. Skips re-prompting.
    """
    if action_type not in ("create", "update", "delete"):
        raise ToolError(
            {
                "status_code": 400,
                "message": f"Invalid action_type '{action_type}'. Must be 'create', 'update', or 'delete'.",
            }
        )
    decline = await _confirm_write(ctx, action_type, "syslog target", syslog_target_id or name, confirmed)
    if decline:
        return decline
    try:
        client = await get_clearpass_client()
        if action_type == "create":
            return await client.request("post", "/syslog-target", json_body=payload)
        if not syslog_target_id and not name:
            raise ToolError(
                {"status_code": 400, "message": "Either syslog_target_id or name is required for update/delete."}
            )
        if action_type == "update":
            path = f"/syslog-target/{syslog_target_id}" if syslog_target_id else f"/syslog-target/name/{name}"
            return await client.request("patch", path, json_body=payload)
        if syslog_target_id:
            return await client.request("delete", f"/syslog-target/{syslog_target_id}")
        return await client.request("delete", f"/syslog-target/name/{name}")
    except ToolError:
        raise
    except Exception as e:
        raise ToolError({"status_code": 502, "message": f"Error managing syslog target: {e}"}) from e


@tool(capability=Capability.WRITE_DELETE)
async def clearpass_manage_syslog_export_filter(
    ctx: Context,
    action_type: Annotated[str, Field(description="Action: 'create', 'update', or 'delete'.")],
    payload: Annotated[dict, Field(description="Syslog export filter config payload. Empty dict {} for delete.")],
    syslog_export_filter_id: Annotated[
        str | None, Field(description="Syslog export filter ID (required for update/delete).")
    ] = None,
    name: Annotated[str | None, Field(description="Filter name (alternative to ID).")] = None,
    confirmed: Annotated[bool, Field(description="Set true after user confirms.")] = False,
) -> dict | str:
    """Create, update, or delete a ClearPass syslog export filter.

    Args:
        action_type: Operation -- 'create', 'update', or 'delete'.
        payload: JSON config body. Required for create/update. Empty dict for delete.
        syslog_export_filter_id: Numeric ID. Required for update/delete (or use name).
        name: Filter name. Alternative to syslog_export_filter_id.
        confirmed: Set true after user confirms. Skips re-prompting.
    """
    if action_type not in ("create", "update", "delete"):
        raise ToolError(
            {
                "status_code": 400,
                "message": f"Invalid action_type '{action_type}'. Must be 'create', 'update', or 'delete'.",
            }
        )
    decline = await _confirm_write(ctx, action_type, "syslog export filter", syslog_export_filter_id or name, confirmed)
    if decline:
        return decline
    try:
        client = await get_clearpass_client()
        if action_type == "create":
            return await client.request("post", "/syslog-export-filter", json_body=payload)
        if not syslog_export_filter_id and not name:
            raise ToolError(
                {"status_code": 400, "message": "Either syslog_export_filter_id or name is required for update/delete."}
            )
        if action_type == "update":
            path = (
                f"/syslog-export-filter/{syslog_export_filter_id}"
                if syslog_export_filter_id
                else f"/syslog-export-filter/name/{name}"
            )
            return await client.request("patch", path, json_body=payload)
        if syslog_export_filter_id:
            return await client.request("delete", f"/syslog-export-filter/{syslog_export_filter_id}")
        return await client.request("delete", f"/syslog-export-filter/name/{name}")
    except ToolError:
        raise
    except Exception as e:
        raise ToolError({"status_code": 502, "message": f"Error managing syslog export filter: {e}"}) from e


@tool(capability=Capability.WRITE_DELETE)
async def clearpass_manage_endpoint_context_server(
    ctx: Context,
    action_type: Annotated[str, Field(description="Action: 'create', 'update', 'delete', or 'trigger_poll'.")],
    payload: Annotated[dict, Field(description="Endpoint context server config payload. Empty dict {} for delete.")],
    endpoint_context_server_id: Annotated[
        str | None, Field(description="Server ID (required for update/delete/trigger_poll).")
    ] = None,
    name: Annotated[str | None, Field(description="Server name (alternative to ID for create/update).")] = None,
    confirmed: Annotated[bool, Field(description="Set true after user confirms.")] = False,
) -> dict | str:
    """Create, update, delete, or trigger poll for a ClearPass endpoint context server.

    Args:
        action_type: Operation -- 'create', 'update', 'delete', or 'trigger_poll'.
        payload: JSON config body. Required for create/update. Empty dict for delete/trigger_poll.
        endpoint_context_server_id: Numeric ID. Required for update/delete/trigger_poll.
        name: Server name. Alternative to ID for update.
        confirmed: Set true after user confirms. Skips re-prompting.
    """
    valid = ("create", "update", "delete", "trigger_poll")
    if action_type not in valid:
        raise ToolError(
            {"status_code": 400, "message": f"Invalid action_type '{action_type}'. Must be one of: {', '.join(valid)}."}
        )
    decline = await _confirm_write(
        ctx, action_type, "endpoint context server", endpoint_context_server_id or name, confirmed
    )
    if decline:
        return decline
    try:
        client = await get_clearpass_client()
        if action_type == "create":
            return await client.request("post", "/endpoint-context-server", json_body=payload)
        if not endpoint_context_server_id and not name:
            raise ToolError({"status_code": 400, "message": "Either endpoint_context_server_id or name is required."})
        if action_type == "update":
            path = (
                f"/endpoint-context-server/{endpoint_context_server_id}"
                if endpoint_context_server_id
                else f"/endpoint-context-server/name/{name}"
            )
            return await client.request("patch", path, json_body=payload)
        if not endpoint_context_server_id:
            raise ToolError(
                {"status_code": 400, "message": "endpoint_context_server_id is required for delete/trigger_poll."}
            )
        if action_type == "trigger_poll":
            return await client.request("patch", f"/endpoint-context-server/{endpoint_context_server_id}/trigger-poll")
        return await client.request("delete", f"/endpoint-context-server/{endpoint_context_server_id}")
    except ToolError:
        raise
    except Exception as e:
        raise ToolError({"status_code": 502, "message": f"Error managing endpoint context server: {e}"}) from e
