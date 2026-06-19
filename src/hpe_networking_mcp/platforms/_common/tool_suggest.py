"""Fuzzy "did you mean" tool-name suggestions for unknown-tool errors (#489).

When a model guesses a plausible-but-wrong tool name — e.g.
``central_list_sites`` when the real tool is ``central_get_sites`` — a bare
``Unknown tool`` string gives it nothing to self-correct from, so it either
loops on the identical call or gives up. This module turns that dead-end into
structured **result data**: a ranked list of real, registered tool names plus
the universal dispatch hint.

The suggestion is data, not an imperative. It carries no "call X first" prose
(skills-first is handled structurally elsewhere, #493) — the model consumes
the candidate list as an observation and self-corrects, which is the normal
agent loop.
"""

from __future__ import annotations

import difflib
import re

from hpe_networking_mcp.platforms._common.tool_registry import REGISTRIES

# fastmcp raises ``NotFoundError("Unknown tool: <name>")`` for an unresolved
# name; inside the code-mode sandbox that surfaces as a MontyError whose text
# still contains the phrase. The top-surface NotFoundError quotes the name
# (``Unknown tool: 'central_x'``) while the in-sandbox text does not, so the
# optional quote is tolerated. Tool names are ``[a-z0-9_]+``.
_UNKNOWN_TOOL_RE = re.compile(r"""Unknown tool:\s*['"]?([A-Za-z0-9_]+)""")

_FUZZY_CUTOFF = 0.6


def _name_to_platform() -> dict[str, str]:
    """Map every registered underlying tool name to its platform.

    Built fresh on each call so it reflects the live registry (tests mutate
    ``REGISTRIES``; the corpus is small enough that rebuilding is cheap).
    """
    out: dict[str, str] = {}
    for platform, reg in REGISTRIES.items():
        if platform == "_template":
            continue
        for name in reg:
            out[name] = platform
    return out


def _platform_from_name(name: str) -> str | None:
    """Best-effort platform from a tool name's prefix (``central_get_x`` -> ``central``)."""
    head = name.split("_", 1)[0].lower()
    return head if head in REGISTRIES and head != "_template" else None


def suggest_tools(requested: str, *, platform: str | None = None, limit: int = 5) -> dict:
    """Build a structured ``did you mean`` payload for an unknown tool name.

    Args:
        requested: The (wrong) tool name the model asked for.
        platform: Scope candidates to this platform when known (the meta-tool
            call sites know it). When ``None`` it is inferred from the name's
            prefix, falling back to the full corpus.
        limit: Maximum number of candidate names to return.

    Returns:
        ``{"error": "unknown_tool", "requested": ..., "candidates": [...],
        "dispatch": "<platform>_invoke_tool(name, params)"}``. ``dispatch`` is
        omitted only when no platform can be determined. ``candidates`` is a
        list of real registered tool names ranked by similarity (possibly
        empty).
    """
    requested = (requested or "").strip()
    name_to_platform = _name_to_platform()
    plat = platform or _platform_from_name(requested)

    # Prefer same-platform candidates; widen to the full corpus if the scoped
    # search finds nothing.
    scoped = [n for n, p in name_to_platform.items() if plat is None or p == plat]
    candidates = difflib.get_close_matches(requested, scoped, n=limit, cutoff=_FUZZY_CUTOFF)
    if not candidates and plat is not None:
        candidates = difflib.get_close_matches(requested, list(name_to_platform), n=limit, cutoff=_FUZZY_CUTOFF)
    # Last resort: substring overlap (handles list_sites <-> get_sites where the
    # shared token is short enough to fall under the fuzzy cutoff).
    if not candidates and requested:
        low = requested.lower()
        candidates = sorted(n for n in scoped if low in n.lower() or n.lower() in low)[:limit]

    payload: dict = {
        "error": "unknown_tool",
        "requested": requested,
        "candidates": candidates,
    }
    if plat is not None:
        payload["dispatch"] = f"{plat}_invoke_tool(name, params)"
    return payload


def unknown_tool_payload_from_text(text: str) -> dict | None:
    """Return a ``did you mean`` payload if ``text`` is an ``Unknown tool`` error.

    Parses the ``Unknown tool: <name>`` phrase out of a sandbox error string
    and resolves candidates. Returns ``None`` when the text is some other
    error, so the caller can fall through to its generic handling.
    """
    match = _UNKNOWN_TOOL_RE.search(text or "")
    if not match:
        return None
    payload = suggest_tools(match.group(1))
    # Only surface the structured payload when it is actionable — a resolved
    # platform dispatch hint or at least one real candidate name. A bare name
    # with neither (e.g. a model calling the top-level `search` tool from
    # inside execute, #208 — not a platform-tool typo) falls through to the
    # caller's plain error text so that behavior is preserved.
    if payload.get("dispatch") or payload.get("candidates"):
        return payload
    return None
