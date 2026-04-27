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
cause, and if it's a ``MontyError`` returns the actual error text as a
string ``ToolResult`` so the LLM can read the real cause.

(Aside on why this differs from ``ValidationCatchMiddleware``: FastMCP
special-cases ``ValidationError`` to re-raise unchanged — so that catch can
match the original type. ``MontyError`` falls through to the generic
``Exception`` branch which applies the masking wrapper.)

Closes #208. The "Unknown tool: search" masking case is the most common
trigger — LLMs frequently try to call discovery tools from inside
``execute()`` even though those only exist at the outer MCP surface.
"""

from __future__ import annotations

from typing import Any

import mcp.types
from fastmcp.exceptions import ToolError
from fastmcp.server.middleware import Middleware, MiddlewareContext
from fastmcp.tools.tool import ToolResult
from loguru import logger

# pydantic_monty ships in the fastmcp[code-mode] extra. If it's missing,
# code mode itself can't run, so we don't need this middleware to act —
# but importing it must not crash the server.
try:
    from pydantic_monty import MontyError  # type: ignore[import-not-found]

    _HAS_MONTY = True
except ImportError:
    MontyError = Exception  # type: ignore[misc,assignment]
    _HAS_MONTY = False


class SandboxErrorCatchMiddleware(Middleware):
    """Convert sandbox ``MontyError`` (wrapped in ``ToolError`` by FastMCP's
    masking layer) into a readable string ``ToolResult``.

    Only acts on the code-mode ``execute`` tool. All other tools pass through
    untouched — sandbox errors are a code-mode-specific failure mode.
    """

    EXECUTE_TOOL_NAME = "execute"

    async def on_call_tool(
        self,
        context: MiddlewareContext[mcp.types.CallToolRequestParams],
        call_next: Any,
    ) -> ToolResult:
        if not _HAS_MONTY:
            return await call_next(context)  # type: ignore[no-any-return]

        tool_name = getattr(context.message, "name", "")
        if tool_name != self.EXECUTE_TOOL_NAME:
            return await call_next(context)  # type: ignore[no-any-return]

        try:
            return await call_next(context)  # type: ignore[no-any-return]
        except ToolError as e:
            # FastMCP wraps the original sandbox exception in ToolError when
            # mask_error_details=True is set. The original is on __cause__.
            cause = e.__cause__
            if not isinstance(cause, MontyError):
                # Not a sandbox failure — let the masked ToolError propagate.
                raise
            error_text = f"Sandbox error: {cause}"
            logger.debug("SandboxErrorCatch: caught on {} → {}", tool_name, error_text)
            return ToolResult(content=error_text)
