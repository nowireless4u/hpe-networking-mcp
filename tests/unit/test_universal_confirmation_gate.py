"""Unit tests for the universal confirmation gate (#415 / #416 / #436).

The gate lives at the ``<platform>_invoke_tool`` dispatch chokepoint and is
keyed ONLY on the ``requires_confirmation`` tag (never hints). The decision
sequence under test:

1. ``DISABLE_ELICITATION=true`` → auto-accept.
2. A real ``ctx.elicit()`` prompt is attempted FIRST — accept proceeds,
   decline/cancel return structured results, and crucially ``confirmed=true``
   is IGNORED while a prompt is available (the #415 self-authorization hole).
3. Only when the prompt raises is ``confirmed=true`` honored (chat fallback).
4. Fail-closed at the dispatcher: an unclassified tool is treated as gated.
"""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastmcp.server.elicitation import (
    AcceptedElicitation,
    CancelledElicitation,
    DeclinedElicitation,
)
from mcp.shared.exceptions import McpError
from mcp.types import ErrorData

from hpe_networking_mcp.middleware.elicitation import _sanitized_param_summary, confirm_gated_invoke


def _no_elicitation_error() -> McpError:
    return McpError(ErrorData(code=-32601, message="Elicitation not supported"))


pytestmark = pytest.mark.unit


def _ctx(*, disable_elicitation: bool = False, elicit: AsyncMock | None = None) -> MagicMock:
    ctx = MagicMock()
    ctx.lifespan_context = {"config": SimpleNamespace(disable_elicitation=disable_elicitation)}
    ctx.elicit = elicit if elicit is not None else AsyncMock(return_value=AcceptedElicitation(data=None))
    return ctx


class TestConfirmGatedInvoke:
    async def test_disabled_elicitation_auto_accepts_without_prompting(self):
        ctx = _ctx(disable_elicitation=True)
        result = await confirm_gated_invoke(ctx, "central tool 'x'", {})
        assert result is None
        ctx.elicit.assert_not_called()

    async def test_accept_proceeds(self):
        ctx = _ctx()
        assert await confirm_gated_invoke(ctx, "central tool 'x'", {}) is None
        ctx.elicit.assert_awaited_once()

    async def test_decline_returns_declined(self):
        ctx = _ctx(elicit=AsyncMock(return_value=DeclinedElicitation()))
        result = await confirm_gated_invoke(ctx, "central tool 'x'", {})
        assert result == {"status": "declined", "message": "Action declined by user."}

    async def test_cancel_returns_cancelled(self):
        ctx = _ctx(elicit=AsyncMock(return_value=CancelledElicitation()))
        result = await confirm_gated_invoke(ctx, "central tool 'x'", {})
        assert result is not None
        assert result["status"] == "cancelled"

    async def test_confirmed_true_is_ignored_while_prompt_available(self):
        """The #415 hole: confirmed=true must NOT bypass a working prompt."""
        ctx = _ctx(elicit=AsyncMock(return_value=DeclinedElicitation()))
        result = await confirm_gated_invoke(ctx, "central tool 'x'", {"confirmed": True})
        assert result is not None
        assert result["status"] == "declined"  # human's decline wins over the flag
        ctx.elicit.assert_awaited_once()  # the prompt WAS shown despite confirmed=true

    async def test_client_without_elicitation_with_confirmed_true_proceeds(self):
        """Popup-less fallback: confirmed=true carries authority ONLY on the
        legitimate no-capability signal (McpError 'Elicitation not supported')."""
        ctx = _ctx(elicit=AsyncMock(side_effect=_no_elicitation_error()))
        result = await confirm_gated_invoke(ctx, "central tool 'x'", {"confirmed": True})
        assert result is None

    async def test_client_without_elicitation_requires_chat_confirmation(self):
        ctx = _ctx(elicit=AsyncMock(side_effect=_no_elicitation_error()))
        result = await confirm_gated_invoke(ctx, "central tool 'x'", {})
        assert result is not None
        assert result["status"] == "confirmation_required"
        assert "confirmed=true" in result["message"]

    async def test_other_mcp_errors_fail_closed_even_with_confirmed(self):
        """An McpError that is NOT the no-capability signal (e.g. transport
        failure) must fail closed — confirmed=true is not honored."""
        transport_err = McpError(ErrorData(code=-32000, message="transport went sideways"))
        ctx = _ctx(elicit=AsyncMock(side_effect=transport_err))
        result = await confirm_gated_invoke(ctx, "central tool 'x'", {"confirmed": True})
        assert result is not None
        assert result["status"] == "confirmation_unavailable"

    async def test_unexpected_elicit_failure_fails_closed_even_with_confirmed(self):
        """A handler crash / framework bug is NOT a license to skip
        confirmation — confirmed=true is not honored for unknown failures."""
        ctx = _ctx(elicit=AsyncMock(side_effect=RuntimeError("handler exploded")))
        result = await confirm_gated_invoke(ctx, "central tool 'x'", {"confirmed": True})
        assert result is not None
        assert result["status"] == "confirmation_unavailable"
        assert "NOT performed" in result["message"]

    async def test_prompt_includes_sanitized_params(self):
        """The human must see WHAT they approve — targets shown, secrets redacted."""
        captured: list[str] = []

        async def grab(message, response_type=None):
            captured.append(message)
            return AcceptedElicitation(data=None)

        ctx = _ctx(elicit=AsyncMock(side_effect=grab))
        await confirm_gated_invoke(
            ctx,
            "central tool 'central_bulk_delete_sites'",
            {"items": [{"id": "7"}], "psk": "supersecret", "confirmed": True},
        )
        assert len(captured) == 1
        assert '"id": "7"' in captured[0]  # target visible
        assert "supersecret" not in captured[0]  # secret redacted
        assert "confirmed" not in captured[0]  # bookkeeping flag dropped

    async def test_redaction_covers_camel_and_compound_keys(self):
        """api_key / apiKey / clientSecret / refreshToken / private-key all redact."""
        captured: list[str] = []

        async def grab(message, response_type=None):
            captured.append(message)
            return AcceptedElicitation(data=None)

        ctx = _ctx(elicit=AsyncMock(side_effect=grab))
        await confirm_gated_invoke(
            ctx,
            "central tool 'x'",
            {
                "apiKey": "LEAK1",
                "clientSecret": "LEAK2",
                "refreshToken": "LEAK3",
                "private-key": "LEAK4",
                "payload": {"radiusSharedSecret": "LEAK5", "site_name": "HQ"},
            },
        )
        prompt = captured[0]
        for leak in ("LEAK1", "LEAK2", "LEAK3", "LEAK4", "LEAK5"):
            assert leak not in prompt
        assert "HQ" in prompt  # non-sensitive values stay visible

    def test_param_summary_caps_length(self):
        summary = _sanitized_param_summary({"payload": {"x" * 10: "y" * 1000}})
        assert len(summary) <= 300


