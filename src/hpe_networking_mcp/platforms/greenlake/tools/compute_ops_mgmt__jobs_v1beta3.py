"""Generated GreenLake tools — DO NOT EDIT BY HAND.

Generated from the vendored spec ``vendor/greenlake/compute-ops-mgmt.json`` by the
maintainer-local GreenLake generator. These modules are committed and are the
runtime source of truth; regeneration is a release-time maintainer workflow
(the generator is intentionally not committed — see ``.gitignore``).

Service: ``compute-ops-mgmt``   Tag: ``jobs_v1beta3``   Operations: 4
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
    name="greenlake_get_compute_ops_mgmt_v1beta3_jobs",
    description="GET /compute-ops-mgmt/v1beta3/jobs\n\nget_v1beta3_jobs\n\nList all jobs",
    capability=Capability.READ,
)
async def greenlake_get_compute_ops_mgmt_v1beta3_jobs(
    ctx: Context,
    offset: Annotated[
        int | None, Field(default=None, description="Zero-based resource offset to start the response from")
    ] = None,
    limit: Annotated[int | None, Field(default=None, description="The maximum number of records to return.")] = None,
    Tenant_Acid: Annotated[
        str | None,
        Field(
            default=None,
            description="Tenant-Acid header can be used by an MSP workspace to make API calls on behalf of their tenant by specifying the tenant's application customer ID.  In order to make such an API call, the Bearer token must belong to an MSP workspace and this header value must be the application customer ID of a tenant within the MSP workspace. Use the `/compute-ops-mgmt/v1beta1/accounts` API to determine the application customer IDs for your tenant accounts.",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if offset is not None:
        query_params["offset"] = offset
    if limit is not None:
        query_params["limit"] = limit
    header_params: dict[str, str] = {}
    if Tenant_Acid is not None:
        header_params["Tenant-Acid"] = str(Tenant_Acid)
    return await greenlake_request(
        ctx,
        "GET",
        "/compute-ops-mgmt/v1beta3/jobs",
        query_params=query_params or None,
        header_params=header_params or None,
    )


@tool(
    name="greenlake_get_compute_ops_mgmt_v1beta3_jobs_id",
    description="GET /compute-ops-mgmt/v1beta3/jobs/{id}\n\nget_v1beta3_job_by_id\n\nGet a job by ID",
    capability=Capability.READ,
)
async def greenlake_get_compute_ops_mgmt_v1beta3_jobs_id(
    ctx: Context,
    id: Annotated[str, Field(description="path parameter 'id'")],
    Tenant_Acid: Annotated[
        str | None,
        Field(
            default=None,
            description="Tenant-Acid header can be used by an MSP workspace to make API calls on behalf of their tenant by specifying the tenant's application customer ID.  In order to make such an API call, the Bearer token must belong to an MSP workspace and this header value must be the application customer ID of a tenant within the MSP workspace. Use the `/compute-ops-mgmt/v1beta1/accounts` API to determine the application customer IDs for your tenant accounts.",
        ),
    ] = None,
) -> Any:
    path = f"/compute-ops-mgmt/v1beta3/jobs/{path_seg(id)}"
    header_params: dict[str, str] = {}
    if Tenant_Acid is not None:
        header_params["Tenant-Acid"] = str(Tenant_Acid)
    return await greenlake_request(
        ctx,
        "GET",
        path,
        header_params=header_params or None,
    )


@tool(
    name="greenlake_patch_compute_ops_mgmt_v1beta3_jobs_id",
    description="PATCH /compute-ops-mgmt/v1beta3/jobs/{id}\n\npatch_v1beta3_job_by_id\n\nPatch a job by ID",
    capability=Capability.WRITE,
)
async def greenlake_patch_compute_ops_mgmt_v1beta3_jobs_id(
    ctx: Context,
    id: Annotated[str, Field(description="path parameter 'id'")],
    Content_Type: Annotated[
        str,
        Field(
            description="Content-Type header must designate 'application/merge-patch+json' in order for the request to be performed."
        ),
    ],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
    Tenant_Acid: Annotated[
        str | None,
        Field(
            default=None,
            description="Tenant-Acid header can be used by an MSP workspace to make API calls on behalf of their tenant by specifying the tenant's application customer ID.  In order to make such an API call, the Bearer token must belong to an MSP workspace and this header value must be the application customer ID of a tenant within the MSP workspace. Use the `/compute-ops-mgmt/v1beta1/accounts` API to determine the application customer IDs for your tenant accounts.",
        ),
    ] = None,
) -> Any:
    path = f"/compute-ops-mgmt/v1beta3/jobs/{path_seg(id)}"
    header_params: dict[str, str] = {}
    if Content_Type is not None:
        header_params["Content-Type"] = str(Content_Type)
    if Tenant_Acid is not None:
        header_params["Tenant-Acid"] = str(Tenant_Acid)
    return await greenlake_request(
        ctx,
        "PATCH",
        path,
        header_params=header_params or None,
        body=body,
    )


@tool(
    name="greenlake_post_compute_ops_mgmt_v1beta3_jobs",
    description="POST /compute-ops-mgmt/v1beta3/jobs\n\ncreate_v1beta3_job\n\nCreate a job",
    capability=Capability.WRITE,
)
async def greenlake_post_compute_ops_mgmt_v1beta3_jobs(
    ctx: Context,
    Content_Type: Annotated[
        str,
        Field(
            description="Content-Type header must designate 'application/json' in order for the request to be performed."
        ),
    ],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
    Tenant_Acid: Annotated[
        str | None,
        Field(
            default=None,
            description="Tenant-Acid header can be used by an MSP workspace to make API calls on behalf of their tenant by specifying the tenant's application customer ID.  In order to make such an API call, the Bearer token must belong to an MSP workspace and this header value must be the application customer ID of a tenant within the MSP workspace. Use the `/compute-ops-mgmt/v1beta1/accounts` API to determine the application customer IDs for your tenant accounts.",
        ),
    ] = None,
) -> Any:
    header_params: dict[str, str] = {}
    if Content_Type is not None:
        header_params["Content-Type"] = str(Content_Type)
    if Tenant_Acid is not None:
        header_params["Tenant-Acid"] = str(Tenant_Acid)
    return await greenlake_request(
        ctx,
        "POST",
        "/compute-ops-mgmt/v1beta3/jobs",
        header_params=header_params or None,
        body=body,
    )
