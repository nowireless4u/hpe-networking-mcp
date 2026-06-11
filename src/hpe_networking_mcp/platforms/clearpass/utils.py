"""Shared utilities for the ClearPass platform tool layer.

Exposes:
- ``build_query_string`` — formats the five list-endpoint pagination /
  filter parameters (filter, sort, offset, limit, calculate_count) into
  a query string. Consolidated from 10 file-local copies (issue #125).
- ``clearpass_get`` — single-purpose GET wrapper. Originally isolated
  pyclearpass's private ``_send_request`` (issue #126); the isolation paid
  off — the SDK removal updated exactly this one function for ~70 read
  call sites.
"""

from __future__ import annotations

from typing import Any


async def clearpass_get(client: Any, path: str) -> Any:
    """Send a GET request via the ClearPass client.

    Args:
        client: A ``ClearPassClient`` returned by ``get_clearpass_client()``.
        path: API path (including any pre-built query string from
            ``build_query_string``).

    Returns:
        The decoded JSON body (pyclearpass-compatible contract — error
        bodies are returned, not raised).
    """
    return await client.request("get", path)


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
