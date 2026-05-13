"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``hpe_networking_mcp.platforms.mist._generator``
from ``vendor/mist_openapi.json``. Regenerate via:

    uv run python -m hpe_networking_mcp.platforms.mist.regenerate

Tag: ``Orgs Maps``
Operations in this file: 2
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
    name="mist_import_org_map_to_site",
    description='POST /api/v1/orgs/{org_id}/sites/{site_name}/maps/import\n\nimportOrgMapToSite\n\nImport data from files is a multipart POST which has a file, an optional json, and an optional csv, to create floorplan, assign matching inventory to specific site, place ap if name or mac matches\n\n#### Request\n\n```\n"json": a JSON string describing your upload\n"file": a binary file\n```',
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_import_org_map_to_site(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    site_name: Annotated[str, Field(description="path parameter 'site_name'")],
    body: Annotated[
        dict[str, Any] | None,
        Field(
            default=None,
            description='a JSON string, site id required, vendor option: ekahau, ibwave, etc., import_all_floorplans: optional, default: false, import_height: optional, default: true, import_orientation: optional, default: true\n"file": a binary file, option: .es...',
        ),
    ] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/orgs/{org_id}/sites/{site_name}/maps/import",
        path_params={"org_id": org_id, "site_name": site_name},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_import_org_maps",
    description="POST /api/v1/orgs/{org_id}/maps/import\n\nimportOrgMaps\n\nImport data from files is a multipart POST which has a file, an optional json, and an optional csv, to create floorplan, assign matching inventory to specific site, place ap if name or mac matches\n\n### CSV File Format\n```csv\nVendor AP name,Mist AP Mac\nUS Office AP-2 - 5c:5b:35:00:00:02,5c5b35000002\n```",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_import_org_maps(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    body: Annotated[
        dict[str, Any] | None,
        Field(default=None, description="Request body for POST /api/v1/orgs/{org_id}/maps/import"),
    ] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/orgs/{org_id}/maps/import",
        path_params={"org_id": org_id},
        query_params=None,
        body=body,
    )
