"""Generated EdgeConnect tools — DO NOT EDIT BY HAND.

Emitted by ``scripts/generate_edgeconnect_tools.py`` from
``vendor/edgeconnect/EdgeConnect-9-7-REST-API.json``. Regenerate via:

    uv run python scripts/generate_edgeconnect_tools.py

Tag: ``ikeless``
Operations in this file: 5
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
    name="edgeconnect_get_ikeless_config",
    description="GET /ikeless/config\n\nikelessConfigGet417\n\nRetrieve IPSec UDP key material rotation configuration",
    capability=Capability.READ,
)
async def edgeconnect_get_ikeless_config(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/ikeless/config",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_ikeless_seed_history",
    description="GET /ikeless/seedHistory\n\nikelessHistory419\n\nRetrieve IPSec UDP key material history from orchestrator",
    capability=Capability.READ,
)
async def edgeconnect_get_ikeless_seed_history(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/ikeless/seedHistory",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_ikeless_seed_status",
    description="GET /ikeless/seedStatus\n\nikelessStatus420\n\nGet IPSec UDP key material status for all appliances",
    capability=Capability.READ,
)
async def edgeconnect_get_ikeless_seed_status(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/ikeless/seedStatus",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_ikeless_seed_status_appliance",
    description="GET /ikeless/seedStatus/appliance\n\nikelessStatusAppliance\n\nGet IPSec UDP key material status for a specific appliance",
    capability=Capability.READ,
)
async def edgeconnect_get_ikeless_seed_status_appliance(
    ctx: Context,
    nePk: Annotated[
        str,
        Field(
            description="Network Element Primary Key - unique appliance identifier assigned by Orchestrator. Format: '<id>.NE' (e.g., '0.NE', '10.NE')."
        ),
    ],
    fromCache: Annotated[
        bool,
        Field(
            description="Data source selector. When true, returns cached status from Orchestrator database. When false, queries the appliance directly (falls back to cache if appliance is unreachable)."
        ),
    ],
) -> Any:
    query_params: dict[str, Any] = {}
    if nePk is not None:
        query_params["nePk"] = nePk
    if fromCache is not None:
        query_params["fromCache"] = fromCache
    return await edgeconnect_request(
        ctx,
        "GET",
        "/ikeless/seedStatus/appliance",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_post_ikeless_config",
    description="POST /ikeless/config\n\nikelessConfigPost418\n\nUpdate IPSec UDP key material configuration and rotation schedule",
    capability=Capability.WRITE,
)
async def edgeconnect_post_ikeless_config(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/ikeless/config",
        query_params=None,
        body=body,
    )
