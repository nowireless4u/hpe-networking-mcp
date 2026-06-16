"""Generated EdgeConnect tools — DO NOT EDIT BY HAND.

Emitted by ``scripts/generate_edgeconnect_tools.py`` from
``vendor/edgeconnect/EdgeConnect-9-7-REST-API.json``. Regenerate via:

    uv run python scripts/generate_edgeconnect_tools.py

Tag: ``overlayAssociation``
Operations in this file: 4
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
    name="edgeconnect_delete_gms_overlays_association",
    description="DELETE /gms/overlays/association\n\ndeleteOverlayApplianceAssociation313\n\nRemove an appliance from an overlay",
    capability=Capability.WRITE_DELETE,
)
async def edgeconnect_delete_gms_overlays_association(
    ctx: Context,
    overlayId: Annotated[
        str,
        Field(
            description="Numeric ID of the overlay from which to remove the appliance. Must be a valid existing overlay."
        ),
    ],
    nePk: Annotated[
        str,
        Field(
            description="Network Element Primary Key - unique appliance identifier assigned by Orchestrator. Format: '<id>.NE' (e.g., '0.NE', '10.NE')."
        ),
    ],
) -> Any:
    query_params: dict[str, Any] = {}
    if overlayId is not None:
        query_params["overlayId"] = overlayId
    if nePk is not None:
        query_params["nePk"] = nePk
    return await edgeconnect_request(
        ctx,
        "DELETE",
        "/gms/overlays/association",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_gms_overlays_association",
    description="GET /gms/overlays/association\n\ngetAppliancesForOverlay312\n\nGet overlay-appliance associations",
    capability=Capability.READ,
)
async def edgeconnect_get_gms_overlays_association(
    ctx: Context,
    overlayId: Annotated[
        int | None,
        Field(
            default=None,
            description="Filter results to a specific overlay. When omitted, returns associations for all overlays.",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if overlayId is not None:
        query_params["overlayId"] = overlayId
    return await edgeconnect_request(
        ctx,
        "GET",
        "/gms/overlays/association",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_post_gms_overlays_association",
    description="POST /gms/overlays/association\n\naddOverlayApplianceAssociations310\n\nAdd appliances to overlays",
    capability=Capability.WRITE,
)
async def edgeconnect_post_gms_overlays_association(
    ctx: Context,
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request body")] = None,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/gms/overlays/association",
        query_params=None,
        body=body,
    )


@tool(
    name="edgeconnect_post_gms_overlays_association_remove",
    description="POST /gms/overlays/association/remove\n\nremoveAppliancesFromOverlays311\n\nRemove appliances from overlays",
    capability=Capability.WRITE,
)
async def edgeconnect_post_gms_overlays_association_remove(
    ctx: Context,
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request body")] = None,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/gms/overlays/association/remove",
        query_params=None,
        body=body,
    )
