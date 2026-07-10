"""Tests for the PII/redaction hardening batch (#586–#590).

Each class targets one Casey Jones finding:

* #586 — ``TokenStore`` idle-TTL purge of stale session keymaps.
* #587 — inbound middleware refuses dead-session tokens on a fresh session.
* #588 — validation-error summaries redact secrets at any loc depth.
* #589 — outbound tokenization sweeps identifier-bearing dict *keys*.
* #590 — MAC normalizer recognizes the ProCurve ``aabbcc-ddeeff`` format.
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from hpe_networking_mcp.redaction.mac_normalizer import (
    canonicalize_mac,
    is_mac_address,
    normalize_macs_in_value,
)
from hpe_networking_mcp.redaction.rules import TokenKind
from hpe_networking_mcp.redaction.safe_summary import REDACTED, summarize_validation_errors
from hpe_networking_mcp.redaction.token_store import TokenEntry, TokenStore
from hpe_networking_mcp.redaction.tokenizer import Tokenizer
from hpe_networking_mcp.redaction.walker import tokenize_response

pytestmark = pytest.mark.unit


def _tokenizer(store: TokenStore, session_id: str = "s") -> Tokenizer:
    km = store.get_or_create(session_id, now=0.0)
    return Tokenizer(km, session_id=session_id, max_entries=store.max_entries_per_session)


# ---------------------------------------------------------------------------
# #590 — ProCurve MAC format
# ---------------------------------------------------------------------------


class TestProCurveMac:
    def test_recognized_and_canonicalized(self) -> None:
        assert is_mac_address("aabbcc-ddeeff")
        assert is_mac_address("AABBCC-DDEEFF")
        assert canonicalize_mac("aabbcc-ddeeff") == "aa:bb:cc:dd:ee:ff"

    def test_free_text_rewrite(self) -> None:
        assert normalize_macs_in_value("client aabbcc-ddeeff dropped") == "client aa:bb:cc:dd:ee:ff dropped"

    def test_other_formats_still_work(self) -> None:
        for mac in ("aa:bb:cc:dd:ee:ff", "aa-bb-cc-dd-ee-ff", "aabb.ccdd.eeff", "aabbccddeeff"):
            assert is_mac_address(mac)

    def test_uuid_not_matched(self) -> None:
        uuid = "12345678-1234-1234-1234-123456789abc"
        assert not is_mac_address(uuid)
        assert normalize_macs_in_value(f"id {uuid} here") == f"id {uuid} here"


# ---------------------------------------------------------------------------
# #588 — validation-error redaction at any loc depth
# ---------------------------------------------------------------------------


class TestValidationErrorRedaction:
    def test_secret_at_list_index_loc_redacted(self) -> None:
        errors = [{"loc": ("shared_secrets", 1), "msg": "invalid", "input": "topsecret-value"}]
        out = summarize_validation_errors("t", errors)
        assert REDACTED in out
        assert "topsecret-value" not in out

    def test_secret_at_union_tag_loc_redacted(self) -> None:
        errors = [{"loc": ("password", "str"), "msg": "invalid", "input": "hunter2"}]
        out = summarize_validation_errors("t", errors)
        assert REDACTED in out
        assert "hunter2" not in out

    def test_non_sensitive_list_index_still_shown(self) -> None:
        errors = [{"loc": ("site_names", 0), "msg": "invalid", "input": "HQ"}]
        out = summarize_validation_errors("t", errors)
        assert "HQ" in out
        assert REDACTED not in out


# ---------------------------------------------------------------------------
# #589 — identifier-bearing dict keys
# ---------------------------------------------------------------------------


class TestIdentifierKeys:
    def test_mac_key_normalized_without_tokenizer(self) -> None:
        # MAC normalization is always-on (tokenizer=None).
        out = tokenize_response({"AABBCC-DDEEFF": {"x": 1}}, None)
        assert out == {"aa:bb:cc:dd:ee:ff": {"x": 1}}

    def test_email_key_tokenized(self) -> None:
        store = TokenStore()
        tok = _tokenizer(store)
        out = tokenize_response({"alice@example.com": {"role": "admin"}}, tok)
        keys = list(out.keys())
        assert "alice@example.com" not in keys
        assert keys[0].startswith("[[EMAIL:")
        # value dict preserved
        assert out[keys[0]] == {"role": "admin"}

    def test_plain_key_untouched(self) -> None:
        store = TokenStore()
        tok = _tokenizer(store)
        out = tokenize_response({"site_name": "HQ"}, tok)
        assert "site_name" in out


# ---------------------------------------------------------------------------
# #586 — TokenStore idle-TTL purge
# ---------------------------------------------------------------------------


class TestTokenStoreTtl:
    def _entry(self) -> TokenEntry:
        return TokenEntry(kind=TokenKind.PSK, token="[[PSK:x]]", plaintext="secret")

    def test_purge_expired_drops_idle_sessions(self) -> None:
        store = TokenStore(session_ttl_seconds=3600.0)
        idle = store.get_or_create("idle", now=0.0)
        idle.by_token["[[PSK:x]]"] = self._entry()
        store.get_or_create("active", now=0.0)
        store.get_or_create("active", now=1000.0)  # touch → last_seen=1000

        dropped = store.purge_expired(now=4000.0)  # cutoff=400: idle(0)<400, active(1000)>=400
        assert dropped == 1  # idle had one entry
        assert "idle" not in store._sessions
        assert "active" in store._sessions
        assert "idle" not in store._last_seen  # no timestamp leak

    def test_get_or_create_sweeps_on_access(self) -> None:
        store = TokenStore(session_ttl_seconds=3600.0)
        store.get_or_create("old", now=0.0)
        store.get_or_create("new", now=4000.0)  # access sweeps 'old'
        assert "old" not in store._sessions
        assert "new" in store._sessions

    def test_ttl_none_disables_purge(self) -> None:
        store = TokenStore(session_ttl_seconds=None)
        store.get_or_create("s", now=0.0)
        assert store.purge_expired(now=10_000_000.0) == 0
        assert "s" in store._sessions

    def test_end_session_clears_last_seen(self) -> None:
        store = TokenStore()
        store.get_or_create("s", now=0.0)
        store.end_session("s")
        assert store.session_count() == 0
        assert "s" not in store._last_seen


# ---------------------------------------------------------------------------
# #587 — fresh-session unknown-token refusal
# ---------------------------------------------------------------------------


def _ctx(session_id: str, arguments: dict) -> MagicMock:
    ctx = MagicMock()
    ctx.fastmcp_context.session_id = session_id
    ctx.message.name = "central_manage_thing"
    ctx.message.arguments = arguments
    return ctx


class TestFreshSessionTokenRefusal:
    async def test_refuses_dead_session_token_before_call_next(self) -> None:
        from hpe_networking_mcp.middleware.pii_tokenization import PIITokenizationMiddleware

        store = TokenStore()  # empty — no keymap for this session yet
        mw = PIITokenizationMiddleware(store, enabled=True)
        called = []

        async def call_next(c):  # pragma: no cover — must NOT run
            called.append(1)
            return MagicMock()

        # First call of a fresh session carrying a token from a dead session.
        ctx = _ctx("fresh-1", {"body": "[[PSK:12345678-1234-1234-1234-123456789abc]]"})
        result = await mw.on_call_tool(ctx, call_next)

        assert not called, "call_next must not run when inbound tokens are unknown"
        sc = result.structured_content
        assert sc["ok"] is False
        assert sc["status"] == 400

    async def test_token_free_args_pass_through(self) -> None:
        from fastmcp.tools.tool import ToolResult
        from mcp.types import TextContent

        from hpe_networking_mcp.middleware.pii_tokenization import PIITokenizationMiddleware

        store = TokenStore()
        mw = PIITokenizationMiddleware(store, enabled=True)
        called = []

        async def call_next(c):
            called.append(1)
            return ToolResult(content=[TextContent(type="text", text="ok")], structured_content={"ok": True})

        ctx = _ctx("fresh-2", {"site_id": "s1"})
        await mw.on_call_tool(ctx, call_next)
        assert called == [1], "token-free args must reach call_next"
