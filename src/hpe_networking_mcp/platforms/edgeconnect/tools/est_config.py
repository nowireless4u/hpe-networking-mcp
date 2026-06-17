"""Generated EdgeConnect tools — DO NOT EDIT BY HAND.

Generated from ``vendor/edgeconnect/EdgeConnect-9-7-REST-API.json`` by the
maintainer-local EdgeConnect generator. These generated modules are committed
and are the runtime source of truth; regeneration is a release-time maintainer
workflow (the generator is intentionally not committed — see ``.gitignore``).

Tag: ``EST Config``
Operations in this file: 4
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
    name="edgeconnect_delete_security_est_server",
    description="DELETE /security/estServer\n\ndeleteEstConfig\n\nDelete an existing EST server configuration",
    capability=Capability.WRITE_DELETE,
)
async def edgeconnect_delete_security_est_server(
    ctx: Context,
    name: Annotated[
        str,
        Field(
            description="Unique profile name of the EST configuration to delete. Must contain only alphanumeric characters, hyphens (-), and underscores (_)."
        ),
    ],
) -> Any:
    query_params: dict[str, Any] = {}
    if name is not None:
        query_params["name"] = name
    return await edgeconnect_request(
        ctx,
        "DELETE",
        "/security/estServer",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_security_est_server",
    description="GET /security/estServer\n\ngetAllEstConfig\n\nRetrieve all EST server configurations",
    capability=Capability.READ,
)
async def edgeconnect_get_security_est_server(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/security/estServer",
        query_params=None,
    )


@tool(
    name="edgeconnect_post_security_est_server",
    description="POST /security/estServer\n\ninsertEstConfig\n\nCreate a new EST server configuration",
    capability=Capability.WRITE,
)
async def edgeconnect_post_security_est_server(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/security/estServer",
        query_params=None,
        body=body,
    )


@tool(
    name="edgeconnect_put_security_est_server",
    description="PUT /security/estServer\n\nupdateEstConfig\n\nUpdate an existing EST server configuration",
    capability=Capability.WRITE,
)
async def edgeconnect_put_security_est_server(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await edgeconnect_request(
        ctx,
        "PUT",
        "/security/estServer",
        query_params=None,
        body=body,
    )
