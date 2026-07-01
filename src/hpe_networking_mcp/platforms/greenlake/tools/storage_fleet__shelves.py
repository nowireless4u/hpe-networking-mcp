"""Generated GreenLake tools — DO NOT EDIT BY HAND.

Generated from the vendored spec ``vendor/greenlake/storage-fleet.json`` by the
maintainer-local GreenLake generator. These modules are committed and are the
runtime source of truth; regeneration is a release-time maintainer workflow
(the generator is intentionally not committed — see ``.gitignore``).

Service: ``storage-fleet``   Tag: ``shelves``   Operations: 21
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
    name="greenlake_get_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_enclosure_cards",
    description="GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/enclosure-cards\n\nDeviceType4EnclosureCardList\n\nGet details of HPE Alletra Storage MP B10000 Enclosure Cards identified by {systemId}",
    capability=Capability.READ,
)
async def greenlake_get_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_enclosure_cards(
    ctx: Context,
    systemId: Annotated[str, Field(description="systemId of the storage system")],
    limit: Annotated[int | None, Field(default=None, description="Number of items to return at a time")] = None,
    offset: Annotated[
        int | None, Field(default=None, description="The offset of the first item in the collection to return")
    ] = None,
    filter: Annotated[
        str | None, Field(default=None, description="oData query to filter enclosure resource by Key.")
    ] = None,
    sort: Annotated[
        str | None, Field(default=None, description="oData query to sort enclosure resource by Key.")
    ] = None,
    select: Annotated[
        str | None,
        Field(default=None, description="Query to select only the required parameters, separated by . if nested"),
    ] = None,
) -> Any:
    path = f"/storage-fleet/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/enclosure-cards"
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
    name="greenlake_get_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_enclosure_connectors",
    description="GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/enclosure-connectors\n\nDeviceType4EnclosureConnectorsList\n\nGet details of HPE Alletra Storage MP B10000 Enclosure Connectors",
    capability=Capability.READ,
)
async def greenlake_get_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_enclosure_connectors(
    ctx: Context,
    systemId: Annotated[str, Field(description="systemId of the storage system")],
    limit: Annotated[int | None, Field(default=None, description="Number of items to return at a time")] = None,
    offset: Annotated[
        int | None, Field(default=None, description="The offset of the first item in the collection to return")
    ] = None,
    filter: Annotated[
        str | None, Field(default=None, description="oData query to filter enclosure resource by Key.")
    ] = None,
    sort: Annotated[
        str | None, Field(default=None, description="oData query to sort enclosure resource by Key.")
    ] = None,
    select: Annotated[
        str | None,
        Field(default=None, description="Query to select only the required parameters, separated by . if nested"),
    ] = None,
) -> Any:
    path = f"/storage-fleet/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/enclosure-connectors"
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
    name="greenlake_get_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_enclosures",
    description="GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/enclosures\n\nDeviceType4EnclosuresList\n\nGet details of HPE Alletra Storage MP B10000 Enclosures",
    capability=Capability.READ,
)
async def greenlake_get_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_enclosures(
    ctx: Context,
    systemId: Annotated[str, Field(description="systemId of the storage system")],
    limit: Annotated[int | None, Field(default=None, description="Number of items to return at a time")] = None,
    offset: Annotated[
        int | None, Field(default=None, description="The offset of the first item in the collection to return")
    ] = None,
    filter: Annotated[
        str | None, Field(default=None, description="oData query to filter enclosure resource by Key.")
    ] = None,
    sort: Annotated[
        str | None, Field(default=None, description="oData query to sort enclosure resource by Key.")
    ] = None,
    select: Annotated[
        str | None,
        Field(default=None, description="Query to select only the required parameters, separated by . if nested"),
    ] = None,
) -> Any:
    path = f"/storage-fleet/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/enclosures"
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
    name="greenlake_get_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_enclosures_cage_id_disks",
    description="GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/enclosures/{cageId}/disks\n\nDeviceType4DisksList\n\nGet details of HPE Alletra Storage MP B10000 disks identified by {cageId}",
    capability=Capability.READ,
)
async def greenlake_get_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_enclosures_cage_id_disks(
    ctx: Context,
    systemId: Annotated[str, Field(description="systemId of the storage system")],
    cageId: Annotated[str, Field(description="cage ID")],
    limit: Annotated[int | None, Field(default=None, description="Number of items to return at a time")] = None,
    offset: Annotated[
        int | None, Field(default=None, description="The offset of the first item in the collection to return")
    ] = None,
    filter: Annotated[str | None, Field(default=None, description="oData query to filter Disk by Key.")] = None,
    sort: Annotated[str | None, Field(default=None, description="oData query to sort Disk by Key.")] = None,
    select: Annotated[
        str | None,
        Field(default=None, description="Query to select only the required parameters, separated by . if nested"),
    ] = None,
) -> Any:
    path = f"/storage-fleet/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/enclosures/{path_seg(cageId)}/disks"
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
    name="greenlake_get_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_enclosures_cage_id_disks_id",
    description="GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/enclosures/{cageId}/disks/{id}\n\nDeviceType4DisksGetById\n\nGet details of HPE Alletra Storage MP B10000 disk identified by {cageId} and {id}",
    capability=Capability.READ,
)
async def greenlake_get_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_enclosures_cage_id_disks_id(
    ctx: Context,
    systemId: Annotated[str, Field(description="systemId of the storage system")],
    cageId: Annotated[str, Field(description="cage ID")],
    id: Annotated[str, Field(description="UID of the disk")],
    select: Annotated[
        str | None,
        Field(default=None, description="Query to select only the required parameters, separated by . if nested"),
    ] = None,
) -> Any:
    path = f"/storage-fleet/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/enclosures/{path_seg(cageId)}/disks/{path_seg(id)}"
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
    name="greenlake_get_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_enclosures_enclosure_id_enclosure_cards",
    description="GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/enclosures/{enclosureId}/enclosure-cards\n\nDeviceType4EnclosureCardsList\n\nGet details of HPE Alletra Storage MP B10000 Enclosure Cards identified by {enclosureId}",
    capability=Capability.READ,
)
async def greenlake_get_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_enclosures_enclosure_id_enclosure_cards(
    ctx: Context,
    systemId: Annotated[str, Field(description="systemId of the storage system")],
    enclosureId: Annotated[str, Field(description="UID of the enclosure")],
    limit: Annotated[int | None, Field(default=None, description="Number of items to return at a time")] = None,
    offset: Annotated[
        int | None, Field(default=None, description="The offset of the first item in the collection to return")
    ] = None,
    filter: Annotated[
        str | None, Field(default=None, description="oData query to filter enclosure resource by Key.")
    ] = None,
    sort: Annotated[
        str | None, Field(default=None, description="oData query to sort enclosure resource by Key.")
    ] = None,
    select: Annotated[
        str | None,
        Field(default=None, description="Query to select only the required parameters, separated by . if nested"),
    ] = None,
) -> Any:
    path = f"/storage-fleet/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/enclosures/{path_seg(enclosureId)}/enclosure-cards"
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
    name="greenlake_get_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_enclosures_enclosure_id_enclosure_cards_id",
    description="GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/enclosures/{enclosureId}/enclosure-cards/{id}\n\nDeviceType4EnclosureCardsGetById\n\nGet details of HPE Alletra Storage MP B10000 Enclosure Card identified by {enclosureId} and {id}",
    capability=Capability.READ,
)
async def greenlake_get_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_enclosures_enclosure_id_enclosure_cards_id(
    ctx: Context,
    systemId: Annotated[str, Field(description="systemId of the storage system")],
    enclosureId: Annotated[str, Field(description="UID of the enclosure")],
    id: Annotated[str, Field(description="UID of the enclosure card")],
    select: Annotated[
        str | None,
        Field(default=None, description="Query to select only the required parameters, separated by . if nested"),
    ] = None,
) -> Any:
    path = f"/storage-fleet/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/enclosures/{path_seg(enclosureId)}/enclosure-cards/{path_seg(id)}"
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
    name="greenlake_get_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_enclosures_enclosure_id_enclosure_connectors",
    description="GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/enclosures/{enclosureId}/enclosure-connectors\n\nDeviceType4EnclosureConnectorList\n\nGet details of HPE Alletra Storage MP B10000 Enclosure Connectors identified by {enclosureId}",
    capability=Capability.READ,
)
async def greenlake_get_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_enclosures_enclosure_id_enclosure_connectors(
    ctx: Context,
    systemId: Annotated[str, Field(description="systemId of the storage system")],
    enclosureId: Annotated[str, Field(description="UID of the enclosure")],
    limit: Annotated[int | None, Field(default=None, description="Number of items to return at a time")] = None,
    offset: Annotated[
        int | None, Field(default=None, description="The offset of the first item in the collection to return")
    ] = None,
    filter: Annotated[
        str | None, Field(default=None, description="oData query to filter enclosure resource by Key.")
    ] = None,
    sort: Annotated[
        str | None, Field(default=None, description="oData query to sort enclosure resource by Key.")
    ] = None,
    select: Annotated[
        str | None,
        Field(default=None, description="Query to select only the required parameters, separated by . if nested"),
    ] = None,
) -> Any:
    path = f"/storage-fleet/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/enclosures/{path_seg(enclosureId)}/enclosure-connectors"
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
    name="greenlake_get_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_enclosures_enclosure_id_enclosure_connectors_enclosure_connector_id",
    description="GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/enclosures/{enclosureId}/enclosure-connectors/{enclosureConnectorId}\n\nDeviceType4EnclosureConnectorsGetById\n\nGet details of HPE Alletra Storage MP B10000 Enclosure Connector identified by {enclosureId} and {enclosureConnectorId}",
    capability=Capability.READ,
)
async def greenlake_get_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_enclosures_enclosure_id_enclosure_connectors_enclosure_connector_id(
    ctx: Context,
    systemId: Annotated[str, Field(description="systemId of the storage system")],
    enclosureId: Annotated[str, Field(description="UID of the enclosure")],
    enclosureConnectorId: Annotated[str, Field(description="UID of the enclosure connector")],
    select: Annotated[
        str | None,
        Field(default=None, description="Query to select only the required parameters, separated by . if nested"),
    ] = None,
) -> Any:
    path = f"/storage-fleet/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/enclosures/{path_seg(enclosureId)}/enclosure-connectors/{path_seg(enclosureConnectorId)}"
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
    name="greenlake_get_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_enclosures_enclosure_id_enclosure_disks",
    description="GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/enclosures/{enclosureId}/enclosure-disks\n\nDeviceType4EnclosureDisksList\n\nGet details of HPE Alletra Storage MP B10000 Enclosure Disks identified by {enclosureId}",
    capability=Capability.READ,
)
async def greenlake_get_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_enclosures_enclosure_id_enclosure_disks(
    ctx: Context,
    systemId: Annotated[str, Field(description="systemId of the storage system")],
    enclosureId: Annotated[str, Field(description="UID of the enclosure")],
    limit: Annotated[int | None, Field(default=None, description="Number of items to return at a time")] = None,
    offset: Annotated[
        int | None, Field(default=None, description="The offset of the first item in the collection to return")
    ] = None,
    filter: Annotated[
        str | None, Field(default=None, description="oData query to filter enclosure resource by Key.")
    ] = None,
    sort: Annotated[
        str | None, Field(default=None, description="oData query to sort enclosure resource by Key.")
    ] = None,
    select: Annotated[
        str | None,
        Field(default=None, description="Query to select only the required parameters, separated by . if nested"),
    ] = None,
) -> Any:
    path = f"/storage-fleet/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/enclosures/{path_seg(enclosureId)}/enclosure-disks"
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
    name="greenlake_get_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_enclosures_enclosure_id_enclosure_disks_id",
    description="GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/enclosures/{enclosureId}/enclosure-disks/{id}\n\nDeviceType4EnclosureDisksGetById\n\nGet details of HPE Alletra Storage MP B10000 Enclosure Disk identified by {enclosureId} and {id}",
    capability=Capability.READ,
)
async def greenlake_get_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_enclosures_enclosure_id_enclosure_disks_id(
    ctx: Context,
    systemId: Annotated[str, Field(description="systemId of the storage system")],
    enclosureId: Annotated[str, Field(description="UID of the enclosure")],
    id: Annotated[str, Field(description="UID of the enclosure disk")],
    select: Annotated[
        str | None,
        Field(default=None, description="Query to select only the required parameters, separated by . if nested"),
    ] = None,
) -> Any:
    path = f"/storage-fleet/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/enclosures/{path_seg(enclosureId)}/enclosure-disks/{path_seg(id)}"
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
    name="greenlake_get_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_enclosures_enclosure_id_enclosure_powers",
    description="GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/enclosures/{enclosureId}/enclosure-powers\n\nDeviceType4EnclosurePowersList\n\nGet details of HPE Alletra Storage MP B10000 Enclosure Powers identified by {enclosureId}",
    capability=Capability.READ,
)
async def greenlake_get_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_enclosures_enclosure_id_enclosure_powers(
    ctx: Context,
    systemId: Annotated[str, Field(description="systemId of the storage system")],
    enclosureId: Annotated[str, Field(description="UID of the enclosure")],
    limit: Annotated[int | None, Field(default=None, description="Number of items to return at a time")] = None,
    offset: Annotated[
        int | None, Field(default=None, description="The offset of the first item in the collection to return")
    ] = None,
    filter: Annotated[
        str | None, Field(default=None, description="oData query to filter enclosure resource by Key.")
    ] = None,
    sort: Annotated[
        str | None, Field(default=None, description="oData query to sort enclosure resource by Key.")
    ] = None,
    select: Annotated[
        str | None,
        Field(default=None, description="Query to select only the required parameters, separated by . if nested"),
    ] = None,
) -> Any:
    path = f"/storage-fleet/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/enclosures/{path_seg(enclosureId)}/enclosure-powers"
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
    name="greenlake_get_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_enclosures_enclosure_id_enclosure_powers_id",
    description="GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/enclosures/{enclosureId}/enclosure-powers/{id}\n\nDeviceType4EnclosurePowersGetById\n\nGet details of HPE Alletra Storage MP B10000 Enclosure Power identified by {enclosureId} and {id}",
    capability=Capability.READ,
)
async def greenlake_get_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_enclosures_enclosure_id_enclosure_powers_id(
    ctx: Context,
    systemId: Annotated[str, Field(description="systemId of the storage system")],
    enclosureId: Annotated[str, Field(description="UID of the enclosure")],
    id: Annotated[str, Field(description="UID of the enclosure power")],
    select: Annotated[
        str | None,
        Field(default=None, description="Query to select only the required parameters, separated by . if nested"),
    ] = None,
) -> Any:
    path = f"/storage-fleet/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/enclosures/{path_seg(enclosureId)}/enclosure-powers/{path_seg(id)}"
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
    name="greenlake_get_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_enclosures_enclosure_id_enclosure_sleds",
    description="GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/enclosures/{enclosureId}/enclosure-sleds\n\nDeviceType4EnclosureSledsList\n\nGet details of HPE Alletra Storage MP B10000 Enclosure Sleds identified by {enclosureId}",
    capability=Capability.READ,
)
async def greenlake_get_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_enclosures_enclosure_id_enclosure_sleds(
    ctx: Context,
    systemId: Annotated[str, Field(description="systemId of the storage system")],
    enclosureId: Annotated[str, Field(description="UID of the enclosure")],
    limit: Annotated[int | None, Field(default=None, description="Number of items to return at a time")] = None,
    offset: Annotated[
        int | None, Field(default=None, description="The offset of the first item in the collection to return")
    ] = None,
    filter: Annotated[
        str | None, Field(default=None, description="oData query to filter enclosure resource by Key.")
    ] = None,
    sort: Annotated[
        str | None, Field(default=None, description="oData query to sort enclosure resource by Key.")
    ] = None,
    select: Annotated[
        str | None,
        Field(default=None, description="Query to select only the required parameters, separated by . if nested"),
    ] = None,
) -> Any:
    path = f"/storage-fleet/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/enclosures/{path_seg(enclosureId)}/enclosure-sleds"
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
    name="greenlake_get_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_enclosures_enclosure_id_enclosure_sleds_id",
    description="GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/enclosures/{enclosureId}/enclosure-sleds/{id}\n\nDeviceType4EnclosureSledsGetById\n\nGet details of HPE Alletra Storage MP B10000 Enclosure Sled identified by {enclosureId} and {id}",
    capability=Capability.READ,
)
async def greenlake_get_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_enclosures_enclosure_id_enclosure_sleds_id(
    ctx: Context,
    systemId: Annotated[str, Field(description="systemId of the storage system")],
    enclosureId: Annotated[str, Field(description="UID of the enclosure")],
    id: Annotated[str, Field(description="UID of the enclosure sled")],
    select: Annotated[
        str | None,
        Field(default=None, description="Query to select only the required parameters, separated by . if nested"),
    ] = None,
) -> Any:
    path = f"/storage-fleet/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/enclosures/{path_seg(enclosureId)}/enclosure-sleds/{path_seg(id)}"
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
    name="greenlake_get_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_enclosures_id",
    description="GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/enclosures/{id}\n\nDeviceType4EnclosuresGetById\n\nGet details of HPE Alletra Storage MP B10000 Enclosure identified by {id}",
    capability=Capability.READ,
)
async def greenlake_get_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_enclosures_id(
    ctx: Context,
    systemId: Annotated[str, Field(description="systemId of the storage system")],
    id: Annotated[str, Field(description="UID of the enclosure")],
    select: Annotated[
        str | None,
        Field(default=None, description="Query to select only the required parameters, separated by . if nested"),
    ] = None,
) -> Any:
    path = f"/storage-fleet/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/enclosures/{path_seg(id)}"
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
    name="greenlake_get_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_physicaldrives_performance",
    description="GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/physicaldrives-performance\n\nDeviceType4PhysicalDrivePerformanceHistoryGet\n\nGet details of performance metrics of physical drives on storage system identified by {systemid}",
    capability=Capability.READ,
)
async def greenlake_get_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_physicaldrives_performance(
    ctx: Context,
    systemId: Annotated[str, Field(description="systemId of the storage system")],
    report_type: Annotated[
        str | None,
        Field(
            default=None,
            description="parameter will be set to report type requested. For api users, set parameter as ApiUser",
        ),
    ] = None,
    range: Annotated[
        str | None,
        Field(default=None, description="range will define start and end time in which query has to be made."),
    ] = None,
    time_interval_min: Annotated[
        int | None, Field(default=None, description="It defines granularity in minutes.")
    ] = None,
    compare_by: Annotated[
        str | None,
        Field(
            default=None,
            description="compareBy will define top and compare metrics for which query has to be made. Allowed values: `readIops, writeIops, totalIops, readThroughput, writeThroughput, totalThroughput, readLatency, writeLatency, totalLatency, readIosize, writeIosize, totalIosize, totalQlen, avgBusy`",
        ),
    ] = None,
    group_by: Annotated[
        str | None,
        Field(
            default=None,
            description="groupBy will define comma separated groupBy parameters. Allowed value: `pdId`. By default, groupBy will be set to `pdId`.",
        ),
    ] = None,
    metric_type: Annotated[
        str | None, Field(default=None, description="metricType will define comma separated metrics")
    ] = None,
    filter: Annotated[
        str | None,
        Field(
            default=None,
            description="filter will define objects to be filtered. Filterable columns are: * `pdId` - id of the physical drive",
        ),
    ] = None,
) -> Any:
    path = f"/storage-fleet/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/physicaldrives-performance"
    query_params: dict[str, Any] = {}
    if report_type is not None:
        query_params["report-type"] = report_type
    if range is not None:
        query_params["range"] = range
    if time_interval_min is not None:
        query_params["time-interval-min"] = time_interval_min
    if compare_by is not None:
        query_params["compare-by"] = compare_by
    if group_by is not None:
        query_params["group-by"] = group_by
    if metric_type is not None:
        query_params["metric-type"] = metric_type
    if filter is not None:
        query_params["filter"] = filter
    return await greenlake_request(
        ctx,
        "GET",
        path,
        query_params=query_params or None,
    )


@tool(
    name="greenlake_post_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_enclosures_enclosure_id_enclosure_cards_id",
    description="POST /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/enclosures/{enclosureId}/enclosure-cards/{id}\n\nDeviceType4EnclosureCardsLocateIOById\n\nLocate IO Module of HPE Alletra Storage MP B10000 identified by {id}",
    capability=Capability.WRITE,
)
async def greenlake_post_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_enclosures_enclosure_id_enclosure_cards_id(
    ctx: Context,
    systemId: Annotated[str, Field(description="systemId of the storage system")],
    enclosureId: Annotated[str, Field(description="UID of the enclosure")],
    id: Annotated[str, Field(description="UID of the enclosure card")],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    path = f"/storage-fleet/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/enclosures/{path_seg(enclosureId)}/enclosure-cards/{path_seg(id)}"
    return await greenlake_request(
        ctx,
        "POST",
        path,
        body=body,
    )


@tool(
    name="greenlake_post_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_enclosures_enclosure_id_enclosure_sleds_id",
    description="POST /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/enclosures/{enclosureId}/enclosure-sleds/{id}\n\nDeviceType4EnclosureSledsLocateDriveById\n\nLocate drive of HPE Alletra Storage MP B10000 identified by {id}",
    capability=Capability.WRITE,
)
async def greenlake_post_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_enclosures_enclosure_id_enclosure_sleds_id(
    ctx: Context,
    systemId: Annotated[str, Field(description="systemId of the storage system")],
    enclosureId: Annotated[str, Field(description="UID of the enclosure")],
    id: Annotated[str, Field(description="UID of the enclosure sled")],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    path = f"/storage-fleet/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/enclosures/{path_seg(enclosureId)}/enclosure-sleds/{path_seg(id)}"
    return await greenlake_request(
        ctx,
        "POST",
        path,
        body=body,
    )


@tool(
    name="greenlake_post_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_enclosures_id",
    description="POST /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/enclosures/{id}\n\nDeviceType4EnclosuresLocateById\n\nLocate enclosure drive of HPE Alletra Storage MP B10000 identified by {id}",
    capability=Capability.WRITE,
)
async def greenlake_post_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_enclosures_id(
    ctx: Context,
    systemId: Annotated[str, Field(description="systemId of the storage system")],
    id: Annotated[str, Field(description="UID of the enclosure")],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    path = f"/storage-fleet/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/enclosures/{path_seg(id)}"
    return await greenlake_request(
        ctx,
        "POST",
        path,
        body=body,
    )


@tool(
    name="greenlake_put_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_enclosures_id",
    description="PUT /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/enclosures/{id}\n\nDeviceType4EnclosuresEditById\n\nEdit details of HPE Alletra Storage MP B10000 Enclosure identified by {id}",
    capability=Capability.WRITE,
)
async def greenlake_put_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_enclosures_id(
    ctx: Context,
    systemId: Annotated[str, Field(description="systemId of the storage system")],
    id: Annotated[str, Field(description="UID of the enclosure")],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    path = f"/storage-fleet/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/enclosures/{path_seg(id)}"
    return await greenlake_request(
        ctx,
        "PUT",
        path,
        body=body,
    )
