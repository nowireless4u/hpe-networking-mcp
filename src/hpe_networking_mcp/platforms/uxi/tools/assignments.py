"""UXI group assignment read tools."""

from __future__ import annotations

from typing import Any

from fastmcp import Context
from fastmcp.exceptions import ToolError

from hpe_networking_mcp.platforms._common.annotations import Capability
from hpe_networking_mcp.platforms.uxi._registry import tool
from hpe_networking_mcp.platforms.uxi.client import format_http_error, get_uxi_client


@tool(capability=Capability.READ)
async def uxi_list_agent_group_assignments(
    ctx: Context,
    next_cursor: str | None = None,
    page_size: int = 50,
) -> dict[str, Any] | str:
    """List UXI agent-to-group assignments.

    Returns: {items: [{id, agent: {id}, group: {id}, type}], count: N, next: str|null}.

    Args:
        next_cursor: Cursor from the previous response 'next' field. Omit for first page.
        page_size: Max items per page (default 50, max 100).
    """
    try:
        client = await get_uxi_client()
        return await client.uxi_get("/agent-group-assignments", next_cursor=next_cursor, limit=page_size)
    except ToolError:
        raise
    except Exception as e:
        return format_http_error(e)


@tool(capability=Capability.READ)
async def uxi_list_sensor_group_assignments(
    ctx: Context,
    next_cursor: str | None = None,
    page_size: int = 50,
) -> dict[str, Any] | str:
    """List UXI sensor-to-group assignments.

    Returns: {items: [{id, sensor: {id}, group: {id}, type}], count: N, next: str|null}.

    Args:
        next_cursor: Cursor from the previous response 'next' field. Omit for first page.
        page_size: Max items per page (default 50, max 100).
    """
    try:
        client = await get_uxi_client()
        return await client.uxi_get("/sensor-group-assignments", next_cursor=next_cursor, limit=page_size)
    except ToolError:
        raise
    except Exception as e:
        return format_http_error(e)


@tool(capability=Capability.READ)
async def uxi_list_network_group_assignments(
    ctx: Context,
    next_cursor: str | None = None,
    page_size: int = 50,
) -> dict[str, Any] | str:
    """List UXI network-to-group assignments.

    Returns: {items: [{id, network: {id}, group: {id}, type}], count: N, next: str|null}.

    Args:
        next_cursor: Cursor from the previous response 'next' field. Omit for first page.
        page_size: Max items per page (default 50, max 100).
    """
    try:
        client = await get_uxi_client()
        return await client.uxi_get("/network-group-assignments", next_cursor=next_cursor, limit=page_size)
    except ToolError:
        raise
    except Exception as e:
        return format_http_error(e)


@tool(capability=Capability.READ)
async def uxi_list_service_test_group_assignments(
    ctx: Context,
    next_cursor: str | None = None,
    page_size: int = 50,
) -> dict[str, Any] | str:
    """List UXI service-test-to-group assignments.

    Returns: {items: [{id, serviceTest: {id}, group: {id}, type}], count: N, next: str|null}.

    Args:
        next_cursor: Cursor from the previous response 'next' field. Omit for first page.
        page_size: Max items per page (default 50, max 100).
    """
    try:
        client = await get_uxi_client()
        return await client.uxi_get("/service-test-group-assignments", next_cursor=next_cursor, limit=page_size)
    except ToolError:
        raise
    except Exception as e:
        return format_http_error(e)
