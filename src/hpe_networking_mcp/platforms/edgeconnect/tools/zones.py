"""Generated EdgeConnect tools — DO NOT EDIT BY HAND.

Emitted by ``scripts/generate_edgeconnect_tools.py`` from
``vendor/edgeconnect/EdgeConnect-9-7-REST-API.json``. Regenerate via:

    uv run python scripts/generate_edgeconnect_tools.py

Tag: ``zones``
Operations in this file: 8
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
    name="edgeconnect_get_zones",
    description="GET /zones\n\nzonesGet940\n\nRetrieve firewall zones",
    capability=Capability.READ,
)
async def edgeconnect_get_zones(
    ctx: Context,
    allVRFZones: Annotated[
        bool | None,
        Field(
            default=None,
            description="When true, returns all zone names assigned to different VRF segments with segment-specific IDs. When false or omitted, returns unique base zone names only.",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if allVRFZones is not None:
        query_params["allVRFZones"] = allVRFZones
    return await edgeconnect_request(
        ctx,
        "GET",
        "/zones",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_zones_ee_enable",
    description="GET /zones/eeEnable\n\nzoneEEEnableGet942\n\nGet End-to-End Zone-Based Firewall status",
    capability=Capability.READ,
)
async def edgeconnect_get_zones_ee_enable(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/zones/eeEnable",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_zones_next_id",
    description="GET /zones/nextId\n\nnextIdGet944\n\nGet next available zone ID",
    capability=Capability.READ,
)
async def edgeconnect_get_zones_next_id(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/zones/nextId",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_zones_vrf_segment_zones_map",
    description="GET /zones/vrfSegmentZonesMap\n\nvrfZonesMapGet946\n\nGet VRF segment zones mapping with full details",
    capability=Capability.READ,
)
async def edgeconnect_get_zones_vrf_segment_zones_map(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/zones/vrfSegmentZonesMap",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_zones_vrf_zones_map",
    description="GET /zones/vrfZonesMap\n\nvrfZonesMapGet947\n\nGet VRF segment to zone index mapping",
    capability=Capability.READ,
)
async def edgeconnect_get_zones_vrf_zones_map(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/zones/vrfZonesMap",
        query_params=None,
    )


@tool(
    name="edgeconnect_post_zones",
    description="POST /zones\n\nzonesPost941\n\nCreate, update, or delete firewall zones",
    capability=Capability.WRITE,
)
async def edgeconnect_post_zones(
    ctx: Context,
    deleteDependencies: Annotated[
        bool,
        Field(
            description="When true, removes deleted zones from overlays, security policies, port profiles, templates, AWS TGNM, Azure VWAN, and SSE connectors. Required parameter."
        ),
    ],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request body")] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if deleteDependencies is not None:
        query_params["deleteDependencies"] = deleteDependencies
    return await edgeconnect_request(
        ctx,
        "POST",
        "/zones",
        query_params=query_params or None,
        body=body,
    )


@tool(
    name="edgeconnect_post_zones_ee_enable",
    description="POST /zones/eeEnable\n\nzoneEEEnablePost943\n\nConfigure End-to-End Zone-Based Firewall",
    capability=Capability.WRITE,
)
async def edgeconnect_post_zones_ee_enable(
    ctx: Context,
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request body")] = None,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/zones/eeEnable",
        query_params=None,
        body=body,
    )


@tool(
    name="edgeconnect_post_zones_next_id",
    description="POST /zones/nextId\n\nnextIdPost945\n\nSet next available zone ID",
    capability=Capability.WRITE,
)
async def edgeconnect_post_zones_next_id(
    ctx: Context,
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request body")] = None,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/zones/nextId",
        query_params=None,
        body=body,
    )
