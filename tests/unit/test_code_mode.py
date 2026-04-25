"""Unit tests for the ``MCP_TOOL_MODE=code`` tool mode.

Code mode wires FastMCP's ``CodeMode`` transform into the server, replacing
the exposed catalog with a four-tier surface (``tags`` + ``search`` +
``get_schema`` + ``execute``). These tests guard the wiring — config
parsing, per-platform meta-tool skipping, cross-platform aggregator
gating, and registry-level tag plumbing. End-to-end sandbox behavior
lives in ``tests/integration/test_code_mode_end_to_end.py`` so the unit
suite stays offline-friendly.
"""

from __future__ import annotations

from unittest.mock import patch

import pytest

from hpe_networking_mcp.config import ServerConfig


@pytest.mark.unit
class TestCodeModeConfig:
    """Patch ``_load_mist`` to return a fake credential so ``load_config``
    gets past the "no enabled platforms" SystemExit and we can observe the
    ``tool_mode`` field on the resulting ServerConfig.
    """

    @staticmethod
    def _load_with_mode(mode: str) -> ServerConfig:
        from hpe_networking_mcp.config import MistSecrets, load_config

        with (
            patch("os.environ", {"MCP_TOOL_MODE": mode}),
            patch(
                "hpe_networking_mcp.config._load_mist",
                return_value=MistSecrets(api_token="x", host="y"),
            ),
            patch("hpe_networking_mcp.config._load_central", return_value=None),
            patch("hpe_networking_mcp.config._load_greenlake", return_value=None),
            patch("hpe_networking_mcp.config._load_clearpass", return_value=None),
            patch("hpe_networking_mcp.config._load_apstra", return_value=None),
            patch("hpe_networking_mcp.config._load_axis", return_value=None),
        ):
            return load_config()

    def test_code_value_parses(self):
        cfg = self._load_with_mode("code")
        assert cfg.tool_mode == "code"

    def test_unknown_value_falls_back_to_dynamic(self):
        cfg = self._load_with_mode("codee")
        assert cfg.tool_mode == "dynamic"

    def test_static_still_accepted(self):
        cfg = self._load_with_mode("static")
        assert cfg.tool_mode == "static"

    def test_dynamic_still_accepted(self):
        cfg = self._load_with_mode("dynamic")
        assert cfg.tool_mode == "dynamic"

    def test_default_is_dynamic(self):
        # No MCP_TOOL_MODE env var set.
        from hpe_networking_mcp.config import MistSecrets, load_config

        with (
            patch("os.environ", {}),
            patch(
                "hpe_networking_mcp.config._load_mist",
                return_value=MistSecrets(api_token="x", host="y"),
            ),
            patch("hpe_networking_mcp.config._load_central", return_value=None),
            patch("hpe_networking_mcp.config._load_greenlake", return_value=None),
            patch("hpe_networking_mcp.config._load_clearpass", return_value=None),
            patch("hpe_networking_mcp.config._load_apstra", return_value=None),
            patch("hpe_networking_mcp.config._load_axis", return_value=None),
        ):
            cfg = load_config()
        assert cfg.tool_mode == "dynamic"


@pytest.mark.unit
class TestCodeModeCrossPlatformGating:
    """Cross-platform aggregators (``site_health_check`` / ``site_rf_check`` /
    ``manage_wlan_profile``) are NOT registered when ``tool_mode == "code"``.

    We assert the gating path in ``server.create_server`` by patching the
    registration helpers and checking call counts.
    """

    def _run_create_server(self, tool_mode: str):
        from hpe_networking_mcp.config import CentralSecrets, MistSecrets, ServerConfig

        cfg = ServerConfig(
            tool_mode=tool_mode,
            # Both platforms present so the aggregators would otherwise register.
            mist=MistSecrets(api_token="x", host="y"),
            central=CentralSecrets(base_url="https://c", client_id="id", client_secret="s"),
        )

        targets = {
            # Stub every per-platform register so we don't pull real tool modules.
            "mist": "hpe_networking_mcp.server._register_mist_tools",
            "central": "hpe_networking_mcp.server._register_central_tools",
            # Capture the cross-platform-aggregator registration points.
            "health": "hpe_networking_mcp.server._register_site_health_check",
            "rf": "hpe_networking_mcp.server._register_site_rf_check",
            "sync_tools": "hpe_networking_mcp.server._register_sync_tools",
            "sync_prompts": "hpe_networking_mcp.server._register_sync_prompts",
            "code_mode": "hpe_networking_mcp.server._register_code_mode",
        }
        patchers = {key: patch(path) for key, path in targets.items()}
        mocks = {key: p.start() for key, p in patchers.items()}
        try:
            from hpe_networking_mcp.server import create_server

            create_server(cfg)
            return mocks
        finally:
            for p in patchers.values():
                p.stop()

    def test_dynamic_mode_registers_all_aggregators(self):
        mocks = self._run_create_server("dynamic")
        assert mocks["health"].call_count == 1
        assert mocks["rf"].call_count == 1
        assert mocks["sync_tools"].call_count == 1
        assert mocks["sync_prompts"].call_count == 1
        assert mocks["code_mode"].call_count == 0

    def test_static_mode_registers_all_aggregators(self):
        mocks = self._run_create_server("static")
        assert mocks["health"].call_count == 1
        assert mocks["rf"].call_count == 1
        assert mocks["sync_tools"].call_count == 1
        assert mocks["sync_prompts"].call_count == 1
        assert mocks["code_mode"].call_count == 0

    def test_code_mode_skips_every_aggregator_and_invokes_code_mode_hook(self):
        mocks = self._run_create_server("code")
        assert mocks["health"].call_count == 0, "site_health_check must NOT register in code mode"
        assert mocks["rf"].call_count == 0, "site_rf_check must NOT register in code mode"
        assert mocks["sync_tools"].call_count == 0, "manage_wlan_profile must NOT register in code mode"
        assert mocks["sync_prompts"].call_count == 0, "sync prompts must NOT register in code mode"
        assert mocks["code_mode"].call_count == 1, "CodeMode transform hook must be invoked"


