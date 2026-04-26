"""Shared dispatch helper for Axis ``axis_manage_*`` tools.

Every Axis entity follows a uniform CRUD shape::

    POST   /<Resource>         -> create
    PUT    /<Resource>/{id}    -> update
    DELETE /<Resource>/{id}    -> delete

Rather than repeat the action-validation, elicitation, and dispatch logic
in every tool file, this helper handles the common path. Each tool file
just calls ``manage_entity(...)`` with its base path and a label.

Writes stage in Axis. To apply, the caller invokes ``axis_commit_changes``;
every successful response from this helper carries a ``next_step`` hint
naming that tool.
"""

from __future__ import annotations

from typing import Any

from fastmcp import Context

from hpe_networking_mcp.middleware.elicitation import confirm_write
from hpe_networking_mcp.platforms.axis.client import format_http_error, get_axis_client

_VALID_ACTIONS = ("create", "update", "delete")
_NEXT_STEP_HINT = "Call axis_commit_changes to apply these staged changes."


async def manage_entity(
    ctx: Context,
    *,
    base_path: str,
    label: str,
    action_type: str,
    payload: dict | None,
    entity_id: str | None,
    confirmed: bool,
) -> dict | str:
    """Generic create/update/delete dispatcher for Axis CRUD entities.

    Args:
        ctx: FastMCP context (needed for elicitation).
        base_path: Resource path under ``/api/v1.0`` — e.g. ``"/Connectors"``.
        label: Human-readable entity name for the elicitation prompt
            (e.g. ``"connector"``, ``"SSL exclusion"``).
        action_type: One of ``"create"``, ``"update"``, ``"delete"``.
        payload: Request body for ``create``/``update``. Ignored for delete.
        entity_id: Resource ID — required for ``update`` and ``delete``.
        confirmed: When true, skip the elicitation prompt.

    Returns:
        Either a dict with the API response plus a ``next_step`` hint, or a
        string error message.
    """
    if action_type not in _VALID_ACTIONS:
        return f"Invalid action_type '{action_type}'. Must be one of: {', '.join(_VALID_ACTIONS)}."
    if action_type in ("update", "delete") and not entity_id:
        return f"entity_id is required for action '{action_type}'."
    if action_type in ("create", "update") and not payload:
        return f"payload is required for action '{action_type}'."

    target = entity_id or "(new)"
    decline = await confirm_write(ctx, f"Axis: {action_type} {label} '{target}'. Confirm?")
    if decline:
        return decline

    try:
        client = await get_axis_client()
        if action_type == "create":
            result = await client.post_json(base_path, payload)
        elif action_type == "update":
            result = await client.put_json(f"{base_path}/{entity_id}", payload)
        else:
            result = await client.delete_resource(f"{base_path}/{entity_id}")
    except Exception as e:
        return f"Error during {action_type} {label}: {format_http_error(e)}"

    response: dict[str, Any] = result if isinstance(result, dict) else {"result": result}
    response["next_step"] = _NEXT_STEP_HINT
    return response
