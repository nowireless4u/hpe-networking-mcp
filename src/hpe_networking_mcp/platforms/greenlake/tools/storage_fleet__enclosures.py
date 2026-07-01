"""Generated GreenLake tools — DO NOT EDIT BY HAND.

Generated from the vendored spec ``vendor/greenlake/storage-fleet.json`` by the
maintainer-local GreenLake generator. These modules are committed and are the
runtime source of truth; regeneration is a release-time maintainer workflow
(the generator is intentionally not committed — see ``.gitignore``).

Service: ``storage-fleet``   Tag: ``enclosures``   Operations: 3
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
    name="greenlake_get_storage_fleet_v1alpha1_devtype7_storage_systems_system_id_enclosures",
    description="GET /storage-fleet/v1alpha1/devtype7-storage-systems/{systemId}/enclosures\n\nDeviceType7GetEnclosures\n\nGet all enclosures of a HPE Alletra Storage MP X10000 system",
    capability=Capability.READ,
)
async def greenlake_get_storage_fleet_v1alpha1_devtype7_storage_systems_system_id_enclosures(
    ctx: Context,
    systemId: Annotated[str, Field(description="ID of the storage system")],
    limit: Annotated[int | None, Field(default=None, description="Number of items to return at a time")] = None,
    offset: Annotated[
        int | None, Field(default=None, description="The offset of the first item in the collection to return")
    ] = None,
    select: Annotated[
        str | None,
        Field(default=None, description="Query to select only the required parameters, separated by . if nested"),
    ] = None,
    filter: Annotated[str | None, Field(default=None, description="Lucene query to filter Enclosures by Key.")] = None,
    sort: Annotated[
        str | None, Field(default=None, description="Data query to sort Enclosure resource by Key.")
    ] = None,
) -> Any:
    path = f"/storage-fleet/v1alpha1/devtype7-storage-systems/{path_seg(systemId)}/enclosures"
    query_params: dict[str, Any] = {}
    if limit is not None:
        query_params["limit"] = limit
    if offset is not None:
        query_params["offset"] = offset
    if select is not None:
        query_params["select"] = select
    if filter is not None:
        query_params["filter"] = filter
    if sort is not None:
        query_params["sort"] = sort
    return await greenlake_request(
        ctx,
        "GET",
        path,
        query_params=query_params or None,
    )


@tool(
    name="greenlake_get_storage_fleet_v1alpha1_devtype7_storage_systems_system_id_enclosures_enclosure_id",
    description="GET /storage-fleet/v1alpha1/devtype7-storage-systems/{systemId}/enclosures/{enclosureId}\n\nDeviceType7GetEnclosureById\n\nGet Enclosure of a HPE Alletra Storage MP X10000 system identified by enclosureID",
    capability=Capability.READ,
)
async def greenlake_get_storage_fleet_v1alpha1_devtype7_storage_systems_system_id_enclosures_enclosure_id(
    ctx: Context,
    systemId: Annotated[str, Field(description="ID of the storage system")],
    enclosureId: Annotated[str, Field(description="Identifier of Enclosure. A 42 digit hexadecimal number.")],
    select: Annotated[
        str | None,
        Field(default=None, description="Query to select only the required parameters, separated by . if nested"),
    ] = None,
) -> Any:
    path = f"/storage-fleet/v1alpha1/devtype7-storage-systems/{path_seg(systemId)}/enclosures/{path_seg(enclosureId)}"
    query_params: dict[str, Any] = {}
    if select is not None:
        query_params["select"] = select
    return await greenlake_request(
        ctx,
        "GET",
        path,
        query_params=query_params or None,
    )


@tool(
    name="greenlake_put_storage_fleet_v1alpha1_devtype7_storage_systems_system_id_enclosures_enclosure_id",
    description="PUT /storage-fleet/v1alpha1/devtype7-storage-systems/{systemId}/enclosures/{enclosureId}\n\nDeviceType7EditEnclosureById\n\nEdit settings of HPE Alletra Storage MP X10000 system Enclosure identified by {enclosureId}",
    capability=Capability.WRITE,
)
async def greenlake_put_storage_fleet_v1alpha1_devtype7_storage_systems_system_id_enclosures_enclosure_id(
    ctx: Context,
    systemId: Annotated[str, Field(description="ID of the storage system")],
    enclosureId: Annotated[str, Field(description="Identifier of Enclosure. A 42 digit hexadecimal number.")],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    path = f"/storage-fleet/v1alpha1/devtype7-storage-systems/{path_seg(systemId)}/enclosures/{path_seg(enclosureId)}"
    return await greenlake_request(
        ctx,
        "PUT",
        path,
        body=body,
    )
