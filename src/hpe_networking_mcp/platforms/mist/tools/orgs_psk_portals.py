"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``scripts/_mist_generator.py`` from
``vendor/mist/mist_openapi.json``. Regenerate via:

    uv run python scripts/regenerate_mist_tools.py

Tag: ``Orgs Psk Portals``
Operations in this file: 11
"""

# ruff: noqa: E501

from __future__ import annotations

from typing import Annotated, Any

from fastmcp import Context
from pydantic import Field

from hpe_networking_mcp.platforms._common.annotations import Capability
from hpe_networking_mcp.platforms.mist._client import mist_request
from hpe_networking_mcp.platforms.mist._registry import tool as _mcp_tool


@_mcp_tool(
    name="mist_count_org_psk_portal_logs",
    description="GET /api/v1/orgs/{org_id}/pskportals/logs/count\n\ncountOrgPskPortalLogs\n\nCount PSK Portal log entries across the organization, optionally grouped by `distinct` and filtered by time range.",
    capability=Capability.READ,
)
async def mist_count_org_psk_portal_logs(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    distinct: Annotated[
        Any | None,
        Field(
            description="Field used to group this count response. enum: `admin_id`, `admin_name`, `psk_id`, `psk_name`, `pskportal_id`, `user_id`"
        ),
    ] = None,
    start: Annotated[
        str | None,
        Field(
            description="Lower bound of the time range, as an epoch timestamp in seconds or a relative value such as `-1d` or `-1w`"
        ),
    ] = None,
    end: Annotated[
        str | None,
        Field(
            description="Upper bound of the time range, as an epoch timestamp in seconds or a relative value such as `-1d`, `-2h`, or `now`"
        ),
    ] = None,
    duration: Annotated[
        str, Field(description="Time range duration for the query, using relative units such as `10m`, `7d`, or `2w`")
    ] = "1d",
    limit: Annotated[int, Field(description="Maximum number of results to return per page")] = 100,
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/orgs/{org_id}/pskportals/logs/count",
        path_params={"org_id": org_id},
        query_params={"distinct": distinct, "start": start, "end": end, "duration": duration, "limit": limit},
        body=None,
    )


@_mcp_tool(
    name="mist_create_org_psk_portal",
    description="POST /api/v1/orgs/{org_id}/pskportals\n\ncreateOrgPskPortal\n\nCreate a self-service PSK Portal configuration for issuing personal PSKs, including SSID, BYOD or admin mode, SSO or sponsor authentication, passphrase rules, and expiry settings.",
    capability=Capability.WRITE,
)
async def mist_create_org_psk_portal(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    body: Annotated[
        dict[str, Any] | None, Field(default=None, description="Request body for POST /api/v1/orgs/{org_id}/pskportals")
    ] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/orgs/{org_id}/pskportals",
        path_params={"org_id": org_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_delete_org_psk_portal",
    description="DELETE /api/v1/orgs/{org_id}/pskportals/{pskportal_id}\n\ndeleteOrgPskPortal\n\nDelete a PSK Portal configuration by portal ID, removing the self-service entry point for issuing PSKs through that portal.",
    capability=Capability.WRITE_DELETE,
)
async def mist_delete_org_psk_portal(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    pskportal_id: Annotated[str, Field(description="path parameter 'pskportal_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "DELETE",
        "/api/v1/orgs/{org_id}/pskportals/{pskportal_id}",
        path_params={"org_id": org_id, "pskportal_id": pskportal_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_delete_org_psk_portal_image",
    description="DELETE /api/v1/orgs/{org_id}/pskportals/{pskportal_id}/portal_image\n\ndeleteOrgPskPortalImage\n\nDelete the custom background image for a PSK Portal. If no image is configured, the PSK Portal uses the default background image.",
    capability=Capability.WRITE_DELETE,
)
async def mist_delete_org_psk_portal_image(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    pskportal_id: Annotated[str, Field(description="path parameter 'pskportal_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "DELETE",
        "/api/v1/orgs/{org_id}/pskportals/{pskportal_id}/portal_image",
        path_params={"org_id": org_id, "pskportal_id": pskportal_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_get_org_psk_portal",
    description="GET /api/v1/orgs/{org_id}/pskportals/{pskportal_id}\n\ngetOrgPskPortal\n\nRetrieve PSK Portal configuration details, including SSID, mode, authentication, SSO, passphrase, expiry, notification, and template URLs.",
    capability=Capability.READ,
)
async def mist_get_org_psk_portal(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    pskportal_id: Annotated[str, Field(description="path parameter 'pskportal_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/orgs/{org_id}/pskportals/{pskportal_id}",
        path_params={"org_id": org_id, "pskportal_id": pskportal_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_list_org_psk_portal_logs",
    description="GET /api/v1/orgs/{org_id}/pskportals/logs\n\nlistOrgPskPortalLogs\n\nList PSK Portal log entries in the organization for the selected time range.",
    capability=Capability.READ,
)
async def mist_list_org_psk_portal_logs(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    start: Annotated[
        str | None,
        Field(
            description="Lower bound of the time range, as an epoch timestamp in seconds or a relative value such as `-1d` or `-1w`"
        ),
    ] = None,
    end: Annotated[
        str | None,
        Field(
            description="Upper bound of the time range, as an epoch timestamp in seconds or a relative value such as `-1d`, `-2h`, or `now`"
        ),
    ] = None,
    duration: Annotated[
        str, Field(description="Time range duration for the query, using relative units such as `10m`, `7d`, or `2w`")
    ] = "1d",
    limit: Annotated[int, Field(description="Maximum number of results to return per page")] = 100,
    page: Annotated[
        int, Field(description="Select the page number to return when using page-based pagination; starts at `1`")
    ] = 1,
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/orgs/{org_id}/pskportals/logs",
        path_params={"org_id": org_id},
        query_params={"start": start, "end": end, "duration": duration, "limit": limit, "page": page},
        body=None,
    )


@_mcp_tool(
    name="mist_list_org_psk_portals",
    description="GET /api/v1/orgs/{org_id}/pskportals\n\nlistOrgPskPortals\n\nList self-service PSK Portal configurations in the organization, including portal mode, SSID, authentication, expiry, and passphrase rules.",
    capability=Capability.READ,
)
async def mist_list_org_psk_portals(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    limit: Annotated[int, Field(description="Maximum number of results to return per page")] = 100,
    page: Annotated[
        int, Field(description="Select the page number to return when using page-based pagination; starts at `1`")
    ] = 1,
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/orgs/{org_id}/pskportals",
        path_params={"org_id": org_id},
        query_params={"limit": limit, "page": page},
        body=None,
    )


@_mcp_tool(
    name="mist_search_org_psk_portal_logs",
    description="GET /api/v1/orgs/{org_id}/pskportals/logs/search\n\nsearchOrgPskPortalLogs\n\nSearch PSK Portal log entries across the organization with filters for PSK, portal, admin, SSO NameID, and time range.",
    capability=Capability.READ,
)
async def mist_search_org_psk_portal_logs(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    psk_name: Annotated[str | None, Field(description="Filter PSK portal log results by PSK name")] = None,
    psk_id: Annotated[str | None, Field(description="Filter PSK portal log results by PSK identifier")] = None,
    pskportal_id: Annotated[
        str | None, Field(description="Filter PSK portal log results by PSK portal identifier")
    ] = None,
    id: Annotated[str | None, Field(description="Filter results by identifier")] = None,
    admin_name: Annotated[str | None, Field(description="Filter audit log results by administrator name")] = None,
    admin_id: Annotated[str | None, Field(description="Filter audit log results by administrator identifier")] = None,
    name_id: Annotated[str | None, Field(description="Filter results by name id")] = None,
    limit: Annotated[int, Field(description="Maximum number of results to return per page")] = 100,
    start: Annotated[
        str | None,
        Field(
            description="Lower bound of the time range, as an epoch timestamp in seconds or a relative value such as `-1d` or `-1w`"
        ),
    ] = None,
    end: Annotated[
        str | None,
        Field(
            description="Upper bound of the time range, as an epoch timestamp in seconds or a relative value such as `-1d`, `-2h`, or `now`"
        ),
    ] = None,
    duration: Annotated[
        str, Field(description="Time range duration for the query, using relative units such as `10m`, `7d`, or `2w`")
    ] = "1d",
    sort: Annotated[
        str, Field(description="On which field the list should be sorted, -prefix represents DESC order")
    ] = "timestamp",
    search_after: Annotated[
        str | None,
        Field(
            description="Pagination cursor for retrieving subsequent pages of results. This value is automatically populated by Mist in the `next` URL from the previous response and should not be manually constructed."
        ),
    ] = None,
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/orgs/{org_id}/pskportals/logs/search",
        path_params={"org_id": org_id},
        query_params={
            "psk_name": psk_name,
            "psk_id": psk_id,
            "pskportal_id": pskportal_id,
            "id": id,
            "admin_name": admin_name,
            "admin_id": admin_id,
            "name_id": name_id,
            "limit": limit,
            "start": start,
            "end": end,
            "duration": duration,
            "sort": sort,
            "search_after": search_after,
        },
        body=None,
    )


@_mcp_tool(
    name="mist_update_org_psk_portal",
    description="PUT /api/v1/orgs/{org_id}/pskportals/{pskportal_id}\n\nupdateOrgPskPortal\n\nUpdate a PSK Portal configuration, including SSID, mode, authentication, SSO, passphrase, expiry, notification, and template settings.",
    capability=Capability.WRITE,
)
async def mist_update_org_psk_portal(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    pskportal_id: Annotated[str, Field(description="path parameter 'pskportal_id'")],
    body: Annotated[
        dict[str, Any] | None,
        Field(default=None, description="Request body for PUT /api/v1/orgs/{org_id}/pskportals/{pskportal_id}"),
    ] = None,
) -> Any:
    return await mist_request(
        ctx,
        "PUT",
        "/api/v1/orgs/{org_id}/pskportals/{pskportal_id}",
        path_params={"org_id": org_id, "pskportal_id": pskportal_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_update_org_psk_portal_template",
    description="PUT /api/v1/orgs/{org_id}/pskportals/{pskportal_id}/portal_template\n\nupdateOrgPskPortalTemplate\n\nUpdate PSK Portal UI template settings, including alignment, color, logo, Powered by visibility, and Terms of Service text.",
    capability=Capability.WRITE,
)
async def mist_update_org_psk_portal_template(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    pskportal_id: Annotated[str, Field(description="path parameter 'pskportal_id'")],
    body: Annotated[
        dict[str, Any] | None,
        Field(
            default=None,
            description="Request body for PUT /api/v1/orgs/{org_id}/pskportals/{pskportal_id}/portal_template",
        ),
    ] = None,
) -> Any:
    return await mist_request(
        ctx,
        "PUT",
        "/api/v1/orgs/{org_id}/pskportals/{pskportal_id}/portal_template",
        path_params={"org_id": org_id, "pskportal_id": pskportal_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_upload_org_psk_portal_image",
    description="POST /api/v1/orgs/{org_id}/pskportals/{pskportal_id}/portal_image\n\nuploadOrgPskPortalImage\n\nUpload a custom background image for a PSK Portal.",
    capability=Capability.WRITE,
)
async def mist_upload_org_psk_portal_image(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    pskportal_id: Annotated[str, Field(description="path parameter 'pskportal_id'")],
    body: Annotated[
        dict[str, Any] | None,
        Field(
            default=None,
            description="Request body for POST /api/v1/orgs/{org_id}/pskportals/{pskportal_id}/portal_image",
        ),
    ] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/orgs/{org_id}/pskportals/{pskportal_id}/portal_image",
        path_params={"org_id": org_id, "pskportal_id": pskportal_id},
        query_params=None,
        body=body,
    )
