"""Aruba UXI platform module.

Wraps the UXI REST API at ``https://api.capenetworks.com/networking-uxi/v1alpha1``
for sensor, agent, group, network, service-test, and assignment management.
Auto-disables when either ``uxi_client_id`` or ``uxi_client_secret`` secret is missing.

Read tools carry no write tag. Write tools (Phase 16) will carry ``uxi_write`` or
``uxi_write_delete`` so the Visibility transform + ElicitationMiddleware gate them on
``ENABLE_UXI_WRITE_TOOLS=true``.
"""

import importlib

from fastmcp import FastMCP
from loguru import logger

from hpe_networking_mcp.config import ServerConfig

# Map of category (tools/<name>.py) -> tool names registered by that module.
TOOLS: dict[str, list[str]] = {
    "sensors": ["uxi_list_sensors", "uxi_get_sensor_status"],
    "agents": ["uxi_list_agents"],
    "groups": ["uxi_list_groups"],
    "networks": ["uxi_list_wired_networks", "uxi_list_wireless_networks"],
    "service_tests": ["uxi_list_service_tests"],
    "assignments": [
        "uxi_list_agent_group_assignments",
        "uxi_list_sensor_group_assignments",
        "uxi_list_network_group_assignments",
        "uxi_list_service_test_group_assignments",
    ],
    "writes.sensors": ["uxi_update_sensor"],
    "writes.agents": ["uxi_update_agent", "uxi_delete_agent"],
    "writes.groups": ["uxi_create_group", "uxi_update_group", "uxi_delete_group"],
    "writes.assignments": [
        "uxi_assign_agent_to_group",
        "uxi_remove_agent_from_group",
        "uxi_assign_sensor_to_group",
        "uxi_remove_sensor_from_group",
    ],
}


def register_tools(mcp: FastMCP, config: ServerConfig) -> int:
    """Load UXI tool modules and register them with FastMCP.

    Returns the count of individual underlying tools that registered.
    """
    from hpe_networking_mcp.platforms._common.meta_tools import build_meta_tools
    from hpe_networking_mcp.platforms.uxi import _registry

    _registry.mcp = mcp

    loaded: list[str] = []
    for category, tool_names in TOOLS.items():
        try:
            importlib.import_module(f"hpe_networking_mcp.platforms.uxi.tools.{category}")
            loaded.extend(tool_names)
            logger.debug("UXI: loaded module {}", category)
        except Exception as e:
            logger.warning("UXI: failed to load module {} -- {}", category, e)

    build_meta_tools("uxi", mcp)
    logger.info(
        "UXI: {} underlying tools + 3 meta-tools registered ({} mode)",
        len(loaded),
        config.tool_mode,
    )

    return len(loaded)
