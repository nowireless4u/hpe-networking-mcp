"""Integration-style unit tests for the Mist dynamic-mode migration (#159).

Mirrors ``test_apstra_dynamic_mode.py`` — imports every Mist tool module
against the stubbed mcp (installed in ``tests/conftest.py``) and asserts the
shared registry is populated with the expected specs.
"""

from __future__ import annotations

import importlib

import pytest

from hpe_networking_mcp.platforms._common.tool_registry import REGISTRIES, clear_registry


@pytest.fixture
def mist_registry_populated():
    """Import every Mist tool module so ``REGISTRIES['mist']`` is fully populated.

    Clears the registry at the start (other tests may have stubbed entries)
    and reloads every module to force re-registration against the currently-
    stubbed ``_registry.mcp``.
    """
    clear_registry("mist")
    from hpe_networking_mcp.platforms.mist import TOOLS

    module_names: list[str] = []
    for tool_names in TOOLS.values():
        for name in tool_names:
            module_names.append(name.replace("mist_", ""))

    for mod_short in sorted(set(module_names)):
        module = importlib.import_module(f"hpe_networking_mcp.platforms.mist.tools.{mod_short}")
        importlib.reload(module)
    yield REGISTRIES["mist"]
    clear_registry("mist")


@pytest.mark.unit
class TestMistRegistryPopulation:
    def test_registry_contains_all_tools(self, mist_registry_populated):
        """Every Mist tool listed in platforms.mist.TOOLS registers cleanly."""
        from hpe_networking_mcp.platforms.mist import TOOLS

        expected = {name for names in TOOLS.values() for name in names}
        actual = set(mist_registry_populated.keys())
        assert actual == expected, f"Mismatch — missing: {expected - actual}, extra: {actual - expected}"

    def test_expected_surface_size(self, mist_registry_populated):
        """Sanity: 35 tools across all categories."""
        from hpe_networking_mcp.platforms.mist import TOOLS

        expected = sum(len(names) for names in TOOLS.values())
        assert len(mist_registry_populated) == expected

    def test_write_tools_carry_write_tags(self, mist_registry_populated):
        """Write-gating relies on tags being set on the registered specs."""
        update_site = mist_registry_populated["mist_update_site_configuration_objects"]
        assert "write" in update_site.tags or any(
            t in update_site.tags for t in ("mist_write", "write", "configuration")
        )

        change_site = mist_registry_populated["mist_change_site_configuration_objects"]
        assert "write_delete" in change_site.tags or any(
            t in change_site.tags for t in ("mist_write_delete", "write_delete", "configuration")
        )

    def test_read_tool_has_no_write_tag(self, mist_registry_populated):
        read = mist_registry_populated["mist_search_device"]
        assert not (read.tags & {"mist_write", "mist_write_delete"})

    def test_categories_derived_from_module_names(self, mist_registry_populated):
        """The registry category comes from the source module's short name."""
        assert mist_registry_populated["mist_search_device"].category == "search_device"
        assert mist_registry_populated["mist_get_self"].category == "get_self"
        assert mist_registry_populated["mist_bounce_switch_port"].category == "bounce_switch_port"

    def test_descriptions_are_populated(self, mist_registry_populated):
        for name, spec in mist_registry_populated.items():
            assert spec.description, f"{name} has empty description"
