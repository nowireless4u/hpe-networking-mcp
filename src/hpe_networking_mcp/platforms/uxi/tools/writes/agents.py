"""UXI agent write tools (PATCH + DELETE).

Tools in this module mutate or remove UXI agent resources. They are gated
behind ``ENABLE_UXI_WRITE_TOOLS=true``; the universal confirmation gate at
``uxi_invoke_tool`` prompts the user before any HTTP mutation is issued.
"""

from __future__ import annotations

from typing import Any

from fastmcp import Context
from fastmcp.exceptions import ToolError

from hpe_networking_mcp.platforms._common.annotations import Capability
from hpe_networking_mcp.platforms._common.url import path_seg
from hpe_networking_mcp.platforms.uxi._registry import tool
from hpe_networking_mcp.platforms.uxi.client import format_http_error, get_uxi_client
from hpe_networking_mcp.platforms.uxi.tools._validators import validate_id

_VALID_PCAP_MODES = {"light", "full", "off"}


@tool(capability=Capability.WRITE)
async def uxi_update_agent(
    ctx: Context,
    agent_id: str,
    name: str | None = None,
    notes: str | None = None,
    pcap_mode: str | None = None,
) -> dict[str, Any] | str:
    """Update a UXI agent's name, notes, or pcap capture mode.

    All fields are optional — only provided fields are sent to the API (sparse PATCH).
    Requires ``ENABLE_UXI_WRITE_TOOLS=true`` and user confirmation.

    Args:
        agent_id: The agent's UXI resource ID (from ``uxi_list_agents`` items[].id).
        name: New agent name (1–100 characters).
        notes: New notes string.
        pcap_mode: Packet capture mode — one of: ``light``, ``full``, ``off``.
    """
    validate_id(agent_id, "agent_id")

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

    try:
        client = await get_uxi_client()
        result = await client.uxi_patch(f"/agents/{path_seg(agent_id)}", body)
        return {"result": result}
    except ToolError:
        raise
    except Exception as e:
        return format_http_error(e)


@tool(capability=Capability.WRITE_DELETE)
async def uxi_delete_agent(
    ctx: Context,
    agent_id: str,
) -> dict[str, Any] | str:
    """Permanently delete a UXI agent. This action is irreversible.

    Requires ``ENABLE_UXI_WRITE_TOOLS=true`` and user confirmation.

    Args:
        agent_id: The agent's UXI resource ID (from ``uxi_list_agents`` items[].id).
    """
    validate_id(agent_id, "agent_id")

    try:
        client = await get_uxi_client()
        result = await client.uxi_delete(f"/agents/{path_seg(agent_id)}")
        return {"result": result}
    except ToolError:
        raise
    except Exception as e:
        return format_http_error(e)
