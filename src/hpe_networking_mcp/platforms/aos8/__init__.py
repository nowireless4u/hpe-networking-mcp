"""Aruba OS 8 / Mobility Conductor platform module."""

from __future__ import annotations

import importlib

from fastmcp import FastMCP
from loguru import logger

from hpe_networking_mcp.config import ServerConfig
from hpe_networking_mcp.platforms._common.meta_tools import build_meta_tools

TOOLS: dict[str, list[str]] = {
    "health": [
        "aos8_get_controllers",
        "aos8_get_ap_database",
        "aos8_get_active_aps",
        "aos8_get_ap_detail",
        "aos8_get_bss_table",
        "aos8_get_radio_summary",
        "aos8_get_version",
        "aos8_get_licenses",
    ],
    "clients": [
        "aos8_get_clients",
        "aos8_find_client",
        "aos8_get_client_detail",
        "aos8_get_client_history",
    ],
    "alerts": [
        "aos8_get_alarms",
        "aos8_get_audit_trail",
        "aos8_get_events",
    ],
    "wlan": [
        "aos8_get_ssid_profiles",
        "aos8_get_virtual_aps",
        "aos8_get_ap_groups",
        "aos8_get_user_roles",
    ],
    "troubleshooting": [
        "aos8_ping",
        "aos8_traceroute",
        "aos8_show_command",
        "aos8_get_logs",
        "aos8_get_controller_stats",
        "aos8_get_arm_history",
        "aos8_get_rf_monitor",
    ],
    "differentiators": [
        "aos8_get_md_hierarchy",
        "aos8_get_effective_config",
        "aos8_get_pending_changes",
        "aos8_get_rf_neighbors",
        "aos8_get_cluster_state",
        "aos8_get_air_monitors",
        "aos8_get_ap_wired_ports",
        "aos8_get_ipsec_tunnels",
        "aos8_get_md_health_check",
    ],
    "writes": [
        "aos8_manage_ssid_profile",
        "aos8_manage_virtual_ap",
        "aos8_manage_ap_group",
        "aos8_manage_user_role",
        "aos8_manage_vlan",
        "aos8_manage_aaa_server",
        "aos8_manage_aaa_server_group",
        "aos8_manage_acl",
        "aos8_manage_netdestination",
        "aos8_disconnect_client",
        "aos8_reboot_ap",
        "aos8_write_memory",
    ],
}

__all__ = ["TOOLS", "register_tools"]


def register_tools(mcp: FastMCP, config: ServerConfig) -> int:
    """Register all AOS8 read tools and (in dynamic mode) the meta-tools.

    Args:
        mcp: The FastMCP server instance.
        config: Server configuration containing tool_mode.

    Returns:
        The number of underlying tools registered. Equal to the sum of
            ``len(names)`` for every entry in ``TOOLS`` (read tools plus, when
            their phases have been wired, the Phase 4 ``differentiators`` set
            and the Phase 5 ``writes`` set).
    """
    from hpe_networking_mcp.platforms.aos8 import _registry

    _registry.mcp = mcp

    total = 0
    for category, names in TOOLS.items():
        importlib.import_module(f"hpe_networking_mcp.platforms.aos8.tools.{category}")
        total += len(names)

    try:
        from hpe_networking_mcp.platforms.aos8.tools import prompts

        prompts.register(mcp)
        logger.debug("AOS8: loaded prompts")
    except Exception as e:
        logger.warning("AOS8: failed to load prompts -- {}", e)

    if config.tool_mode == "dynamic":
        build_meta_tools("aos8", mcp)
        logger.info("AOS8: registered {} underlying tools + 3 meta-tools (dynamic mode)", total)
    else:
        logger.info("AOS8: registered {} underlying tools (code mode)", total)
    return total
