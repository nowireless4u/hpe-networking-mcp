"""Generated EdgeConnect tools — DO NOT EDIT BY HAND.

Emitted by ``scripts/generate_edgeconnect_tools.py`` from
``vendor/edgeconnect/EdgeConnect-9-7-REST-API.json``. Regenerate via:

    uv run python scripts/generate_edgeconnect_tools.py

Tag: ``rbacApplianceAccessGroup``
Operations in this file: 3
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
    name="edgeconnect_delete_rbac_asset",
    description="DELETE /rbac/asset\n\ndeleteApplianceAccessGroupByName506\n\nDelete appliance access group (asset) by name",
    capability=Capability.WRITE_DELETE,
)
async def edgeconnect_delete_rbac_asset(
    ctx: Context,
    applianceAccessTypeName: Annotated[
        str,
        Field(
            description="Unique name of the appliance access group (asset) to delete. Must be non-empty and match an existing asset name."
        ),
    ],
) -> Any:
    query_params: dict[str, Any] = {}
    if applianceAccessTypeName is not None:
        query_params["applianceAccessTypeName"] = applianceAccessTypeName
    return await edgeconnect_request(
        ctx,
        "DELETE",
        "/rbac/asset",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_rbac_asset",
    description="GET /rbac/asset\n\ngetAllApplianceAccessGroups504\n\nRetrieve appliance access groups (assets)",
    capability=Capability.READ,
)
async def edgeconnect_get_rbac_asset(
    ctx: Context,
    applianceAccessTypeName: Annotated[
        str | None,
        Field(
            default=None,
            description="Name of a specific appliance access group (asset) to retrieve. When provided, returns only the configuration for that asset.",
        ),
    ] = None,
    assigned: Annotated[
        bool | None,
        Field(
            default=None,
            description="When true, returns the appliance access group assigned to the current user's session. Returns 204 if no asset is assigned or if request is from API key/local. Ignored when applianceAccessTypeName is provided.",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if applianceAccessTypeName is not None:
        query_params["applianceAccessTypeName"] = applianceAccessTypeName
    if assigned is not None:
        query_params["assigned"] = assigned
    return await edgeconnect_request(
        ctx,
        "GET",
        "/rbac/asset",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_post_rbac_asset",
    description="POST /rbac/asset\n\ncreateOrUpdateApplianceAccessGroup505\n\nCreate or update appliance access group (asset)",
    capability=Capability.WRITE,
)
async def edgeconnect_post_rbac_asset(
    ctx: Context,
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request body")] = None,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/rbac/asset",
        query_params=None,
        body=body,
    )
