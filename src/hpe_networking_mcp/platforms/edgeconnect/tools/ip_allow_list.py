"""Generated EdgeConnect tools — DO NOT EDIT BY HAND.

Generated from ``vendor/edgeconnect/EdgeConnect-9-7-REST-API.json`` by the
maintainer-local EdgeConnect generator. These generated modules are committed
and are the runtime source of truth; regeneration is a release-time maintainer
workflow (the generator is intentionally not committed — see ``.gitignore``).

Tag: ``ipAllowList``
Operations in this file: 5
"""

# ruff: noqa: E501
from __future__ import annotations

from typing import Annotated, Any

from fastmcp import Context
from pydantic import Field

from hpe_networking_mcp.platforms._common.annotations import Capability
from hpe_networking_mcp.platforms.edgeconnect._registry import tool
from hpe_networking_mcp.platforms.edgeconnect.client import edgeconnect_request


@tool(
    name="edgeconnect_get_gms_ip_allow_list_drops",
    description="GET /gms/ipAllowList/drops\n\ngetIPAllowListDrops292\n\nGet blocked request history from IP allow list",
    capability=Capability.READ,
)
async def edgeconnect_get_gms_ip_allow_list_drops(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/gms/ipAllowList/drops",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_gms_ip_allow_list_external",
    description="GET /gms/ipAllowList/external\n\ngetExternalIPAllowList293\n\nGet the external IP/mask allow list",
    capability=Capability.READ,
)
async def edgeconnect_get_gms_ip_allow_list_external(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/gms/ipAllowList/external",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_gms_ip_allow_list_use_socket_ip",
    description="GET /gms/ipAllowList/useSocketIP\n\ngetUseSocketIP295\n\nGet the Use Socket IP setting for IP allow list validation",
    capability=Capability.READ,
)
async def edgeconnect_get_gms_ip_allow_list_use_socket_ip(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/gms/ipAllowList/useSocketIP",
        query_params=None,
    )


@tool(
    name="edgeconnect_post_gms_ip_allow_list_external",
    description="POST /gms/ipAllowList/external\n\nsetExternalIPAllowList294\n\nSet the external IP/mask allow list",
    capability=Capability.WRITE,
)
async def edgeconnect_post_gms_ip_allow_list_external(
    ctx: Context,
    body: Annotated[list[Any], Field(description="Request body (required)")],
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/gms/ipAllowList/external",
        query_params=None,
        body=body,
    )


@tool(
    name="edgeconnect_post_gms_ip_allow_list_use_socket_ip",
    description="POST /gms/ipAllowList/useSocketIP\n\nsetUseSocketIP296\n\nConfigure socket IP usage for IP allow list validation",
    capability=Capability.WRITE,
)
async def edgeconnect_post_gms_ip_allow_list_use_socket_ip(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/gms/ipAllowList/useSocketIP",
        query_params=None,
        body=body,
    )
