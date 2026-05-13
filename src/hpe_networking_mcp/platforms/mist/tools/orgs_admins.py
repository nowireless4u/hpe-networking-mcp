"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``hpe_networking_mcp.platforms.mist._generator``
from ``vendor/mist_openapi.json``. Regenerate via:

    uv run python -m hpe_networking_mcp.platforms.mist.regenerate

Tag: ``Orgs Admins``
Operations in this file: 6
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
    name="mist_invite_org_admin",
    description="POST /api/v1/orgs/{org_id}/invites\n\ninviteOrgAdmin\n\nIf the request is successful, an email will also be sent to the user with a link to ```https://manage.mist.com/verify/invite?token=:token&expire=1459632743&org=OrgName```",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_invite_org_admin(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request Body")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/orgs/{org_id}/invites",
        path_params={"org_id": org_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_list_org_admins",
    description="GET /api/v1/orgs/{org_id}/admins\n\nlistOrgAdmins\n\nGet List of people who can manage the Site/Org under the Org",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_list_org_admins(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/orgs/{org_id}/admins",
        path_params={"org_id": org_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_revoke_org_admin",
    description="DELETE /api/v1/orgs/{org_id}/admins/{admin_id}\n\nrevokeOrgAdmin\n\nThis removes all privileges this admin has against the org",
    tags={"mist", "mist_write", "mist_write_delete"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=True),
)
async def mist_revoke_org_admin(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    admin_id: Annotated[str, Field(description="path parameter 'admin_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "DELETE",
        "/api/v1/orgs/{org_id}/admins/{admin_id}",
        path_params={"org_id": org_id, "admin_id": admin_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_uninvite_org_admin",
    description="DELETE /api/v1/orgs/{org_id}/invites/{invite_id}\n\nuninviteOrgAdmin\n\nDelete Admin Invite",
    tags={"mist", "mist_write", "mist_write_delete"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=True),
)
async def mist_uninvite_org_admin(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    invite_id: Annotated[str, Field(description="path parameter 'invite_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "DELETE",
        "/api/v1/orgs/{org_id}/invites/{invite_id}",
        path_params={"org_id": org_id, "invite_id": invite_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_update_org_admin",
    description="PUT /api/v1/orgs/{org_id}/admins/{admin_id}\n\nupdateOrgAdmin\n\nInvite Org Admin",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_update_org_admin(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    admin_id: Annotated[str, Field(description="path parameter 'admin_id'")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request Body")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "PUT",
        "/api/v1/orgs/{org_id}/admins/{admin_id}",
        path_params={"org_id": org_id, "admin_id": admin_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_update_org_admin_invite",
    description="PUT /api/v1/orgs/{org_id}/invites/{invite_id}\n\nupdateOrgAdminInvite\n\nUpdate Admin Invite",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_update_org_admin_invite(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    invite_id: Annotated[str, Field(description="path parameter 'invite_id'")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request Body")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "PUT",
        "/api/v1/orgs/{org_id}/invites/{invite_id}",
        path_params={"org_id": org_id, "invite_id": invite_id},
        query_params=None,
        body=body,
    )
