"""Unit tests for NullStripMiddleware, ElicitationMiddleware, and ValidationCatchMiddleware."""

from unittest.mock import AsyncMock, MagicMock

import pytest
from pydantic import BaseModel, Field, ValidationError

from hpe_networking_mcp.middleware.null_strip import NullStripMiddleware
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
