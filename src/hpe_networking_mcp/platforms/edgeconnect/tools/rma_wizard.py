"""Generated EdgeConnect tools — DO NOT EDIT BY HAND.

Generated from ``vendor/edgeconnect/EdgeConnect-9-7-REST-API.json`` by the
maintainer-local EdgeConnect generator. These generated modules are committed
and are the runtime source of truth; regeneration is a release-time maintainer
workflow (the generator is intentionally not committed — see ``.gitignore``).

Tag: ``rmaWizard``
Operations in this file: 2
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
    name="edgeconnect_post_rma_wizard",
    description="POST /rmaWizard\n\napplyRmaWizard547\n\nApply RMA wizard to replace an existing appliance",
    capability=Capability.WRITE,
)
async def edgeconnect_post_rma_wizard(
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
        "/rmaWizard",
        query_params=query_params or None,
        body=body,
    )


@tool(
    name="edgeconnect_post_rma_wizard_check_interface_mapping",
    description="POST /rmaWizard/checkInterfaceMapping\n\ncheckInterfaceMapping\n\nValidate interface mapping for RMA replacement",
    capability=Capability.WRITE,
)
async def edgeconnect_post_rma_wizard_check_interface_mapping(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/rmaWizard/checkInterfaceMapping",
        query_params=None,
        body=body,
    )
