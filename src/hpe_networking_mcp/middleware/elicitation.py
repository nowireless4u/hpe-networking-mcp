"""Elicitation middleware — detects client support and enables write tools accordingly.

During MCP initialization, detects whether the client supports elicitation
(via MCP capabilities) or has explicitly opted out via HTTP headers/query params.
Write tools are disabled by default via the server-level Visibility transform.
If elicitation support is detected, write tools are enabled for that session.
"""

import mcp.types
from fastmcp import Context
from fastmcp.client.elicitation import ElicitResult
from fastmcp.server.elicitation import (
    AcceptedElicitation,
    CancelledElicitation,
    DeclinedElicitation,
)
from fastmcp.server.middleware import Middleware, MiddlewareContext
from loguru import logger


class ElicitationMiddleware(Middleware):
    async def on_initialize(
        self,
        context: MiddlewareContext[mcp.types.InitializeRequest],
        call_next,
    ) -> mcp.types.InitializeResult | None:
        result = await call_next(context)
        ctx = context.fastmcp_context
        if ctx is None:
            return result  # type: ignore[return-value]

        # Access server config from lifespan context
        try:
            config = ctx.lifespan_context.get("config")
        except Exception:
            config = None

        if config is None:
            return result  # type: ignore[return-value]

        enable_write = False

        # DANGER ZONE: both flags set — skip elicitation entirely
        if config.enable_write_tools and config.disable_elicitation:
            enable_write = True
            await ctx.set_state("disable_elicitation", True)
            logger.warning(
                "Elicitation: enable_write_tools AND disable_elicitation both set — "
                "write tools enabled WITHOUT confirmation. Use with caution!"
            )

        # Check if client supports elicitation via MCP capabilities
        elif config.enable_write_tools:
            try:
                caps = context.message.params.capabilities
                if caps is not None and caps.elicitation is not None:
                    enable_write = True
                    await ctx.set_state("disable_elicitation", False)
                    logger.debug("Elicitation: client supports elicitation")
            except Exception as exc:
                logger.error("Elicitation: error checking capabilities — {}", exc)

            # HTTP transport: check headers/query params for bypass
            try:
                from fastmcp.server.dependencies import get_http_request

                request = get_http_request()
                if request.headers.get("X-Disable-Elicitation", "false").lower() == "true":
                    enable_write = True
                    await ctx.set_state("disable_elicitation", True)
                    logger.debug("Elicitation: X-Disable-Elicitation header detected")
                elif request.query_params.get("disable_elicitation", "false").lower() == "true":
                    enable_write = True
                    await ctx.set_state("disable_elicitation", True)
                    logger.debug("Elicitation: disable_elicitation query param detected")
            except Exception:
                pass  # Not HTTP transport or request not available

        if enable_write:
            await ctx.enable_components(tags={"write", "write_delete"}, components={"tool"})
            logger.debug("Elicitation: write tools enabled for this session")
        else:
            await ctx.disable_components(tags={"write", "write_delete"}, components={"tool"})
            logger.debug("Elicitation: write tools disabled (no support detected)")

        return result  # type: ignore[return-value]


async def elicitation_handler(message: str, ctx: Context) -> ElicitResult:
    """Prompt user for confirmation before write operations."""
    if await ctx.get_state("disable_elicitation") is True:
        logger.debug("Elicitation: auto-accepting (elicitation disabled for this client)")
        return ElicitResult(action="accept")

    logger.debug("Elicitation: prompting user — {}", message)
    result = await ctx.elicit(message, response_type=None)
    match result:
        case AcceptedElicitation():
            return ElicitResult(action="accept")
        case DeclinedElicitation():
            return ElicitResult(action="decline")
        case CancelledElicitation():
            return ElicitResult(action="cancel")
        case _:
            return ElicitResult(action="cancel")
