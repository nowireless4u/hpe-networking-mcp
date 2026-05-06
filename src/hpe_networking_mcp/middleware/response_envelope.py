"""Response envelope middleware — wraps tool responses in a uniform shape.

v3.0.0.0 scope: applies to **every tool** in the catalog. The v2.5.1.0
prototype was scoped to the 4 cross-platform tools (``health``,
``site_health_check``, ``site_rf_check``, ``manage_wlan_profile``) to
validate the pattern; Zach's OpenClaw + Qwen3 4B test (#246 reassessment
comment) confirmed the envelope worked for the small-local-model use case
that motivated v3 in the first place. Allowlist removed in v3.0.0.0.

Envelope shape::

    {
      "ok":       bool,           # success indicator
      "status":   int | None,     # HTTP status (200, 401, 503) or None
      "data":     Any,            # the actual payload — list, dict, or None
      "message":  str | None,     # human-readable summary; populated on errors
      "tool":     str,            # tool name
      "platform": str | None,     # "central" / "mist" / ... / None for cross-platform
    }

The middleware sits **innermost** in the chain so it wraps raw tool output
*before* retry / PII / elicitation / etc. process the response. Retry's
``_extract_status_code`` works equally on the envelope's ``status`` field
as it does on raw tool output's ``status_code`` / ``code`` / ``status``.

When a tool already returned a dict matching the envelope shape (e.g. a
tool that explicitly constructed and returned an envelope), the middleware
passes through without re-wrapping (idempotency check via ``_is_envelope_shape``).
"""

from __future__ import annotations

from typing import Any

import mcp.types
from fastmcp.server.middleware import Middleware, MiddlewareContext
from fastmcp.tools.tool import ToolResult
from loguru import logger

# Platform prefixes used to derive the ``platform`` envelope field. Cross-platform
# tools (those without one of these prefixes) end up with ``platform: null``.
_PLATFORM_PREFIXES: tuple[str, ...] = (
    "mist_",
    "central_",
    "greenlake_",
    "clearpass_",
    "apstra_",
    "axis_",
    "aos8_",
)

# Keys an existing envelope-shaped dict must contain (idempotency check).
_ENVELOPE_REQUIRED_KEYS: frozenset[str] = frozenset({"ok", "data", "tool"})

# Keys to inspect when extracting an HTTP status code from a raw tool result.
# Mirrors ``retry.py:_extract_status_code`` so the envelope's ``status`` field
# is populated consistently with what RetryMiddleware would see.
_STATUS_CODE_KEYS: tuple[str, ...] = ("status_code", "code", "http_status")


def _infer_platform(tool_name: str) -> str | None:
    """Derive ``platform`` from a tool name's prefix.

    Returns ``None`` for cross-platform tools (no prefix match).
    """
    for prefix in _PLATFORM_PREFIXES:
        if tool_name.startswith(prefix):
            return prefix.rstrip("_")
    return None


def _extract_status(raw: Any) -> int | None:
    """Best-effort HTTP-status extraction from a raw tool result.

    Looks for ``status_code`` / ``code`` / ``http_status`` at the top level.
    Returns ``None`` when the tool's response doesn't carry an HTTP status
    (most non-HTTP-bound tools).
    """
    if not isinstance(raw, dict):
        return None
    for key in _STATUS_CODE_KEYS:
        value = raw.get(key)
        if isinstance(value, int):
            return value
    return None


def _is_envelope_shape(value: Any) -> bool:
    """True when ``value`` is already an envelope dict (idempotency)."""
    return isinstance(value, dict) and _ENVELOPE_REQUIRED_KEYS.issubset(value.keys())


def _build_envelope(
    *,
    ok: bool,
    data: Any,
    status: int | None,
    message: str | None,
    tool: str,
    platform: str | None,
) -> dict[str, Any]:
    return {
        "ok": ok,
        "status": status,
        "data": data,
        "message": message,
        "tool": tool,
        "platform": platform,
    }


class ResponseEnvelopeMiddleware(Middleware):
    """Wrap every tool response in the uniform envelope shape.

    Position **innermost** in the middleware chain (last in the
    ``middleware=[...]`` list) so the wrap happens on raw tool output
    *before* retry / PII / elicitation see the response.

    v2.5.1.0 had an allowlist (``PROTOTYPE_TOOLS``); v3.0.0.0 removes it
    and the envelope applies fleet-wide. Tools that explicitly returned an
    envelope shape are still passed through via the idempotency check.
    """

    async def on_call_tool(
        self,
        context: MiddlewareContext[mcp.types.CallToolRequestParams],
        call_next,
    ) -> ToolResult:
        tool_name = context.message.name
        platform = _infer_platform(tool_name)
        result = await call_next(context)

        # Determine the raw structured payload, if any.
        raw = getattr(result, "structured_content", None)

        if raw is not None and _is_envelope_shape(raw):
            # Tool already returned an envelope — respect it.
            logger.debug("response_envelope: {} already enveloped, pass-through", tool_name)
            return result  # type: ignore[return-value]

        envelope = _build_envelope(
            ok=True,
            data=raw,
            status=_extract_status(raw),
            message=None,
            tool=tool_name,
            platform=platform,
        )

        logger.debug("response_envelope: wrapped {} (platform={})", tool_name, platform)

        return ToolResult(
            content=result.content,
            structured_content=envelope,
        )
