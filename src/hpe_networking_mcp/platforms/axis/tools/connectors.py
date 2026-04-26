"""Axis connector read tools (``/Connectors``).

Connectors are tunnel-endpoint devices that link the customer network
into Axis Atmos Cloud. Each carries rich telemetry (state, CPU/mem/disk,
hostname, OS, version) — fetch it via ``axis_get_status``.
"""

from __future__ import annotations

from typing import Any

from fastmcp import Context

from hpe_networking_mcp.middleware.elicitation import confirm_write
from hpe_networking_mcp.platforms.axis._registry import tool
from hpe_networking_mcp.platforms.axis.client import format_http_error, get_axis_client
from hpe_networking_mcp.platforms.axis.tools import READ_ONLY, WRITE_DELETE
from hpe_networking_mcp.platforms.axis.tools._manage import manage_entity


@tool(annotations=READ_ONLY)
async def axis_get_connectors(
    ctx: Context,
    connector_id: str | None = None,
    page_number: int = 1,
    page_size: int = 50,
) -> dict[str, Any] | str:
    """Get Axis connectors (tunnel-endpoint devices).

    If ``connector_id`` is provided, returns a single connector record.
    Otherwise returns a paged list. For runtime telemetry on a specific
    connector (state, CPU/mem/disk, version), call ``axis_get_status``
    with ``entity_type="connector"``.

    Args:
        connector_id: GUID for single-item lookup.
        page_number: 1-indexed page number for list calls.
        page_size: Items per page for list calls.
    """
    try:
        client = await get_axis_client()
        if connector_id:
            return await client.get_json(f"/Connectors/{connector_id}")
        return await client.get_paged("/Connectors", page_number=page_number, page_size=page_size)
    except Exception as e:
        return f"Error fetching connectors: {format_http_error(e)}"


@tool(annotations=WRITE_DELETE, tags={"axis_write_delete"})
async def axis_manage_connector(
    ctx: Context,
    action_type: str,
    payload: dict | None = None,
    connector_id: str | None = None,
    confirmed: bool = False,
) -> dict | str:
    """Create, update, or delete an Axis connector.

    Writes stage in Axis. Call ``axis_commit_changes`` to apply.

    Args:
        action_type: One of ``'create'``, ``'update'``, ``'delete'``.
        payload: Body for create/update. Ignored for delete.
        connector_id: GUID — required for update/delete.
        confirmed: Set true after user confirms; skips re-prompting.
    """
    return await manage_entity(
        ctx,
        base_path="/Connectors",
        label="connector",
        action_type=action_type,
        payload=payload,
        entity_id=connector_id,
        confirmed=confirmed,
    )


@tool(annotations=WRITE_DELETE, tags={"axis_write_delete"})
async def axis_regenerate_connector(
    ctx: Context,
    connector_id: str,
    confirmed: bool = False,
) -> dict | str:
    """Issue a fresh installation command for an existing Axis connector.

    Invalidates the prior install command for the same connector — anyone
    holding the old command can no longer use it. The connector record
    itself is preserved (no data loss).

    Returns the new installation command. Does NOT require ``axis_commit_changes``
    (regenerate is an immediate operation, not a staged write).

    Args:
        connector_id: GUID of the connector to regenerate.
        confirmed: Set true after user confirms; skips re-prompting.
    """
    decline = await confirm_write(
        ctx,
        f"Axis: regenerate install command for connector {connector_id}. "
        "This invalidates the prior install command. Confirm?",
    )
    if decline:
        return decline
    try:
        client = await get_axis_client()
        return await client.post_json(f"/Connectors/{connector_id}/regenerate", json_body={})
    except Exception as e:
        return f"Error regenerating connector: {format_http_error(e)}"
