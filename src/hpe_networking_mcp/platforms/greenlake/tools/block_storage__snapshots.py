"""Generated GreenLake tools — DO NOT EDIT BY HAND.

Generated from the vendored spec ``vendor/greenlake/block-storage.json`` by the
maintainer-local GreenLake generator. These modules are committed and are the
runtime source of truth; regeneration is a release-time maintainer workflow
(the generator is intentionally not committed — see ``.gitignore``).

Service: ``block-storage``   Tag: ``snapshots``   Operations: 2
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
    name="greenlake_get_block_storage_v1alpha1_devtype4_storage_systems_system_id_snapshots_child_snapshot_id_restore_options",
    description="GET /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/snapshots/{childSnapshotId}/restore-options\n\nDeviceType4GetSnapshotRestoreOptions\n\nGet the details of all read-write parent snapshots and base volume to which the child snapshot identified by {childSnapshotId} can be restored on HPE Alletra Storage MP B10000 system identified by {systemId}.",
    capability=Capability.READ,
)
async def greenlake_get_block_storage_v1alpha1_devtype4_storage_systems_system_id_snapshots_child_snapshot_id_restore_options(
    ctx: Context,
    systemId: Annotated[str, Field(description="systemId of the storage system")],
    childSnapshotId: Annotated[str, Field(description="UID of the child snapshot to be restored")],
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
    path = f"/block-storage/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/snapshots/{path_seg(childSnapshotId)}/restore-options"
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
    name="greenlake_post_block_storage_v1alpha1_devtype4_storage_systems_system_id_snapshots_parent_snapshot_id_snapshots_child_snapshot_id_restore",
    description="POST /block-storage/v1alpha1/devtype4-storage-systems/{systemId}/snapshots/{parentSnapshotId}/snapshots/{childSnapshotId}/restore\n\nDeviceType4RestoreSnapshotOfSnapshot\n\nRestore a child snapshot identified by {childSnapshotId} to a read-write parent snapshot identified by {parentSnapshotId} on HPE Alletra Storage MP B10000 storage system identified by {systemId}",
    capability=Capability.WRITE,
)
async def greenlake_post_block_storage_v1alpha1_devtype4_storage_systems_system_id_snapshots_parent_snapshot_id_snapshots_child_snapshot_id_restore(
    ctx: Context,
    systemId: Annotated[str, Field(description="systemId of the storage system")],
    parentSnapshotId: Annotated[str, Field(description="UID of the read-write parent snapshot")],
    childSnapshotId: Annotated[str, Field(description="UID of the child snapshot to be restored")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request body")] = None,
) -> Any:
    path = f"/block-storage/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/snapshots/{path_seg(parentSnapshotId)}/snapshots/{path_seg(childSnapshotId)}/restore"
    return await greenlake_request(
        ctx,
        "POST",
        path,
        body=body,
    )
