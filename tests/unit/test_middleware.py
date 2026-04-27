"""Unit tests for NullStripMiddleware, ValidationCatchMiddleware, SandboxErrorCatchMiddleware."""

from unittest.mock import AsyncMock, MagicMock

import pytest
from fastmcp.exceptions import ToolError
from pydantic import BaseModel, Field, ValidationError

from hpe_networking_mcp.middleware.null_strip import NullStripMiddleware
from hpe_networking_mcp.middleware.sandbox_error_catch import SandboxErrorCatchMiddleware
from hpe_networking_mcp.middleware.validation_catch import ValidationCatchMiddleware

# ---------------------------------------------------------------------------
# Helper to build a fake MiddlewareContext
# ---------------------------------------------------------------------------


def _make_context(arguments: dict | None):
    """Return a mock MiddlewareContext whose message.arguments is *arguments*."""
    message = MagicMock()
    message.arguments = arguments

    # model_copy should return a new message with updated fields
    def _model_copy(update=None):
        new_msg = MagicMock()
        new_msg.arguments = update.get("arguments", arguments) if update else arguments
        return new_msg

    message.model_copy = _model_copy

    context = MagicMock()
    context.message = message

    # context.copy should return a new context with the updated message
    def _context_copy(message=None):
        new_ctx = MagicMock()
        new_ctx.message = message if message is not None else context.message
        return new_ctx

    context.copy = _context_copy
    return context


# ---------------------------------------------------------------------------
# NullStripMiddleware
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestNullStripMiddleware:
    @pytest.mark.asyncio
    async def test_strips_null_values(self):
        middleware = NullStripMiddleware()
        ctx = _make_context({"org_id": "abc", "site_id": None, "name": None})
        call_next = AsyncMock(return_value="tool_result")

        result = await middleware.on_call_tool(ctx, call_next)

        assert result == "tool_result"
        # call_next should have been called with a context whose arguments lack None values
        called_ctx = call_next.call_args[0][0]
        assert called_ctx.message.arguments == {"org_id": "abc"}

    @pytest.mark.asyncio
    async def test_preserves_non_null_values(self):
        middleware = NullStripMiddleware()
        ctx = _make_context({"org_id": "abc", "limit": 100, "name": "test"})
        call_next = AsyncMock(return_value="tool_result")

        await middleware.on_call_tool(ctx, call_next)

        # No nulls, so the original context should be passed through unchanged
        called_ctx = call_next.call_args[0][0]
        assert called_ctx.message.arguments == {"org_id": "abc", "limit": 100, "name": "test"}

    @pytest.mark.asyncio
    async def test_handles_empty_arguments(self):
        middleware = NullStripMiddleware()
        ctx = _make_context({})
        call_next = AsyncMock(return_value="tool_result")

        result = await middleware.on_call_tool(ctx, call_next)

        assert result == "tool_result"
        # Empty dict is falsy, so call_next gets the original context
        call_next.assert_called_once_with(ctx)

    @pytest.mark.asyncio
    async def test_handles_none_arguments(self):
        middleware = NullStripMiddleware()
        ctx = _make_context(None)
        call_next = AsyncMock(return_value="tool_result")

        result = await middleware.on_call_tool(ctx, call_next)

        assert result == "tool_result"
        call_next.assert_called_once_with(ctx)

    @pytest.mark.asyncio
    async def test_passthrough_when_no_nulls(self):
        """When all values are non-null, the original context is passed through."""
        middleware = NullStripMiddleware()
        ctx = _make_context({"a": 1, "b": "two", "c": [3]})
        call_next = AsyncMock(return_value="ok")

        await middleware.on_call_tool(ctx, call_next)

        # len(filtered) == len(message.arguments), so original context is used
        call_next.assert_called_once_with(ctx)

    @pytest.mark.asyncio
    async def test_strips_all_null_values(self):
        """When every argument is None, the result should be an empty dict."""
        middleware = NullStripMiddleware()
        ctx = _make_context({"a": None, "b": None})
        call_next = AsyncMock(return_value="done")

        await middleware.on_call_tool(ctx, call_next)

        called_ctx = call_next.call_args[0][0]
        assert called_ctx.message.arguments == {}


# ---------------------------------------------------------------------------
# ValidationCatchMiddleware
# ---------------------------------------------------------------------------


def _make_validation_error(field: str, msg: str, value=None) -> ValidationError:
    """Build a real Pydantic ValidationError for testing.

    Triggers it through a Pydantic model so the structure matches what
    FastMCP's tool dispatcher actually raises during param coercion.
    """

    class _M(BaseModel):
        x: int = Field()

    try:
        _M(x=value if value is not None else "not-an-int")  # type: ignore[arg-type]
    except ValidationError as e:
        return e
    raise AssertionError("expected ValidationError")  # pragma: no cover


