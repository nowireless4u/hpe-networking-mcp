"""Generated EdgeConnect tools — DO NOT EDIT BY HAND.

Emitted by ``scripts/generate_edgeconnect_tools.py`` from
``vendor/edgeconnect/EdgeConnect-9-7-REST-API.json``. Regenerate via:

    uv run python scripts/generate_edgeconnect_tools.py

Tag: ``gmsPermission``
Operations in this file: 1
"""

# ruff: noqa: E501, N803
from __future__ import annotations

from typing import Annotated, Any

from fastmcp import Context
from pydantic import Field

from hpe_networking_mcp.platforms._common.annotations import Capability
from hpe_networking_mcp.platforms.edgeconnect._registry import tool
from hpe_networking_mcp.platforms.edgeconnect.client import edgeconnect_request


@tool(
    name="edgeconnect_get_gms_permissions",
    description="GET /gms/permissions\n\ngmsUserPermission\n\nGet user permission level",
    capability=Capability.READ,
)
async def edgeconnect_get_gms_permissions(
    ctx: Context,
    userID: Annotated[
        str,
        Field(
            description="The unique identifier of the user whose permission level is being queried. Cannot be null or empty."
        ),
    ],
) -> Any:
    query_params: dict[str, Any] = {}
    if userID is not None:
        query_params["userID"] = userID
    return await edgeconnect_request(
        ctx,
        "GET",
        "/gms/permissions",
        query_params=query_params or None,
    )
