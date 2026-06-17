"""Generated EdgeConnect tools — DO NOT EDIT BY HAND.

Generated from ``vendor/edgeconnect/EdgeConnect-9-7-REST-API.json`` by the
maintainer-local EdgeConnect generator. These generated modules are committed
and are the runtime source of truth; regeneration is a release-time maintainer
workflow (the generator is intentionally not committed — see ``.gitignore``).

Tag: ``securitySettings``
Operations in this file: 3
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
    name="edgeconnect_get_security_advanced_settings",
    description="GET /security/advancedSettings\n\ngetAdvancedSecuritySettings550\n\nRetrieve advanced security settings",
    capability=Capability.READ,
)
async def edgeconnect_get_security_advanced_settings(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/security/advancedSettings",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_security_ddos_protection_profiles_appliance",
    description="GET /security/ddos/protectionProfiles/appliance\n\ngetApplianceProtectionProfiles\n\nRetrieve DDoS protection profiles for an appliance",
    capability=Capability.READ,
)
async def edgeconnect_get_security_ddos_protection_profiles_appliance(
    ctx: Context,
    nePk: Annotated[
        str,
        Field(
            description="Network Element Primary Key - unique appliance identifier assigned by Orchestrator. Format: '<id>.NE' (e.g., '0.NE', '10.NE')."
        ),
    ],
    cached: Annotated[
        bool | None,
        Field(
            default=None,
            description="Data source selector. When true, returns cached data from database; when false, fetches fresh data directly from the appliance and updates the cache.",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if nePk is not None:
        query_params["nePk"] = nePk
    if cached is not None:
        query_params["cached"] = cached
    return await edgeconnect_request(
        ctx,
        "GET",
        "/security/ddos/protectionProfiles/appliance",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_post_security_advanced_settings",
    description="POST /security/advancedSettings\n\npostAdvancedSecuritySettings551\n\nUpdate advanced security settings",
    capability=Capability.WRITE,
)
async def edgeconnect_post_security_advanced_settings(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/security/advancedSettings",
        query_params=None,
        body=body,
    )
