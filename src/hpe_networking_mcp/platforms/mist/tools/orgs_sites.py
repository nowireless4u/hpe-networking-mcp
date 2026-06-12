"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``scripts/_mist_generator.py`` from
``vendor/mist/mist_openapi.json``. Regenerate via:

    uv run python scripts/regenerate_mist_tools.py

Tag: ``Orgs Sites``
Operations in this file: 4
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
    name="mist_count_org_sites",
    description="GET /api/v1/orgs/{org_id}/sites/count\n\ncountOrgSites\n\nCount organization sites grouped by a distinct site attribute, such as country code, site name, feature flags, or enabled services.",
    capability=Capability.READ,
)
async def mist_count_org_sites(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    distinct: Annotated[
        Any | None,
        Field(
            description="Field used to group this count response. enum: `analytic_enabled`, `app_waking`, `asset_enabled`, `auto_upgrade_enabled`, `auto_upgrade_version`, `country_code`, `honeypot_enabled`, `id`, `locate_unconnected`, `mesh_enabled`, `name`, `re..."
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
        "/api/v1/orgs/{org_id}/sites/count",
        path_params={"org_id": org_id},
        query_params={"distinct": distinct, "start": start, "end": end, "duration": duration, "limit": limit},
        body=None,
    )


@_mcp_tool(
    name="mist_create_org_site",
    description="POST /api/v1/orgs/{org_id}/sites\n\ncreateOrgSite\n\nCreate a site in the organization with location metadata, timezone, site group membership, and optional template or policy associations.",
    capability=Capability.WRITE,
)
async def mist_create_org_site(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request Body")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/orgs/{org_id}/sites",
        path_params={"org_id": org_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_list_org_sites",
    description="GET /api/v1/orgs/{org_id}/sites\n\nlistOrgSites\n\nList sites in the organization. Site records include location metadata, timezone, site group membership, and template or policy associations.",
    capability=Capability.READ,
)
async def mist_list_org_sites(
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
        "/api/v1/orgs/{org_id}/sites",
        path_params={"org_id": org_id},
        query_params={"limit": limit, "page": page},
        body=None,
    )


@_mcp_tool(
    name="mist_search_org_sites",
    description="GET /api/v1/orgs/{org_id}/sites/search\n\nsearchOrgSites\n\nSearch organization sites with filters for feature flags, country code, identifiers, names, upgrade settings, and other site attributes. Supports pagination and sorting.",
    capability=Capability.READ,
)
async def mist_search_org_sites(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    analytic_enabled: Annotated[
        bool | None,
        Field(description="If Advanced Analytic feature is enabled. Accepts multiple comma-separated boolean values."),
    ] = None,
    app_waking: Annotated[bool | None, Field(description="If App Waking feature is enabled")] = None,
    asset_enabled: Annotated[
        bool | None, Field(description="If Asset Tracking is enabled. Accepts multiple comma-separated boolean values.")
    ] = None,
    auto_upgrade_enabled: Annotated[
        bool | None, Field(description="Filter results by whether automatic upgrades are enabled")
    ] = None,
    auto_upgrade_version: Annotated[
        str | None,
        Field(description="Filter results by automatic upgrade version. Accepts multiple comma-separated values."),
    ] = None,
    country_code: Annotated[
        str | None, Field(description="Filter results by country code. Accepts multiple comma-separated values.")
    ] = None,
    honeypot_enabled: Annotated[
        bool | None,
        Field(description="If Honeypot detection is enabled. Accepts multiple comma-separated boolean values."),
    ] = None,
    id: Annotated[
        str | None, Field(description="Filter results by identifier. Accepts multiple comma-separated values.")
    ] = None,
    locate_unconnected: Annotated[
        bool | None,
        Field(description="If unconnected client are located. Accepts multiple comma-separated boolean values."),
    ] = None,
    mesh_enabled: Annotated[
        bool | None, Field(description="If Mesh feature is enabled. Accepts multiple comma-separated boolean values.")
    ] = None,
    name: Annotated[
        str | None,
        Field(
            description="Partial / full Site name. Case insensitive. Use `prefix*` for prefix search or `*substring*` for contains search (e.g. `my-site*` and `*site*` match `my-site-01`). Suffix-only wildcards (e.g. `*site-01`) are not supported. Accepts multip..."
        ),
    ] = None,
    rogue_enabled: Annotated[
        bool | None,
        Field(description="If Rogue detection is enabled. Accepts multiple comma-separated boolean values."),
    ] = None,
    remote_syslog_enabled: Annotated[bool | None, Field(description="If Remote Syslog is enabled")] = None,
    rtsa_enabled: Annotated[
        bool | None,
        Field(description="If managed mobility feature is enabled. Accepts multiple comma-separated boolean values."),
    ] = None,
    vna_enabled: Annotated[
        bool | None,
        Field(description="If Virtual Network Assistant is enabled. Accepts multiple comma-separated boolean values."),
    ] = None,
    wifi_enabled: Annotated[bool | None, Field(description="If Wi-Fi feature is enabled")] = None,
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
        "/api/v1/orgs/{org_id}/sites/search",
        path_params={"org_id": org_id},
        query_params={
            "analytic_enabled": analytic_enabled,
            "app_waking": app_waking,
            "asset_enabled": asset_enabled,
            "auto_upgrade_enabled": auto_upgrade_enabled,
            "auto_upgrade_version": auto_upgrade_version,
            "country_code": country_code,
            "honeypot_enabled": honeypot_enabled,
            "id": id,
            "locate_unconnected": locate_unconnected,
            "mesh_enabled": mesh_enabled,
            "name": name,
            "rogue_enabled": rogue_enabled,
            "remote_syslog_enabled": remote_syslog_enabled,
            "rtsa_enabled": rtsa_enabled,
            "vna_enabled": vna_enabled,
            "wifi_enabled": wifi_enabled,
            "limit": limit,
            "start": start,
            "end": end,
            "duration": duration,
            "sort": sort,
            "search_after": search_after,
        },
        body=None,
    )
