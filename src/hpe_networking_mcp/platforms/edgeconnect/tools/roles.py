"""Generated EdgeConnect tools — DO NOT EDIT BY HAND.

Emitted by ``scripts/generate_edgeconnect_tools.py`` from
``vendor/edgeconnect/EdgeConnect-9-7-REST-API.json``. Regenerate via:

    uv run python scripts/generate_edgeconnect_tools.py

Tag: ``roles``
Operations in this file: 3
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
    name="edgeconnect_get_roles",
    description="GET /roles\n\ngetRoles\n\nGet All Roles",
    capability=Capability.READ,
)
async def edgeconnect_get_roles(
    ctx: Context,
    pattern: Annotated[
        str | None,
        Field(
            default=None,
            description="Filter roles by name using a case-insensitive substring match. Only alphanumeric characters, dashes (-), and underscores (_) are allowed.",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if pattern is not None:
        query_params["pattern"] = pattern
    return await edgeconnect_request(
        ctx,
        "GET",
        "/roles",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_roles_next_id",
    description="GET /roles/nextId\n\ngetNextRoleId\n\nGet Next Available Role ID",
    capability=Capability.READ,
)
async def edgeconnect_get_roles_next_id(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/roles/nextId",
        query_params=None,
    )


@tool(
    name="edgeconnect_post_roles",
    description="POST /roles\n\nsaveRoles\n\nSave Roles Configuration",
    capability=Capability.WRITE,
)
async def edgeconnect_post_roles(
    ctx: Context,
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request body")] = None,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/roles",
        query_params=None,
        body=body,
    )
