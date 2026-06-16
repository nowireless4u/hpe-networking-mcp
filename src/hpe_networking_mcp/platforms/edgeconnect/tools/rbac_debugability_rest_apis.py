"""Generated EdgeConnect tools — DO NOT EDIT BY HAND.

Emitted by ``scripts/generate_edgeconnect_tools.py`` from
``vendor/edgeconnect/EdgeConnect-9-7-REST-API.json``. Regenerate via:

    uv run python scripts/generate_edgeconnect_tools.py

Tag: ``rbacDebugabilityRestApis``
Operations in this file: 1
"""

# ruff: noqa: E501
from __future__ import annotations

from typing import Annotated, Any

from fastmcp import Context
from pydantic import Field

from hpe_networking_mcp.platforms._common.annotations import Capability
from hpe_networking_mcp.platforms.edgeconnect._registry import tool
from hpe_networking_mcp.platforms.edgeconnect.client import edgeconnect_request


@tool(
    name="edgeconnect_get_rbac_allowed_rest_apis",
    description="GET /rbac/allowedRestApis\n\ngetAllDebugApis\n\nGet allowed REST API endpoints for current user",
    capability=Capability.READ,
)
async def edgeconnect_get_rbac_allowed_rest_apis(
    ctx: Context,
    method: Annotated[
        str | None,
        Field(
            default=None,
            description="Filter results by HTTP method. Only alphabetic characters are retained and converted to uppercase. If omitted, returns endpoints for all methods.",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if method is not None:
        query_params["method"] = method
    return await edgeconnect_request(
        ctx,
        "GET",
        "/rbac/allowedRestApis",
        query_params=query_params or None,
    )
