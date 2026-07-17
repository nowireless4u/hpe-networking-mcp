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

import re
from typing import Any

import mcp.types
from fastmcp.exceptions import ValidationError as FastMCPValidationError
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

# A rendered pydantic / FastMCP validation error echoes the rejected value as
# ``input_value=<repr>`` — a PSK, token, or password the caller mis-supplied.
# The repr can contain commas, quotes, and ``]`` (e.g. ``input_value='a,b]c'``),
# so a delimiter-bounded strip would leave a tail of the secret behind. Anchor
# instead on the end of the line: pydantic renders each error's
# ``[type=..., input_value=..., input_type=...]`` detail on a single line (any
# newline inside the value is escaped to a literal ``\n``), so removing from
# ``input_value=`` to the line end drops the value, the trailing
# ``input_type=``, and any URL in one shot while preserving the field name and
# human-readable message on the surrounding lines.
_INPUT_ECHO_RE = re.compile(r",?\s*input_value=[^\n]*")


def _summarize_message_only(tool_name: str, message: str) -> str:
    """Redact a validation message we only have as a string.

    Used for FastMCP's ``ValidationError``, which (unlike pydantic's) carries
    no structured ``.errors()`` — only a rendered string that may embed the
    rejected input value. Drop the ``input_value``/``input_type`` echoes and
    collapse whitespace so the model still learns *which* argument was wrong
    without the value leaking.
    """
    cleaned = _INPUT_ECHO_RE.sub("", message)
    cleaned = " ".join(cleaned.split())
    return f"Invalid arguments for tool {tool_name!r}: {cleaned}"


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
        except (ValidationError, FastMCPValidationError) as e:
            tool_name = getattr(context.message, "name", "unknown")
            # Two distinct exception types reach here:
            #
            #   * pydantic ``ValidationError`` — raised by a tool's own body
            #     validation. Carries structured ``.errors()``.
            #   * fastmcp ``ValidationError`` — raised by FastMCP's argument
            #     binding for a bad/unexpected kwarg (found during testing: an
            #     ``object_type`` kwarg the tool never declared). This is a
            #     plain ``FastMCPError`` with NO ``.errors()`` and only a string
            #     message — and it does NOT subclass pydantic's, so the old
            #     ``except ValidationError`` missed it entirely. In code mode
            #     that meant the whole ``execute()`` block died before the
            #     model's own try/except could see it, because a host exception
            #     out of ``call_tool`` is fatal to the sandbox. FastMCP stashes
            #     the originating pydantic error on ``__cause__`` when it has
            #     one, so recover the structured form for a clean, redacted
            #     summary and fall back to the (also redacted) string otherwise.
            structured = e.errors() if isinstance(e, ValidationError) else None
            cause = getattr(e, "__cause__", None)
            if structured is None and isinstance(cause, ValidationError):
                structured = cause.errors()

            # Build the message via the shared redactor (#523/#534): sensitive
            # field VALUES are redacted by name and complex/long inputs are
            # summarized by type/shape. The SAME redacted text feeds both the
            # model-visible response AND the log, so neither channel can leak a
            # password / token / PSK or dump a huge rejected payload.
            if structured is not None:
                error_text = summarize_validation_errors(tool_name, structured)
            else:
                error_text = _summarize_message_only(tool_name, str(e))
            logger.debug("ValidationCatchMiddleware: caught {} → {}", tool_name, error_text)

            # Reactive spec-index enrichment: append the legal body field set (and
            # the documented 422 meaning) so the model can fix an opaque-body
            # config/write call. Best-effort — never mask the validation error.
            try:
                from hpe_networking_mcp.spec_index.error_help import reactive_hint

                hint = reactive_hint(tool_name, _VALIDATION_STATUS)
            except Exception:  # pragma: no cover - enrichment must never break dispatch
                hint = None
            if hint:
                error_text += hint

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
