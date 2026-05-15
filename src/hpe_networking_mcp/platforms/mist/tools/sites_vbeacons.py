"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``scripts/_mist_generator.py``
from ``vendor/mist_openapi.json``. Regenerate via:

    uv run python scripts/regenerate_mist_tools.py

Tag: ``Sites vBeacons``
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
    name="mist_create_site_v_beacon",
    description="POST /api/v1/sites/{site_id}/vbeacons\n\ncreateSiteVBeacon\n\nCreate Virtual Beacon",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_create_site_v_beacon(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request Body")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/sites/{site_id}/vbeacons",
        path_params={"site_id": site_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_delete_site_v_beacon",
    description="DELETE /api/v1/sites/{site_id}/vbeacons/{vbeacon_id}\n\ndeleteSiteVBeacon\n\nDelete Site Virtual Beacon",
    tags={"mist", "mist_write", "mist_write_delete"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=True),
)
async def mist_delete_site_v_beacon(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    vbeacon_id: Annotated[str, Field(description="path parameter 'vbeacon_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "DELETE",
        "/api/v1/sites/{site_id}/vbeacons/{vbeacon_id}",
        path_params={"site_id": site_id, "vbeacon_id": vbeacon_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_get_site_v_beacon",
    description="GET /api/v1/sites/{site_id}/vbeacons/{vbeacon_id}\n\ngetSiteVBeacon\n\nGet Site Virtual Beacon Details",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_get_site_v_beacon(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    vbeacon_id: Annotated[str, Field(description="path parameter 'vbeacon_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/sites/{site_id}/vbeacons/{vbeacon_id}",
        path_params={"site_id": site_id, "vbeacon_id": vbeacon_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_list_site_v_beacons",
    description="GET /api/v1/sites/{site_id}/vbeacons\n\nlistSiteVBeacons\n\nGet List of Site Virtual Beacons",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_list_site_v_beacons(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    limit: Annotated[int, Field(description="query parameter 'limit'")] = 100,
    page: Annotated[int, Field(description="query parameter 'page'")] = 1,
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/sites/{site_id}/vbeacons",
        path_params={"site_id": site_id},
        query_params={"limit": limit, "page": page},
        body=None,
    )


@_mcp_tool(
    name="mist_update_site_v_beacon",
    description="PUT /api/v1/sites/{site_id}/vbeacons/{vbeacon_id}\n\nupdateSiteVBeacon\n\nUpdate Site Virtual Beacon",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_update_site_v_beacon(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    vbeacon_id: Annotated[str, Field(description="path parameter 'vbeacon_id'")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request Body")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "PUT",
        "/api/v1/sites/{site_id}/vbeacons/{vbeacon_id}",
        path_params={"site_id": site_id, "vbeacon_id": vbeacon_id},
        query_params=None,
        body=body,
    )
