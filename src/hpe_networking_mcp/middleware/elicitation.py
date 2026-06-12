"""Elicitation middleware and handler for write tool confirmation.

The ElicitationMiddleware runs at session init to enable write tools
based on config flags and detect client elicitation support.

The elicitation_handler function is called by individual write tools
to get user confirmation. Behavior depends on config and client:
- DISABLE_ELICITATION=true: auto-accept, no confirmation
- Client supports elicitation: show confirmation prompt dialog
- Client lacks elicitation: decline and instruct AI to ask user in chat
"""

import json as _json

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
from mcp.shared.exceptions import McpError

# Normalized suffixes whose VALUES are redacted from confirmation-prompt
# parameter summaries. Keys are normalized (lowercased, separators stripped)
# before matching, so ``api_key`` / ``apiKey`` / ``api-key`` all redact; the
# suffix match catches compound names (``clientSecret``, ``refreshToken``,
# ``radiusSharedSecret``). Over-redaction is acceptable; leaking is not.
_SENSITIVE_KEY_SUFFIXES = (
    "password",
    "secret",
    "token",
    "key",
    "psk",
    "passphrase",
    "community",
    "credential",
    "credentials",
)
_PARAM_SUMMARY_MAX_LEN = 300


def _is_sensitive_key(key: str) -> bool:
    """True when a (normalized) parameter key names secret material."""
    normalized = "".join(ch for ch in key.lower() if ch.isalnum())
    return any(normalized == suffix or normalized.endswith(suffix) for suffix in _SENSITIVE_KEY_SUFFIXES)


def _sanitized_param_summary(params: dict | None) -> str:
    """Render a compact, redacted view of invocation params for the prompt.

    The human must see WHAT they are approving (target IDs, payload fields),
    not just the tool name — but never secret values, and never unbounded
    payload dumps. Sensitive keys are redacted by name at any nesting depth,
    the bookkeeping ``confirmed`` flag is dropped, and the rendering is
    length-capped.
    """
    if not params:
        return "(no parameters)"

    def scrub(value):
        if isinstance(value, dict):
            return {k: ("***" if _is_sensitive_key(k) else scrub(v)) for k, v in value.items() if k != "confirmed"}
        if isinstance(value, list):
            return [scrub(v) for v in value]
        return value

    rendered = _json.dumps(scrub(params), separators=(", ", ": "), ensure_ascii=False, default=str)
    if len(rendered) > _PARAM_SUMMARY_MAX_LEN:
        rendered = rendered[: _PARAM_SUMMARY_MAX_LEN - 1] + "…"
    return rendered


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
        apstra_write = config.enable_apstra_write_tools
        axis_write = config.enable_axis_write_tools
        aos8_write = config.enable_aos8_write_tools
        uxi_write = config.enable_uxi_write_tools
        any_write = (
            mist_write or central_write or clearpass_write or apstra_write or axis_write or aos8_write or uxi_write
        )

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
        if apstra_write:
            await ctx.enable_components(tags={"apstra_write", "apstra_write_delete"}, components={"tool"})
        if axis_write:
            await ctx.enable_components(tags={"axis_write", "axis_write_delete"}, components={"tool"})
        if aos8_write:
            await ctx.enable_components(tags={"aos8_write", "aos8_write_delete"}, components={"tool"})
        if uxi_write:
            await ctx.enable_components(tags={"uxi_write", "uxi_write_delete"}, components={"tool"})
        logger.info(
            "Elicitation: write tools enabled (mist=%s, central=%s, clearpass=%s, apstra=%s, axis=%s, aos8=%s, uxi=%s)",
            mist_write,
            central_write,
            clearpass_write,
            apstra_write,
            axis_write,
            aos8_write,
            uxi_write,
        )

        return result  # type: ignore[return-value]


