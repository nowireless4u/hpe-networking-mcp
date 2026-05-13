"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``hpe_networking_mcp.platforms.mist._generator``
from ``vendor/mist_openapi.json``. Regenerate via:

    uv run python -m hpe_networking_mcp.platforms.mist.regenerate

Tag: ``Orgs Device Profiles``
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
    name="mist_assign_org_device_profile",
    description="POST /api/v1/orgs/{org_id}/deviceprofiles/{deviceprofile_id}/assign\n\nassignOrgDeviceProfile\n\nAssign Org Device Profile to Devices",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_assign_org_device_profile(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    deviceprofile_id: Annotated[str, Field(description="path parameter 'deviceprofile_id'")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request Body")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/orgs/{org_id}/deviceprofiles/{deviceprofile_id}/assign",
        path_params={"org_id": org_id, "deviceprofile_id": deviceprofile_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_create_org_device_profile",
    description="POST /api/v1/orgs/{org_id}/deviceprofiles\n\ncreateOrgDeviceProfile\n\nCreate Device Profile",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_create_org_device_profile(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request Body")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/orgs/{org_id}/deviceprofiles",
        path_params={"org_id": org_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_delete_org_device_profile",
    description="DELETE /api/v1/orgs/{org_id}/deviceprofiles/{deviceprofile_id}\n\ndeleteOrgDeviceProfile\n\nDelete Org Device Profile",
    tags={"mist", "mist_write", "mist_write_delete"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=True),
)
async def mist_delete_org_device_profile(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    deviceprofile_id: Annotated[str, Field(description="path parameter 'deviceprofile_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "DELETE",
        "/api/v1/orgs/{org_id}/deviceprofiles/{deviceprofile_id}",
        path_params={"org_id": org_id, "deviceprofile_id": deviceprofile_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_get_org_device_profile",
    description="GET /api/v1/orgs/{org_id}/deviceprofiles/{deviceprofile_id}\n\ngetOrgDeviceProfile\n\nGet Org device Profile Details",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_get_org_device_profile(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    deviceprofile_id: Annotated[str, Field(description="path parameter 'deviceprofile_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/orgs/{org_id}/deviceprofiles/{deviceprofile_id}",
        path_params={"org_id": org_id, "deviceprofile_id": deviceprofile_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_list_org_device_profiles",
    description="GET /api/v1/orgs/{org_id}/deviceprofiles\n\nlistOrgDeviceProfiles\n\nGet List of Org Device Profiles",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_list_org_device_profiles(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    type: Annotated[Any | None, Field(description="query parameter 'type'")] = None,
    limit: Annotated[int, Field(description="query parameter 'limit'")] = 100,
    page: Annotated[int, Field(description="query parameter 'page'")] = 1,
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/orgs/{org_id}/deviceprofiles",
        path_params={"org_id": org_id},
        query_params={"type": type, "limit": limit, "page": page},
        body=None,
    )


@_mcp_tool(
    name="mist_unassign_org_device_profile",
    description="POST /api/v1/orgs/{org_id}/deviceprofiles/{deviceprofile_id}/unassign\n\nunassignOrgDeviceProfile\n\nUnassign Org Device Profile from Devices",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_unassign_org_device_profile(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    deviceprofile_id: Annotated[str, Field(description="path parameter 'deviceprofile_id'")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request Body")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/orgs/{org_id}/deviceprofiles/{deviceprofile_id}/unassign",
        path_params={"org_id": org_id, "deviceprofile_id": deviceprofile_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_update_org_device_profile",
    description="PUT /api/v1/orgs/{org_id}/deviceprofiles/{deviceprofile_id}\n\nupdateOrgDeviceProfile\n\nUpdate Org Device Profile",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_update_org_device_profile(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    deviceprofile_id: Annotated[str, Field(description="path parameter 'deviceprofile_id'")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request Body")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "PUT",
        "/api/v1/orgs/{org_id}/deviceprofiles/{deviceprofile_id}",
        path_params={"org_id": org_id, "deviceprofile_id": deviceprofile_id},
        query_params=None,
        body=body,
    )
