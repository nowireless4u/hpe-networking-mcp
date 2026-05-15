"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``scripts/_mist_generator.py``
from ``vendor/mist_openapi.json``. Regenerate via:

    uv run python scripts/regenerate_mist_tools.py

Tag: ``Orgs WxTags``
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
    name="mist_create_org_wx_tag",
    description="POST /api/v1/orgs/{org_id}/wxtags\n\ncreateOrgWxTag\n\nCreate WxLAN Tag",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_create_org_wx_tag(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request Body")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/orgs/{org_id}/wxtags",
        path_params={"org_id": org_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_delete_org_wx_tag",
    description="DELETE /api/v1/orgs/{org_id}/wxtags/{wxtag_id}\n\ndeleteOrgWxTag\n\nDelete WxLAN Tag",
    tags={"mist", "mist_write", "mist_write_delete"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=True),
)
async def mist_delete_org_wx_tag(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    wxtag_id: Annotated[str, Field(description="path parameter 'wxtag_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "DELETE",
        "/api/v1/orgs/{org_id}/wxtags/{wxtag_id}",
        path_params={"org_id": org_id, "wxtag_id": wxtag_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_get_org_application_list",
    description="GET /api/v1/orgs/{org_id}/wxtags/apps\n\ngetOrgApplicationList\n\nGet Application List",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_get_org_application_list(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/orgs/{org_id}/wxtags/apps",
        path_params={"org_id": org_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_get_org_current_matching_clients_of_a_wx_tag",
    description="GET /api/v1/orgs/{org_id}/wxtags/{wxtag_id}/clients\n\ngetOrgCurrentMatchingClientsOfAWxTag\n\nGet Current Matching Clients of a WXLAN Tag",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_get_org_current_matching_clients_of_a_wx_tag(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    wxtag_id: Annotated[str, Field(description="path parameter 'wxtag_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/orgs/{org_id}/wxtags/{wxtag_id}/clients",
        path_params={"org_id": org_id, "wxtag_id": wxtag_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_get_org_wx_tag",
    description="GET /api/v1/orgs/{org_id}/wxtags/{wxtag_id}\n\ngetOrgWxTag\n\nGet WxLAN Tag Details",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_get_org_wx_tag(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    wxtag_id: Annotated[str, Field(description="path parameter 'wxtag_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/orgs/{org_id}/wxtags/{wxtag_id}",
        path_params={"org_id": org_id, "wxtag_id": wxtag_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_list_org_wx_tags",
    description="GET /api/v1/orgs/{org_id}/wxtags\n\nlistOrgWxTags\n\nGet List of Org WxLAN Tags",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_list_org_wx_tags(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    limit: Annotated[int, Field(description="query parameter 'limit'")] = 100,
    page: Annotated[int, Field(description="query parameter 'page'")] = 1,
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/orgs/{org_id}/wxtags",
        path_params={"org_id": org_id},
        query_params={"limit": limit, "page": page},
        body=None,
    )


@_mcp_tool(
    name="mist_update_org_wx_tag",
    description="PUT /api/v1/orgs/{org_id}/wxtags/{wxtag_id}\n\nupdateOrgWxTag\n\nUpdate WxLAN Tag",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_update_org_wx_tag(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    wxtag_id: Annotated[str, Field(description="path parameter 'wxtag_id'")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request Body")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "PUT",
        "/api/v1/orgs/{org_id}/wxtags/{wxtag_id}",
        path_params={"org_id": org_id, "wxtag_id": wxtag_id},
        query_params=None,
        body=body,
    )
