"""Phase 16 UXI write-tool tests — full Wave 3 implementation.

Covers:
- TestUXIWriteRegistry: 10 write tools registered in REGISTRIES["uxi"]
- TestElicitationWiring: elicitation.py source contains enable_uxi_write_tools (D-03)
- TestIDValidation:    _validate_id raises ToolError for path-traversal IDs (D-07)
- TestToolErrorPropagation: ToolError re-raised from client (CR-02)
- TestWriteToolTags:   uxi_ prefix + uxi_write/uxi_write_delete tag set + no httpx
"""

from __future__ import annotations

import importlib
import inspect
import pathlib
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastmcp.exceptions import ToolError

from hpe_networking_mcp.platforms._common.tool_registry import REGISTRIES, clear_registry

# Canonical set of 10 Phase 16 UXI write tools.
EXPECTED_WRITE_TOOLS: set[str] = {
    "uxi_update_sensor",
    "uxi_update_agent",
    "uxi_delete_agent",
    "uxi_create_group",
    "uxi_update_group",
    "uxi_delete_group",
    "uxi_assign_agent_to_group",
    "uxi_remove_agent_from_group",
    "uxi_assign_sensor_to_group",
    "uxi_remove_sensor_from_group",
}


@pytest.fixture
def uxi_write_registry_populated():
    """Reload every UXI tool module (read + write) so REGISTRIES['uxi'] is full."""
    clear_registry("uxi")
    from hpe_networking_mcp.platforms.uxi import TOOLS

    for category in TOOLS:
        module = importlib.import_module(f"hpe_networking_mcp.platforms.uxi.tools.{category}")
        importlib.reload(module)
    yield REGISTRIES["uxi"]
    clear_registry("uxi")


def _make_uxi_ctx() -> MagicMock:
    """Build a MagicMock Context for calling tool functions directly.

    Confirmation is structural (the universal gate at ``uxi_invoke_tool``
    dispatch), so direct calls proceed straight to the mocked client call.
    """
    return MagicMock()


@pytest.mark.unit
class TestUXIWriteRegistry:
    """All 10 Phase 16 UXI write tools must register in REGISTRIES['uxi']."""

    def test_all_10_write_tools_registered(self, uxi_write_registry_populated):
        actual_names = set(uxi_write_registry_populated.keys())
        missing = EXPECTED_WRITE_TOOLS - actual_names
        assert not missing, f"Missing write tools in registry: {missing}"


@pytest.mark.unit
class TestWriteToolTags:
    """uxi_ prefix, uxi_write/uxi_write_delete tag set, no direct httpx in writes/."""

    def test_all_write_tools_have_uxi_prefix(self, uxi_write_registry_populated):
        """Every tool with a uxi_write* tag must start with 'uxi_' (CI tag assertion)."""
        for name, spec in uxi_write_registry_populated.items():
            if spec.tags & {"uxi_write", "uxi_write_delete"}:
                assert name.startswith("uxi_"), f"{name} carries write tag but lacks uxi_ prefix"

    def test_write_tools_have_correct_tags(self, uxi_write_registry_populated):
        """The set of write-tagged tool names must equal exactly the expected 10."""
        tagged_names = {
            name for name, spec in uxi_write_registry_populated.items() if spec.tags & {"uxi_write", "uxi_write_delete"}
        }
        assert tagged_names == EXPECTED_WRITE_TOOLS, (
            f"missing: {EXPECTED_WRITE_TOOLS - tagged_names}, extra: {tagged_names - EXPECTED_WRITE_TOOLS}"
        )

    def test_no_httpx_import_in_write_tool_files(self):
        """No write-tool file may import httpx directly — must go through UXIClient helpers."""
        writes_dir = (
            pathlib.Path(__file__).parent.parent.parent
            / "src"
            / "hpe_networking_mcp"
            / "platforms"
            / "uxi"
            / "tools"
            / "writes"
        )
        files = [f for f in writes_dir.glob("*.py") if f.name != "__init__.py"]
        assert files, f"No write-tool files found in {writes_dir}"

        violations = []
        for f in files:
            if "import httpx" in f.read_text(encoding="utf-8"):
                violations.append(f.name)
        assert not violations, f"Write-tool files must not import httpx directly. Violators: {violations}"


