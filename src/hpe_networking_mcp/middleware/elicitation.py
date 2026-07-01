"""Elicitation middleware and the universal confirmation gate.

``ElicitationMiddleware`` runs at session init to enable write tools
based on the per-platform ``ENABLE_<PLATFORM>_WRITE_TOOLS`` config flags.

``confirm_gated_invoke`` is the universal confirmation gate, called from
the ``<platform>_invoke_tool`` dispatch chokepoint for every tool whose
capability classification derives the ``requires_confirmation`` tag.
Behavior depends on config and client:
- DISABLE_ELICITATION=true: auto-accept, no confirmation
- Client supports elicitation: show confirmation prompt dialog
- Client lacks elicitation: instruct the AI to confirm with the user in
  chat, then honor ``confirmed=true`` on the retry (fallback path only)
"""

import json as _json

import mcp.types
from fastmcp import Context
from fastmcp.server.elicitation import (
    AcceptedElicitation,
    CancelledElicitation,
    DeclinedElicitation,
)
from fastmcp.server.middleware import Middleware, MiddlewareContext
from fastmcp.tools.tool import ToolResult
from loguru import logger
from mcp.shared.exceptions import McpError

from hpe_networking_mcp.middleware.response_envelope import _build_envelope
from hpe_networking_mcp.platforms._common.tool_registry import REGISTRIES, ToolSpec
from hpe_networking_mcp.redaction.safe_summary import is_sensitive_key as _is_sensitive_key

_PARAM_SUMMARY_MAX_LEN = 300


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


def _find_registry_spec(tool_name: str) -> ToolSpec | None:
    """Return the platform ``ToolSpec`` for a tool name, or ``None``.

    Only registry-managed **platform** tools live in ``REGISTRIES``. The
    per-platform meta-tools (``<platform>_list_tools`` / ``_get_tool_schema`` /
    ``_invoke_tool``), the code-mode ``execute`` + discovery tools, the
    cross-platform statics (``health`` / ``site_*`` / ``translate_*``) and the
    MCP-Apps tools are registered with ``@mcp.tool`` OUTSIDE the registry, so
    they return ``None`` here and are NOT gated by ``on_call_tool``. That is
    correct: ``_invoke_tool`` and the translate-apply tools carry their own
    in-body ``confirm_gated_invoke`` and dispatch the target via ``spec.func``
    directly (never re-entering middleware), so gating them here too would
    double-prompt; the rest are reads/discovery/sandbox and must not prompt.
    """
    for registry in REGISTRIES.values():
        spec = registry.get(tool_name)
        if spec is not None:
            return spec
    return None


