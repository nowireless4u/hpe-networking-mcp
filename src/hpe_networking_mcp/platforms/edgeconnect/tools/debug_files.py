"""Generated EdgeConnect tools — DO NOT EDIT BY HAND.

Generated from ``vendor/edgeconnect/EdgeConnect-9-7-REST-API.json`` by the
maintainer-local EdgeConnect generator. These generated modules are committed
and are the runtime source of truth; regeneration is a release-time maintainer
workflow (the generator is intentionally not committed — see ``.gitignore``).

Tag: ``debugFiles``
Operations in this file: 5
"""

# ruff: noqa: E501, N803
from __future__ import annotations

from typing import Annotated, Any

from fastmcp import Context
from pydantic import Field

from hpe_networking_mcp.platforms._common.annotations import Capability
from hpe_networking_mcp.platforms.edgeconnect._registry import tool
from hpe_networking_mcp.platforms.edgeconnect.client import edgeconnect_request


@tool(
    name="edgeconnect_get_debug_files",
    description="GET /debugFiles\n\ndebugFiles215\n\nRetrieve debug files from an appliance",
    capability=Capability.READ,
)
async def edgeconnect_get_debug_files(
    ctx: Context,
    nePk: Annotated[
        str,
        Field(
            description="Network Element Primary Key - unique appliance identifier assigned by Orchestrator. Format: '<id>.NE' (e.g., '0.NE', '10.NE')."
        ),
    ],
) -> Any:
    query_params: dict[str, Any] = {}
    if nePk is not None:
        query_params["nePk"] = nePk
    return await edgeconnect_request(
        ctx,
        "GET",
        "/debugFiles",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_debug_files_proxy_config",
    description="GET /debugFiles/proxyConfig \n\ngetProxyConfig213\n\nRetrieve Orchestrator HTTP proxy configuration",
    capability=Capability.READ,
)
async def edgeconnect_get_debug_files_proxy_config(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/debugFiles/proxyConfig ",
        query_params=None,
    )


@tool(
    name="edgeconnect_post_debug_files_cancel",
    description="POST /debugFiles/cancel\n\ncancel210\n\nCancel Orchestrator system dump generation",
    capability=Capability.WRITE,
)
async def edgeconnect_post_debug_files_cancel(
    ctx: Context,
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request body")] = None,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/debugFiles/cancel",
        query_params=None,
        body=body,
    )


@tool(
    name="edgeconnect_post_debug_files_delete",
    description="POST /debugFiles/delete\n\ndeleteGMSNeFile212\n\nDelete debug file from Orchestrator or appliance",
    capability=Capability.WRITE,
)
async def edgeconnect_post_debug_files_delete(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
    nePk: Annotated[
        str | None,
        Field(
            default=None,
            description="Network Element Primary Key - unique appliance identifier assigned by Orchestrator. Format: '<id>.NE' (e.g., '0.NE', '10.NE'). When omitted, results are returned for all appliances.",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if nePk is not None:
        query_params["nePk"] = nePk
    return await edgeconnect_request(
        ctx,
        "POST",
        "/debugFiles/delete",
        query_params=query_params or None,
        body=body,
    )


@tool(
    name="edgeconnect_post_debug_files_proxy_config",
    description="POST /debugFiles/proxyConfig \n\nsetProxyConfig214\n\nConfigure HTTP proxy settings for Orchestrator",
    capability=Capability.WRITE,
)
async def edgeconnect_post_debug_files_proxy_config(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/debugFiles/proxyConfig ",
        query_params=None,
        body=body,
    )
