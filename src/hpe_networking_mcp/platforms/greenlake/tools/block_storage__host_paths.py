"""Generated GreenLake tools — DO NOT EDIT BY HAND.

Generated from the vendored spec ``vendor/greenlake/block-storage.json`` by the
maintainer-local GreenLake generator. These modules are committed and are the
runtime source of truth; regeneration is a release-time maintainer workflow
(the generator is intentionally not committed — see ``.gitignore``).

Service: ``block-storage``   Tag: ``host_paths``   Operations: 2
"""

# ruff: noqa: E501, N803
from __future__ import annotations

from typing import Annotated, Any

from fastmcp import Context
from pydantic import Field

from hpe_networking_mcp.platforms._common.annotations import Capability
from hpe_networking_mcp.platforms._common.url import path_seg
from hpe_networking_mcp.platforms.greenlake._registry import tool
from hpe_networking_mcp.platforms.greenlake.client import greenlake_request


@tool(
    name="greenlake_get_block_storage_v1alpha1_devtype4_storage_systems_system_id_host_paths",
    description="GET /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/host-paths\n\nDeviceType4GetAllHostPaths\n\nGet details of HPE Alletra Storage MP B10000 Host Paths",
    capability=Capability.READ,
)
async def greenlake_get_block_storage_v1alpha1_devtype4_storage_systems_system_id_host_paths(
    ctx: Context,
    systemId: Annotated[str, Field(description="systemId of the storage system")],
    limit: Annotated[int | None, Field(default=None, description="Number of items to return at a time")] = None,
    offset: Annotated[
        int | None, Field(default=None, description="The offset of the first item in the collection to return")
    ] = None,
    filter: Annotated[str | None, Field(default=None, description="Lucene query to filter host path by Key.")] = None,
    sort: Annotated[
        str | None, Field(default=None, description="oData query to sort host path resource by Key.")
    ] = None,
    select: Annotated[
        str | None,
        Field(default=None, description="Query to select only the required parameters, separated by . if nested"),
    ] = None,
) -> Any:
    path = f"/block-storage/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/host-paths"
    query_params: dict[str, Any] = {}
    if limit is not None:
        query_params["limit"] = limit
    if offset is not None:
        query_params["offset"] = offset
    if filter is not None:
        query_params["filter"] = filter
    if sort is not None:
        query_params["sort"] = sort
    if select is not None:
        query_params["select"] = select
    return await greenlake_request(
        ctx,
        "GET",
        path,
        query_params=query_params or None,
    )


@tool(
    name="greenlake_get_block_storage_v1alpha1_devtype4_storage_systems_system_id_host_paths_host_path_id",
    description="GET /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/host-paths/{hostPathId}\n\nDeviceType4GetHostPathsById\n\nGet details of HPE Alletra Storage MP B10000 Host Path identified by {HostPathId}",
    capability=Capability.READ,
)
async def greenlake_get_block_storage_v1alpha1_devtype4_storage_systems_system_id_host_paths_host_path_id(
    ctx: Context,
    systemId: Annotated[str, Field(description="systemId of the storage system")],
    hostPathId: Annotated[
        str, Field(description="ID of the HPE Alletra Storage MP B10000 Host Path. A 42 digit hexadecimal number.")
    ],
    select: Annotated[
        str | None,
        Field(default=None, description="Query to select only the required parameters, separated by . if nested"),
    ] = None,
) -> Any:
    path = f"/block-storage/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/host-paths/{path_seg(hostPathId)}"
    query_params: dict[str, Any] = {}
    if select is not None:
        query_params["select"] = select
    return await greenlake_request(
        ctx,
        "GET",
        path,
        query_params=query_params or None,
    )
