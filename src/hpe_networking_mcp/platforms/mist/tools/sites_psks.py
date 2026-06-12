"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``scripts/_mist_generator.py`` from
``vendor/mist/mist_openapi.json``. Regenerate via:

    uv run python scripts/regenerate_mist_tools.py

Tag: ``Sites Psks``
Operations in this file: 7
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
    name="mist_create_site_psk",
    description='POST /api/v1/sites/{site_id}/psks\n\ncreateSitePsk\n\nCreate Site PSK\n\n\nWhen `usage`==`macs`, corresponding "macs" field will hold a list consisting of client MAC addresses (["xx:xx:xx:xx:xx",...]) or mac patterns(["xx:xx:*","xx*",...]) or both (["xx:xx:xx:xx:xx:xx", "xx:*", ...]). This list is capped at 5000',
    capability=Capability.WRITE,
)
async def mist_create_site_psk(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request Body")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/sites/{site_id}/psks",
        path_params={"site_id": site_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_delete_site_psk",
    description="DELETE /api/v1/sites/{site_id}/psks/{psk_id}\n\ndeleteSitePsk\n\nDelete Site PSK",
    capability=Capability.WRITE_DELETE,
)
async def mist_delete_site_psk(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    psk_id: Annotated[str, Field(description="PSK ID")],
) -> Any:
    return await mist_request(
        ctx,
        "DELETE",
        "/api/v1/sites/{site_id}/psks/{psk_id}",
        path_params={"site_id": site_id, "psk_id": psk_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_get_site_psk",
    description="GET /api/v1/sites/{site_id}/psks/{psk_id}\n\ngetSitePsk\n\nGet Site PSK Details",
    capability=Capability.READ,
)
async def mist_get_site_psk(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    psk_id: Annotated[str, Field(description="PSK ID")],
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/sites/{site_id}/psks/{psk_id}",
        path_params={"site_id": site_id, "psk_id": psk_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_import_site_psks",
    description="POST /api/v1/sites/{site_id}/psks/import\n\nimportSitePsks\n\nImport PSK from CSV file or JSON\n\n## CSV File Format\n```csv\nPSK Import CSV File Format:\nname,ssid,passphrase,usage,vlan_id,mac\nCommon,warehouse,foryoureyesonly,single,35,a31425f31278\nJustin,reception,visible,multi,1002\n```",
    capability=Capability.WRITE,
)
async def mist_import_site_psks(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    body: Annotated[
        dict[str, Any] | None,
        Field(default=None, description="Request body for POST /api/v1/sites/{site_id}/psks/import"),
    ] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/sites/{site_id}/psks/import",
        path_params={"site_id": site_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_list_site_psks",
    description="GET /api/v1/sites/{site_id}/psks\n\nlistSitePsks\n\nGet List of Site PSKs",
    capability=Capability.READ,
)
async def mist_list_site_psks(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    ssid: Annotated[str | None, Field(description="Filter results by SSID")] = None,
    role: Annotated[str | None, Field(description="Filter PSK results by role")] = None,
    name: Annotated[str | None, Field(description="Filter results by name")] = None,
    limit: Annotated[int, Field(description="Maximum number of results to return per page")] = 100,
    page: Annotated[
        int, Field(description="Select the page number to return when using page-based pagination; starts at `1`")
    ] = 1,
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/sites/{site_id}/psks",
        path_params={"site_id": site_id},
        query_params={"ssid": ssid, "role": role, "name": name, "limit": limit, "page": page},
        body=None,
    )


@_mcp_tool(
    name="mist_update_site_multiple_psks",
    description="PUT /api/v1/sites/{site_id}/psks\n\nupdateSiteMultiplePsks\n\nUpdate multiple PSKs",
    capability=Capability.WRITE,
)
async def mist_update_site_multiple_psks(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    body: Annotated[
        dict[str, Any] | None, Field(default=None, description="Request body for PUT /api/v1/sites/{site_id}/psks")
    ] = None,
) -> Any:
    return await mist_request(
        ctx,
        "PUT",
        "/api/v1/sites/{site_id}/psks",
        path_params={"site_id": site_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_update_site_psk",
    description="PUT /api/v1/sites/{site_id}/psks/{psk_id}\n\nupdateSitePsk\n\nUpdate Site PSK",
    capability=Capability.WRITE,
)
async def mist_update_site_psk(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    psk_id: Annotated[str, Field(description="PSK ID")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request Body")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "PUT",
        "/api/v1/sites/{site_id}/psks/{psk_id}",
        path_params={"site_id": site_id, "psk_id": psk_id},
        query_params=None,
        body=body,
    )
