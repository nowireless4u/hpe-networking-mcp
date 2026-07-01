"""Generated GreenLake tools — DO NOT EDIT BY HAND.

Generated from the vendored spec ``vendor/greenlake/storage-fleet.json`` by the
maintainer-local GreenLake generator. These modules are committed and are the
runtime source of truth; regeneration is a release-time maintainer workflow
(the generator is intentionally not committed — see ``.gitignore``).

Service: ``storage-fleet``   Tag: ``encryption``   Operations: 7
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
    name="greenlake_post_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_encryption_backup",
    description="POST /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/encryption/backup\n\nDeviceType4backupActionOnEncryption\n\nEncryption Backup Action on HPE Alletra Storage MP B10000 identified by {systemId}",
    capability=Capability.WRITE,
)
async def greenlake_post_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_encryption_backup(
    ctx: Context,
    systemId: Annotated[str, Field(description="systemId of the storage system")],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    path = f"/storage-fleet/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/encryption/backup"
    return await greenlake_request(
        ctx,
        "POST",
        path,
        body=body,
    )


@tool(
    name="greenlake_post_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_encryption_checkekm",
    description="POST /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/encryption/checkekm\n\nDeviceType4checkEKMConfiguration\n\nCheck EKM configuration on HPE Alletra Storage MP B10000 identified by {systemId}",
    capability=Capability.WRITE,
)
async def greenlake_post_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_encryption_checkekm(
    ctx: Context,
    systemId: Annotated[str, Field(description="systemId of the storage system")],
) -> Any:
    path = f"/storage-fleet/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/encryption/checkekm"
    return await greenlake_request(
        ctx,
        "POST",
        path,
    )


@tool(
    name="greenlake_post_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_encryption_enable",
    description="POST /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/encryption/enable\n\nDeviceType4enableActionOnEncryption\n\nEncryption Enable Action on HPE Alletra Storage MP B10000 identified by {systemId}",
    capability=Capability.WRITE,
)
async def greenlake_post_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_encryption_enable(
    ctx: Context,
    systemId: Annotated[str, Field(description="systemId of the storage system")],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    path = f"/storage-fleet/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/encryption/enable"
    return await greenlake_request(
        ctx,
        "POST",
        path,
        body=body,
    )


@tool(
    name="greenlake_post_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_encryption_rekey",
    description="POST /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/encryption/rekey\n\nDeviceType4rekeyActionOnEncryption\n\nEncryption Rekey Action on HPE Alletra Storage MP B10000 identified by {systemId}",
    capability=Capability.WRITE,
)
async def greenlake_post_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_encryption_rekey(
    ctx: Context,
    systemId: Annotated[str, Field(description="systemId of the storage system")],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    path = f"/storage-fleet/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/encryption/rekey"
    return await greenlake_request(
        ctx,
        "POST",
        path,
        body=body,
    )


@tool(
    name="greenlake_post_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_encryption_restore",
    description="POST /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/encryption/restore\n\nDeviceType4restoreActionOnEncryption\n\nEncryption Restore Action on HPE Alletra Storage MP B10000 identified by {systemId}",
    capability=Capability.WRITE,
)
async def greenlake_post_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_encryption_restore(
    ctx: Context,
    systemId: Annotated[str, Field(description="systemId of the storage system")],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    path = f"/storage-fleet/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/encryption/restore"
    return await greenlake_request(
        ctx,
        "POST",
        path,
        body=body,
    )


@tool(
    name="greenlake_post_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_encryption_setekm",
    description="POST /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/encryption/setekm\n\nDeviceType4setEKMConfiguration\n\nSet EKM configuration on HPE Alletra Storage MP B10000 identified by {systemId}",
    capability=Capability.WRITE,
)
async def greenlake_post_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_encryption_setekm(
    ctx: Context,
    systemId: Annotated[str, Field(description="systemId of the storage system")],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    path = f"/storage-fleet/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/encryption/setekm"
    return await greenlake_request(
        ctx,
        "POST",
        path,
        body=body,
    )


@tool(
    name="greenlake_post_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_encryption_setekm_backup",
    description="POST /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/encryption/setekm-backup\n\nDeviceType4setekmbackupActionOnEncryption\n\nSet EKM configuration and Encryption Backup Action on HPE Alletra Storage MP B10000 identified by {systemId}",
    capability=Capability.WRITE,
)
async def greenlake_post_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_encryption_setekm_backup(
    ctx: Context,
    systemId: Annotated[str, Field(description="systemId of the storage system")],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    path = f"/storage-fleet/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/encryption/setekm-backup"
    return await greenlake_request(
        ctx,
        "POST",
        path,
        body=body,
    )
