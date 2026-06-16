"""Generated EdgeConnect tools — DO NOT EDIT BY HAND.

Emitted by ``scripts/generate_edgeconnect_tools.py`` from
``vendor/edgeconnect/EdgeConnect-9-7-REST-API.json``. Regenerate via:

    uv run python scripts/generate_edgeconnect_tools.py

Tag: ``license``
Operations in this file: 14
"""

# ruff: noqa: E501, N803
from __future__ import annotations

from typing import Annotated, Any

from fastmcp import Context
from pydantic import Field

from hpe_networking_mcp.platforms._common.annotations import Capability
from hpe_networking_mcp.platforms.edgeconnect._registry import tool
from hpe_networking_mcp.platforms.edgeconnect.client import edgeconnect_request


@tool(
    name="edgeconnect_delete_license_portal_appliance_license_token",
    description="DELETE /license/portal/appliance/license/token\n\ndeleteLicenseToken442\n\nRemove license token from appliance",
    capability=Capability.WRITE_DELETE,
)
async def edgeconnect_delete_license_portal_appliance_license_token(
    ctx: Context,
    nePk: Annotated[
        str,
        Field(
            description="Network Element Primary Key - unique appliance identifier assigned by Orchestrator. Format: '<id>.NE' (e.g., '0.NE', '10.NE')."
        ),
    ],
) -> Any:
    query_params: dict[str, Any] = {}
    if nePk is not None:
        query_params["nePk"] = nePk
    return await edgeconnect_request(
        ctx,
        "DELETE",
        "/license/portal/appliance/license/token",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_license_management_settings",
    description="GET /license/managementSettings\n\ngetManagementSettings\n\nRetrieve license management settings",
    capability=Capability.READ,
)
async def edgeconnect_get_license_management_settings(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/license/managementSettings",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_license_nx",
    description="GET /license/nx\n\ngetNxLicensedAppliances\n\nRetrieve NX licensed appliances",
    capability=Capability.READ,
)
async def edgeconnect_get_license_nx(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/license/nx",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_license_portal_appliance",
    description="GET /license/portal/appliance\n\nlicensing440\n\nRetrieves portal licensed appliances",
    capability=Capability.READ,
)
async def edgeconnect_get_license_portal_appliance(
    ctx: Context,
    cached: Annotated[
        bool | None,
        Field(
            default=None,
            description="When true, returns data from local cache without contacting Portal. Default is false, which fetches fresh data from Portal.",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if cached is not None:
        query_params["cached"] = cached
    return await edgeconnect_request(
        ctx,
        "GET",
        "/license/portal/appliance",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_license_portal_appliance2",
    description="GET /license/portal/appliance2\n\ngetPortalLicensedAppliances2\n\nGet portal licensed appliances with timestamp",
    capability=Capability.READ,
)
async def edgeconnect_get_license_portal_appliance2(
    ctx: Context,
    cached: Annotated[
        bool | None,
        Field(
            default=None,
            description="When true, returns cached data without contacting the Portal. When false or omitted, fetches fresh data from the Portal and updates the cache.",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if cached is not None:
        query_params["cached"] = cached
    return await edgeconnect_request(
        ctx,
        "GET",
        "/license/portal/appliance2",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_license_portal_appliance_account",
    description="GET /license/portal/appliance/account\n\ngetApplianceAccount\n\nRetrieve portal-registered account for an appliance",
    capability=Capability.READ,
)
async def edgeconnect_get_license_portal_appliance_account(
    ctx: Context,
    nePk: Annotated[
        str,
        Field(
            description="Network Element Primary Key - unique appliance identifier assigned by Orchestrator. Format: '<id>.NE' (e.g., '0.NE', '10.NE')."
        ),
    ],
) -> Any:
    query_params: dict[str, Any] = {}
    if nePk is not None:
        query_params["nePk"] = nePk
    return await edgeconnect_request(
        ctx,
        "GET",
        "/license/portal/appliance/account",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_license_portal_appliance_account_discovered",
    description="GET /license/portal/appliance/account/discovered\n\ngetDiscoveredApplianceAccount\n\nGet portal account for discovered appliance",
    capability=Capability.READ,
)
async def edgeconnect_get_license_portal_appliance_account_discovered(
    ctx: Context,
    discoveredId: Annotated[
        str,
        Field(
            description="Unique identifier of the discovered appliance. Must be a valid integer ID from the discovered appliances list."
        ),
    ],
) -> Any:
    query_params: dict[str, Any] = {}
    if discoveredId is not None:
        query_params["discoveredId"] = discoveredId
    return await edgeconnect_request(
        ctx,
        "GET",
        "/license/portal/appliance/account/discovered",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_license_portal_summary",
    description="GET /license/portal/summary\n\nlicensing445\n\nRetrieve portal account license summary",
    capability=Capability.READ,
)
async def edgeconnect_get_license_portal_summary(
    ctx: Context,
    cached: Annotated[
        bool | None,
        Field(
            default=None,
            description="When true, returns cached license data from Orchestrator. When false or omitted, fetches fresh data directly from Cloud Portal.",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if cached is not None:
        query_params["cached"] = cached
    return await edgeconnect_request(
        ctx,
        "GET",
        "/license/portal/summary",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_license_portal_summary_account",
    description="GET /license/portal/summary/account\n\ngetAllAccountsPortalLicenseSummary\n\nRetrieve portal license summary for all accounts",
    capability=Capability.READ,
)
async def edgeconnect_get_license_portal_summary_account(
    ctx: Context,
    cached: Annotated[
        bool | None,
        Field(
            default=None,
            description="When true, returns cached license data from the Orchestrator. When false or omitted, fetches fresh data directly from Cloud Portal. Default is false.",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if cached is not None:
        query_params["cached"] = cached
    return await edgeconnect_request(
        ctx,
        "GET",
        "/license/portal/summary/account",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_license_vx",
    description="GET /license/vx\n\nlicensing446\n\nRetrieves VX licensed appliances",
    capability=Capability.READ,
)
async def edgeconnect_get_license_vx(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/license/vx",
        query_params=None,
    )


@tool(
    name="edgeconnect_post_license_portal_appliance_ec_account_license",
    description="POST /license/portal/appliance/ec/account/license\n\nlicensing450\n\nUpdate EC appliance account and license settings",
    capability=Capability.WRITE,
)
async def edgeconnect_post_license_portal_appliance_ec_account_license(
    ctx: Context,
    nePk: Annotated[
        str,
        Field(
            description="Network Element Primary Key - unique appliance identifier assigned by Orchestrator. Format: '<id>.NE' (e.g., '0.NE', '10.NE')."
        ),
    ],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    query_params: dict[str, Any] = {}
    if nePk is not None:
        query_params["nePk"] = nePk
    return await edgeconnect_request(
        ctx,
        "POST",
        "/license/portal/appliance/ec/account/license",
        query_params=query_params or None,
        body=body,
    )


@tool(
    name="edgeconnect_post_license_portal_appliance_grant",
    description="POST /license/portal/appliance/grant\n\ngrant441\n\nGrant an appliance a base license via HPE Aruba Networking EdgeConnect Cloud Portal",
    capability=Capability.WRITE,
)
async def edgeconnect_post_license_portal_appliance_grant(
    ctx: Context,
    nePk: Annotated[
        str,
        Field(
            description="Network Element Primary Key - unique appliance identifier assigned by Orchestrator. Format: '<id>.NE' (e.g., '0.NE', '10.NE')."
        ),
    ],
) -> Any:
    query_params: dict[str, Any] = {}
    if nePk is not None:
        query_params["nePk"] = nePk
    return await edgeconnect_request(
        ctx,
        "POST",
        "/license/portal/appliance/grant",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_post_license_portal_appliance_revoke",
    description="POST /license/portal/appliance/revoke\n\nrevokePortalLicense\n\nRevoke appliance base license via Cloud Portal",
    capability=Capability.WRITE,
)
async def edgeconnect_post_license_portal_appliance_revoke(
    ctx: Context,
    nePk: Annotated[
        str,
        Field(
            description="Network Element Primary Key - unique appliance identifier assigned by Orchestrator. Format: '<id>.NE' (e.g., '0.NE', '10.NE')."
        ),
    ],
) -> Any:
    query_params: dict[str, Any] = {}
    if nePk is not None:
        query_params["nePk"] = nePk
    return await edgeconnect_request(
        ctx,
        "POST",
        "/license/portal/appliance/revoke",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_post_license_portal_ec",
    description="POST /license/portal/ec\n\nchangeECLicenseSettings\n\nConfigure EC appliance license settings",
    capability=Capability.WRITE,
)
async def edgeconnect_post_license_portal_ec(
    ctx: Context,
    nePk: Annotated[
        str,
        Field(
            description="Network Element Primary Key - unique appliance identifier assigned by Orchestrator. Format: '<id>.NE' (e.g., '0.NE', '10.NE')."
        ),
    ],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    query_params: dict[str, Any] = {}
    if nePk is not None:
        query_params["nePk"] = nePk
    return await edgeconnect_request(
        ctx,
        "POST",
        "/license/portal/ec",
        query_params=query_params or None,
        body=body,
    )
