"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``scripts/_mist_generator.py``
from ``vendor/mist_openapi.json``. Regenerate via:

    uv run python scripts/regenerate_mist_tools.py

Tag: ``Orgs Wlans``
Operations in this file: 8
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
    name="mist_create_org_wlan",
    description="POST /api/v1/orgs/{org_id}/wlans\n\ncreateOrgWlan\n\nCreate Org Wlan",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_create_org_wlan(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request Body")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/orgs/{org_id}/wlans",
        path_params={"org_id": org_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_delete_org_wlan",
    description="DELETE /api/v1/orgs/{org_id}/wlans/{wlan_id}\n\ndeleteOrgWlan\n\nDelete Org WLAN",
    tags={"mist", "mist_write", "mist_write_delete"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=True),
)
async def mist_delete_org_wlan(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    wlan_id: Annotated[str, Field(description="path parameter 'wlan_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "DELETE",
        "/api/v1/orgs/{org_id}/wlans/{wlan_id}",
        path_params={"org_id": org_id, "wlan_id": wlan_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_delete_org_wlan_portal_image",
    description="DELETE /api/v1/orgs/{org_id}/wlans/{wlan_id}/portal_image\n\ndeleteOrgWlanPortalImage\n\nDelete Org WLAN Portal Image",
    tags={"mist", "mist_write", "mist_write_delete"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=True),
)
async def mist_delete_org_wlan_portal_image(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    wlan_id: Annotated[str, Field(description="path parameter 'wlan_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "DELETE",
        "/api/v1/orgs/{org_id}/wlans/{wlan_id}/portal_image",
        path_params={"org_id": org_id, "wlan_id": wlan_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_get_org_wlan",
    description="GET /api/v1/orgs/{org_id}/wlans/{wlan_id}\n\ngetOrgWLAN\n\nGet Org Wlan Detail",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_get_org_wlan(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    wlan_id: Annotated[str, Field(description="path parameter 'wlan_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/orgs/{org_id}/wlans/{wlan_id}",
        path_params={"org_id": org_id, "wlan_id": wlan_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_list_org_wlans",
    description="GET /api/v1/orgs/{org_id}/wlans\n\nlistOrgWlans\n\nGet List of Org Wlans",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_list_org_wlans(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    limit: Annotated[int, Field(description="query parameter 'limit'")] = 100,
    page: Annotated[int, Field(description="query parameter 'page'")] = 1,
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/orgs/{org_id}/wlans",
        path_params={"org_id": org_id},
        query_params={"limit": limit, "page": page},
        body=None,
    )


@_mcp_tool(
    name="mist_update_org_wlan",
    description="PUT /api/v1/orgs/{org_id}/wlans/{wlan_id}\n\nupdateOrgWlan\n\nUpdate Org Wlan",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_update_org_wlan(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    wlan_id: Annotated[str, Field(description="path parameter 'wlan_id'")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request Body")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "PUT",
        "/api/v1/orgs/{org_id}/wlans/{wlan_id}",
        path_params={"org_id": org_id, "wlan_id": wlan_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_update_org_wlan_portal_template",
    description="PUT /api/v1/orgs/{org_id}/wlans/{wlan_id}/portal_template\n\nupdateOrgWlanPortalTemplate\n\nUpdate a Portal Template\n\n#### Sponsor Email Template\nSponsor Email Template supports following template variables:\n\n| **Name** | **Description** |\n| --- | --- |\n| approve_url | Renders URL to approve the request; optionally &minutes=N query param can be appended to change the Authorization period of the guest, where N is a valid integer denoting number of minutes a guest remains authorized |\n| deny_url | Renders URL to reject the request |\n| guest_email | Renders Email ID of the guest |\n| guest_name | R...",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_update_org_wlan_portal_template(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    wlan_id: Annotated[str, Field(description="path parameter 'wlan_id'")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request Body")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "PUT",
        "/api/v1/orgs/{org_id}/wlans/{wlan_id}/portal_template",
        path_params={"org_id": org_id, "wlan_id": wlan_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_upload_org_wlan_portal_image",
    description="POST /api/v1/orgs/{org_id}/wlans/{wlan_id}/portal_image\n\nuploadOrgWlanPortalImage\n\nUpload Org WLAN Portal Image",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_upload_org_wlan_portal_image(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    wlan_id: Annotated[str, Field(description="path parameter 'wlan_id'")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request Body")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/orgs/{org_id}/wlans/{wlan_id}/portal_image",
        path_params={"org_id": org_id, "wlan_id": wlan_id},
        query_params=None,
        body=body,
    )
