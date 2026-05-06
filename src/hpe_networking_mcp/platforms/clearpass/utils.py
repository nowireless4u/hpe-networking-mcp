"""Shared utilities for the ClearPass platform tool layer.

Currently exposes the ClearPass REST API list-endpoint query-string builder.
Each ClearPass list operation supports the same five pagination/filter
parameters (filter, sort, offset, limit, calculate_count); this helper
formats them into a query string consistently across all 10+ tool files
that previously inlined an identical local copy.
"""

from __future__ import annotations


def build_query_string(
    filter: str | None = None,
    sort: str | None = None,
    offset: int = 0,
    limit: int = 25,
    calculate_count: bool = False,
) -> str:
    """Build a ClearPass REST API query string for list endpoints.

    Args:
        filter: JSON filter expression (ClearPass REST API syntax).
        sort: Sort order (e.g. ``"+name"`` or ``"-id"``).
        offset: Pagination offset.
        limit: Max results per page.
        calculate_count: When true, response includes the total item count.

    Returns:
        Query string starting with ``"?"`` for appending to a path.
    """
    params = [
        f"filter={filter}" if filter else "",
        f"sort={sort}" if sort else "",
        f"offset={offset}",
        f"limit={limit}",
        f"calculate_count={'true' if calculate_count else 'false'}",
    ]
    return "?" + "&".join(p for p in params if p)
