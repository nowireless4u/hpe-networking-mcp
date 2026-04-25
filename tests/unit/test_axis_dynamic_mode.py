"""Unit tests for the Axis Atmos Cloud platform scaffold (Phase 1).

Phase 1 ships the platform skeleton — config loader, lifespan client init,
health probe, registry plumbing — but no underlying tools yet (``TOOLS``
is intentionally empty until subsequent waves). The tests below validate
the scaffold itself: the registry is wired in cleanly, the empty TOOLS
dict round-trips, and the pieces a tool would need (decorator, client
accessor, annotation constants) are importable.

When read tools land in Wave 3, expand ``TestAxisRegistryPopulation`` to
mirror ``test_apstra_dynamic_mode.py``.
"""

from __future__ import annotations

import pytest

from hpe_networking_mcp.platforms._common.tool_registry import REGISTRIES


@pytest.mark.unit
class TestAxisRegistryWiring:
    def test_axis_in_registries_dict(self):
        """The cross-platform registry must contain the axis key.

        ``record_tool`` raises ``ValueError("Unknown platform: axis")`` if
        the platform name isn't a known key — caught this exact bug live
        during scaffold development.
        """
        assert "axis" in REGISTRIES

    def test_axis_starts_empty(self):
        """Phase 1 ships zero tools. Read tools land in a later wave."""
        from hpe_networking_mcp.platforms.axis import TOOLS

        assert TOOLS == {}

    def test_axis_register_tools_returns_zero(self):
        """register_tools should report 0 underlying tools at this stage."""
        from hpe_networking_mcp.platforms.axis import TOOLS

        # Tool count is just len(flatten(TOOLS.values())).
        flat = [n for names in TOOLS.values() for n in names]
        assert len(flat) == 0


@pytest.mark.unit
class TestAxisModuleImports:
    """The scaffold's pieces must import cleanly. Catches typos / missing files."""

    def test_axis_package_importable(self):
        import hpe_networking_mcp.platforms.axis  # noqa: F401

    def test_registry_decorator_exposed(self):
        from hpe_networking_mcp.platforms.axis._registry import tool

        assert callable(tool)

    def test_annotation_constants_exposed(self):
        from hpe_networking_mcp.platforms.axis.tools import READ_ONLY, WRITE, WRITE_DELETE

        assert READ_ONLY.readOnlyHint is True
        assert WRITE.readOnlyHint is False
        assert WRITE_DELETE.destructiveHint is True

    def test_client_module_importable(self):
        # AxisClient + get_axis_client + format_http_error are all needed by
        # future tool modules — make sure the import surface is intact.
        from hpe_networking_mcp.platforms.axis.client import (
            AxisAuthError,
            AxisClient,
            format_http_error,
            get_axis_client,
        )

        assert callable(get_axis_client)
        assert callable(format_http_error)
        assert isinstance(AxisAuthError("x"), RuntimeError)
        # Constructor expects an AxisSecrets — don't call it here, just
        # verify it's a class.
        assert isinstance(AxisClient, type)


@pytest.mark.unit
class TestAxisConfig:
    """The config-side wiring (AxisSecrets, _load_axis, ServerConfig fields)."""

    def test_axis_secrets_dataclass(self):
        from hpe_networking_mcp.config import AxisSecrets

        s = AxisSecrets(api_token="abc")
        assert s.api_token == "abc"

    def test_server_config_has_axis_field(self):
        from hpe_networking_mcp.config import AxisSecrets, ServerConfig

        cfg = ServerConfig(axis=AxisSecrets(api_token="t"))
        assert cfg.axis is not None
        assert "axis" in cfg.enabled_platforms

    def test_server_config_has_write_flag(self):
        from hpe_networking_mcp.config import ServerConfig

        cfg = ServerConfig(enable_axis_write_tools=True)
        assert cfg.enable_axis_write_tools is True

        # Default off — matches every other platform's posture.
        cfg2 = ServerConfig()
        assert cfg2.enable_axis_write_tools is False

    def test_axis_disabled_when_token_missing(self, tmp_path, monkeypatch):
        """``_load_axis`` returns None when the secret file is absent."""
        # Point SECRETS_DIR at an empty tmp dir so no file resolves.
        monkeypatch.setattr("hpe_networking_mcp.config.SECRETS_DIR", str(tmp_path))
        from hpe_networking_mcp.config import _load_axis

        assert _load_axis() is None

    def test_axis_loaded_when_token_present(self, tmp_path, monkeypatch):
        """``_load_axis`` returns AxisSecrets with the token contents."""
        (tmp_path / "axis_api_token").write_text("secret-token-here\n")
        monkeypatch.setattr("hpe_networking_mcp.config.SECRETS_DIR", str(tmp_path))
        from hpe_networking_mcp.config import _load_axis

        secrets = _load_axis()
        assert secrets is not None
        assert secrets.api_token == "secret-token-here"


@pytest.mark.unit
class TestAxisHealthProbe:
    """The cross-platform health.py wiring."""

    def test_axis_in_all_platforms(self):
        from hpe_networking_mcp.platforms.health import _ALL_PLATFORMS

        assert "axis" in _ALL_PLATFORMS

    def test_axis_in_probes_dict(self):
        from hpe_networking_mcp.platforms.health import _PROBES

        assert "axis" in _PROBES
        assert callable(_PROBES["axis"])

    @pytest.mark.asyncio
    async def test_probe_returns_unavailable_when_client_missing(self):
        """If lifespan didn't initialize axis_client, the probe must report 'unavailable'.

        Mirrors the contract every other platform's probe follows.
        """
        from hpe_networking_mcp.platforms.health import _probe_axis

        class _FakeCtx:
            lifespan_context = {}

        result = await _probe_axis(_FakeCtx())
        assert result["status"] == "unavailable"
        assert "Axis is not configured" in result["message"]


@pytest.mark.unit
class TestAxisWriteTagWiring:
    """Visibility transform + is_tool_enabled depend on these dicts."""

    def test_axis_in_write_tag_map(self):
        from hpe_networking_mcp.platforms._common.tool_registry import _WRITE_TAG_BY_PLATFORM

        assert "axis" in _WRITE_TAG_BY_PLATFORM
        # When a tool carries axis_write or axis_write_delete tag, gating fires.
        assert _WRITE_TAG_BY_PLATFORM["axis"] == {"axis_write", "axis_write_delete"}

    def test_axis_in_gate_config_attr(self):
        from hpe_networking_mcp.platforms._common.tool_registry import _GATE_CONFIG_ATTR

        assert _GATE_CONFIG_ATTR.get("axis") == "enable_axis_write_tools"
