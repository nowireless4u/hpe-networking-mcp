"""UXI assignment write tools (POST + DELETE).

Tools in this module create and remove agent-group and sensor-group assignments.
They are gated behind ``ENABLE_UXI_WRITE_TOOLS=true`` and require user
confirmation via ``confirm_write`` elicitation before any HTTP mutation is issued.

Note on remove tools: the DELETE endpoints take the **assignment record ID**
returned by ``uxi_list_*_group_assignments`` items[].id — NOT the agent, sensor,
or group ID. The remove tools document this explicitly to prevent accidental
deletion of the wrong resource.
"""

from __future__ import annotations

from typing import Any

from fastmcp import Context
from fastmcp.exceptions import ToolError

from hpe_networking_mcp.middleware.elicitation import confirm_write
from hpe_networking_mcp.platforms.uxi._registry import tool
from hpe_networking_mcp.platforms.uxi.client import format_http_error, get_uxi_client
from hpe_networking_mcp.platforms.uxi.tools import WRITE, WRITE_DELETE
from hpe_networking_mcp.platforms.uxi.tools._validators import validate_id


@tool(annotations=WRITE, tags={"uxi_write"})
async def uxi_assign_agent_to_group(
    ctx: Context,
    agent_id: str,
    group_id: str,
) -> dict[str, Any] | str:
    """Assign a UXI agent to a group.

    Creates a new agent-group assignment record. Requires
    ``ENABLE_UXI_WRITE_TOOLS=true`` and user confirmation.

    Args:
        agent_id: The agent's UXI resource ID (from ``uxi_list_agents`` items[].id).
        group_id: The group's UXI resource ID (from ``uxi_list_groups`` items[].id).
    """
    validate_id(agent_id, "agent_id")
    validate_id(group_id, "group_id")

    decision = await confirm_write(ctx, f"Assign agent {agent_id!r} to group {group_id!r}?")
    if decision is not None:
        return decision

    body = {"agentId": agent_id, "groupId": group_id}  # API fields are camelCase

    try:
        client = await get_uxi_client()
        result = await client.uxi_post("/agent-group-assignments", body)
        return {"result": result}
    except ToolError:
        raise
    except Exception as e:
        return format_http_error(e)


@tool(annotations=WRITE_DELETE, tags={"uxi_write", "uxi_write_delete"})
async def uxi_remove_agent_from_group(
    ctx: Context,
    assignment_id: str,
) -> dict[str, Any] | str:
    """Remove an agent-group assignment.

    Pass the assignment record 'id' from ``uxi_list_agent_group_assignments``
    items[].id — NOT the agent or group ID. Requires
    ``ENABLE_UXI_WRITE_TOOLS=true`` and user confirmation.

    Args:
        assignment_id: The assignment record's UXI resource ID (from
            ``uxi_list_agent_group_assignments`` items[].id).
    """
    validate_id(assignment_id, "assignment_id")

    decision = await confirm_write(ctx, f"Remove agent-group assignment {assignment_id!r}?")
    if decision is not None:
        return decision

    try:
        client = await get_uxi_client()
        result = await client.uxi_delete(f"/agent-group-assignments/{assignment_id}")
        return {"result": result}
    except ToolError:
        raise
    except Exception as e:
        return format_http_error(e)


@tool(annotations=WRITE, tags={"uxi_write"})
async def uxi_assign_sensor_to_group(
    ctx: Context,
    sensor_id: str,
    group_id: str,
) -> dict[str, Any] | str:
    """Assign a UXI sensor to a group.

    Creates a new sensor-group assignment record. Requires
    ``ENABLE_UXI_WRITE_TOOLS=true`` and user confirmation.

    Args:
        sensor_id: The sensor's UXI resource ID (from ``uxi_list_sensors`` items[].id).
        group_id: The group's UXI resource ID (from ``uxi_list_groups`` items[].id).
    """
    validate_id(sensor_id, "sensor_id")
    validate_id(group_id, "group_id")

    decision = await confirm_write(ctx, f"Assign sensor {sensor_id!r} to group {group_id!r}?")
    if decision is not None:
        return decision

    body = {"sensorId": sensor_id, "groupId": group_id}  # API fields are camelCase

    try:
        client = await get_uxi_client()
        result = await client.uxi_post("/sensor-group-assignments", body)
        return {"result": result}
    except ToolError:
        raise
    except Exception as e:
        return format_http_error(e)


@tool(annotations=WRITE_DELETE, tags={"uxi_write", "uxi_write_delete"})
async def uxi_remove_sensor_from_group(
    ctx: Context,
    assignment_id: str,
) -> dict[str, Any] | str:
    """Remove a sensor-group assignment.

    Pass the assignment record 'id' from ``uxi_list_sensor_group_assignments``
    items[].id — NOT the sensor or group ID. Requires
    ``ENABLE_UXI_WRITE_TOOLS=true`` and user confirmation.

    Args:
        assignment_id: The assignment record's UXI resource ID (from
            ``uxi_list_sensor_group_assignments`` items[].id).
    """
    validate_id(assignment_id, "assignment_id")

    decision = await confirm_write(ctx, f"Remove sensor-group assignment {assignment_id!r}?")
    if decision is not None:
        return decision

    try:
        client = await get_uxi_client()
        result = await client.uxi_delete(f"/sensor-group-assignments/{assignment_id}")
        return {"result": result}
    except ToolError:
        raise
    except Exception as e:
        return format_http_error(e)
