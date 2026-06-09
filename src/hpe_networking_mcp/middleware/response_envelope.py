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

import json
from typing import Any

import mcp.types
from fastmcp.server.middleware import Middleware, MiddlewareContext
from fastmcp.tools.tool import ToolResult
from loguru import logger
from mcp.types import TextContent

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

# Discovery tools that ship with their own ``x-fastmcp-wrap-result`` output
# schema requiring a top-level ``result`` field. The envelope would wrap them
# as ``{"ok": ..., "data": {"result": ...}}`` which fails output validation
# because the OUTER envelope has no top-level ``result``. Bypass these tools
# entirely — they already return a uniform shape the client expects.
# (Fixes #293, root cause of the "Mist intermittent" report from Mike
# Gallagher 2026-05-12 / issue #302.)
_NO_ENVELOPE_TOOLS: frozenset[str] = frozenset(
    {
        "tags",
        "search",
        "get_schema",
        "skills_list",
        "skills_load",
        # GenerativeUI provider (MCP_ENABLE_GENERATIVE_UI). Both tools carry an
        # ``x-fastmcp-wrap-result`` output schema requiring a top-level ``result``
        # key; wrapping them in the envelope strips ``result`` and the tool's own
        # output validation fails with "'result' is a required property" — the same
        # failure mode as the discovery tools above (#293/#302). ``generate_prefab_ui``
        # also returns a ``$prefab`` UI view (caught by the marker bypass below), but
        # naming it here covers its non-UI/error returns too. Names are the
        # GenerativeUI defaults — keep in sync if the provider is constructed with
        # custom tool_name / components_tool_name.
        "generate_prefab_ui",
        "search_prefab_components",
    }
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


def _payload_from_content(content: list | None) -> Any:
    """Recover a tool's payload from its content blocks.

    FastMCP leaves ``structured_content`` as ``None`` for a tool annotated
    ``-> Any`` that returns a **non-dict** value — most importantly a bare
    JSON array, the shape ~189 generated ``mist_list_*`` tools and every
    ``<platform>_invoke_tool`` meta-tool produce. (A dict return *does*
    populate ``structured_content``; a list return under ``-> Any`` does
    not.) The payload is still serialized into the content blocks as JSON
    text, so recover it here — otherwise the envelope's ``data`` is
    ``null`` and the AI never sees the result. See issue #327.

    Two-pass recovery:

    1. First pass — find a JSON-parseable block (preserves dict/list
       payloads from ``-> Any`` tools that returned a non-dict, plus
       structured returns from ``-> dict | list | str`` tools).
    2. Fallback — if no block parses as JSON, return the first non-empty
       text block as a raw string. This preserves bare-string returns —
       Mermaid source from ``central_get_scope_diagram``, error fallback
       strings from tools declared ``-> dict | list | str``, etc. — that
       previously vanished into ``data: null`` (issue #362).

    Returns ``None`` only when no text block carries any content.
    """
    # First pass: any JSON-parseable block wins (preserves dict/list payloads).
    for block in content or []:
        if isinstance(block, TextContent) and block.text:
            try:
                return json.loads(block.text)
            except (ValueError, TypeError):
                continue
    # Second pass: no JSON found. Fall back to the first non-empty text
    # block so bare-string returns survive instead of becoming data: null.
    for block in content or []:
        if isinstance(block, TextContent) and block.text:
            return block.text
    return None


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

        # Discovery tools (``tags`` / ``search`` / ``get_schema`` / ``skills_list``
        # / ``skills_load``) ship with their own ``x-fastmcp-wrap-result`` schema
        # requiring a top-level ``result`` field. Wrapping them in the envelope
        # produces ``{"ok": ..., "data": {"result": ...}}``, which fails the
        # discovery tool's output validation. Pass them through unmodified —
        # they already speak a uniform shape that AI clients understand.
        # See issue #293 + #302 for the root-cause history.
        if tool_name in _NO_ENVELOPE_TOOLS:
            logger.debug("response_envelope: {} is a discovery tool, pass-through", tool_name)
            return result  # type: ignore[return-value]

        # Determine the raw structured payload, if any.
        raw = getattr(result, "structured_content", None)

        # MCP-Apps / Prefab UI tools (FastMCP ``FileUpload`` provider's
        # ``file_manager`` / ``store_files``, etc.) return a UI *view spec*
        # under a top-level ``$prefab`` key in ``structured_content``. The
        # host's renderer reads ``structured_content`` directly to draw the
        # interface; wrapping it in the envelope buries ``$prefab`` under
        # ``data`` and the renderer hangs on "waiting for content". Detect the
        # marker (not a hardcoded tool name) so any Prefab tool passes through
        # untouched.
        if isinstance(raw, dict) and "$prefab" in raw:
            logger.debug("response_envelope: {} is a Prefab UI tool, pass-through", tool_name)
            return result  # type: ignore[return-value]

        # FastMCP only populates ``structured_content`` for dict-shaped
        # returns from ``-> Any`` tools; a bare JSON array (every
        # ``mist_list_*`` tool, every ``<platform>_invoke_tool`` dispatch
        # to one) leaves it ``None`` with the payload stranded in the
        # content blocks. Recover it so ``data`` carries the real result
        # instead of ``null``. See issue #327.
        if raw is None:
            raw = _payload_from_content(result.content)

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
