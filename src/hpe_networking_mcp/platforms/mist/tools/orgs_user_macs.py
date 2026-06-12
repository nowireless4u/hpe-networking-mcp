"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``scripts/_mist_generator.py`` from
``vendor/mist/mist_openapi.json``. Regenerate via:

    uv run python scripts/regenerate_mist_tools.py

Tag: ``Orgs User MACs``
Operations in this file: 9
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
    name="mist_count_org_user_macs",
    description="GET /api/v1/orgs/{org_id}/usermacs/count\n\ncountOrgUserMacs\n\nCount by Distinct Attributes of User MACs",
    capability=Capability.READ,
)
async def mist_count_org_user_macs(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    distinct: Annotated[Any, Field(description="Attribute to count by. enum: `mac`, `name`, `labels`, `org_id`")],
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
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/orgs/{org_id}/usermacs/count",
        path_params={"org_id": org_id},
        query_params={"distinct": distinct, "limit": limit, "start": start, "end": end},
        body=None,
    )


@_mcp_tool(
    name="mist_create_org_user_mac",
    description='POST /api/v1/orgs/{org_id}/usermacs\n\ncreateOrgUserMac\n\nCreate Org User MACs\n\n### Usermacs import CSV file format\nmac,labels,vlan,notes \n921b638445cd,"bldg1,flor1",vlan-100 \n721b638445ef,"bldg2,flor2",vlan-101,Canon Printers \n721b638445ee,"bldg3,flor3",vlan-102 \n921b638445ce,"bldg4,flor4",vlan-103 \n921b638445cf,"bldg5,flor5",vlan-104',
    capability=Capability.WRITE,
)
async def mist_create_org_user_mac(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    body: Annotated[
        dict[str, Any] | None, Field(default=None, description="Request body for POST /api/v1/orgs/{org_id}/usermacs")
    ] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/orgs/{org_id}/usermacs",
        path_params={"org_id": org_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_delete_org_multiple_user_macs",
    description="POST /api/v1/orgs/{org_id}/usermacs/delete\n\ndeleteOrgMultipleUserMacs\n\nDelete Multiple Org User MACs",
    capability=Capability.WRITE,
)
async def mist_delete_org_multiple_user_macs(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request Body")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/orgs/{org_id}/usermacs/delete",
        path_params={"org_id": org_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_delete_org_user_mac",
    description="DELETE /api/v1/orgs/{org_id}/usermacs/{usermac_id}\n\ndeleteOrgUserMac\n\nDelete Org User MAC",
    capability=Capability.WRITE_DELETE,
)
async def mist_delete_org_user_mac(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    usermac_id: Annotated[str, Field(description="path parameter 'usermac_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "DELETE",
        "/api/v1/orgs/{org_id}/usermacs/{usermac_id}",
        path_params={"org_id": org_id, "usermac_id": usermac_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_get_org_user_mac",
    description="GET /api/v1/orgs/{org_id}/usermacs/{usermac_id}\n\ngetOrgUserMac\n\nGet Org User MAC",
    capability=Capability.READ,
)
async def mist_get_org_user_mac(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    usermac_id: Annotated[str, Field(description="path parameter 'usermac_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/orgs/{org_id}/usermacs/{usermac_id}",
        path_params={"org_id": org_id, "usermac_id": usermac_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_import_org_user_macs",
    description='POST /api/v1/orgs/{org_id}/usermacs/import\n\nimportOrgUserMacs\n\nImport Org User MACs\n\n### CSV Import example\n```csv \nmac,labels,vlan,notes,name,radius_group\n921b638445cd,"bldg1,flor1",vlan-100\n721b638445ef,"bldg2,flor2",vlan-101,Canon Printers\n721b638445ee,"bldg3,flor3",vlan-102,Printer2,VIP\n921b638445ce,"bldg4,flor4",vlan-103\n921b638445cf,"bldg5,flor5",vlan-104\n````',
    capability=Capability.WRITE,
)
async def mist_import_org_user_macs(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    body: Annotated[
        dict[str, Any] | None,
        Field(default=None, description="Request body for POST /api/v1/orgs/{org_id}/usermacs/import"),
    ] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/orgs/{org_id}/usermacs/import",
        path_params={"org_id": org_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_search_org_user_macs",
    description="GET /api/v1/orgs/{org_id}/usermacs/search\n\nsearchOrgUserMacs\n\nSearch Org User MACs",
    capability=Capability.READ,
)
async def mist_search_org_user_macs(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    mac: Annotated[
        str | None,
        Field(
            description="Partial / full Client MAC address. Use `prefix*` for prefix search or `*substring*` for contains search (e.g. `aabbcc*` and `*bbcc*` match `aabbccddeeff`). Suffix-only wildcards (e.g. `*bccddeeff`) are not supported"
        ),
    ] = None,
    labels: Annotated[Any | None, Field(description="Optional, array of strings of labels")] = None,
    limit: Annotated[int, Field(description="Maximum number of results to return per page")] = 100,
    page: Annotated[
        int, Field(description="Select the page number to return when using page-based pagination; starts at `1`")
    ] = 1,
    sort: Annotated[
        str, Field(description="On which field the list should be sorted, -prefix represents DESC order")
    ] = "timestamp",
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/orgs/{org_id}/usermacs/search",
        path_params={"org_id": org_id},
        query_params={"mac": mac, "labels": labels, "limit": limit, "page": page, "sort": sort},
        body=None,
    )


@_mcp_tool(
    name="mist_update_org_multiple_user_macs",
    description="PUT /api/v1/orgs/{org_id}/usermacs\n\nupdateOrgMultipleUserMacs\n\nUpdate Multiple Org User MACs",
    capability=Capability.WRITE,
)
async def mist_update_org_multiple_user_macs(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    body: Annotated[
        dict[str, Any] | None, Field(default=None, description="Request body for PUT /api/v1/orgs/{org_id}/usermacs")
    ] = None,
) -> Any:
    return await mist_request(
        ctx,
        "PUT",
        "/api/v1/orgs/{org_id}/usermacs",
        path_params={"org_id": org_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_update_org_user_mac",
    description="PUT /api/v1/orgs/{org_id}/usermacs/{usermac_id}\n\nupdateOrgUserMac\n\nUpdate Org User MAC",
    capability=Capability.WRITE,
)
async def mist_update_org_user_mac(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    usermac_id: Annotated[str, Field(description="path parameter 'usermac_id'")],
    body: Annotated[
        dict[str, Any] | None,
        Field(default=None, description="Request body for PUT /api/v1/orgs/{org_id}/usermacs/{usermac_id}"),
    ] = None,
) -> Any:
    return await mist_request(
        ctx,
        "PUT",
        "/api/v1/orgs/{org_id}/usermacs/{usermac_id}",
        path_params={"org_id": org_id, "usermac_id": usermac_id},
        query_params=None,
        body=body,
    )
