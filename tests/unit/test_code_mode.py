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

    def test_unknown_value_falls_back_to_code(self):
        # Default fell back to "dynamic" pre-v3.0.0.0; now falls back to "code".
        cfg = self._load_with_mode("codee")
        assert cfg.tool_mode == "code"

    def test_static_raises_value_error(self):
        # MCP_TOOL_MODE=static was REMOVED in v3.0.0.0 — at 367 tools / ~64K
        # tokens it was no longer practical. Setting it now raises with a
        # migration message pointing at dynamic / code.
        import pytest

        with pytest.raises(ValueError, match="REMOVED in v3.0.0.0"):
            self._load_with_mode("static")

    def test_dynamic_still_accepted(self):
        cfg = self._load_with_mode("dynamic")
        assert cfg.tool_mode == "dynamic"

    def test_default_is_code(self):
        # No MCP_TOOL_MODE env var set. Default flipped from "dynamic" → "code"
        # in v3.0.0.0; the server logs a migration message at startup when this
        # happens.
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
        assert cfg.tool_mode == "code"


@pytest.mark.unit
class TestCodeModeCrossPlatformGating:
    """Cross-platform aggregators (``site_health_check`` / ``site_rf_check``) are
    NOT registered when ``tool_mode == "code"``.

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
            "code_mode": "hpe_networking_mcp.server._register_code_mode",
            # Skills registration — patched at source because server.py
            # imports skills.register lazily inside create_server.
            "skills_register": "hpe_networking_mcp.skills.register",
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
        assert mocks["code_mode"].call_count == 0
        assert mocks["skills_register"].call_count == 1, (
            "skills.register must be called in dynamic mode (skills via @mcp.tool)"
        )

    def test_code_mode_skips_every_aggregator_and_invokes_code_mode_hook(self):
        mocks = self._run_create_server("code")
        assert mocks["health"].call_count == 0, "site_health_check must NOT register in code mode"
        assert mocks["rf"].call_count == 0, "site_rf_check must NOT register in code mode"
        assert mocks["code_mode"].call_count == 1, "CodeMode transform hook must be invoked"
        assert mocks["skills_register"].call_count == 0, (
            "skills.register must NOT be called in code mode — skills are wired "
            "through CodeMode.discovery_tools via SkillsListDiscoveryTool / "
            "SkillsLoadDiscoveryTool factories instead. The @mcp.tool path "
            "would otherwise be hidden by CodeMode.transform_tools and skills "
            "would never appear at the top level (the v2.3.0.0 → v2.3.0.2 bug "
            "we shipped before realizing it). See _register_code_mode."
        )


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


@pytest.mark.unit
class TestCodeModeErrorReturns:
    """Error-contract coverage — REVISED for the v3.2.1.0 sweep.

    The original issue #202 rule ("tools must RETURN error strings, never
    raise") was reversed: `SandboxErrorCatchMiddleware` (post-#333) now
    catches `ToolError` inside the code-mode sandbox and re-raises with
    readable text, so the sandbox no longer dies. The preferred pattern is
    to `raise ToolError({"status_code": ..., "message": ...})`. These tests
    assert the migrated GreenLake surface raises structured ToolErrors.

    See CHANGELOG.md [3.2.0.1] / [3.2.1.0] and docs/TOOLS.md "Tool error
    contract" for the full writeup.
    """

    def test_greenlake_request_raises_structured_toolerror_on_4xx(self):
        """GreenLake is now spec-generated: every tool routes through
        ``greenlake_request``, whose ``_raise_for_status`` converts a non-2xx
        response into a structured ``ToolError`` (the codified contract). The
        former hand-curated per-tool validation tests were removed with those
        modules; this pins the contract at the transport layer instead.
        """
        import httpx
        from fastmcp.exceptions import ToolError

        from hpe_networking_mcp.platforms.greenlake.client import _raise_for_status

        resp = httpx.Response(404, json={"message": "not found"})
        with pytest.raises(ToolError) as exc_info:
            _raise_for_status("GET", "/devices/v1/devices/x", resp)
        assert exc_info.value.args[0]["status_code"] == 404

    def test_greenlake_raise_for_status_treats_3xx_as_error(self):
        """3xx is NOT success — httpx doesn't follow redirects, so a regional/proxy
        redirect must surface as a structured ToolError, not a fake 2xx body."""
        import httpx
        from fastmcp.exceptions import ToolError

        from hpe_networking_mcp.platforms.greenlake.client import _raise_for_status

        resp = httpx.Response(302, headers={"location": "https://elsewhere/x"})
        with pytest.raises(ToolError) as exc_info:
            _raise_for_status("GET", "/devices/v1/devices", resp)
        assert exc_info.value.args[0]["status_code"] == 302

    def test_normalize_location_relative_and_same_origin(self):
        """Relative → leading slash; absolute same-origin → path?query only."""
        from hpe_networking_mcp.platforms.greenlake.client import _normalize_location

        base = "https://global.api.greenlake.hpe.com"
        assert _normalize_location(base, "async-operations/v1/abc") == "/async-operations/v1/abc"
        assert _normalize_location(base, "/async-operations/v1/abc") == "/async-operations/v1/abc"
        assert (
            _normalize_location(base, f"{base}/async-operations/v1/abc?wait=true")
            == "/async-operations/v1/abc?wait=true"
        )

    def test_normalize_location_rejects_cross_origin(self):
        """An absolute Location to a different host must raise, not concatenate."""
        from fastmcp.exceptions import ToolError

        from hpe_networking_mcp.platforms.greenlake.client import _normalize_location

        base = "https://global.api.greenlake.hpe.com"
        with pytest.raises(ToolError) as exc_info:
            _normalize_location(base, "https://other-host.example.com/async-operations/v1/abc")
        assert exc_info.value.args[0]["status_code"] == 502

    # NOTE (v3.2.1.0): the old ``test_no_raise_in_greenlake_tool_files`` AST
    # guard was removed — it enforced the obsolete no-raise rule. GreenLake
    # tools now raise ToolError per the codified contract. An inverse guard
    # (assert tools DO raise ToolError) is deferred until 2-3 more platforms
    # migrate so it has enough surface area to be worth maintaining.
