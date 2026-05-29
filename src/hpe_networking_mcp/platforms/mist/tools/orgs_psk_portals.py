"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``scripts/_mist_generator.py`` from
``vendor/mist_openapi.json``. Regenerate via:

    uv run python scripts/regenerate_mist_tools.py

Tag: ``Orgs Psk Portals``
Operations in this file: 11
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
    name="mist_count_org_psk_portal_logs",
    description="GET /api/v1/orgs/{org_id}/pskportals/logs/count\n\ncountOrgPskPortalLogs\n\nCount by Distinct Attributes of PskPortal Logs",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_count_org_psk_portal_logs(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    distinct: Annotated[Any | None, Field(description="query parameter 'distinct'")] = None,
    start: Annotated[
        str | None, Field(description='Start time (epoch timestamp in seconds, or relative string like "-1d", "-1w")')
    ] = None,
    end: Annotated[
        str | None,
        Field(description='End time (epoch timestamp in seconds, or relative string like "-1d", "-2h", "now")'),
    ] = None,
    duration: Annotated[str, Field(description="Duration like 7d, 2w")] = "1d",
    limit: Annotated[int, Field(description="query parameter 'limit'")] = 100,
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
    description="POST /api/v1/orgs/{org_id}/pskportals\n\ncreateOrgPskPortal\n\nCreate Org Psk Portal",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
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
    description="DELETE /api/v1/orgs/{org_id}/pskportals/{pskportal_id}\n\ndeleteOrgPskPortal\n\nDelete Org Psk Portal",
    tags={"mist", "mist_write", "mist_write_delete"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=True),
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
    description="DELETE /api/v1/orgs/{org_id}/pskportals/{pskportal_id}/portal_image\n\ndeleteOrgPskPortalImage\n\nDelete background image for PskPortal\n\n\nIf image is not uploaded or is deleted, PskPortal will use default image.",
    tags={"mist", "mist_write", "mist_write_delete"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=True),
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
    description="GET /api/v1/orgs/{org_id}/pskportals/{pskportal_id}\n\ngetOrgPskPortal\n\nGet Org Psk Portal Details",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
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
    description="GET /api/v1/orgs/{org_id}/pskportals/logs\n\nlistOrgPskPortalLogs\n\nGet the list of PSK Portals Logs",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_list_org_psk_portal_logs(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
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
        "/api/v1/orgs/{org_id}/pskportals/logs",
        path_params={"org_id": org_id},
        query_params={"start": start, "end": end, "duration": duration, "limit": limit, "page": page},
        body=None,
    )


@_mcp_tool(
    name="mist_list_org_psk_portals",
    description="GET /api/v1/orgs/{org_id}/pskportals\n\nlistOrgPskPortals\n\nGet List of Org Psk Portals",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_list_org_psk_portals(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    limit: Annotated[int, Field(description="query parameter 'limit'")] = 100,
    page: Annotated[int, Field(description="query parameter 'page'")] = 1,
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
    description="GET /api/v1/orgs/{org_id}/pskportals/logs/search\n\nsearchOrgPskPortalLogs\n\nSearch Org PSK Portal Logs",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_search_org_psk_portal_logs(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    psk_name: Annotated[str | None, Field(description="query parameter 'psk_name'")] = None,
    psk_id: Annotated[str | None, Field(description="query parameter 'psk_id'")] = None,
    pskportal_id: Annotated[str | None, Field(description="query parameter 'pskportal_id'")] = None,
    id: Annotated[str | None, Field(description="audit_id")] = None,
    admin_name: Annotated[str | None, Field(description="query parameter 'admin_name'")] = None,
    admin_id: Annotated[str | None, Field(description="query parameter 'admin_id'")] = None,
    name_id: Annotated[str | None, Field(description="Name_id used in SSO")] = None,
    limit: Annotated[int, Field(description="query parameter 'limit'")] = 100,
    start: Annotated[
        str | None, Field(description='Start time (epoch timestamp in seconds, or relative string like "-1d", "-1w")')
    ] = None,
    end: Annotated[
        str | None,
        Field(description='End time (epoch timestamp in seconds, or relative string like "-1d", "-2h", "now")'),
    ] = None,
    duration: Annotated[str, Field(description="Duration like 7d, 2w")] = "1d",
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
    description="PUT /api/v1/orgs/{org_id}/pskportals/{pskportal_id}\n\nupdateOrgPskPortal\n\nUpdate Org Psk Portal",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
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
    description="PUT /api/v1/orgs/{org_id}/pskportals/{pskportal_id}/portal_template\n\nupdateOrgPskPortalTemplate\n\nUpdate Org Psk Portal Template",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
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
    description="POST /api/v1/orgs/{org_id}/pskportals/{pskportal_id}/portal_image\n\nuploadOrgPskPortalImage\n\nUpload background image for PskPortal",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
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
