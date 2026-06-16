"""Generated EdgeConnect tools — DO NOT EDIT BY HAND.

Emitted by ``scripts/generate_edgeconnect_tools.py`` from
``vendor/edgeconnect/EdgeConnect-9-7-REST-API.json``. Regenerate via:

    uv run python scripts/generate_edgeconnect_tools.py

Tag: ``networkRoleAndSite``
Operations in this file: 2
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
    name="edgeconnect_get_appliance_network_role_and_site",
    description="GET /appliance/networkRoleAndSite\n\ngetNetworkRoleAndSite\n\nRetrieve appliance network role and site information",
    capability=Capability.READ,
)
async def edgeconnect_get_appliance_network_role_and_site(
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
        "/appliance/networkRoleAndSite",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_post_appliance_network_role_and_site",
    description="POST /appliance/networkRoleAndSite\n\nmodifyNetworkRoleAndSite\n\nUpdate appliance network role and site assignment",
    capability=Capability.WRITE,
)
async def edgeconnect_post_appliance_network_role_and_site(
    ctx: Context,
    nePk: Annotated[
        str,
        Field(
            description="Network Element Primary Key - unique appliance identifier assigned by Orchestrator. Format: '<id>.NE' (e.g., '0.NE', '10.NE')."
        ),
    ],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request body")] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if nePk is not None:
        query_params["nePk"] = nePk
    return await edgeconnect_request(
        ctx,
        "POST",
        "/appliance/networkRoleAndSite",
        query_params=query_params or None,
        body=body,
    )
