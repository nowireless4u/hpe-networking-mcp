"""Unit tests for the unknown-tool "did you mean" suggestion layer (#489).

Covers the pure suggestion helper, the error-text parser, and the top-surface
``UnknownToolSuggestMiddleware``. The in-sandbox glue in
``SandboxErrorCatchMiddleware`` reuses the same helper (``MontyError`` is not
directly instantiable, so the helper is the testable seam).
"""

from __future__ import annotations

import json

import pytest
from fastmcp.exceptions import NotFoundError, ToolError

from hpe_networking_mcp.platforms._common import tool_registry
from hpe_networking_mcp.platforms._common.tool_registry import ToolSpec
from hpe_networking_mcp.platforms._common.tool_suggest import (
    suggest_tools,
    unknown_tool_payload_from_text,
)


@pytest.fixture
def fake_registry():
    """Inject a few fake central/mist tools into REGISTRIES; clean up after."""
    reg = tool_registry.REGISTRIES
    added = {
        "central": [
            "central_get_sites",
            "central_get_site_name_id_mapping",
            "central_get_aps",
        ],
        "mist": ["mist_get_self", "mist_list_sites"],
    }

    def _spec(name: str, platform: str) -> ToolSpec:
        return ToolSpec(name=name, func=lambda: None, platform=platform, category="test")

    for plat, names in added.items():
        for n in names:
            reg[plat][n] = _spec(n, plat)
    yield
    for plat, names in added.items():
        for n in names:
            reg[plat].pop(n, None)


@pytest.mark.unit
class TestSuggestTools:
    def test_close_match_scoped_to_platform_prefix(self, fake_registry) -> None:
        out = suggest_tools("central_list_sites")
        assert out["error"] == "unknown_tool"
        assert out["requested"] == "central_list_sites"
        assert "central_get_sites" in out["candidates"]
        # scoped by the `central_` prefix — no cross-platform noise
        assert all(not c.startswith("mist_") for c in out["candidates"])
        assert out["dispatch"] == "central_invoke_tool(name, params)"

    def test_explicit_platform_scopes_unprefixed_name(self, fake_registry) -> None:
        out = suggest_tools("get_site", platform="central")
        assert out["candidates"]
        assert all(c.startswith("central_") for c in out["candidates"])
        assert out["dispatch"] == "central_invoke_tool(name, params)"

    def test_unknown_platform_has_no_dispatch(self, fake_registry) -> None:
        out = suggest_tools("zzz_made_up_thing")
        assert "dispatch" not in out  # no resolvable platform
        assert out["candidates"] == [] or all(isinstance(c, str) for c in out["candidates"])

    def test_substring_fallback_when_below_fuzzy_cutoff(self, fake_registry) -> None:
        # "sites" is a short shared token; ensure it still surfaces matches
        out = suggest_tools("central_sites")
        assert any("sites" in c for c in out["candidates"])


@pytest.mark.unit
class TestUnknownToolPayloadFromText:
    def test_parses_unquoted_in_sandbox_form(self, fake_registry) -> None:
        out = unknown_tool_payload_from_text("Unknown tool: central_list_sites")
        assert out is not None
        assert out["requested"] == "central_list_sites"
        assert "central_get_sites" in out["candidates"]

    def test_parses_quoted_top_surface_form(self, fake_registry) -> None:
        out = unknown_tool_payload_from_text("Unknown tool: 'central_list_sites'")
        assert out is not None
        assert out["requested"] == "central_list_sites"

    def test_returns_none_for_unrelated_error(self) -> None:
        assert unknown_tool_payload_from_text("Some other sandbox error") is None
        assert unknown_tool_payload_from_text("") is None

    def test_returns_none_for_nonactionable_discovery_tool(self, fake_registry) -> None:
        """#208 preserved: a model calling the top-level `search` tool from
        inside execute is not a platform-tool typo — no platform prefix and no
        candidates — so the helper declines (caller keeps its plain text)."""
        assert unknown_tool_payload_from_text("Unknown tool: search") is None


