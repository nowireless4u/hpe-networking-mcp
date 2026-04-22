"""Juniper Apstra platform module."""

import importlib

from fastmcp import FastMCP
from loguru import logger

from hpe_networking_mcp.config import ServerConfig

TOOLS: dict[str, list[str]] = {
    "health": [
        "apstra_health",
        "apstra_formatting_guidelines",
    ],
    "blueprints": [
        "apstra_get_blueprints",
        "apstra_get_templates",
    ],
    "blueprint_topology": [
        "apstra_get_racks",
        "apstra_get_routing_zones",
        "apstra_get_system_info",
    ],
    "networks": [
        "apstra_get_virtual_networks",
        "apstra_get_remote_gateways",
    ],
    "connectivity": [
        "apstra_get_connectivity_templates",
        "apstra_get_application_endpoints",
    ],
    "status": [
        "apstra_get_anomalies",
        "apstra_get_diff_status",
        "apstra_get_protocol_sessions",
    ],
    "manage_blueprints": [
        "apstra_create_datacenter_blueprint",
        "apstra_create_freeform_blueprint",
        "apstra_delete_blueprint",
        "apstra_deploy",
    ],
    "manage_networks": [
        "apstra_create_virtual_network",
        "apstra_create_remote_gateway",
    ],
    "manage_connectivity": [
        "apstra_apply_ct_policies",
    ],
}

WRITE_CATEGORIES = {k for k in TOOLS if k.startswith("manage_")}


def register_tools(mcp: FastMCP, config: ServerConfig) -> int:
    """Dynamically load Apstra tool modules. Returns count of loaded tools."""
    from hpe_networking_mcp.platforms.apstra import _registry

    _registry.mcp = mcp

    write_enabled = config.enable_apstra_write_tools
    loaded: list[str] = []

    for category, tool_names in TOOLS.items():
        if category in WRITE_CATEGORIES and not write_enabled:
            logger.info("Apstra: write tools disabled, skipping {} ({} tools)", category, len(tool_names))
            continue
        try:
            importlib.import_module(f"hpe_networking_mcp.platforms.apstra.tools.{category}")
            loaded.extend(tool_names)
            logger.debug("Apstra: loaded module {}", category)
        except Exception as e:
            logger.warning("Apstra: failed to load module {} -- {}", category, e)

    return len(loaded)
