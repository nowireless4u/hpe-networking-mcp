"""Generated GreenLake tools — DO NOT EDIT BY HAND.

Generated from the vendored spec ``vendor/greenlake/credentials.json`` by the
maintainer-local GreenLake generator. These modules are committed and are the
runtime source of truth; regeneration is a release-time maintainer workflow
(the generator is intentionally not committed — see ``.gitignore``).

Service: ``credentials``   Tag: ``credential_management``   Operations: 4
"""

# ruff: noqa: E501, N803
from __future__ import annotations

from typing import Annotated, Any

from fastmcp import Context
from pydantic import Field

from hpe_networking_mcp.platforms._common.annotations import Capability
from hpe_networking_mcp.platforms._common.url import path_seg
from hpe_networking_mcp.platforms.greenlake._registry import tool
from hpe_networking_mcp.platforms.greenlake.client import greenlake_request


@tool(
    name="greenlake_delete_workspaces_v1_credentials_credential_id",
    description="DELETE /workspaces/v1/credentials/{credentialId}\n\ndelete_credentials_workspaces_v1_msp_tenants__tenantId__credentials__credentialId__delete\n\nDelete a credential",
    capability=Capability.WRITE_DELETE,
)
async def greenlake_delete_workspaces_v1_credentials_credential_id(
    ctx: Context,
    credentialId: Annotated[str, Field(description="The unique ID of the credential")],
) -> Any:
    path = f"/workspaces/v1/credentials/{path_seg(credentialId)}"
    return await greenlake_request(
        ctx,
        "DELETE",
        path,
    )


@tool(
    name="greenlake_get_workspaces_v1_credentials",
    description="GET /workspaces/v1/credentials\n\nget_all_credentials_workspaces_v1_msp_tenants__tenantId__credentials_get\n\nGet list of credentials",
    capability=Capability.READ,
)
async def greenlake_get_workspaces_v1_credentials(
    ctx: Context,
    filter: Annotated[
        str | None,
        Field(
            default=None,
            description="Filter data using a subset of OData 4.0 and return only the subset of resources that match the filter.   Get list of credentials that can be filtered by:   - tenantId",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if filter is not None:
        query_params["filter"] = filter
    return await greenlake_request(
        ctx,
        "GET",
        "/workspaces/v1/credentials",
        query_params=query_params or None,
    )


@tool(
    name="greenlake_post_workspaces_v1_credentials",
    description="POST /workspaces/v1/credentials\n\ncreate_credentials_workspaces_v1_msp_tenants__tenantId__credentials_post\n\nCreate a credential",
    capability=Capability.WRITE,
)
async def greenlake_post_workspaces_v1_credentials(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await greenlake_request(
        ctx,
        "POST",
        "/workspaces/v1/credentials",
        body=body,
    )


@tool(
    name="greenlake_post_workspaces_v1_credentials_credential_id_reset",
    description="POST /workspaces/v1/credentials/{credentialId}/reset\n\nreset_credential_workspaces_v1_msp_tenants__tenantId__credentials__credentialId__reset_post\n\nReset a credential",
    capability=Capability.WRITE,
)
async def greenlake_post_workspaces_v1_credentials_credential_id_reset(
    ctx: Context,
    credentialId: Annotated[str, Field(description="The unique ID of the credential.")],
) -> Any:
    path = f"/workspaces/v1/credentials/{path_seg(credentialId)}/reset"
    return await greenlake_request(
        ctx,
        "POST",
        path,
    )
