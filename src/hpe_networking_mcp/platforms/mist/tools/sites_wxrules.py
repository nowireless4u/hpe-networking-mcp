"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``hpe_networking_mcp.platforms.mist._generator``
from ``vendor/mist_openapi.json``. Regenerate via:

    uv run python -m hpe_networking_mcp.platforms.mist.regenerate

Tag: ``Sites WxRules``
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
    name="mist_create_site_wx_rule",
    description="POST /api/v1/sites/{site_id}/wxrules\n\ncreateSiteWxRule\n\nCreate Site WxLan Rule",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_create_site_wx_rule(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request Body")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/sites/{site_id}/wxrules",
        path_params={"site_id": site_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_delete_site_wx_rule",
    description="DELETE /api/v1/sites/{site_id}/wxrules/{wxrule_id}\n\ndeleteSiteWxRule\n\nDelete Site WxLan Rule",
    tags={"mist", "mist_write", "mist_write_delete"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=True),
)
async def mist_delete_site_wx_rule(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    wxrule_id: Annotated[str, Field(description="path parameter 'wxrule_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "DELETE",
        "/api/v1/sites/{site_id}/wxrules/{wxrule_id}",
        path_params={"site_id": site_id, "wxrule_id": wxrule_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_get_site_wx_rule",
    description="GET /api/v1/sites/{site_id}/wxrules/{wxrule_id}\n\ngetSiteWxRule\n\nGet Site WxLan Rule Details",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_get_site_wx_rule(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    wxrule_id: Annotated[str, Field(description="path parameter 'wxrule_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/sites/{site_id}/wxrules/{wxrule_id}",
        path_params={"site_id": site_id, "wxrule_id": wxrule_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_list_site_wx_rules",
    description="GET /api/v1/sites/{site_id}/wxrules\n\nlistSiteWxRules\n\nGet List of Site WxLan Rules",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_list_site_wx_rules(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    limit: Annotated[int, Field(description="query parameter 'limit'")] = 100,
    page: Annotated[int, Field(description="query parameter 'page'")] = 1,
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/sites/{site_id}/wxrules",
        path_params={"site_id": site_id},
        query_params={"limit": limit, "page": page},
        body=None,
    )


@_mcp_tool(
    name="mist_list_site_wx_rules_derived",
    description="GET /api/v1/sites/{site_id}/wxrules/derived\n\nListSiteWxRulesDerived\n\nGet the list of derived WxLan Rule for a site",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_list_site_wx_rules_derived(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/sites/{site_id}/wxrules/derived",
        path_params={"site_id": site_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_update_site_wx_rule",
    description="PUT /api/v1/sites/{site_id}/wxrules/{wxrule_id}\n\nupdateSiteWxRule\n\nUpdate Site WxLan Rule",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_update_site_wx_rule(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    wxrule_id: Annotated[str, Field(description="path parameter 'wxrule_id'")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request Body")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "PUT",
        "/api/v1/sites/{site_id}/wxrules/{wxrule_id}",
        path_params={"site_id": site_id, "wxrule_id": wxrule_id},
        query_params=None,
        body=body,
    )
