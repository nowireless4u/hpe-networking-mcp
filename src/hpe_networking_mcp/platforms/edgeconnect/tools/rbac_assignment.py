"""Generated EdgeConnect tools — DO NOT EDIT BY HAND.

Emitted by ``scripts/generate_edgeconnect_tools.py`` from
``vendor/edgeconnect/EdgeConnect-9-7-REST-API.json``. Regenerate via:

    uv run python scripts/generate_edgeconnect_tools.py

Tag: ``rbacAssignment``
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
    name="edgeconnect_delete_rbac_assignment",
    description="DELETE /rbac/assignment\n\ndeleteRbacAssignment510\n\nDelete RBAC user access customization by username",
    capability=Capability.WRITE_DELETE,
)
async def edgeconnect_delete_rbac_assignment(
    ctx: Context,
    username: Annotated[
        str,
        Field(
            description="The username whose RBAC assignment should be deleted. Must be non-empty and match an existing assignment."
        ),
    ],
) -> Any:
    query_params: dict[str, Any] = {}
    if username is not None:
        query_params["username"] = username
    return await edgeconnect_request(
        ctx,
        "DELETE",
        "/rbac/assignment",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_rbac_assignment",
    description="GET /rbac/assignment\n\ngetRbacAssignmentByUsername511\n\nGet RBAC assignments",
    capability=Capability.READ,
)
async def edgeconnect_get_rbac_assignment(
    ctx: Context,
    username: Annotated[
        str | None,
        Field(
            default=None,
            description="Filter by specific username. When omitted, returns all RBAC assignments. When provided, returns only the assignment for that user.",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if username is not None:
        query_params["username"] = username
    return await edgeconnect_request(
        ctx,
        "GET",
        "/rbac/assignment",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_post_rbac_assignment",
    description="POST /rbac/assignment\n\ncreateOrUpdateRbacAssignment509\n\nCreate or update RBAC user access customization",
    capability=Capability.WRITE,
)
async def edgeconnect_post_rbac_assignment(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/rbac/assignment",
        query_params=None,
        body=body,
    )
