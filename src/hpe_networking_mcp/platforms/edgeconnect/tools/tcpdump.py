"""Generated EdgeConnect tools — DO NOT EDIT BY HAND.

Emitted by ``scripts/generate_edgeconnect_tools.py`` from
``vendor/edgeconnect/EdgeConnect-9-7-REST-API.json``. Regenerate via:

    uv run python scripts/generate_edgeconnect_tools.py

Tag: ``tcpdump``
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
    name="edgeconnect_get_tcpdump_status",
    description="GET /tcpdump/status\n\ngetTcpdumpStatus\n\nGet packet capture status for an appliance",
    capability=Capability.READ,
)
async def edgeconnect_get_tcpdump_status(
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
        "/tcpdump/status",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_tcpdump_tcpdump_status",
    description="GET /tcpdump/tcpdumpStatus\n\ngetTcpdumpPollHandle\n\nGet poll handle of running packet capture",
    capability=Capability.READ,
)
async def edgeconnect_get_tcpdump_tcpdump_status(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/tcpdump/tcpdumpStatus",
        query_params=None,
    )


@tool(
    name="edgeconnect_post_tcpdump_run",
    description="POST /tcpdump/run\n\nrunTcpdump\n\nStart packet capture on appliances",
    capability=Capability.WRITE,
)
async def edgeconnect_post_tcpdump_run(
    ctx: Context,
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request body")] = None,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/tcpdump/run",
        query_params=None,
        body=body,
    )
