"""Generated EdgeConnect tools — DO NOT EDIT BY HAND.

Emitted by ``scripts/generate_edgeconnect_tools.py`` from
``vendor/edgeconnect/EdgeConnect-9-7-REST-API.json``. Regenerate via:

    uv run python scripts/generate_edgeconnect_tools.py

Tag: ``EdgeHAGroups``
Operations in this file: 4
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
    name="edgeconnect_delete_edge_ha_groups",
    description="DELETE /edge-ha/groups\n\nhaGroupsDelete409\n\nDelete an Edge HA group and unpair appliances",
    capability=Capability.WRITE_DELETE,
)
async def edgeconnect_delete_edge_ha_groups(
    ctx: Context,
    id: Annotated[
        int,
        Field(
            description="Unique integer identifier of the HA group to delete. Obtained from GET /edge-ha/groups response."
        ),
    ],
) -> Any:
    query_params: dict[str, Any] = {}
    if id is not None:
        query_params["id"] = id
    return await edgeconnect_request(
        ctx,
        "DELETE",
        "/edge-ha/groups",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_edge_ha_groups",
    description="GET /edge-ha/groups\n\nedgehaGroupsGet406\n\nRetrieve all Edge HA groups",
    capability=Capability.READ,
)
async def edgeconnect_get_edge_ha_groups(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/edge-ha/groups",
        query_params=None,
    )


@tool(
    name="edgeconnect_post_edge_ha_groups",
    description="POST /edge-ha/groups\n\nhaGroupsPost407\n\nCreate a new Edge HA group",
    capability=Capability.WRITE,
)
async def edgeconnect_post_edge_ha_groups(
    ctx: Context,
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request body")] = None,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/edge-ha/groups",
        query_params=None,
        body=body,
    )


@tool(
    name="edgeconnect_put_edge_ha_groups",
    description="PUT /edge-ha/groups\n\nhaGroupsPut408\n\nUpdate an existing Edge HA group",
    capability=Capability.WRITE,
)
async def edgeconnect_put_edge_ha_groups(
    ctx: Context,
    id: Annotated[
        int, Field(description="Unique identifier of the HA group to update. Must reference an existing group.")
    ],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request body")] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if id is not None:
        query_params["id"] = id
    return await edgeconnect_request(
        ctx,
        "PUT",
        "/edge-ha/groups",
        query_params=query_params or None,
        body=body,
    )
