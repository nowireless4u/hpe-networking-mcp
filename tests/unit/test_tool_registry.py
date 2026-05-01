"""Unit tests for the shared tool registry (v2.0 Phase 0, #158)."""

from __future__ import annotations

import pytest

from hpe_networking_mcp.config import ServerConfig
from hpe_networking_mcp.platforms._common.tool_registry import (
    REGISTRIES,
    ToolSpec,
    clear_registry,
    is_tool_enabled,
    record_tool,
)


def _fn() -> None:
    """Stub for ``ToolSpec.func``."""


@pytest.fixture(autouse=True)
def _clean_registry():
    """Every test starts with empty registries and leaves them empty."""
    clear_registry()
    yield
    clear_registry()


@pytest.mark.unit
class TestRecordTool:
    def test_records_into_the_right_platform(self):
        spec = ToolSpec(name="apstra_get_blueprints", func=_fn, platform="apstra", category="blueprints")
        record_tool(spec)
        assert REGISTRIES["apstra"]["apstra_get_blueprints"] is spec
        aos8_spec = ToolSpec(name="aos8_get_controllers", func=_fn, platform="aos8", category="devices")
        record_tool(aos8_spec)
        assert REGISTRIES["aos8"]["aos8_get_controllers"] is aos8_spec

    def test_record_does_not_leak_to_other_platforms(self):
        spec = ToolSpec(name="apstra_x", func=_fn, platform="apstra", category="x")
        record_tool(spec)
        assert REGISTRIES["mist"] == {}
        assert REGISTRIES["central"] == {}

    def test_same_name_overwrites(self):
        first = ToolSpec(name="t", func=_fn, platform="apstra", category="a")
        second = ToolSpec(name="t", func=_fn, platform="apstra", category="b")
        record_tool(first)
        record_tool(second)
        assert REGISTRIES["apstra"]["t"] is second

    def test_unknown_platform_raises(self):
        spec = ToolSpec(name="t", func=_fn, platform="acme", category="x")
        with pytest.raises(ValueError, match="Unknown platform"):
            record_tool(spec)


@pytest.mark.unit
class TestClearRegistry:
    def test_clear_all(self):
        record_tool(ToolSpec(name="a", func=_fn, platform="apstra", category="x"))
        record_tool(ToolSpec(name="b", func=_fn, platform="mist", category="x"))
        clear_registry()
        assert REGISTRIES["apstra"] == {}
        assert REGISTRIES["mist"] == {}

    def test_clear_one_platform(self):
        record_tool(ToolSpec(name="a", func=_fn, platform="apstra", category="x"))
        record_tool(ToolSpec(name="b", func=_fn, platform="mist", category="x"))
        clear_registry("apstra")
        assert REGISTRIES["apstra"] == {}
        assert REGISTRIES["mist"] == {"b": REGISTRIES["mist"]["b"]}

    def test_clear_unknown_platform_raises(self):
        with pytest.raises(ValueError, match="Unknown platform"):
            clear_registry("acme")


@pytest.mark.unit
class TestIsToolEnabled:
    def _make_config(self, **overrides) -> ServerConfig:
        return ServerConfig(**overrides)

    def test_read_only_tool_always_enabled(self):
        spec = ToolSpec(name="apstra_get_blueprints", func=_fn, platform="apstra", category="r", tags=set())
        assert is_tool_enabled(spec, self._make_config()) is True

    def test_write_tool_disabled_by_default(self):
        spec = ToolSpec(name="apstra_deploy", func=_fn, platform="apstra", category="w", tags={"apstra_write_delete"})
        assert is_tool_enabled(spec, self._make_config()) is False

    def test_write_tool_enabled_when_flag_set(self):
        spec = ToolSpec(name="apstra_deploy", func=_fn, platform="apstra", category="w", tags={"apstra_write_delete"})
        assert is_tool_enabled(spec, self._make_config(enable_apstra_write_tools=True)) is True

    def test_apstra_write_non_delete_tag_also_respects_gate(self):
        spec = ToolSpec(
            name="apstra_create_virtual_network",
            func=_fn,
            platform="apstra",
            category="w",
            tags={"apstra_write"},
        )
        assert is_tool_enabled(spec, self._make_config()) is False
        assert is_tool_enabled(spec, self._make_config(enable_apstra_write_tools=True)) is True

    def test_central_write_gate(self):
        spec = ToolSpec(
            name="central_manage_site",
            func=_fn,
            platform="central",
            category="w",
            tags={"central_write_delete"},
        )
        assert is_tool_enabled(spec, self._make_config()) is False
        assert is_tool_enabled(spec, self._make_config(enable_central_write_tools=True)) is True

    def test_greenlake_has_no_write_gate(self):
        """GreenLake is read-only today — any tool registered under it is always enabled."""
        spec = ToolSpec(name="greenlake_get_devices", func=_fn, platform="greenlake", category="r", tags=set())
        assert is_tool_enabled(spec, self._make_config()) is True

    def test_unrelated_tag_does_not_gate(self):
        spec = ToolSpec(name="t", func=_fn, platform="apstra", category="c", tags={"random_tag"})
        assert is_tool_enabled(spec, self._make_config()) is True

    def test_aos8_write_gate(self):
        spec = ToolSpec(
            name="aos8_create_wlan",
            func=_fn,
            platform="aos8",
            category="w",
            tags={"aos8_write"},
        )
        assert is_tool_enabled(spec, self._make_config()) is False
        assert is_tool_enabled(spec, self._make_config(enable_aos8_write_tools=True)) is True

    def test_aos8_write_delete_gate(self):
        spec = ToolSpec(
            name="aos8_delete_wlan",
            func=_fn,
            platform="aos8",
            category="w",
            tags={"aos8_write_delete"},
        )
        assert is_tool_enabled(spec, self._make_config()) is False
        assert is_tool_enabled(spec, self._make_config(enable_aos8_write_tools=True)) is True


@pytest.mark.unit
class TestRecordToolAos8:
    def test_records_into_the_right_platform(self):
        clear_registry()
        spec = ToolSpec(name="aos8_get_devices", func=_fn, platform="aos8", category="devices")
        record_tool(spec)
        assert REGISTRIES["aos8"]["aos8_get_devices"] is spec
        clear_registry()
