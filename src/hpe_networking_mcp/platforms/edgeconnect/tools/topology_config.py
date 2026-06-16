"""Generated EdgeConnect tools — DO NOT EDIT BY HAND.

Emitted by ``scripts/generate_edgeconnect_tools.py`` from
``vendor/edgeconnect/EdgeConnect-9-7-REST-API.json``. Regenerate via:

    uv run python scripts/generate_edgeconnect_tools.py

Tag: ``topologyConfig``
Operations in this file: 10
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
    name="edgeconnect_get_gms_topology_config",
    description="GET /gms/topologyConfig\n\ngetDefaultTopologyConfig346\n\nRetrieve topology view configuration for the authenticated user",
    capability=Capability.READ,
)
async def edgeconnect_get_gms_topology_config(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/gms/topologyConfig",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_gms_topology_config_export",
    description="GET /gms/topologyConfig/export\n\nexportTopologyInfoForTunnelType352\n\nExport topology tunnel details as CSV file",
    capability=Capability.READ,
)
async def edgeconnect_get_gms_topology_config_export(
    ctx: Context,
    nePk: Annotated[
        str,
        Field(
            description="Network Element Primary Key - unique appliance identifier assigned by Orchestrator. Format: '<id>.NE' (e.g., '0.NE', '10.NE')."
        ),
    ],
    tunnelType: Annotated[
        str | None,
        Field(
            default=None,
            description="Type of tunnel to export. Controls which tunnel category is included in the CSV output.",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if nePk is not None:
        query_params["nePk"] = nePk
    if tunnelType is not None:
        query_params["tunnelType"] = tunnelType
    return await edgeconnect_request(
        ctx,
        "GET",
        "/gms/topologyConfig/export",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_gms_topology_config_link_info",
    description="GET /gms/topologyConfig/linkInfo\n\ngetLinkInfoForOverlayId\n\nGet tunnel link status matrix for an overlay network",
    capability=Capability.READ,
)
async def edgeconnect_get_gms_topology_config_link_info(
    ctx: Context,
    overlayId: Annotated[
        str, Field(description="Unique identifier of the overlay network to query. Cannot be null or empty.")
    ],
    If_None_Match: Annotated[
        str | None,
        Field(
            default=None,
            description="ETag value from previous response for conditional caching. If provided and cache is valid, returns 304.",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if overlayId is not None:
        query_params["overlayId"] = overlayId
    header_params: dict[str, Any] = {}
    if If_None_Match is not None:
        header_params["If-None-Match"] = If_None_Match
    return await edgeconnect_request(
        ctx,
        "GET",
        "/gms/topologyConfig/linkInfo",
        query_params=query_params or None,
        header_params=header_params or None,
    )


@tool(
    name="edgeconnect_get_gms_topology_config_link_info_v2",
    description="GET /gms/topologyConfig/linkInfo/v2\n\ngetLinkInfoForOverlayIdV2\n\nGet sparse tunnel link status pairs for an overlay network (v2)",
    capability=Capability.READ,
)
async def edgeconnect_get_gms_topology_config_link_info_v2(
    ctx: Context,
    overlayId: Annotated[
        str,
        Field(
            description="Overlay network identifier. Use 'all' for worst-case status across all overlays, '0' for underlays, or a specific overlay ID (e.g. '1', '2')."
        ),
    ],
    If_None_Match: Annotated[
        str | None,
        Field(
            default=None,
            description="ETag value from previous response for conditional caching. If provided and cache is valid, returns 304.",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if overlayId is not None:
        query_params["overlayId"] = overlayId
    header_params: dict[str, Any] = {}
    if If_None_Match is not None:
        header_params["If-None-Match"] = If_None_Match
    return await edgeconnect_request(
        ctx,
        "GET",
        "/gms/topologyConfig/linkInfo/v2",
        query_params=query_params or None,
        header_params=header_params or None,
    )


@tool(
    name="edgeconnect_post_gms_topology_config",
    description="POST /gms/topologyConfig\n\nupdateTopologyConfig347\n\nSave topology view configuration for the authenticated user",
    capability=Capability.WRITE,
)
async def edgeconnect_post_gms_topology_config(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/gms/topologyConfig",
        query_params=None,
        body=body,
    )


@tool(
    name="edgeconnect_post_gms_topology_config_export",
    description="POST /gms/topologyConfig/export\n\nexportTopologyInfo348\n\nExport all tunnel topology for multiple appliances as CSV",
    capability=Capability.WRITE,
)
async def edgeconnect_post_gms_topology_config_export(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/gms/topologyConfig/export",
        query_params=None,
        body=body,
    )


@tool(
    name="edgeconnect_post_gms_topology_config_export_overlay",
    description="POST /gms/topologyConfig/export/overlay\n\nexportOverlayTopologyInfo349\n\nExport overlay (bonded) tunnel topology as CSV",
    capability=Capability.WRITE,
)
async def edgeconnect_post_gms_topology_config_export_overlay(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/gms/topologyConfig/export/overlay",
        query_params=None,
        body=body,
    )


@tool(
    name="edgeconnect_post_gms_topology_config_export_passthrough",
    description="POST /gms/topologyConfig/export/passthrough\n\nexportPassthroughTopologyInfo350\n\nExport passthrough tunnel topology as CSV",
    capability=Capability.WRITE,
)
async def edgeconnect_post_gms_topology_config_export_passthrough(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/gms/topologyConfig/export/passthrough",
        query_params=None,
        body=body,
    )


@tool(
    name="edgeconnect_post_gms_topology_config_export_underlay",
    description="POST /gms/topologyConfig/export/underlay\n\nexportUnderlayTopologyInfo351\n\nExport underlay (physical) tunnel topology as CSV",
    capability=Capability.WRITE,
)
async def edgeconnect_post_gms_topology_config_export_underlay(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/gms/topologyConfig/export/underlay",
        query_params=None,
        body=body,
    )


@tool(
    name="edgeconnect_post_gms_topology_config_map",
    description="POST /gms/topologyConfig/map\n\nsaveMapImage354\n\nUpdate the global topology background map image",
    capability=Capability.WRITE,
)
async def edgeconnect_post_gms_topology_config_map(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/gms/topologyConfig/map",
        query_params=None,
        body=body,
    )
