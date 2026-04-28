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
}


def test_tools_dict_complete():
    from hpe_networking_mcp.platforms.aos8 import TOOLS

    for category, count in EXPECTED_CATEGORY_COUNTS.items():
        assert category in TOOLS, f"missing category: {category}"
        assert len(TOOLS[category]) == count, f"category {category} expected {count}, got {len(TOOLS[category])}"

    flat = {name for names in TOOLS.values() for name in names}
    assert len(flat) == 26
    assert flat == EXPECTED_TOOLS


def test_register_tools_dynamic_mode():
    from fastmcp import FastMCP

    from hpe_networking_mcp.platforms._common.tool_registry import REGISTRIES
    from hpe_networking_mcp.platforms.aos8 import register_tools

    mcp = FastMCP("test-aos8-dynamic", on_duplicate="replace")
    config = MagicMock()
    config.tool_mode = "dynamic"

    count = register_tools(mcp, config)

    assert count == 26
    assert len(REGISTRIES.get("aos8", {})) == 26


def test_register_tools_static_mode():
    from fastmcp import FastMCP

    from hpe_networking_mcp.platforms.aos8 import register_tools

    mcp = FastMCP("test-aos8-static", on_duplicate="replace")
    config = MagicMock()
    config.tool_mode = "static"

    count = register_tools(mcp, config)

    assert count == 26
