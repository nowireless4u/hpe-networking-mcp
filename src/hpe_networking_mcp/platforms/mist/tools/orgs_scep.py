"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``scripts/_mist_generator.py`` from
``vendor/mist/mist_openapi.json``. Regenerate via:

    uv run python scripts/regenerate_mist_tools.py

Tag: ``Orgs SCEP``
Operations in this file: 5
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
    name="mist_disable_org_mist_scep",
    description="DELETE /api/v1/orgs/{org_id}/setting/mist_scep\n\ndisableOrgMistScep\n\nDisable Mist SCEP for the organization and return the updated read-only SCEP settings.",
    capability=Capability.WRITE_DELETE,
)
async def mist_disable_org_mist_scep(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "DELETE",
        "/api/v1/orgs/{org_id}/setting/mist_scep",
        path_params={"org_id": org_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_get_org_mist_scep",
    description="GET /api/v1/orgs/{org_id}/setting/mist_scep\n\ngetOrgMistScep\n\nReturn Mist SCEP settings for the organization, including enabled and suspended status, configured certificate providers, and generated enrollment or webhook URLs.",
    capability=Capability.READ,
)
async def mist_get_org_mist_scep(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/orgs/{org_id}/setting/mist_scep",
        path_params={"org_id": org_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_list_org_issued_client_certificates",
    description="GET /api/v1/orgs/{org_id}/setting/mist_scep/client_certs\n\nlistOrgIssuedClientCertificates\n\nList Mist SCEP client certificates issued for the organization. Results can be filtered by SSO name ID, certificate serial number, or device ID; `serial_number` and `device_id` accept comma-separated values.",
    capability=Capability.READ,
)
async def mist_list_org_issued_client_certificates(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    sso_name_id: Annotated[str | None, Field(description="Filter results by sso name id")] = None,
    serial_number: Annotated[
        str | None, Field(description="Serial Number of the certificate. Accepts multiple comma-separated values.")
    ] = None,
    device_id: Annotated[
        str | None, Field(description="Filter results by device id. Accepts multiple comma-separated values.")
    ] = None,
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/orgs/{org_id}/setting/mist_scep/client_certs",
        path_params={"org_id": org_id},
        query_params={"sso_name_id": sso_name_id, "serial_number": serial_number, "device_id": device_id},
        body=None,
    )


@_mcp_tool(
    name="mist_revoke_org_issued_client_certificates",
    description="POST /api/v1/orgs/{org_id}/setting/mist_scep/client_certs/revoke\n\nrevokeOrgIssuedClientCertificates\n\nRevoke issued Mist SCEP client certificates by certificate serial number.",
    capability=Capability.WRITE,
)
async def mist_revoke_org_issued_client_certificates(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    body: Annotated[
        dict[str, Any] | None,
        Field(
            default=None,
            description="Request body for POST /api/v1/orgs/{org_id}/setting/mist_scep/client_certs/revoke",
        ),
    ] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/orgs/{org_id}/setting/mist_scep/client_certs/revoke",
        path_params={"org_id": org_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_update_org_mist_scep",
    description="PUT /api/v1/orgs/{org_id}/setting/mist_scep\n\nupdateOrgMistScep\n\nUpdate Mist SCEP settings for the organization, including enabled state, suspension state, and certificate providers.",
    capability=Capability.WRITE,
)
async def mist_update_org_mist_scep(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    body: Annotated[
        dict[str, Any] | None,
        Field(default=None, description="Request body for PUT /api/v1/orgs/{org_id}/setting/mist_scep"),
    ] = None,
) -> Any:
    return await mist_request(
        ctx,
        "PUT",
        "/api/v1/orgs/{org_id}/setting/mist_scep",
        path_params={"org_id": org_id},
        query_params=None,
        body=body,
    )
