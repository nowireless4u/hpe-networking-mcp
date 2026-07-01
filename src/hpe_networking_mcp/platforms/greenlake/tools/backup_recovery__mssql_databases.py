"""Generated GreenLake tools — DO NOT EDIT BY HAND.

Generated from the vendored spec ``vendor/greenlake/backup-recovery.json`` by the
maintainer-local GreenLake generator. These modules are committed and are the
runtime source of truth; regeneration is a release-time maintainer workflow
(the generator is intentionally not committed — see ``.gitignore``).

Service: ``backup-recovery``   Tag: ``mssql_databases``   Operations: 4
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
    name="greenlake_get_backup_recovery_v1beta1_mssql_databases",
    description="GET /backup-recovery/v1beta1/mssql-databases\n\nMSSQLDatabaseList\n\nGet all discovered MSSQL databases.",
    capability=Capability.READ,
)
async def greenlake_get_backup_recovery_v1beta1_mssql_databases(
    ctx: Context,
    offset: Annotated[
        int | None,
        Field(default=None, description="The number of items to skip before starting to collect the result set"),
    ] = None,
    limit: Annotated[int | None, Field(default=None, description="The numbers of items to return")] = None,
    filter: Annotated[
        str | None,
        Field(
            default=None,
            description='The filter query parameter is used to filter the set of resources returned in the response. The returned set of resources must match the criteria in the filter query parameter.  A comparison compares a property name to a literal. The following comparisons are supported: * “eq” : Is a property equal to value. Valid for number, boolean and string properties. * “gt” : Is a property greater than a value. Valid for number or string timestamp properties. * “lt” : Is a property less than a value. Valid for number or string timestamp properties * “in” : Is a value in a property (that is an array of strings)  Examples: * GET /backup-recovery/v1beta1/mssql-databases?filter="name eq billing-db-1" * GET /backup-recovery/v1beta1/mssql-databases?filter="applicationHostInfo/name eq myhost1 and status eq Error"   Filters are supported on the following attributes: * state * status * applicationHostInfo/id * applicationHostInfo/name * mssqlDatabaseProtectionGroupInfo/id * mssqlDatabaseProtectionGroupInfo/name * virtualizationInfo/hypervisorManagerInfo/id * createdAt * name',
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
        "/backup-recovery/v1beta1/mssql-databases",
        query_params=query_params or None,
    )


@tool(
    name="greenlake_get_backup_recovery_v1beta1_mssql_databases_db_id",
    description="GET /backup-recovery/v1beta1/mssql-databases/{db-id}\n\nMSSQLDatabase\n\nGet an MSSQL database resource identified by {db-id}.",
    capability=Capability.READ,
)
async def greenlake_get_backup_recovery_v1beta1_mssql_databases_db_id(
    ctx: Context,
    db_id: Annotated[str, Field(description="path parameter 'db-id'")],
) -> Any:
    path = f"/backup-recovery/v1beta1/mssql-databases/{path_seg(db_id)}"
    return await greenlake_request(
        ctx,
        "GET",
        path,
    )


@tool(
    name="greenlake_post_backup_recovery_v1beta1_mssql_databases_db_id_refresh",
    description="POST /backup-recovery/v1beta1/mssql-databases/{db-id}/refresh\n\nRefreshMSSQLDatabase\n\nRefresh an MSSQL database and its sub-resources.",
    capability=Capability.WRITE,
)
async def greenlake_post_backup_recovery_v1beta1_mssql_databases_db_id_refresh(
    ctx: Context,
    db_id: Annotated[str, Field(description="path parameter 'db-id'")],
) -> Any:
    path = f"/backup-recovery/v1beta1/mssql-databases/{path_seg(db_id)}/refresh"
    return await greenlake_request(
        ctx,
        "POST",
        path,
    )


@tool(
    name="greenlake_post_backup_recovery_v1beta1_mssql_databases_db_id_restore",
    description="POST /backup-recovery/v1beta1/mssql-databases/{db-id}/restore\n\nMSSQLDatabaseRestore\n\nRestore an MSSQL database from snapshot or backup.",
    capability=Capability.WRITE,
)
async def greenlake_post_backup_recovery_v1beta1_mssql_databases_db_id_restore(
    ctx: Context,
    db_id: Annotated[str, Field(description="path parameter 'db-id'")],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    path = f"/backup-recovery/v1beta1/mssql-databases/{path_seg(db_id)}/restore"
    return await greenlake_request(
        ctx,
        "POST",
        path,
        body=body,
    )
