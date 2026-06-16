"""Generated EdgeConnect tools — DO NOT EDIT BY HAND.

Emitted by ``scripts/generate_edgeconnect_tools.py`` from
``vendor/edgeconnect/EdgeConnect-9-7-REST-API.json``. Regenerate via:

    uv run python scripts/generate_edgeconnect_tools.py

Tag: ``cluster``
Operations in this file: 9
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
    name="edgeconnect_delete_cluster_profiles",
    description="DELETE /cluster/profiles\n\ndeleteClusterProfile\n\nDelete Cluster Profile",
    capability=Capability.WRITE_DELETE,
)
async def edgeconnect_delete_cluster_profiles(
    ctx: Context,
    profileId: Annotated[
        str,
        Field(
            description="UUID of the cluster profile to delete. Must be an existing, non-default profile that is not mapped to any site."
        ),
    ],
) -> Any:
    query_params: dict[str, Any] = {}
    if profileId is not None:
        query_params["profileId"] = profileId
    return await edgeconnect_request(
        ctx,
        "DELETE",
        "/cluster/profiles",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_cluster",
    description="GET /cluster\n\ngetClusterState\n\nGet Cluster State",
    capability=Capability.READ,
)
async def edgeconnect_get_cluster(
    ctx: Context,
    clusterName: Annotated[
        str | None,
        Field(
            default=None,
            description="Filter results by specific cluster/site name. When not provided, returns state for all clusters.",
        ),
    ] = None,
    cached: Annotated[
        bool | None,
        Field(
            default=None,
            description="When true, uses cached flow redirection config from database. When false, fetches fresh data directly from appliances.",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if clusterName is not None:
        query_params["clusterName"] = clusterName
    if cached is not None:
        query_params["cached"] = cached
    return await edgeconnect_request(
        ctx,
        "GET",
        "/cluster",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_cluster_alarm_count",
    description="GET /cluster/alarmCount\n\ngetClusterAlarmCount\n\nGet Cluster Alarm Count",
    capability=Capability.READ,
)
async def edgeconnect_get_cluster_alarm_count(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/cluster/alarmCount",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_cluster_profile_mapping",
    description="GET /cluster/profileMapping\n\ngetClusterProfileMapping\n\nGet All Cluster Profile Mappings",
    capability=Capability.READ,
)
async def edgeconnect_get_cluster_profile_mapping(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/cluster/profileMapping",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_cluster_profiles",
    description="GET /cluster/profiles\n\ngetAllClusterProfiles\n\nGet All Cluster Profiles",
    capability=Capability.READ,
)
async def edgeconnect_get_cluster_profiles(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/cluster/profiles",
        query_params=None,
    )


@tool(
    name="edgeconnect_post_cluster_init_for_edge_ha",
    description="POST /cluster/initForEdgeHA\n\ninitForEdgeHA\n\nInitialize Appliances for EdgeHA Cluster",
    capability=Capability.WRITE,
)
async def edgeconnect_post_cluster_init_for_edge_ha(
    ctx: Context,
    body: Annotated[list[Any], Field(description="Request body (required)")],
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/cluster/initForEdgeHA",
        query_params=None,
        body=body,
    )


@tool(
    name="edgeconnect_post_cluster_profiles",
    description="POST /cluster/profiles\n\naddClusterProfile\n\nAdd Cluster Profiles",
    capability=Capability.WRITE,
)
async def edgeconnect_post_cluster_profiles(
    ctx: Context,
    body: Annotated[list[Any], Field(description="Request body (required)")],
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/cluster/profiles",
        query_params=None,
        body=body,
    )


@tool(
    name="edgeconnect_put_cluster_profile_mapping",
    description="PUT /cluster/profileMapping\n\naddClusterProfileMapping\n\nUpdate Cluster Profile Mappings",
    capability=Capability.WRITE,
)
async def edgeconnect_put_cluster_profile_mapping(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await edgeconnect_request(
        ctx,
        "PUT",
        "/cluster/profileMapping",
        query_params=None,
        body=body,
    )


@tool(
    name="edgeconnect_put_cluster_profiles",
    description="PUT /cluster/profiles\n\nupdateClusterProfile\n\nUpdate Cluster Profile",
    capability=Capability.WRITE,
)
async def edgeconnect_put_cluster_profiles(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await edgeconnect_request(
        ctx,
        "PUT",
        "/cluster/profiles",
        query_params=None,
        body=body,
    )
