"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``scripts/_mist_generator.py`` from
``vendor/mist/mist_openapi.json``. Regenerate via:

    uv run python scripts/regenerate_mist_tools.py

Tag: ``Orgs NAC Tags``
Operations in this file: 5
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
    name="mist_create_org_nac_tag",
    description="POST /api/v1/orgs/{org_id}/nactags\n\ncreateOrgNacTag\n\nCreate a NAC tag used either as rule-matching criteria or as a result attribute returned when NAC allows access.",
    capability=Capability.WRITE,
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
    description="DELETE /api/v1/orgs/{org_id}/nactags/{nactag_id}\n\ndeleteOrgNacTag\n\nDelete an organization NAC tag by tag ID so it can no longer be used by NAC rules.",
    capability=Capability.WRITE_DELETE,
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
    description="GET /api/v1/orgs/{org_id}/nactags/{nactag_id}\n\ngetOrgNacTag\n\nRetrieve configuration details for a specific NAC tag, including type, match values, RADIUS attributes, VLAN or session results, and portal redirection settings.",
    capability=Capability.READ,
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
    description="GET /api/v1/orgs/{org_id}/nactags\n\nlistOrgNacTags\n\nList organization NAC tags, optionally filtering by tag type, name, or match attribute.",
    capability=Capability.READ,
)
async def mist_list_org_nac_tags(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    type: Annotated[
        str | None,
        Field(
            description="Filter results by type. enum: `egress_vlan_names`, `gbp_tag`, `match`, `radius_attrs`, `radius_group`, `radius_vendor_attrs`, `redirect_nacportal_id`, `session_timeout`, `username_attr`, `vlan`. Accepts multiple comma-separated values."
        ),
    ] = None,
    name: Annotated[
        str | None, Field(description="Filter results by name. Accepts multiple comma-separated values.")
    ] = None,
    match: Annotated[
        str | None,
        Field(
            description="if `type`==`match`, Type of NAC Tag. enum: `cert_cn`, `cert_eku`, `cert_issuer`, `cert_san`, `cert_serial`, `cert_sub`, `cert_template`, `client_mac`, `edr_status`, `gbp_tag`, `hostname`, `idp_role`, `ingress_vlan`, `mdm_status`, `nas_ip..."
        ),
    ] = None,
    limit: Annotated[int, Field(description="Maximum number of results to return per page")] = 100,
    page: Annotated[
        int, Field(description="Select the page number to return when using page-based pagination; starts at `1`")
    ] = 1,
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
    description="PUT /api/v1/orgs/{org_id}/nactags/{nactag_id}\n\nupdateOrgNacTag\n\nUpdate a NAC tag, including matcher values or result attributes such as RADIUS attributes, VLAN, session timeout, username attribute, or portal redirection.",
    capability=Capability.WRITE,
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
