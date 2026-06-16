"""Generated EdgeConnect tools — DO NOT EDIT BY HAND.

Emitted by ``scripts/generate_edgeconnect_tools.py`` from
``vendor/edgeconnect/EdgeConnect-9-7-REST-API.json``. Regenerate via:

    uv run python scripts/generate_edgeconnect_tools.py

Tag: ``gmsLicense``
Operations in this file: 8
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
    name="edgeconnect_get_gms_license",
    description="GET /gmsLicense\n\nlicenseByGet361\n\nGet current license key and information",
    capability=Capability.READ,
)
async def edgeconnect_get_gms_license(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/gmsLicense",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_gms_license_aas_token_display",
    description="GET /gmsLicense/aas/token/display\n\ngetAASTokenDisplay\n\nRetrieve AAS license feature display metadata",
    capability=Capability.READ,
)
async def edgeconnect_get_gms_license_aas_token_display(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/gmsLicense/aas/token/display",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_gms_license_aas_token_stats",
    description="GET /gmsLicense/aas/token/stats\n\ngetAASTokenStats\n\nRetrieve AAS licensing runtime statistics",
    capability=Capability.READ,
)
async def edgeconnect_get_gms_license_aas_token_stats(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/gmsLicense/aas/token/stats",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_gms_license_aas_token_usage",
    description="GET /gmsLicense/aas/token/usage\n\ngetAASTokenUsage\n\nGet AAS license feature usage and limits",
    capability=Capability.READ,
)
async def edgeconnect_get_gms_license_aas_token_usage(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/gmsLicense/aas/token/usage",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_gms_license_validation",
    description="GET /gmsLicense/validation\n\nvalidateKey363\n\nValidate an encrypted license key without applying it",
    capability=Capability.READ,
)
async def edgeconnect_get_gms_license_validation(
    ctx: Context,
    licenseKey: Annotated[
        str,
        Field(
            description="Encrypted license key string to validate. The key is decrypted to extract serial number, max appliances, and optional expiration date in format: SERIAL#MAX[#DATE]."
        ),
    ],
) -> Any:
    query_params: dict[str, Any] = {}
    if licenseKey is not None:
        query_params["licenseKey"] = licenseKey
    return await edgeconnect_request(
        ctx,
        "GET",
        "/gmsLicense/validation",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_post_gms_license",
    description="POST /gmsLicense\n\nlicenseByPut362\n\nApply a new Orchestrator license key",
    capability=Capability.WRITE,
)
async def edgeconnect_post_gms_license(
    ctx: Context,
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request body")] = None,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/gmsLicense",
        query_params=None,
        body=body,
    )


@tool(
    name="edgeconnect_post_gms_license_aas_token_validate",
    description="POST /gmsLicense/aas/token/validate\n\nvalidateAASFeature\n\nValidate feature requests against AAS license limits",
    capability=Capability.WRITE,
)
async def edgeconnect_post_gms_license_aas_token_validate(
    ctx: Context,
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request body")] = None,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/gmsLicense/aas/token/validate",
        query_params=None,
        body=body,
    )


@tool(
    name="edgeconnect_post_gms_license_aas_token_validate_hub",
    description="POST /gmsLicense/aas/token/validate/hub\n\nvalidateAASFeatureHub\n\nValidate hub configurations against AAS license limits",
    capability=Capability.WRITE,
)
async def edgeconnect_post_gms_license_aas_token_validate_hub(
    ctx: Context,
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request body")] = None,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/gmsLicense/aas/token/validate/hub",
        query_params=None,
        body=body,
    )
