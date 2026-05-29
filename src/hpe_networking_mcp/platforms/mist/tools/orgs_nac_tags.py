"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``scripts/_mist_generator.py`` from
``vendor/mist_openapi.json``. Regenerate via:

    uv run python scripts/regenerate_mist_tools.py

Tag: ``Orgs NAC Tags``
Operations in this file: 5
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
    name="mist_create_org_nac_tag",
    description="POST /api/v1/orgs/{org_id}/nactags\n\ncreateOrgNacTag\n\nCreate Org NAC Tag",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_create_org_nac_tag(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    body: Annotated[
        dict[str, Any] | None, Field(default=None, description="Request body for POST /api/v1/orgs/{org_id}/nactags")
    ] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/orgs/{org_id}/nactags",
        path_params={"org_id": org_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_delete_org_nac_tag",
    description="DELETE /api/v1/orgs/{org_id}/nactags/{nactag_id}\n\ndeleteOrgNacTag\n\nDelete Org NAC Tag",
    tags={"mist", "mist_write", "mist_write_delete"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=True),
)
async def mist_delete_org_nac_tag(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    nactag_id: Annotated[str, Field(description="path parameter 'nactag_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "DELETE",
        "/api/v1/orgs/{org_id}/nactags/{nactag_id}",
        path_params={"org_id": org_id, "nactag_id": nactag_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_get_org_nac_tag",
    description="GET /api/v1/orgs/{org_id}/nactags/{nactag_id}\n\ngetOrgNacTag\n\nGet Org NAC Tag",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_get_org_nac_tag(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    nactag_id: Annotated[str, Field(description="path parameter 'nactag_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/orgs/{org_id}/nactags/{nactag_id}",
        path_params={"org_id": org_id, "nactag_id": nactag_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_list_org_nac_tags",
    description="GET /api/v1/orgs/{org_id}/nactags\n\nlistOrgNacTags\n\nGet List of Org NAC Tags",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_list_org_nac_tags(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    type: Annotated[
        Any | None,
        Field(
            description="Type of NAC Tag. enum: `egress_vlan_names`, `gbp_tag`, `match`, `radius_attrs`, `radius_group`, `radius_vendor_attrs`, `session_timeout`, `username_attr`, `vlan`"
        ),
    ] = None,
    name: Annotated[str | None, Field(description="Name of NAC Tag")] = None,
    match: Annotated[
        Any | None,
        Field(
            description="if `type`==`match`, Type of NAC Tag. enum: `cert_cn`, `cert_eku`, `cert_issuer`, `cert_san`, `cert_serial`, `cert_sub`, `cert_template`, `client_mac`, `edr_status`, `gbp_tag`, `hostname`, `idp_role`, `ingress_vlan`, `mdm_status`, `nas_ip..."
        ),
    ] = None,
    limit: Annotated[int, Field(description="query parameter 'limit'")] = 100,
    page: Annotated[int, Field(description="query parameter 'page'")] = 1,
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/orgs/{org_id}/nactags",
        path_params={"org_id": org_id},
        query_params={"type": type, "name": name, "match": match, "limit": limit, "page": page},
        body=None,
    )


@_mcp_tool(
    name="mist_update_org_nac_tag",
    description="PUT /api/v1/orgs/{org_id}/nactags/{nactag_id}\n\nupdateOrgNacTag\n\nUpdate Org NAC Tag",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_update_org_nac_tag(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    nactag_id: Annotated[str, Field(description="path parameter 'nactag_id'")],
    body: Annotated[
        dict[str, Any] | None,
        Field(default=None, description="Request body for PUT /api/v1/orgs/{org_id}/nactags/{nactag_id}"),
    ] = None,
) -> Any:
    return await mist_request(
        ctx,
        "PUT",
        "/api/v1/orgs/{org_id}/nactags/{nactag_id}",
        path_params={"org_id": org_id, "nactag_id": nactag_id},
        query_params=None,
        body=body,
    )
