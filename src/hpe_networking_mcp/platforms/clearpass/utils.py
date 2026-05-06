"""Shared utilities for the ClearPass platform tool layer.

Exposes:
- ``build_query_string`` — formats the five list-endpoint pagination /
  filter parameters (filter, sort, offset, limit, calculate_count) into
  a query string. Consolidated from 10 file-local copies (issue #125).
- ``clearpass_get`` — single-purpose wrapper for ``ClearPassAPILogin._send_request(path, "get")``.
  Centralizes the use of pyclearpass's private transport method so a
  future SDK change (e.g. addition of a public list method) only needs
  updating in one place rather than ~70 call sites (issue #126).
"""

from __future__ import annotations

from typing import Any


def clearpass_get(client: Any, path: str) -> Any:
    """Send a GET request via pyclearpass's transport layer.

    pyclearpass does not expose a public list method for most resource
    types — list and single-item reads have to use the private
    ``ClearPassAPILogin._send_request(path, "get")`` method. This wrapper
    isolates the dependency so a future SDK change only requires
    updating a single call site.

    Args:
        client: A ``ClearPassAPILogin`` instance returned by
            ``get_clearpass_session()``.
        path: API path (including any pre-built query string from
            ``build_query_string``).

    Returns:
        The decoded JSON body returned by pyclearpass.
    """
    return client._send_request(path, "get")


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
