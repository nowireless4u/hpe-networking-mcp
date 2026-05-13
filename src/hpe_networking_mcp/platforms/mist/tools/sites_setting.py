"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``hpe_networking_mcp.platforms.mist._generator``
from ``vendor/mist_openapi.json``. Regenerate via:

    uv run python -m hpe_networking_mcp.platforms.mist.regenerate

Tag: ``Sites Setting``
Operations in this file: 9
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
    name="mist_create_site_watched_stations",
    description="POST /api/v1/sites/{site_id}/setting/watched_station\n\ncreateSiteWatchedStations\n\nThis endpoint is to provide list of client macs for annotation as watched station.\n\nRetrieve the current clients list from `watched_station_url` under Site:Setting",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_create_site_watched_stations(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request Body")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/sites/{site_id}/setting/watched_station",
        path_params={"site_id": site_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_create_site_wireless_clients_allowlist",
    description="POST /api/v1/sites/{site_id}/setting/whitelist\n\ncreateSiteWirelessClientsAllowlist\n\nThis endpoint is to provide list of client macs for annotation as whitelist.\n\nRetrieve the current clients list from `whitelist_url` under Site:Setting",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_create_site_wireless_clients_allowlist(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request Body")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/sites/{site_id}/setting/whitelist",
        path_params={"site_id": site_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_create_site_wireless_clients_blocklist",
    description="POST /api/v1/sites/{site_id}/setting/blacklist\n\ncreateSiteWirelessClientsBlocklist\n\nThis endpoint is to provide list of client macs for annotation blacklist.\n\nRetrieve the current clients list `blacklist_url` under Site:Setting",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_create_site_wireless_clients_blocklist(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request Body")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/sites/{site_id}/setting/blacklist",
        path_params={"site_id": site_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_delete_site_watched_stations",
    description="DELETE /api/v1/sites/{site_id}/setting/watched_station\n\ndeleteSiteWatchedStations\n\nDelete Site Watched Station Clients",
    tags={"mist", "mist_write", "mist_write_delete"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=True),
)
async def mist_delete_site_watched_stations(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "DELETE",
        "/api/v1/sites/{site_id}/setting/watched_station",
        path_params={"site_id": site_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_delete_site_wireless_clients_allowlist",
    description="DELETE /api/v1/sites/{site_id}/setting/whitelist\n\ndeleteSiteWirelessClientsAllowlist\n\nDelete Site Whitelist Station Clients",
    tags={"mist", "mist_write", "mist_write_delete"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=True),
)
async def mist_delete_site_wireless_clients_allowlist(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "DELETE",
        "/api/v1/sites/{site_id}/setting/whitelist",
        path_params={"site_id": site_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_delete_site_wireless_clients_blocklist",
    description="DELETE /api/v1/sites/{site_id}/setting/blacklist\n\ndeleteSiteWirelessClientsBlocklist\n\nDelete Site Blacklist Station Clients",
    tags={"mist", "mist_write", "mist_write_delete"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=True),
)
async def mist_delete_site_wireless_clients_blocklist(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "DELETE",
        "/api/v1/sites/{site_id}/setting/blacklist",
        path_params={"site_id": site_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_get_site_setting",
    description="GET /api/v1/sites/{site_id}/setting\n\ngetSiteSetting\n\nGet the Site Settings",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_get_site_setting(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/sites/{site_id}/setting",
        path_params={"site_id": site_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_get_site_setting_derived",
    description="GET /api/v1/sites/{site_id}/setting/derived\n\ngetSiteSettingDerived\n\nGet the Derived Site Settings, generated by merging the Org level templates (network templates, gateway templates) and the Site level configuration. If the same parameter is defined in both scopes, the Site level one is used. In addition, the Zoom and Teams accounts are also merged into the derived settings.",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_get_site_setting_derived(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/sites/{site_id}/setting/derived",
        path_params={"site_id": site_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_update_site_settings",
    description="PUT /api/v1/sites/{site_id}/setting\n\nupdateSiteSettings\n\nUpdate Site Settings",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_update_site_settings(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request Body")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "PUT",
        "/api/v1/sites/{site_id}/setting",
        path_params={"site_id": site_id},
        query_params=None,
        body=body,
    )
