"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``scripts/_mist_generator.py`` from
``vendor/mist/mist_openapi.json``. Regenerate via:

    uv run python scripts/regenerate_mist_tools.py

Tag: ``MSPs Marvis``
Operations in this file: 1
"""

# ruff: noqa: E501

from __future__ import annotations

from typing import Annotated, Any

from fastmcp import Context
from pydantic import Field

from hpe_networking_mcp.platforms._common.annotations import Capability
from hpe_networking_mcp.platforms.mist._client import mist_request
from hpe_networking_mcp.platforms.mist._registry import tool as _mcp_tool


@_mcp_tool(
    name="mist_count_msps_marvis_actions",
    description="GET /api/v1/msps/{msp_id}/suggestion/count\n\ncountMspsMarvisActions\n\nReturn distinct counts of Marvis actions for this MSP grouped by the requested field, such as organization or status.",
    capability=Capability.READ,
)
async def mist_count_msps_marvis_actions(
    ctx: Context,
    msp_id: Annotated[str, Field(description="path parameter 'msp_id'")],
    distinct: Annotated[
        Any | None, Field(description="Field used to group this count response. enum: `org_id`, `status`")
    ] = None,
    limit: Annotated[int, Field(description="Maximum number of results to return per page")] = 100,
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/msps/{msp_id}/suggestion/count",
        path_params={"msp_id": msp_id},
        query_params={"distinct": distinct, "limit": limit},
        body=None,
    )
