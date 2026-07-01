"""Generated GreenLake tools — DO NOT EDIT BY HAND.

Generated from the vendored spec ``vendor/greenlake/backup-recovery.json`` by the
maintainer-local GreenLake generator. These modules are committed and are the
runtime source of truth; regeneration is a release-time maintainer workflow
(the generator is intentionally not committed — see ``.gitignore``).

Service: ``backup-recovery``   Tag: ``virtual_machine_protection_groups``   Operations: 16
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
    name="greenlake_delete_backup_recovery_v1beta1_virtual_machine_protection_groups_id",
    description="DELETE /backup-recovery/v1beta1/virtual-machine-protection-groups/{id}\n\nVmProtectionGroupDelete\n\nRemove a virtual machine Protection Group.",
    capability=Capability.WRITE_DELETE,
)
async def greenlake_delete_backup_recovery_v1beta1_virtual_machine_protection_groups_id(
    ctx: Context,
    id: Annotated[str, Field(description="path parameter 'id'")],
    cascadedelete: Annotated[
        bool | None,
        Field(
            default=None,
            description="Cascade delete option for Virtual Machine Protection Group of type Storage Replication.",
        ),
    ] = None,
    force: Annotated[
        bool | None,
        Field(
            default=None,
            description="Forceful delete option for Virtual Machine Protection Group of type Storage Replication.",
        ),
    ] = None,
) -> Any:
    path = f"/backup-recovery/v1beta1/virtual-machine-protection-groups/{path_seg(id)}"
    query_params: dict[str, Any] = {}
    if cascadedelete is not None:
        query_params["cascadedelete"] = cascadedelete
    if force is not None:
        query_params["force"] = force
    return await greenlake_request(
        ctx,
        "DELETE",
        path,
        query_params=query_params or None,
    )


@tool(
    name="greenlake_delete_backup_recovery_v1beta1_virtual_machine_protection_groups_vmpg_id_backups_backup_id",
    description="DELETE /backup-recovery/v1beta1/virtual-machine-protection-groups/{vmpg-id}/backups/{backup-id}\n\nDeleteVmpgBackup\n\nDelete a virtual machine protection group backup.",
    capability=Capability.WRITE_DELETE,
)
async def greenlake_delete_backup_recovery_v1beta1_virtual_machine_protection_groups_vmpg_id_backups_backup_id(
    ctx: Context,
    vmpg_id: Annotated[str, Field(description="path parameter 'vmpg-id'")],
    backup_id: Annotated[str, Field(description="path parameter 'backup-id'")],
) -> Any:
    path = (
        f"/backup-recovery/v1beta1/virtual-machine-protection-groups/{path_seg(vmpg_id)}/backups/{path_seg(backup_id)}"
    )
    return await greenlake_request(
        ctx,
        "DELETE",
        path,
    )


@tool(
    name="greenlake_delete_backup_recovery_v1beta1_virtual_machine_protection_groups_vmpg_id_snapshots_snapshot_id",
    description="DELETE /backup-recovery/v1beta1/virtual-machine-protection-groups/{vmpg-id}/snapshots/{snapshot-id}\n\nDeleteVmpgSnapshot\n\nDelete a virtual machine protection group snapshot.",
    capability=Capability.WRITE_DELETE,
)
async def greenlake_delete_backup_recovery_v1beta1_virtual_machine_protection_groups_vmpg_id_snapshots_snapshot_id(
    ctx: Context,
    vmpg_id: Annotated[str, Field(description="path parameter 'vmpg-id'")],
    snapshot_id: Annotated[str, Field(description="path parameter 'snapshot-id'")],
) -> Any:
    path = f"/backup-recovery/v1beta1/virtual-machine-protection-groups/{path_seg(vmpg_id)}/snapshots/{path_seg(snapshot_id)}"
    return await greenlake_request(
        ctx,
        "DELETE",
        path,
    )


@tool(
    name="greenlake_get_backup_recovery_v1beta1_virtual_machine_protection_groups",
    description="GET /backup-recovery/v1beta1/virtual-machine-protection-groups\n\nVmProtectionGroupList\n\nGet all  virtual machine Protection Groups.",
    capability=Capability.READ,
)
async def greenlake_get_backup_recovery_v1beta1_virtual_machine_protection_groups(
    ctx: Context,
    offset: Annotated[
        int | None,
        Field(
            default=None,
            description='The number of items to omit from the beginning of the result set. The offset and limit query parameters are used in conjunction with pagination. For example "offset=30&limit=10" indicates the fourth page of 10 items.',
        ),
    ] = None,
    limit: Annotated[
        int | None,
        Field(
            default=None,
            description='The maximum number of items to include in the response. The offset and limit query parameters are used in conjunction for pagination, for example "offset=30&limit=10" indicates the fourth page of 10 items.',
        ),
    ] = None,
    filter: Annotated[
        str | None,
        Field(
            default=None,
            description="An expression by which to filter the results.  A comparison compares a property name to a literal. The following comparisons are supported: * “eq” : Is a property equal to value. Valid for number, boolean and string properties. * “gt” : Is a property greater than a value. Valid for number or string timestamp properties. * “lt” : Is a property less than a value. Valid for number or string timestamp properties. * “in” : Is a value in a property (that is an array of strings). example: vmProtectionGroupType eq 'NATIVE'  Filters are supported on the following attributes: * hypervisorManagerInfo/name * hypervisorManagerInfo/id * vmProtectionGroupType * dataOrchestratorInfo/id * createdAt * name",
        ),
    ] = None,
    sort: Annotated[
        str | None,
        Field(
            default=None,
            description="Comma separated list of properties defining the sort order. Each item in the “sort” query parameter is a property name optionally followed by a direction indicator. The direction indicator may only be either “asc” (ascending) or “desc” (descending). If no direction indicator is specified, the default order is ascending.",
        ),
    ] = None,
    select: Annotated[
        str | None,
        Field(
            default=None,
            description="The select query parameter is used to limit the properties returned with a resource or collection-level GET. Multiple properties can be listed to be returned. The server must only return the set of properties requested by the client formatted as an exclusive comma separated list of properties. If not specified, all properties are returned.",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if offset is not None:
        query_params["offset"] = offset
    if limit is not None:
        query_params["limit"] = limit
    if filter is not None:
        query_params["filter"] = filter
    if sort is not None:
        query_params["sort"] = sort
    if select is not None:
        query_params["select"] = select
    return await greenlake_request(
        ctx,
        "GET",
        "/backup-recovery/v1beta1/virtual-machine-protection-groups",
        query_params=query_params or None,
    )


@tool(
    name="greenlake_get_backup_recovery_v1beta1_virtual_machine_protection_groups_id",
    description="GET /backup-recovery/v1beta1/virtual-machine-protection-groups/{id}\n\nVmProtectionGroup\n\nGet a virtual machine Protection Group resource.",
    capability=Capability.READ,
)
async def greenlake_get_backup_recovery_v1beta1_virtual_machine_protection_groups_id(
    ctx: Context,
    id: Annotated[str, Field(description="path parameter 'id'")],
) -> Any:
    path = f"/backup-recovery/v1beta1/virtual-machine-protection-groups/{path_seg(id)}"
    return await greenlake_request(
        ctx,
        "GET",
        path,
    )


@tool(
    name="greenlake_get_backup_recovery_v1beta1_virtual_machine_protection_groups_vmpg_id_backups",
    description="GET /backup-recovery/v1beta1/virtual-machine-protection-groups/{vmpg-id}/backups\n\nVmpgBackupList\n\nGet information about all virtual machine protection groups backups.",
    capability=Capability.READ,
)
async def greenlake_get_backup_recovery_v1beta1_virtual_machine_protection_groups_vmpg_id_backups(
    ctx: Context,
    vmpg_id: Annotated[str, Field(description="path parameter 'vmpg-id'")],
    offset: Annotated[
        int | None,
        Field(default=None, description="The number of items to skip before starting to collect the result set."),
    ] = None,
    limit: Annotated[int | None, Field(default=None, description="query parameter 'limit'")] = None,
    filter: Annotated[
        str | None,
        Field(
            default=None,
            description="The filter query parameter is used to filter the set of resources returned in the response. The returned set of resources must match the criteria in the filter query parameter.  A comparision compares a property name to a literal. The comparisons supported are the following: * “eq” : Is a property equal to value. Valid for number, boolean and string properties. * “gt” : Is a property greater than a value. Valid for number or string timestamp properties. * “lt” : Is a property less than a value. Valid for number or string timestamp properties. * “in” : Is a value in a property (that is an array of strings).  Filters are supported on following attributes: * backupType * state * status * createdByInfo/id * createdByInfo/name * sourceCopyInfo/id * pointInTime * verified * storageSystemInfo/id * storageSystemInfo/name * protectionStoreInfo/id * protectionStoreInfo/name * dataOrchestratorInfo/id * expiresAt * name Examples: * GET /backup-recovery/v1beta1/virtual-machine-protection-groups/{vmpg-id}/backups?filter=backupType eq 'CLOUD_BACKUP'",
        ),
    ] = None,
    sort: Annotated[
        str | None,
        Field(
            default=None,
            description='A comma separated list of properties to sort by, followed by a direction indicator ("asc" or "desc"). If no direction indicator is specified, the default order is ascending.',
        ),
    ] = None,
    select: Annotated[
        str | None,
        Field(
            default=None,
            description="The select query parameter is used to limit the properties returned with a resource or collection-level GET. Multiple properties can be listed to be returned. The server must only return the set of properties requested by the client. The property “select” is the name of the select query parameter; its value is the list of properties to return separated by commas.",
        ),
    ] = None,
) -> Any:
    path = f"/backup-recovery/v1beta1/virtual-machine-protection-groups/{path_seg(vmpg_id)}/backups"
    query_params: dict[str, Any] = {}
    if offset is not None:
        query_params["offset"] = offset
    if limit is not None:
        query_params["limit"] = limit
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
    name="greenlake_get_backup_recovery_v1beta1_virtual_machine_protection_groups_vmpg_id_backups_backup_id",
    description="GET /backup-recovery/v1beta1/virtual-machine-protection-groups/{vmpg-id}/backups/{backup-id}\n\nVmpgBackup\n\nGet details of a virtual machine protection group backup.",
    capability=Capability.READ,
)
async def greenlake_get_backup_recovery_v1beta1_virtual_machine_protection_groups_vmpg_id_backups_backup_id(
    ctx: Context,
    vmpg_id: Annotated[str, Field(description="path parameter 'vmpg-id'")],
    backup_id: Annotated[str, Field(description="path parameter 'backup-id'")],
) -> Any:
    path = (
        f"/backup-recovery/v1beta1/virtual-machine-protection-groups/{path_seg(vmpg_id)}/backups/{path_seg(backup_id)}"
    )
    return await greenlake_request(
        ctx,
        "GET",
        path,
    )


@tool(
    name="greenlake_get_backup_recovery_v1beta1_virtual_machine_protection_groups_vmpg_id_snapshots",
    description="GET /backup-recovery/v1beta1/virtual-machine-protection-groups/{vmpg-id}/snapshots\n\nVmpgSnapshotList\n\nGet information about all virtual machine protection groups snapshots.",
    capability=Capability.READ,
)
async def greenlake_get_backup_recovery_v1beta1_virtual_machine_protection_groups_vmpg_id_snapshots(
    ctx: Context,
    vmpg_id: Annotated[str, Field(description="path parameter 'vmpg-id'")],
    offset: Annotated[
        int | None,
        Field(default=None, description="The number of items to skip before starting to collect the result set"),
    ] = None,
    limit: Annotated[int | None, Field(default=None, description="The numbers of items to return")] = None,
    filter: Annotated[
        str | None,
        Field(
            default=None,
            description="The filter query parameter is used to filter the set of resources returned in the response. The returned set of resources must match the criteria in the filter query parameter.  A comparision compares a property name to a literal. The comparisons supported are the following: * “eq” : Is a property equal to value. Valid for number, boolean and string properties. * “gt” : Is a property greater than a value. Valid for number or string timestamp properties. * “lt” : Is a property less than a value. Valid for number or string timestamp properties * “in” : Is a value in a property (that is an array of strings)  Filters are supported on following attributes: * snapshotType * state * status * createdByInfo/id * createdByInfo/name * storageSystemsInfo/id * storageSystemsInfo/storageSystemType * storageSystemsInfo/name * consistency * pointInTime * dataOrchestratorInfo/id * expiresAt * name Examples: * GET /backup-recovery/v1beta1/virtual-machine-protection-groups/{vmpg-id}/snapshots?filter=consistency eq 'APPLICATION'",
        ),
    ] = None,
    sort: Annotated[
        str | None,
        Field(
            default=None,
            description='A comma separated list of properties to sort by, followed by a direction indicator ("asc" or "desc"). If no direction indicator is specified, the default order is ascending.',
        ),
    ] = None,
    select: Annotated[
        str | None,
        Field(
            default=None,
            description="The select query parameter is used to limit the properties returned with a resource or collection-level GET. Multiple properties can be listed to be returned. The server must only return the set of properties requested by the client. The property “select” is the name of the select query parameter; its value is the list of properties to return separated by commas.",
        ),
    ] = None,
) -> Any:
    path = f"/backup-recovery/v1beta1/virtual-machine-protection-groups/{path_seg(vmpg_id)}/snapshots"
    query_params: dict[str, Any] = {}
    if offset is not None:
        query_params["offset"] = offset
    if limit is not None:
        query_params["limit"] = limit
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
    name="greenlake_get_backup_recovery_v1beta1_virtual_machine_protection_groups_vmpg_id_snapshots_snapshot_id",
    description="GET /backup-recovery/v1beta1/virtual-machine-protection-groups/{vmpg-id}/snapshots/{snapshot-id}\n\nVmpgSnapshot\n\nGet details of a virtual machine protection group snapshot.",
    capability=Capability.READ,
)
async def greenlake_get_backup_recovery_v1beta1_virtual_machine_protection_groups_vmpg_id_snapshots_snapshot_id(
    ctx: Context,
    vmpg_id: Annotated[str, Field(description="path parameter 'vmpg-id'")],
    snapshot_id: Annotated[str, Field(description="path parameter 'snapshot-id'")],
) -> Any:
    path = f"/backup-recovery/v1beta1/virtual-machine-protection-groups/{path_seg(vmpg_id)}/snapshots/{path_seg(snapshot_id)}"
    return await greenlake_request(
        ctx,
        "GET",
        path,
    )


@tool(
    name="greenlake_patch_backup_recovery_v1beta1_virtual_machine_protection_groups_id",
    description="PATCH /backup-recovery/v1beta1/virtual-machine-protection-groups/{id}\n\nVmProtectionGroupUpdate\n\nUpdate a virtual machine Protection Group.",
    capability=Capability.WRITE,
)
async def greenlake_patch_backup_recovery_v1beta1_virtual_machine_protection_groups_id(
    ctx: Context,
    id: Annotated[str, Field(description="path parameter 'id'")],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    path = f"/backup-recovery/v1beta1/virtual-machine-protection-groups/{path_seg(id)}"
    return await greenlake_request(
        ctx,
        "PATCH",
        path,
        body=body,
    )


@tool(
    name="greenlake_patch_backup_recovery_v1beta1_virtual_machine_protection_groups_vmpg_id_backups_backup_id",
    description="PATCH /backup-recovery/v1beta1/virtual-machine-protection-groups/{vmpg-id}/backups/{backup-id}\n\nVmpgBackupUpdate\n\nUpdate a virtual machine protection groups backup.",
    capability=Capability.WRITE,
)
async def greenlake_patch_backup_recovery_v1beta1_virtual_machine_protection_groups_vmpg_id_backups_backup_id(
    ctx: Context,
    vmpg_id: Annotated[str, Field(description="path parameter 'vmpg-id'")],
    backup_id: Annotated[str, Field(description="path parameter 'backup-id'")],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    path = (
        f"/backup-recovery/v1beta1/virtual-machine-protection-groups/{path_seg(vmpg_id)}/backups/{path_seg(backup_id)}"
    )
    return await greenlake_request(
        ctx,
        "PATCH",
        path,
        body=body,
    )


@tool(
    name="greenlake_patch_backup_recovery_v1beta1_virtual_machine_protection_groups_vmpg_id_snapshots_snapshot_id",
    description="PATCH /backup-recovery/v1beta1/virtual-machine-protection-groups/{vmpg-id}/snapshots/{snapshot-id}\n\nVmpgSnapshotUpdate\n\nUpdate a virtual machine protection group snapshot.",
    capability=Capability.WRITE,
)
async def greenlake_patch_backup_recovery_v1beta1_virtual_machine_protection_groups_vmpg_id_snapshots_snapshot_id(
    ctx: Context,
    vmpg_id: Annotated[str, Field(description="path parameter 'vmpg-id'")],
    snapshot_id: Annotated[str, Field(description="path parameter 'snapshot-id'")],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    path = f"/backup-recovery/v1beta1/virtual-machine-protection-groups/{path_seg(vmpg_id)}/snapshots/{path_seg(snapshot_id)}"
    return await greenlake_request(
        ctx,
        "PATCH",
        path,
        body=body,
    )


@tool(
    name="greenlake_post_backup_recovery_v1beta1_virtual_machine_protection_groups",
    description="POST /backup-recovery/v1beta1/virtual-machine-protection-groups\n\nVmProtectionGroupCreate\n\nCreate a new virtual machine Protection Group.",
    capability=Capability.WRITE,
)
async def greenlake_post_backup_recovery_v1beta1_virtual_machine_protection_groups(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await greenlake_request(
        ctx,
        "POST",
        "/backup-recovery/v1beta1/virtual-machine-protection-groups",
        body=body,
    )


@tool(
    name="greenlake_post_backup_recovery_v1beta1_virtual_machine_protection_groups_id_refresh",
    description="POST /backup-recovery/v1beta1/virtual-machine-protection-groups/{id}/refresh\n\nVmProtectionGroupRefresh\n\nRefresh a virtual machine Protection Group.",
    capability=Capability.WRITE,
)
async def greenlake_post_backup_recovery_v1beta1_virtual_machine_protection_groups_id_refresh(
    ctx: Context,
    id: Annotated[str, Field(description="path parameter 'id'")],
) -> Any:
    path = f"/backup-recovery/v1beta1/virtual-machine-protection-groups/{path_seg(id)}/refresh"
    return await greenlake_request(
        ctx,
        "POST",
        path,
    )


@tool(
    name="greenlake_post_backup_recovery_v1beta1_virtual_machine_protection_groups_id_restore",
    description="POST /backup-recovery/v1beta1/virtual-machine-protection-groups/{id}/restore\n\nVmpgRestore\n\nRestore a virtual machine Protection Group from recovery points.",
    capability=Capability.WRITE,
)
async def greenlake_post_backup_recovery_v1beta1_virtual_machine_protection_groups_id_restore(
    ctx: Context,
    id: Annotated[str, Field(description="path parameter 'id'")],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    path = f"/backup-recovery/v1beta1/virtual-machine-protection-groups/{path_seg(id)}/restore"
    return await greenlake_request(
        ctx,
        "POST",
        path,
        body=body,
    )


@tool(
    name="greenlake_post_backup_recovery_v1beta1_virtual_machine_protection_groups_id_restore_pre_check",
    description="POST /backup-recovery/v1beta1/virtual-machine-protection-groups/{id}/restore-pre-check\n\nVmpgRestorePreCheckList\n\nRestore pre-check of a virtual machine Protection Group from recovery points.",
    capability=Capability.WRITE,
)
async def greenlake_post_backup_recovery_v1beta1_virtual_machine_protection_groups_id_restore_pre_check(
    ctx: Context,
    id: Annotated[str, Field(description="path parameter 'id'")],
) -> Any:
    path = f"/backup-recovery/v1beta1/virtual-machine-protection-groups/{path_seg(id)}/restore-pre-check"
    return await greenlake_request(
        ctx,
        "POST",
        path,
    )
