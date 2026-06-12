"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``scripts/_mist_generator.py`` from
``vendor/mist/mist_openapi.json``. Regenerate via:

    uv run python scripts/regenerate_mist_tools.py

Tag: ``Sites Devices - WAN Cluster``
Operations in this file: 3
"""

# ruff: noqa: E501

from __future__ import annotations

from typing import Annotated, Any

from fastmcp import Context
from pydantic import Field

from hpe_networking_mcp.platforms._common.annotations import Capability
from hpe_networking_mcp.platforms.mist._client import mist_request
from hpe_networking_mcp.platforms.mist._registry import tool as _mcp_tool


@_mcp_tool(
    name="mist_create_site_device_ha_cluster",
    description="POST /api/v1/sites/{site_id}/devices/{device_id}/ha\n\ncreateSiteDeviceHaCluster\n\n## Create HA Cluster\nBoth nodes has to be in the same site. We expect the user to configure ha_sync / ha_data port in port_configs already\n\n### SRX cabling\n\nsee [Chassis Cluster User Guide for SRX Series Devices](https://www.juniper.net/documentation/us/en/software/junos/chassis-cluster-security-devices/topics/concept/chassis-cluster-srx-series-node-interface-understanding.html) Here’s the recommended cabling.\n\n#### SRX300\n\nFrom ZTP / default state, ge-0/0/0 and ge-0/0/7 (SFP) are default WAN ports and will get ...",
    capability=Capability.WRITE,
)
async def mist_create_site_device_ha_cluster(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    device_id: Annotated[str, Field(description="path parameter 'device_id'")],
    body: Annotated[
        dict[str, Any] | None,
        Field(default=None, description="Request body for POST /api/v1/sites/{site_id}/devices/{device_id}/ha"),
    ] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/sites/{site_id}/devices/{device_id}/ha",
        path_params={"site_id": site_id, "device_id": device_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_delete_site_device_ha_cluster",
    description="DELETE /api/v1/sites/{site_id}/devices/{device_id}/ha\n\ndeleteSiteDeviceHaCluster\n\nDelete HA Cluster",
    capability=Capability.WRITE_DELETE,
)
async def mist_delete_site_device_ha_cluster(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    device_id: Annotated[str, Field(description="path parameter 'device_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "DELETE",
        "/api/v1/sites/{site_id}/devices/{device_id}/ha",
        path_params={"site_id": site_id, "device_id": device_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_get_site_device_ha_cluster_node",
    description="GET /api/v1/sites/{site_id}/devices/{device_id}/ha\n\nGetSiteDeviceHaClusterNode\n\nDelete HA Cluster",
    capability=Capability.READ,
)
async def mist_get_site_device_ha_cluster_node(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    device_id: Annotated[str, Field(description="path parameter 'device_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/sites/{site_id}/devices/{device_id}/ha",
        path_params={"site_id": site_id, "device_id": device_id},
        query_params=None,
        body=None,
    )
