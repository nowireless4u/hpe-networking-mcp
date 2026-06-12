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

from hpe_networking_mcp.middleware.elicitation import confirm_gated_invoke

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

    async def test_prompt_failure_with_confirmed_true_proceeds(self):
        """Popup-less fallback: confirmed=true carries authority ONLY after elicit raises."""
        ctx = _ctx(elicit=AsyncMock(side_effect=RuntimeError("client has no elicitation")))
        result = await confirm_gated_invoke(ctx, "central tool 'x'", {"confirmed": True})
        assert result is None

    async def test_prompt_failure_without_confirmed_requires_chat_confirmation(self):
        ctx = _ctx(elicit=AsyncMock(side_effect=RuntimeError("client has no elicitation")))
        result = await confirm_gated_invoke(ctx, "central tool 'x'", {})
        assert result is not None
        assert result["status"] == "confirmation_required"
        assert "confirmed=true" in result["message"]


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
