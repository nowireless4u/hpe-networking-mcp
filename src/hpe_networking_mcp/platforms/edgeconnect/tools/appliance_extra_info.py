"""Generated EdgeConnect tools — DO NOT EDIT BY HAND.

Generated from ``vendor/edgeconnect/EdgeConnect-9-7-REST-API.json`` by the
maintainer-local EdgeConnect generator. These generated modules are committed
and are the runtime source of truth; regeneration is a release-time maintainer
workflow (the generator is intentionally not committed — see ``.gitignore``).

Tag: ``applianceExtraInfo``
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
    name="edgeconnect_delete_appliance_extra_info",
    description="DELETE /appliance/extraInfo\n\ndeleteApplianceExtraInfo58\n\nDelete appliance extra information",
    capability=Capability.WRITE_DELETE,
)
async def edgeconnect_delete_appliance_extra_info(
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
        "DELETE",
        "/appliance/extraInfo",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_appliance_extra_info",
    description="GET /appliance/extraInfo\n\ngetApplianceExtraInfo59\n\nGet appliance extra information",
    capability=Capability.READ,
)
async def edgeconnect_get_appliance_extra_info(
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
        "/appliance/extraInfo",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_post_appliance_extra_info",
    description="POST /appliance/extraInfo\n\nsaveApplianceExtraInfo60\n\nSave appliance extra information",
    capability=Capability.WRITE,
)
async def edgeconnect_post_appliance_extra_info(
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
        "/appliance/extraInfo",
        query_params=query_params or None,
        body=body,
    )
