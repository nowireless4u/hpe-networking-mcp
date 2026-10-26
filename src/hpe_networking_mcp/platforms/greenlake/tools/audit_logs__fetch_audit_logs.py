"""Generated GreenLake tools — DO NOT EDIT BY HAND.

Generated from the vendored spec ``vendor/greenlake/audit-logs.json`` by the
maintainer-local GreenLake generator. These modules are committed and are the
runtime source of truth; regeneration is a release-time maintainer workflow
(the generator is intentionally not committed — see ``.gitignore``).

Service: ``audit-logs``   Tag: ``fetch_audit_logs``   Operations: 3
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
    name="greenlake_get_audit_log_v2beta1_logs",
    description="GET /audit-log/v2beta1/logs\n\ngetAuditLogs\n\nRetrieves audit logs of one or more services.",
    capability=Capability.READ,
)
async def greenlake_get_audit_log_v2beta1_logs(
    ctx: Context,
    filter: Annotated[str | None, Field(default=None, description="query parameter 'filter'")] = None,
    select: Annotated[
        str | None,
        Field(
            default=None,
            description="Use the `select` query parameter to restrict the number of properties included in the audit log response. Specify as comma-separated values. The supported select parameters are:  * serviceOffer  * createdAt  * category  * hasDetails  * workspace  * description  * username  * ipAddress  * additionalInfo",
        ),
    ] = None,
    limit: Annotated[
        int | None, Field(default=None, description="How many items to return at one time (max 2000)")
    ] = None,
    offset: Annotated[
        int | None,
        Field(default=None, description="Specifies the zero-based resource offset to start the response from."),
    ] = None,
    sort: Annotated[
        str | None,
        Field(
            default=None,
            description="Sort the results based on the specified field. The default sort order is descending. Each sort expression is a property name optionally followed by a direction indicator asc (ascending) or desc (descending).",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if filter is not None:
        query_params["filter"] = filter
    if select is not None:
        query_params["select"] = select
    if limit is not None:
        query_params["limit"] = limit
    if offset is not None:
        query_params["offset"] = offset
    if sort is not None:
        query_params["sort"] = sort
    return await greenlake_request(
        ctx,
        "GET",
        "/audit-log/v2beta1/logs",
        query_params=query_params or None,
    )


@tool(
    name="greenlake_get_audit_log_v2beta1_logs_id",
    description="GET /audit-log/v2beta1/logs/{id}\n\ngetAuditLog\n\nGet a specific audit log.",
    capability=Capability.READ,
)
async def greenlake_get_audit_log_v2beta1_logs_id(
    ctx: Context,
    id: Annotated[str, Field(description="Provide the ID of the audit log record to fetch the audit log.")],
) -> Any:
    path = f"/audit-log/v2beta1/logs/{path_seg(id)}"
    return await greenlake_request(
        ctx,
        "GET",
        path,
    )


@tool(
    name="greenlake_get_audit_log_v2beta1_logs_id_details",
    description="GET /audit-log/v2beta1/logs/{id}/details\n\ngetAuditLogDetails\n\nGet a specific audit log details.",
    capability=Capability.READ,
)
async def greenlake_get_audit_log_v2beta1_logs_id_details(
    ctx: Context,
    id: Annotated[str, Field(description="Provide the ID of the audit log record to fetch the audit log details.")],
) -> Any:
    path = f"/audit-log/v2beta1/logs/{path_seg(id)}/details"
    return await greenlake_request(
        ctx,
        "GET",
        path,
    )