def _make_call_tool_context(name: str = "some_tool"):
    """Mock MiddlewareContext for on_call_tool — message.name set to *name*."""
    message = MagicMock()
    message.name = name

    context = MagicMock()
    context.message = message
    return context


@pytest.mark.unit
class TestValidationCatchMiddleware:
    """The middleware must intercept Pydantic ValidationError and return a
    structured ToolResult so the AI in code mode receives a readable string
    instead of a MontyRuntimeError that crashes execute(). Closes #206.
    """

    @pytest.mark.asyncio
    async def test_catches_validation_error_returns_string(self):
        """The originally-bug-inducing case: Pydantic raises during param
        coercion → middleware catches → ToolResult content is a string the
        AI can read.
        """
        middleware = ValidationCatchMiddleware()
        ctx = _make_call_tool_context("mist_search_alarms")

        async def _raise(_ctx):
            raise _make_validation_error("severity", "Input should be 'critical', 'info' or 'warn'")

        result = await middleware.on_call_tool(ctx, _raise)

        # ToolResult — content is a list of TextContent blocks; first block has the readable text.
        assert hasattr(result, "content"), "must return a ToolResult-like object"
        text = result.content[0].text if result.content else ""
        assert "validation failed" in text.lower()
        assert "mist_search_alarms" in text

    @pytest.mark.asyncio
    async def test_passes_through_valid_calls(self):
        """No ValidationError → middleware returns whatever call_next returned."""
        middleware = ValidationCatchMiddleware()
        ctx = _make_call_tool_context("any_tool")
        sentinel = object()
        call_next = AsyncMock(return_value=sentinel)

        result = await middleware.on_call_tool(ctx, call_next)

        assert result is sentinel
        call_next.assert_called_once_with(ctx)

    @pytest.mark.asyncio
    async def test_does_not_catch_other_exceptions(self):
        """Only Pydantic ValidationError is intercepted. Other exceptions
        (ToolError, RuntimeError, KeyError, ...) propagate unchanged so
        they hit the existing handlers further up the stack.
        """
        middleware = ValidationCatchMiddleware()
        ctx = _make_call_tool_context("any_tool")

        async def _raise(_ctx):
            raise RuntimeError("boom — not a ValidationError")

        with pytest.raises(RuntimeError, match="boom"):
            await middleware.on_call_tool(ctx, _raise)

    @pytest.mark.asyncio
    async def test_error_string_lists_each_failing_field(self):
        """Multi-field validation errors should produce one readable line per field."""

        class _M(BaseModel):
            severity: str = Field()
            limit: int = Field()

        try:
            _M(severity=None, limit="not-a-number")  # type: ignore[arg-type]
            raise AssertionError("expected ValidationError")  # pragma: no cover
        except ValidationError as e:
            multi_err = e

        middleware = ValidationCatchMiddleware()
        ctx = _make_call_tool_context("mist_search_alarms")

        async def _raise(_ctx):
            raise multi_err

        result = await middleware.on_call_tool(ctx, _raise)
        text = result.content[0].text

        # Both failing fields should appear in the formatted error.
        assert "severity" in text
        assert "limit" in text

    @pytest.mark.asyncio
    async def test_tool_name_appears_in_error_string(self):
        """The AI uses the tool name in error messages to know which call failed."""
        middleware = ValidationCatchMiddleware()
        ctx = _make_call_tool_context("apstra_apply_ct_policies")

        async def _raise(_ctx):
            raise _make_validation_error("application_points", "must be a list")

        result = await middleware.on_call_tool(ctx, _raise)
        text = result.content[0].text

        assert "apstra_apply_ct_policies" in text


# ---------------------------------------------------------------------------
# SandboxErrorCatchMiddleware
# ---------------------------------------------------------------------------


async def _make_monty_error(message: str):
    """Build a real ``MontyError`` instance by running code that raises in
    the sandbox.

    All three concrete Monty error classes (``MontyRuntimeError`` /
    ``MontySyntaxError`` / ``MontyTypingError``) plus their base
    ``MontyError`` are Rust-backed and cannot be constructed from Python.
    The only way to get one is to run failing Monty code and capture
    what the sandbox raises.
    """
    import pydantic_monty

    monty = pydantic_monty.Monty(f'raise Exception("{message}")')
    try:
        await monty.run_async()
    except pydantic_monty.MontyError as e:
        return e
    raise AssertionError("expected MontyError")  # pragma: no cover


