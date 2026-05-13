"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``hpe_networking_mcp.platforms.mist._generator``
from ``vendor/mist_openapi.json``. Regenerate via:

    uv run python -m hpe_networking_mcp.platforms.mist.regenerate

Tag: ``Orgs Linked Applications``
Operations in this file: 4
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
    name="mist_add_org_oauth_app_accounts",
    description="POST /api/v1/orgs/{org_id}/setting/{app_name}/link_accounts\n\naddOrgOauthAppAccounts\n\nAdd Jamf, VMware Authorization With Mist Portal",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_add_org_oauth_app_accounts(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    app_name: Annotated[Any, Field(description="OAuth application name")],
    body: Annotated[
        dict[str, Any] | None,
        Field(default=None, description="Request body for POST /api/v1/orgs/{org_id}/setting/{app_name}/link_accounts"),
    ] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/orgs/{org_id}/setting/{app_name}/link_accounts",
        path_params={"org_id": org_id, "app_name": app_name},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_delete_org_oauth_app_authorization",
    description="DELETE /api/v1/orgs/{org_id}/setting/{app_name}/link_accounts/{account_id}\n\ndeleteOrgOauthAppAuthorization\n\nDelete Org Level OAuth Application Authorization With Mist Portal",
    tags={"mist", "mist_write", "mist_write_delete"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=True),
)
async def mist_delete_org_oauth_app_authorization(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    app_name: Annotated[Any, Field(description="OAuth application name")],
    account_id: Annotated[str, Field(description="path parameter 'account_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "DELETE",
        "/api/v1/orgs/{org_id}/setting/{app_name}/link_accounts/{account_id}",
        path_params={"org_id": org_id, "app_name": app_name, "account_id": account_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_get_org_oauth_app_linked_status",
    description="GET /api/v1/orgs/{org_id}/setting/{app_name}/link_accounts\n\ngetOrgOauthAppAuthorizationUrl\n\nGet Org Level OAuth Application Linked Status",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_get_org_oauth_app_linked_status(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    app_name: Annotated[Any, Field(description="OAuth application name")],
    forward: Annotated[
        str,
        Field(
            description="Mist portal url to which backend needs to redirect after successful OAuth authorization. **Required** to get the `authorization_url`"
        ),
    ],
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/orgs/{org_id}/setting/{app_name}/link_accounts",
        path_params={"org_id": org_id, "app_name": app_name},
        query_params={"forward": forward},
        body=None,
    )


@_mcp_tool(
    name="mist_update_org_oauth_app_account",
    description="PUT /api/v1/orgs/{org_id}/setting/{app_name}/link_accounts/{account_id}\n\nupdateOrgOauthAppAccount\n\nUpdate Zoom, Teams, Intune Authorization.\n\nRequest Payload, These Field And Values Will Be Specific To Each Of The Third Party Apps Accounts.",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_update_org_oauth_app_account(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    app_name: Annotated[Any, Field(description="OAuth application name")],
    account_id: Annotated[str, Field(description="path parameter 'account_id'")],
    body: Annotated[
        dict[str, Any] | None,
        Field(
            default=None,
            description="Request body for PUT /api/v1/orgs/{org_id}/setting/{app_name}/link_accounts/{account_id}",
        ),
    ] = None,
) -> Any:
    return await mist_request(
        ctx,
        "PUT",
        "/api/v1/orgs/{org_id}/setting/{app_name}/link_accounts/{account_id}",
        path_params={"org_id": org_id, "app_name": app_name, "account_id": account_id},
        query_params=None,
        body=body,
    )
