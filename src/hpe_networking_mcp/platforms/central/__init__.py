"""Aruba Central platform module."""

import importlib

from fastmcp import FastMCP
from loguru import logger

from hpe_networking_mcp.config import ServerConfig

# Tool categories mapped to module names and their tool names
TOOLS = {
    "sites": ["central_get_sites", "central_get_site_health", "central_get_site_name_id_mapping"],
    "devices": ["central_get_devices", "central_find_device"],
    "clients": ["central_get_clients", "central_find_client"],
    "alerts": ["central_get_alerts"],
    "events": ["central_get_events", "central_get_events_count"],
    "monitoring": [
        "central_get_aps",
        "central_get_ap_wlans",
        "central_get_ap_details",
        "central_get_switch_details",
        "central_get_gateway_details",
    ],
    "wlans": ["central_get_wlans", "central_get_wlan_stats"],
    "audit_logs": ["central_get_audit_logs", "central_get_audit_log_detail"],
    "stats": [
        "central_get_ap_stats",
        "central_get_ap_utilization",
        "central_get_gateway_stats",
        "central_get_gateway_utilization",
        "central_get_gateway_wan_availability",
        "central_get_tunnel_health",
    ],
    "switch_poe": ["central_get_switch_hardware_trends", "central_get_switch_poe"],
    "applications": ["central_get_applications"],
    "troubleshooting": [
        "central_ping",
        "central_traceroute",
        "central_cable_test",
        "central_show_commands",
    ],
    "actions": [
        "central_disconnect_users_ssid",
        "central_disconnect_users_ap",
        "central_disconnect_client_ap",
        "central_disconnect_client_gateway",
        "central_disconnect_clients_gateway",
        "central_port_bounce_switch",
        "central_poe_bounce_switch",
        "central_port_bounce_gateway",
        "central_poe_bounce_gateway",
    ],
    "scope": [
        "central_get_scope_tree",
        "central_get_scope_resources",
        "central_get_effective_config",
        "central_get_devices_in_scope",
        "central_get_scope_diagram",
    ],
    "aliases": ["central_get_aliases"],
    "server_groups": ["central_get_server_groups"],
    "named_vlans": ["central_get_named_vlans"],
    "wlan_profiles": [
        "central_get_wlan_profiles",
        "central_manage_wlan_profile",
    ],
    "roles": [
        "central_get_roles",
        "central_manage_role",
    ],
    "config_assignments": [
        "central_get_config_assignments",
        "central_manage_config_assignment",
    ],
    "configuration": [
        "central_manage_site",
        "central_manage_site_collection",
        "central_manage_device_group",
    ],
}


def register_tools(mcp: FastMCP, config: ServerConfig) -> int:
    """Dynamically load and register all Central tool modules. Returns count of loaded tools."""
    from hpe_networking_mcp.platforms.central import _registry

    _registry.mcp = mcp

    write_enabled = config.enable_central_write_tools
    loaded: list[str] = []

    for category, tool_names in TOOLS.items():
        if category == "configuration" and not write_enabled:
            logger.info("Central: write tools disabled, skipping {} tools", len(tool_names))
            continue
        try:
            importlib.import_module(f"hpe_networking_mcp.platforms.central.tools.{category}")
            loaded.extend(tool_names)
            logger.debug("Central: loaded module {}", category)
        except Exception as e:
            logger.warning("Central: failed to load module {} -- {}", category, e)

    # Register prompts (these use register(mcp) pattern, not _registry)
    try:
        from hpe_networking_mcp.platforms.central.tools import prompts

        prompts.register(mcp)
        logger.debug("Central: loaded prompts")
    except Exception as e:
        logger.warning("Central: failed to load prompts -- {}", e)

    return len(loaded)
