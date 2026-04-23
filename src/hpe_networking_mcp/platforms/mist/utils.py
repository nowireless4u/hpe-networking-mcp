"""Shared helpers for Mist tools.

Kept deliberately small — Mist tools mostly delegate to ``mistapi`` directly.
This module exists to host normalization helpers that multiple tools share,
the first of which was introduced for the filter-parameter consistency sweep
(#156).
"""

from __future__ import annotations


def as_comma_separated(value: str | list[str] | None) -> str | None:
    """Normalize a filter value into the comma-separated string form mistapi expects.

    mistapi exposes many list-endpoint parameters that accept either a single
    value or a comma-separated list. This helper lets our tool parameters accept
    either a ``str`` or a ``list[str]`` without surprising LLMs that pattern-match
    against sibling tools that use the singular form.

    ::

        "AP43"                 -> "AP43"              (unchanged)
        "AP43,AP44"            -> "AP43,AP44"         (unchanged)
        ["AP43", "AP44"]       -> "AP43,AP44"         (joined)
        None                   -> None
    """
    if value is None:
        return None
    if isinstance(value, str):
        return value
    return ",".join(str(v) for v in value)