@pytest.mark.unit
class TestRegistryPlatformTag:
    """Every tool registered through a platform's ``_registry.py`` shim carries
    the platform name in ``tool.tags`` so ``GetTags`` and ``Search(tags=[...])``
    can scope by platform in code mode.

    We don't import every real platform's tool modules here (that pulls in
    heavy SDK deps). Instead we verify the shim itself by instantiating a
    fake mcp and checking what the decorator passes through.
    """

    def test_mist_shim_adds_platform_tag(self):
        from hpe_networking_mcp.platforms.mist import _registry as mist_registry

        captured: list[dict] = []

        class FakeMCP:
            def tool(self, **kwargs):
                captured.append(kwargs)

                def decorator(fn):
                    return fn

                return decorator

        mist_registry.mcp = FakeMCP()  # type: ignore[assignment]

        @mist_registry.tool(name="t_mist", description="d", tags={"mist_write"})
        async def _fake(ctx):  # pragma: no cover — never actually invoked
            pass

        assert captured, "mist registry shim did not forward to FastMCP"
        tags = captured[0]["tags"]
        assert "mist" in tags, "platform name must be in effective tags"
        assert "mist_write" in tags, "supplied tags must pass through"
        assert "dynamic_managed" in tags, "dynamic_managed must still be present"

    def test_axis_shim_adds_platform_tag(self):
        # Axis has zero real tools today; verify the shim in isolation.
        from hpe_networking_mcp.platforms.axis import _registry as axis_registry

        captured: list[dict] = []

        class FakeMCP:
            def tool(self, **kwargs):
                captured.append(kwargs)

                def decorator(fn):
                    return fn

                return decorator

        axis_registry.mcp = FakeMCP()  # type: ignore[assignment]

        @axis_registry.tool(name="t_axis", description="d")
        async def _fake(ctx):  # pragma: no cover
            pass

        assert "axis" in captured[0]["tags"]


@pytest.mark.unit
class TestCodeModeRegistrationHook:
    """``_register_code_mode(mcp)`` falls back gracefully if pydantic-monty is missing."""

    def test_import_error_falls_back_with_log(self, caplog):
        """Simulate a broken install — the hook should NOT raise."""
        import builtins

        real_import = builtins.__import__

        def fake_import(name, *args, **kwargs):
            if name.startswith("pydantic_monty") or "code_mode" in name:
                raise ImportError(f"simulated missing: {name}")
            return real_import(name, *args, **kwargs)

        with patch.object(builtins, "__import__", side_effect=fake_import):
            from hpe_networking_mcp.server import _register_code_mode

            class FakeMCP:
                def __init__(self):
                    self.transforms: list = []

                def add_transform(self, t):  # pragma: no cover
                    self.transforms.append(t)

            m = FakeMCP()
            # Should not raise — just log and return.
            _register_code_mode(m)
            assert m.transforms == [], "no transform should be added when imports fail"


# NOTE: per-platform register_tools behavior (skipping build_meta_tools in code
# mode) is exercised by the live docker check in the PR, not by a unit test —
# calling real register_tools mutates each platform's ``_registry.mcp`` module
# attribute, leaking state across tests in ways that are disproportionate to
# what the check is worth. The ``TestCodeModeCrossPlatformGating`` class above
# already proves the code-mode branch is reached in create_server.
