"""Juniper Mist platform module."""

import importlib

from fastmcp import FastMCP
from loguru import logger

from hpe_networking_mcp.config import ServerConfig

# Tool categories and their tool names -- maps to modules in tools/
TOOLS = {
    "clients": ["mist_search_guest_authorization", "mist_search_client"],
    "configuration": [
        "mist_get_configuration_objects",
        "mist_get_configuration_object_schema",
        "mist_search_device_config_history",
        "mist_get_wlans",
    ],
    "constants": ["mist_get_constants"],
    "devices": [
        "mist_search_device",
        "mist_get_ap_details",
        "mist_get_switch_details",
        "mist_get_gateway_details",
        "mist_bounce_switch_port",
    ],
    "events": [
        "mist_search_events",
        "mist_search_audit_logs",
        "mist_search_alarms",
    ],
    "info": [
        "mist_get_next_page",
        "mist_get_org_or_site_info",
        "mist_get_site_health",
    ],
    "marvis": ["mist_troubleshoot"],
    "orgs": ["mist_get_org_licenses"],
    "orgs_nac": ["mist_search_nac_user_macs"],
    "self_account": ["mist_get_self"],
    "sites_insights": ["mist_get_insight_metrics"],
    "sites_rogues": ["mist_list_rogue_devices"],
    "sites_rrm": ["mist_get_site_rrm_info"],
    "sles": [
        "mist_get_site_sle",
        "mist_list_site_sle_info",
        "mist_get_org_sle",
        "mist_get_org_sites_sle",
    ],
    "stats": ["mist_get_stats"],
    "utilities_upgrade": ["mist_list_upgrades"],
    "write": [
        "mist_update_site_configuration_objects",
        "mist_update_org_configuration_objects",
    ],
    "write_delete": [
        "mist_change_site_configuration_objects",
        "mist_change_org_configuration_objects",
    ],
}


def register_tools(mcp: FastMCP, config: ServerConfig) -> int:
    """Load all Mist tool modules and register them with FastMCP.

    Always imports every tool file so ``REGISTRIES["mist"]`` is fully populated;
    runtime write-gating is handled by the Visibility transform (static mode)
    and ``is_tool_enabled`` (dynamic mode, via the meta-tools).

    Returns the count of individual underlying tools that registered.
    """
    from hpe_networking_mcp.platforms._common.meta_tools import build_meta_tools
    from hpe_networking_mcp.platforms.mist import _registry

    _registry.mcp = mcp

    loaded: list[str] = []
    for _category, tool_names in TOOLS.items():
        for tool_name in tool_names:
            if tool_name in loaded:
                continue
            try:
                module_name = tool_name.replace("mist_", "")
                module_path = f"hpe_networking_mcp.platforms.mist.tools.{module_name}"
                importlib.import_module(module_path)
                loaded.append(tool_name)
                logger.debug("Mist: loaded tool {}", tool_name)
            except Exception as e:
                logger.warning("Mist: failed to load tool {} -- {}", tool_name, e)

    # Register prompts (not in TOOLS dict — prompts are a different MCP primitive
    # and aren't part of the dynamic-mode meta-tool surface).
    try:
        from hpe_networking_mcp.platforms.mist.tools import prompts as mist_prompts

        mist_prompts.register(mcp)
        logger.debug("Mist: loaded prompts")
    except Exception as e:
        logger.warning("Mist: failed to load prompts -- {}", e)

    if config.tool_mode == "dynamic":
        build_meta_tools("mist", mcp)
        logger.info(
            "Mist: {} underlying tools + 3 meta-tools registered (dynamic mode)",
            len(loaded),
        )
    else:
        logger.info("Mist: {} tools registered (static mode)", len(loaded))

    return len(loaded)
