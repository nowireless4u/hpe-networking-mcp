"""SandboxErrorCatchMiddleware — catch code-mode sandbox errors.

In ``MCP_TOOL_MODE=code``, the ``execute`` tool runs LLM-written Python in a
``pydantic_monty`` sandbox. Any sandbox-level error (``MontyRuntimeError``,
``MontySyntaxError``, ``MontyTypingError``) bubbles out and, combined with
``mask_error_details=True`` (which we deliberately set for security), is
caught by FastMCP's tool dispatcher in ``server.py:call_tool`` and re-raised
as a generic ``ToolError("Error calling tool 'execute'")`` — leaving the
LLM with nothing to self-correct from.

The original ``MontyError`` is preserved on ``ToolError.__cause__``, so this
middleware catches ``ToolError`` for the ``execute`` tool, inspects the
cause, and if it's a ``MontyError`` re-raises a fresh ``ToolError`` carrying
the actual error text. Middleware sits *outside* the masking layer in the
call chain, so this fresh exception propagates to the MCP request handler
unmasked — the wire response gets ``isError: true`` AND the readable error
text in ``content``. The LLM sees the message; the orchestrator sees the
failure flag.

(Aside on why this differs from ``ValidationCatchMiddleware``: FastMCP
special-cases ``ValidationError`` to re-raise unchanged — so that catch can
match the original type. ``MontyError`` falls through to the generic
``Exception`` branch which applies the masking wrapper.)

Closes #208 (LLM self-correction) and #(this PR) (orchestrator-visible
``isError`` flag). The "Unknown tool: search" masking case is the most
common trigger — LLMs frequently try to call discovery tools from inside
``execute()`` even though those only exist at the outer MCP surface.
Syntax errors from stray indentation in model-generated code are another.
"""

from __future__ import annotations

import json
import re
from datetime import UTC, datetime
from typing import Any

import mcp.types
from fastmcp.exceptions import ToolError
from fastmcp.server.middleware import Middleware, MiddlewareContext
from loguru import logger

from hpe_networking_mcp.platforms._common.tool_suggest import (
    unknown_tool_payload_from_text,
)

# pydantic_monty ships in the fastmcp[code-mode] extra. If it's missing,
# code mode itself can't run, so we don't need this middleware to act —
# but importing it must not crash the server.
try:
    from pydantic_monty import MontyError  # type: ignore[import-not-found]

    _HAS_MONTY = True
except ImportError:
    MontyError = Exception  # type: ignore[misc,assignment]
    _HAS_MONTY = False


# Sandbox clock/time dead-ends monty can't satisfy even with the clock
# enabled: `datetime.utcnow()` (monty implements only `datetime.now`) and the
# absent `time` module. The clock-enabled provider makes `datetime.now()` /
# `date.today()` work, but a model reaching for these specific names still
# hard-fails — so we turn the raw error into a self-correcting one. Substring
# match against the lower-cased cause text.
_CLOCK_DEADEND_MARKERS: tuple[str, ...] = (
    "utcnow",  # AttributeError: ... no attribute 'utcnow'
    "no module named 'time'",  # ModuleNotFoundError on `import time`
    "os function 'datetime",  # NotImplementedError (clock disabled / older deploy)
    "os function 'date",
)


def _clock_error_hint(cause_text: str) -> str | None:
    """Return self-correcting guidance for a sandbox clock/time dead-end.

    The middleware runs in real (non-sandbox) Python, so it can stamp the
    actual current time into the message — giving the model both the working
    substitute API and a literal value it can hardcode. Returns ``None`` when
    the error is unrelated to the clock.
    """
    low = cause_text.lower()
    if not any(marker in low for marker in _CLOCK_DEADEND_MARKERS):
        return None
    now = datetime.now(UTC)
    iso = now.strftime("%Y-%m-%dT%H:%M:%SZ")
    return (
        "Hint: the sandbox has no `datetime.utcnow()` and no `time` module, but "
        "the clock IS available — use `datetime.now(datetime.timezone.utc)` "
        "(or `datetime.now()` / `datetime.date.today()`), and "
        "`datetime.now().timestamp()` instead of `time.time()`. "
        f"Current UTC time is {iso}. Many search/report tools also accept a "
        '`duration` argument (e.g. "1d"), so you often need not compute a '
        "window at all."
    )


