"""UXI sensor write tools (PATCH).

Tools in this module mutate UXI sensor configuration. They are gated behind
``ENABLE_UXI_WRITE_TOOLS=true`` and require user confirmation via
``confirm_write`` elicitation before any HTTP mutation is issued.
"""

from __future__ import annotations

from typing import Any

from fastmcp import Context
from fastmcp.exceptions import ToolError

from hpe_networking_mcp.middleware.elicitation import confirm_write
from hpe_networking_mcp.platforms._common.annotations import Capability
from hpe_networking_mcp.platforms.uxi._registry import tool
from hpe_networking_mcp.platforms.uxi.client import format_http_error, get_uxi_client
from hpe_networking_mcp.platforms.uxi.tools._validators import validate_id

_VALID_PCAP_MODES = {"light", "full", "off"}


@tool(capability=Capability.WRITE)
async def uxi_update_sensor(
    ctx: Context,
    sensor_id: str,
    name: str | None = None,
    notes: str | None = None,
    pcap_mode: str | None = None,
) -> dict[str, Any] | str:
    """Update a UXI sensor's name, notes, or pcap capture mode.

    All fields are optional — only provided fields are sent to the API (sparse PATCH).
    Requires ``ENABLE_UXI_WRITE_TOOLS=true`` and user confirmation.

    Args:
        sensor_id: The sensor's UXI resource ID (from ``uxi_list_sensors`` items[].id).
        name: New sensor name (1–100 characters).
        notes: New notes string.
        pcap_mode: Packet capture mode — one of: ``light``, ``full``, ``off``.
    """
    validate_id(sensor_id, "sensor_id")

    if pcap_mode is not None and pcap_mode not in _VALID_PCAP_MODES:
        raise ToolError(
            {
                "status_code": 400,
                "message": f"Invalid pcap_mode {pcap_mode!r}: must be one of light, full, off",
            }
        )

    body: dict[str, Any] = {}
    if name is not None:
        body["name"] = name
    if notes is not None:
        body["notes"] = notes
    if pcap_mode is not None:
        body["pcapMode"] = pcap_mode  # API field is camelCase

    if not body:
        return {"status": "no_op", "message": "No fields provided — nothing to update."}

    decision = await confirm_write(ctx, f"Update sensor {sensor_id!r} — fields: {', '.join(body.keys())}")
    if decision is not None:
        return decision

    try:
        client = await get_uxi_client()
        result = await client.uxi_patch(f"/sensors/{sensor_id}", body)
        return {"result": result}
    except ToolError:
        raise
    except Exception as e:
        return format_http_error(e)
