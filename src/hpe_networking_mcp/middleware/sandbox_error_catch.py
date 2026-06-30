"""SandboxErrorCatchMiddleware — catch code-mode sandbox errors.

In ``MCP_TOOL_MODE=code``, the ``execute`` tool runs LLM-written Python in a
``pydantic_monty`` sandbox. Any sandbox-level error (``MontyRuntimeError``,
``MontySyntaxError``, ``MontyTypingError``) bubbles out and, combined with
``mask_error_details=True`` (which we deliberately set for security), is
caught by FastMCP's tool dispatcher in ``server.py:call_tool`` and re-raised
as a generic ``ToolError("Error calling tool 'execute'")`` — leaving the
LLM with nothing to self-correct from.

The original ``MontyError`` is preserved on ``ToolError.__cause__``, so this
middleware catches ``ToolError`` for the ``execute`` tool, inspects the
cause, and if it's a ``MontyError`` re-raises a fresh ``ToolError`` carrying
the actual error text. Middleware sits *outside* the masking layer in the
call chain, so this fresh exception propagates to the MCP request handler
unmasked — the wire response gets ``isError: true`` AND the readable error
text in ``content``. The LLM sees the message; the orchestrator sees the
failure flag.

(Aside on why this differs from ``ValidationCatchMiddleware``: FastMCP
special-cases ``ValidationError`` to re-raise unchanged — so that catch can
match the original type. ``MontyError`` falls through to the generic
``Exception`` branch which applies the masking wrapper.)

Closes #208 (LLM self-correction) and #(this PR) (orchestrator-visible
``isError`` flag). The "Unknown tool: search" masking case is the most
common trigger — LLMs frequently try to call discovery tools from inside
``execute()`` even though those only exist at the outer MCP surface.
Syntax errors from stray indentation in model-generated code are another.
"""

from __future__ import annotations

import json
import re
from datetime import UTC, datetime
from typing import Any

import mcp.types
from fastmcp.exceptions import ToolError
from fastmcp.server.middleware import Middleware, MiddlewareContext
from loguru import logger

from hpe_networking_mcp.platforms._common.tool_suggest import (
    unknown_tool_payload_from_text,
)

# pydantic_monty ships in the fastmcp[code-mode] extra. If it's missing,
# code mode itself can't run, so we don't need this middleware to act —
# but importing it must not crash the server.
try:
    from pydantic_monty import MontyError  # type: ignore[import-not-found]

    _HAS_MONTY = True
except ImportError:
    MontyError = Exception  # type: ignore[misc,assignment]
    _HAS_MONTY = False


# Sandbox clock/time dead-ends monty can't satisfy even with the clock
# enabled: `datetime.utcnow()` (monty implements only `datetime.now`) and the
# absent `time` module. The clock-enabled provider makes `datetime.now()` /
# `date.today()` work, but a model reaching for these specific names still
# hard-fails — so we turn the raw error into a self-correcting one. Substring
# match against the lower-cased cause text.
_CLOCK_DEADEND_MARKERS: tuple[str, ...] = (
    "utcnow",  # AttributeError: ... no attribute 'utcnow'
    "no module named 'time'",  # ModuleNotFoundError on `import time`
    "os function 'datetime",  # NotImplementedError (clock disabled / older deploy)
    "os function 'date",
)


def _clock_error_hint(cause_text: str) -> str | None:
    """Return self-correcting guidance for a sandbox clock/time dead-end.

    The middleware runs in real (non-sandbox) Python, so it can stamp the
    actual current time into the message — giving the model both the working
    substitute API and a literal value it can hardcode. Returns ``None`` when
    the error is unrelated to the clock.
    """
    low = cause_text.lower()
    if not any(marker in low for marker in _CLOCK_DEADEND_MARKERS):
        return None
    now = datetime.now(UTC)
    iso = now.strftime("%Y-%m-%dT%H:%M:%SZ")
    return (
        "Hint: the sandbox has no `datetime.utcnow()` and no `time` module, but "
        "the clock IS available — use `datetime.now(datetime.timezone.utc)` "
        "(or `datetime.now()` / `datetime.date.today()`), and "
        "`datetime.now().timestamp()` instead of `time.time()`. "
        f"Current UTC time is {iso}. Many search/report tools also accept a "
        '`duration` argument (e.g. "1d"), so you often need not compute a '
        "window at all."
    )


_NAMEERROR_RE = re.compile(r"name ['\"]([^'\"]+)['\"] is not defined")

# Python builtins monty does NOT provide in the sandbox. A NameError on one of
# these is an "unavailable builtin", not a cross-block-state slip — telling them
# apart keeps the hint accurate (#513: `getattr(object(), ...)` raises NameError
# on `object`, which previously got the misleading "recompute from a previous
# block" advice).
_UNAVAILABLE_BUILTINS: frozenset[str] = frozenset(
    {
        "object",
        "open",
        "eval",
        "exec",
        "compile",
        "input",
        "globals",
        "locals",
        "vars",
        "help",
        "breakpoint",
        "__import__",
        "memoryview",
        "bytearray",
    }
)


