"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``scripts/_mist_generator.py`` from
``vendor/mist/mist_openapi.json``. Regenerate via:

    uv run python scripts/regenerate_mist_tools.py

Tag: ``MSPs Logo``
Operations in this file: 2
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
    name="mist_delete_msp_logo",
    description="DELETE /api/v1/msps/{msp_id}/logo\n\ndeleteMspLogo\n\nRemove the logo configured for an advanced-tier MSP account.",
    capability=Capability.WRITE_DELETE,
)
async def mist_delete_msp_logo(
    ctx: Context,
    msp_id: Annotated[str, Field(description="path parameter 'msp_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "DELETE",
        "/api/v1/msps/{msp_id}/logo",
        path_params={"msp_id": msp_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_post_msp_logo",
    description="POST /api/v1/msps/{msp_id}/logo\n\npostMspLogo\n\nUpload or update the public logo URL for an advanced-tier MSP account.",
    capability=Capability.WRITE,
)
async def mist_post_msp_logo(
    ctx: Context,
    msp_id: Annotated[str, Field(description="path parameter 'msp_id'")],
    body: Annotated[
        dict[str, Any] | None, Field(default=None, description="Request body for POST /api/v1/msps/{msp_id}/logo")
    ] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/msps/{msp_id}/logo",
        path_params={"msp_id": msp_id},
        query_params=None,
        body=body,
    )
