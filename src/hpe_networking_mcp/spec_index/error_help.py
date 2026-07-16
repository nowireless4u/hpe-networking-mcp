"""Reactive enrichment for failed tool calls (spec-index-backed).

When a tool call fails with a non-2xx status, append the API's *documented*
meaning of that status code — so the model learns what ``429`` / ``403`` / ``409``
mean instead of retrying blind — and, for input errors (``400`` / ``422``) on the
opaque-body config/write tools, the legal body field set. Grounded in the same
spec-index that powers ``get_schema``; degrades to ``None`` (no enrichment) when
the index is absent or the tool/platform isn't resolvable.

This is the reactive half of the enrichment design: ``get_schema`` helps a model
that consults it first; this catches the model that guessed and hit an error —
the failure loop behind the AP-rename report.
"""

from __future__ import annotations

from hpe_networking_mcp.spec_index.query import get_spec_index
from hpe_networking_mcp.spec_index.tool_schema import payload_schema_for_tool

_PLATFORMS = ("mist", "central", "greenlake", "clearpass", "apstra", "axis", "aos8", "uxi", "edgeconnect")
_INPUT_ERROR_CODES = (400, 422)
_MAX_FIELDS_SHOWN = 60


def _platform_of(tool_name: str) -> str | None:
    for p in _PLATFORMS:
        if tool_name.startswith(p + "_"):
            return p
    return None


def _coerce_code(status_code: object) -> int | None:
    if isinstance(status_code, bool):
        return None
    if isinstance(status_code, int):
        return status_code
    try:
        return int(str(status_code))
    except (TypeError, ValueError):
        return None


def reactive_hint(tool_name: str, status_code: object) -> str | None:
    """A one-line ``[spec-index]`` enrichment for a failed call, or ``None``.

    Args:
        tool_name: The tool that failed (platform inferred from its prefix).
        status_code: The upstream/validation status (int or str).
    """
    if not tool_name:
        return None
    code = _coerce_code(status_code)
    if code is None or 200 <= code < 300:
        return None
    platform = _platform_of(tool_name)
    if platform is None:
        return None
    idx = get_spec_index()
    if not idx.available:
        return None

    parts: list[str] = []
    desc = idx.response_description(platform, str(code))
    if desc:
        parts.append(f"API documents {code}: {desc.strip()}")

    if code in _INPUT_ERROR_CODES:
        try:
            schema = payload_schema_for_tool(tool_name)
        except Exception:
            schema = None
        if schema and schema.get("fields"):
            names = [f["name"] for f in schema["fields"]][:_MAX_FIELDS_SHOWN]
            parts.append("valid body fields: " + ", ".join(names))

    if not parts:
        return None
    return "  [spec-index] " + " | ".join(parts)