_NAMEERROR_RE = re.compile(r"name ['\"]([^'\"]+)['\"] is not defined")


def _nameerror_hint(cause_text: str) -> str | None:
    """Return guidance for a sandbox ``NameError``.

    The single most common cause is a model splitting work across multiple
    ``execute()`` calls and referencing a variable defined in an earlier
    block — but each ``execute()`` runs in a FRESH, stateless sandbox, so
    nothing persists between calls (observed: Haiku 4.5 referencing an
    `org_id` set in a prior block). The hint also covers the plain-typo case.
    Returns ``None`` for non-NameError causes.
    """
    m = _NAMEERROR_RE.search(cause_text)
    if m is None:
        return None
    name = m.group(1)
    return (
        f"Hint: `{name}` is undefined. Each `execute()` call runs in a FRESH, "
        "stateless sandbox — variables defined in a PREVIOUS `execute()` block "
        "do NOT carry over. Do all the work for one task inside a SINGLE "
        f"`execute()` block, or recompute/re-fetch `{name}` at the top of this "
        "block before using it. (If it's simply a typo, fix the name.)"
    )


class SandboxErrorCatchMiddleware(Middleware):
    """Convert sandbox ``MontyError`` (wrapped in ``ToolError`` by FastMCP's
    masking layer) into a fresh ``ToolError`` with the readable cause text.

    Re-raising (rather than returning a ``ToolResult``) is deliberate: the
    fresh ``ToolError`` propagates to the MCP request handler unmasked, so
    the wire response gets ``isError: true`` AND the readable error text in
    ``content``. Returning a ``ToolResult`` instead would suppress
    ``isError`` (the wire flag would be ``false`` since no exception was
    raised) — orchestrators can't distinguish failed tool calls from
    successful ones that returned an error-shaped string.

    Only acts on the code-mode ``execute`` tool. All other tools pass through
    untouched — sandbox errors are a code-mode-specific failure mode.
    """

    EXECUTE_TOOL_NAME = "execute"

    async def on_call_tool(
        self,
        context: MiddlewareContext[mcp.types.CallToolRequestParams],
        call_next: Any,
    ) -> Any:
        if not _HAS_MONTY:
            return await call_next(context)

        tool_name = getattr(context.message, "name", "")
        if tool_name != self.EXECUTE_TOOL_NAME:
            return await call_next(context)

        try:
            return await call_next(context)
        except ToolError as e:
            # FastMCP wraps the original sandbox exception in ToolError when
            # mask_error_details=True is set. The original is on __cause__.
            cause = e.__cause__
            if not isinstance(cause, MontyError):
                # Not a sandbox failure — let the masked ToolError propagate.
                raise
            # An "Unknown tool: X" inside execute() is the single most common
            # sandbox error (a model guessing a tool name). Turn it into a
            # structured "did you mean" payload with real candidate names so
            # the model self-corrects instead of looping on the same call
            # (#489). The candidates are data, not an imperative.
            suggestion = unknown_tool_payload_from_text(str(cause))
            if suggestion is not None:
                error_text = json.dumps(suggestion)
            else:
                error_text = f"Sandbox error: {cause}"
                # Append a self-correcting hint for the common small-model
                # sandbox-model mistakes (clock dead-ends, cross-block state).
                # The error result is the one channel the model reliably acts
                # on, unlike advisory INSTRUCTIONS.md content. The causes are
                # mutually exclusive, so the first match wins.
                for hint_fn in (_clock_error_hint, _nameerror_hint):
                    hint = hint_fn(str(cause))
                    if hint is not None:
                        error_text = f"{error_text}\n\n{hint}"
                        break
            logger.debug("SandboxErrorCatch: caught on {} → {}", tool_name, error_text)
            # Re-raise so the wire response sets isError=true. Middleware
            # sits outside the masking layer, so this propagates with the
            # message intact — fixing both LLM-readability (#208) and
            # orchestrator-visible isError flag.
            raise ToolError(error_text) from cause
