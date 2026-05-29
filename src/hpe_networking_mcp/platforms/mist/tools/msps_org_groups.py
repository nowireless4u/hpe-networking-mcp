"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``scripts/_mist_generator.py`` from
``vendor/mist_openapi.json``. Regenerate via:

    uv run python scripts/regenerate_mist_tools.py

Tag: ``MSPs Org Groups``
Operations in this file: 5
"""

# ruff: noqa: E501

from __future__ import annotations

from typing import Annotated, Any

from fastmcp import Context
from mcp.types import ToolAnnotations
from pydantic import Field

from hpe_networking_mcp.platforms.mist._client import mist_request
from hpe_networking_mcp.platforms.mist._registry import tool as _mcp_tool


@_mcp_tool(
    name="mist_create_msp_org_group",
    description="POST /api/v1/msps/{msp_id}/orggroups\n\ncreateMspOrgGroup\n\nCreate MSP Org Group",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_create_msp_org_group(
    ctx: Context,
    msp_id: Annotated[str, Field(description="path parameter 'msp_id'")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request Body")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/msps/{msp_id}/orggroups",
        path_params={"msp_id": msp_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_delete_msp_org_group",
    description="DELETE /api/v1/msps/{msp_id}/orggroups/{orggroup_id}\n\ndeleteMspOrgGroup\n\nDelete MSP Org Group",
    tags={"mist", "mist_write", "mist_write_delete"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=True),
)
async def mist_delete_msp_org_group(
    ctx: Context,
    msp_id: Annotated[str, Field(description="path parameter 'msp_id'")],
    orggroup_id: Annotated[str, Field(description="path parameter 'orggroup_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "DELETE",
        "/api/v1/msps/{msp_id}/orggroups/{orggroup_id}",
        path_params={"msp_id": msp_id, "orggroup_id": orggroup_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_get_msp_org_group",
    description="GET /api/v1/msps/{msp_id}/orggroups/{orggroup_id}\n\ngetMspOrgGroup\n\nGet MSP Org Group Details",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_get_msp_org_group(
    ctx: Context,
    msp_id: Annotated[str, Field(description="path parameter 'msp_id'")],
    orggroup_id: Annotated[str, Field(description="path parameter 'orggroup_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/msps/{msp_id}/orggroups/{orggroup_id}",
        path_params={"msp_id": msp_id, "orggroup_id": orggroup_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_list_msp_org_groups",
    description="GET /api/v1/msps/{msp_id}/orggroups\n\nlistMspOrgGroups\n\nGet List of MSP Org Groups",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_list_msp_org_groups(
    ctx: Context,
    msp_id: Annotated[str, Field(description="path parameter 'msp_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/msps/{msp_id}/orggroups",
        path_params={"msp_id": msp_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_update_msp_org_group",
    description="PUT /api/v1/msps/{msp_id}/orggroups/{orggroup_id}\n\nupdateMspOrgGroup\n\nUpdate MSP Org Group",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_update_msp_org_group(
    ctx: Context,
    msp_id: Annotated[str, Field(description="path parameter 'msp_id'")],
    orggroup_id: Annotated[str, Field(description="path parameter 'orggroup_id'")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request Body")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "PUT",
        "/api/v1/msps/{msp_id}/orggroups/{orggroup_id}",
        path_params={"msp_id": msp_id, "orggroup_id": orggroup_id},
        query_params=None,
        body=body,
    )
