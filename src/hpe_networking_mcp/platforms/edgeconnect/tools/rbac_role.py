"""Generated EdgeConnect tools — DO NOT EDIT BY HAND.

Emitted by ``scripts/generate_edgeconnect_tools.py`` from
``vendor/edgeconnect/EdgeConnect-9-7-REST-API.json``. Regenerate via:

    uv run python scripts/generate_edgeconnect_tools.py

Tag: ``rbacRole``
Operations in this file: 4
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
    name="edgeconnect_delete_rbac_role",
    description="DELETE /rbac/role\n\ndeleteRoleByRoleName515\n\nDelete an RBAC role by name",
    capability=Capability.WRITE_DELETE,
)
async def edgeconnect_delete_rbac_role(
    ctx: Context,
    menuTypeName: Annotated[
        str,
        Field(
            description="Unique name identifier of the role to delete. Must be a non-empty string matching an existing role name."
        ),
    ],
) -> Any:
    query_params: dict[str, Any] = {}
    if menuTypeName is not None:
        query_params["menuTypeName"] = menuTypeName
    return await edgeconnect_request(
        ctx,
        "DELETE",
        "/rbac/role",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_rbac_role",
    description="GET /rbac/role\n\ngetAllRoles512\n\nGet all RBAC roles or a specific role by name",
    capability=Capability.READ,
)
async def edgeconnect_get_rbac_role(
    ctx: Context,
    menuTypeName: Annotated[
        str | None,
        Field(default=None, description="Name of a specific role to retrieve. If omitted, all roles are returned."),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if menuTypeName is not None:
        query_params["menuTypeName"] = menuTypeName
    return await edgeconnect_request(
        ctx,
        "GET",
        "/rbac/role",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_rbac_role_menu_assigned",
    description="GET /rbac/role/menuAssigned\n\ngetAssignedMenus514\n\nGet menu access permissions for current session user",
    capability=Capability.READ,
)
async def edgeconnect_get_rbac_role_menu_assigned(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/rbac/role/menuAssigned",
        query_params=None,
    )


@tool(
    name="edgeconnect_post_rbac_role",
    description="POST /rbac/role\n\nsaveRole513\n\nCreate or update an RBAC role",
    capability=Capability.WRITE,
)
async def edgeconnect_post_rbac_role(
    ctx: Context,
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request body")] = None,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/rbac/role",
        query_params=None,
        body=body,
    )
