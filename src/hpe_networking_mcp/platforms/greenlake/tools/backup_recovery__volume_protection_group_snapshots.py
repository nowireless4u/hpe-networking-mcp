"""Generated GreenLake tools — DO NOT EDIT BY HAND.

Generated from the vendored spec ``vendor/greenlake/backup-recovery.json`` by the
maintainer-local GreenLake generator. These modules are committed and are the
runtime source of truth; regeneration is a release-time maintainer workflow
(the generator is intentionally not committed — see ``.gitignore``).

Service: ``backup-recovery``   Tag: ``volume_protection_group_snapshots``   Operations: 5
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
    name="greenlake_delete_backup_recovery_v1beta1_volume_protection_groups_id_snapshots_snapshot_id",
    description="DELETE /backup-recovery/v1beta1/volume-protection-groups/{id}/snapshots/{snapshot-id}\n\nRemoveVpgSnapshot\n\nRemove a Volume Protection Group snapshot.",
    capability=Capability.WRITE_DELETE,
)
async def greenlake_delete_backup_recovery_v1beta1_volume_protection_groups_id_snapshots_snapshot_id(
    ctx: Context,
    id: Annotated[str, Field(description="path parameter 'id'")],
    snapshot_id: Annotated[str, Field(description="path parameter 'snapshot-id'")],
) -> Any:
    path = f"/backup-recovery/v1beta1/volume-protection-groups/{path_seg(id)}/snapshots/{path_seg(snapshot_id)}"
    return await greenlake_request(
        ctx,
        "DELETE",
        path,
    )


@tool(
    name="greenlake_get_backup_recovery_v1beta1_volume_protection_groups_id_snapshots",
    description="GET /backup-recovery/v1beta1/volume-protection-groups/{id}/snapshots\n\nVpgSnapshotList\n\nGet all Volume Protection Group snapshots.",
    capability=Capability.READ,
)
async def greenlake_get_backup_recovery_v1beta1_volume_protection_groups_id_snapshots(
    ctx: Context,
    id: Annotated[str, Field(description="path parameter 'id'")],
    offset: Annotated[
        int | None,
        Field(default=None, description="The number of items to skip before starting to collect the result set"),
    ] = None,
    limit: Annotated[int | None, Field(default=None, description="The numbers of items to return")] = None,
    filter: Annotated[
        str | None,
        Field(
            default=None,
            description="The filter query parameter is used to filter the set of resources returned in the response. The returned set of resources must match the criteria in the filter query parameter.            A comparison compares a property name to a literal. The following comparisons are supported: “eq” : Is a property equal to value. Valid for number, boolean and string properties. “gt” : Is a property greater than a value. Valid for number or string timestamp properties. “lt” : Is a property less than a value. Valid for number or string timestamp properties “in” : Is a value in a property (that is an array of strings)  Examples: GET /backup-recovery/v1beta1/volume-protection-groups/{id}/snapshots?filter=storageSystemInfo/name eq 'myStorageSystem'  Filters are supported on following attributes: * state * status * storageSystemInfo/id * storageSystemInfo/name * pointInTime",
        ),
    ] = None,
    sort: Annotated[
        str | None, Field(default=None, description="Comma separated list of properties defining the sort order")
    ] = None,
    select: Annotated[
        str | None,
        Field(
            default=None,
            description="The select query parameter is used to limit the properties returned with a resource or collection-level GET. Multiple properties can be listed to be returned. The server must only return the set of properties requested by the client. The property “select” is the name of the select query parameter; its value is the list of properties to return separated by commas.",
        ),
    ] = None,
) -> Any:
    path = f"/backup-recovery/v1beta1/volume-protection-groups/{path_seg(id)}/snapshots"
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
    name="greenlake_get_backup_recovery_v1beta1_volume_protection_groups_id_snapshots_snapshot_id",
    description="GET /backup-recovery/v1beta1/volume-protection-groups/{id}/snapshots/{snapshot-id}\n\nVpgSnapshot\n\nGet a Volume Protection Group snapshot identified by {id}.",
    capability=Capability.READ,
)
async def greenlake_get_backup_recovery_v1beta1_volume_protection_groups_id_snapshots_snapshot_id(
    ctx: Context,
    id: Annotated[str, Field(description="path parameter 'id'")],
    snapshot_id: Annotated[str, Field(description="path parameter 'snapshot-id'")],
) -> Any:
    path = f"/backup-recovery/v1beta1/volume-protection-groups/{path_seg(id)}/snapshots/{path_seg(snapshot_id)}"
    return await greenlake_request(
        ctx,
        "GET",
        path,
    )


@tool(
    name="greenlake_patch_backup_recovery_v1beta1_volume_protection_groups_id_snapshots_snapshot_id",
    description="PATCH /backup-recovery/v1beta1/volume-protection-groups/{id}/snapshots/{snapshot-id}\n\nVpgSnapshotUpdate\n\nUpdate a Volume Protection Group snapshot.",
    capability=Capability.WRITE,
)
async def greenlake_patch_backup_recovery_v1beta1_volume_protection_groups_id_snapshots_snapshot_id(
    ctx: Context,
    id: Annotated[str, Field(description="path parameter 'id'")],
    snapshot_id: Annotated[str, Field(description="path parameter 'snapshot-id'")],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    path = f"/backup-recovery/v1beta1/volume-protection-groups/{path_seg(id)}/snapshots/{path_seg(snapshot_id)}"
    return await greenlake_request(
        ctx,
        "PATCH",
        path,
        body=body,
    )


@tool(
    name="greenlake_post_backup_recovery_v1beta1_volume_protection_groups_id_snapshots",
    description="POST /backup-recovery/v1beta1/volume-protection-groups/{id}/snapshots\n\nVpgSnapshotCreate\n\nCreate a snapshot copy of a Volume Protection Group.",
    capability=Capability.WRITE,
)
async def greenlake_post_backup_recovery_v1beta1_volume_protection_groups_id_snapshots(
    ctx: Context,
    id: Annotated[str, Field(description="path parameter 'id'")],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    path = f"/backup-recovery/v1beta1/volume-protection-groups/{path_seg(id)}/snapshots"
    return await greenlake_request(
        ctx,
        "POST",
        path,
        body=body,
    )
