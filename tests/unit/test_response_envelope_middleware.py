"""Unit tests for ResponseEnvelopeMiddleware.

v2.5.1.0 prototype scoped wrapping to 4 cross-platform tools via
``PROTOTYPE_TOOLS``. v3.0.0.0 expanded to every tool — the allowlist is
gone. These tests verify the universal-wrapping contract: every tool
gets enveloped, already-enveloped responses pass through idempotently,
and edge cases (None structured content, status-code extraction, platform
inference) all behave correctly.
"""

from __future__ import annotations

import json
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastmcp.tools.tool import ToolResult
from mcp.types import TextContent

from hpe_networking_mcp.middleware.response_envelope import (
    ResponseEnvelopeMiddleware,
    _extract_status,
    _infer_platform,
    _is_envelope_shape,
    _payload_from_content,
)

# ---------------------------------------------------------------------------
# Helpers — mock MiddlewareContext + tool-result builders
# ---------------------------------------------------------------------------


def _make_context(tool_name: str):
    message = MagicMock()
    message.name = tool_name
    context = MagicMock()
    context.message = message
    return context


def _make_tool_result(structured: object | None, content: list | None = None) -> ToolResult:
    """Build a ToolResult with the given structured_content."""
    return ToolResult(
        content=content if content is not None else [],
        structured_content=structured,
    )


# ---------------------------------------------------------------------------
# _infer_platform
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestInferPlatform:
    def test_central_tool(self):
        assert _infer_platform("central_get_sites") == "central"

    def test_mist_tool(self):
        assert _infer_platform("mist_search_device") == "mist"

    def test_aos8_tool(self):
        assert _infer_platform("aos8_get_ap_database") == "aos8"

    def test_clearpass_tool(self):
        assert _infer_platform("clearpass_get_sessions") == "clearpass"

    def test_cross_platform_health(self):
        assert _infer_platform("health") is None

    def test_cross_platform_site_health_check(self):
        assert _infer_platform("site_health_check") is None

    def test_cross_platform_translate_wlan(self):
        assert _infer_platform("translate_wlan_apply") is None


# ---------------------------------------------------------------------------
# _extract_status
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestExtractStatus:
    def test_status_code_key(self):
        assert _extract_status({"status_code": 200, "data": "x"}) == 200

    def test_code_key(self):
        assert _extract_status({"code": 404, "message": "not found"}) == 404

    def test_http_status_key(self):
        assert _extract_status({"http_status": 503}) == 503

    def test_priority_status_code_over_others(self):
        # Should pick status_code first (mirrors retry.py's _extract_status_code)
        assert _extract_status({"status_code": 200, "code": 500}) == 200

    def test_no_status_field(self):
        assert _extract_status({"sites": [], "total": 0}) is None

    def test_non_dict(self):
        assert _extract_status([1, 2, 3]) is None
        assert _extract_status("string") is None
        assert _extract_status(None) is None

    def test_non_int_status(self):
        # Some tools return status as a string; prototype only accepts int
        assert _extract_status({"status_code": "200"}) is None


# ---------------------------------------------------------------------------
# _is_envelope_shape
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestIsEnvelopeShape:
    def test_full_envelope(self):
        assert (
            _is_envelope_shape(
                {
                    "ok": True,
                    "data": {},
                    "status": None,
                    "message": None,
                    "tool": "health",
                    "platform": None,
                }
            )
            is True
        )

    def test_minimal_envelope_keys_only(self):
        # Only ok/data/tool required
        assert _is_envelope_shape({"ok": False, "data": None, "tool": "x"}) is True

    def test_missing_ok(self):
        assert _is_envelope_shape({"data": {}, "tool": "x"}) is False

    def test_missing_data(self):
        assert _is_envelope_shape({"ok": True, "tool": "x"}) is False

    def test_missing_tool(self):
        assert _is_envelope_shape({"ok": True, "data": {}}) is False

    def test_non_dict(self):
        assert _is_envelope_shape([{"ok": True}]) is False
        assert _is_envelope_shape("string") is False
        assert _is_envelope_shape(None) is False


