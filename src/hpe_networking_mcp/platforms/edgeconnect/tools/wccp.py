"""Generated EdgeConnect tools — DO NOT EDIT BY HAND.

Emitted by ``scripts/generate_edgeconnect_tools.py`` from
``vendor/edgeconnect/EdgeConnect-9-7-REST-API.json``. Regenerate via:

    uv run python scripts/generate_edgeconnect_tools.py

Tag: ``wccp``
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
    name="edgeconnect_get_wccp_config_group",
    description="GET /wccp/config/group\n\nWccpConfigGroup937\n\nGet WCCP service groups configuration",
    capability=Capability.READ,
)
async def edgeconnect_get_wccp_config_group(
    ctx: Context,
    nePk: Annotated[
        str,
        Field(
            description="Network Element Primary Key - unique appliance identifier assigned by Orchestrator. Format: '<id>.NE' (e.g., '0.NE', '10.NE')."
        ),
    ],
    cached: Annotated[
        str | None,
        Field(
            default=None,
            description="When true, retrieves data from Orchestrator cache. When false, fetches fresh data directly from the appliance. Defaults to true if not specified.",
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
        "/wccp/config/group",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_wccp_config_system",
    description="GET /wccp/config/system\n\nWccpConfigSystem938\n\nGet WCCP system configuration",
    capability=Capability.READ,
)
async def edgeconnect_get_wccp_config_system(
    ctx: Context,
    nePk: Annotated[
        str,
        Field(
            description="Network Element Primary Key - unique appliance identifier assigned by Orchestrator. Format: '<id>.NE' (e.g., '0.NE', '10.NE')."
        ),
    ],
    cached: Annotated[
        str | None,
        Field(
            default=None,
            description="When true, retrieves data from Orchestrator cache. When false, fetches fresh data directly from the appliance. Defaults to true if not specified.",
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
        "/wccp/config/system",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_wccp_state",
    description="GET /wccp/state\n\nWccpState939\n\nGet WCCP operational state",
    capability=Capability.READ,
)
async def edgeconnect_get_wccp_state(
    ctx: Context,
    nePk: Annotated[
        str,
        Field(
            description="Network Element Primary Key - unique appliance identifier assigned by Orchestrator. Format: '<id>.NE' (e.g., '0.NE', '10.NE')."
        ),
    ],
    cached: Annotated[
        str | None,
        Field(
            default=None,
            description="When true, retrieves data from Orchestrator cache. When false, fetches fresh data directly from the appliance. Defaults to true if not specified.",
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
        "/wccp/state",
        query_params=query_params or None,
    )