async def _resolve_elicitation_mode(ctx: Context) -> str:
    """Resolve the active elicitation mode, robust to code mode.

    ``ElicitationMiddleware.on_initialize`` stores the mode in FastMCP
    *request-scoped* state. In code mode a write tool runs inside a **nested**
    ``call_tool`` context dispatched from the Monty sandbox; that context does
    not inherit the ``initialize`` request's state, so ``get_state`` returns
    ``None``. Left unhandled, a ``None`` mode meant the tool never surfaced a
    prompt yet still reported ``"Action declined by user."`` — a decline the
    user never made (the AI then spins, believing it was vetoed).

    When state is missing we re-derive the mode from ``config`` (always
    reachable via ``lifespan_context``) and default to ``chat_confirm``.
    NOTE: ``elicit()`` DOES round-trip from the code-mode sandbox (verified
    live, 2026-06-03 — #414's contrary premise was false); the universal
    gate (:func:`confirm_gated_invoke`) therefore attempts a real prompt
    first regardless of stored mode, and only falls back to chat-confirm
    when the prompt raises. This resolver remains for the legacy inline
    path and the DISABLE_ELICITATION check.

    Args:
        ctx: FastMCP context.

    Returns:
        One of ``"disabled"``, ``"prompt"``, or ``"chat_confirm"``.
    """
    mode = await ctx.get_state("elicitation_mode")
    if mode in ("disabled", "prompt", "chat_confirm"):
        return mode  # type: ignore[return-value]

    try:
        config = ctx.lifespan_context.get("config")
    except Exception:
        config = None
    resolved = "disabled" if (config is not None and config.disable_elicitation) else "chat_confirm"
    await ctx.set_state("elicitation_mode", resolved)
    logger.debug("Elicitation: mode state absent (code mode?) — resolved to {}", resolved)
    return resolved


async def confirm_write(
    ctx: Context,
    message: str,
    *,
    chat_confirm_hint: str | None = None,
) -> dict | None:
    """High-level write-tool confirmation helper.

    Most write tools were carrying nearly-identical ``_confirm`` helpers that
    wrapped :func:`elicitation_handler` and turned the returned action into the
    canonical ``{"status": ..., "message": ...}`` dict shape. This helper
    consolidates that boilerplate (#148).

    Args:
        ctx: FastMCP context.
        message: Human-readable description of what the tool is about to do.
            Passed verbatim to the elicitation prompt.
        chat_confirm_hint: Optional replacement for the default "call again
            with confirmed=true" message returned when the client cannot
            present an elicitation prompt. Useful for tools whose parameter
            name isn't ``confirmed``.

    Returns:
        ``None`` if the user accepted (or elicitation is disabled) — caller
        proceeds. A dict with ``status`` of ``confirmation_required``,
        ``declined``, or ``cancelled`` if not — caller should return the dict
        as the tool result.
    """
    result = await elicitation_handler(message=message, ctx=ctx)
    if result.action == "accept":
        return None
    if result.action == "cancel":
        return {"status": "cancelled", "message": "Action cancelled by user."}
    # decline
    mode = await ctx.get_state("elicitation_mode")
    if mode == "chat_confirm":
        hint = chat_confirm_hint or (
            f"{message} — please confirm with the user before proceeding, then "
            "call this tool again with confirmed=true."
        )
        return {"status": "confirmation_required", "message": hint}
    return {"status": "declined", "message": "Action declined by user."}


