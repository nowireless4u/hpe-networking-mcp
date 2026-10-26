"""Reactive spec-index enrichment for RAISED ``ToolError``s (issue #638).

Platform tools that follow the ToolError contract (e.g. Mist's ``_client``)
**raise** ``ToolError({"status_code": N, "message": ...})`` on a non-2xx
upstream response. Two existing hooks already enrich errors from the spec-index:
``ResponseEnvelopeMiddleware`` (tools that *return* a non-2xx envelope) and
``ValidationCatchMiddleware`` (422 ``ValidationError``). A **raised** ToolError
hits neither — so it reaches the model (or the code-mode sandbox) with only its
bare message and no ``[spec-index]`` hint. That is the gap Zach's Mist SLE 404
fell through.

This middleware closes it: it catches ``ToolError`` at ``on_call_tool`` and
appends ``reactive_hint(tool_name, status_code)`` — the API's *documented*
meaning of the status code (+ the legal body field set for 400/422) — so a model
that guessed and hit an error learns to self-correct instead of retrying blind.
Best-effort and non-destructive: the original ToolError (type, status_code,
message) is preserved; only the message string gains a suffix, and only when the
spec-index actually has something to say.
"""

from __future__ import annotations

from typing import Any

import mcp.types
from fastmcp.exceptions import ToolError
from fastmcp.server.middleware import Middleware, MiddlewareContext
from fastmcp.tools.tool import ToolResult


class ToolErrorEnrichMiddleware(Middleware):
    """Append spec-index status guidance to raised ``ToolError``s."""

    async def on_call_tool(
        self,
        context: MiddlewareContext[mcp.types.CallToolRequestParams],
        call_next: Any,
    ) -> ToolResult:
        try:
            return await call_next(context)  # type: ignore[no-any-return]
        except ToolError as err:
            tool_name = getattr(context.message, "name", "") or ""
            enriched = self._enriched(tool_name, err)
            if enriched is not None:
                raise enriched from err
            raise

    @staticmethod
    def _enriched(tool_name: str, err: ToolError) -> ToolError | None:
        """Return a new ToolError with the spec-index hint appended, or ``None``.

        Only structured ``{"status_code", "message"}`` payloads are enrichable;
        string-only ToolErrors carry no status code to look up and pass through.
        Skips messages already carrying a ``[spec-index]`` suffix (idempotent).
        """
        payload = err.args[0] if err.args else None
        if not isinstance(payload, dict):
            return None
        message = payload.get("message")
        if not isinstance(message, str) or "[spec-index]" in message:
            return None
        try:
            from hpe_networking_mcp.spec_index.error_help import reactive_hint

            hint = reactive_hint(tool_name, payload.get("status_code"))
        except Exception:  # pragma: no cover - enrichment must never break dispatch
            hint = None
        if not hint:
            return None
        return ToolError({**payload, "message": message + hint})
