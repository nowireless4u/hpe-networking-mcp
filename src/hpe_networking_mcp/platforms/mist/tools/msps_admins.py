"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``scripts/_mist_generator.py``
from ``vendor/mist_openapi.json``. Regenerate via:

    uv run python scripts/regenerate_mist_tools.py

Tag: ``MSPs Admins``
Operations in this file: 7
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
    name="mist_get_msp_admin",
    description="GET /api/v1/msps/{msp_id}/admins/{admin_id}\n\ngetMspAdmin\n\nGet MSP Admins",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_get_msp_admin(
    ctx: Context,
    msp_id: Annotated[str, Field(description="path parameter 'msp_id'")],
    admin_id: Annotated[str, Field(description="path parameter 'admin_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/msps/{msp_id}/admins/{admin_id}",
        path_params={"msp_id": msp_id, "admin_id": admin_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_invite_msp_admin",
    description="POST /api/v1/msps/{msp_id}/invites\n\ninviteMspAdmin\n\nInvite MSP Admin\n\n**Note**: An email will also be sent to the user with a link to https://manage.mist.com/verify/invite?token=:token",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_invite_msp_admin(
    ctx: Context,
    msp_id: Annotated[str, Field(description="path parameter 'msp_id'")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request Body")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/msps/{msp_id}/invites",
        path_params={"msp_id": msp_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_list_msp_admins",
    description="GET /api/v1/msps/{msp_id}/admins\n\nlistMspAdmins\n\nGet List of MSP Admins",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_list_msp_admins(
    ctx: Context,
    msp_id: Annotated[str, Field(description="path parameter 'msp_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/msps/{msp_id}/admins",
        path_params={"msp_id": msp_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_revoke_msp_admin",
    description="DELETE /api/v1/msps/{msp_id}/admins/{admin_id}\n\nrevokeMspAdmin\n\nThis removes all privileges this admin has against the MSP. This goes deep all the way to the sites",
    tags={"mist", "mist_write", "mist_write_delete"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=True),
)
async def mist_revoke_msp_admin(
    ctx: Context,
    msp_id: Annotated[str, Field(description="path parameter 'msp_id'")],
    admin_id: Annotated[str, Field(description="path parameter 'admin_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "DELETE",
        "/api/v1/msps/{msp_id}/admins/{admin_id}",
        path_params={"msp_id": msp_id, "admin_id": admin_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_uninvite_msp_admin",
    description="DELETE /api/v1/msps/{msp_id}/invites/{invite_id}\n\nuninviteMspAdmin\n\nDelete admin invite",
    tags={"mist", "mist_write", "mist_write_delete"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=True),
)
async def mist_uninvite_msp_admin(
    ctx: Context,
    msp_id: Annotated[str, Field(description="path parameter 'msp_id'")],
    invite_id: Annotated[str, Field(description="path parameter 'invite_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "DELETE",
        "/api/v1/msps/{msp_id}/invites/{invite_id}",
        path_params={"msp_id": msp_id, "invite_id": invite_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_update_msp_admin",
    description="PUT /api/v1/msps/{msp_id}/admins/{admin_id}\n\nupdateMspAdmin\n\nUpdate MSP Admin",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_update_msp_admin(
    ctx: Context,
    msp_id: Annotated[str, Field(description="path parameter 'msp_id'")],
    admin_id: Annotated[str, Field(description="path parameter 'admin_id'")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request Body")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "PUT",
        "/api/v1/msps/{msp_id}/admins/{admin_id}",
        path_params={"msp_id": msp_id, "admin_id": admin_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_update_msp_admin_invite",
    description="PUT /api/v1/msps/{msp_id}/invites/{invite_id}\n\nupdateMspAdminInvite\n\nUpdate MSP admin invite",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_update_msp_admin_invite(
    ctx: Context,
    msp_id: Annotated[str, Field(description="path parameter 'msp_id'")],
    invite_id: Annotated[str, Field(description="path parameter 'invite_id'")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request Body")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "PUT",
        "/api/v1/msps/{msp_id}/invites/{invite_id}",
        path_params={"msp_id": msp_id, "invite_id": invite_id},
        query_params=None,
        body=body,
    )
