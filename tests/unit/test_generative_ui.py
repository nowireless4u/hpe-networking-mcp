"""Unit tests for the env-gated Generative UI provider wiring.

``MCP_ENABLE_GENERATIVE_UI=true`` registers FastMCP's ``GenerativeUI`` provider,
which exposes ``generate_prefab_ui`` + ``search_prefab_components`` tools and a
``ui://`` streaming-renderer resource. The provider is off by default; when on,
both tools must survive the code-mode transform (re-exposed top-level) and ride
alongside in dynamic mode. Mirrors the FileUpload provider's gating contract.

These tests are intentionally SYNCHRONOUS. ``create_server()`` re-exposes the
app-provider tools in code mode via a one-shot ``asyncio.run(mcp.get_tool(...))``,
which is valid only when no event loop is already running — exactly how the real
entrypoint calls it (before the server starts serving). Building the server from
inside an ``async def`` test would nest event loops, the re-expose would silently
no-op, and the test would assert against a state production never produces. So we
build synchronously and drive the async list_* calls with our own ``asyncio.run``.
"""

from __future__ import annotations

import asyncio

import pytest

from hpe_networking_mcp.config import MistSecrets, ServerConfig
from hpe_networking_mcp.server import create_server

pytestmark = pytest.mark.unit

_PREFAB_TOOLS = {"generate_prefab_ui", "search_prefab_components"}


def _build(tool_mode: str) -> object:
    """Build a real server (Mist-only, no aggregators pulled) in the given mode."""
    cfg = ServerConfig(tool_mode=tool_mode, mist=MistSecrets(api_token="x", host="y"))
    return create_server(cfg)


def _tool_names(mcp: object) -> set[str]:
    return {t.name for t in asyncio.run(mcp.list_tools())}  # type: ignore[attr-defined]


def _tool_descriptions(mcp: object) -> dict[str, str]:
    return {t.name: (t.description or "") for t in asyncio.run(mcp.list_tools())}  # type: ignore[attr-defined]


def _resource_labels(mcp: object) -> list[str]:
    items = asyncio.run(mcp.list_resources())  # type: ignore[attr-defined]
    return [str(getattr(r, "name", getattr(r, "uri", r))) for r in items]


def test_disabled_by_default(monkeypatch: pytest.MonkeyPatch) -> None:
    """No env var → the prefab tools must NOT be registered."""
    monkeypatch.delenv("MCP_ENABLE_GENERATIVE_UI", raising=False)
    names = _tool_names(_build("code"))
    assert not (_PREFAB_TOOLS & names), f"generative-UI tools leaked while disabled: {_PREFAB_TOOLS & names}"


def test_enabled_code_mode_reexposes_tools(monkeypatch: pytest.MonkeyPatch) -> None:
    """Flag on + code mode: both prefab tools survive the CodeMode transform
    (re-exposed top-level) and the streaming renderer resource is present."""
    monkeypatch.setenv("MCP_ENABLE_GENERATIVE_UI", "true")
    mcp = _build("code")
    names = _tool_names(mcp)
    assert names >= _PREFAB_TOOLS, f"prefab tools missing top-level in code mode: {_PREFAB_TOOLS - names}"
    # The CodeMode base surface (execute + 5 discovery tools) must still be there.
    assert "execute" in names
    labels = _resource_labels(mcp)
    assert any("prefab" in s.lower() or "render" in s.lower() for s in labels), (
        f"streaming renderer resource missing: {labels}"
    )


def test_enabled_dynamic_mode_exposes_tools(monkeypatch: pytest.MonkeyPatch) -> None:
    """Flag on + dynamic mode: the prefab tools ride alongside the others."""
    monkeypatch.setenv("MCP_ENABLE_GENERATIVE_UI", "true")
    names = _tool_names(_build("dynamic"))
    assert names >= _PREFAB_TOOLS, f"prefab tools missing in dynamic mode: {_PREFAB_TOOLS - names}"


def test_search_prefab_components_not_enveloped(monkeypatch: pytest.MonkeyPatch) -> None:
    """Regression: the prefab tools declare an ``x-fastmcp-wrap-result`` output schema
    requiring a top-level ``result`` key. The ResponseEnvelopeMiddleware must NOT wrap
    them — wrapping strips ``result`` and the tool's own output validation fails with
    "'result' is a required property" (same class as discovery tools, #293/#302)."""
    monkeypatch.setenv("MCP_ENABLE_GENERATIVE_UI", "true")
    mcp = _build("code")
    res = asyncio.run(mcp.call_tool("search_prefab_components", {"query": "card"}))  # type: ignore[attr-defined]
    sc = getattr(res, "structured_content", None) or {}
    assert "result" in sc, "wrap-result 'result' key stripped — envelope wrapped a prefab tool"
    assert "ok" not in sc, "prefab tool got enveloped; it must be in _NO_ENVELOPE_TOOLS"


def test_description_augmented_with_dashboard_guidance(monkeypatch: pytest.MonkeyPatch) -> None:
    """The tool description (not INSTRUCTIONS.md) is what steers tool selection, so
    generate_prefab_ui's description must carry the dashboard guidance AND keep the
    upstream Prefab authoring instructions. Applies in both modes."""
    monkeypatch.setenv("MCP_ENABLE_GENERATIVE_UI", "true")
    for mode in ("code", "dynamic"):
        desc = _tool_descriptions(_build(mode)).get("generate_prefab_ui", "")
        assert "USE THIS TOOL FIRST" in desc, f"dashboard guidance missing in {mode} mode"
        assert "dashboard" in desc.lower()
        # The data->globals contract must be spelled out (prevents the NameError: 'data').
        assert "DATA CONTRACT" in desc, f"data contract guidance missing in {mode} mode"
        # Upstream Prefab authoring instructions must survive the prepend.
        assert "PrefabApp" in desc, f"upstream Prefab instructions lost in {mode} mode"
