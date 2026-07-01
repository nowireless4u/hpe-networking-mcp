"""Registry tests for the spec-generated GreenLake platform.

GreenLake is now spec-driven (like Mist/EdgeConnect): tool modules are generated
from ``vendor/greenlake/`` and auto-discovered by ``pkgutil`` (no ``TOOLS`` dict).
These tests import every module against the stubbed mcp (``tests/conftest.py``)
and assert the shared registry is populated with the generated + hand-written
(``bulk_add``) tools, and that write/delete tools are correctly tagged for gating.
"""

from __future__ import annotations

import importlib
import pkgutil

import pytest

from hpe_networking_mcp.platforms._common.tool_registry import REGISTRIES, clear_registry


@pytest.fixture
def greenlake_registry_populated():
    """Import every GreenLake tool module so ``REGISTRIES['greenlake']`` is full."""
    clear_registry("greenlake")
    import hpe_networking_mcp.platforms.greenlake.tools as tools_pkg

    for _finder, modname, _ispkg in pkgutil.iter_modules(tools_pkg.__path__):
        if modname.startswith("_"):
            continue
        # reload so the @tool decorators re-run and repopulate the just-cleared
        # registry even when the module was already imported earlier this session.
        importlib.reload(importlib.import_module(f"{tools_pkg.__name__}.{modname}"))
    yield REGISTRIES["greenlake"]
    clear_registry("greenlake")


@pytest.mark.unit
class TestGreenLakeRegistryPopulation:
    def test_registry_is_large_and_generated(self, greenlake_registry_populated):
        """The generated surface is substantial (hundreds of tools)."""
        assert len(greenlake_registry_populated) > 800

    def test_known_generated_reads_present(self, greenlake_registry_populated):
        """A few representative generated read tools register under their path-slug names."""
        reg = greenlake_registry_populated
        for name in (
            "greenlake_get_devices_v1_devices",
            "greenlake_get_subscriptions_v1_subscriptions",
            "greenlake_get_workspaces_v1_workspaces_workspace_id",
        ):
            assert name in reg, f"expected generated tool {name} missing"

    def test_hand_written_bulk_add_still_present(self, greenlake_registry_populated):
        """The hand-written orchestration tool survives alongside generated modules."""
        assert "greenlake_bulk_add_devices" in greenlake_registry_populated

    def test_write_and_delete_tools_are_tagged_for_gating(self, greenlake_registry_populated):
        """Generated POST/PUT/PATCH carry greenlake_write; DELETE carries greenlake_write_delete."""
        reg = greenlake_registry_populated
        writes = {n for n, s in reg.items() if "greenlake_write" in s.tags}
        deletes = {n for n, s in reg.items() if "greenlake_write_delete" in s.tags}
        assert len(writes) > 300, "expected many write-tagged tools"
        assert len(deletes) > 50, "expected many delete-tagged tools"
        # A concrete delete is gated
        assert any(n.startswith("greenlake_delete_") for n in deletes)

    def test_descriptions_are_populated(self, greenlake_registry_populated):
        for name, spec in greenlake_registry_populated.items():
            assert spec.description, f"{name} has empty description"

    def test_old_endpoint_dispatch_tool_names_not_in_registry(self, greenlake_registry_populated):
        """The v0.9.x REST-endpoint-dispatch meta-tools must not appear."""
        for legacy in ("greenlake_list_endpoints", "greenlake_get_endpoint_schema", "greenlake_invoke_endpoint"):
            assert legacy not in greenlake_registry_populated
