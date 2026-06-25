"""Pydantic ``ValidationError`` catch middleware.

In ``MCP_TOOL_MODE=code``, a tool whose parameters fail Pydantic validation
would otherwise propagate as ``MontyRuntimeError`` and crash the AI's whole
``execute()`` block — the AI's try/except inside the sandbox cannot catch it.

This middleware catches ``ValidationError`` at the ``on_call_tool`` layer
(BEFORE it reaches FastMCP's exception transform) and returns a
properly-shaped envelope ``ToolResult`` so the AI's
``response.get("ok")`` style code branches cleanly.

The fix shape (#309): we return a ``ToolResult`` with BOTH ``content``
(text for clients that read the text channel) AND ``structured_content``
(envelope dict for clients that read the structured channel — which is
every code-mode caller via ``await call_tool(...)``). Without
``structured_content``, code-mode callers receive a bare string and
hit ``AttributeError: 'str' object has no attribute 'get'`` when they
treat the response like every other tool's response.

``ResponseEnvelopeMiddleware``'s idempotency check (`_is_envelope_shape`)
recognizes the envelope by ``{ok, data, tool}`` key presence and passes
it through unchanged, so the wrap is not double-applied.
"""

from __future__ import annotations

from typing import Any

import mcp.types
from fastmcp.server.middleware import Middleware, MiddlewareContext
from fastmcp.tools.tool import ToolResult
from loguru import logger
from pydantic import ValidationError

from hpe_networking_mcp.middleware.response_envelope import _build_envelope, _infer_platform
from hpe_networking_mcp.redaction.safe_summary import summarize_validation_errors

# HTTP-style status code for parameter validation failures. Matches what
# the envelope's ``status`` field would carry if the tool itself had
# raised a 422 — keeps RetryMiddleware's status-code-based decision
# tree consistent across validation rejections and upstream API 422s.
_VALIDATION_STATUS = 422


class ValidationCatchMiddleware(Middleware):
    """Convert Pydantic ``ValidationError`` into a properly-enveloped tool result.

    Without this, the error fires inside FastMCP's tool dispatcher, becomes
    ``MontyRuntimeError`` in code mode, and crashes ``execute()``. With this,
    the AI receives a normal envelope-shaped dict response with
    ``ok=False, status=422, message=<readable error>`` and can branch on it
    the same way it branches on any other tool's error path.
    """

    async def on_call_tool(
        self,
        context: MiddlewareContext[mcp.types.CallToolRequestParams],
        call_next: Any,
    ) -> ToolResult:
        try:
            return await call_next(context)  # type: ignore[no-any-return]
        except ValidationError as e:
            tool_name = getattr(context.message, "name", "unknown")
            # Build the message via the shared redactor (#523/#534): sensitive
            # field VALUES are redacted by name and complex/long inputs are
            # summarized by type/shape. The SAME redacted text feeds both the
            # model-visible response AND the log, so neither channel can leak a
            # password / token / PSK or dump a huge rejected payload.
            error_text = summarize_validation_errors(tool_name, e.errors())
            logger.debug("ValidationCatchMiddleware: caught {} → {}", tool_name, error_text)

            # Build a proper envelope so code-mode callers receive a dict
            # via ``call_tool(...)`` instead of a bare string (#309). The
            # text content is preserved for clients that read the text
            # channel — both surfaces carry the same readable error.
            envelope = _build_envelope(
                ok=False,
                data=None,
                status=_VALIDATION_STATUS,
                message=error_text,
                tool=tool_name,
                platform=_infer_platform(tool_name),
            )
            return ToolResult(content=error_text, structured_content=envelope)
