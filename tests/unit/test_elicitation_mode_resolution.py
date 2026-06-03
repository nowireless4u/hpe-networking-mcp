"""Regression tests for elicitation mode resolution in code mode.

Covers the bug where a destructive write dispatched through the code-mode
sandbox (``execute`` -> ``<platform>_invoke_tool`` -> tool) ran in a nested
``call_tool`` context that did NOT inherit the ``initialize`` request's
``elicitation_mode`` state. With the mode resolving to ``None``, the tool
never surfaced a prompt yet still returned ``"Action declined by user."`` —
a decline the user never made (the AI then spun, believing it was vetoed).

The fix (``_resolve_elicitation_mode``) re-derives the mode from ``config``
when request state is absent and defaults to ``chat_confirm`` so the tool
returns ``confirmation_required`` and the AI confirms with the user in chat.
"""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastmcp.server.elicitation import (
    AcceptedElicitation,
    DeclinedElicitation,
)

from hpe_networking_mcp.middleware.elicitation import (
    _resolve_elicitation_mode,
    confirm_write,
    elicitation_handler,
)

pytestmark = pytest.mark.unit


def _make_ctx(*, state: dict | None = None, disable_elicitation: bool = False) -> MagicMock:
    """Context double with dict-backed get_state/set_state and a config."""
    store: dict = dict(state or {})

    async def _get_state(key: str):
        return store.get(key)

    async def _set_state(key: str, value):
        store[key] = value

    ctx = MagicMock()
    ctx.get_state = AsyncMock(side_effect=_get_state)
    ctx.set_state = AsyncMock(side_effect=_set_state)
    ctx.lifespan_context = {"config": SimpleNamespace(disable_elicitation=disable_elicitation)}
    ctx._store = store  # expose for assertions
    return ctx


class TestResolveMode:
    async def test_missing_state_defaults_to_chat_confirm(self):
        """Code-mode nested context: state absent -> chat_confirm (and written back)."""
        ctx = _make_ctx(state={})  # mode is None
        mode = await _resolve_elicitation_mode(ctx)
        assert mode == "chat_confirm"
        assert ctx._store["elicitation_mode"] == "chat_confirm"

    async def test_missing_state_with_disable_resolves_disabled(self):
        ctx = _make_ctx(state={}, disable_elicitation=True)
        assert await _resolve_elicitation_mode(ctx) == "disabled"
        assert ctx._store["elicitation_mode"] == "disabled"

    @pytest.mark.parametrize("known", ["disabled", "prompt", "chat_confirm"])
    async def test_known_state_passed_through_untouched(self, known):
        ctx = _make_ctx(state={"elicitation_mode": known})
        assert await _resolve_elicitation_mode(ctx) == known
        ctx.set_state.assert_not_called()  # already known — no rewrite


class TestHandler:
    async def test_none_mode_returns_decline_and_marks_chat_confirm(self):
        """The exact transcript path: mode None -> no prompt, degrade to chat."""
        ctx = _make_ctx(state={})
        result = await elicitation_handler("delete X?", ctx)
        assert result.action == "decline"
        # ctx.elicit must NOT have been attempted (no popup possible)
        assert not ctx.elicit.called
        # mode now chat_confirm so the caller routes to confirmation_required
        assert ctx._store["elicitation_mode"] == "chat_confirm"

    async def test_disabled_autoaccepts(self):
        ctx = _make_ctx(state={"elicitation_mode": "disabled"})
        result = await elicitation_handler("delete X?", ctx)
        assert result.action == "accept"

    async def test_prompt_accept(self):
        ctx = _make_ctx(state={"elicitation_mode": "prompt"})
        ctx.elicit = AsyncMock(return_value=AcceptedElicitation(data=None))
        assert (await elicitation_handler("delete X?", ctx)).action == "accept"

    async def test_prompt_genuine_decline_preserved(self):
        """A surfaced popup the user actually declined stays a real decline."""
        ctx = _make_ctx(state={"elicitation_mode": "prompt"})
        ctx.elicit = AsyncMock(return_value=DeclinedElicitation())
        result = await elicitation_handler("delete X?", ctx)
        assert result.action == "decline"
        # mode unchanged — NOT degraded to chat_confirm
        assert ctx._store["elicitation_mode"] == "prompt"

    async def test_prompt_raises_degrades_to_chat_confirm(self):
        """elicit() can't round-trip from the sandbox -> degrade, don't fabricate."""
        ctx = _make_ctx(state={"elicitation_mode": "prompt"})
        ctx.elicit = AsyncMock(side_effect=RuntimeError("no transport"))
        result = await elicitation_handler("delete X?", ctx)
        assert result.action == "decline"
        assert ctx._store["elicitation_mode"] == "chat_confirm"


class TestConfirmWrite:
    async def test_code_mode_returns_confirmation_required_not_declined(self):
        """End-to-end: missing state must NOT yield a silent false decline."""
        ctx = _make_ctx(state={})
        guard = await confirm_write(ctx, message="remove profile FOO from scope 7")
        assert guard is not None
        assert guard["status"] == "confirmation_required"
        assert "confirmed=true" in guard["message"]

    async def test_genuine_decline_returns_declined(self):
        ctx = _make_ctx(state={"elicitation_mode": "prompt"})
        ctx.elicit = AsyncMock(return_value=DeclinedElicitation())
        guard = await confirm_write(ctx, message="remove profile FOO from scope 7")
        assert guard == {"status": "declined", "message": "Action declined by user."}

    async def test_disabled_proceeds(self):
        ctx = _make_ctx(state={"elicitation_mode": "disabled"})
        assert await confirm_write(ctx, message="remove profile FOO") is None