@pytest.mark.unit
class TestUnknownToolSuggestMiddleware:
    async def test_reraises_structured_payload(self, fake_registry) -> None:
        from hpe_networking_mcp.middleware.unknown_tool_suggest import (
            UnknownToolSuggestMiddleware,
        )

        mw = UnknownToolSuggestMiddleware()

        class _Ctx:
            message = type("M", (), {"name": "central_list_sites"})()

        async def call_next(ctx):
            raise NotFoundError("Unknown tool: 'central_list_sites'")

        with pytest.raises(ToolError) as ei:
            await mw.on_call_tool(_Ctx(), call_next)
        payload = json.loads(str(ei.value))
        assert payload["error"] == "unknown_tool"
        assert payload["requested"] == "central_list_sites"
        assert "central_get_sites" in payload["candidates"]
        assert payload["dispatch"] == "central_invoke_tool(name, params)"

    async def test_passthrough_unrelated_error(self) -> None:
        from hpe_networking_mcp.middleware.unknown_tool_suggest import (
            UnknownToolSuggestMiddleware,
        )

        mw = UnknownToolSuggestMiddleware()

        class _Ctx:
            message = type("M", (), {"name": "x"})()

        async def call_next(ctx):
            raise ValueError("totally unrelated")

        with pytest.raises(ValueError):
            await mw.on_call_tool(_Ctx(), call_next)


@pytest.mark.unit
class TestDisabledPlatform:
    """#640: a call to a platform with zero registered tools (disabled — empty or
    absent secrets) must return a clear 'not configured' verdict, NOT a
    ``<plat>_invoke_tool`` dispatch hint that points at a tool that also doesn't
    exist. Affects every platform identically, so this is verified across all of
    them."""

    @pytest.fixture
    def central_on_clearpass_off(self):
        """Central enabled (has tools); ClearPass disabled (no tools)."""
        reg = tool_registry.REGISTRIES
        snap = {p: dict(reg.get(p, {})) for p in ("central", "clearpass")}
        reg["central"] = {
            "central_get_sites": ToolSpec(
                name="central_get_sites", func=lambda: None, platform="central", category="test"
            )
        }
        reg["clearpass"] = {}
        yield
        for p, d in snap.items():
            reg[p] = d

    def test_disabled_platform_returns_not_configured(self, central_on_clearpass_off) -> None:
        out = suggest_tools("clearpass_get_sessions")
        assert out["error"] == "platform_not_configured"
        assert out["platform"] == "clearpass"
        assert out["candidates"] == []
        assert "dispatch" not in out  # no circular pointer to a non-existent tool
        assert "not configured" in out["message"].lower()

    def test_enabled_platform_still_suggests_candidates(self, central_on_clearpass_off) -> None:
        # A configured platform's bad guess still gets candidates + dispatch.
        out = suggest_tools("central_list_sites")
        assert out["error"] == "unknown_tool"
        assert "central_get_sites" in out["candidates"]
        assert out["dispatch"] == "central_invoke_tool(name, params)"

    def test_payload_from_text_surfaces_not_configured(self, central_on_clearpass_off) -> None:
        out = unknown_tool_payload_from_text("Unknown tool: clearpass_invoke_tool")
        assert out is not None
        assert out["error"] == "platform_not_configured"
        assert out["platform"] == "clearpass"

    def test_all_known_platforms_when_empty(self) -> None:
        """Every platform prefix, when it has zero tools, yields not_configured."""
        from hpe_networking_mcp.platforms._common.tool_suggest import _KNOWN_PLATFORMS

        reg = tool_registry.REGISTRIES
        snap = {p: dict(reg.get(p, {})) for p in _KNOWN_PLATFORMS}
        for p in _KNOWN_PLATFORMS:
            reg[p] = {}
        try:
            for p in _KNOWN_PLATFORMS:
                out = suggest_tools(f"{p}_invoke_tool")
                assert out["error"] == "platform_not_configured", p
                assert out["platform"] == p
                assert "dispatch" not in out, p
        finally:
            for p, d in snap.items():
                reg[p] = d