# ---------------------------------------------------------------------------
# ResponseEnvelopeMiddleware
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestResponseEnvelopeMiddleware:
    @pytest.mark.asyncio
    async def test_wraps_health_response(self):
        """The cross-platform `health` tool gets wrapped in the envelope."""
        middleware = ResponseEnvelopeMiddleware()
        ctx = _make_context("health")
        raw_response = {
            "status": "ok",
            "platforms": {"central": {"status": "ok"}, "mist": {"status": "ok"}},
        }
        call_next = AsyncMock(return_value=_make_tool_result(structured=raw_response))

        result = await middleware.on_call_tool(ctx, call_next)

        assert result.structured_content == {
            "ok": True,
            "status": None,  # no HTTP status in raw response
            "data": raw_response,
            "message": None,
            "tool": "health",
            "platform": None,  # cross-platform
        }

    @pytest.mark.asyncio
    async def test_wraps_site_health_check(self):
        middleware = ResponseEnvelopeMiddleware()
        ctx = _make_context("site_health_check")
        raw = {"site_name": "dallas-hq", "verdict": "GO"}
        call_next = AsyncMock(return_value=_make_tool_result(structured=raw))

        result = await middleware.on_call_tool(ctx, call_next)

        assert result.structured_content["data"] == raw
        assert result.structured_content["tool"] == "site_health_check"
        assert result.structured_content["platform"] is None

    @pytest.mark.asyncio
    async def test_wraps_translate_wlan_apply_with_status(self):
        """Status code present in raw response is lifted into the envelope."""
        middleware = ResponseEnvelopeMiddleware()
        ctx = _make_context("translate_wlan_apply")
        raw = {"status_code": 200, "wlan": "Corp"}
        call_next = AsyncMock(return_value=_make_tool_result(structured=raw))

        result = await middleware.on_call_tool(ctx, call_next)

        assert result.structured_content["status"] == 200
        assert result.structured_content["ok"] is True

    @pytest.mark.asyncio
    async def test_wraps_platform_prefixed_tool(self):
        """v3.0.0.0: every tool gets wrapped — including platform-prefixed ones.
        v2.5.1.0 prototype passed these through unchanged; v3 wraps them in
        the envelope with platform field inferred from the prefix.
        """
        middleware = ResponseEnvelopeMiddleware()
        ctx = _make_context("central_get_sites")
        raw = {"sites": [{"name": "dallas-hq"}]}
        original = _make_tool_result(structured=raw)
        call_next = AsyncMock(return_value=original)

        result = await middleware.on_call_tool(ctx, call_next)

        # Wrapped now
        assert result is not original
        assert result.structured_content == {
            "ok": True,
            "status": None,
            "data": raw,
            "message": None,
            "tool": "central_get_sites",
            "platform": "central",
        }

    @pytest.mark.asyncio
    async def test_already_enveloped_passes_through(self):
        """If a tool already returned an envelope, don't re-wrap."""
        middleware = ResponseEnvelopeMiddleware()
        ctx = _make_context("health")
        existing_envelope = {
            "ok": True,
            "data": {"central": {"status": "ok"}},
            "status": None,
            "message": None,
            "tool": "health",
            "platform": None,
        }
        original = _make_tool_result(structured=existing_envelope)
        call_next = AsyncMock(return_value=original)

        result = await middleware.on_call_tool(ctx, call_next)

        # Same object — pass through
        assert result is original
        assert result.structured_content == existing_envelope

    @pytest.mark.asyncio
    async def test_wraps_none_structured_content(self):
        """When structured_content is None (e.g. text-only result), envelope wraps with data=None."""
        middleware = ResponseEnvelopeMiddleware()
        ctx = _make_context("health")
        call_next = AsyncMock(return_value=_make_tool_result(structured=None))

        result = await middleware.on_call_tool(ctx, call_next)

        assert result.structured_content == {
            "ok": True,
            "status": None,
            "data": None,
            "message": None,
            "tool": "health",
            "platform": None,
        }

    @pytest.mark.asyncio
    async def test_wraps_aos8_tool(self):
        """v3.0.0.0: AOS 8 tools (added after the v2.5.1.0 prototype) are
        wrapped just like every other tool. Pin a sample so future regressions
        in the platform-prefix list are caught.
        """
        middleware = ResponseEnvelopeMiddleware()
        ctx = _make_context("aos8_get_md_hierarchy")
        raw = {"Configuration node hierarchy": [{"Config Node": "/md", "Type": "System"}]}
        call_next = AsyncMock(return_value=_make_tool_result(structured=raw))

        result = await middleware.on_call_tool(ctx, call_next)

        envelope = result.structured_content
        assert envelope["tool"] == "aos8_get_md_hierarchy"
        assert envelope["platform"] == "aos8"
        assert envelope["data"] == raw
        assert envelope["ok"] is True


