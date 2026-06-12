"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``scripts/_mist_generator.py`` from
``vendor/mist/mist_openapi.json``. Regenerate via:

    uv run python scripts/regenerate_mist_tools.py

Tag: ``Utilities MxEdge``
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
    name="mist_preempt_sites_mx_tunnel",
    description="POST /api/v1/sites/{site_id}/mxtunnels/{mxtunnel_id}/preempt_aps\n\npreemptSitesMxTunnel\n\nTo preempt AP’s which are not connected to preferred peer to the preferred peer",
    capability=Capability.WRITE,
)
async def mist_preempt_sites_mx_tunnel(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    mxtunnel_id: Annotated[str, Field(description="path parameter 'mxtunnel_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/sites/{site_id}/mxtunnels/{mxtunnel_id}/preempt_aps",
        path_params={"site_id": site_id, "mxtunnel_id": mxtunnel_id},
        query_params=None,
        body=None,
    )
