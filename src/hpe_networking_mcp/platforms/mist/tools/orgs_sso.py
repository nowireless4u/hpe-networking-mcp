"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``hpe_networking_mcp.platforms.mist._generator``
from ``vendor/mist_openapi.json``. Regenerate via:

    uv run python -m hpe_networking_mcp.platforms.mist.regenerate

Tag: ``Orgs SSO``
Operations in this file: 9
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
    name="mist_create_org_sso",
    description="POST /api/v1/orgs/{org_id}/ssos\n\ncreateOrgSso\n\nCreate Org SSO Configuration",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_create_org_sso(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request Body")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/orgs/{org_id}/ssos",
        path_params={"org_id": org_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_delete_org_sso",
    description="DELETE /api/v1/orgs/{org_id}/ssos/{sso_id}\n\ndeleteOrgSso\n\nDelete Org SSO Configuration",
    tags={"mist", "mist_write", "mist_write_delete"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=True),
)
async def mist_delete_org_sso(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    sso_id: Annotated[str, Field(description="path parameter 'sso_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "DELETE",
        "/api/v1/orgs/{org_id}/ssos/{sso_id}",
        path_params={"org_id": org_id, "sso_id": sso_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_delete_org_sso_admins",
    description="POST /api/v1/orgs/{org_id}/ssos/{sso_id}/delete_admins\n\ndeleteOrgSsoAdmins\n\nDelete SSO Admin users by email. This removes SSO-linked admin accounts from the organization.",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_delete_org_sso_admins(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    sso_id: Annotated[str, Field(description="path parameter 'sso_id'")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request Body")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/orgs/{org_id}/ssos/{sso_id}/delete_admins",
        path_params={"org_id": org_id, "sso_id": sso_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_download_org_saml_metadata",
    description='GET /api/v1/orgs/{org_id}/ssos/{sso_id}/metadata.xml\n\ndownloadOrgSamlMetadata\n\nDownload Org SAML Metadata\n\nExample of metadata.xml:\n```xml\n<?xml version="1.0" encoding="UTF-8"?><md:EntityDescriptor xmlns:md="urn:oasis:names:tc:SAML:2.0:metadata" entityID="https://api.mist.com/api/v1/saml/5hdF5g/login" validUntil="2027-10-12T21:59:01Z" xmlns:ds="http://www.w3.org/2000/09/xmldsig#">\n    <md:SPSSODescriptor AuthnRequestsSigned="false" WantAssertionsSigned="true" protocolSupportEnumeration="urn:oasis:names:tc:SAML:2.0:protocol">\n        <md:SingleLogoutService Binding="urn:oasis:names:tc:SAML:2...',
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_download_org_saml_metadata(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    sso_id: Annotated[str, Field(description="path parameter 'sso_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/orgs/{org_id}/ssos/{sso_id}/metadata.xml",
        path_params={"org_id": org_id, "sso_id": sso_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_get_org_saml_metadata",
    description="GET /api/v1/orgs/{org_id}/ssos/{sso_id}/metadata\n\ngetOrgSamlMetadata\n\nGet Org SAML Metadata",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_get_org_saml_metadata(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    sso_id: Annotated[str, Field(description="path parameter 'sso_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/orgs/{org_id}/ssos/{sso_id}/metadata",
        path_params={"org_id": org_id, "sso_id": sso_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_get_org_sso",
    description="GET /api/v1/orgs/{org_id}/ssos/{sso_id}\n\ngetOrgSso\n\nGet Org SSO Configuration Details",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_get_org_sso(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    sso_id: Annotated[str, Field(description="path parameter 'sso_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/orgs/{org_id}/ssos/{sso_id}",
        path_params={"org_id": org_id, "sso_id": sso_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_list_org_sso_latest_failures",
    description="GET /api/v1/orgs/{org_id}/ssos/{sso_id}/failures\n\nlistOrgSsoLatestFailures\n\nGet List of Org SSO Latest Failures",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_list_org_sso_latest_failures(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    sso_id: Annotated[str, Field(description="path parameter 'sso_id'")],
    start: Annotated[
        str | None, Field(description='Start time (epoch timestamp in seconds, or relative string like "-1d", "-1w")')
    ] = None,
    end: Annotated[
        str | None,
        Field(description='End time (epoch timestamp in seconds, or relative string like "-1d", "-2h", "now")'),
    ] = None,
    duration: Annotated[str, Field(description="Duration like 7d, 2w")] = "1d",
    limit: Annotated[int, Field(description="query parameter 'limit'")] = 100,
    page: Annotated[int, Field(description="query parameter 'page'")] = 1,
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/orgs/{org_id}/ssos/{sso_id}/failures",
        path_params={"org_id": org_id, "sso_id": sso_id},
        query_params={"start": start, "end": end, "duration": duration, "limit": limit, "page": page},
        body=None,
    )


@_mcp_tool(
    name="mist_list_org_ssos",
    description="GET /api/v1/orgs/{org_id}/ssos\n\nlistOrgSsos\n\nGet List of Org SSO Configuration",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_list_org_ssos(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    limit: Annotated[int, Field(description="query parameter 'limit'")] = 100,
    page: Annotated[int, Field(description="query parameter 'page'")] = 1,
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/orgs/{org_id}/ssos",
        path_params={"org_id": org_id},
        query_params={"limit": limit, "page": page},
        body=None,
    )


@_mcp_tool(
    name="mist_update_org_sso",
    description="PUT /api/v1/orgs/{org_id}/ssos/{sso_id}\n\nupdateOrgSso\n\nUpdate Org SSO Configuration",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_update_org_sso(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    sso_id: Annotated[str, Field(description="path parameter 'sso_id'")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request Body")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "PUT",
        "/api/v1/orgs/{org_id}/ssos/{sso_id}",
        path_params={"org_id": org_id, "sso_id": sso_id},
        query_params=None,
        body=body,
    )
