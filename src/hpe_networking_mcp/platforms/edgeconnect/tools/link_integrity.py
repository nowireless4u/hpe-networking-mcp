"""Generated EdgeConnect tools — DO NOT EDIT BY HAND.

Emitted by ``scripts/generate_edgeconnect_tools.py`` from
``vendor/edgeconnect/EdgeConnect-9-7-REST-API.json``. Regenerate via:

    uv run python scripts/generate_edgeconnect_tools.py

Tag: ``linkIntegrity``
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
    name="edgeconnect_get_link_integrity_test_status",
    description="GET /linkIntegrityTest/status\n\ngetLinkIntegrityStatus\n\nRetrieve link integrity test status for an appliance",
    capability=Capability.READ,
)
async def edgeconnect_get_link_integrity_test_status(
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
        "/linkIntegrityTest/status",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_post_link_integrity_test_run",
    description="POST /linkIntegrityTest/run\n\nrunLinkIntegrityTest\n\nStart a bidirectional link integrity test between two appliances",
    capability=Capability.WRITE,
)
async def edgeconnect_post_link_integrity_test_run(
    ctx: Context,
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request body")] = None,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/linkIntegrityTest/run",
        query_params=None,
        body=body,
    )
