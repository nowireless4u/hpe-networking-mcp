"""Null strip middleware — removes explicit null values from tool call arguments.

Many MCP clients send null for optional parameters instead of omitting them.
Pydantic rejects None when the declared type doesn't allow it (default=None
only skips validation when the key is absent). Removing null-valued keys
before the call reaches validation lets the Pydantic default kick in normally.
"""

import mcp.types
from fastmcp.server.middleware import Middleware, MiddlewareContext
from fastmcp.tools.tool import ToolResult
from loguru import logger


class NullStripMiddleware(Middleware):
    async def on_call_tool(
        self,
        context: MiddlewareContext[mcp.types.CallToolRequestParams],
        call_next,
    ) -> ToolResult:
        message = context.message
        if message.arguments:
            filtered = {k: v for k, v in message.arguments.items() if v is not None}
            if len(filtered) != len(message.arguments):
                logger.debug(
                    "NullStrip: stripped null keys {}",
                    sorted(set(message.arguments) - set(filtered)),
                )
                new_message = message.model_copy(update={"arguments": filtered})
                context = context.copy(message=new_message)
        return await call_next(context)  # type: ignore[return-value]
