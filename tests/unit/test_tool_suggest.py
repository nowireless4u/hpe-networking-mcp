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