def _nameerror_hint(cause_text: str) -> str | None:
    """Return guidance for a sandbox ``NameError``.

    Two distinct causes share the ``NameError`` shape:

    * An **unavailable builtin** (``object`` / ``open`` / ...) — the sandbox
      doesn't bind it (#513).
    * A **cross-block-state slip** — the model referenced a variable defined in
      a PREVIOUS ``execute()`` call, but each call is a fresh, stateless sandbox
      (observed: Haiku 4.5 referencing an `org_id` from a prior block).

    Returns ``None`` for non-NameError causes.
    """
    m = _NAMEERROR_RE.search(cause_text)
    if m is None:
        return None
    name = m.group(1)
    if name in _UNAVAILABLE_BUILTINS:
        return (
            f"Hint: `{name}` is a Python builtin the sandbox does NOT provide "
            "(file/OS and reflection builtins are unavailable). Use plain data, "
            "literals, and the injected `call_tool` instead."
        )
    return (
        f"Hint: `{name}` is undefined. Most often this is because each `execute()` "
        "call runs in a FRESH, stateless sandbox — variables defined in a PREVIOUS "
        "`execute()` block do NOT carry over. Do all the work for one task inside a "
        f"SINGLE block, or recompute/re-fetch `{name}` here first. (It could also be "
        "an unsupported builtin or a typo.)"
    )


_MODULE_RE = re.compile(r"no module named ['\"]([^'\"]+)['\"]", re.IGNORECASE)

# Targeted builtin substitutes for the stdlib modules small models reach for
# most (#514). Anything not listed falls back to the generic guidance.
_MODULE_SUBSTITUTES: dict[str, str] = {
    "collections": "use a plain dict (`d[k] = d.get(k, 0) + 1` for Counter, "
    "`d.setdefault(k, []).append(v)` for defaultdict)",
    "statistics": "compute directly (mean = `sum(xs) / len(xs)`)",
    "itertools": "use loops / comprehensions",
    "functools": "use an explicit loop instead of reduce",
    "random": "not available; take the first N items instead of sampling",
}


def _module_hint(cause_text: str) -> str | None:
    """``ModuleNotFoundError`` — most stdlib modules are absent (#514)."""
    m = _MODULE_RE.search(cause_text)
    if m is None:
        return None
    module = m.group(1)
    sub = _MODULE_SUBSTITUTES.get(module)
    tail = f" For `{module}`, {sub}." if sub else " Most stdlib modules are absent."
    return (
        f"Hint: the sandbox has no `{module}` module.{tail} Available modules: `json`, "
        "`re`, `math`, `datetime`. Otherwise use builtins (`dict`/`set`/`sorted`/`sum`/"
        "`min`/`max`/`enumerate`/`zip`) and f-strings."
    )


def _strformat_hint(cause_text: str) -> str | None:
    """``str.format()`` is unsupported — only f-strings work (#515)."""
    if "object has no attribute 'format'" not in cause_text:
        return None
    return "Hint: the sandbox supports f-strings, not `str.format()`. Rewrite `'{} {}'.format(a, b)` as `f'{a} {b}'`."


def _json_default_hint(cause_text: str) -> str | None:
    """``json.dumps(default=...)`` is unsupported (#516)."""
    if "unexpected keyword argument 'default'" not in cause_text:
        return None
    return (
        "Hint: the sandbox `json.dumps` does not accept `default=`. Drop it and "
        "pre-convert non-serializable values (e.g. `str(x)`) before dumping."
    )


def _next_iter_hint(cause_text: str) -> str | None:
    """``next(<generator>, default)`` fails in the sandbox (#517)."""
    if "object is not an iterator" not in cause_text:
        return None
    return (
        "Hint: `next(<generator/list>, default)` doesn't work in the sandbox. Use a "
        "comprehension + index (`hits = [x for x in xs if cond]; hits[0] if hits else "
        "default`) or `next(iter(seq), default)`."
    )


def _dict_union_hint(cause_text: str) -> str | None:
    """``dict | dict`` is unsupported — use spread (#518)."""
    if "unsupported operand type(s) for |: 'dict' and 'dict'" not in cause_text:
        return None
    return "Hint: the sandbox doesn't support `dict | dict`. Merge with `{**a, **b}`."


