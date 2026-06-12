"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``scripts/_mist_generator.py`` from
``vendor/mist/mist_openapi.json``. Regenerate via:

    uv run python scripts/regenerate_mist_tools.py

Tag: ``MSPs Admins``
Operations in this file: 7
"""

# ruff: noqa: E501

from __future__ import annotations

from typing import Annotated, Any

from fastmcp import Context
from pydantic import Field

from hpe_networking_mcp.platforms._common.annotations import Capability
from hpe_networking_mcp.platforms.mist._client import mist_request
from hpe_networking_mcp.platforms.mist._registry import tool as _mcp_tool


@_mcp_tool(
    name="mist_get_msp_admin",
    description="GET /api/v1/msps/{msp_id}/admins/{admin_id}\n\ngetMspAdmin\n\nReturn administrator details and privilege assignments for one administrator under this MSP.",
    capability=Capability.READ,
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
    description="POST /api/v1/msps/{msp_id}/invites\n\ninviteMspAdmin\n\nSend an MSP administrator invitation with the requested identity fields and privilege assignments.\n\n**Note**: An email will also be sent to the user with a link to https://manage.mist.com/verify/invite?token=:token",
    capability=Capability.WRITE,
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
    description="GET /api/v1/msps/{msp_id}/admins\n\nlistMspAdmins\n\nList administrators that have privileges in this MSP hierarchy, including MSP, organization, organization group, site, or site group scopes.",
    capability=Capability.READ,
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
    description="DELETE /api/v1/msps/{msp_id}/admins/{admin_id}\n\nrevokeMspAdmin\n\nRemove all privileges this administrator has through the MSP hierarchy, including inherited organization and site access. This does not delete the administrator account.",
    capability=Capability.WRITE_DELETE,
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
    description="DELETE /api/v1/msps/{msp_id}/invites/{invite_id}\n\nuninviteMspAdmin\n\nCancel a pending MSP administrator invitation before the invitee accepts it.",
    capability=Capability.WRITE_DELETE,
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
    description="PUT /api/v1/msps/{msp_id}/admins/{admin_id}\n\nupdateMspAdmin\n\nUpdate identity fields and privilege assignments for an existing administrator under this MSP.",
    capability=Capability.WRITE,
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
    description="PUT /api/v1/msps/{msp_id}/invites/{invite_id}\n\nupdateMspAdminInvite\n\nUpdate the identity fields or privilege assignments on a pending MSP administrator invitation.",
    capability=Capability.WRITE,
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
