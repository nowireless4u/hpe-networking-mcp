"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``scripts/_mist_generator.py`` from
``vendor/mist_openapi.json``. Regenerate via:

    uv run python scripts/regenerate_mist_tools.py

Tag: ``MSPs``
Operations in this file: 5
"""

# ruff: noqa: E501

from __future__ import annotations

from typing import Annotated, Any

from fastmcp import Context
from mcp.types import ToolAnnotations
from pydantic import Field

from hpe_networking_mcp.platforms.mist._client import mist_request
from hpe_networking_mcp.platforms.mist._registry import tool as _mcp_tool


@_mcp_tool(
    name="mist_create_msp",
    description="POST /api/v1/msps\n\ncreateMsp\n\nCreate MSP account",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_create_msp(
    ctx: Context,
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request Body")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/msps",
        path_params=None,
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_delete_msp",
    description="DELETE /api/v1/msps/{msp_id}\n\ndeleteMsp\n\nDeleting MSP removes the MSP and OrgGroup under the MSP as well as all privileges associated with them. It does not remove any Org or Admins",
    tags={"mist", "mist_write", "mist_write_delete"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=True),
)
async def mist_delete_msp(
    ctx: Context,
    msp_id: Annotated[str, Field(description="path parameter 'msp_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "DELETE",
        "/api/v1/msps/{msp_id}",
        path_params={"msp_id": msp_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_get_msp_details",
    description="GET /api/v1/msps/{msp_id}\n\ngetMspDetails\n\nGet MSP Detail",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_get_msp_details(
    ctx: Context,
    msp_id: Annotated[str, Field(description="path parameter 'msp_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/msps/{msp_id}",
        path_params={"msp_id": msp_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_search_msp_org_group",
    description="GET /api/v1/msps/{msp_id}/search\n\nsearchMspOrgGroup\n\nSearch in MSP Orgs",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_search_msp_org_group(
    ctx: Context,
    msp_id: Annotated[str, Field(description="path parameter 'msp_id'")],
    type: Annotated[Any, Field(description="Orgs")],
    q: Annotated[str, Field(description="Search string")],
    limit: Annotated[int, Field(description="query parameter 'limit'")] = 100,
    start: Annotated[
        str | None, Field(description='Start time (epoch timestamp in seconds, or relative string like "-1d", "-1w")')
    ] = None,
    end: Annotated[
        str | None,
        Field(description='End time (epoch timestamp in seconds, or relative string like "-1d", "-2h", "now")'),
    ] = None,
    duration: Annotated[str, Field(description="Duration like 7d, 2w")] = "1d",
    sort: Annotated[
        str, Field(description="On which field the list should be sorted, -prefix represents DESC order")
    ] = "timestamp",
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/msps/{msp_id}/search",
        path_params={"msp_id": msp_id},
        query_params={
            "type": type,
            "q": q,
            "limit": limit,
            "start": start,
            "end": end,
            "duration": duration,
            "sort": sort,
        },
        body=None,
    )


@_mcp_tool(
    name="mist_update_msp",
    description="PUT /api/v1/msps/{msp_id}\n\nupdateMsp\n\nUpdate MSP",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_update_msp(
    ctx: Context,
    msp_id: Annotated[str, Field(description="path parameter 'msp_id'")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request Body")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "PUT",
        "/api/v1/msps/{msp_id}",
        path_params={"msp_id": msp_id},
        query_params=None,
        body=body,
    )
