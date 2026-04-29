"""Red tests for AOS8 platform module wiring (TOOLS dict + register_tools).

Fail until plan 03-07 wires the TOOLS dict and register_tools to import
each category module and call ``build_meta_tools`` in dynamic mode.
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

pytestmark = pytest.mark.unit

EXPECTED_TOOLS = {
    "aos8_get_controllers",
    "aos8_get_ap_database",
    "aos8_get_active_aps",
    "aos8_get_ap_detail",
    "aos8_get_bss_table",
    "aos8_get_radio_summary",
    "aos8_get_version",
    "aos8_get_licenses",
    "aos8_get_clients",
    "aos8_find_client",
    "aos8_get_client_detail",
    "aos8_get_client_history",
    "aos8_get_alarms",
    "aos8_get_audit_trail",
    "aos8_get_events",
    "aos8_get_ssid_profiles",
    "aos8_get_virtual_aps",
    "aos8_get_ap_groups",
    "aos8_get_user_roles",
    "aos8_ping",
    "aos8_traceroute",
    "aos8_show_command",
    "aos8_get_logs",
    "aos8_get_controller_stats",
    "aos8_get_arm_history",
    "aos8_get_rf_monitor",
}

EXPECTED_CATEGORY_COUNTS = {
    "health": 8,
    "clients": 4,
    "alerts": 3,
    "wlan": 4,
    "troubleshooting": 7,
    "differentiators": 9,
}

# Phase 5 adds 12 write tools; Phase 7 adds 9 differentiator tools.
# Total is 26 read + 12 write + 9 diff = 47
EXPECTED_WRITE_TOOLS = {
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
}
EXPECTED_DIFF_TOOLS = {
    "aos8_get_md_hierarchy",
    "aos8_get_effective_config",
    "aos8_get_pending_changes",
    "aos8_get_rf_neighbors",
    "aos8_get_cluster_state",
    "aos8_get_air_monitors",
    "aos8_get_ap_wired_ports",
    "aos8_get_ipsec_tunnels",
    "aos8_get_md_health_check",
}
EXPECTED_TOTAL = (
    len(EXPECTED_TOOLS) + len(EXPECTED_WRITE_TOOLS) + len(EXPECTED_DIFF_TOOLS)
)  # 26 + 12 + 9 = 47


def test_tools_dict_complete():
    from hpe_networking_mcp.platforms.aos8 import TOOLS

    for category, count in EXPECTED_CATEGORY_COUNTS.items():
        assert category in TOOLS, f"missing category: {category}"
        assert len(TOOLS[category]) == count, f"category {category} expected {count}, got {len(TOOLS[category])}"

    # Read categories (excluding differentiators which is its own set)
    read_categories = {"health", "clients", "alerts", "wlan", "troubleshooting"}
    read_flat = {name for cat in read_categories for name in TOOLS[cat]}
    assert read_flat == EXPECTED_TOOLS, "Read tool set mismatch"

    # Phase 5: writes category must also be present
    assert "writes" in TOOLS, "TOOLS dict missing 'writes' category"
    assert set(TOOLS["writes"]) == EXPECTED_WRITE_TOOLS, "TOOLS['writes'] mismatch"

    # Phase 7: differentiators category must be present (9 tools)
    assert "differentiators" in TOOLS, "TOOLS dict missing 'differentiators' category"
    assert set(TOOLS["differentiators"]) == EXPECTED_DIFF_TOOLS, "TOOLS['differentiators'] mismatch"


def test_register_tools_dynamic_mode():
    from fastmcp import FastMCP

    from hpe_networking_mcp.platforms._common.tool_registry import REGISTRIES
    from hpe_networking_mcp.platforms.aos8 import register_tools

    mcp = FastMCP("test-aos8-dynamic", on_duplicate="replace")
    config = MagicMock()
    config.tool_mode = "dynamic"

    count = register_tools(mcp, config)

    assert count == EXPECTED_TOTAL
    assert len(REGISTRIES.get("aos8", {})) == EXPECTED_TOTAL


def test_register_tools_static_mode():
    from fastmcp import FastMCP

    from hpe_networking_mcp.platforms.aos8 import register_tools

    mcp = FastMCP("test-aos8-static", on_duplicate="replace")
    config = MagicMock()
    config.tool_mode = "static"

    count = register_tools(mcp, config)

    assert count == EXPECTED_TOTAL
