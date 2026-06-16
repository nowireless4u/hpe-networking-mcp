"""Generated EdgeConnect tools — DO NOT EDIT BY HAND.

Emitted by ``scripts/generate_edgeconnect_tools.py`` from
``vendor/edgeconnect/EdgeConnect-9-7-REST-API.json``. Regenerate via:

    uv run python scripts/generate_edgeconnect_tools.py

Tag: ``activeSessions``
Operations in this file: 2
"""

from __future__ import annotations

from typing import Annotated, Any

from fastmcp import Context
from pydantic import Field

from hpe_networking_mcp.platforms._common.annotations import Capability
from hpe_networking_mcp.platforms.edgeconnect._registry import tool
from hpe_networking_mcp.platforms.edgeconnect.client import edgeconnect_request


@tool(
    name="edgeconnect_get_session_active_sessions",
    description="GET /session/activeSessions\n\nsessions553\n\nRetrieve all current active user sessions",
    capability=Capability.READ,
)
async def edgeconnect_get_session_active_sessions(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/session/activeSessions",
        query_params=None,
    )


@tool(
    name="edgeconnect_post_session_active_sessions_delete",
    description="POST /session/activeSessions/delete\n\npostDeleteSessions554\n\nTerminate active user sessions",
    capability=Capability.WRITE,
)
async def edgeconnect_post_session_active_sessions_delete(
    ctx: Context,
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request body")] = None,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/session/activeSessions/delete",
        query_params=None,
        body=body,
    )
