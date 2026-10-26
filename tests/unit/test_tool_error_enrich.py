"""Unit tests for ToolErrorEnrichMiddleware (#638).

Raised ``ToolError``s bypass the spec-index enrichment that returned-envelope
and ValidationError paths get. This middleware closes that gap by appending
``reactive_hint(tool_name, status_code)`` to the message. These tests pin the
enrichment logic (the ``_enriched`` decision) with ``reactive_hint`` stubbed.
"""

from __future__ import annotations

import pytest
from fastmcp.exceptions import ToolError

from hpe_networking_mcp.middleware.tool_error_enrich import ToolErrorEnrichMiddleware

pytestmark = pytest.mark.unit

_HINT = "  [spec-index] API documents 404: The requested resource does not exist"


def test_structured_toolerror_gets_hint_appended(monkeypatch):
    monkeypatch.setattr(
        "hpe_networking_mcp.spec_index.error_help.reactive_hint",
        lambda tool, code: _HINT,
    )
    err = ToolError({"status_code": 404, "message": "boom"})
    out = ToolErrorEnrichMiddleware._enriched("mist_get_site_sle_impact_summary", err)
    assert out is not None
    assert out.args[0]["status_code"] == 404
    assert out.args[0]["message"] == "boom" + _HINT


def test_string_payload_passes_through():
    # No status_code to look up → nothing to enrich.
    err = ToolError("plain string error")
    assert ToolErrorEnrichMiddleware._enriched("mist_get_x", err) is None


def test_already_enriched_is_idempotent(monkeypatch):
    calls = []
    monkeypatch.setattr(
        "hpe_networking_mcp.spec_index.error_help.reactive_hint",
        lambda tool, code: calls.append(1) or "x",
    )
    err = ToolError({"status_code": 404, "message": "boom  [spec-index] already there"})
    assert ToolErrorEnrichMiddleware._enriched("mist_get_x", err) is None
    assert not calls  # short-circuits before calling reactive_hint


def test_no_hint_available_passes_through(monkeypatch):
    monkeypatch.setattr(
        "hpe_networking_mcp.spec_index.error_help.reactive_hint",
        lambda tool, code: None,
    )
    err = ToolError({"status_code": 500, "message": "boom"})
    assert ToolErrorEnrichMiddleware._enriched("central_get_x", err) is None


def test_enrichment_failure_never_breaks(monkeypatch):
    def _boom(tool, code):
        raise RuntimeError("index blew up")

    monkeypatch.setattr("hpe_networking_mcp.spec_index.error_help.reactive_hint", _boom)
    err = ToolError({"status_code": 404, "message": "boom"})
    # Must swallow the enrichment failure and pass the original through unchanged.
    assert ToolErrorEnrichMiddleware._enriched("mist_get_x", err) is None


async def test_middleware_enriches_raised_toolerror_end_to_end(monkeypatch):
    """The wired middleware catches a tool's raised ToolError and the enriched
    message reaches the client — the path a raw `_enriched` unit test can't prove."""
    from fastmcp import Client, FastMCP

    monkeypatch.setattr(
        "hpe_networking_mcp.spec_index.error_help.reactive_hint",
        lambda tool, code: "  [spec-index] API documents 404: Not found",
    )
    mcp = FastMCP("enrich-test", middleware=[ToolErrorEnrichMiddleware()])

    @mcp.tool
    async def boom_tool() -> dict:
        raise ToolError({"status_code": 404, "message": "no such metric"})

    async with Client(mcp) as client:
        with pytest.raises(ToolError) as e:
            await client.call_tool("boom_tool", {})
    text = str(e.value)
    assert "no such metric" in text
    assert "[spec-index] API documents 404" in text
