"""Example read-only tool — reference pattern only, never registered.

Delete this file when you copy the template into a real platform and
replace it with your real ``<platform>_get_*`` tools.
"""

from __future__ import annotations

from typing import Any

from fastmcp import Context

from hpe_networking_mcp.platforms._template._registry import tool
from hpe_networking_mcp.platforms._template.client import format_http_error, get_template_client
from hpe_networking_mcp.platforms._template.tools import READ_ONLY


@tool(annotations=READ_ONLY)
async def template_get_example(ctx: Context) -> list[dict[str, Any]] | str:
    """Get a list of example things from the template platform.

    Reference pattern: every read tool follows this shape.

    - Acquire the platform client via ``get_<platform>_client()``.
    - Call ``client.get_json(...)`` (or ``client.request(...)`` for non-JSON).
    - Return the parsed body or a string error message.
    - Wrap the call in ``try/except`` and run errors through ``format_http_error``.
    """
    try:
        client = await get_template_client()
        payload = await client.get_json("/api/v1.0/Things")
        items = payload.get("items", payload) if isinstance(payload, dict) else payload
        return items
    except Exception as e:
        return f"Error fetching things: {format_http_error(e) if hasattr(e, 'response') else e}"
