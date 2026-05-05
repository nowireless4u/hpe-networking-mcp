"""Unit tests for ResponseEnvelopeMiddleware (v2.5.1.0 prototype, issue #246).

Verifies the envelope-wrapping middleware against the four tool-name
scopes defined in ``PROTOTYPE_TOOLS``. Non-prototype tools pass through
unchanged. Already-enveloped responses pass through idempotently.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest
from fastmcp.tools.tool import ToolResult

from hpe_networking_mcp.middleware.response_envelope import (
    PROTOTYPE_TOOLS,
    ResponseEnvelopeMiddleware,
    _extract_status,
    _infer_platform,
    _is_envelope_shape,
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

    def test_cross_platform_manage_wlan_profile(self):
        assert _infer_platform("manage_wlan_profile") is None


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
    async def test_wraps_manage_wlan_profile_with_status(self):
        """Status code present in raw response is lifted into the envelope."""
        middleware = ResponseEnvelopeMiddleware()
        ctx = _make_context("manage_wlan_profile")
        raw = {"status_code": 200, "wlan": "Corp"}
        call_next = AsyncMock(return_value=_make_tool_result(structured=raw))

        result = await middleware.on_call_tool(ctx, call_next)

        assert result.structured_content["status"] == 200
        assert result.structured_content["ok"] is True

    @pytest.mark.asyncio
    async def test_passes_through_non_prototype_tool(self):
        """Tools NOT in PROTOTYPE_TOOLS are not wrapped — short-circuit."""
        middleware = ResponseEnvelopeMiddleware()
        ctx = _make_context("central_get_sites")
        raw = {"sites": [{"name": "dallas-hq"}]}
        original = _make_tool_result(structured=raw)
        call_next = AsyncMock(return_value=original)

        result = await middleware.on_call_tool(ctx, call_next)

        # Same object — no wrapping
        assert result is original
        assert result.structured_content == raw

    @pytest.mark.asyncio
    async def test_already_enveloped_passes_through(self):
        """If a prototype tool already returned an envelope, don't re-wrap."""
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
    async def test_prototype_tools_set_membership(self):
        """All four documented prototype tools are in PROTOTYPE_TOOLS."""
        assert "health" in PROTOTYPE_TOOLS
        assert "site_health_check" in PROTOTYPE_TOOLS
        assert "site_rf_check" in PROTOTYPE_TOOLS
        assert "manage_wlan_profile" in PROTOTYPE_TOOLS
        assert len(PROTOTYPE_TOOLS) == 4
