"""Generated GreenLake tools — DO NOT EDIT BY HAND.

Generated from the vendored spec ``vendor/greenlake/block-storage.json`` by the
maintainer-local GreenLake generator. These modules are committed and are the
runtime source of truth; regeneration is a release-time maintainer workflow
(the generator is intentionally not committed — see ``.gitignore``).

Service: ``block-storage``   Tag: ``volume_sets``   Operations: 29
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
    name="greenlake_delete_block_storage_v1alpha1_devtype4_storage_systems_system_id_applicationsets_appset_id_snapsets_snapset_id",
    description="DELETE /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/applicationsets/{appsetId}/snapsets/{snapsetId}\n\nDeviceType4VolumeSetSnapshotGetById\n\nRemove HPE Alletra Storage MP B10000 snapset in system identified by {snapsetId}",
    capability=Capability.WRITE_DELETE,
)
async def greenlake_delete_block_storage_v1alpha1_devtype4_storage_systems_system_id_applicationsets_appset_id_snapsets_snapset_id(
    ctx: Context,
    systemId: Annotated[str, Field(description="systemId of the storage system")],
    appsetId: Annotated[str, Field(description="UID of the applicationset")],
    snapsetId: Annotated[str, Field(description="Identifier of snapset.")],
    force: Annotated[bool | None, Field(default=None, description="Make snapset offline and remove.")] = None,
) -> Any:
    path = f"/block-storage/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/applicationsets/{path_seg(appsetId)}/snapsets/{path_seg(snapsetId)}"
    query_params: dict[str, Any] = {}
    if force is not None:
        query_params["force"] = force
    return await greenlake_request(
        ctx,
        "DELETE",
        path,
        query_params=query_params or None,
    )


@tool(
    name="greenlake_delete_block_storage_v1alpha1_devtype4_storage_systems_system_id_applicationsets_id",
    description="DELETE /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/applicationsets/{id}\n\nDeviceType4VolumeSetsDeleteById\n\nRemove applicationset identified by {id} from HPE Alletra Storage MP B10000 identified by {systemId}",
    capability=Capability.WRITE_DELETE,
)
async def greenlake_delete_block_storage_v1alpha1_devtype4_storage_systems_system_id_applicationsets_id(
    ctx: Context,
    systemId: Annotated[str, Field(description="systemId of the storage system")],
    id: Annotated[str, Field(description="UID of the applicationset")],
) -> Any:
    path = f"/block-storage/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/applicationsets/{path_seg(id)}"
    return await greenlake_request(
        ctx,
        "DELETE",
        path,
    )


@tool(
    name="greenlake_get_block_storage_v1alpha1_devtype4_storage_systems_system_id_applicationsets",
    description="GET /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/applicationsets\n\nDeviceType4VolumeSetsList\n\nGet all applicationset details for HPE Alletra Storage MP B10000",
    capability=Capability.READ,
)
async def greenlake_get_block_storage_v1alpha1_devtype4_storage_systems_system_id_applicationsets(
    ctx: Context,
    systemId: Annotated[str, Field(description="systemId of the storage system")],
    limit: Annotated[int | None, Field(default=None, description="Number of items to return at a time")] = None,
    offset: Annotated[
        int | None, Field(default=None, description="The offset of the first item in the collection to return")
    ] = None,
    filter: Annotated[
        str | None, Field(default=None, description="Lucene query to filter application-sets by Key.")
    ] = None,
    sort: Annotated[
        str | None, Field(default=None, description="Lucene query to sort application-sets by Key.")
    ] = None,
    select: Annotated[
        str | None,
        Field(default=None, description="Query to select only the required parameters, separated by . if nested"),
    ] = None,
) -> Any:
    path = f"/block-storage/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/applicationsets"
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
    name="greenlake_get_block_storage_v1alpha1_devtype4_storage_systems_system_id_applicationsets_appset_id_replication_partners",
    description="GET /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/applicationsets/{appsetId}/replication-partners\n\nDeviceType4GetReplicationPartnersByAppSetId\n\nGet details of HPE Alletra Storage MP B10000 replication partners identified by {systemId} and {appsetId}",
    capability=Capability.READ,
)
async def greenlake_get_block_storage_v1alpha1_devtype4_storage_systems_system_id_applicationsets_appset_id_replication_partners(
    ctx: Context,
    systemId: Annotated[str, Field(description="systemId of the storage system")],
    appsetId: Annotated[str, Field(description="UID of the applicationset")],
) -> Any:
    path = f"/block-storage/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/applicationsets/{path_seg(appsetId)}/replication-partners"
    return await greenlake_request(
        ctx,
        "GET",
        path,
    )


@tool(
    name="greenlake_get_block_storage_v1alpha1_devtype4_storage_systems_system_id_applicationsets_appset_id_replication_partners_replication_partner_id_volumes",
    description="GET /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/applicationsets/{appsetId}/replication-partners/{replicationPartnerId}/volumes\n\nDeviceType4GetReplicationPartnerVolumesByAppSetId\n\nGet volume details of replication partners identified by {appsetId} and {replicationPartnerId} for HPE Alletra Storage MP B10000",
    capability=Capability.READ,
)
async def greenlake_get_block_storage_v1alpha1_devtype4_storage_systems_system_id_applicationsets_appset_id_replication_partners_replication_partner_id_volumes(
    ctx: Context,
    systemId: Annotated[str, Field(description="systemId of the storage system")],
    appsetId: Annotated[str, Field(description="UID of the applicationset")],
    replicationPartnerId: Annotated[str, Field(description="ID of device-type4 replication partner")],
    limit: Annotated[int | None, Field(default=None, description="Number of items to return at a time")] = None,
    offset: Annotated[
        int | None, Field(default=None, description="The offset of the first item in the collection to return")
    ] = None,
) -> Any:
    path = f"/block-storage/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/applicationsets/{path_seg(appsetId)}/replication-partners/{path_seg(replicationPartnerId)}/volumes"
    query_params: dict[str, Any] = {}
    if limit is not None:
        query_params["limit"] = limit
    if offset is not None:
        query_params["offset"] = offset
    return await greenlake_request(
        ctx,
        "GET",
        path,
        query_params=query_params or None,
    )


@tool(
    name="greenlake_get_block_storage_v1alpha1_devtype4_storage_systems_system_id_applicationsets_appset_id_snapsets_snapset_id",
    description="GET /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/applicationsets/{appsetId}/snapsets/{snapsetId}\n\nDeviceType4SnapsetsGetById\n\nGet details of snapsets identified by {snapsetId} for Applicationset identified by {appsetId} for HPE Alletra Storage MP B10000",
    capability=Capability.READ,
)
async def greenlake_get_block_storage_v1alpha1_devtype4_storage_systems_system_id_applicationsets_appset_id_snapsets_snapset_id(
    ctx: Context,
    systemId: Annotated[str, Field(description="systemId of the storage system")],
    appsetId: Annotated[str, Field(description="UID of the applicationset")],
    snapsetId: Annotated[str, Field(description="Identifier of snapset.")],
    select: Annotated[
        str | None,
        Field(default=None, description="Query to select only the required parameters, separated by . if nested"),
    ] = None,
) -> Any:
    path = f"/block-storage/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/applicationsets/{path_seg(appsetId)}/snapsets/{path_seg(snapsetId)}"
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
    name="greenlake_get_block_storage_v1alpha1_devtype4_storage_systems_system_id_applicationsets_appset_id_volumes",
    description="GET /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/applicationsets/{appsetId}/volumes\n\nDeviceType4VolumeSetVolumesList\n\nGet volumes for an applicationset identified by appsetUid",
    capability=Capability.READ,
)
async def greenlake_get_block_storage_v1alpha1_devtype4_storage_systems_system_id_applicationsets_appset_id_volumes(
    ctx: Context,
    appsetId: Annotated[str, Field(description="UID of the applicationset")],
    systemId: Annotated[str, Field(description="systemId of the storage system")],
    limit: Annotated[int | None, Field(default=None, description="Number of items to return at a time")] = None,
    offset: Annotated[
        int | None, Field(default=None, description="The offset of the first item in the collection to return")
    ] = None,
    filter: Annotated[str | None, Field(default=None, description="oData query to filter by Key.")] = None,
    sort: Annotated[str | None, Field(default=None, description="oData query to sort by Key.")] = None,
    select: Annotated[
        str | None,
        Field(default=None, description="Query to select only the required parameters, separated by . if nested"),
    ] = None,
) -> Any:
    path = f"/block-storage/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/applicationsets/{path_seg(appsetId)}/volumes"
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
    name="greenlake_get_block_storage_v1alpha1_devtype4_storage_systems_system_id_applicationsets_id",
    description="GET /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/applicationsets/{id}\n\nDeviceType4VolumeSetsGetById\n\nGet applicationset details for an applicationset identified by appsetUid",
    capability=Capability.READ,
)
async def greenlake_get_block_storage_v1alpha1_devtype4_storage_systems_system_id_applicationsets_id(
    ctx: Context,
    id: Annotated[str, Field(description="UID of the applicationset")],
    systemId: Annotated[str, Field(description="systemId of the storage system")],
    select: Annotated[
        str | None,
        Field(default=None, description="Query to select only the required parameters, separated by . if nested"),
    ] = None,
) -> Any:
    path = f"/block-storage/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/applicationsets/{path_seg(id)}"
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
    name="greenlake_get_block_storage_v1alpha1_devtype4_storage_systems_system_id_applicationsets_id_capacity_statistics",
    description="GET /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/applicationsets/{id}/capacity-statistics\n\nDeviceType4VolumeSetCapacityStatisticsGetById\n\nGet capacity details for an applicationset identified by appsetUid",
    capability=Capability.READ,
)
async def greenlake_get_block_storage_v1alpha1_devtype4_storage_systems_system_id_applicationsets_id_capacity_statistics(
    ctx: Context,
    id: Annotated[str, Field(description="UID of the applicationset")],
    systemId: Annotated[str, Field(description="systemId of the storage system")],
    select: Annotated[
        str | None,
        Field(default=None, description="Query to select only the required parameters, separated by . if nested"),
    ] = None,
) -> Any:
    path = f"/block-storage/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/applicationsets/{path_seg(id)}/capacity-statistics"
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
    name="greenlake_get_block_storage_v1alpha1_devtype4_storage_systems_system_id_applicationsets_id_protection_policies",
    description="GET /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/applicationsets/{id}/protection-policies\n\nDeviceType4GetProtectionPolicies\n\nGet details of protection policies configured on application set identified by {id} created on HPE Alletra Storage MP B10000 identified by {systemId}",
    capability=Capability.READ,
)
async def greenlake_get_block_storage_v1alpha1_devtype4_storage_systems_system_id_applicationsets_id_protection_policies(
    ctx: Context,
    id: Annotated[str, Field(description="ID of the applicationset")],
    systemId: Annotated[str, Field(description="systemId of the storage system")],
    select: Annotated[
        str | None,
        Field(default=None, description="Query to select only the required parameters, separated by . if nested"),
    ] = None,
    filter: Annotated[
        str | None, Field(default=None, description="Lucene query to filter application-sets by Key.")
    ] = None,
) -> Any:
    path = f"/block-storage/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/applicationsets/{path_seg(id)}/protection-policies"
    query_params: dict[str, Any] = {}
    if select is not None:
        query_params["select"] = select
    if filter is not None:
        query_params["filter"] = filter
    return await greenlake_request(
        ctx,
        "GET",
        path,
        query_params=query_params or None,
    )


@tool(
    name="greenlake_get_block_storage_v1alpha1_devtype4_storage_systems_system_id_applicationsets_id_proximity_settings",
    description="GET /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/applicationsets/{id}/proximity-settings\n\nDeviceType4GetProximitySettings\n\nGet hosts and proximity details identified by application set {id} for HPE Alletra Storage MP B10000 identified by {systemId}",
    capability=Capability.READ,
)
async def greenlake_get_block_storage_v1alpha1_devtype4_storage_systems_system_id_applicationsets_id_proximity_settings(
    ctx: Context,
    id: Annotated[str, Field(description="ID of the applicationset")],
    systemId: Annotated[str, Field(description="systemId of the storage system")],
) -> Any:
    path = f"/block-storage/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/applicationsets/{path_seg(id)}/proximity-settings"
    return await greenlake_request(
        ctx,
        "GET",
        path,
    )


@tool(
    name="greenlake_get_block_storage_v1alpha1_devtype4_storage_systems_system_id_applicationsets_id_snapsets",
    description="GET /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/applicationsets/{id}/snapsets\n\nDeviceType4VolumeSetSnapshotsList\n\nGet snapshot details of volume sets identified by {id} for HPE Alletra Storage MP B10000",
    capability=Capability.READ,
)
async def greenlake_get_block_storage_v1alpha1_devtype4_storage_systems_system_id_applicationsets_id_snapsets(
    ctx: Context,
    systemId: Annotated[str, Field(description="systemId of the storage system")],
    id: Annotated[str, Field(description="UID of the applicationset")],
    limit: Annotated[int | None, Field(default=None, description="Number of items to return at a time")] = None,
    offset: Annotated[
        int | None, Field(default=None, description="The offset of the first item in the collection to return")
    ] = None,
    select: Annotated[
        str | None,
        Field(default=None, description="Query to select only the required parameters, separated by . if nested"),
    ] = None,
    filter: Annotated[str | None, Field(default=None, description="oData query to filter by Key.")] = None,
    sort: Annotated[str | None, Field(default=None, description="oData query to sort by Key.")] = None,
) -> Any:
    path = (
        f"/block-storage/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/applicationsets/{path_seg(id)}/snapsets"
    )
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
    name="greenlake_get_block_storage_v1alpha1_devtype4_storage_systems_system_id_applicationsets_id_supported_protection",
    description="GET /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/applicationsets/{id}/supported-protection\n\nDeviceType4getSupportedProtectionTypes\n\nGet supported protection types for application set identified by {id} on HPE Alletra Storage MP B10000 storage system identified by {systemId}",
    capability=Capability.READ,
)
async def greenlake_get_block_storage_v1alpha1_devtype4_storage_systems_system_id_applicationsets_id_supported_protection(
    ctx: Context,
    id: Annotated[str, Field(description="ID of the applicationset")],
    systemId: Annotated[str, Field(description="systemId of the storage system")],
) -> Any:
    path = f"/block-storage/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/applicationsets/{path_seg(id)}/supported-protection"
    return await greenlake_request(
        ctx,
        "GET",
        path,
    )


@tool(
    name="greenlake_get_block_storage_v1alpha1_storage_systems_system_id_volume_sets",
    description="GET /block-storage/v1alpha1/storage-systems/{systemId}/volume-sets\n\nVolumesetListForSystemBySystemId\n\nGet all volume-sets for a systemId",
    capability=Capability.READ,
)
async def greenlake_get_block_storage_v1alpha1_storage_systems_system_id_volume_sets(
    ctx: Context,
    systemId: Annotated[str, Field(description="systemId of the storage system")],
    limit: Annotated[int | None, Field(default=None, description="Number of items to return at a time")] = None,
    offset: Annotated[
        int | None, Field(default=None, description="The offset of the first item in the collection to return")
    ] = None,
    filter: Annotated[str | None, Field(default=None, description="oData query to filter by Key.")] = None,
    sort: Annotated[str | None, Field(default=None, description="oData query to sort by Key.")] = None,
    select: Annotated[
        str | None,
        Field(default=None, description="Query to select only the required parameters, separated by . if nested"),
    ] = None,
) -> Any:
    path = f"/block-storage/v1alpha1/storage-systems/{path_seg(systemId)}/volume-sets"
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
    name="greenlake_get_block_storage_v1alpha1_storage_systems_system_id_volume_sets_id",
    description="GET /block-storage/v1alpha1/storage-systems/{systemId}/volume-sets/{id}\n\nVolumesetSystemGetById\n\nGet volume-set identified by id",
    capability=Capability.READ,
)
async def greenlake_get_block_storage_v1alpha1_storage_systems_system_id_volume_sets_id(
    ctx: Context,
    systemId: Annotated[str, Field(description="systemId of the storage system")],
    id: Annotated[str, Field(description="UID of Volume Set")],
    select: Annotated[
        str | None,
        Field(default=None, description="Query to select only the required parameters, separated by . if nested"),
    ] = None,
) -> Any:
    path = f"/block-storage/v1alpha1/storage-systems/{path_seg(systemId)}/volume-sets/{path_seg(id)}"
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
    name="greenlake_get_block_storage_v1alpha1_volume_sets",
    description="GET /block-storage/v1alpha1/volume-sets\n\nVolumesetList\n\nGet all volume-sets",
    capability=Capability.READ,
)
async def greenlake_get_block_storage_v1alpha1_volume_sets(
    ctx: Context,
    limit: Annotated[int | None, Field(default=None, description="Number of items to return at a time")] = None,
    offset: Annotated[
        int | None, Field(default=None, description="The offset of the first item in the collection to return")
    ] = None,
    filter: Annotated[str | None, Field(default=None, description="oData query to filter by Key.")] = None,
    sort: Annotated[str | None, Field(default=None, description="oData query to sort by Key.")] = None,
    select: Annotated[
        str | None,
        Field(default=None, description="Query to select only the required parameters, separated by . if nested"),
    ] = None,
) -> Any:
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
        "/block-storage/v1alpha1/volume-sets",
        query_params=query_params or None,
    )


@tool(
    name="greenlake_get_block_storage_v1alpha1_volume_sets_id",
    description="GET /block-storage/v1alpha1/volume-sets/{id}\n\nVolumesetGetById\n\nGet volume-set identified by id",
    capability=Capability.READ,
)
async def greenlake_get_block_storage_v1alpha1_volume_sets_id(
    ctx: Context,
    id: Annotated[str, Field(description="UID of Volume Set")],
    select: Annotated[
        str | None,
        Field(default=None, description="Query to select only the required parameters, separated by . if nested"),
    ] = None,
) -> Any:
    path = f"/block-storage/v1alpha1/volume-sets/{path_seg(id)}"
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
    name="greenlake_get_block_storage_v1alpha1_volume_sets_id_volumes",
    description="GET /block-storage/v1alpha1/volume-sets/{id}/volumes\n\nVolumesetGetByvolumesetId\n\nGet volumes identified by volume set id",
    capability=Capability.READ,
)
async def greenlake_get_block_storage_v1alpha1_volume_sets_id_volumes(
    ctx: Context,
    id: Annotated[str, Field(description="UID of Volume Set")],
    select: Annotated[
        str | None,
        Field(default=None, description="Query to select only the required parameters, separated by . if nested"),
    ] = None,
    limit: Annotated[int | None, Field(default=None, description="Number of items to return at a time")] = None,
    offset: Annotated[
        int | None, Field(default=None, description="The offset of the first item in the collection to return")
    ] = None,
    filter: Annotated[str | None, Field(default=None, description="oData query to filter by Key.")] = None,
    sort: Annotated[str | None, Field(default=None, description="oData query to sort by Key.")] = None,
) -> Any:
    path = f"/block-storage/v1alpha1/volume-sets/{path_seg(id)}/volumes"
    query_params: dict[str, Any] = {}
    if select is not None:
        query_params["select"] = select
    if limit is not None:
        query_params["limit"] = limit
    if offset is not None:
        query_params["offset"] = offset
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
    name="greenlake_post_block_storage_v1alpha1_devtype4_storage_systems_system_id_applicationsets",
    description="POST /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/applicationsets\n\nDeviceType4VolumeSetsCreate\n\nCreate Application Set for an HPE Alletra Storage MP B10000 storage system",
    capability=Capability.WRITE,
)
async def greenlake_post_block_storage_v1alpha1_devtype4_storage_systems_system_id_applicationsets(
    ctx: Context,
    systemId: Annotated[str, Field(description="systemId of the storage system")],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    path = f"/block-storage/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/applicationsets"
    return await greenlake_request(
        ctx,
        "POST",
        path,
        body=body,
    )


@tool(
    name="greenlake_post_block_storage_v1alpha1_devtype4_storage_systems_system_id_applicationsets_appset_id_export",
    description="POST /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/applicationsets/{appsetId}/export\n\nDeviceType4VolumeSetExport\n\nExport applicationset identified by {appsetId} from HPE Alletra Storage MP B10000 identified by {systemId}",
    capability=Capability.WRITE,
)
async def greenlake_post_block_storage_v1alpha1_devtype4_storage_systems_system_id_applicationsets_appset_id_export(
    ctx: Context,
    systemId: Annotated[str, Field(description="systemId of the storage system")],
    appsetId: Annotated[str, Field(description="UID of the applicationset")],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    path = f"/block-storage/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/applicationsets/{path_seg(appsetId)}/export"
    return await greenlake_request(
        ctx,
        "POST",
        path,
        body=body,
    )


@tool(
    name="greenlake_post_block_storage_v1alpha1_devtype4_storage_systems_system_id_applicationsets_appset_id_un_export",
    description="POST /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/applicationsets/{appsetId}/un-export\n\nDeviceType4VolumeSetUnexport\n\nUnexport applicationset identified by {appsetId} from HPE Alletra Storage MP B10000 identified by {systemId}",
    capability=Capability.WRITE,
)
async def greenlake_post_block_storage_v1alpha1_devtype4_storage_systems_system_id_applicationsets_appset_id_un_export(
    ctx: Context,
    systemId: Annotated[str, Field(description="systemId of the storage system")],
    appsetId: Annotated[str, Field(description="UID of the applicationset")],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    path = f"/block-storage/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/applicationsets/{path_seg(appsetId)}/un-export"
    return await greenlake_request(
        ctx,
        "POST",
        path,
        body=body,
    )


@tool(
    name="greenlake_post_block_storage_v1alpha1_devtype4_storage_systems_system_id_applicationsets_id_protection_policies",
    description="POST /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/applicationsets/{id}/protection-policies\n\nDeviceType4CreateProtectionPolicy\n\nAdd protection policy on application set identified by {id} for an HPE Alletra Storage MP B10000 storage system identified by {systemId}",
    capability=Capability.WRITE,
)
async def greenlake_post_block_storage_v1alpha1_devtype4_storage_systems_system_id_applicationsets_id_protection_policies(
    ctx: Context,
    id: Annotated[str, Field(description="ID of the applicationset")],
    systemId: Annotated[str, Field(description="systemId of the storage system")],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    path = f"/block-storage/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/applicationsets/{path_seg(id)}/protection-policies"
    return await greenlake_request(
        ctx,
        "POST",
        path,
        body=body,
    )


@tool(
    name="greenlake_post_block_storage_v1alpha1_devtype4_storage_systems_system_id_applicationsets_id_protection_policies_fix",
    description="POST /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/applicationsets/{id}/protection-policies/fix\n\nDeviceType4FixProtectionPolicy\n\nFix protection policy configuration on application set identified by {id} for an HPE Alletra Storage MP B10000 storage system identified by {systemId}",
    capability=Capability.WRITE,
)
async def greenlake_post_block_storage_v1alpha1_devtype4_storage_systems_system_id_applicationsets_id_protection_policies_fix(
    ctx: Context,
    id: Annotated[str, Field(description="ID of the applicationset")],
    systemId: Annotated[str, Field(description="systemId of the storage system")],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    path = f"/block-storage/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/applicationsets/{path_seg(id)}/protection-policies/fix"
    return await greenlake_request(
        ctx,
        "POST",
        path,
        body=body,
    )


@tool(
    name="greenlake_post_block_storage_v1alpha1_devtype4_storage_systems_system_id_applicationsets_id_protection_policies_remove",
    description="POST /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/applicationsets/{id}/protection-policies/remove\n\nDeviceType4removeProtectionPolicies\n\nRemove protection policy on application set identified by {id} for an HPE Alletra Storage MP B10000 storage system identified by {systemId}",
    capability=Capability.WRITE,
)
async def greenlake_post_block_storage_v1alpha1_devtype4_storage_systems_system_id_applicationsets_id_protection_policies_remove(
    ctx: Context,
    id: Annotated[str, Field(description="ID of the applicationset")],
    systemId: Annotated[str, Field(description="systemId of the storage system")],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    path = f"/block-storage/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/applicationsets/{path_seg(id)}/protection-policies/remove"
    return await greenlake_request(
        ctx,
        "POST",
        path,
        body=body,
    )


@tool(
    name="greenlake_post_block_storage_v1alpha1_devtype4_storage_systems_system_id_applicationsets_id_remote_protection_actions",
    description="POST /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/applicationsets/{id}/remote-protection/actions\n\nDeviceType4actionOnVolumeSets\n\nActions on volume set identified by {id} and {systemId} from HPE Alletra Storage MP B10000",
    capability=Capability.WRITE,
)
async def greenlake_post_block_storage_v1alpha1_devtype4_storage_systems_system_id_applicationsets_id_remote_protection_actions(
    ctx: Context,
    systemId: Annotated[str, Field(description="systemId of the storage system")],
    id: Annotated[str, Field(description="ID of the applicationset")],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    path = f"/block-storage/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/applicationsets/{path_seg(id)}/remote-protection/actions"
    return await greenlake_request(
        ctx,
        "POST",
        path,
        body=body,
    )


@tool(
    name="greenlake_post_block_storage_v1alpha1_devtype4_storage_systems_system_id_applicationsets_id_snapsets",
    description="POST /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/applicationsets/{id}/snapsets\n\nDeviceType4VolumeSetsSnapshotCreate\n\nCreate snapshot for application set identified by {id}",
    capability=Capability.WRITE,
)
async def greenlake_post_block_storage_v1alpha1_devtype4_storage_systems_system_id_applicationsets_id_snapsets(
    ctx: Context,
    systemId: Annotated[str, Field(description="systemId of the storage system")],
    id: Annotated[str, Field(description="UID of the applicationset")],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    path = (
        f"/block-storage/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/applicationsets/{path_seg(id)}/snapsets"
    )
    return await greenlake_request(
        ctx,
        "POST",
        path,
        body=body,
    )


@tool(
    name="greenlake_put_block_storage_v1alpha1_devtype4_storage_systems_system_id_applicationsets_id",
    description="PUT /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/applicationsets/{id}\n\nDeviceType4VolumeSetsEditById\n\nEdit applicationset identified by {id} from HPE Alletra Storage MP B10000 identified by {systemId}",
    capability=Capability.WRITE,
)
async def greenlake_put_block_storage_v1alpha1_devtype4_storage_systems_system_id_applicationsets_id(
    ctx: Context,
    systemId: Annotated[str, Field(description="systemId of the storage system")],
    id: Annotated[str, Field(description="UID of the applicationset")],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    path = f"/block-storage/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/applicationsets/{path_seg(id)}"
    return await greenlake_request(
        ctx,
        "PUT",
        path,
        body=body,
    )


@tool(
    name="greenlake_put_block_storage_v1alpha1_devtype4_storage_systems_system_id_applicationsets_id_protection_policies",
    description="PUT /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/applicationsets/{id}/protection-policies\n\nDeviceType4EditProtectionPolicies\n\nEdit protection policy on application set identified by {id} for an HPE Alletra Storage MP B10000 storage system identified by {systemId}",
    capability=Capability.WRITE,
)
async def greenlake_put_block_storage_v1alpha1_devtype4_storage_systems_system_id_applicationsets_id_protection_policies(
    ctx: Context,
    id: Annotated[str, Field(description="ID of the applicationset")],
    systemId: Annotated[str, Field(description="systemId of the storage system")],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    path = f"/block-storage/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/applicationsets/{path_seg(id)}/protection-policies"
    return await greenlake_request(
        ctx,
        "PUT",
        path,
        body=body,
    )


@tool(
    name="greenlake_put_block_storage_v1alpha1_devtype4_storage_systems_system_id_applicationsets_id_proximity_settings",
    description="PUT /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/applicationsets/{id}/proximity-settings\n\nDeviceType4EditProximitySettings\n\nChange proximity settings of hosts where volume sets are exported identified by {id} and {systemId} from HPE Alletra Storage MP B10000",
    capability=Capability.WRITE,
)
async def greenlake_put_block_storage_v1alpha1_devtype4_storage_systems_system_id_applicationsets_id_proximity_settings(
    ctx: Context,
    systemId: Annotated[str, Field(description="systemId of the storage system")],
    id: Annotated[str, Field(description="UID of the applicationset")],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    path = f"/block-storage/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/applicationsets/{path_seg(id)}/proximity-settings"
    return await greenlake_request(
        ctx,
        "PUT",
        path,
        body=body,
    )
