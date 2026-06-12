"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``scripts/_mist_generator.py`` from
``vendor/mist/mist_openapi.json``. Regenerate via:

    uv run python scripts/regenerate_mist_tools.py

Tag: ``MSPs Orgs``
Operations in this file: 8
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
    name="mist_create_msp_org",
    description="POST /api/v1/msps/{msp_id}/orgs\n\ncreateMspOrg\n\nCreate an organization under this MSP, optionally assigning it to organization groups and setting organization-level defaults.",
    capability=Capability.WRITE,
)
async def mist_create_msp_org(
    ctx: Context,
    msp_id: Annotated[str, Field(description="path parameter 'msp_id'")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request Body")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/msps/{msp_id}/orgs",
        path_params={"msp_id": msp_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_delete_msp_org",
    description="DELETE /api/v1/msps/{msp_id}/orgs/{org_id}\n\ndeleteMspOrg\n\nDelete an organization managed by this MSP. Use the MSP organization assignment endpoint when only assigning or unassigning organizations from the MSP account.",
    capability=Capability.WRITE_DELETE,
)
async def mist_delete_msp_org(
    ctx: Context,
    msp_id: Annotated[str, Field(description="path parameter 'msp_id'")],
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "DELETE",
        "/api/v1/msps/{msp_id}/orgs/{org_id}",
        path_params={"msp_id": msp_id, "org_id": org_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_get_msp_org",
    description="GET /api/v1/msps/{msp_id}/orgs/{org_id}\n\ngetMspOrg\n\nReturn details for one organization managed by this MSP, including MSP ownership, organization groups, support access, and session settings.",
    capability=Capability.READ,
)
async def mist_get_msp_org(
    ctx: Context,
    msp_id: Annotated[str, Field(description="path parameter 'msp_id'")],
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/msps/{msp_id}/orgs/{org_id}",
        path_params={"msp_id": msp_id, "org_id": org_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_list_msp_org_stats",
    description="GET /api/v1/msps/{msp_id}/stats/orgs\n\nlistMspOrgStats\n\nList organization statistics for organizations managed by this MSP, including device, inventory, site, and SLE summary fields.",
    capability=Capability.READ,
)
async def mist_list_msp_org_stats(
    ctx: Context,
    msp_id: Annotated[str, Field(description="path parameter 'msp_id'")],
    limit: Annotated[int, Field(description="Maximum number of results to return per page")] = 100,
    page: Annotated[
        int, Field(description="Select the page number to return when using page-based pagination; starts at `1`")
    ] = 1,
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/msps/{msp_id}/stats/orgs",
        path_params={"msp_id": msp_id},
        query_params={"limit": limit, "page": page},
        body=None,
    )


@_mcp_tool(
    name="mist_list_msp_orgs",
    description="GET /api/v1/msps/{msp_id}/orgs\n\nlistMspOrgs\n\nList organizations managed by this MSP account, including MSP ownership and organization-group membership metadata.",
    capability=Capability.READ,
)
async def mist_list_msp_orgs(
    ctx: Context,
    msp_id: Annotated[str, Field(description="path parameter 'msp_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/msps/{msp_id}/orgs",
        path_params={"msp_id": msp_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_manage_msp_orgs",
    description="PUT /api/v1/msps/{msp_id}/orgs\n\nmanageMspOrgs\n\nAssign existing organizations to this MSP account or unassign organizations from it by providing the desired operation and org IDs.",
    capability=Capability.WRITE,
)
async def mist_manage_msp_orgs(
    ctx: Context,
    msp_id: Annotated[str, Field(description="path parameter 'msp_id'")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request Body")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "PUT",
        "/api/v1/msps/{msp_id}/orgs",
        path_params={"msp_id": msp_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_search_msp_orgs",
    description="GET /api/v1/msps/{msp_id}/orgs/search\n\nsearchMspOrgs\n\nSearch organizations under this MSP using organization identifiers, names, subscription state, trial state, usage types, and time-based filters.",
    capability=Capability.READ,
)
async def mist_search_msp_orgs(
    ctx: Context,
    msp_id: Annotated[str, Field(description="path parameter 'msp_id'")],
    name: Annotated[str | None, Field(description="Filter results by name")] = None,
    org_id: Annotated[str | None, Field(description="Filter results by organization identifier")] = None,
    sub_insufficient: Annotated[bool | None, Field(description="If this org has sufficient subscription")] = None,
    trial_enabled: Annotated[bool | None, Field(description="If this org is under trial period")] = None,
    usage_types: Annotated[Any | None, Field(description="List of types that enabled by usage")] = None,
    limit: Annotated[int, Field(description="Maximum number of results to return per page")] = 100,
    sort: Annotated[
        str, Field(description="On which field the list should be sorted, -prefix represents DESC order")
    ] = "timestamp",
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
        "/api/v1/msps/{msp_id}/orgs/search",
        path_params={"msp_id": msp_id},
        query_params={
            "name": name,
            "org_id": org_id,
            "sub_insufficient": sub_insufficient,
            "trial_enabled": trial_enabled,
            "usage_types": usage_types,
            "limit": limit,
            "sort": sort,
            "start": start,
            "end": end,
            "search_after": search_after,
        },
        body=None,
    )


@_mcp_tool(
    name="mist_update_msp_org",
    description="PUT /api/v1/msps/{msp_id}/orgs/{org_id}\n\nupdateMspOrg\n\nUpdate organization settings for an organization managed by this MSP.",
    capability=Capability.WRITE,
)
async def mist_update_msp_org(
    ctx: Context,
    msp_id: Annotated[str, Field(description="path parameter 'msp_id'")],
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    body: Annotated[
        dict[str, Any] | None,
        Field(default=None, description="Request body for PUT /api/v1/msps/{msp_id}/orgs/{org_id}"),
    ] = None,
) -> Any:
    return await mist_request(
        ctx,
        "PUT",
        "/api/v1/msps/{msp_id}/orgs/{org_id}",
        path_params={"msp_id": msp_id, "org_id": org_id},
        query_params=None,
        body=body,
    )