@pytest.mark.unit
class TestIDValidation:
    """_validate_id must raise ToolError for path-traversal IDs (D-07 / CR-01)."""

    async def test_update_sensor_rejects_path_traversal_id(self):
        """uxi_update_sensor must raise ToolError for sensor_id='../../etc/passwd'."""
        from hpe_networking_mcp.platforms.uxi.tools.writes.sensors import uxi_update_sensor

        ctx = _make_uxi_ctx()
        with pytest.raises(ToolError):
            await uxi_update_sensor(ctx, sensor_id="../../etc/passwd", name="x")

    async def test_delete_agent_rejects_slashes_in_id(self):
        """uxi_delete_agent must raise ToolError for agent_id='id/with/slashes'."""
        from hpe_networking_mcp.platforms.uxi.tools.writes.agents import uxi_delete_agent

        ctx = _make_uxi_ctx()
        with pytest.raises(ToolError):
            await uxi_delete_agent(ctx, agent_id="id/with/slashes")

    async def test_valid_id_passes_validation(self):
        """A valid ID like 'abc-123' must pass validation and proceed to the mocked client call."""
        from hpe_networking_mcp.platforms.uxi.tools.writes import sensors as sensors_mod

        mock_client = MagicMock()
        mock_client.uxi_patch = AsyncMock(return_value={"id": "abc-123", "name": "ok"})

        ctx = _make_uxi_ctx()
        with patch.object(sensors_mod, "get_uxi_client", AsyncMock(return_value=mock_client)):
            result = await sensors_mod.uxi_update_sensor(ctx, sensor_id="abc-123", name="ok")
        assert isinstance(result, dict)
        assert "result" in result


@pytest.mark.unit
class TestToolErrorPropagation:
    """ToolError raised by the client must be re-raised, not converted to a string (CR-02)."""

    async def test_patch_tool_propagates_toolerror(self):
        """uxi_update_sensor must re-raise ToolError raised by client.uxi_patch."""
        from hpe_networking_mcp.platforms.uxi.tools.writes import sensors as sensors_mod

        mock_client = MagicMock()
        mock_client.uxi_patch = AsyncMock(side_effect=ToolError({"status_code": 422, "message": "bad request"}))

        ctx = _make_uxi_ctx()
        with patch.object(sensors_mod, "get_uxi_client", AsyncMock(return_value=mock_client)), pytest.raises(ToolError):
            await sensors_mod.uxi_update_sensor(ctx, sensor_id="abc-123", name="x")

    async def test_delete_tool_propagates_toolerror(self):
        """uxi_delete_agent must re-raise ToolError raised by client.uxi_delete."""
        from hpe_networking_mcp.platforms.uxi.tools.writes import agents as agents_mod

        mock_client = MagicMock()
        mock_client.uxi_delete = AsyncMock(side_effect=ToolError({"status_code": 404, "message": "not found"}))

        ctx = _make_uxi_ctx()
        with patch.object(agents_mod, "get_uxi_client", AsyncMock(return_value=mock_client)), pytest.raises(ToolError):
            await agents_mod.uxi_delete_agent(ctx, agent_id="abc-123")


@pytest.mark.unit
class TestElicitationWiring:
    """elicitation.py source must wire uxi_write into any_write and enable_components (D-03)."""

    def test_elicitation_source_contains_uxi_write_wiring(self):
        """The middleware module source must reference enable_uxi_write_tools and uxi_write_delete."""
        from hpe_networking_mcp.middleware import elicitation

        source = inspect.getsource(elicitation)
        assert "enable_uxi_write_tools" in source, "elicitation.py must reference config.enable_uxi_write_tools"
        assert "uxi_write_delete" in source, "elicitation.py must enable the uxi_write_delete tag set"
