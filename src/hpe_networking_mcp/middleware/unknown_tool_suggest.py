"""UnknownToolSuggestMiddleware — teach the model when it calls a missing tool.

In code mode the only top-level tools are ``execute`` plus the discovery
tools. A model that assumes per-platform tools are first-class calls
``central_list_sites`` directly at the MCP surface and gets a bare
``Unknown tool`` error, from which it typically concludes the platform is
"unavailable" and gives up (#489).

This middleware catches an ``Unknown tool`` failure for **any** top-level tool
call and re-raises it as a structured "did you mean" payload carrying real,
registered candidate names — so the model self-corrects instead of giving up.

It is the top-surface companion to ``SandboxErrorCatchMiddleware``, which
handles the same class of error for guesses made *inside* ``execute``. The two
do not collide: the sandbox middleware emits a JSON payload whose text does
not contain the ``Unknown tool:`` phrase, so this middleware leaves it
untouched regardless of ordering.
"""

from __future__ import annotations

import json
from typing import Any

import mcp.types
from fastmcp.exceptions import ToolError
from fastmcp.server.middleware import Middleware, MiddlewareContext
from loguru import logger

from hpe_networking_mcp.platforms._common.tool_suggest import (
    unknown_tool_payload_from_text,
)


class UnknownToolSuggestMiddleware(Middleware):
    """Convert a top-level ``Unknown tool`` error into a structured suggestion.

    Re-raises (rather than returning a result) so the wire response keeps
    ``isError: true`` while carrying the readable candidate list in the
    content — matching the contract ``SandboxErrorCatchMiddleware`` uses.
    """

    async def on_call_tool(
        self,
        context: MiddlewareContext[mcp.types.CallToolRequestParams],
        call_next: Any,
    ) -> Any:
        try:
            return await call_next(context)
        except Exception as e:
            # Only act on an "Unknown tool: X" error; everything else (real
            # tool failures, validation, sandbox payloads already formatted by
            # SandboxErrorCatch) passes through unchanged.
            payload = unknown_tool_payload_from_text(str(e))
            if payload is None:
                raise
            logger.debug("UnknownToolSuggest: {} → {}", getattr(context.message, "name", ""), payload)
            raise ToolError(json.dumps(payload)) from e
