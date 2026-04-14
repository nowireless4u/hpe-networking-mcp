"""Elicitation middleware and handler for write tool confirmation.

The ElicitationMiddleware runs at session init to enable write tools
based on config flags. Write tools are always enabled when the config
says so — regardless of whether the client supports elicitation prompts.

The elicitation_handler function is called by individual write tools
to prompt the user for confirmation. If the client does not support
elicitation, it auto-accepts with a warning log.
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
        any_write = mist_write or central_write

        if not any_write:
            return result  # type: ignore[return-value]

        # Determine whether to auto-accept or prompt
        if config.disable_elicitation:
            await ctx.set_state("disable_elicitation", True)
            logger.warning("Elicitation: DISABLE_ELICITATION=true — write tools will execute without confirmation")
        else:
            # Check if client supports elicitation
            client_supports = False
            try:
                caps = context.message.params.capabilities
                if caps is not None and caps.elicitation is not None:
                    client_supports = True
            except Exception:
                pass

            if client_supports:
                await ctx.set_state("disable_elicitation", False)
                logger.debug("Elicitation: client supports elicitation prompts")
            else:
                # Client doesn't support elicitation — auto-accept
                await ctx.set_state("disable_elicitation", True)
                logger.info("Elicitation: client does not support elicitation, write tools will auto-accept")

        # Enable write tools — always, when config says enabled
        if mist_write:
            await ctx.enable_components(tags={"mist_write", "mist_write_delete"}, components={"tool"})
        if central_write:
            await ctx.enable_components(tags={"central_write_delete"}, components={"tool"})
        logger.info("Elicitation: write tools enabled (mist=%s, central=%s)", mist_write, central_write)

        return result  # type: ignore[return-value]


async def elicitation_handler(message: str, ctx: Context) -> ElicitResult:
    """Prompt user for confirmation before write operations.

    If the client supports elicitation, shows a confirmation prompt.
    If the client does not support elicitation or DISABLE_ELICITATION=true,
    auto-accepts the operation.
    """
    if await ctx.get_state("disable_elicitation") is True:
        logger.debug("Elicitation: auto-accepting — {}", message)
        return ElicitResult(action="accept")

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
        logger.warning("Elicitation: client cannot prompt, auto-accepting write operation")
        return ElicitResult(action="accept")
