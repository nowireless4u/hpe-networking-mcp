"""Unit tests for ValidationCatchMiddleware envelope-contract fix (#309).

Before the fix, a Pydantic ValidationError caught by this middleware
returned ``ToolResult(content=error_text)`` — content-only, no
structured_content. Code-mode callers using ``await call_tool(...)``
received a bare string and crashed with ``AttributeError: 'str' object
has no attribute 'get'`` when they did the standard ``response.get('ok')``
check.

The fix returns a properly-shaped envelope via ``structured_content``,
so code-mode callers always receive a dict envelope they can branch on.

These tests pin that contract.
"""

from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock

import pytest
from fastmcp.tools.tool import ToolResult
from pydantic import BaseModel, ValidationError

from hpe_networking_mcp.middleware.validation_catch import ValidationCatchMiddleware

pytestmark = pytest.mark.unit


class _Sample(BaseModel):
    """Minimal pydantic model used to trigger a real ValidationError."""

    count: int


def _trigger_validation_error() -> ValidationError:
    """Produce a real ValidationError to feed the middleware via raise."""
    try:
        _Sample(count="not-an-int")  # type: ignore[arg-type]
    except ValidationError as e:
        return e
    raise AssertionError("expected ValidationError")


def _make_context(tool_name: str) -> MagicMock:
    """Build a MiddlewareContext mock matching the middleware's expectations."""
    ctx = MagicMock()
    ctx.message = MagicMock()
    ctx.message.name = tool_name
    return ctx


class TestValidationCatchEnvelope:
    """The fix: response carries a structured envelope, not just text content."""

    async def test_returns_envelope_with_ok_false(self):
        middleware = ValidationCatchMiddleware()
        ctx = _make_context("central_get_alerts")

        async def raising_next(_: Any) -> Any:
            raise _trigger_validation_error()

        result = await middleware.on_call_tool(ctx, raising_next)

        assert isinstance(result, ToolResult)
        env = result.structured_content
        assert env is not None, "structured_content must be present (#309 fix)"
        assert env["ok"] is False
        assert env["status"] == 422
        assert env["data"] is None
        assert env["tool"] == "central_get_alerts"
        assert env["platform"] == "central"

    async def test_message_carries_readable_error(self):
        middleware = ValidationCatchMiddleware()
        ctx = _make_context("mist_list_org_devices")

        async def raising_next(_: Any) -> Any:
            raise _trigger_validation_error()

        result = await middleware.on_call_tool(ctx, raising_next)

        env = result.structured_content
        assert env is not None
        assert "validation failed" in env["message"]
        assert "count" in env["message"]  # the field name from _Sample model

    async def test_content_field_matches_message(self):
        """Text content and envelope message carry the same human-readable string."""
        middleware = ValidationCatchMiddleware()
        ctx = _make_context("apstra_get_blueprints")

        async def raising_next(_: Any) -> Any:
            raise _trigger_validation_error()

        result = await middleware.on_call_tool(ctx, raising_next)

        env = result.structured_content
        assert env is not None
        # ``content`` is a list of ContentBlocks (mcp.types). Extract text.
        content_text = next(
            (block.text for block in result.content if hasattr(block, "text")),
            None,
        )
        assert content_text == env["message"]

    async def test_platform_inference_for_each_prefix(self):
        """Every platform prefix should be inferred correctly into the envelope."""
        cases = [
            ("mist_anything", "mist"),
            ("central_anything", "central"),
            ("greenlake_anything", "greenlake"),
            ("clearpass_anything", "clearpass"),
            ("apstra_anything", "apstra"),
            ("axis_anything", "axis"),
            ("aos8_anything", "aos8"),
            ("health", None),  # cross-platform tool — no prefix match
            ("execute", None),  # code-mode entry — no prefix match
        ]
        middleware = ValidationCatchMiddleware()

        for tool_name, expected_platform in cases:
            ctx = _make_context(tool_name)

            async def raising_next(_: Any) -> Any:
                raise _trigger_validation_error()

            result = await middleware.on_call_tool(ctx, raising_next)
            env = result.structured_content
            assert env is not None
            assert env["platform"] == expected_platform, (
                f"tool {tool_name!r} should infer platform={expected_platform!r}, got {env['platform']!r}"
            )

    async def test_non_validation_errors_propagate(self):
        """Anything that isn't a ValidationError must NOT be caught here."""
        middleware = ValidationCatchMiddleware()
        ctx = _make_context("central_get_alerts")

        async def raising_next(_: Any) -> Any:
            raise RuntimeError("not a validation error")

        with pytest.raises(RuntimeError, match="not a validation error"):
            await middleware.on_call_tool(ctx, raising_next)

    async def test_passes_through_normal_results(self):
        """When call_next succeeds, the middleware must return its result unchanged."""
        middleware = ValidationCatchMiddleware()
        ctx = _make_context("central_get_sites")

        expected = ToolResult(content="ok", structured_content={"ok": True, "data": "ok", "tool": "x"})

        async def succeeding_next(_: Any) -> Any:
            return expected

        result = await middleware.on_call_tool(ctx, succeeding_next)
        assert result is expected


class _SecretModel(BaseModel):
    """Model with a sensitive field name to test value redaction."""

    password: int


def _trigger_secret_validation_error(secret_value: str) -> ValidationError:
    try:
        _SecretModel(password=secret_value)  # type: ignore[arg-type]
    except ValidationError as e:
        return e
    raise AssertionError("expected ValidationError")


class TestValidationCatchRedaction:
    """#523/#534 — a validation failure must not echo a secret-bearing or
    oversized rejected input into the model-visible response OR the logs.
    """

    async def test_secret_value_redacted_in_response(self):
        middleware = ValidationCatchMiddleware()
        ctx = _make_context("central_invoke_tool")
        err = _trigger_secret_validation_error("supersecret-value")

        async def raising_next(_: Any) -> Any:
            raise err

        result = await middleware.on_call_tool(ctx, raising_next)
        message = result.structured_content["message"]
        assert "supersecret-value" not in message
        assert "***redacted***" in message

    async def test_secret_value_not_in_logs(self, loguru_capture):
        """#534 — the log channel must not leak the rejected secret either."""
        middleware = ValidationCatchMiddleware()
        ctx = _make_context("central_invoke_tool")
        err = _trigger_secret_validation_error("supersecret-value")

        async def raising_next(_: Any) -> Any:
            raise err

        await middleware.on_call_tool(ctx, raising_next)
        joined = "\n".join(loguru_capture)
        assert "supersecret-value" not in joined