def _unhashable_list_hint(cause_text: str) -> str | None:
    """A list used as a dict key / set member — usually a Mist search array.

    Mist org-level search/aggregation endpoints (``mist_search_org_wireless_clients``,
    ``mist_search_org_devices``, ...) return ARRAYS for fields that can vary over the
    search window — ``ssid`` / ``hostname`` / ``ap`` / ``device`` — because a client or
    device may have several across the window (``mac`` / ``band`` stay scalar). Models
    routinely use one of these directly as a dict key and hit ``unhashable type: 'list'``
    (Zach report). Verified live against the Mist API. The fix is to index or join the
    array, NOT to expect a scalar.
    """
    if "unhashable type: 'list'" not in cause_text and "'list' as a dict key" not in cause_text:
        return None
    return (
        "Hint: a list was used as a dict key or set member (lists are unhashable). This "
        "commonly comes from Mist org-level search results: `mist_search_org_wireless_clients` / "
        "`mist_search_org_devices` (and other `*_search_org_*` tools) return ARRAYS for "
        "window-aggregated fields — `ssid`, `hostname`, `ap`, `device` — since a client/device "
        "can have several over the window (`mac` and `band` stay scalar). Index the array "
        "(`value[0]`) or join it (`', '.join(value)`) before using it as a key; iterate it for "
        "set membership. Do NOT assume these fields are scalars — a value that's one element "
        "today can be several tomorrow."
    )


_SHAPE_RE = re.compile(r"'(\w+)' object has no attribute '(get|keys|items|values)'")


def _shape_hint(cause_text: str) -> str | None:
    """Dict-method on a non-dict — usually envelope/collection mis-navigation (#532)."""
    m = _SHAPE_RE.search(cause_text)
    if m is None:
        return None
    typ = m.group(1)
    return (
        f"Hint: you're calling a dict method on a `{typ}` (often a string from "
        "iterating a dict's keys). `call_tool` results are wrapped in an envelope — "
        "read the payload via `result['data']`. Collection shape varies: "
        "`<platform>_list_tools` → `result['data']['tools']`; many monitoring reads → "
        "`result['data']['items']`; some reads are a bare list under `result['data']`. "
        "Check `isinstance(x, dict)` before calling `.get()`."
    )


# Ordered hint rules — first match wins. Order matters where causes overlap:
# clock runs before module (the absent `time` module is a clock dead-end), and
# the NameError builtin/state split is handled inside `_nameerror_hint`.
_HINT_FNS = (
    _clock_error_hint,
    _nameerror_hint,
    _module_hint,
    _strformat_hint,
    _json_default_hint,
    _next_iter_hint,
    _dict_union_hint,
    _unhashable_list_hint,
    _shape_hint,
)


class SandboxErrorCatchMiddleware(Middleware):
    """Convert sandbox ``MontyError`` (wrapped in ``ToolError`` by FastMCP's
    masking layer) into a fresh ``ToolError`` with the readable cause text.

    Re-raising (rather than returning a ``ToolResult``) is deliberate: the
    fresh ``ToolError`` propagates to the MCP request handler unmasked, so
    the wire response gets ``isError: true`` AND the readable error text in
    ``content``. Returning a ``ToolResult`` instead would suppress
    ``isError`` (the wire flag would be ``false`` since no exception was
    raised) — orchestrators can't distinguish failed tool calls from
    successful ones that returned an error-shaped string.

    Only acts on the code-mode ``execute`` tool. All other tools pass through
    untouched — sandbox errors are a code-mode-specific failure mode.
    """

    EXECUTE_TOOL_NAME = "execute"

    async def on_call_tool(
        self,
        context: MiddlewareContext[mcp.types.CallToolRequestParams],
        call_next: Any,
    ) -> Any:
        if not _HAS_MONTY:
            return await call_next(context)

        tool_name = getattr(context.message, "name", "")
        if tool_name != self.EXECUTE_TOOL_NAME:
            return await call_next(context)

        try:
            return await call_next(context)
        except ToolError as e:
            # FastMCP wraps the original sandbox exception in ToolError when
            # mask_error_details=True is set. The original is on __cause__.
            cause = e.__cause__
            if not isinstance(cause, MontyError):
                # Not a sandbox failure — let the masked ToolError propagate.
                raise
            # An "Unknown tool: X" inside execute() is the single most common
            # sandbox error (a model guessing a tool name). Turn it into a
            # structured "did you mean" payload with real candidate names so
            # the model self-corrects instead of looping on the same call
            # (#489). The candidates are data, not an imperative.
            suggestion = unknown_tool_payload_from_text(str(cause))
            if suggestion is not None:
                error_text = json.dumps(suggestion)
            else:
                error_text = f"Sandbox error: {cause}"
                # Append a self-correcting hint for the common small-model
                # sandbox mistakes (clock/time, cross-block state, missing
                # modules/builtins, str.format, json default=, next(gen),
                # dict|, envelope/shape navigation). The error result is the one
                # channel the model reliably acts on, unlike advisory
                # INSTRUCTIONS.md content. First matching rule wins.
                for hint_fn in _HINT_FNS:
                    hint = hint_fn(str(cause))
                    if hint is not None:
                        error_text = f"{error_text}\n\n{hint}"
                        break
            logger.debug("SandboxErrorCatch: caught on {} → {}", tool_name, error_text)
            # Re-raise so the wire response sets isError=true. Middleware
            # sits outside the masking layer, so this propagates with the
            # message intact — fixing both LLM-readability (#208) and
            # orchestrator-visible isError flag.
            raise ToolError(error_text) from cause