def _text(payload: object) -> list[TextContent]:
    """One JSON TextContent block, the way FastMCP serializes a tool return."""
    return [TextContent(type="text", text=json.dumps(payload))]


@pytest.mark.unit
class TestPayloadFromContent:
    """Issue #327 — `_payload_from_content` recovers a tool's JSON payload
    from its content blocks when `structured_content` is None."""

    def test_recovers_bare_array(self):
        payload = [{"id": "site-1"}, {"id": "site-2"}]
        assert _payload_from_content(_text(payload)) == payload

    def test_recovers_dict(self):
        payload = {"name": "mcp", "privileges": []}
        assert _payload_from_content(_text(payload)) == payload

    def test_non_json_text_preserved_as_string(self):
        """Issue #362 — bare-string returns (e.g. Mermaid source from
        central_get_scope_diagram, error fallback strings from tools
        declared `-> dict | list | str`) MUST survive the envelope wrap
        instead of becoming ``data: null``. Pre-fix this returned None
        and the AI silently lost the entire result."""
        assert _payload_from_content([TextContent(type="text", text="not json")]) == "not json"

    def test_mermaid_string_preserved(self):
        """The actual scope_diagram failure case from operator #362."""
        mermaid = "flowchart TD\n    N1((HQ))\n    N2((BRANCH-1))\n    N1 --> N2"
        assert _payload_from_content([TextContent(type="text", text=mermaid)]) == mermaid

    def test_empty_or_none_content_returns_none(self):
        assert _payload_from_content([]) is None
        assert _payload_from_content(None) is None

    def test_empty_text_block_returns_none(self):
        """Empty-string text blocks shouldn't satisfy the fallback —
        truly empty content still yields None."""
        assert _payload_from_content([TextContent(type="text", text="")]) is None

    def test_first_json_parseable_block_wins(self):
        """JSON blocks take priority over later non-JSON blocks (existing behaviour)."""
        blocks = [
            TextContent(type="text", text="not json"),
            TextContent(type="text", text=json.dumps({"recovered": True})),
        ]
        assert _payload_from_content(blocks) == {"recovered": True}

    def test_first_text_used_when_no_block_parses_as_json(self):
        """When zero blocks parse as JSON, fall back to the FIRST non-empty
        text block — not concatenated, not later blocks. Preserves
        single-block string returns deterministically."""
        blocks = [
            TextContent(type="text", text="first non-json"),
            TextContent(type="text", text="second non-json"),
        ]
        assert _payload_from_content(blocks) == "first non-json"