class ElicitationMiddleware(Middleware):
    async def on_call_tool(
        self,
        context: MiddlewareContext[mcp.types.CallToolRequestParams],
        call_next,
    ) -> ToolResult:
        """Structural confirmation gate at the ``tools/call`` layer (#558).

        The ``<platform>_invoke_tool`` dispatcher gates its target, but a tool
        called DIRECTLY by name — which the code-mode sandbox allows and the
        ``execute`` description says is equivalent — never went through that
        dispatcher, so it bypassed confirmation entirely. This gates the direct
        path structurally: every registry ``ToolSpec`` whose classification
        requires confirmation (``requires_confirmation`` tag) — or is missing
        (``capability is None``, fail-closed) — prompts before it runs, exactly
        like the dispatcher. Non-registry infra tools pass through unchanged
        (see ``_find_registry_spec``), so ``invoke_tool`` / translate keep their
        single in-body gate and reads/discovery never prompt.
        """
        tool_name = getattr(context.message, "name", None)
        ctx = context.fastmcp_context
        spec = _find_registry_spec(tool_name) if tool_name else None

        if spec is not None and ctx is not None:
            # Same predicate as the _invoke_tool dispatcher: tag-driven, and
            # fail-closed on a registered-but-unclassified tool.
            needs_confirmation = "requires_confirmation" in spec.tags or spec.capability is None
            if needs_confirmation:
                params = dict(getattr(context.message, "arguments", None) or {})
                summary = (spec.description or spec.category or "no description")[:120]
                gate = await confirm_gated_invoke(
                    ctx,
                    f"{spec.platform} tool '{tool_name}' ({summary})",
                    params,
                )
                if gate is not None:
                    # Blocked — return the structured outcome as the tool result
                    # WITHOUT running the tool. We short-circuit before the inner
                    # ResponseEnvelopeMiddleware, so build the envelope here (as
                    # ValidationCatchMiddleware does).
                    envelope = _build_envelope(
                        ok=False,
                        data=gate,
                        status=403,
                        message=gate.get("message"),
                        tool=tool_name or "unknown",
                        platform=spec.platform,
                    )
                    return ToolResult(content=gate.get("message", ""), structured_content=envelope)

        return await call_next(context)  # type: ignore[no-any-return]

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
        greenlake_write = config.enable_greenlake_write_tools
        edgeconnect_write = config.enable_edgeconnect_write_tools
        any_write = (
            mist_write
            or central_write
            or clearpass_write
            or apstra_write
            or axis_write
            or aos8_write
            or uxi_write
            or greenlake_write
            or edgeconnect_write
        )

        if not any_write:
            return result  # type: ignore[return-value]

        if config.disable_elicitation:
            logger.warning("Elicitation: DISABLE_ELICITATION=true — gated tools will execute without confirmation")

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
        if greenlake_write:
            await ctx.enable_components(tags={"greenlake_write", "greenlake_write_delete"}, components={"tool"})
        if edgeconnect_write:
            await ctx.enable_components(tags={"edgeconnect_write", "edgeconnect_write_delete"}, components={"tool"})
        logger.info(
            "Elicitation: write tools enabled (mist=%s, central=%s, clearpass=%s, "
            "apstra=%s, axis=%s, aos8=%s, uxi=%s, greenlake=%s, edgeconnect=%s)",
            mist_write,
            central_write,
            clearpass_write,
            apstra_write,
            axis_write,
            aos8_write,
            uxi_write,
            greenlake_write,
            edgeconnect_write,
        )

        return result  # type: ignore[return-value]


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
    2. Attempt a REAL ``ctx.elicit()`` prompt with a REQUIRED ``approve``
       boolean schema — it round-trips transparently from the code-mode
       sandbox (verified live; #414's contrary premise was false). Only an
       explicit ``approve=true`` proceeds; decline/cancel/approve-false return
       structured results. The required field also closes a live safety gap:
       the old empty-schema (``response_type=None``) form was silently
       auto-accepted by some clients (Claude Desktop), letting writes run with
       no visible confirmation; a missing ``approve`` now fails closed.
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
        # Use a REQUIRED boolean response schema rather than the deprecated
        # ``response_type=None`` (empty-object) form. The empty schema is
        # rendered inconsistently by clients: some (e.g. Claude Desktop)
        # silently auto-ACCEPT it — so a gated write executes with no visible
        # confirmation — while others auto-cancel. A required ``approve`` field
        # forces the client to render a real dialog; and critically, a client
        # that auto-accepts with an EMPTY payload now fails schema validation
        # (``approve`` missing) → the ``except Exception`` below fails closed,
        # instead of silently proceeding. Only an explicit ``approve=true``
        # from a human proceeds.
        result = await ctx.elicit(
            prompt,
            # mypy can't bind `bool` to elicit's generic scalar overload `type[T]`
            # and falls back to the deprecated `response_type: None` overload;
            # the scalar form is correct and runtime-verified (schema requires a
            # boolean `value`; empty auto-accept raises ValidationError → fails
            # closed below). Hence the targeted ignore.
            bool,  # type: ignore[arg-type]
            response_title="Approve",
            response_description="Approve this action? Must be set to true to proceed.",
        )
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
        case AcceptedElicitation(data=True):
            return None
        case AcceptedElicitation():
            # Accepted the dialog but did NOT set approve=true (unchecked, or a
            # client that auto-accepts with a default-false payload) → treat as
            # a refusal, never a proceed.
            return {"status": "declined", "message": "Action not approved (approve was not set to true)."}
        case DeclinedElicitation():
            return {"status": "declined", "message": "Action declined by user."}
        case CancelledElicitation():
            return {"status": "cancelled", "message": "Action cancelled by user."}
        case _:
            return {"status": "cancelled", "message": "Action cancelled (unrecognized elicitation result)."}