def _wrap_in_tool_error(cause: BaseException) -> ToolError:
    """Mirror what FastMCP's ``server.call_tool`` does with
    ``mask_error_details=True``: wrap the original exception in a generic
    ``ToolError`` with the original on ``__cause__``.
    """
    err = ToolError("Error calling tool 'execute'")
    err.__cause__ = cause
    return err


@pytest.mark.unit
class TestSandboxErrorCatchMiddleware:
    """The middleware must intercept the ``ToolError`` that FastMCP wraps
    around a sandbox ``MontyError`` (caused by the masking layer) and
    return the underlying error's text as a structured ToolResult, so the
    AI can read the actual cause and self-correct instead of seeing a
    generic "Error calling tool 'execute'". Closes #208.

    We synthesize the wrap-in-ToolError shape in tests because that's
    exactly what FastMCP's ``server.call_tool`` produces when
    ``mask_error_details=True`` (set in our ``create_server`` for security).
    """

    @pytest.mark.asyncio
    async def test_catches_monty_runtime_error_on_execute(self):
        """The originally-bug-inducing case: LLM calls `search` from inside
        execute() → sandbox raises MontyError("Unknown tool: search")
        → FastMCP wraps as ToolError → middleware unwraps → ToolResult
        content carries the readable text.
        """
        cause = await _make_monty_error("Unknown tool: search")
        wrapped = _wrap_in_tool_error(cause)

        middleware = SandboxErrorCatchMiddleware()
        ctx = _make_call_tool_context("execute")

        async def _raise(_ctx):
            raise wrapped

        result = await middleware.on_call_tool(ctx, _raise)

        assert hasattr(result, "content"), "must return a ToolResult-like object"
        text = result.content[0].text if result.content else ""
        assert "sandbox error" in text.lower()
        assert "Unknown tool: search" in text

    @pytest.mark.asyncio
    async def test_does_not_catch_on_non_execute_tools(self):
        """Sandbox errors only happen on `execute`. The middleware must NOT
        intercept anything on other tools — those have their own contract.
        """
        cause = await _make_monty_error("simulated runtime error on the wrong tool")
        wrapped = _wrap_in_tool_error(cause)

        middleware = SandboxErrorCatchMiddleware()
        ctx = _make_call_tool_context("mist_get_sites")

        async def _raise(_ctx):
            raise wrapped

        with pytest.raises(ToolError):
            await middleware.on_call_tool(ctx, _raise)

    @pytest.mark.asyncio
    async def test_passes_through_successful_execute_calls(self):
        """No exception → middleware returns whatever call_next returned."""
        middleware = SandboxErrorCatchMiddleware()
        ctx = _make_call_tool_context("execute")
        sentinel = object()
        call_next = AsyncMock(return_value=sentinel)

        result = await middleware.on_call_tool(ctx, call_next)

        assert result is sentinel
        call_next.assert_called_once_with(ctx)

    @pytest.mark.asyncio
    async def test_does_not_catch_tool_error_with_non_monty_cause(self):
        """ToolError is also raised for non-sandbox failures (e.g. unrelated
        bugs that get masked). When the underlying cause is NOT a MontyError,
        the middleware must let the ToolError propagate so the existing
        masked-error contract still applies.
        """
        wrapped = _wrap_in_tool_error(RuntimeError("not sandbox-related"))

        middleware = SandboxErrorCatchMiddleware()
        ctx = _make_call_tool_context("execute")

        async def _raise(_ctx):
            raise wrapped

        with pytest.raises(ToolError):
            await middleware.on_call_tool(ctx, _raise)

    @pytest.mark.asyncio
    async def test_does_not_catch_unrelated_exceptions_on_execute(self):
        """Bare exceptions (not a ToolError wrap) must propagate. Only the
        wrapped-by-FastMCP-with-MontyError-cause shape is intercepted.
        """
        middleware = SandboxErrorCatchMiddleware()
        ctx = _make_call_tool_context("execute")

        async def _raise(_ctx):
            raise RuntimeError("boom — bare exception, not a ToolError")

        with pytest.raises(RuntimeError, match="boom"):
            await middleware.on_call_tool(ctx, _raise)

    @pytest.mark.asyncio
    async def test_error_text_carries_actionable_detail(self):
        """The wrapped error's str() form must be preserved in the returned
        text — that's what the LLM reads to fix its code.
        """
        cause = await _make_monty_error("division by zero at line 4")
        wrapped = _wrap_in_tool_error(cause)

        middleware = SandboxErrorCatchMiddleware()
        ctx = _make_call_tool_context("execute")

        async def _raise(_ctx):
            raise wrapped

        result = await middleware.on_call_tool(ctx, _raise)
        text = result.content[0].text

        assert "division by zero" in text
        assert "line 4" in text
