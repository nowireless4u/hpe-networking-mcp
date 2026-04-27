"""SPIKE — Pydantic ValidationError catch middleware.

Goal: in MCP_TOOL_MODE=code, a tool whose parameters fail Pydantic validation
currently propagates as MontyRuntimeError and crashes the AI's whole
execute() block. The AI's try/except inside the sandbox cannot catch it.

This middleware catches ValidationError at the on_call_tool layer (BEFORE it
reaches FastMCP's exception transform) and returns a structured ToolResult
with a string error the AI can branch on — same shape as tools that
explicitly return error strings (Axis, ClearPass).

If the spike works, this becomes the permanent fix for #202's out-of-scope
follow-up (Apstra Pydantic field validators + any future similar pattern
across all platforms).
"""

from __future__ import annotations

from typing import Any

import mcp.types
from fastmcp.server.middleware import Middleware, MiddlewareContext
from fastmcp.tools.tool import ToolResult
from loguru import logger
from pydantic import ValidationError


class ValidationCatchMiddleware(Middleware):
    """Convert Pydantic ValidationError into a structured tool-result string.

    Without this, the error fires inside FastMCP's tool dispatcher, becomes
    MontyRuntimeError in code mode, and crashes execute(). With this, the
    AI sees a normal-looking string return and can recover.
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
            # Format the ValidationError details into a readable string —
            # mirrors what Pydantic's str(e) gives us but trimmed.
            error_lines = [f"Error: validation failed for tool '{tool_name}':"]
            for err in e.errors():
                loc = ".".join(str(x) for x in err.get("loc", []))
                msg = err.get("msg", "invalid")
                err_input = err.get("input")
                if err_input is not None:
                    error_lines.append(f"  - {loc}: {msg} (got: {err_input!r})")
                else:
                    error_lines.append(f"  - {loc}: {msg}")
            error_text = "\n".join(error_lines)
            logger.debug("ValidationCatchMiddleware: caught {} → {}", tool_name, error_text)
            return ToolResult(content=error_text)
