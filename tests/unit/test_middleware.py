"""Unit tests for NullStripMiddleware and ElicitationMiddleware."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from hpe_networking_mcp.middleware.null_strip import NullStripMiddleware


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
