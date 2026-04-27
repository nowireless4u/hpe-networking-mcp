"""Unit tests for NullStripMiddleware, ValidationCatchMiddleware,
SandboxErrorCatchMiddleware, and RetryMiddleware."""

from unittest.mock import AsyncMock, MagicMock

import pytest
from fastmcp.exceptions import ToolError
from fastmcp.tools.tool import ToolResult
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


# ---------------------------------------------------------------------------
# RetryMiddleware
# ---------------------------------------------------------------------------


def _toolresult_with_status(status_code: int, **extra) -> ToolResult:
    """Build a ToolResult whose structured_content carries a status code,
    matching the shape Mist/GreenLake return on error.
    """
    body = {"status_code": status_code, "message": "test", **extra}
    return ToolResult(structured_content=body)


def _toolresult_ok() -> ToolResult:
    """Build a successful ToolResult with no status_code field."""
    return ToolResult(structured_content={"results": [], "ok": True})


def _make_retry_context(tool_name: str, fastmcp_tool=None):
    """Mock MiddlewareContext for RetryMiddleware tests.

    fastmcp_tool: optional Tool-like object whose .tags drive read/write
    classification. None means the tool isn't found → treated as read.
    """
    message = MagicMock()
    message.name = tool_name

    class _FakeFastMCP:
        async def get_tool(self, _name):
            return fastmcp_tool

    class _FakeFastMCPContext:
        @property
        def fastmcp(self):
            return _FakeFastMCP()

    context = MagicMock()
    context.message = message
    context.fastmcp_context = _FakeFastMCPContext()
    return context


def _fake_tool(*tags: str):
    """Build a fake Tool-like object with the given tags set."""
    t = MagicMock()
    t.tags = set(tags)
    return t


