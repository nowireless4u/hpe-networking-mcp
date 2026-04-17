"""Elicitation middleware and handler for write tool confirmation.

The ElicitationMiddleware runs at session init to enable write tools
based on config flags and detect client elicitation support.

The elicitation_handler function is called by individual write tools
to get user confirmation. Behavior depends on config and client:
- DISABLE_ELICITATION=true: auto-accept, no confirmation
- Client supports elicitation: show confirmation prompt dialog
- Client lacks elicitation: decline and instruct AI to ask user in chat
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

        try:
            config = ctx.lifespan_context.get("config")
        except Exception:
            config = None

        if config is None:
            return result  # type: ignore[return-value]

        mist_write = config.enable_mist_write_tools
        central_write = config.enable_central_write_tools
        clearpass_write = config.enable_clearpass_write_tools
        any_write = mist_write or central_write or clearpass_write

        if not any_write:
            return result  # type: ignore[return-value]

        # Determine confirmation mode
        if config.disable_elicitation:
            await ctx.set_state("elicitation_mode", "disabled")
            logger.warning("Elicitation: DISABLE_ELICITATION=true — write tools will execute without confirmation")
        else:
            client_supports = False
            try:
                caps = context.message.params.capabilities
                if caps is not None and caps.elicitation is not None:
                    client_supports = True
            except Exception:
                pass

            if client_supports:
                await ctx.set_state("elicitation_mode", "prompt")
                logger.debug("Elicitation: client supports elicitation prompts")
            else:
                await ctx.set_state("elicitation_mode", "chat_confirm")
                logger.info(
                    "Elicitation: client does not support elicitation — "
                    "write tools will require AI to confirm with user in chat"
                )

        # Enable write tools
        if mist_write:
            await ctx.enable_components(tags={"mist_write", "mist_write_delete"}, components={"tool"})
        if central_write:
            await ctx.enable_components(tags={"central_write_delete"}, components={"tool"})
        if clearpass_write:
            await ctx.enable_components(tags={"clearpass_write_delete"}, components={"tool"})
        logger.info(
            "Elicitation: write tools enabled (mist=%s, central=%s, clearpass=%s)",
            mist_write,
            central_write,
            clearpass_write,
        )

        return result  # type: ignore[return-value]


async def elicitation_handler(message: str, ctx: Context) -> ElicitResult:
    """Get user confirmation before a write operation.

    Returns:
        ElicitResult with action "accept", "decline", or "cancel".
        On "decline" when chat confirmation is needed, the calling tool
        should return a confirmation request message to the AI.
    """
    mode = await ctx.get_state("elicitation_mode")

    # DISABLE_ELICITATION=true — skip all confirmation
    if mode == "disabled":
        logger.debug("Elicitation: auto-accepting (disabled) — {}", message)
        return ElicitResult(action="accept")

    # Client supports elicitation — show prompt dialog
    if mode == "prompt":
        try:
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
        except Exception:
            logger.warning("Elicitation: prompt failed, falling through to chat confirm")

    # Client lacks elicitation — tell AI to ask the user in chat
    logger.debug("Elicitation: chat confirmation required — {}", message)
    return ElicitResult(action="decline")
