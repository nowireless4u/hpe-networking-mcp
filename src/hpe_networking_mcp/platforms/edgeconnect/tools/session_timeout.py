"""Generated EdgeConnect tools — DO NOT EDIT BY HAND.

Generated from ``vendor/edgeconnect/EdgeConnect-9-7-REST-API.json`` by the
maintainer-local EdgeConnect generator. These generated modules are committed
and are the runtime source of truth; regeneration is a release-time maintainer
workflow (the generator is intentionally not committed — see ``.gitignore``).

Tag: ``sessionTimeout``
Operations in this file: 2
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
    name="edgeconnect_get_gms_session_timeout",
    description="GET /gms/sessionTimeout\n\ngetSessionTimeout\n\nGet session timeout settings",
    capability=Capability.READ,
)
async def edgeconnect_get_gms_session_timeout(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/gms/sessionTimeout",
        query_params=None,
    )


@tool(
    name="edgeconnect_put_gms_session_timeout",
    description="PUT /gms/sessionTimeout\n\nupdateSessionTimeout\n\nUpdate session timeout and concurrent session settings",
    capability=Capability.WRITE,
)
async def edgeconnect_put_gms_session_timeout(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await edgeconnect_request(
        ctx,
        "PUT",
        "/gms/sessionTimeout",
        query_params=None,
        body=body,
    )
