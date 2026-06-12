"""UXI group write tools (POST + PATCH + DELETE).

Tools in this module create, update, and delete UXI group resources. They are
gated behind ``ENABLE_UXI_WRITE_TOOLS=true``; the universal confirmation gate
at ``uxi_invoke_tool`` prompts the user before any HTTP mutation is issued.
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


@tool(capability=Capability.WRITE)
async def uxi_create_group(
    ctx: Context,
    name: str,
    parent_id: str | None = None,
) -> dict[str, Any] | str:
    """Create a new UXI group.

    Requires ``ENABLE_UXI_WRITE_TOOLS=true`` and user confirmation.

    Args:
        name: The group name (required, free-form label assigned by the caller).
        parent_id: Optional parent group ID — if provided, the new group becomes
            a child of that group; otherwise it is created at the root.
    """
    body: dict[str, Any] = {"name": name}
    if parent_id is not None:
        validate_id(parent_id, "parent_id")
        body["parentId"] = parent_id  # API field is camelCase

    try:
        client = await get_uxi_client()
        result = await client.uxi_post("/groups", body)
        return {"result": result}
    except ToolError:
        raise
    except Exception as e:
        return format_http_error(e)


@tool(capability=Capability.WRITE)
async def uxi_update_group(
    ctx: Context,
    group_id: str,
    name: str,
) -> dict[str, Any] | str:
    """Update a UXI group's name.

    ``name`` is the only updatable field per the UXI API. Requires
    ``ENABLE_UXI_WRITE_TOOLS=true`` and user confirmation.

    Args:
        group_id: The group's UXI resource ID (from ``uxi_list_groups`` items[].id).
        name: New group name.
    """
    validate_id(group_id, "group_id")

    try:
        client = await get_uxi_client()
        result = await client.uxi_patch(f"/groups/{path_seg(group_id)}", {"name": name})
        return {"result": result}
    except ToolError:
        raise
    except Exception as e:
        return format_http_error(e)


@tool(capability=Capability.WRITE_DELETE)
async def uxi_delete_group(
    ctx: Context,
    group_id: str,
) -> dict[str, Any] | str:
    """Permanently delete a UXI group.

    This action is irreversible and may orphan child groups. Requires
    ``ENABLE_UXI_WRITE_TOOLS=true`` and user confirmation.

    Args:
        group_id: The group's UXI resource ID (from ``uxi_list_groups`` items[].id).
    """
    validate_id(group_id, "group_id")

    try:
        client = await get_uxi_client()
        result = await client.uxi_delete(f"/groups/{path_seg(group_id)}")
        return {"result": result}
    except ToolError:
        raise
    except Exception as e:
        return format_http_error(e)
