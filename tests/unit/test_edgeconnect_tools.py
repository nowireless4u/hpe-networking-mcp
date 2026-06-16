"""Unit tests for the generated EdgeConnect tool surface + config loader."""

from __future__ import annotations

import inspect

import pytest
from fastmcp import FastMCP

from hpe_networking_mcp import config as config_module
from hpe_networking_mcp.config import ServerConfig
from hpe_networking_mcp.platforms import edgeconnect
from hpe_networking_mcp.platforms._common.tool_registry import REGISTRIES, is_tool_enabled


@pytest.fixture
def registered() -> dict:
    """Ensure the EdgeConnect tools are registered and return the shared registry.

    The ``@tool`` decorators populate ``REGISTRIES["edgeconnect"]`` at module
    import time. We must NOT clear it first — modules are import-cached, so a
    clear + re-``register_tools`` would not re-run the decorators and would leave
    the registry empty.
    """
    mcp = FastMCP("test-edgeconnect")
    edgeconnect.register_tools(mcp, ServerConfig(tool_mode="code"))
    return REGISTRIES["edgeconnect"]


@pytest.mark.unit
class TestGeneratedSurface:
    def test_total_tool_count(self, registered):
        # Every operation in the vendored spec becomes a tool (total generation).
        assert len(registered) == 1216

    def test_capability_breakdown(self, registered):
        caps: dict[str, int] = {}
        for spec in registered.values():
            key = spec.capability.value if spec.capability else "none"
            caps[key] = caps.get(key, 0) + 1
        # 3 side-effecting GETs (logout, idle/clear, idle/increment) are reclassified
        # OPERATIONAL, so they drop out of READ.
        assert caps == {"read": 657, "write": 470, "write_delete": 86, "operational": 3}

    def test_side_effecting_gets_not_read(self, registered):
        logout = registered.get("edgeconnect_get_authentication_logout")
        assert logout is not None and logout.capability.value == "operational"

    def test_all_names_prefixed_and_unique(self, registered):
        names = list(registered)
        assert all(n.startswith("edgeconnect_") for n in names)
        assert len(names) == len(set(names))  # no collisions survived de-duping

    def test_write_tools_carry_gate_tags(self, registered):
        # A mutating tool must carry the write/write_delete enable tag so the
        # Visibility transform can hide it when writes are disabled.
        for spec in registered.values():
            if spec.capability and spec.capability.value in ("write", "write_delete"):
                assert spec.tags & {"edgeconnect_write", "edgeconnect_write_delete"}


@pytest.mark.unit
class TestWriteGating:
    """Regression: EdgeConnect writes must be gated by default through is_tool_enabled
    (the meta-tool / dynamic-mode path), not just the static Visibility transform."""

    def _a_write_tool(self, registered):
        return next(s for s in registered.values() if s.capability and s.capability.value in ("write", "write_delete"))

    def _a_read_tool(self, registered):
        return next(s for s in registered.values() if s.capability and s.capability.value == "read")

    def test_write_tool_disabled_by_default(self, registered):
        cfg = ServerConfig(tool_mode="code")  # enable_edgeconnect_write_tools defaults False
        assert is_tool_enabled(self._a_write_tool(registered), cfg) is False

    def test_write_tool_enabled_when_flag_set(self, registered):
        cfg = ServerConfig(tool_mode="code", enable_edgeconnect_write_tools=True)
        assert is_tool_enabled(self._a_write_tool(registered), cfg) is True

    def test_read_tool_always_enabled(self, registered):
        assert is_tool_enabled(self._a_read_tool(registered), ServerConfig(tool_mode="code")) is True


@pytest.mark.unit
class TestGeneratedBodies:
    """Required request bodies are required (no default); non-object bodies keep their type."""

    def test_required_object_body(self):
        from hpe_networking_mcp.platforms.edgeconnect.tools import est_config

        sig = inspect.signature(est_config.edgeconnect_post_security_est_server)
        body = sig.parameters["body"]
        assert body.default is inspect.Parameter.empty  # required, no default
        assert "dict" in str(body.annotation)

    def test_array_body_type(self):
        from hpe_networking_mcp.platforms.edgeconnect.tools import aggregate_stats

        sig = inspect.signature(aggregate_stats.edgeconnect_post_stats2_aggregate_ports)
        assert "list" in str(sig.parameters["body"].annotation)


@pytest.mark.unit
class TestConfigLoader:
    def test_api_key_only_loads(self, monkeypatch):
        secrets = {"edgeconnect_host": "orch.example.com", "edgeconnect_api_key": "k"}
        monkeypatch.setattr(config_module, "_read_secret", lambda name: secrets.get(name))
        cfg = config_module._load_edgeconnect()
        assert cfg is not None and cfg.api_key == "k" and cfg.user is None

    def test_user_pass_only_loads(self, monkeypatch):
        secrets = {
            "edgeconnect_host": "orch.example.com",
            "edgeconnect_user": "admin",
            "edgeconnect_password": "pw",
            "edgeconnect_login_type": "2",
        }
        monkeypatch.setattr(config_module, "_read_secret", lambda name: secrets.get(name))
        cfg = config_module._load_edgeconnect()
        assert cfg is not None and cfg.user == "admin" and cfg.login_type == 2

    def test_missing_host_disables(self, monkeypatch):
        secrets = {"edgeconnect_api_key": "k"}
        monkeypatch.setattr(config_module, "_read_secret", lambda name: secrets.get(name))
        assert config_module._load_edgeconnect() is None

    def test_no_auth_disables(self, monkeypatch):
        secrets = {"edgeconnect_host": "orch.example.com"}
        monkeypatch.setattr(config_module, "_read_secret", lambda name: secrets.get(name))
        assert config_module._load_edgeconnect() is None
