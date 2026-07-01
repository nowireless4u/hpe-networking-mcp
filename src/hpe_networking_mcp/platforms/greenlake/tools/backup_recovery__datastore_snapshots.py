"""Generated GreenLake tools — DO NOT EDIT BY HAND.

Generated from the vendored spec ``vendor/greenlake/backup-recovery.json`` by the
maintainer-local GreenLake generator. These modules are committed and are the
runtime source of truth; regeneration is a release-time maintainer workflow
(the generator is intentionally not committed — see ``.gitignore``).

Service: ``backup-recovery``   Tag: ``datastore_snapshots``   Operations: 4
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
    name="greenlake_delete_backup_recovery_v1beta1_datastores_id_snapshots_snapshot_id",
    description="DELETE /backup-recovery/v1beta1/datastores/{id}/snapshots/{snapshot-id}\n\nDeleteDatastoreSnapshot\n\nDelete a datastore snapshot.",
    capability=Capability.WRITE_DELETE,
)
async def greenlake_delete_backup_recovery_v1beta1_datastores_id_snapshots_snapshot_id(
    ctx: Context,
    id: Annotated[str, Field(description="path parameter 'id'")],
    snapshot_id: Annotated[str, Field(description="path parameter 'snapshot-id'")],
) -> Any:
    path = f"/backup-recovery/v1beta1/datastores/{path_seg(id)}/snapshots/{path_seg(snapshot_id)}"
    return await greenlake_request(
        ctx,
        "DELETE",
        path,
    )


@tool(
    name="greenlake_get_backup_recovery_v1beta1_datastores_id_snapshots",
    description="GET /backup-recovery/v1beta1/datastores/{id}/snapshots\n\nDatastoreSnapshotList\n\nGet information about all datastore snapshots.",
    capability=Capability.READ,
)
async def greenlake_get_backup_recovery_v1beta1_datastores_id_snapshots(
    ctx: Context,
    id: Annotated[str, Field(description="path parameter 'id'")],
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
            description='The maximum number of items to include in the response. The offset and limit query parameters are used in conjunction with pagination. For example "offset=30&limit=10" indicates the fourth page of 10 items.',
        ),
    ] = None,
    filter: Annotated[
        str | None,
        Field(
            default=None,
            description="An expression that enables you to filter the results.  A comparison compares a property name to a literal. The following comparisons are supported: * “eq” : Is a property equal to value. Valid for number, boolean and string properties. * “gt” : Is a property greater than a value. Valid for number or string timestamp properties. * “lt” : Is a property less than a value. Valid for number or string timestamp properties. * “in” : Is a value in a property (that is an array of strings).  Filters are supported on the following attributes: * snapshotType * state * status * createdByInfo/id * createdByInfo/name * storageSystemsInfo/id * storageSystemsInfo/storageSystemType * storageSystemsInfo/name * consistency * pointInTime * dataOrchestratorInfo/id * expiresAt * name",
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
    path = f"/backup-recovery/v1beta1/datastores/{path_seg(id)}/snapshots"
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
    name="greenlake_get_backup_recovery_v1beta1_datastores_id_snapshots_snapshot_id",
    description="GET /backup-recovery/v1beta1/datastores/{id}/snapshots/{snapshot-id}\n\nDatastoreSnapshot\n\nGet details of a datastore snapshot.",
    capability=Capability.READ,
)
async def greenlake_get_backup_recovery_v1beta1_datastores_id_snapshots_snapshot_id(
    ctx: Context,
    id: Annotated[str, Field(description="path parameter 'id'")],
    snapshot_id: Annotated[str, Field(description="path parameter 'snapshot-id'")],
) -> Any:
    path = f"/backup-recovery/v1beta1/datastores/{path_seg(id)}/snapshots/{path_seg(snapshot_id)}"
    return await greenlake_request(
        ctx,
        "GET",
        path,
    )


@tool(
    name="greenlake_patch_backup_recovery_v1beta1_datastores_id_snapshots_snapshot_id",
    description="PATCH /backup-recovery/v1beta1/datastores/{id}/snapshots/{snapshot-id}\n\nDatastoreSnapshotUpdate\n\nUpdate a datastore snapshot.",
    capability=Capability.WRITE,
)
async def greenlake_patch_backup_recovery_v1beta1_datastores_id_snapshots_snapshot_id(
    ctx: Context,
    id: Annotated[str, Field(description="path parameter 'id'")],
    snapshot_id: Annotated[str, Field(description="path parameter 'snapshot-id'")],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    path = f"/backup-recovery/v1beta1/datastores/{path_seg(id)}/snapshots/{path_seg(snapshot_id)}"
    return await greenlake_request(
        ctx,
        "PATCH",
        path,
        body=body,
    )
