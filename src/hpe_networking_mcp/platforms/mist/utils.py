"""Shared helpers for Mist tools.

Kept deliberately small — generated tools delegate to ``_client.mist_request``
directly. This module hosts normalization helpers that cross-platform tools
share when assembling Mist filter values. First introduced for the filter-
parameter consistency sweep (#156); the helper survives the v3.1.0.0 ``mistapi``
removal because the Mist REST API still accepts comma-separated list filters.
"""

from __future__ import annotations


def as_comma_separated(value: str | list[str] | None) -> str | None:
    """Normalize a filter value into the comma-separated string form Mist expects.

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