@pytest.mark.unit
class TestContentFallbackRecovery:
    """Issue #327 — FastMCP leaves `structured_content` None for a tool
    annotated `-> Any` that returns a non-dict (a bare JSON array — the
    shape every `mist_list_*` tool and every `<platform>_invoke_tool`
    dispatch to one produces). The payload survives only in the content
    TextContent block. The middleware must recover it so the envelope's
    `data` carries the real result, not `null`.
    """

    @pytest.mark.asyncio
    async def test_bare_array_recovered_from_content(self):
        middleware = ResponseEnvelopeMiddleware()
        ctx = _make_context("mist_list_org_sites")
        payload = [{"id": "site-1", "name": "HQ"}, {"id": "site-2", "name": "BRANCH-1"}]
        original = _make_tool_result(structured=None, content=_text(payload))
        call_next = AsyncMock(return_value=original)

        result = await middleware.on_call_tool(ctx, call_next)

        assert result.structured_content["data"] == payload
        assert result.structured_content["ok"] is True
        assert result.structured_content["tool"] == "mist_list_org_sites"
        assert result.structured_content["platform"] == "mist"

    @pytest.mark.asyncio
    async def test_meta_tool_dispatch_to_bare_array_recovered(self):
        """`mist_invoke_tool` dispatching to a list-returning underlying tool:
        the meta-tool is `-> Any`, structured_content is None, payload lives
        in content. This is the exact path the operator transcript hit."""
        middleware = ResponseEnvelopeMiddleware()
        ctx = _make_context("mist_invoke_tool")
        payload = [{"mac": "aa:bb:cc:dd:ee:ff", "radio_stat": {"band_5": {}}}]
        original = _make_tool_result(structured=None, content=_text(payload))
        call_next = AsyncMock(return_value=original)

        result = await middleware.on_call_tool(ctx, call_next)

        assert result.structured_content["data"] == payload

    @pytest.mark.asyncio
    async def test_dict_in_content_recovered_when_structured_none(self):
        middleware = ResponseEnvelopeMiddleware()
        ctx = _make_context("mist_get_self")
        payload = {"name": "mcp", "privileges": [{"org_id": "abc"}]}
        original = _make_tool_result(structured=None, content=_text(payload))
        call_next = AsyncMock(return_value=original)

        result = await middleware.on_call_tool(ctx, call_next)

        assert result.structured_content["data"] == payload

    @pytest.mark.asyncio
    async def test_already_enveloped_in_content_passes_through(self):
        """If the recovered payload is itself envelope-shaped, the idempotency
        check still fires — no double-wrap."""
        middleware = ResponseEnvelopeMiddleware()
        ctx = _make_context("mist_invoke_tool")
        envelope = {
            "ok": True,
            "data": [1, 2],
            "status": None,
            "message": None,
            "tool": "x",
            "platform": "mist",
        }
        original = _make_tool_result(structured=None, content=_text(envelope))
        call_next = AsyncMock(return_value=original)

        result = await middleware.on_call_tool(ctx, call_next)

        assert result is original

    @pytest.mark.asyncio
    async def test_non_json_content_preserved_as_string(self):
        """Issue #362 — bare-string returns (e.g. Mermaid source from
        central_get_scope_diagram, error strings from tools declared
        `-> dict | list | str`) MUST land in `data` as the raw string
        rather than `data: null`. Pre-fix the string was silently lost.
        """
        middleware = ResponseEnvelopeMiddleware()
        ctx = _make_context("health")
        original = _make_tool_result(
            structured=None,
            content=[TextContent(type="text", text="plain text, not json")],
        )
        call_next = AsyncMock(return_value=original)

        result = await middleware.on_call_tool(ctx, call_next)

        assert result.structured_content["data"] == "plain text, not json"
        assert result.structured_content["ok"] is True

    @pytest.mark.asyncio
    async def test_invoke_tool_dispatch_to_string_returning_tool_preserves_mermaid(self):
        """The exact path from issue #362: `central_invoke_tool` dispatching
        to `central_get_scope_diagram`. The underlying tool returns the
        Mermaid source as a `str`; FastMCP doesn't populate
        structured_content for `-> Any` meta-tools forwarding a non-dict;
        the envelope must recover the string from content rather than
        emitting `data: null`.
        """
        middleware = ResponseEnvelopeMiddleware()
        ctx = _make_context("central_invoke_tool")
        mermaid = "flowchart TD\n    N1((HQ))\n    N2((BRANCH-1))\n    N1 --> N2"
        original = _make_tool_result(
            structured=None,
            content=[TextContent(type="text", text=mermaid)],
        )
        call_next = AsyncMock(return_value=original)

        result = await middleware.on_call_tool(ctx, call_next)

        assert result.structured_content["data"] == mermaid
        assert result.structured_content["ok"] is True
        assert result.structured_content["tool"] == "central_invoke_tool"
        assert result.structured_content["platform"] == "central"

    @pytest.mark.asyncio
    async def test_structured_content_takes_precedence_over_content(self):
        """When structured_content IS populated, content is not consulted."""
        middleware = ResponseEnvelopeMiddleware()
        ctx = _make_context("central_get_sites")
        structured = {"sites": ["from_structured_content"]}
        original = _make_tool_result(structured=structured, content=_text({"sites": ["from_content_block"]}))
        call_next = AsyncMock(return_value=original)

        result = await middleware.on_call_tool(ctx, call_next)

        assert result.structured_content["data"] == structured


