"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``scripts/_mist_generator.py`` from
``vendor/mist/mist_openapi.json``. Regenerate via:

    uv run python scripts/regenerate_mist_tools.py

Tag: ``Orgs SSO``
Operations in this file: 9
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
    name="mist_create_org_sso",
    description="POST /api/v1/orgs/{org_id}/ssos\n\ncreateOrgSso\n\nCreate an organization SSO identity provider configuration, including provider settings and role-handling behavior.",
    capability=Capability.WRITE,
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
    description="DELETE /api/v1/orgs/{org_id}/ssos/{sso_id}\n\ndeleteOrgSso\n\nDelete an organization SSO identity provider configuration so it can no longer be used for administrator login.",
    capability=Capability.WRITE_DELETE,
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
    description="POST /api/v1/orgs/{org_id}/ssos/{sso_id}/delete_admins\n\ndeleteOrgSsoAdmins\n\nRemove SSO-linked organization administrator accounts by email for this SSO profile.",
    capability=Capability.WRITE,
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
    description='GET /api/v1/orgs/{org_id}/ssos/{sso_id}/metadata.xml\n\ndownloadOrgSamlMetadata\n\nDownload generated SAML service provider metadata XML for this\norganization SSO configuration. Use this XML to configure the identity provider\nwith Mist service-provider details such as entity ID, ACS URL, logout URL,\nNameID format, and requested attributes.\n\n\nExample of metadata.xml:\n```xml\n<?xml version=\\"1.0\\" encoding=\\"UTF-8\\"?><md:EntityDescriptor xmlns:md=\\"urn:oasis:names:tc:SAML:2.0:metadata\\" entityID=\\"https://api.mist.com/api/v1/saml/5hdF5g/login\\"\\ validUntil=\\"2027-10-12T21:59:01Z\\" xmlns:ds=\\"http:...',
    capability=Capability.READ,
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
    description="GET /api/v1/orgs/{org_id}/ssos/{sso_id}/metadata\n\ngetOrgSamlMetadata\n\nReturn generated SAML service provider metadata for this organization SSO configuration as JSON.",
    capability=Capability.READ,
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
    description="GET /api/v1/orgs/{org_id}/ssos/{sso_id}\n\ngetOrgSso\n\nReturn one organization SSO identity provider configuration, including provider settings and generated SSO URLs.",
    capability=Capability.READ,
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
    description="GET /api/v1/orgs/{org_id}/ssos/{sso_id}/failures\n\nlistOrgSsoLatestFailures\n\nList recent authentication failures for this organization SSO configuration, including failure details and captured SAML assertion data when available.",
    capability=Capability.READ,
)
async def mist_list_org_sso_latest_failures(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    sso_id: Annotated[str, Field(description="path parameter 'sso_id'")],
    start: Annotated[
        str | None,
        Field(
            description="Lower bound of the time range, as an epoch timestamp in seconds or a relative value such as `-1d` or `-1w`"
        ),
    ] = None,
    end: Annotated[
        str | None,
        Field(
            description="Upper bound of the time range, as an epoch timestamp in seconds or a relative value such as `-1d`, `-2h`, or `now`"
        ),
    ] = None,
    duration: Annotated[
        str, Field(description="Time range duration for the query, using relative units such as `10m`, `7d`, or `2w`")
    ] = "1d",
    limit: Annotated[int, Field(description="Maximum number of results to return per page")] = 100,
    page: Annotated[
        int, Field(description="Select the page number to return when using page-based pagination; starts at `1`")
    ] = 1,
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
    description="GET /api/v1/orgs/{org_id}/ssos\n\nlistOrgSsos\n\nList SSO identity provider configurations defined for this organization.",
    capability=Capability.READ,
)
async def mist_list_org_ssos(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    limit: Annotated[int, Field(description="Maximum number of results to return per page")] = 100,
    page: Annotated[
        int, Field(description="Select the page number to return when using page-based pagination; starts at `1`")
    ] = 1,
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
    description="PUT /api/v1/orgs/{org_id}/ssos/{sso_id}\n\nupdateOrgSso\n\nUpdate an organization SSO identity provider configuration, such as IdP URLs, certificates, issuer, NameID format, and unmatched-role handling.",
    capability=Capability.WRITE,
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
