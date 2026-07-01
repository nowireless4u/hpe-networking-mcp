"""Generated GreenLake tools — DO NOT EDIT BY HAND.

Generated from the vendored spec ``vendor/greenlake/storage-fleet.json`` by the
maintainer-local GreenLake generator. These modules are committed and are the
runtime source of truth; regeneration is a release-time maintainer workflow
(the generator is intentionally not committed — see ``.gitignore``).

Service: ``storage-fleet``   Tag: ``switches``   Operations: 13
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
    name="greenlake_get_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_switch_ports",
    description="GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/switch-ports\n\nDeviceType4SwitchPortsList\n\nGet details of HPE Alletra Storage MP B10000 Switch ports",
    capability=Capability.READ,
)
async def greenlake_get_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_switch_ports(
    ctx: Context,
    systemId: Annotated[str, Field(description="systemId of the storage system")],
    limit: Annotated[int | None, Field(default=None, description="Number of items to return at a time")] = None,
    offset: Annotated[
        int | None, Field(default=None, description="The offset of the first item in the collection to return")
    ] = None,
    filter: Annotated[
        str | None, Field(default=None, description="oData query to filter switch resource by Key.")
    ] = None,
    sort: Annotated[str | None, Field(default=None, description="oData query to sort switch resource by Key.")] = None,
    select: Annotated[
        str | None,
        Field(default=None, description="Query to select only the required parameters, separated by . if nested"),
    ] = None,
) -> Any:
    path = f"/storage-fleet/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/switch-ports"
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
    name="greenlake_get_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_switches",
    description="GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/switches\n\nDeviceType4SwitchesList\n\nGet details of HPE Alletra Storage MP B10000 Switches",
    capability=Capability.READ,
)
async def greenlake_get_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_switches(
    ctx: Context,
    systemId: Annotated[str, Field(description="systemId of the storage system")],
    limit: Annotated[int | None, Field(default=None, description="Number of items to return at a time")] = None,
    offset: Annotated[
        int | None, Field(default=None, description="The offset of the first item in the collection to return")
    ] = None,
    filter: Annotated[
        str | None, Field(default=None, description="oData query to filter switch resource by Key.")
    ] = None,
    sort: Annotated[str | None, Field(default=None, description="oData query to sort switch resource by Key.")] = None,
    select: Annotated[
        str | None,
        Field(default=None, description="Query to select only the required parameters, separated by . if nested"),
    ] = None,
) -> Any:
    path = f"/storage-fleet/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/switches"
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
    name="greenlake_get_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_switches_id",
    description="GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/switches/{id}\n\nDeviceType4SwitchesGetById\n\nGet details of HPE Alletra Storage MP B10000 Switch identified by {id}",
    capability=Capability.READ,
)
async def greenlake_get_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_switches_id(
    ctx: Context,
    systemId: Annotated[str, Field(description="systemId of the storage system")],
    id: Annotated[str, Field(description="UID of the switch")],
    select: Annotated[
        str | None,
        Field(default=None, description="Query to select only the required parameters, separated by . if nested"),
    ] = None,
) -> Any:
    path = f"/storage-fleet/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/switches/{path_seg(id)}"
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
    name="greenlake_get_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_switches_switch_id_switch_fans",
    description="GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/switches/{switchId}/switch-fans\n\nDeviceType4SwitchFanList\n\nGet details of HPE Alletra Storage MP B10000 Switch Fans identified by switch id",
    capability=Capability.READ,
)
async def greenlake_get_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_switches_switch_id_switch_fans(
    ctx: Context,
    systemId: Annotated[str, Field(description="systemId of the storage system")],
    switchId: Annotated[str, Field(description="UID of the switch")],
    limit: Annotated[int | None, Field(default=None, description="Number of items to return at a time")] = None,
    offset: Annotated[
        int | None, Field(default=None, description="The offset of the first item in the collection to return")
    ] = None,
    filter: Annotated[
        str | None, Field(default=None, description="oData query to filter switch resource by Key.")
    ] = None,
    sort: Annotated[str | None, Field(default=None, description="oData query to sort switch resource by Key.")] = None,
    select: Annotated[
        str | None,
        Field(default=None, description="Query to select only the required parameters, separated by . if nested"),
    ] = None,
) -> Any:
    path = f"/storage-fleet/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/switches/{path_seg(switchId)}/switch-fans"
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
    name="greenlake_get_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_switches_switch_id_switch_fans_id",
    description="GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/switches/{switchId}/switch-fans/{id}\n\nDeviceType4SwitchFanGetById\n\nGet details of HPE Alletra Storage MP B10000 Switch Fan identified by switchId} and Fan id",
    capability=Capability.READ,
)
async def greenlake_get_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_switches_switch_id_switch_fans_id(
    ctx: Context,
    systemId: Annotated[str, Field(description="systemId of the storage system")],
    switchId: Annotated[str, Field(description="UID of the switch")],
    id: Annotated[str, Field(description="UID of the switch fan")],
    select: Annotated[
        str | None,
        Field(default=None, description="Query to select only the required parameters, separated by . if nested"),
    ] = None,
) -> Any:
    path = f"/storage-fleet/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/switches/{path_seg(switchId)}/switch-fans/{path_seg(id)}"
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
    name="greenlake_get_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_switches_switch_id_switch_ports",
    description="GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/switches/{switchId}/switch-ports\n\nDeviceType4SwitchPortList\n\nGet details of HPE Alletra Storage MP B10000 Switch ports identified by {switchId}",
    capability=Capability.READ,
)
async def greenlake_get_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_switches_switch_id_switch_ports(
    ctx: Context,
    systemId: Annotated[str, Field(description="systemId of the storage system")],
    switchId: Annotated[str, Field(description="UID of the switch")],
    limit: Annotated[int | None, Field(default=None, description="Number of items to return at a time")] = None,
    offset: Annotated[
        int | None, Field(default=None, description="The offset of the first item in the collection to return")
    ] = None,
    filter: Annotated[
        str | None, Field(default=None, description="oData query to filter switch resource by Key.")
    ] = None,
    sort: Annotated[str | None, Field(default=None, description="oData query to sort switch resource by Key.")] = None,
    select: Annotated[
        str | None,
        Field(default=None, description="Query to select only the required parameters, separated by . if nested"),
    ] = None,
) -> Any:
    path = f"/storage-fleet/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/switches/{path_seg(switchId)}/switch-ports"
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
    name="greenlake_get_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_switches_switch_id_switch_ports_id",
    description="GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/switches/{switchId}/switch-ports/{id}\n\nDeviceType4SwitchPortGetById\n\nGet details of HPE Alletra Storage MP B10000 Switch Port identified by {switchId} and {id}",
    capability=Capability.READ,
)
async def greenlake_get_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_switches_switch_id_switch_ports_id(
    ctx: Context,
    systemId: Annotated[str, Field(description="systemId of the storage system")],
    switchId: Annotated[str, Field(description="UID of the switch")],
    id: Annotated[str, Field(description="UID of the switch fan")],
    select: Annotated[
        str | None,
        Field(default=None, description="Query to select only the required parameters, separated by . if nested"),
    ] = None,
) -> Any:
    path = f"/storage-fleet/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/switches/{path_seg(switchId)}/switch-ports/{path_seg(id)}"
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
    name="greenlake_get_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_switches_switch_id_switch_ps",
    description="GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/switches/{switchId}/switch-ps\n\nDeviceType4SwitchPSList\n\nGet details of HPE Alletra Storage MP B10000 Switch power supplies identified by {switchId}",
    capability=Capability.READ,
)
async def greenlake_get_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_switches_switch_id_switch_ps(
    ctx: Context,
    systemId: Annotated[str, Field(description="systemId of the storage system")],
    switchId: Annotated[str, Field(description="UID of the switch")],
    limit: Annotated[int | None, Field(default=None, description="Number of items to return at a time")] = None,
    offset: Annotated[
        int | None, Field(default=None, description="The offset of the first item in the collection to return")
    ] = None,
    filter: Annotated[
        str | None, Field(default=None, description="oData query to filter switch resource by Key.")
    ] = None,
    sort: Annotated[str | None, Field(default=None, description="oData query to sort switch resource by Key.")] = None,
    select: Annotated[
        str | None,
        Field(default=None, description="Query to select only the required parameters, separated by . if nested"),
    ] = None,
) -> Any:
    path = (
        f"/storage-fleet/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/switches/{path_seg(switchId)}/switch-ps"
    )
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
    name="greenlake_get_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_switches_switch_id_switch_ps_id",
    description="GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/switches/{switchId}/switch-ps/{id}\n\nDeviceType4SwitchPSGetById\n\nGet details of HPE Alletra Storage MP B10000 Switch Power Supplies identified by {switchId} and {id}",
    capability=Capability.READ,
)
async def greenlake_get_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_switches_switch_id_switch_ps_id(
    ctx: Context,
    systemId: Annotated[str, Field(description="systemId of the storage system")],
    switchId: Annotated[str, Field(description="UID of the switch")],
    id: Annotated[str, Field(description="UID of the switch fan")],
    select: Annotated[
        str | None,
        Field(default=None, description="Query to select only the required parameters, separated by . if nested"),
    ] = None,
) -> Any:
    path = f"/storage-fleet/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/switches/{path_seg(switchId)}/switch-ps/{path_seg(id)}"
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
    name="greenlake_get_storage_fleet_v1alpha1_devtype7_storage_systems_system_id_switches",
    description="GET /storage-fleet/v1alpha1/devtype7-storage-systems/{systemId}/switches\n\nDeviceType7GetSwitches\n\nGet all switches of a HPE Alletra Storage MP X10000 system",
    capability=Capability.READ,
)
async def greenlake_get_storage_fleet_v1alpha1_devtype7_storage_systems_system_id_switches(
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
    filter: Annotated[str | None, Field(default=None, description="Lucene query to filter Switches by Key.")] = None,
    sort: Annotated[str | None, Field(default=None, description="Data query to sort Switch resource by Key.")] = None,
) -> Any:
    path = f"/storage-fleet/v1alpha1/devtype7-storage-systems/{path_seg(systemId)}/switches"
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
    name="greenlake_get_storage_fleet_v1alpha1_devtype7_storage_systems_system_id_switches_switch_id",
    description="GET /storage-fleet/v1alpha1/devtype7-storage-systems/{systemId}/switches/{switchId}\n\nDeviceType7GetSwitchById\n\nGet Switch of a HPE Alletra Storage MP X10000 system identified by switchID",
    capability=Capability.READ,
)
async def greenlake_get_storage_fleet_v1alpha1_devtype7_storage_systems_system_id_switches_switch_id(
    ctx: Context,
    systemId: Annotated[str, Field(description="ID of the storage system")],
    switchId: Annotated[str, Field(description="Identifier of Switch. A 42 digit hexadecimal number.")],
    select: Annotated[
        str | None,
        Field(default=None, description="Query to select only the required parameters, separated by . if nested"),
    ] = None,
) -> Any:
    path = f"/storage-fleet/v1alpha1/devtype7-storage-systems/{path_seg(systemId)}/switches/{path_seg(switchId)}"
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
    name="greenlake_post_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_switches_id",
    description="POST /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/switches/{id}\n\nDeviceType4SwitchLocateById\n\nLocate switch of HPE Alletra Storage MP B10000 identified by {id}",
    capability=Capability.WRITE,
)
async def greenlake_post_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_switches_id(
    ctx: Context,
    systemId: Annotated[str, Field(description="systemId of the storage system")],
    id: Annotated[str, Field(description="UID of the switch")],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    path = f"/storage-fleet/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/switches/{path_seg(id)}"
    return await greenlake_request(
        ctx,
        "POST",
        path,
        body=body,
    )


@tool(
    name="greenlake_put_storage_fleet_v1alpha1_devtype7_storage_systems_system_id_switches_switch_id",
    description="PUT /storage-fleet/v1alpha1/devtype7-storage-systems/{systemId}/switches/{switchId}\n\nDeviceType7EditSwitchById\n\nEdit HPE Alletra Storage MP X10000 system Switch identified by {switchId}",
    capability=Capability.WRITE,
)
async def greenlake_put_storage_fleet_v1alpha1_devtype7_storage_systems_system_id_switches_switch_id(
    ctx: Context,
    systemId: Annotated[str, Field(description="ID of the storage system")],
    switchId: Annotated[str, Field(description="Identifier of Switch. A 42 digit hexadecimal number.")],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    path = f"/storage-fleet/v1alpha1/devtype7-storage-systems/{path_seg(systemId)}/switches/{path_seg(switchId)}"
    return await greenlake_request(
        ctx,
        "PUT",
        path,
        body=body,
    )