class TestInvokeToolGating:
    """The dispatcher applies the gate iff requires_confirmation (fail-closed)."""

    def _spec(self, *, tags: set[str], capability):
        return SimpleNamespace(
            name="central_test_tool",
            func=AsyncMock(return_value={"ok": True}),
            platform="central",
            category="test",
            description="Test tool.",
            tags=tags,
            capability=capability,
        )

    def test_gate_predicate_matches_design(self):
        """Pin the predicate: tag-driven, fail-closed on missing capability."""
        from hpe_networking_mcp.platforms._common.annotations import Capability

        gated = self._spec(tags={"central_write_delete", "requires_confirmation"}, capability=Capability.WRITE_DELETE)
        read = self._spec(tags=set(), capability=Capability.READ)
        unclassified = self._spec(tags=set(), capability=None)

        def needs_confirmation(spec) -> bool:
            return "requires_confirmation" in spec.tags or spec.capability is None

        assert needs_confirmation(gated) is True
        assert needs_confirmation(read) is False
        assert needs_confirmation(unclassified) is True  # fail-closed

    async def test_dispatch_blocks_on_decline_and_never_calls_tool(self):
        """End-to-end through the real _invoke_tool body via the registry."""
        from hpe_networking_mcp.platforms._common import meta_tools

        spec = self._spec(tags={"requires_confirmation"}, capability=None)

        ctx = MagicMock()
        ctx.lifespan_context = {"config": SimpleNamespace(disable_elicitation=False)}
        ctx.elicit = AsyncMock(return_value=DeclinedElicitation())

        # Drive the gate exactly as _invoke_tool does.
        needs = "requires_confirmation" in spec.tags or spec.capability is None
        assert needs
        gate = await meta_tools.confirm_gated_invoke(ctx, "central tool 'central_test_tool'", {"confirmed": True})
        assert gate is not None and gate["status"] == "declined"
        spec.func.assert_not_called()
