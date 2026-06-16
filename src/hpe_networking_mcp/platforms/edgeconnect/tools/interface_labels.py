"""Generated EdgeConnect tools — DO NOT EDIT BY HAND.

Emitted by ``scripts/generate_edgeconnect_tools.py`` from
``vendor/edgeconnect/EdgeConnect-9-7-REST-API.json``. Regenerate via:

    uv run python scripts/generate_edgeconnect_tools.py

Tag: ``interfaceLabels``
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
    name="edgeconnect_get_gms_interface_labels",
    description="GET /gms/interfaceLabels\n\ngetLabelsForType289\n\nRetrieve interface labels",
    capability=Capability.READ,
)
async def edgeconnect_get_gms_interface_labels(
    ctx: Context,
    type: Annotated[
        str | None,
        Field(
            default=None,
            description="Filter labels by interface type. When specified, returns only labels for that type. If omitted, returns all labels.",
        ),
    ] = None,
    active: Annotated[
        bool | None,
        Field(
            default=None,
            description="Filter labels by active status. When true, returns only active labels; when false, returns only inactive (soft-deleted) labels. If omitted, returns all labels.",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if type is not None:
        query_params["type"] = type
    if active is not None:
        query_params["active"] = active
    return await edgeconnect_request(
        ctx,
        "GET",
        "/gms/interfaceLabels",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_post_gms_interface_labels",
    description="POST /gms/interfaceLabels\n\npostInterfaceLabels288\n\nSave interface labels",
    capability=Capability.WRITE,
)
async def edgeconnect_post_gms_interface_labels(
    ctx: Context,
    deleteDependencies: Annotated[
        bool | None,
        Field(
            default=None,
            description="Auto-remove inactive labels from dependent configurations. When false (default), fails if inactive labels are referenced elsewhere.",
        ),
    ] = None,
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request body")] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if deleteDependencies is not None:
        query_params["deleteDependencies"] = deleteDependencies
    return await edgeconnect_request(
        ctx,
        "POST",
        "/gms/interfaceLabels",
        query_params=query_params or None,
        body=body,
    )


@tool(
    name="edgeconnect_post_interface_labels",
    description="POST /interfaceLabels\n\napplyLabelsToAppliance422\n\nPush interface labels to appliance",
    capability=Capability.WRITE,
)
async def edgeconnect_post_interface_labels(
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
        "POST",
        "/interfaceLabels",
        query_params=query_params or None,
    )
