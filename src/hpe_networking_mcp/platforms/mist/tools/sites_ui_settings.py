"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``scripts/_mist_generator.py`` from
``vendor/mist_openapi.json``. Regenerate via:

    uv run python scripts/regenerate_mist_tools.py

Tag: ``Sites UI Settings``
Operations in this file: 6
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
    name="mist_create_site_ui_settings",
    description="POST /api/v1/sites/{site_id}/uisettings\n\ncreateSiteUiSettings\n\nCreate a Site UI settings/databoard",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_create_site_ui_settings(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request Body")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/sites/{site_id}/uisettings",
        path_params={"site_id": site_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_delete_site_ui_setting",
    description="DELETE /api/v1/sites/{site_id}/uisettings/{uisetting_id}\n\ndeleteSiteUiSetting\n\nSite UI settings",
    tags={"mist", "mist_write", "mist_write_delete"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=True),
)
async def mist_delete_site_ui_setting(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    uisetting_id: Annotated[str, Field(description="path parameter 'uisetting_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "DELETE",
        "/api/v1/sites/{site_id}/uisettings/{uisetting_id}",
        path_params={"site_id": site_id, "uisetting_id": uisetting_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_get_site_ui_setting",
    description="GET /api/v1/sites/{site_id}/uisettings/{uisetting_id}\n\ngetSiteUiSetting\n\nSite UI settings",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_get_site_ui_setting(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    uisetting_id: Annotated[str, Field(description="path parameter 'uisetting_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/sites/{site_id}/uisettings/{uisetting_id}",
        path_params={"site_id": site_id, "uisetting_id": uisetting_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_list_site_ui_setting_derived",
    description="GET /api/v1/sites/{site_id}/uisettings/derived\n\nlistSiteUiSettingDerived\n\nGet both site UI settings(for_site=true) and org UI settings (for_site=false)",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_list_site_ui_setting_derived(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/sites/{site_id}/uisettings/derived",
        path_params={"site_id": site_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_list_site_ui_settings",
    description="GET /api/v1/sites/{site_id}/uisettings\n\nlistSiteUiSettings\n\nList the Site UI settings/databoard",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_list_site_ui_settings(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/sites/{site_id}/uisettings",
        path_params={"site_id": site_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_update_site_ui_setting",
    description="POST /api/v1/sites/{site_id}/uisettings/{uisetting_id}\n\nupdateSiteUiSetting\n\nSite UI settings",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_update_site_ui_setting(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    uisetting_id: Annotated[str, Field(description="path parameter 'uisetting_id'")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request Body")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/sites/{site_id}/uisettings/{uisetting_id}",
        path_params={"site_id": site_id, "uisetting_id": uisetting_id},
        query_params=None,
        body=body,
    )
