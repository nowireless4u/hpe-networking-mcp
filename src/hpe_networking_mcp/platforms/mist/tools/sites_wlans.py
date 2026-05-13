"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``hpe_networking_mcp.platforms.mist._generator``
from ``vendor/mist_openapi.json``. Regenerate via:

    uv run python -m hpe_networking_mcp.platforms.mist.regenerate

Tag: ``Sites Wlans``
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
    name="mist_create_site_wlan",
    description="POST /api/v1/sites/{site_id}/wlans\n\ncreateSiteWlan\n\nCreate Site WLAN",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_create_site_wlan(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request Body")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/sites/{site_id}/wlans",
        path_params={"site_id": site_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_delete_site_wlan",
    description="DELETE /api/v1/sites/{site_id}/wlans/{wlan_id}\n\ndeleteSiteWlan\n\nDelete Site WLAN",
    tags={"mist", "mist_write", "mist_write_delete"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=True),
)
async def mist_delete_site_wlan(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    wlan_id: Annotated[str, Field(description="path parameter 'wlan_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "DELETE",
        "/api/v1/sites/{site_id}/wlans/{wlan_id}",
        path_params={"site_id": site_id, "wlan_id": wlan_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_delete_site_wlan_portal_image",
    description="DELETE /api/v1/sites/{site_id}/wlans/{wlan_id}/portal_image\n\ndeleteSiteWlanPortalImage\n\nDelete Site WLAN Portal Image",
    tags={"mist", "mist_write", "mist_write_delete"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=True),
)
async def mist_delete_site_wlan_portal_image(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    wlan_id: Annotated[str, Field(description="path parameter 'wlan_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "DELETE",
        "/api/v1/sites/{site_id}/wlans/{wlan_id}/portal_image",
        path_params={"site_id": site_id, "wlan_id": wlan_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_get_site_wlan",
    description="GET /api/v1/sites/{site_id}/wlans/{wlan_id}\n\ngetSiteWlan\n\nGet Site WLAN",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_get_site_wlan(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    wlan_id: Annotated[str, Field(description="path parameter 'wlan_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/sites/{site_id}/wlans/{wlan_id}",
        path_params={"site_id": site_id, "wlan_id": wlan_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_list_site_wlans",
    description="GET /api/v1/sites/{site_id}/wlans\n\nlistSiteWlans\n\nGet List of Site WLANs",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_list_site_wlans(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    limit: Annotated[int, Field(description="query parameter 'limit'")] = 100,
    page: Annotated[int, Field(description="query parameter 'page'")] = 1,
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/sites/{site_id}/wlans",
        path_params={"site_id": site_id},
        query_params={"limit": limit, "page": page},
        body=None,
    )


@_mcp_tool(
    name="mist_list_site_wlans_derived",
    description="GET /api/v1/sites/{site_id}/wlans/derived\n\nlistSiteWlansDerived\n\nGet the list of derived Wlans for a Site",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_list_site_wlans_derived(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    resolve: Annotated[bool, Field(description="Whether to resolve SITE_VARS")] = False,
    wlan_id: Annotated[str | None, Field(description="Filter by WLAN ID")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/sites/{site_id}/wlans/derived",
        path_params={"site_id": site_id},
        query_params={"resolve": resolve, "wlan_id": wlan_id},
        body=None,
    )


@_mcp_tool(
    name="mist_update_site_wlan",
    description="PUT /api/v1/sites/{site_id}/wlans/{wlan_id}\n\nupdateSiteWlan\n\nUpdate Site WLAN",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_update_site_wlan(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    wlan_id: Annotated[str, Field(description="path parameter 'wlan_id'")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request Body")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "PUT",
        "/api/v1/sites/{site_id}/wlans/{wlan_id}",
        path_params={"site_id": site_id, "wlan_id": wlan_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_update_site_wlan_portal_template",
    description="PUT /api/v1/sites/{site_id}/wlans/{wlan_id}/portal_template\n\nupdateSiteWlanPortalTemplate\n\nUpdate a Portal Template\n\n#### Sponsor Email Template\nSponsor Email Template supports following template variables:\n\n| **Name** | **Description** |\n| --- | --- |\n| approve_url | Renders URL to approve the request; optionally &minutes=N query param can be appended to change the Authorization period of the guest, where N is a valid integer denoting number of minutes a guest remains authorized |\n| deny_url | Renders URL to reject the request |\n| guest_email | Renders Email ID of the guest |\n| guest_name ...",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_update_site_wlan_portal_template(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    wlan_id: Annotated[str, Field(description="path parameter 'wlan_id'")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request Body")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "PUT",
        "/api/v1/sites/{site_id}/wlans/{wlan_id}/portal_template",
        path_params={"site_id": site_id, "wlan_id": wlan_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_upload_site_wlan_portal_image",
    description="POST /api/v1/sites/{site_id}/wlans/{wlan_id}/portal_image\n\nuploadSiteWlanPortalImage\n\nWLAN Portal Image Upload",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_upload_site_wlan_portal_image(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    wlan_id: Annotated[str, Field(description="path parameter 'wlan_id'")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request Body")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/sites/{site_id}/wlans/{wlan_id}/portal_image",
        path_params={"site_id": site_id, "wlan_id": wlan_id},
        query_params=None,
        body=body,
    )