async def confirm_gated_invoke(
    ctx: Context,
    description: str,
    params: dict | None,
) -> dict | None:
    """Universal confirmation gate for ``requires_confirmation`` tools.

    Called from the ``<platform>_invoke_tool`` dispatch chokepoint — the path
    BOTH code mode and dynamic mode use — so destructive-tool confirmation is
    structural rather than per-tool (closes the #415 honor-system bypass and
    the #416 ungated-tool class).

    The decision sequence, per the agreed design:

    1. ``DISABLE_ELICITATION=true`` → auto-accept (operator opt-out).
    2. Attempt a REAL ``ctx.elicit()`` prompt — it round-trips transparently
       from the code-mode sandbox (verified live; #414's contrary premise was
       false). Accept proceeds; decline/cancel return structured results.
    3. Only when the prompt RAISES (client genuinely cannot present one) is
       ``confirmed=true`` honored as the popup-less chat fallback. An AI
       cannot self-authorize while a human-facing prompt is available.

    Args:
        ctx: FastMCP context of the invoke call.
        description: Human-readable description of the tool invocation.
        params: The raw params dict passed to the invoke (read-only; the
            ``confirmed`` flag is consumed from here for the fallback path).

    Returns:
        ``None`` when the invocation may proceed; otherwise a structured
        ``{"status": "confirmation_required" | "declined" | "cancelled", ...}``
        dict the dispatcher returns as the tool result.
    """
    try:
        config = ctx.lifespan_context.get("config")
    except Exception:
        config = None
    if config is not None and config.disable_elicitation:
        logger.debug("Gate: auto-accepting (DISABLE_ELICITATION) — {}", description)
        return None

    param_summary = _sanitized_param_summary(params)
    prompt = f"Confirm: {description}\nParams: {param_summary}"
    try:
        result = await ctx.elicit(prompt, response_type=None)
    except McpError as e:
        # Only the specific no-capability signal opens the fallback path:
        # "Elicitation not supported" / METHOD_NOT_FOUND (verified against
        # fastmcp). Every other MCP-layer error (transport failure, malformed
        # elicitation response, framework bug surfaced as McpError) fails
        # CLOSED below, exactly like non-MCP failures.
        error = getattr(e, "error", None)
        code = getattr(error, "code", None)
        message = (getattr(error, "message", None) or str(e)).lower()
        is_no_capability = code == -32601 or "elicitation not supported" in message
        if not is_no_capability:
            logger.error(
                "Gate: MCP-layer elicitation failure (code={}, {}) — failing closed for {}",
                code,
                message[:120],
                description,
            )
            return {
                "status": "confirmation_unavailable",
                "message": (
                    f"{description} requires user confirmation, but the confirmation prompt failed "
                    "at the MCP layer. The action was NOT performed. Retry later, or have the "
                    "operator set DISABLE_ELICITATION=true if confirmations must be bypassed "
                    "deliberately."
                ),
            }
        # ONLY here does confirmed=true carry authority — the human-in-chat fallback.
        if params and params.get("confirmed") is True:
            logger.info("Gate: client lacks elicitation — honoring confirmed=true for {}", description)
            return None
        return {
            "status": "confirmation_required",
            "message": (
                f"{description} requires user confirmation and this client cannot show a "
                f"confirmation prompt. Params: {param_summary}. Confirm with the user in "
                "chat, then call again with confirmed=true in params."
            ),
        }
    except Exception as e:
        # Any OTHER failure (handler crash, serialization bug, framework
        # regression) is NOT a license to skip confirmation — fail closed.
        # confirmed=true is deliberately not honored here: the gate only
        # opens when it knows the fallback path is legitimate.
        logger.error(
            "Gate: elicitation failed unexpectedly ({}: {}) — failing closed for {}", type(e).__name__, e, description
        )
        return {
            "status": "confirmation_unavailable",
            "message": (
                f"{description} requires user confirmation, but the confirmation prompt failed "
                f"unexpectedly ({type(e).__name__}). The action was NOT performed. Retry later, "
                "or have the operator set DISABLE_ELICITATION=true if confirmations must be "
                "bypassed deliberately."
            ),
        }

    match result:
        case AcceptedElicitation():
            return None
        case DeclinedElicitation():
            return {"status": "declined", "message": "Action declined by user."}
        case CancelledElicitation():
            return {"status": "cancelled", "message": "Action cancelled by user."}
        case _:
            return {"status": "cancelled", "message": "Action cancelled (unrecognized elicitation result)."}


async def elicitation_handler(message: str, ctx: Context) -> ElicitResult:
    """Get user confirmation before a write operation.

    Returns:
        ElicitResult with action "accept", "decline", or "cancel".
        On "decline" when chat confirmation is needed, the calling tool
        should return a confirmation request message to the AI.
    """
    mode = await _resolve_elicitation_mode(ctx)

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
            # The prompt never reached the user — do NOT report a decline they
            # never made. Degrade to chat-confirm so the caller returns a
            # confirmation_required result and the AI confirms in chat.
            logger.warning("Elicitation: prompt failed, degrading to chat confirm")
            await ctx.set_state("elicitation_mode", "chat_confirm")

    # Client lacks elicitation (or prompt failed to surface) — tell the AI to
    # ask the user in chat. Callers map this decline to confirmation_required
    # by re-reading the (now chat_confirm) mode.
    logger.debug("Elicitation: chat confirmation required — {}", message)
    return ElicitResult(action="decline")
