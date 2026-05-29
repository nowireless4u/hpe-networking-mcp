"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``scripts/_mist_generator.py`` from
``vendor/mist_openapi.json``. Regenerate via:

    uv run python scripts/regenerate_mist_tools.py

Tag: ``Sites Auto Map Assignment``
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
    name="mist_apply_site_auto_map_assignment",
    description="POST /api/v1/sites/{site_id}/apply_auto_map_assignment\n\napplySiteAutoMapAssignment\n\nApply (accept) auto map assignment results for a site. Devices are associated with their assigned maps. Omit `map_ids` or provide an empty list to accept all pending assignments; provide specific `map_ids` for a partial accept.",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_apply_site_auto_map_assignment(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request Body")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/sites/{site_id}/apply_auto_map_assignment",
        path_params={"site_id": site_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_cancel_site_auto_map_assignment",
    description="DELETE /api/v1/sites/{site_id}/auto_map_assignment\n\ncancelSiteAutoMapAssignment\n\nCancel an in-progress auto map assignment operation for the site. Validates that auto map assignment is currently running, notifies all APs to fetch new configuration, and sends a cancel command to the orchestration service.",
    tags={"mist", "mist_write", "mist_write_delete"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=True),
)
async def mist_cancel_site_auto_map_assignment(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "DELETE",
        "/api/v1/sites/{site_id}/auto_map_assignment",
        path_params={"site_id": site_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_clear_site_auto_map_assignment",
    description="POST /api/v1/sites/{site_id}/clear_auto_map_assignment\n\nclearSiteAutoMapAssignment\n\nClear (reject) auto map assignment results for a site without applying them. The cached assignment results are cleared. Omit `map_ids` or provide an empty list to reject all pending assignments; provide specific `map_ids` for a partial reject.",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_clear_site_auto_map_assignment(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request Body")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/sites/{site_id}/clear_auto_map_assignment",
        path_params={"site_id": site_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_get_site_auto_map_assignment_status",
    description="GET /api/v1/sites/{site_id}/auto_map_assignment\n\ngetSiteAutoMapAssignmentStatus\n\nGet the current status of auto map assignment for the site.",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_get_site_auto_map_assignment_status(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/sites/{site_id}/auto_map_assignment",
        path_params={"site_id": site_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_start_site_auto_map_assignment",
    description="POST /api/v1/sites/{site_id}/auto_map_assignment\n\nstartSiteAutoMapAssignment\n\nStart the auto map assignment process for a site. The service automatically assigns APs to maps based on BLE ranging data and requires at least 3 APs with compatible firmware and model support for BLE.\n\nRepeated POST requests while a site assignment is still running will be rejected.",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_start_site_auto_map_assignment(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request Body")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/sites/{site_id}/auto_map_assignment",
        path_params={"site_id": site_id},
        query_params=None,
        body=body,
    )
