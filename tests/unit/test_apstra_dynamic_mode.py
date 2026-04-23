"""Integration-style unit tests for the Apstra dynamic-mode pilot (#158 PR B).

Exercises the shared tool-registry + meta-tool machinery against Apstra's real
tool modules. The conftest stub for ``_registry.mcp`` (installed at session
scope in ``tests/conftest.py``) provides a pass-through decorator, so importing
Apstra tool files here populates ``REGISTRIES['apstra']`` with every tool's
``ToolSpec`` — which is exactly what dynamic mode consumes at runtime.
"""

from __future__ import annotations

import importlib

import pytest

from hpe_networking_mcp.platforms._common.tool_registry import REGISTRIES, clear_registry


@pytest.fixture
def apstra_registry_populated():
    """Import every Apstra tool module so ``REGISTRIES['apstra']`` is full.

    Clears the registry at the start so tests that had stubbed entries earlier
    don't pollute the result. Also clears afterwards so the next test starts
    clean.
    """
    clear_registry("apstra")
    # Import order mirrors platforms.apstra.TOOLS keys.
    for mod in (
        "blueprints",
        "blueprint_topology",
        "networks",
        "connectivity",
        "status",
        "manage_blueprints",
        "manage_networks",
        "manage_connectivity",
    ):
        # Reload to force re-registration against the currently-stubbed mcp.
        module = importlib.import_module(f"hpe_networking_mcp.platforms.apstra.tools.{mod}")
        importlib.reload(module)
    yield REGISTRIES["apstra"]
    clear_registry("apstra")


@pytest.mark.unit
class TestApstraRegistryPopulation:
    def test_registry_contains_all_19_tools(self, apstra_registry_populated):
        """Every Apstra tool listed in platforms.apstra.TOOLS registers cleanly."""
        from hpe_networking_mcp.platforms.apstra import TOOLS

        expected = {name for names in TOOLS.values() for name in names}
        actual = set(apstra_registry_populated.keys())
        assert actual == expected, f"Mismatch — missing: {expected - actual}, extra: {actual - expected}"

    def test_no_apstra_health_tool_registered(self, apstra_registry_populated):
        """The per-platform health tool is gone in v2.0 (#158)."""
        assert "apstra_health" not in apstra_registry_populated

    def test_no_apstra_formatting_guidelines_registered(self, apstra_registry_populated):
        """Guidelines content moved to INSTRUCTIONS.md; the tool is gone."""
        assert "apstra_formatting_guidelines" not in apstra_registry_populated

    def test_write_tools_carry_write_tags(self, apstra_registry_populated):
        """Gating relies on the write tags being present on the registered spec."""
        destructive = apstra_registry_populated["apstra_deploy"]
        assert "apstra_write_delete" in destructive.tags

        create = apstra_registry_populated["apstra_create_virtual_network"]
        assert "apstra_write" in create.tags

        read_only = apstra_registry_populated["apstra_get_blueprints"]
        assert not (read_only.tags & {"apstra_write", "apstra_write_delete"})

    def test_categories_match_module_names(self, apstra_registry_populated):
        """Registry category == the source module's short name.

        Matters for ``<platform>_list_tools(category=...)`` filtering — the
        categories users would search for need to be predictable.
        """
        assert apstra_registry_populated["apstra_get_blueprints"].category == "blueprints"
        assert apstra_registry_populated["apstra_deploy"].category == "manage_blueprints"
        assert apstra_registry_populated["apstra_create_virtual_network"].category == "manage_networks"
        assert apstra_registry_populated["apstra_apply_ct_policies"].category == "manage_connectivity"
        assert apstra_registry_populated["apstra_get_anomalies"].category == "status"

    def test_descriptions_are_populated(self, apstra_registry_populated):
        """Every spec has a non-empty description (used by list_tools summary)."""
        for name, spec in apstra_registry_populated.items():
            assert spec.description, f"{name} has empty description"
