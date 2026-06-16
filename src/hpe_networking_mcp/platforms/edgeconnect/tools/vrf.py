"""Generated EdgeConnect tools — DO NOT EDIT BY HAND.

Emitted by ``scripts/generate_edgeconnect_tools.py`` from
``vendor/edgeconnect/EdgeConnect-9-7-REST-API.json``. Regenerate via:

    uv run python scripts/generate_edgeconnect_tools.py

Tag: ``vrf``
Operations in this file: 15
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
    name="edgeconnect_delete_vrf_config_maps",
    description="DELETE /vrf/config/maps\n\nsegmentMapDelete921\n\nDelete Inter-Segment DNAT policies for a source segment",
    capability=Capability.WRITE_DELETE,
)
async def edgeconnect_delete_vrf_config_maps(
    ctx: Context,
    srcSegmentId: Annotated[
        int,
        Field(
            description="Unique identifier of the source routing segment whose Inter-Segment DNAT policies will be deleted. Must be a non-negative integer."
        ),
    ],
) -> Any:
    query_params: dict[str, Any] = {}
    if srcSegmentId is not None:
        query_params["srcSegmentId"] = srcSegmentId
    return await edgeconnect_request(
        ctx,
        "DELETE",
        "/vrf/config/maps",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_delete_vrf_config_segments",
    description="DELETE /vrf/config/segments\n\nsegmentDelete929\n\nDelete a routing segment",
    capability=Capability.WRITE_DELETE,
)
async def edgeconnect_delete_vrf_config_segments(
    ctx: Context,
    id: Annotated[
        int,
        Field(
            description="Unique identifier of the routing segment to delete. Must be a positive integer (greater than 0). The default segment (id=0) cannot be deleted."
        ),
    ],
) -> Any:
    query_params: dict[str, Any] = {}
    if id is not None:
        query_params["id"] = id
    return await edgeconnect_request(
        ctx,
        "DELETE",
        "/vrf/config/segments",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_vrf_config_enable",
    description="GET /vrf/config/enable\n\nsegmentsEnableGet918\n\nGet Routing Segmentation enable status",
    capability=Capability.READ,
)
async def edgeconnect_get_vrf_config_enable(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/vrf/config/enable",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_vrf_config_maps",
    description="GET /vrf/config/maps\n\nsegmentMapGET922\n\nGet Inter-Segment DNAT policies",
    capability=Capability.READ,
)
async def edgeconnect_get_vrf_config_maps(
    ctx: Context,
    srcSegmentId: Annotated[
        int | None,
        Field(
            default=None,
            description="Optional source routing segment ID to filter DNAT policies. If omitted, returns all Inter-Segment DNAT policies for all segments.",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if srcSegmentId is not None:
        query_params["srcSegmentId"] = srcSegmentId
    return await edgeconnect_request(
        ctx,
        "GET",
        "/vrf/config/maps",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_vrf_config_security_policies",
    description="GET /vrf/config/securityPolicies\n\nsecurityMapGet924\n\nGet Security Policies for a segment map",
    capability=Capability.READ,
)
async def edgeconnect_get_vrf_config_security_policies(
    ctx: Context,
    map: Annotated[
        str,
        Field(
            description="Segment map identifier in format 'sourceSegmentId_destinationSegmentId'. Specifies the source and destination routing segments for which to retrieve security policies."
        ),
    ],
) -> Any:
    query_params: dict[str, Any] = {}
    if map is not None:
        query_params["map"] = map
    return await edgeconnect_request(
        ctx,
        "GET",
        "/vrf/config/securityPolicies",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_vrf_config_security_policies_segments",
    description="GET /vrf/config/securityPoliciesSegments\n\ngetSecurityMaps926\n\nGet all security policy segment map identifiers",
    capability=Capability.READ,
)
async def edgeconnect_get_vrf_config_security_policies_segments(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/vrf/config/securityPoliciesSegments",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_vrf_config_segments",
    description="GET /vrf/config/segments\n\nsegmentGet930\n\nGet routing segments",
    capability=Capability.READ,
)
async def edgeconnect_get_vrf_config_segments(
    ctx: Context,
    id: Annotated[
        int | None,
        Field(
            default=None,
            description="Unique identifier of a routing segment to retrieve. If omitted, returns all segments. Use 0 for the default segment.",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if id is not None:
        query_params["id"] = id
    return await edgeconnect_request(
        ctx,
        "GET",
        "/vrf/config/segments",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_vrf_config_snat_maps",
    description="GET /vrf/config/snatMaps\n\nsnatMapsGet932\n\nGet all Inter-Segment SNAT maps",
    capability=Capability.READ,
)
async def edgeconnect_get_vrf_config_snat_maps(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/vrf/config/snatMaps",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_vrf_segments",
    description="GET /vrfSegments\n\ngetApplianceVRFSegmentPolicies\n\nGet Inter-Segment DNAT policies from appliance",
    capability=Capability.READ,
)
async def edgeconnect_get_vrf_segments(
    ctx: Context,
    nePk: Annotated[
        str,
        Field(
            description="Network Element Primary Key - unique appliance identifier assigned by Orchestrator. Format: '<id>.NE' (e.g., '0.NE', '10.NE')."
        ),
    ],
    cached: Annotated[
        str | None,
        Field(
            default=None,
            description="Data retrieval source. When true (default), returns cached data from Orchestrator database. When false, fetches live data directly from the appliance.",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if nePk is not None:
        query_params["nePk"] = nePk
    if cached is not None:
        query_params["cached"] = cached
    return await edgeconnect_request(
        ctx,
        "GET",
        "/vrfSegments",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_post_vrf_config_enable",
    description="POST /vrf/config/enable\n\nsegmentsEnableGPost919\n\nUpdate Routing Segmentation enable status",
    capability=Capability.WRITE,
)
async def edgeconnect_post_vrf_config_enable(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/vrf/config/enable",
        query_params=None,
        body=body,
    )


@tool(
    name="edgeconnect_post_vrf_config_maps",
    description="POST /vrf/config/maps\n\nsegmentMapPost923\n\nCreate or update Inter-Segment DNAT policies for a source segment",
    capability=Capability.WRITE,
)
async def edgeconnect_post_vrf_config_maps(
    ctx: Context,
    srcSegmentId: Annotated[
        int,
        Field(
            description="Source routing segment ID for which to create or update DNAT policies. Must be a non-negative integer representing an existing segment."
        ),
    ],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    query_params: dict[str, Any] = {}
    if srcSegmentId is not None:
        query_params["srcSegmentId"] = srcSegmentId
    return await edgeconnect_request(
        ctx,
        "POST",
        "/vrf/config/maps",
        query_params=query_params or None,
        body=body,
    )


@tool(
    name="edgeconnect_post_vrf_config_security_policies",
    description="POST /vrf/config/securityPolicies\n\nsecurityMapPost925\n\nCreate or update Security Policies for a segment map",
    capability=Capability.WRITE,
)
async def edgeconnect_post_vrf_config_security_policies(
    ctx: Context,
    map: Annotated[
        str,
        Field(
            description="Segment map identifier in format 'sourceSegmentId_destinationSegmentId'. Specifies the source and destination routing segments for which to create/update security policies. Both segment IDs must reference existing segments."
        ),
    ],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
    comment: Annotated[
        str | None,
        Field(
            default=None,
            description="Optional audit log comment for tracking changes. Appears in system action logs with prefix 'Audit Log Comment'.",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if map is not None:
        query_params["map"] = map
    if comment is not None:
        query_params["comment"] = comment
    return await edgeconnect_request(
        ctx,
        "POST",
        "/vrf/config/securityPolicies",
        query_params=query_params or None,
        body=body,
    )


@tool(
    name="edgeconnect_post_vrf_config_segments",
    description="POST /vrf/config/segments\n\nsegmentsPost928\n\nCreate a new routing segment",
    capability=Capability.WRITE,
)
async def edgeconnect_post_vrf_config_segments(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/vrf/config/segments",
        query_params=None,
        body=body,
    )


@tool(
    name="edgeconnect_post_vrf_config_snat_maps",
    description="POST /vrf/config/snatMaps\n\nsnatMapsPost933\n\nCreate or update Inter-Segment SNAT maps",
    capability=Capability.WRITE,
)
async def edgeconnect_post_vrf_config_snat_maps(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/vrf/config/snatMaps",
        query_params=None,
        body=body,
    )


@tool(
    name="edgeconnect_put_vrf_config_segments",
    description="PUT /vrf/config/segments\n\nsegmentPut931\n\nUpdate an existing routing segment",
    capability=Capability.WRITE,
)
async def edgeconnect_put_vrf_config_segments(
    ctx: Context,
    id: Annotated[
        int,
        Field(
            description="Unique identifier of the routing segment to update. Must be a positive integer (1-65400). The default segment (id=0) cannot be modified via this endpoint."
        ),
    ],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    query_params: dict[str, Any] = {}
    if id is not None:
        query_params["id"] = id
    return await edgeconnect_request(
        ctx,
        "PUT",
        "/vrf/config/segments",
        query_params=query_params or None,
        body=body,
    )
