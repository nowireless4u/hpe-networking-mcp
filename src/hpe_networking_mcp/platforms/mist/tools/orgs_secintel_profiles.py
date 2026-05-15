"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``scripts/_mist_generator.py``
from ``vendor/mist_openapi.json``. Regenerate via:

    uv run python scripts/regenerate_mist_tools.py

Tag: ``Orgs SecIntel Profiles``
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
    name="mist_create_org_sec_intel_profile",
    description="POST /api/v1/orgs/{org_id}/secintelprofiles\n\ncreateOrgSecIntelProfile\n\nCreate Sec Intel Profiles",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_create_org_sec_intel_profile(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request Body")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/orgs/{org_id}/secintelprofiles",
        path_params={"org_id": org_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_delete_org_sec_intel_profile",
    description="DELETE /api/v1/orgs/{org_id}/secintelprofiles/{secintelprofile_id}\n\ndeleteOrgSecIntelProfile\n\nDelete Sec Intel Profile",
    tags={"mist", "mist_write", "mist_write_delete"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=True),
)
async def mist_delete_org_sec_intel_profile(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    secintelprofile_id: Annotated[str, Field(description="path parameter 'secintelprofile_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "DELETE",
        "/api/v1/orgs/{org_id}/secintelprofiles/{secintelprofile_id}",
        path_params={"org_id": org_id, "secintelprofile_id": secintelprofile_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_get_org_sec_intel_profile",
    description="GET /api/v1/orgs/{org_id}/secintelprofiles/{secintelprofile_id}\n\ngetOrgSecIntelProfile\n\nGet Sec Intel Profile",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_get_org_sec_intel_profile(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    secintelprofile_id: Annotated[str, Field(description="path parameter 'secintelprofile_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/orgs/{org_id}/secintelprofiles/{secintelprofile_id}",
        path_params={"org_id": org_id, "secintelprofile_id": secintelprofile_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_list_org_sec_intel_profiles",
    description="GET /api/v1/orgs/{org_id}/secintelprofiles\n\nlistOrgSecIntelProfiles\n\nGet List of Sec Intel Profiles",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_list_org_sec_intel_profiles(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    limit: Annotated[int, Field(description="query parameter 'limit'")] = 100,
    page: Annotated[int, Field(description="query parameter 'page'")] = 1,
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/orgs/{org_id}/secintelprofiles",
        path_params={"org_id": org_id},
        query_params={"limit": limit, "page": page},
        body=None,
    )


@_mcp_tool(
    name="mist_update_org_sec_intel_profile",
    description="PUT /api/v1/orgs/{org_id}/secintelprofiles/{secintelprofile_id}\n\ncreateOrgSecIntelProfile\n\nUpdate Sec Intel Profile",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_update_org_sec_intel_profile(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    secintelprofile_id: Annotated[str, Field(description="path parameter 'secintelprofile_id'")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request Body")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "PUT",
        "/api/v1/orgs/{org_id}/secintelprofiles/{secintelprofile_id}",
        path_params={"org_id": org_id, "secintelprofile_id": secintelprofile_id},
        query_params=None,
        body=body,
    )
