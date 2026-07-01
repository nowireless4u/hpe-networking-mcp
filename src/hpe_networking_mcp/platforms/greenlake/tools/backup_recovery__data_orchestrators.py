"""Generated GreenLake tools — DO NOT EDIT BY HAND.

Generated from the vendored spec ``vendor/greenlake/backup-recovery.json`` by the
maintainer-local GreenLake generator. These modules are committed and are the
runtime source of truth; regeneration is a release-time maintainer workflow
(the generator is intentionally not committed — see ``.gitignore``).

Service: ``backup-recovery``   Tag: ``data_orchestrators``   Operations: 11
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
    name="greenlake_delete_backup_recovery_v1beta1_data_orchestrators_id",
    description="DELETE /backup-recovery/v1beta1/data-orchestrators/{id}\n\nDataOrchestratorDelete\n\nUnregister the Data Orchestrator from DSCC",
    capability=Capability.WRITE_DELETE,
)
async def greenlake_delete_backup_recovery_v1beta1_data_orchestrators_id(
    ctx: Context,
    id: Annotated[str, Field(description="id of the Data Orchestrator.")],
    force: Annotated[
        bool | None,
        Field(
            default=None,
            description="Force option to forcefully unregister the Data Orchestrator when dependent resources cannot first be removed.",
        ),
    ] = None,
) -> Any:
    path = f"/backup-recovery/v1beta1/data-orchestrators/{path_seg(id)}"
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
    name="greenlake_get_backup_recovery_v1beta1_data_orchestrators",
    description="GET /backup-recovery/v1beta1/data-orchestrators\n\nDataOrchestratorList\n\nGet a list of the Data Orchestrators that are registered with DSCC",
    capability=Capability.READ,
)
async def greenlake_get_backup_recovery_v1beta1_data_orchestrators(
    ctx: Context,
    offset: Annotated[
        int | None,
        Field(
            default=None,
            description="When listing a large number of Data Orchestrators, the offset query parameter defines the index of the first Data Orchestrator to include in the response.  Example: * GET /backup-recovery/v1beta1/data-orchestrators?offset=10",
        ),
    ] = None,
    limit: Annotated[
        int | None,
        Field(
            default=None,
            description="The limit query parameter defines the maximum number of Data Orchestrators to included in the response.  Example: * GET /backup-recovery/v1beta1/data-orchestrators?limit=10",
        ),
    ] = None,
    sort: Annotated[
        str | None,
        Field(
            default=None,
            description="The sort query is a comma separated list of properties defining the sort order. The direction indicator may only be either “asc” (ascending) or “desc” (descending).  If no direction indicator is specified, the default order is ascending.  Sorting is supported on the following properties: * name * generation * connectionState * serialNumber * softwareVersion * status * state * stateReason * id * platform * vCpu * totalMemoryInGiB * poweredOnAt * createdAt * interfaces/network/defaultGateway * dateTime/methodDateTimeSet * dateTime/timezone * ntp/status * ntp/state * ntp/stateReason  Example: * GET /backup-recovery/v1beta1/data-orchestrators?sort=name,generation desc",
        ),
    ] = None,
    select: Annotated[
        str | None,
        Field(
            default=None,
            description="The select query parameter is used to define a subset of properties to be included in the response. Each property to be included should be passed in a comma-separated list.  Example: * GET /backup-recovery/v1beta1/data-orchestrators?select=id,name,serialNumber",
        ),
    ] = None,
    filter: Annotated[
        str | None,
        Field(
            default=None,
            description="The filter query parameter is used to filter the list of on-prem engines returned in the response. The returned set of resources will match the criteria in the filter query parameter.  A comparision compares a property name to a literal. The comparisons supported are the following: * “eq” : Is a property equal to value. Valid for number, boolean and string properties. * “gt” : Is a property greater than a value. Valid for number or string timestamp properties. * “lt” : Is a property less than a value. Valid for number or string timestamp properties * “in” : Is a value in a property (that is an array of strings)  Examples: * GET /backup-recovery/v1beta1/data-orchestrators?filter=connectionState eq 'CONNECTED' * GET /backup-recovery/v1beta1/data-orchestrators?filter=connectionState eq 'CONNECTED' and status eq 'ERROR'  Filtering is supported with the following attributes: * id * name * interfaces/network/hostname * serialNumber * status * state * connectionState  * softwareVersion",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if offset is not None:
        query_params["offset"] = offset
    if limit is not None:
        query_params["limit"] = limit
    if sort is not None:
        query_params["sort"] = sort
    if select is not None:
        query_params["select"] = select
    if filter is not None:
        query_params["filter"] = filter
    return await greenlake_request(
        ctx,
        "GET",
        "/backup-recovery/v1beta1/data-orchestrators",
        query_params=query_params or None,
    )


@tool(
    name="greenlake_get_backup_recovery_v1beta1_data_orchestrators_id",
    description="GET /backup-recovery/v1beta1/data-orchestrators/{id}\n\nDataOrchestratorListById\n\nGet details of a Data Orchestrator registered with DSCC",
    capability=Capability.READ,
)
async def greenlake_get_backup_recovery_v1beta1_data_orchestrators_id(
    ctx: Context,
    id: Annotated[str, Field(description="id of the Data Orchestrator.")],
    select: Annotated[
        str | None,
        Field(
            default=None,
            description="The select query parameter is used to define a subset of properties to be included in the response. Each property to be included should be passed in a comma-separated list.  Example: * GET /backup-recovery/v1beta1/data-orchestrators/4cf33ce9-3d8a-4c79-8dbb-3a145804bf7d?select=id,name,interfaces/network/hostname",
        ),
    ] = None,
) -> Any:
    path = f"/backup-recovery/v1beta1/data-orchestrators/{path_seg(id)}"
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
    name="greenlake_patch_backup_recovery_v1beta1_data_orchestrators_id",
    description="PATCH /backup-recovery/v1beta1/data-orchestrators/{id}\n\nDataOrchestratorModify\n\nModify the configuration of a Data Orchestrator",
    capability=Capability.WRITE,
)
async def greenlake_patch_backup_recovery_v1beta1_data_orchestrators_id(
    ctx: Context,
    id: Annotated[str, Field(description="id of the Data Orchestrator.")],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    path = f"/backup-recovery/v1beta1/data-orchestrators/{path_seg(id)}"
    return await greenlake_request(
        ctx,
        "PATCH",
        path,
        body=body,
    )


@tool(
    name="greenlake_post_backup_recovery_v1beta1_data_orchestrators",
    description="POST /backup-recovery/v1beta1/data-orchestrators\n\nDataOrchestratorCreate\n\nRegister a new Data Orchestrator with DSCC",
    capability=Capability.WRITE,
)
async def greenlake_post_backup_recovery_v1beta1_data_orchestrators(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await greenlake_request(
        ctx,
        "POST",
        "/backup-recovery/v1beta1/data-orchestrators",
        body=body,
    )


@tool(
    name="greenlake_post_backup_recovery_v1beta1_data_orchestrators_id_generate_support_bundle",
    description="POST /backup-recovery/v1beta1/data-orchestrators/{id}/generate-support-bundle\n\nSupportBundleCreate\n\nGenerate a new support-bundle",
    capability=Capability.WRITE,
)
async def greenlake_post_backup_recovery_v1beta1_data_orchestrators_id_generate_support_bundle(
    ctx: Context,
    id: Annotated[str, Field(description="id of the Data Orchestrator.")],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    path = f"/backup-recovery/v1beta1/data-orchestrators/{path_seg(id)}/generate-support-bundle"
    return await greenlake_request(
        ctx,
        "POST",
        path,
        body=body,
    )


@tool(
    name="greenlake_post_backup_recovery_v1beta1_data_orchestrators_id_generate_totp",
    description="POST /backup-recovery/v1beta1/data-orchestrators/{id}/generate-totp\n\nOTPCreate\n\nGenerate a time-based one time passcode (TOTP) for Data Orchestrator access",
    capability=Capability.WRITE,
)
async def greenlake_post_backup_recovery_v1beta1_data_orchestrators_id_generate_totp(
    ctx: Context,
    id: Annotated[str, Field(description="id of the Data Orchestrator.")],
) -> Any:
    path = f"/backup-recovery/v1beta1/data-orchestrators/{path_seg(id)}/generate-totp"
    return await greenlake_request(
        ctx,
        "POST",
        path,
    )


@tool(
    name="greenlake_post_backup_recovery_v1beta1_data_orchestrators_id_recover",
    description="POST /backup-recovery/v1beta1/data-orchestrators/{id}/recover\n\nDataOrchestratorRecover\n\nRecover a Data Orchestrator identified by id",
    capability=Capability.WRITE,
)
async def greenlake_post_backup_recovery_v1beta1_data_orchestrators_id_recover(
    ctx: Context,
    id: Annotated[str, Field(description="id of the Data Orchestrator.")],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    path = f"/backup-recovery/v1beta1/data-orchestrators/{path_seg(id)}/recover"
    return await greenlake_request(
        ctx,
        "POST",
        path,
        body=body,
    )


@tool(
    name="greenlake_post_backup_recovery_v1beta1_data_orchestrators_id_restart_guest_os",
    description="POST /backup-recovery/v1beta1/data-orchestrators/{id}/restart-guest-os\n\nDataOrchestratorReboot\n\nRestart a Data Orchestrator",
    capability=Capability.WRITE,
)
async def greenlake_post_backup_recovery_v1beta1_data_orchestrators_id_restart_guest_os(
    ctx: Context,
    id: Annotated[str, Field(description="id of the Data Orchestrator.")],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    path = f"/backup-recovery/v1beta1/data-orchestrators/{path_seg(id)}/restart-guest-os"
    return await greenlake_request(
        ctx,
        "POST",
        path,
        body=body,
    )


@tool(
    name="greenlake_post_backup_recovery_v1beta1_data_orchestrators_id_set_remote_support",
    description="POST /backup-recovery/v1beta1/data-orchestrators/{id}/set-remote-support\n\nDataOrchestratorInfosightConfigModify\n\nModify InfoSight Configuration for a Data Orchestrator",
    capability=Capability.WRITE,
)
async def greenlake_post_backup_recovery_v1beta1_data_orchestrators_id_set_remote_support(
    ctx: Context,
    id: Annotated[str, Field(description="id of the Data Orchestrator.")],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    path = f"/backup-recovery/v1beta1/data-orchestrators/{path_seg(id)}/set-remote-support"
    return await greenlake_request(
        ctx,
        "POST",
        path,
        body=body,
    )


@tool(
    name="greenlake_post_backup_recovery_v1beta1_data_orchestrators_id_shutdown_guest_os",
    description="POST /backup-recovery/v1beta1/data-orchestrators/{id}/shutdown-guest-os\n\nDataOrchestratorShutdown\n\nShutdown a Data Orchestrator",
    capability=Capability.WRITE,
)
async def greenlake_post_backup_recovery_v1beta1_data_orchestrators_id_shutdown_guest_os(
    ctx: Context,
    id: Annotated[str, Field(description="id of the Data Orchestrator.")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request body")] = None,
) -> Any:
    path = f"/backup-recovery/v1beta1/data-orchestrators/{path_seg(id)}/shutdown-guest-os"
    return await greenlake_request(
        ctx,
        "POST",
        path,
        body=body,
    )
