"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``scripts/_mist_generator.py`` from
``vendor/mist/mist_openapi.json``. Regenerate via:

    uv run python scripts/regenerate_mist_tools.py

Tag: ``MSPs``
Operations in this file: 5
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
    name="mist_create_msp",
    description="POST /api/v1/msps\n\ncreateMsp\n\nCreate a managed service provider account that can own organizations, organization groups, admins, licenses, and MSP-level settings.",
    capability=Capability.WRITE,
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
    description="DELETE /api/v1/msps/{msp_id}\n\ndeleteMsp\n\nDelete the MSP account and its MSP-level organization groups and privileges. This does not delete any organizations or administrator accounts.",
    capability=Capability.WRITE_DELETE,
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
    description="GET /api/v1/msps/{msp_id}\n\ngetMspDetails\n\nReturn MSP account details, including the display name, service tier, support-access setting, logo URL, custom URL, and timestamps.",
    capability=Capability.READ,
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
    description="GET /api/v1/msps/{msp_id}/search\n\nsearchMspOrgGroup\n\nSearch MSP resources by query string. Currently `type=orgs` returns matching organizations in this MSP.",
    capability=Capability.READ,
)
async def mist_search_msp_org_group(
    ctx: Context,
    msp_id: Annotated[str, Field(description="path parameter 'msp_id'")],
    type: Annotated[Any, Field(description="MSP search result type to return. enum: `orgs`")],
    q: Annotated[str, Field(description="Filter results by search string")],
    limit: Annotated[int, Field(description="Maximum number of results to return per page")] = 100,
    start: Annotated[
        str | None,
        Field(
            description="Lower bound of the time range, as an epoch timestamp in seconds or a relative value such as `-1d` or `-1w`"
        ),
    ] = None,
    end: Annotated[
        str | None,
        Field(
            description="Upper bound of the time range, as an epoch timestamp in seconds or a relative value such as `-1d`, `-2h`, or `now`"
        ),
    ] = None,
    duration: Annotated[
        str, Field(description="Time range duration for the query, using relative units such as `10m`, `7d`, or `2w`")
    ] = "1d",
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
    description="PUT /api/v1/msps/{msp_id}\n\nupdateMsp\n\nUpdate editable MSP account settings such as the display name, support-access setting, logo URL, or custom URL.",
    capability=Capability.WRITE,
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
