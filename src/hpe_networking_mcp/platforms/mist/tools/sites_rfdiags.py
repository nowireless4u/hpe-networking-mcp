"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``scripts/_mist_generator.py`` from
``vendor/mist_openapi.json``. Regenerate via:

    uv run python scripts/regenerate_mist_tools.py

Tag: ``Sites Rfdiags``
Operations in this file: 7
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
    name="mist_delete_site_rfdiag_recording",
    description="DELETE /api/v1/sites/{site_id}/rfdiags/{rfdiag_id}\n\ndeleteSiteRfdiagRecording\n\nDelete Recording",
    tags={"mist", "mist_write", "mist_write_delete"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=True),
)
async def mist_delete_site_rfdiag_recording(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    rfdiag_id: Annotated[str, Field(description="path parameter 'rfdiag_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "DELETE",
        "/api/v1/sites/{site_id}/rfdiags/{rfdiag_id}",
        path_params={"site_id": site_id, "rfdiag_id": rfdiag_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_download_site_rfdiag_recording",
    description="GET /api/v1/sites/{site_id}/rfdiags/{rfdiag_id}/download\n\ndownloadSiteRfdiagRecording\n\nDownload Recording\nDownload raw_events blob",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_download_site_rfdiag_recording(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    rfdiag_id: Annotated[str, Field(description="path parameter 'rfdiag_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/sites/{site_id}/rfdiags/{rfdiag_id}/download",
        path_params={"site_id": site_id, "rfdiag_id": rfdiag_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_get_site_rfdiag_recording",
    description="GET /api/v1/sites/{site_id}/rfdiags/{rfdiag_id}\n\ngetSiteRfdiagRecording\n\nGet RF Diag Recording Details",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_get_site_rfdiag_recording(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    rfdiag_id: Annotated[str, Field(description="path parameter 'rfdiag_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/sites/{site_id}/rfdiags/{rfdiag_id}",
        path_params={"site_id": site_id, "rfdiag_id": rfdiag_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_get_site_site_rfdiag_recording",
    description="GET /api/v1/sites/{site_id}/rfdiags\n\ngetSiteSiteRfdiagRecording\n\nList RF Glass Recording",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_get_site_site_rfdiag_recording(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    start: Annotated[
        str | None, Field(description='Start time (epoch timestamp in seconds, or relative string like "-1d", "-1w")')
    ] = None,
    end: Annotated[
        str | None,
        Field(description='End time (epoch timestamp in seconds, or relative string like "-1d", "-2h", "now")'),
    ] = None,
    duration: Annotated[str, Field(description="Duration like 7d, 2w")] = "1d",
    limit: Annotated[int, Field(description="query parameter 'limit'")] = 100,
    page: Annotated[int, Field(description="query parameter 'page'")] = 1,
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/sites/{site_id}/rfdiags",
        path_params={"site_id": site_id},
        query_params={"start": start, "end": end, "duration": duration, "limit": limit, "page": page},
        body=None,
    )


@_mcp_tool(
    name="mist_start_site_recording",
    description="POST /api/v1/sites/{site_id}/rfdiags\n\nstartSiteRecording\n\nStart RF Glass Recording",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_start_site_recording(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request Body")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/sites/{site_id}/rfdiags",
        path_params={"site_id": site_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_stop_site_rfdiag_recording",
    description="POST /api/v1/sites/{site_id}/rfdiags/{rfdiag_id}/stop\n\nstopSiteRfdiagRecording\n\nIf the recording session is active for the given rfdiag_id, it will finish the recording. duration and end_time will be updated to reflect the correct values.",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_stop_site_rfdiag_recording(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    rfdiag_id: Annotated[str, Field(description="path parameter 'rfdiag_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/sites/{site_id}/rfdiags/{rfdiag_id}/stop",
        path_params={"site_id": site_id, "rfdiag_id": rfdiag_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_update_site_rfdiag_recording",
    description="PUT /api/v1/sites/{site_id}/rfdiags/{rfdiag_id}\n\nupdateSiteRfdiagRecording\n\nUpdate Recording",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_update_site_rfdiag_recording(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    rfdiag_id: Annotated[str, Field(description="path parameter 'rfdiag_id'")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request Body")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "PUT",
        "/api/v1/sites/{site_id}/rfdiags/{rfdiag_id}",
        path_params={"site_id": site_id, "rfdiag_id": rfdiag_id},
        query_params=None,
        body=body,
    )
