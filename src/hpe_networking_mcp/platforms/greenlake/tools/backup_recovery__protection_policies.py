"""Generated GreenLake tools — DO NOT EDIT BY HAND.

Generated from the vendored spec ``vendor/greenlake/backup-recovery.json`` by the
maintainer-local GreenLake generator. These modules are committed and are the
runtime source of truth; regeneration is a release-time maintainer workflow
(the generator is intentionally not committed — see ``.gitignore``).

Service: ``backup-recovery``   Tag: ``protection_policies``   Operations: 6
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
    name="greenlake_delete_backup_recovery_v1beta1_protection_policies_id",
    description="DELETE /backup-recovery/v1beta1/protection-policies/{id}\n\nDeleteDataManagementTemplate\n\nDelete a Protection Policy.",
    capability=Capability.WRITE_DELETE,
)
async def greenlake_delete_backup_recovery_v1beta1_protection_policies_id(
    ctx: Context,
    id: Annotated[str, Field(description="path parameter 'id'")],
) -> Any:
    path = f"/backup-recovery/v1beta1/protection-policies/{path_seg(id)}"
    return await greenlake_request(
        ctx,
        "DELETE",
        path,
    )


@tool(
    name="greenlake_get_backup_recovery_v1beta1_protection_policies",
    description="GET /backup-recovery/v1beta1/protection-policies\n\nDataManagementTemplatesList\n\nGet all protection policies.",
    capability=Capability.READ,
)
async def greenlake_get_backup_recovery_v1beta1_protection_policies(
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
            description="The filter query parameter is used to filter the set of resources returned in the response. The returned set of resources must match the criteria in the filter query parameter.        A comparison compares a property name to a literal. The following comparisons are supported: “eq” : Is a property equal to value. Valid for number, boolean and string properties. “gt” : Is a property greater than a value. Valid for number or string timestamp properties. “lt” : Is a property less than a value. Valid for number or string timestamp properties “in” : Is a value in a property (that is an array of strings)  Examples: GET /backup-recovery/v1beta1/protection-policies?filter=protections/type eq CLOUD_BACKUP  Filters are supported on following attributes: * assigned * name * protections/type * protections/applicationType * protections/protectionStoreInfo/name * protections/protectionStoreInfo/id",
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
        "/backup-recovery/v1beta1/protection-policies",
        query_params=query_params or None,
    )


@tool(
    name="greenlake_get_backup_recovery_v1beta1_protection_policies_id",
    description="GET /backup-recovery/v1beta1/protection-policies/{id}\n\nDataManagementTemplateDetail\n\nGet a Protection Policy identified by {id}.",
    capability=Capability.READ,
)
async def greenlake_get_backup_recovery_v1beta1_protection_policies_id(
    ctx: Context,
    id: Annotated[str, Field(description="path parameter 'id'")],
) -> Any:
    path = f"/backup-recovery/v1beta1/protection-policies/{path_seg(id)}"
    return await greenlake_request(
        ctx,
        "GET",
        path,
    )


@tool(
    name="greenlake_patch_backup_recovery_v1beta1_protection_policies_id",
    description="PATCH /backup-recovery/v1beta1/protection-policies/{id}\n\nDataManagementTemplateUpdate\n\nUpdate an assigned Protection Policy.",
    capability=Capability.WRITE,
)
async def greenlake_patch_backup_recovery_v1beta1_protection_policies_id(
    ctx: Context,
    id: Annotated[str, Field(description="path parameter 'id'")],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    path = f"/backup-recovery/v1beta1/protection-policies/{path_seg(id)}"
    return await greenlake_request(
        ctx,
        "PATCH",
        path,
        body=body,
    )


@tool(
    name="greenlake_post_backup_recovery_v1beta1_protection_policies",
    description="POST /backup-recovery/v1beta1/protection-policies\n\nDataManagementTemplateCreate\n\nCreate a new Protection Policy.",
    capability=Capability.WRITE,
)
async def greenlake_post_backup_recovery_v1beta1_protection_policies(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await greenlake_request(
        ctx,
        "POST",
        "/backup-recovery/v1beta1/protection-policies",
        body=body,
    )


@tool(
    name="greenlake_put_backup_recovery_v1beta1_protection_policies_id",
    description="PUT /backup-recovery/v1beta1/protection-policies/{id}\n\nDataManagementTemplateReplace\n\nReplace a Protection Policy completely.",
    capability=Capability.WRITE,
)
async def greenlake_put_backup_recovery_v1beta1_protection_policies_id(
    ctx: Context,
    id: Annotated[str, Field(description="path parameter 'id'")],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    path = f"/backup-recovery/v1beta1/protection-policies/{path_seg(id)}"
    return await greenlake_request(
        ctx,
        "PUT",
        path,
        body=body,
    )