@pytest.mark.unit
class TestDiscoveryToolBypass:
    """v3.0.1.15: discovery tools (`tags`, `search`, `get_schema`,
    `skills_list`, `skills_load`) ship with their own ``x-fastmcp-wrap-result``
    output schemas requiring a top-level ``result`` field. Wrapping them in
    the envelope as ``{"ok": ..., "data": {"result": ...}}`` produces a
    validation error because the outer envelope has no top-level ``result``.
    The middleware must pass these tools through unchanged (closes #293,
    root cause of the "Mist intermittent" report — issue #302).
    """

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "tool_name",
        ["tags", "search", "get_schema", "skills_list", "skills_load"],
    )
    async def test_discovery_tool_response_passes_through_unchanged(self, tool_name: str):
        """Each of the 5 discovery tools' responses must pass through verbatim,
        retaining the ``{"result": ...}`` shape rather than being wrapped.
        """
        middleware = ResponseEnvelopeMiddleware()
        ctx = _make_context(tool_name)
        # FastMCP's auto-wrap convention: discovery tools that return strings
        # get serialized as {"result": "<rendered>"}.
        native = {"result": f"<rendered output from {tool_name}>"}
        original = _make_tool_result(structured=native)
        call_next = AsyncMock(return_value=original)

        result = await middleware.on_call_tool(ctx, call_next)

        # The exact ToolResult must come back — no rewrapping.
        assert result is original
        assert result.structured_content == native
        # Specifically: it must NOT be wrapped in the envelope shape.
        assert "ok" not in result.structured_content
        assert "data" not in result.structured_content
        assert "tool" not in result.structured_content

    @pytest.mark.asyncio
    async def test_non_discovery_tool_still_gets_wrapped(self):
        """Sanity: a tool with a name similar to a discovery tool but not in
        the bypass set (e.g. an `mcp__hpe-networking__search`-prefixed tool
        if one ever existed) still gets wrapped normally.
        """
        middleware = ResponseEnvelopeMiddleware()
        ctx = _make_context("central_search_clients")
        raw = {"clients": [{"mac": "aa:bb:cc:dd:ee:ff"}]}
        call_next = AsyncMock(return_value=_make_tool_result(structured=raw))

        result = await middleware.on_call_tool(ctx, call_next)

        assert result.structured_content["ok"] is True
        assert result.structured_content["data"] == raw
        assert result.structured_content["tool"] == "central_search_clients"
        assert result.structured_content["platform"] == "central"
