"""Generated EdgeConnect tools — DO NOT EDIT BY HAND.

Emitted by ``scripts/generate_edgeconnect_tools.py`` from
``vendor/edgeconnect/EdgeConnect-9-7-REST-API.json``. Regenerate via:

    uv run python scripts/generate_edgeconnect_tools.py

Tag: ``gmsRegistration``
Operations in this file: 4
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
    name="edgeconnect_get_gms_gms_registration",
    description="GET /gms/gmsRegistration\n\nmgmInterfaceByGet271\n\nGet GMS registration settings for appliance connectivity (deprecated)",
    capability=Capability.READ,
)
async def edgeconnect_get_gms_gms_registration(
    ctx: Context,
    nePk: Annotated[
        str | None,
        Field(
            default=None,
            description="Network Element Primary Key - unique appliance identifier assigned by Orchestrator. Format: '<id>.NE' (e.g., '0.NE', '10.NE'). When omitted, results are returned for all appliances.",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if nePk is not None:
        query_params["nePk"] = nePk
    return await edgeconnect_request(
        ctx,
        "GET",
        "/gms/gmsRegistration",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_gms_gms_registration2",
    description="GET /gms/gmsRegistration2\n\nmgmInterfaceByGet273\n\nGet GMS registration settings for appliance connectivity",
    capability=Capability.READ,
)
async def edgeconnect_get_gms_gms_registration2(
    ctx: Context,
    nePk: Annotated[
        str | None,
        Field(
            default=None,
            description="Network Element Primary Key - unique appliance identifier assigned by Orchestrator. Format: '<id>.NE' (e.g., '0.NE', '10.NE'). When omitted, results are returned for all appliances.",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if nePk is not None:
        query_params["nePk"] = nePk
    return await edgeconnect_request(
        ctx,
        "GET",
        "/gms/gmsRegistration2",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_post_gms_gms_registration",
    description="POST /gms/gmsRegistration\n\nmgmInterfaceByPost272\n\nUpdate GMS registration settings (deprecated)",
    capability=Capability.WRITE,
)
async def edgeconnect_post_gms_gms_registration(
    ctx: Context,
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request body")] = None,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/gms/gmsRegistration",
        query_params=None,
        body=body,
    )


@tool(
    name="edgeconnect_post_gms_gms_registration2",
    description="POST /gms/gmsRegistration2\n\nmgmInterfaceByPost274\n\nUpdate GMS registration settings for appliance connectivity",
    capability=Capability.WRITE,
)
async def edgeconnect_post_gms_gms_registration2(
    ctx: Context,
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request body")] = None,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/gms/gmsRegistration2",
        query_params=None,
        body=body,
    )
