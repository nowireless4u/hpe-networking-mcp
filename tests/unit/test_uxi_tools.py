"""Unit tests for the Aruba UXI platform tool registry and surface.

Validates registry wiring, read-tool surface, CI disjoint-set assertion (D-11),
and the no-direct-httpx constraint (UXI-DYN-04). Covers UXI-READ-01 through
UXI-READ-07, UXI-DYN-01, UXI-DYN-02, and UXI-DYN-04.
"""

from __future__ import annotations

import importlib
import pathlib

import pytest

from hpe_networking_mcp.platforms._common.tool_registry import REGISTRIES, clear_registry


@pytest.fixture
def uxi_registry_populated():
    """Import every UXI tool module so ``REGISTRIES['uxi']`` is full."""
    clear_registry("uxi")
    from hpe_networking_mcp.platforms.uxi import TOOLS

    for category in TOOLS:
        module = importlib.import_module(f"hpe_networking_mcp.platforms.uxi.tools.{category}")
        importlib.reload(module)
    yield REGISTRIES["uxi"]
    clear_registry("uxi")


@pytest.mark.unit
class TestUXIRegistryPopulation:
    """UXI-READ-01 through UXI-READ-07, UXI-DYN-01: registry wiring and tool surface."""

    def test_uxi_in_registries_dict(self):
        """'uxi' key must exist in REGISTRIES before any tools are loaded."""
        assert "uxi" in REGISTRIES

    def test_registry_contains_all_eleven_read_tools(self, uxi_registry_populated):
        """All 11 UXI read tools must register when tool modules are imported.

        Phase 16 added write tools to the registry; this test scopes its assertion
        to the read-tool set only (write-tool registration is asserted in
        ``test_uxi_write_tools.py::TestUXIWriteRegistry``).
        """
        expected_reads = {
            "uxi_list_sensors",
            "uxi_get_sensor_status",
            "uxi_list_agents",
            "uxi_list_groups",
            "uxi_list_service_tests",
            "uxi_list_wired_networks",
            "uxi_list_wireless_networks",
            "uxi_list_agent_group_assignments",
            "uxi_list_sensor_group_assignments",
            "uxi_list_network_group_assignments",
            "uxi_list_service_test_group_assignments",
        }
        actual = set(uxi_registry_populated.keys())
        missing = expected_reads - actual
        assert not missing, f"missing read tools: {missing}"

    def test_read_tools_carry_no_write_tag(self, uxi_registry_populated):
        """No UXI read tool may carry a write tag (uxi_write or uxi_write_delete).

        Iteration is scoped to tools whose names start with one of the read-tool
        verb prefixes (``uxi_list_*``, ``uxi_get_*``); Phase 16 write tools
        (``uxi_update_*``, ``uxi_create_*``, ``uxi_delete_*``, ``uxi_assign_*``,
        ``uxi_remove_*``) live in the same registry but are intentionally tagged
        ``uxi_write``/``uxi_write_delete`` and are exercised by
        ``test_uxi_write_tools.py``.
        """
        read_prefixes = ("uxi_list_", "uxi_get_")
        for name, spec in uxi_registry_populated.items():
            if not name.startswith(read_prefixes):
                continue
            assert not (spec.tags & {"uxi_write", "uxi_write_delete"}), (
                f"{name} unexpectedly carries a write tag: {spec.tags}"
            )

    def test_every_tool_has_uxi_platform(self, uxi_registry_populated):
        """Every registered tool must have platform='uxi' for code-mode discovery."""
        for name, spec in uxi_registry_populated.items():
            assert spec.platform == "uxi", f"{name} platform={spec.platform!r} — expected 'uxi'"

    def test_every_tool_has_non_empty_description(self, uxi_registry_populated):
        """Every tool must have a non-empty description for the LLM to use."""
        for name, spec in uxi_registry_populated.items():
            assert spec.description, f"{name} has empty description"


@pytest.mark.unit
class TestUXINameCollision:
    """UXI-DYN-02 — D-11 CI assertion: uxi and greenlake tool names must be disjoint."""

    def test_uxi_tool_names_disjoint_from_greenlake(self, uxi_registry_populated):
        """CI assertion D-11: no UXI tool name must collide with a GreenLake tool name."""
        greenlake_names = set(REGISTRIES.get("greenlake", {}).keys())
        uxi_names = set(uxi_registry_populated.keys())
        overlap = uxi_names & greenlake_names
        assert not overlap, f"Tool name collision between uxi and greenlake: {overlap}"


@pytest.mark.unit
class TestNoDirectHttpxInToolFiles:
    """UXI-DYN-04: Tool files must not import httpx directly (use client helpers)."""

    def test_no_httpx_import_in_tool_files(self):
        """None of the 6 UXI tool files may contain 'import httpx' (UXI-DYN-04).

        All HTTP calls must go through UXIClient helpers (uxi_get, uxi_post, etc.)
        so that auth, retry, and error handling are consistent.
        """
        tools_dir = (
            pathlib.Path(__file__).parent.parent.parent / "src" / "hpe_networking_mcp" / "platforms" / "uxi" / "tools"
        )

        tool_files = [f for f in tools_dir.glob("*.py") if f.name != "__init__.py"]
        assert tool_files, f"No tool files found in {tools_dir}"

        violations = []
        for tool_file in tool_files:
            source = tool_file.read_text(encoding="utf-8")
            if "import httpx" in source:
                violations.append(tool_file.name)

        assert not violations, f"Tool files must not import httpx directly (UXI-DYN-04). Violators: {violations}"
