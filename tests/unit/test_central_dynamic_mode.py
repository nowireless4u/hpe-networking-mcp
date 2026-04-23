"""Integration-style unit tests for the Central dynamic-mode migration (#160).

Mirrors ``test_apstra_dynamic_mode.py`` and ``test_mist_dynamic_mode.py``:
import every Central tool module against the stubbed mcp (installed in
``tests/conftest.py``) and assert the shared registry ends up populated with
the expected Central specs.
"""

from __future__ import annotations

import importlib

import pytest

from hpe_networking_mcp.platforms._common.tool_registry import REGISTRIES, clear_registry


@pytest.fixture
def central_registry_populated():
    """Import every Central tool module so ``REGISTRIES['central']`` is full."""
    clear_registry("central")
    from hpe_networking_mcp.platforms.central import TOOLS

    for category in TOOLS:
        module = importlib.import_module(f"hpe_networking_mcp.platforms.central.tools.{category}")
        importlib.reload(module)
    yield REGISTRIES["central"]
    clear_registry("central")


@pytest.mark.unit
class TestCentralRegistryPopulation:
    def test_registry_contains_all_tools(self, central_registry_populated):
        """Every Central tool listed in platforms.central.TOOLS registers cleanly."""
        from hpe_networking_mcp.platforms.central import TOOLS

        expected = {name for names in TOOLS.values() for name in names}
        actual = set(central_registry_populated.keys())
        assert actual == expected, f"Mismatch — missing: {expected - actual}, extra: {actual - expected}"

    def test_expected_surface_size(self, central_registry_populated):
        """Sanity: the full Central tool surface is > 60 tools."""
        assert len(central_registry_populated) > 60

    def test_write_tools_carry_write_delete_tag(self, central_registry_populated):
        """The three configuration CRUD tools are the flagship write_delete surface."""
        for name in ("central_manage_site", "central_manage_site_collection", "central_manage_device_group"):
            assert "central_write_delete" in central_registry_populated[name].tags

    def test_read_tool_has_no_write_tag(self, central_registry_populated):
        read = central_registry_populated["central_get_sites"]
        assert "central_write_delete" not in read.tags

    def test_categories_derived_from_module_names(self, central_registry_populated):
        """Registry category == source module's short name."""
        assert central_registry_populated["central_get_sites"].category == "sites"
        assert central_registry_populated["central_get_devices"].category == "devices"
        assert central_registry_populated["central_manage_site"].category == "configuration"
        assert central_registry_populated["central_get_aps"].category == "monitoring"

    def test_descriptions_are_populated(self, central_registry_populated):
        for name, spec in central_registry_populated.items():
            assert spec.description, f"{name} has empty description"
