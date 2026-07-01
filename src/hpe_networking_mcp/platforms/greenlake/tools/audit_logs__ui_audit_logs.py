"""Generated GreenLake tools — DO NOT EDIT BY HAND.

Generated from the vendored spec ``vendor/greenlake/audit-logs.json`` by the
maintainer-local GreenLake generator. These modules are committed and are the
runtime source of truth; regeneration is a release-time maintainer workflow
(the generator is intentionally not committed — see ``.gitignore``).

Service: ``audit-logs``   Tag: ``ui_audit_logs``   Operations: 9
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
    name="greenlake_delete_auditligs_ui_v1_configs_audit_id",
    description="DELETE /auditligs/ui/v1/configs/{audit-id}\n\ndeleteAuditLogConfigs\n\nDelete external application audit logs specific configurations.",
    capability=Capability.WRITE_DELETE,
)
async def greenlake_delete_auditligs_ui_v1_configs_audit_id(
    ctx: Context,
    audit_id: Annotated[str, Field(description="Audit id")],
) -> Any:
    path = f"/auditligs/ui/v1/configs/{path_seg(audit_id)}"
    return await greenlake_request(
        ctx,
        "DELETE",
        path,
    )


@tool(
    name="greenlake_get_auditlogs_ui_v1_application_id_configs",
    description="GET /auditlogs/ui/v1/{application-id}/configs\n\ngetAuditLogConfigs\n\nGet the audit log configurations related to an application",
    capability=Capability.READ,
)
async def greenlake_get_auditlogs_ui_v1_application_id_configs(
    ctx: Context,
    application_id: Annotated[str, Field(description="Application id")],
) -> Any:
    path = f"/auditlogs/ui/v1/{path_seg(application_id)}/configs"
    return await greenlake_request(
        ctx,
        "GET",
        path,
    )


@tool(
    name="greenlake_get_auditlogs_ui_v1_applications",
    description="GET /auditlogs/ui/v1/applications\n\ngetApplications\n\nGet all the application instance details.",
    capability=Capability.READ,
)
async def greenlake_get_auditlogs_ui_v1_applications(
    ctx: Context,
) -> Any:
    return await greenlake_request(
        ctx,
        "GET",
        "/auditlogs/ui/v1/applications",
    )


@tool(
    name="greenlake_get_auditlogs_ui_v1_count",
    description="GET /auditlogs/ui/v1/count\n\ngetAuditLogsCount\n\nGet the number of audit logs in the system for the current customer-id from given timestamp",
    capability=Capability.READ,
)
async def greenlake_get_auditlogs_ui_v1_count(
    ctx: Context,
    start_time: Annotated[float, Field(description="Start time for filtering. Expects a epoch time integer value")],
    end_time: Annotated[float, Field(description="End time for filtering. Expects a epoch time integer value")],
    app_slug: Annotated[str, Field(description="Application slug")],
    application_customer_id: Annotated[
        str | None, Field(default=None, description="Application customer id of the application instance.")
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if start_time is not None:
        query_params["start_time"] = start_time
    if end_time is not None:
        query_params["end_time"] = end_time
    if app_slug is not None:
        query_params["app_slug"] = app_slug
    if application_customer_id is not None:
        query_params["application_customer_id"] = application_customer_id
    return await greenlake_request(
        ctx,
        "GET",
        "/auditlogs/ui/v1/count",
        query_params=query_params or None,
    )


@tool(
    name="greenlake_get_auditlogs_ui_v1_details",
    description="GET /auditlogs/ui/v1/details\n\ngetAuditLogDetails\n\nGet additional detail of an audit log.",
    capability=Capability.READ,
)
async def greenlake_get_auditlogs_ui_v1_details(
    ctx: Context,
    audit_id: Annotated[str, Field(description="Unique audit log id")],
    index_id: Annotated[str, Field(description="Elasticsearch index for the entry.")],
) -> Any:
    query_params: dict[str, Any] = {}
    if audit_id is not None:
        query_params["audit_id"] = audit_id
    if index_id is not None:
        query_params["index_id"] = index_id
    return await greenlake_request(
        ctx,
        "GET",
        "/auditlogs/ui/v1/details",
        query_params=query_params or None,
    )


@tool(
    name="greenlake_get_auditlogs_ui_v1_download",
    description="GET /auditlogs/ui/v1/download\n\ndownloadAuditLogs\n\nDownload audit logs in CSV or PDF format.",
    capability=Capability.READ,
)
async def greenlake_get_auditlogs_ui_v1_download(
    ctx: Context,
    app_slug: Annotated[str, Field(description="Application slug")],
    columns: Annotated[list[str], Field(description="The columns which are to be present in the requested file.")],
    file_extension: Annotated[
        str, Field(description="The file extension implying the format in which the audit-trail has to be downloaded")
    ],
) -> Any:
    query_params: dict[str, Any] = {}
    if app_slug is not None:
        query_params["app_slug"] = app_slug
    if columns is not None:
        query_params["columns"] = columns
    if file_extension is not None:
        query_params["file_extension"] = file_extension
    return await greenlake_request(
        ctx,
        "GET",
        "/auditlogs/ui/v1/download",
        query_params=query_params or None,
    )


@tool(
    name="greenlake_get_auditlogs_ui_v1_search",
    description="GET /auditlogs/ui/v1/search\n\ngetAuditLogs\n\nGet all audit logs of an application instance or workspace.",
    capability=Capability.READ,
)
async def greenlake_get_auditlogs_ui_v1_search(
    ctx: Context,
    app_slug: Annotated[str, Field(description="Application slug")],
    application_customer_id: Annotated[
        str | None, Field(default=None, description="Application customer id of the application instance.")
    ] = None,
    start_time: Annotated[
        int | None, Field(default=None, description="Start time for filtering. Expects a epoch time integer value")
    ] = None,
    end_time: Annotated[
        int | None, Field(default=None, description="End time for filtering. Expects a epoch time integer value")
    ] = None,
    category: Annotated[str | None, Field(default=None, description="Audit log category")] = None,
    description: Annotated[str | None, Field(default=None, description="Audit log description")] = None,
    ip_address: Annotated[
        str | None, Field(default=None, description="IP address contained within the additional details of the log.")
    ] = None,
    username: Annotated[str | None, Field(default=None, description="User's email address")] = None,
    account_name: Annotated[
        str | None, Field(default=None, description="Name of the Workspace to which the audit log belong")
    ] = None,
    all: Annotated[str | None, Field(default=None, description="Filter for all fields")] = None,
    offset: Annotated[int | None, Field(default=None, description="Offset for pagination")] = None,
    limit: Annotated[int | None, Field(default=None, description="Number of items per page")] = None,
    sort_by: Annotated[str | None, Field(default=None, description="Field to sort by")] = None,
    sort_dir: Annotated[str | None, Field(default=None, description="Sort direction (asc or desc)")] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if app_slug is not None:
        query_params["app_slug"] = app_slug
    if application_customer_id is not None:
        query_params["application_customer_id"] = application_customer_id
    if start_time is not None:
        query_params["start_time"] = start_time
    if end_time is not None:
        query_params["end_time"] = end_time
    if category is not None:
        query_params["category"] = category
    if description is not None:
        query_params["description"] = description
    if ip_address is not None:
        query_params["ip_address"] = ip_address
    if username is not None:
        query_params["username"] = username
    if account_name is not None:
        query_params["account_name"] = account_name
    if all is not None:
        query_params["_all"] = all
    if offset is not None:
        query_params["offset"] = offset
    if limit is not None:
        query_params["limit"] = limit
    if sort_by is not None:
        query_params["sort_by"] = sort_by
    if sort_dir is not None:
        query_params["sort_dir"] = sort_dir
    return await greenlake_request(
        ctx,
        "GET",
        "/auditlogs/ui/v1/search",
        query_params=query_params or None,
    )


@tool(
    name="greenlake_post_auditlogs_ui_v1_configs",
    description="POST /auditlogs/ui/v1/configs\n\ncreateAuditLogConfigs\n\nPost external application audit logs specific configurations.",
    capability=Capability.WRITE,
)
async def greenlake_post_auditlogs_ui_v1_configs(
    ctx: Context,
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request body")] = None,
) -> Any:
    return await greenlake_request(
        ctx,
        "POST",
        "/auditlogs/ui/v1/configs",
        body=body,
    )


@tool(
    name="greenlake_put_auditlogs_ui_v1_configs",
    description="PUT /auditlogs/ui/v1/configs\n\nupdateAuditLogConfigs\n\nUpdate external application audit logs specific configurations.",
    capability=Capability.WRITE,
)
async def greenlake_put_auditlogs_ui_v1_configs(
    ctx: Context,
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request body")] = None,
) -> Any:
    return await greenlake_request(
        ctx,
        "PUT",
        "/auditlogs/ui/v1/configs",
        body=body,
    )
