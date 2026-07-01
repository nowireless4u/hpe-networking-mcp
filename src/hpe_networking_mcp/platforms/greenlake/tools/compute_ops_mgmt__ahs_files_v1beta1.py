"""Generated GreenLake tools — DO NOT EDIT BY HAND.

Generated from the vendored spec ``vendor/greenlake/compute-ops-mgmt.json`` by the
maintainer-local GreenLake generator. These modules are committed and are the
runtime source of truth; regeneration is a release-time maintainer workflow
(the generator is intentionally not committed — see ``.gitignore``).

Service: ``compute-ops-mgmt``   Tag: ``ahs_files_v1beta1``   Operations: 6
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
    name="greenlake_get_compute_ops_mgmt_v1beta1_ahs_files",
    description="GET /compute-ops-mgmt/v1beta1/ahs-files\n\nget_ahs_files_parse_request_v1beta1\n\nList of all AHS files",
    capability=Capability.READ,
)
async def greenlake_get_compute_ops_mgmt_v1beta1_ahs_files(
    ctx: Context,
    offset: Annotated[
        int | None, Field(default=None, description="Zero-based resource offset to start the response from")
    ] = None,
    limit: Annotated[int | None, Field(default=None, description="The maximum number of records to return.")] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if offset is not None:
        query_params["offset"] = offset
    if limit is not None:
        query_params["limit"] = limit
    return await greenlake_request(
        ctx,
        "GET",
        "/compute-ops-mgmt/v1beta1/ahs-files",
        query_params=query_params or None,
    )


@tool(
    name="greenlake_get_compute_ops_mgmt_v1beta1_ahs_files_id",
    description="GET /compute-ops-mgmt/v1beta1/ahs-files/{id}\n\nget_ahs_file_parse_request_v1beta1_by_id\n\nGet AHS file by id",
    capability=Capability.READ,
)
async def greenlake_get_compute_ops_mgmt_v1beta1_ahs_files_id(
    ctx: Context,
    id: Annotated[str, Field(description="Unique File Identifier (File UUID)")],
) -> Any:
    path = f"/compute-ops-mgmt/v1beta1/ahs-files/{path_seg(id)}"
    return await greenlake_request(
        ctx,
        "GET",
        path,
    )


@tool(
    name="greenlake_get_compute_ops_mgmt_v1beta1_ahs_files_id_download",
    description="GET /compute-ops-mgmt/v1beta1/ahs-files/{id}/download\n\nget_ahs_file_download_request_v1beta1\n\nDownload parsed AHS file contents",
    capability=Capability.READ,
)
async def greenlake_get_compute_ops_mgmt_v1beta1_ahs_files_id_download(
    ctx: Context,
    id: Annotated[str, Field(description="Unique File Identifier (File UUID)")],
    filename: Annotated[str, Field(description="File name to be downloaded")],
) -> Any:
    path = f"/compute-ops-mgmt/v1beta1/ahs-files/{path_seg(id)}/download"
    query_params: dict[str, Any] = {}
    if filename is not None:
        query_params["filename"] = filename
    return await greenlake_request(
        ctx,
        "GET",
        path,
        query_params=query_params or None,
    )


@tool(
    name="greenlake_patch_compute_ops_mgmt_v1beta1_ahs_files_id",
    description="PATCH /compute-ops-mgmt/v1beta1/ahs-files/{id}\n\npatch_ahs_file_parse_status_request_v1beta1_by_id\n\nUpdate the parsing status of an AHS file",
    capability=Capability.WRITE,
)
async def greenlake_patch_compute_ops_mgmt_v1beta1_ahs_files_id(
    ctx: Context,
    id: Annotated[str, Field(description="Unique File Identifier (File UUID)")],
    Content_Type: Annotated[
        str,
        Field(
            description="Content-Type header must designate 'application/merge-patch+json' in order for the request to be performed."
        ),
    ],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    path = f"/compute-ops-mgmt/v1beta1/ahs-files/{path_seg(id)}"
    header_params: dict[str, str] = {}
    if Content_Type is not None:
        header_params["Content-Type"] = str(Content_Type)
    return await greenlake_request(
        ctx,
        "PATCH",
        path,
        header_params=header_params or None,
        body=body,
    )


@tool(
    name="greenlake_post_compute_ops_mgmt_v1beta1_ahs_files",
    description="POST /compute-ops-mgmt/v1beta1/ahs-files\n\npost_ahs_file_upload_request_v1beta1\n\nCreate AHS file upload",
    capability=Capability.WRITE,
)
async def greenlake_post_compute_ops_mgmt_v1beta1_ahs_files(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await greenlake_request(
        ctx,
        "POST",
        "/compute-ops-mgmt/v1beta1/ahs-files",
        body=body,
    )


@tool(
    name="greenlake_post_compute_ops_mgmt_v1beta1_ahs_files_id_parse",
    description="POST /compute-ops-mgmt/v1beta1/ahs-files/{id}/parse\n\npost_ahs_file_parse_request_v1beta1_by_id\n\nParse uploaded AHS file",
    capability=Capability.WRITE,
)
async def greenlake_post_compute_ops_mgmt_v1beta1_ahs_files_id_parse(
    ctx: Context,
    id: Annotated[str, Field(description="Unique File Identifier (File UUID)")],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    path = f"/compute-ops-mgmt/v1beta1/ahs-files/{path_seg(id)}/parse"
    return await greenlake_request(
        ctx,
        "POST",
        path,
        body=body,
    )
