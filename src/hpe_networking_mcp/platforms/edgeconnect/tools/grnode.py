"""Generated EdgeConnect tools — DO NOT EDIT BY HAND.

Generated from ``vendor/edgeconnect/EdgeConnect-9-7-REST-API.json`` by the
maintainer-local EdgeConnect generator. These generated modules are committed
and are the runtime source of truth; regeneration is a release-time maintainer
workflow (the generator is intentionally not committed — see ``.gitignore``).

Tag: ``grnode``
Operations in this file: 3
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
    name="edgeconnect_get_gms_gr_node",
    description="GET /gms/grNode\n\nallGRNodeGet275\n\nGet graphical node positions for topology map",
    capability=Capability.READ,
)
async def edgeconnect_get_gms_gr_node(
    ctx: Context,
    grNodePk: Annotated[
        str | None,
        Field(
            default=None,
            description="Unique identifier for a specific GRNode (e.g., '1.GrNode'). When omitted, returns all GRNodes visible to the user based on RBAC settings.",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if grNodePk is not None:
        query_params["grNodePk"] = grNodePk
    return await edgeconnect_request(
        ctx,
        "GET",
        "/gms/grNode",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_post_gms_gr_node",
    description="POST /gms/grNode\n\ngrNodeUpdate278\n\nUpdate GRNode position coordinates",
    capability=Capability.WRITE,
)
async def edgeconnect_post_gms_gr_node(
    ctx: Context,
    grNodePk: Annotated[
        str,
        Field(
            description="Unique identifier for the GRNode to update (format: '<index>.GrNode', e.g., '1.GrNode'). This parameter is required."
        ),
    ],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    query_params: dict[str, Any] = {}
    if grNodePk is not None:
        query_params["grNodePk"] = grNodePk
    return await edgeconnect_request(
        ctx,
        "POST",
        "/gms/grNode",
        query_params=query_params or None,
        body=body,
    )


@tool(
    name="edgeconnect_post_gms_gr_node_for_ne_pk",
    description="POST /gms/grNode/forNePk\n\ngrNodeUpdateByNePk276\n\nUpdate appliance GRNode position by nePk",
    capability=Capability.WRITE,
)
async def edgeconnect_post_gms_gr_node_for_ne_pk(
    ctx: Context,
    nePk: Annotated[
        str,
        Field(
            description="Network Element Primary Key - unique appliance identifier assigned by Orchestrator. Format: '<id>.NE' (e.g., '0.NE', '10.NE')."
        ),
    ],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    query_params: dict[str, Any] = {}
    if nePk is not None:
        query_params["nePk"] = nePk
    return await edgeconnect_request(
        ctx,
        "POST",
        "/gms/grNode/forNePk",
        query_params=query_params or None,
        body=body,
    )