@pytest.mark.unit
class TestRetryMiddleware:
    """Closes #133 + #134. RetryMiddleware retries 5xx on reads, 429 on
    reads+writes, honors Retry-After, respects max-attempts cap, leaves
    valid responses + non-transient errors untouched.
    """

    @pytest.mark.asyncio
    async def test_retries_5xx_on_read_and_succeeds(self):
        """A read tool that 503s once then 200s should be retried and succeed."""
        from hpe_networking_mcp.middleware.retry import RetryMiddleware

        middleware = RetryMiddleware(max_attempts=3, initial_delay=0.0, max_delay=0.0)
        ctx = _make_retry_context("mist_get_devices", fastmcp_tool=_fake_tool("mist"))

        responses = [_toolresult_with_status(503), _toolresult_ok()]
        call_next = AsyncMock(side_effect=responses)

        result = await middleware.on_call_tool(ctx, call_next)

        assert call_next.call_count == 2  # one retry
        # The second response (the OK one) is what we should see
        assert result.structured_content["ok"] is True

    @pytest.mark.asyncio
    async def test_does_not_retry_5xx_on_write_tool(self):
        """5xx on a write tool returns immediately (idempotency unsafe)."""
        from hpe_networking_mcp.middleware.retry import RetryMiddleware

        middleware = RetryMiddleware(max_attempts=3, initial_delay=0.0, max_delay=0.0)
        ctx = _make_retry_context(
            "mist_change_site_configuration_objects",
            fastmcp_tool=_fake_tool("mist", "mist_write_delete"),
        )

        result_503 = _toolresult_with_status(503)
        call_next = AsyncMock(return_value=result_503)

        result = await middleware.on_call_tool(ctx, call_next)

        assert call_next.call_count == 1  # no retry on write
        assert result.structured_content["status_code"] == 503

    @pytest.mark.asyncio
    async def test_retries_429_on_write_tool(self):
        """429 retries even on write tools — server is asking us to slow down."""
        from hpe_networking_mcp.middleware.retry import RetryMiddleware

        middleware = RetryMiddleware(max_attempts=3, initial_delay=0.0, max_delay=0.0)
        ctx = _make_retry_context("axis_manage_user", fastmcp_tool=_fake_tool("axis", "axis_write_delete"))

        responses = [_toolresult_with_status(429), _toolresult_ok()]
        call_next = AsyncMock(side_effect=responses)

        result = await middleware.on_call_tool(ctx, call_next)

        assert call_next.call_count == 2
        assert result.structured_content["ok"] is True

    @pytest.mark.asyncio
    async def test_does_not_retry_2xx_or_4xx(self):
        """Non-transient responses pass through unchanged on the first call."""
        from hpe_networking_mcp.middleware.retry import RetryMiddleware

        middleware = RetryMiddleware(max_attempts=3, initial_delay=0.0, max_delay=0.0)
        ctx = _make_retry_context("mist_get_devices", fastmcp_tool=_fake_tool("mist"))

        # 200-shaped (no status_code in dict) — middleware sees it as a clean success
        call_next = AsyncMock(return_value=_toolresult_ok())
        await middleware.on_call_tool(ctx, call_next)
        assert call_next.call_count == 1

        # 400-shaped — non-transient, pass through
        call_next = AsyncMock(return_value=_toolresult_with_status(400))
        await middleware.on_call_tool(ctx, call_next)
        assert call_next.call_count == 1

    @pytest.mark.asyncio
    async def test_max_attempts_cap_enforced(self):
        """If every attempt fails, return after max_attempts and don't retry forever."""
        from hpe_networking_mcp.middleware.retry import RetryMiddleware

        middleware = RetryMiddleware(max_attempts=3, initial_delay=0.0, max_delay=0.0)
        ctx = _make_retry_context("mist_get_devices", fastmcp_tool=_fake_tool("mist"))

        result_503 = _toolresult_with_status(503)
        call_next = AsyncMock(return_value=result_503)

        result = await middleware.on_call_tool(ctx, call_next)

        assert call_next.call_count == 3  # exactly max_attempts
        # Last result is what surfaces back
        assert result.structured_content["status_code"] == 503

    @pytest.mark.asyncio
    async def test_retry_after_header_respected(self):
        """When 429 carries Retry-After, sleep that many seconds (capped at max_delay)."""
        from hpe_networking_mcp.middleware.retry import RetryMiddleware

        middleware = RetryMiddleware(max_attempts=2, initial_delay=10.0, max_delay=60.0)
        ctx = _make_retry_context("mist_get_devices", fastmcp_tool=_fake_tool("mist"))

        # Server says wait 5 seconds — middleware should honor that, not the 10s default
        responses = [
            _toolresult_with_status(429, **{"Retry-After": "5"}),
            _toolresult_ok(),
        ]
        call_next = AsyncMock(side_effect=responses)

        # Patch asyncio.sleep so the test doesn't actually wait
        async def _spy_sleep(seconds):
            _spy_sleep.last_seconds = seconds  # type: ignore[attr-defined]

        from unittest.mock import patch

        with patch("hpe_networking_mcp.middleware.retry.asyncio.sleep", side_effect=_spy_sleep):
            await middleware.on_call_tool(ctx, call_next)

        assert _spy_sleep.last_seconds == 5.0  # type: ignore[attr-defined]

    @pytest.mark.asyncio
    async def test_retry_after_capped_at_max_delay(self):
        """Server-supplied Retry-After is capped — don't sleep forever even if asked."""
        from hpe_networking_mcp.middleware.retry import RetryMiddleware

        middleware = RetryMiddleware(max_attempts=2, initial_delay=1.0, max_delay=60.0)
        ctx = _make_retry_context("mist_get_devices", fastmcp_tool=_fake_tool("mist"))

        # Server says wait 999 seconds — we cap at max_delay (60)
        responses = [
            _toolresult_with_status(429, **{"Retry-After": "999"}),
            _toolresult_ok(),
        ]
        call_next = AsyncMock(side_effect=responses)

        async def _spy_sleep(seconds):
            _spy_sleep.last_seconds = seconds  # type: ignore[attr-defined]

        from unittest.mock import patch

        with patch("hpe_networking_mcp.middleware.retry.asyncio.sleep", side_effect=_spy_sleep):
            await middleware.on_call_tool(ctx, call_next)

        assert _spy_sleep.last_seconds == 60.0  # type: ignore[attr-defined]

    @pytest.mark.asyncio
    async def test_max_attempts_one_disables_retry(self):
        """RETRY_MAX_ATTEMPTS=1 should pass through with no retry behavior."""
        from hpe_networking_mcp.middleware.retry import RetryMiddleware

        middleware = RetryMiddleware(max_attempts=1, initial_delay=0.0, max_delay=0.0)
        ctx = _make_retry_context("mist_get_devices", fastmcp_tool=_fake_tool("mist"))

        result_503 = _toolresult_with_status(503)
        call_next = AsyncMock(return_value=result_503)

        await middleware.on_call_tool(ctx, call_next)

        assert call_next.call_count == 1  # no retry

    @pytest.mark.asyncio
    async def test_status_in_response_central_pattern(self):
        """Central uses ``code`` instead of ``status_code`` — middleware should still detect."""
        from fastmcp.tools.tool import ToolResult

        from hpe_networking_mcp.middleware.retry import RetryMiddleware

        middleware = RetryMiddleware(max_attempts=2, initial_delay=0.0, max_delay=0.0)
        ctx = _make_retry_context("central_get_devices", fastmcp_tool=_fake_tool("central"))

        # pycentral's error shape uses ``code``, not ``status_code``
        first = ToolResult(structured_content={"code": 503, "msg": "transient"})
        second = _toolresult_ok()
        call_next = AsyncMock(side_effect=[first, second])

        result = await middleware.on_call_tool(ctx, call_next)

        assert call_next.call_count == 2
        assert result.structured_content["ok"] is True

    @pytest.mark.asyncio
    async def test_status_in_response_clearpass_pattern(self):
        """ClearPass uses ``status`` instead of ``status_code``."""
        from fastmcp.tools.tool import ToolResult

        from hpe_networking_mcp.middleware.retry import RetryMiddleware

        middleware = RetryMiddleware(max_attempts=2, initial_delay=0.0, max_delay=0.0)
        ctx = _make_retry_context("clearpass_get_network_devices", fastmcp_tool=_fake_tool("clearpass"))

        first = ToolResult(structured_content={"status": 503, "title": "transient"})
        second = _toolresult_ok()
        call_next = AsyncMock(side_effect=[first, second])

        result = await middleware.on_call_tool(ctx, call_next)

        assert call_next.call_count == 2
        assert result.structured_content["ok"] is True

    @pytest.mark.asyncio
    async def test_httpx_exception_path_retries(self):
        """httpx.HTTPStatusError on a read tool retries via the exception path."""
        import httpx

        from hpe_networking_mcp.middleware.retry import RetryMiddleware

        middleware = RetryMiddleware(max_attempts=3, initial_delay=0.0, max_delay=0.0)
        ctx = _make_retry_context("axis_get_connectors", fastmcp_tool=_fake_tool("axis"))

        # Build a real HTTPStatusError with a 503 response
        request = httpx.Request("GET", "https://x")
        response = httpx.Response(503, request=request)
        exc = httpx.HTTPStatusError("server error", request=request, response=response)

        call_next = AsyncMock(side_effect=[exc, _toolresult_ok()])

        result = await middleware.on_call_tool(ctx, call_next)

        assert call_next.call_count == 2
        assert result.structured_content["ok"] is True

    @pytest.mark.asyncio
    async def test_httpx_exception_does_not_retry_on_write(self):
        """5xx exception on a write tool re-raises — idempotency unsafe."""
        import httpx

        from hpe_networking_mcp.middleware.retry import RetryMiddleware

        middleware = RetryMiddleware(max_attempts=3, initial_delay=0.0, max_delay=0.0)
        ctx = _make_retry_context("axis_manage_connector", fastmcp_tool=_fake_tool("axis", "axis_write_delete"))

        request = httpx.Request("POST", "https://x")
        response = httpx.Response(503, request=request)
        exc = httpx.HTTPStatusError("server error", request=request, response=response)

        call_next = AsyncMock(side_effect=exc)

        with pytest.raises(httpx.HTTPStatusError):
            await middleware.on_call_tool(ctx, call_next)
        assert call_next.call_count == 1  # no retry

    @pytest.mark.asyncio
    async def test_httpx_429_retry_after_from_header(self):
        """httpx exception path also honors Retry-After."""
        import httpx

        from hpe_networking_mcp.middleware.retry import RetryMiddleware

        middleware = RetryMiddleware(max_attempts=2, initial_delay=10.0, max_delay=60.0)
        ctx = _make_retry_context("axis_get_connectors", fastmcp_tool=_fake_tool("axis"))

        request = httpx.Request("GET", "https://x")
        response = httpx.Response(429, headers={"Retry-After": "7"}, request=request)
        exc = httpx.HTTPStatusError("rate limit", request=request, response=response)

        call_next = AsyncMock(side_effect=[exc, _toolresult_ok()])

        async def _spy_sleep(seconds):
            _spy_sleep.last_seconds = seconds  # type: ignore[attr-defined]

        from unittest.mock import patch

        with patch("hpe_networking_mcp.middleware.retry.asyncio.sleep", side_effect=_spy_sleep):
            await middleware.on_call_tool(ctx, call_next)

        assert _spy_sleep.last_seconds == 7.0  # type: ignore[attr-defined]

    @pytest.mark.asyncio
    async def test_unknown_exceptions_are_not_caught(self):
        """Only httpx.HTTPStatusError is intercepted on the exception path —
        other exceptions propagate to upstream handlers."""
        from hpe_networking_mcp.middleware.retry import RetryMiddleware

        middleware = RetryMiddleware(max_attempts=3, initial_delay=0.0, max_delay=0.0)
        ctx = _make_retry_context("mist_get_devices", fastmcp_tool=_fake_tool("mist"))

        call_next = AsyncMock(side_effect=RuntimeError("boom"))

        with pytest.raises(RuntimeError, match="boom"):
            await middleware.on_call_tool(ctx, call_next)
        assert call_next.call_count == 1  # no retry on unknown exception
