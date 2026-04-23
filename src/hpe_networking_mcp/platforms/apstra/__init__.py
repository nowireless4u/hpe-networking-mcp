"""Juniper Apstra platform module."""

import importlib

from fastmcp import FastMCP
from loguru import logger

from hpe_networking_mcp.config import ServerConfig

TOOLS: dict[str, list[str]] = {
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


def register_tools(mcp: FastMCP, config: ServerConfig) -> int:
    """Load Apstra tool modules and register them with FastMCP.

    Always imports every category so ``REGISTRIES["apstra"]`` is fully
    populated; runtime write-gating is handled by the Visibility transform
    (static mode) and ``is_tool_enabled`` (dynamic mode, via the meta-tools).

    Returns the count of individual underlying tools that registered.
    """
    from hpe_networking_mcp.platforms._common.meta_tools import build_meta_tools
    from hpe_networking_mcp.platforms.apstra import _registry

    _registry.mcp = mcp

    loaded: list[str] = []
    for category, tool_names in TOOLS.items():
        try:
            importlib.import_module(f"hpe_networking_mcp.platforms.apstra.tools.{category}")
            loaded.extend(tool_names)
            logger.debug("Apstra: loaded module {}", category)
        except Exception as e:
            logger.warning("Apstra: failed to load module {} -- {}", category, e)

    if config.tool_mode == "dynamic":
        # Register the three meta-tools on top of the now-populated registry.
        # Individual tools remain registered with FastMCP but get hidden by
        # the Visibility(dynamic_managed) transform in server.py.
        build_meta_tools("apstra", mcp)
        logger.info(
            "Apstra: {} underlying tools + 3 meta-tools registered (dynamic mode)",
            len(loaded),
        )
    else:
        logger.info("Apstra: {} tools registered (static mode)", len(loaded))

    return len(loaded)
