"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``scripts/_mist_generator.py`` from
``vendor/mist/mist_openapi.json``. Regenerate via:

    uv run python scripts/regenerate_mist_tools.py

Tag: ``Orgs Admins``
Operations in this file: 6
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
    name="mist_invite_org_admin",
    description="POST /api/v1/orgs/{org_id}/invites\n\ninviteOrgAdmin\n\nIf the request is successful, an email will also be sent to the user with a link to ```https://manage.mist.com/verify/invite?token=:token&expire=1459632743&org=OrgName```",
    capability=Capability.WRITE,
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
    description="GET /api/v1/orgs/{org_id}/admins\n\nlistOrgAdmins\n\nList administrators that have privileges in this organization hierarchy, including organization, site, or site group scopes.",
    capability=Capability.READ,
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
    description="DELETE /api/v1/orgs/{org_id}/admins/{admin_id}\n\nrevokeOrgAdmin\n\nRemove all privileges this administrator has in the organization hierarchy. This does not delete the administrator account.",
    capability=Capability.WRITE_DELETE,
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
    description="DELETE /api/v1/orgs/{org_id}/invites/{invite_id}\n\nuninviteOrgAdmin\n\nCancel a pending organization admin invite by invite ID.",
    capability=Capability.WRITE_DELETE,
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
    description="PUT /api/v1/orgs/{org_id}/admins/{admin_id}\n\nupdateOrgAdmin\n\nUpdate identity fields and privilege assignments for an existing administrator under this organization.",
    capability=Capability.WRITE,
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
    description="PUT /api/v1/orgs/{org_id}/invites/{invite_id}\n\nupdateOrgAdminInvite\n\nUpdate a pending organization admin invite, including invitee identity and requested privileges.",
    capability=Capability.WRITE,
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
