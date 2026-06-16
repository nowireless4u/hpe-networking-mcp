"""Generated EdgeConnect tools — DO NOT EDIT BY HAND.

Emitted by ``scripts/generate_edgeconnect_tools.py`` from
``vendor/edgeconnect/EdgeConnect-9-7-REST-API.json``. Regenerate via:

    uv run python scripts/generate_edgeconnect_tools.py

Tag: ``ScheduledPDFreports``
Operations in this file: 1
"""

# ruff: noqa: E501
from __future__ import annotations

from typing import Annotated, Any

from fastmcp import Context
from pydantic import Field

from hpe_networking_mcp.platforms._common.annotations import Capability
from hpe_networking_mcp.platforms.edgeconnect._registry import tool
from hpe_networking_mcp.platforms.edgeconnect.client import edgeconnect_request


@tool(
    name="edgeconnect_get_reports",
    description="GET /reports\n\ngetScheduledPDFReports\n\nRetrieve scheduled PDF reports",
    capability=Capability.READ,
)
async def edgeconnect_get_reports(
    ctx: Context,
    id: Annotated[
        int | None,
        Field(
            default=None,
            description="Unique identifier of the report to download. When omitted, returns metadata for all available reports.",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if id is not None:
        query_params["id"] = id
    return await edgeconnect_request(
        ctx,
        "GET",
        "/reports",
        query_params=query_params or None,
    )
