"""Unit tests for the env-gated MCP-Apps provider wiring.

``MCP_APP_ENABLE=true`` is the single switch for every MCP-Apps capability — it
registers BOTH FastMCP's ``GenerativeUI`` provider (``generate_prefab_ui`` +
``search_prefab_components`` + a ``ui://`` streaming-renderer resource) AND the
``FileUpload`` provider (``file_manager`` / ``list_files`` / ``read_file``). All
are off by default; when on, the model-visible tools must survive the code-mode
transform (re-exposed top-level) and ride alongside in dynamic mode.

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
_FILE_UPLOAD_TOOLS = {"file_manager", "list_files", "read_file"}
_APP_TOOLS = _PREFAB_TOOLS | _FILE_UPLOAD_TOOLS


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
    """No env var → NO MCP-Apps tools (prefab OR file-upload) are registered."""
    monkeypatch.delenv("MCP_APP_ENABLE", raising=False)
    names = _tool_names(_build("code"))
    assert not (_APP_TOOLS & names), f"MCP-Apps tools leaked while disabled: {_APP_TOOLS & names}"


def test_enabled_code_mode_reexposes_tools(monkeypatch: pytest.MonkeyPatch) -> None:
    """Flag on + code mode: the single switch brings up BOTH providers' tools past
    the CodeMode transform (re-exposed top-level), and the streaming renderer
    resource is present."""
    monkeypatch.setenv("MCP_APP_ENABLE", "true")
    mcp = _build("code")
    names = _tool_names(mcp)
    assert names >= _PREFAB_TOOLS, f"prefab tools missing top-level in code mode: {_PREFAB_TOOLS - names}"
    assert names >= _FILE_UPLOAD_TOOLS, f"file-upload tools missing in code mode: {_FILE_UPLOAD_TOOLS - names}"
    # The CodeMode base surface (execute + 5 discovery tools) must still be there.
    assert "execute" in names
    labels = _resource_labels(mcp)
    assert any("prefab" in s.lower() or "render" in s.lower() for s in labels), (
        f"streaming renderer resource missing: {labels}"
    )


def test_enabled_dynamic_mode_exposes_tools(monkeypatch: pytest.MonkeyPatch) -> None:
    """Flag on + dynamic mode: both providers' tools ride alongside the others."""
    monkeypatch.setenv("MCP_APP_ENABLE", "true")
    names = _tool_names(_build("dynamic"))
    assert names >= _APP_TOOLS, f"MCP-Apps tools missing in dynamic mode: {_APP_TOOLS - names}"


def test_search_prefab_components_not_enveloped(monkeypatch: pytest.MonkeyPatch) -> None:
    """Regression: the prefab tools declare an ``x-fastmcp-wrap-result`` output schema
    requiring a top-level ``result`` key. The ResponseEnvelopeMiddleware must NOT wrap
    them — wrapping strips ``result`` and the tool's own output validation fails with
    "'result' is a required property" (same class as discovery tools, #293/#302)."""
    monkeypatch.setenv("MCP_APP_ENABLE", "true")
    mcp = _build("code")
    res = asyncio.run(mcp.call_tool("search_prefab_components", {"query": "card"}))  # type: ignore[attr-defined]
    sc = getattr(res, "structured_content", None) or {}
    assert "result" in sc, "wrap-result 'result' key stripped — envelope wrapped a prefab tool"
    assert "ok" not in sc, "prefab tool got enveloped; it must be in _NO_ENVELOPE_TOOLS"


def test_list_files_not_enveloped(monkeypatch: pytest.MonkeyPatch) -> None:
    """Regression (v3.4.6.1): the FileUpload provider's ``list_files`` declares the
    same ``x-fastmcp-wrap-result`` output schema requiring a top-level ``result``
    key. Calling it through the real server stack must succeed — the envelope must
    NOT wrap it, or FastMCP's own output validation raises "'result' is a required
    property" (observed live in an MCP-Apps client when the model called list_files
    to discover an uploaded CSV's name for greenlake_bulk_add_devices).

    This drives the REAL FileUpload tool through the REAL middleware chain (no
    mock) so it actually reproduces the production failure if the bypass regresses.
    """
    monkeypatch.setenv("MCP_APP_ENABLE", "true")
    mcp = _build("code")
    # Empty session store → the provider returns {"result": []}; the point is that
    # the call completes through output validation rather than raising.
    res = asyncio.run(mcp.call_tool("list_files", {}))  # type: ignore[attr-defined]
    sc = getattr(res, "structured_content", None) or {}
    assert "result" in sc, "wrap-result 'result' key stripped — envelope wrapped list_files"
    assert "ok" not in sc, "list_files got enveloped; it must be in _NO_ENVELOPE_TOOLS"


def test_description_augmented_with_dashboard_guidance(monkeypatch: pytest.MonkeyPatch) -> None:
    """The tool description (not INSTRUCTIONS.md) is what steers tool selection, so
    generate_prefab_ui's description must carry the dashboard guidance AND keep the
    upstream Prefab authoring instructions. Applies in both modes."""
    monkeypatch.setenv("MCP_APP_ENABLE", "true")
    for mode in ("code", "dynamic"):
        desc = _tool_descriptions(_build(mode)).get("generate_prefab_ui", "")
        assert "USE THIS TOOL FIRST" in desc, f"dashboard guidance missing in {mode} mode"
        assert "dashboard" in desc.lower()
        # The data->globals contract must be spelled out (prevents the NameError: 'data').
        assert "DATA CONTRACT" in desc, f"data contract guidance missing in {mode} mode"
        # Round-trip-reducing steers: unwrap-the-envelope + one-shot component discovery.
        assert "DATA SHAPE" in desc, f"envelope-unwrap guidance missing in {mode} mode"
        assert "search_prefab_components" in desc, f"component-discovery steer missing in {mode} mode"
        # Upstream Prefab authoring instructions must survive the prepend.
        assert "PrefabApp" in desc, f"upstream Prefab instructions lost in {mode} mode"
