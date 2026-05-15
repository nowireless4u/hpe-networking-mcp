"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``scripts/_mist_generator.py``
from ``vendor/mist_openapi.json``. Regenerate via:

    uv run python scripts/regenerate_mist_tools.py

Tag: ``MSPs SSO``
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
    name="mist_create_msp_sso",
    description="POST /api/v1/msps/{msp_id}/ssos\n\ncreateMspSso\n\nCreate MSP SSO profile",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_create_msp_sso(
    ctx: Context,
    msp_id: Annotated[str, Field(description="path parameter 'msp_id'")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request Body")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/msps/{msp_id}/ssos",
        path_params={"msp_id": msp_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_delete_msp_sso",
    description="DELETE /api/v1/msps/{msp_id}/ssos/{sso_id}\n\ndeleteMspSso\n\nDelete MSP SSO Config",
    tags={"mist", "mist_write", "mist_write_delete"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=True),
)
async def mist_delete_msp_sso(
    ctx: Context,
    msp_id: Annotated[str, Field(description="path parameter 'msp_id'")],
    sso_id: Annotated[str, Field(description="path parameter 'sso_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "DELETE",
        "/api/v1/msps/{msp_id}/ssos/{sso_id}",
        path_params={"msp_id": msp_id, "sso_id": sso_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_delete_msp_sso_admins",
    description="POST /api/v1/msps/{msp_id}/ssos/{sso_id}/delete_admins\n\ndeleteMspSsoAdmins\n\nDelete MSP SSO Admin users by email. This removes SSO-linked admin accounts from the organization.",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_delete_msp_sso_admins(
    ctx: Context,
    msp_id: Annotated[str, Field(description="path parameter 'msp_id'")],
    sso_id: Annotated[str, Field(description="path parameter 'sso_id'")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request Body")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/msps/{msp_id}/ssos/{sso_id}/delete_admins",
        path_params={"msp_id": msp_id, "sso_id": sso_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_download_msp_saml_metadata",
    description='GET /api/v1/msps/{msp_id}/ssos/{sso_id}/metadata.xml\n\ndownloadMspSamlMetadata\n\nDownload MSP SAML Metadata\n\nExample of metadata.xml:\n```xml\n<?xml version="1.0" encoding="UTF-8"?><md:EntityDescriptor xmlns:md="urn:oasis:names:tc:SAML:2.0:metadata" entityID="https://api.mist.com/api/v1/saml/5hdF5g/login" validUntil="2027-10-12T21:59:01Z" xmlns:ds="http://www.w3.org/2000/09/xmldsig#">\n  <md:SPSSODescriptor AuthnRequestsSigned="false" WantAssertionsSigned="true" protocolSupportEnumeration="urn:oasis:names:tc:SAML:2.0:protocol">\n      <md:SingleLogoutService Binding="urn:oasis:names:tc:SAML:2.0:b...',
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_download_msp_saml_metadata(
    ctx: Context,
    msp_id: Annotated[str, Field(description="path parameter 'msp_id'")],
    sso_id: Annotated[str, Field(description="path parameter 'sso_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/msps/{msp_id}/ssos/{sso_id}/metadata.xml",
        path_params={"msp_id": msp_id, "sso_id": sso_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_get_msp_saml_metadata",
    description="GET /api/v1/msps/{msp_id}/ssos/{sso_id}/metadata\n\ngetMspSamlMetadata\n\nGet MSP SAML Metadata",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_get_msp_saml_metadata(
    ctx: Context,
    msp_id: Annotated[str, Field(description="path parameter 'msp_id'")],
    sso_id: Annotated[str, Field(description="path parameter 'sso_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/msps/{msp_id}/ssos/{sso_id}/metadata",
        path_params={"msp_id": msp_id, "sso_id": sso_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_get_msp_sso",
    description="GET /api/v1/msps/{msp_id}/ssos/{sso_id}\n\ngetMspSso\n\nGet MSP SSO Config",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_get_msp_sso(
    ctx: Context,
    msp_id: Annotated[str, Field(description="path parameter 'msp_id'")],
    sso_id: Annotated[str, Field(description="path parameter 'sso_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/msps/{msp_id}/ssos/{sso_id}",
        path_params={"msp_id": msp_id, "sso_id": sso_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_list_msp_sso_latest_failures",
    description="GET /api/v1/msps/{msp_id}/ssos/{sso_id}/failures\n\nlistMspSsoLatestFailures\n\nGet List of MSP SSO Latest Failures",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_list_msp_sso_latest_failures(
    ctx: Context,
    msp_id: Annotated[str, Field(description="path parameter 'msp_id'")],
    sso_id: Annotated[str, Field(description="path parameter 'sso_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/msps/{msp_id}/ssos/{sso_id}/failures",
        path_params={"msp_id": msp_id, "sso_id": sso_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_list_msp_ssos",
    description="GET /api/v1/msps/{msp_id}/ssos\n\nlistMspSsos\n\nList MSP SSO Configs",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_list_msp_ssos(
    ctx: Context,
    msp_id: Annotated[str, Field(description="path parameter 'msp_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/msps/{msp_id}/ssos",
        path_params={"msp_id": msp_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_update_msp_sso",
    description="PUT /api/v1/msps/{msp_id}/ssos/{sso_id}\n\nupdateMspSso\n\nUpdate MSP SSO config",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_update_msp_sso(
    ctx: Context,
    msp_id: Annotated[str, Field(description="path parameter 'msp_id'")],
    sso_id: Annotated[str, Field(description="path parameter 'sso_id'")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request Body")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "PUT",
        "/api/v1/msps/{msp_id}/ssos/{sso_id}",
        path_params={"msp_id": msp_id, "sso_id": sso_id},
        query_params=None,
        body=body,
    )
