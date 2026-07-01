"""Generated GreenLake tools — DO NOT EDIT BY HAND.

Generated from the vendored spec ``vendor/greenlake/backup-recovery.json`` by the
maintainer-local GreenLake generator. These modules are committed and are the
runtime source of truth; regeneration is a release-time maintainer workflow
(the generator is intentionally not committed — see ``.gitignore``).

Service: ``backup-recovery``   Tag: ``virtual_machines``   Operations: 3
"""

# ruff: noqa: E501
from __future__ import annotations

from typing import Annotated, Any

from fastmcp import Context
from pydantic import Field

from hpe_networking_mcp.platforms._common.annotations import Capability
from hpe_networking_mcp.platforms._common.url import path_seg
from hpe_networking_mcp.platforms.greenlake._registry import tool
from hpe_networking_mcp.platforms.greenlake.client import greenlake_request


@tool(
    name="greenlake_post_backup_recovery_v1beta1_virtual_machines_id_restore",
    description="POST /backup-recovery/v1beta1/virtual-machines/{id}/restore\n\nVirtualMachineRestore\n\nRestore a virtual machine from snapshot or backup.",
    capability=Capability.WRITE,
)
async def greenlake_post_backup_recovery_v1beta1_virtual_machines_id_restore(
    ctx: Context,
    id: Annotated[str, Field(description="path parameter 'id'")],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    path = f"/backup-recovery/v1beta1/virtual-machines/{path_seg(id)}/restore"
    return await greenlake_request(
        ctx,
        "POST",
        path,
        body=body,
    )


@tool(
    name="greenlake_post_backup_recovery_v1beta1_virtual_machines_id_restore_disks",
    description="POST /backup-recovery/v1beta1/virtual-machines/{id}/restore-disks\n\nVirtualMachineDisksRestore\n\nRestore one or more disks of a virtual machine from snapshot or backup.",
    capability=Capability.WRITE,
)
async def greenlake_post_backup_recovery_v1beta1_virtual_machines_id_restore_disks(
    ctx: Context,
    id: Annotated[str, Field(description="path parameter 'id'")],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    path = f"/backup-recovery/v1beta1/virtual-machines/{path_seg(id)}/restore-disks"
    return await greenlake_request(
        ctx,
        "POST",
        path,
        body=body,
    )


@tool(
    name="greenlake_post_backup_recovery_v1beta1_virtual_machines_id_restore_files",
    description="POST /backup-recovery/v1beta1/virtual-machines/{id}/restore-files\n\nVirtualMachineFileRestore\n\nRestore files and folders of a virtual machine.",
    capability=Capability.WRITE,
)
async def greenlake_post_backup_recovery_v1beta1_virtual_machines_id_restore_files(
    ctx: Context,
    id: Annotated[str, Field(description="path parameter 'id'")],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    path = f"/backup-recovery/v1beta1/virtual-machines/{path_seg(id)}/restore-files"
    return await greenlake_request(
        ctx,
        "POST",
        path,
        body=body,
    )
