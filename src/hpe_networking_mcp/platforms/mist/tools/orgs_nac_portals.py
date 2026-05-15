"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``scripts/_mist_generator.py``
from ``vendor/mist_openapi.json``. Regenerate via:

    uv run python scripts/regenerate_mist_tools.py

Tag: ``Orgs NAC Portals``
Operations in this file: 11
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
    name="mist_create_org_nac_portal",
    description="POST /api/v1/orgs/{org_id}/nacportals\n\ncreateOrgNacPortal\n\nCreate Org NAC Portal",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_create_org_nac_portal(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    body: Annotated[
        dict[str, Any] | None, Field(default=None, description="Request body for POST /api/v1/orgs/{org_id}/nacportals")
    ] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/orgs/{org_id}/nacportals",
        path_params={"org_id": org_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_delete_org_nac_portal",
    description="DELETE /api/v1/orgs/{org_id}/nacportals/{nacportal_id}\n\ndeleteOrgNacPortal\n\nDelete Org NAC Portal",
    tags={"mist", "mist_write", "mist_write_delete"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=True),
)
async def mist_delete_org_nac_portal(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    nacportal_id: Annotated[str, Field(description="path parameter 'nacportal_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "DELETE",
        "/api/v1/orgs/{org_id}/nacportals/{nacportal_id}",
        path_params={"org_id": org_id, "nacportal_id": nacportal_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_delete_org_nac_portal_image",
    description="DELETE /api/v1/orgs/{org_id}/nacportals/{nacportal_id}/portal_image\n\ndeleteOrgNacPortalImage\n\nDelete background image for NAC Portal\n\n\nIf image is not uploaded or is deleted, NAC Portal will use default image.",
    tags={"mist", "mist_write", "mist_write_delete"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=True),
)
async def mist_delete_org_nac_portal_image(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    nacportal_id: Annotated[str, Field(description="path parameter 'nacportal_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "DELETE",
        "/api/v1/orgs/{org_id}/nacportals/{nacportal_id}/portal_image",
        path_params={"org_id": org_id, "nacportal_id": nacportal_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_download_org_nac_portal_saml_metadata",
    description='GET /api/v1/orgs/{org_id}/nacportals/{nacportal_id}/saml_metadata.xml\n\ndownloadOrgNacPortalSamlMetadata\n\nDownload Org NAC Portal SAML Metadata\n\nExample of metadata.xml:\n```xml\n<?xml version="1.0" encoding="UTF-8"?><md:EntityDescriptor xmlns:md="urn:oasis:names:tc:SAML:2.0:metadata" entityID="https://api.mist.com/api/v1/saml/5hdF5g/login" validUntil="2027-10-12T21:59:01Z" xmlns:ds="http://www.w3.org/2000/09/xmldsig#">\n    <md:SPSSODescriptor AuthnRequestsSigned="false" WantAssertionsSigned="true" protocolSupportEnumeration="urn:oasis:names:tc:SAML:2.0:protocol">\n        <md:SingleLogoutServi...',
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_download_org_nac_portal_saml_metadata(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    nacportal_id: Annotated[str, Field(description="path parameter 'nacportal_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/orgs/{org_id}/nacportals/{nacportal_id}/saml_metadata.xml",
        path_params={"org_id": org_id, "nacportal_id": nacportal_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_get_org_nac_portal",
    description="GET /api/v1/orgs/{org_id}/nacportals/{nacportal_id}\n\ngetOrgNacPortal\n\nGet Org NAC Portal",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_get_org_nac_portal(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    nacportal_id: Annotated[str, Field(description="path parameter 'nacportal_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/orgs/{org_id}/nacportals/{nacportal_id}",
        path_params={"org_id": org_id, "nacportal_id": nacportal_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_get_org_nac_portal_saml_metadata",
    description="GET /api/v1/orgs/{org_id}/nacportals/{nacportal_id}/saml_metadata\n\ngetOrgNacPortalSamlMetadata\n\nGet Org NAC Portal SAML Metadata",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_get_org_nac_portal_saml_metadata(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    nacportal_id: Annotated[str, Field(description="path parameter 'nacportal_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/orgs/{org_id}/nacportals/{nacportal_id}/saml_metadata",
        path_params={"org_id": org_id, "nacportal_id": nacportal_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_list_org_nac_portal_sso_latest_failures",
    description="GET /api/v1/orgs/{org_id}/nacportals/{nacportal_id}/failures\n\nlistOrgNacPortalSsoLatestFailures\n\nGet List of Org NAC Portal SSO Latest Failures",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_list_org_nac_portal_sso_latest_failures(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    nacportal_id: Annotated[str, Field(description="path parameter 'nacportal_id'")],
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
        "/api/v1/orgs/{org_id}/nacportals/{nacportal_id}/failures",
        path_params={"org_id": org_id, "nacportal_id": nacportal_id},
        query_params={"start": start, "end": end, "duration": duration, "limit": limit, "page": page},
        body=None,
    )


@_mcp_tool(
    name="mist_list_org_nac_portals",
    description="GET /api/v1/orgs/{org_id}/nacportals\n\nlistOrgNacPortals\n\nList Org NAC Portals",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_list_org_nac_portals(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    limit: Annotated[int, Field(description="query parameter 'limit'")] = 100,
    page: Annotated[int, Field(description="query parameter 'page'")] = 1,
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/orgs/{org_id}/nacportals",
        path_params={"org_id": org_id},
        query_params={"limit": limit, "page": page},
        body=None,
    )


@_mcp_tool(
    name="mist_update_org_nac_portal",
    description="PUT /api/v1/orgs/{org_id}/nacportals/{nacportal_id}\n\nupdateOrgNacPortal\n\nUpdate Org NAC Portal",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_update_org_nac_portal(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    nacportal_id: Annotated[str, Field(description="path parameter 'nacportal_id'")],
    body: Annotated[
        dict[str, Any] | None,
        Field(default=None, description="Request body for PUT /api/v1/orgs/{org_id}/nacportals/{nacportal_id}"),
    ] = None,
) -> Any:
    return await mist_request(
        ctx,
        "PUT",
        "/api/v1/orgs/{org_id}/nacportals/{nacportal_id}",
        path_params={"org_id": org_id, "nacportal_id": nacportal_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_update_org_nac_portal_template",
    description="PUT /api/v1/orgs/{org_id}/nacportals/{nacportal_id}/portal_template\n\nupdateOrgNacPortalTemplate\n\nUpdate Org NAC Portal Template",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_update_org_nac_portal_template(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    nacportal_id: Annotated[str, Field(description="path parameter 'nacportal_id'")],
    body: Annotated[
        dict[str, Any] | None,
        Field(
            default=None,
            description="Request body for PUT /api/v1/orgs/{org_id}/nacportals/{nacportal_id}/portal_template",
        ),
    ] = None,
) -> Any:
    return await mist_request(
        ctx,
        "PUT",
        "/api/v1/orgs/{org_id}/nacportals/{nacportal_id}/portal_template",
        path_params={"org_id": org_id, "nacportal_id": nacportal_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_upload_org_nac_portal_image",
    description="POST /api/v1/orgs/{org_id}/nacportals/{nacportal_id}/portal_image\n\nuploadOrgNacPortalImage\n\nUpload background image for NAC Portal",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_upload_org_nac_portal_image(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    nacportal_id: Annotated[str, Field(description="path parameter 'nacportal_id'")],
    body: Annotated[
        dict[str, Any] | None,
        Field(
            default=None,
            description="Request body for POST /api/v1/orgs/{org_id}/nacportals/{nacportal_id}/portal_image",
        ),
    ] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/orgs/{org_id}/nacportals/{nacportal_id}/portal_image",
        path_params={"org_id": org_id, "nacportal_id": nacportal_id},
        query_params=None,
        body=body,
    )
