"""FastMCP middleware that wires PII tokenization into the tool-call lifecycle.

Two-sided middleware:

1. **Inbound (request)**: walk ``arguments`` for any ``[[KIND:uuid]]``
   tokens the AI passed in, replace them with plaintext from the
   session keymap before the call hits the platform tool. Unknown
   tokens (e.g. references from a different session) cause the call
   to fail with a JSON-RPC error rather than passing literal bracket
   text downstream.

2. **Outbound (response)**: walk the returned ``ToolResult`` —
   ``structured_content`` and any JSON-shaped text content blocks —
   and apply MAC normalization (always-on) and PII tokenization (when
   the toggle is enabled).

The middleware is a no-op when neither tokenization nor normalization
applies (e.g. tool returned no JSON-shaped content) — overhead on a
quiet path is just the dict-walk recursion.

Audit logging happens inside the tokenizer; the middleware adds one
event per tool call summarizing how many tokens were materialized
and how many were detokenized, again without revealing values.
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

import mcp.types
from fastmcp.server.middleware import Middleware, MiddlewareContext
from fastmcp.tools.tool import ToolResult
from loguru import logger
from mcp.types import TextContent

from hpe_networking_mcp.redaction.tokenizer import Tokenizer
from hpe_networking_mcp.redaction.walker import (
    detokenize_arguments,
    iter_kinds_in_string,
    tokenize_response,
)

if TYPE_CHECKING:
    from hpe_networking_mcp.redaction.token_store import TokenStore


# A short, low-entropy session ID prefix shown in audit logs so engineers
# can correlate events across log lines without exposing the full ID.
_SESSION_ID_LOG_LEN = 12


class PIITokenizationMiddleware(Middleware):
    """Bidirectional PII middleware.

    Args:
        token_store: The shared per-process ``TokenStore`` (created in
            the FastMCP lifespan handler). One keymap per Mcp-Session-Id
            is allocated lazily inside.
        enabled: If False, the middleware applies *only* MAC
            normalization on outbound responses and skips both
            tokenization and detokenization. Lets operators leave the
            middleware wired in without committing to tokenization.
    """

    def __init__(self, token_store: TokenStore, *, enabled: bool) -> None:
        self._store = token_store
        self._enabled = enabled

    @property
    def enabled(self) -> bool:
        return self._enabled

    async def on_call_tool(
        self,
        context: MiddlewareContext[mcp.types.CallToolRequestParams],
        call_next,
    ) -> ToolResult:
        session_id = self._resolve_session_id(context)
        tool_name = context.message.name

        # --- Inbound: detokenize arguments ---
        if self._enabled and session_id:
            inbound_keymap = self._store.get(session_id)
            if inbound_keymap is not None and context.message.arguments:
                inbound_tokenizer = Tokenizer(
                    inbound_keymap,
                    session_id=session_id,
                    max_entries=self._store.max_entries_per_session,
                )
                new_args, unknown = detokenize_arguments(context.message.arguments, inbound_tokenizer)
                if unknown:
                    logger.warning(
                        "pii.unknown_inbound_tokens session={} tool={} tokens={}",
                        session_id[:_SESSION_ID_LOG_LEN],
                        tool_name,
                        sorted(set(unknown)),
                    )
                    return _make_unknown_token_error(unknown)

                if new_args is not context.message.arguments:
                    logger.info(
                        "pii.detokenize session={} tool={} kinds={}",
                        session_id[:_SESSION_ID_LOG_LEN],
                        tool_name,
                        sorted(_kinds_used_in_args(context.message.arguments)),
                    )
                    new_message = context.message.model_copy(update={"arguments": new_args})
                    context = context.copy(message=new_message)

        # --- Forward to next middleware / handler ---
        result = await call_next(context)

        # --- Outbound: normalize MACs + (optionally) tokenize PII ---
        # MAC normalization runs even when ``self._enabled`` is False;
        # tokenization requires both the toggle on AND a session ID.
        outbound_tokenizer: Tokenizer | None = None
        if self._enabled and session_id:
            outbound_keymap = self._store.get_or_create(session_id)
            outbound_tokenizer = Tokenizer(
                outbound_keymap,
                session_id=session_id,
                max_entries=self._store.max_entries_per_session,
            )

        return _process_outbound_result(result, outbound_tokenizer)

    @staticmethod
    def _resolve_session_id(
        context: MiddlewareContext[mcp.types.CallToolRequestParams],
    ) -> str | None:
        """Return the Mcp-Session-Id for this call, or None if unavailable."""
        fastmcp_ctx = context.fastmcp_context
        if fastmcp_ctx is None:
            return None
        try:
            return fastmcp_ctx.session_id
        except Exception:  # pragma: no cover — defensive against API shifts
            return None


# ---------------------------------------------------------------------------
# Helpers — outbound result transformation
# ---------------------------------------------------------------------------


def _process_outbound_result(
    result: ToolResult,
    tokenizer: Tokenizer | None,
) -> ToolResult:
    """Apply MAC normalization + (optional) tokenization to a ToolResult."""
    if not isinstance(result, ToolResult):
        # Defensive: some FastMCP middleware returns raw values during
        # error paths. Pass through unchanged.
        return result

    new_structured = _process_structured(result.structured_content, tokenizer)
    new_content = _process_content_blocks(result.content, tokenizer)

    structured_changed = new_structured is not result.structured_content
    content_changed = new_content is not result.content

    if not structured_changed and not content_changed:
        return result

    return ToolResult(
        content=new_content,
        structured_content=new_structured,
        meta=result.meta,
    )


def _process_structured(
    structured: dict | None,
    tokenizer: Tokenizer | None,
) -> dict | None:
    if structured is None:
        return None
    walked = tokenize_response(structured, tokenizer)
    return walked if isinstance(walked, dict) else structured


def _process_content_blocks(
    blocks: list,
    tokenizer: Tokenizer | None,
) -> list:
    """Walk ``content`` blocks. For each TextContent, try JSON-parse the
    text; if it parses, walk and re-serialize. Otherwise leave as-is.

    Non-text blocks (image, audio, embedded resources) pass through
    unchanged — those payloads aren't structured customer data in this
    server's context.
    """
    out: list = []
    changed = False
    for block in blocks:
        if isinstance(block, TextContent) and block.text:
            new_text = _process_text_block(block.text, tokenizer)
            if new_text is not block.text:
                out.append(TextContent(type="text", text=new_text))
                changed = True
            else:
                out.append(block)
        else:
            out.append(block)
    return out if changed else blocks


def _process_text_block(text: str, tokenizer: Tokenizer | None) -> str:
    """Parse text as JSON; if it parses, walk + re-serialize; else return as-is.

    Mist / Central / etc. tools serialize structured responses with
    ``json.dumps(data)`` so most text blocks ARE JSON. The free-text
    sweep would still catch in-text secrets even when the block is
    plain prose, but we apply it only on the JSON-parsed path so we
    don't re-tokenize values that the structured walker already
    handled.
    """
    try:
        parsed = json.loads(text)
    except (ValueError, TypeError):
        return text

    if not isinstance(parsed, (dict, list)):
        # JSON scalar — no structure to walk
        return text

    walked = tokenize_response(parsed, tokenizer)
    return json.dumps(walked)


# ---------------------------------------------------------------------------
# Helpers — inbound argument inspection
# ---------------------------------------------------------------------------


def _kinds_used_in_args(arguments: dict) -> set[str]:
    """Return the set of token KIND strings present in any string arg.

    Used for the audit log entry summarizing what kinds of tokens the
    AI dereferenced for this call. We log kinds, not full tokens, so an
    operator can see "model used PSK and SITE tokens here" without the
    log itself becoming sensitive.
    """
    kinds: set[str] = set()

    def _scan(value: object) -> None:
        if isinstance(value, str):
            kinds.update(iter_kinds_in_string(value))
        elif isinstance(value, dict):
            for v in value.values():
                _scan(v)
        elif isinstance(value, list):
            for v in value:
                _scan(v)

    _scan(arguments)
    return kinds


def _make_unknown_token_error(unknown_tokens: list[str]) -> ToolResult:
    """Build a ToolResult error when the AI references unknown tokens.

    The model gets a short string explanation in the tool's content
    block. We deliberately list the unknown tokens (they're not
    sensitive — they don't map to anything) so the model can correct
    itself if it copy-pasted from a stale conversation.
    """
    distinct = sorted(set(unknown_tokens))
    msg = (
        "Tokenization error: the following tokens are not valid in the "
        "current session and cannot be detokenized. They may be from a "
        f"previous session that has ended: {distinct}. "
        "Re-fetch the source data so a fresh tokenization can be issued."
    )
    return ToolResult(content=[TextContent(type="text", text=msg)])
