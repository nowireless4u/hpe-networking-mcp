"""Integration-style unit tests for the ClearPass dynamic-mode migration (#161).

Mirrors the Apstra / Mist / Central tests. Imports every ClearPass tool module
against the stubbed mcp (installed in ``tests/conftest.py``) and asserts the
shared registry ends up populated with the expected specs.
"""

from __future__ import annotations

import importlib

import pytest

from hpe_networking_mcp.platforms._common.tool_registry import REGISTRIES, clear_registry


@pytest.fixture
def clearpass_registry_populated():
    """Import every ClearPass tool module so ``REGISTRIES['clearpass']`` is full."""
    clear_registry("clearpass")
    from hpe_networking_mcp.platforms.clearpass import TOOLS

    for category in TOOLS:
        module = importlib.import_module(f"hpe_networking_mcp.platforms.clearpass.tools.{category}")
        importlib.reload(module)
    yield REGISTRIES["clearpass"]
    clear_registry("clearpass")


@pytest.mark.unit
class TestClearPassRegistryPopulation:
    def test_registry_contains_all_tools(self, clearpass_registry_populated):
        """Every ClearPass tool listed in platforms.clearpass.TOOLS registers cleanly."""
        from hpe_networking_mcp.platforms.clearpass import TOOLS

        expected = {name for names in TOOLS.values() for name in names}
        actual = set(clearpass_registry_populated.keys())
        assert actual == expected, f"Mismatch — missing: {expected - actual}, extra: {actual - expected}"

    def test_expected_surface_size(self, clearpass_registry_populated):
        """ClearPass is the largest single platform (>= 125 tools)."""
        assert len(clearpass_registry_populated) >= 125

    def test_write_tools_carry_write_delete_tag(self, clearpass_registry_populated):
        """Spot-check: key destructive tools carry the gating tag."""
        for name in (
            "clearpass_manage_role",
            "clearpass_disconnect_session",
            "clearpass_perform_coa",
            "clearpass_manage_endpoint",
        ):
            assert "clearpass_write_delete" in clearpass_registry_populated[name].tags

    def test_read_tool_has_no_write_tag(self, clearpass_registry_populated):
        read = clearpass_registry_populated["clearpass_get_sessions"]
        assert "clearpass_write_delete" not in read.tags

    def test_categories_derived_from_module_names(self, clearpass_registry_populated):
        assert clearpass_registry_populated["clearpass_get_sessions"].category == "sessions"
        assert clearpass_registry_populated["clearpass_manage_role"].category == "manage_roles"
        assert clearpass_registry_populated["clearpass_get_endpoints"].category == "endpoints"
        assert clearpass_registry_populated["clearpass_generate_random_password"].category == "utilities"

    def test_clearpass_test_connection_removed_in_v2(self, clearpass_registry_populated):
        """The v1.x clearpass_test_connection tool was removed in v2.0.

        Platform reachability now goes through the cross-platform
        ``health(platform="clearpass")`` tool — see MIGRATING_TO_V2.md.
        """
        assert "clearpass_test_connection" not in clearpass_registry_populated

    def test_descriptions_are_populated(self, clearpass_registry_populated):
        for name, spec in clearpass_registry_populated.items():
            assert spec.description, f"{name} has empty description"
