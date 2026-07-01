"""Generated GreenLake tools — DO NOT EDIT BY HAND.

Generated from the vendored spec ``vendor/greenlake/compute-ops-mgmt.json`` by the
maintainer-local GreenLake generator. These modules are committed and are the
runtime source of truth; regeneration is a release-time maintainer workflow
(the generator is intentionally not committed — see ``.gitignore``).

Service: ``compute-ops-mgmt``   Tag: ``approval_policy_v1beta2``   Operations: 5
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
    name="greenlake_delete_compute_ops_mgmt_v1beta2_approval_policies_policy_id",
    description="DELETE /compute-ops-mgmt/v1beta2/approval-policies/{policy_id}\n\ndelete_v1beta1_approval_policy_by_id\n\nDelete an approval policy",
    capability=Capability.WRITE_DELETE,
)
async def greenlake_delete_compute_ops_mgmt_v1beta2_approval_policies_policy_id(
    ctx: Context,
    policy_id: Annotated[str, Field(description="Unique Policy Identifier")],
) -> Any:
    path = f"/compute-ops-mgmt/v1beta2/approval-policies/{path_seg(policy_id)}"
    return await greenlake_request(
        ctx,
        "DELETE",
        path,
    )


@tool(
    name="greenlake_get_compute_ops_mgmt_v1beta2_approval_policies",
    description="GET /compute-ops-mgmt/v1beta2/approval-policies\n\nget_v1beta2_approval_policies\n\nList all approval policies",
    capability=Capability.READ,
)
async def greenlake_get_compute_ops_mgmt_v1beta2_approval_policies(
    ctx: Context,
    offset: Annotated[
        int | None, Field(default=None, description="Zero-based resource offset to start the response from")
    ] = None,
    limit: Annotated[int | None, Field(default=None, description="The maximum number of records to return.")] = None,
    filter: Annotated[
        str | None,
        Field(
            default=None,
            description="Limit the resources operated on by an endpoint or when used with a multiple-GET endpoint, return only the subset of resources that match the filter. The filter grammar is a subset of OData 4.0.  NOTE: The filter query parameter must use [URL encoding](https://en.wikipedia.org/wiki/URL_encoding). Most clients do this automatically with inputs provided to them specifically as query parameters. Encoding must be done manually for any query parameters provided as part of the URL.   The reserved characters `!` `#` `$` `&` `'` `(` `)` `*` `+` `,` `/` `:` `;` `=` `?` `@` `[` `]` must be encoded with percent encoded equivalents. Server IDs contain a `+`, which must be encoded as `%2B`.   For example: the value `P06760-B21+2M212504P8` must be encoded as `P06760-B21%2B2M212504P8` when it is used in a query parameter.  | CLASS     |  EXAMPLES                                          | |-----------|----------------------------------------------------| | Types     | integer, decimal, timestamp, string, boolean, null | | Operations| eq, ne, gt, ge, lt, le, in                         | | Logic     | and, or, not                                       |  Approval policies can be filtered by: - createdAt - description - name - policyData/resources/id - policyData/resources/type - updatedAt  The following examples are not an exhaustive list of all possible filtering options.",
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
    return await greenlake_request(
        ctx,
        "GET",
        "/compute-ops-mgmt/v1beta2/approval-policies",
        query_params=query_params or None,
    )


@tool(
    name="greenlake_get_compute_ops_mgmt_v1beta2_approval_policies_policy_id",
    description="GET /compute-ops-mgmt/v1beta2/approval-policies/{policy_id}\n\nget_v1beta2_approval_policy_by_id\n\nGet approval policy by id",
    capability=Capability.READ,
)
async def greenlake_get_compute_ops_mgmt_v1beta2_approval_policies_policy_id(
    ctx: Context,
    policy_id: Annotated[str, Field(description="Unique Policy Identifier")],
) -> Any:
    path = f"/compute-ops-mgmt/v1beta2/approval-policies/{path_seg(policy_id)}"
    return await greenlake_request(
        ctx,
        "GET",
        path,
    )


@tool(
    name="greenlake_patch_compute_ops_mgmt_v1beta2_approval_policies_policy_id",
    description="PATCH /compute-ops-mgmt/v1beta2/approval-policies/{policy_id}\n\npatch_v1beta2_approval_policy_by_id\n\nUpdate the policy by id",
    capability=Capability.WRITE,
)
async def greenlake_patch_compute_ops_mgmt_v1beta2_approval_policies_policy_id(
    ctx: Context,
    policy_id: Annotated[str, Field(description="Unique Policy Identifier")],
    Content_Type: Annotated[
        str,
        Field(
            description="Content-Type header must designate 'application/merge-patch+json' in order for the request to be performed."
        ),
    ],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    path = f"/compute-ops-mgmt/v1beta2/approval-policies/{path_seg(policy_id)}"
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
    name="greenlake_post_compute_ops_mgmt_v1beta2_approval_policies",
    description="POST /compute-ops-mgmt/v1beta2/approval-policies\n\npost_create_approval_policy_v1beta2\n\nCreate an approval policy",
    capability=Capability.WRITE,
)
async def greenlake_post_compute_ops_mgmt_v1beta2_approval_policies(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await greenlake_request(
        ctx,
        "POST",
        "/compute-ops-mgmt/v1beta2/approval-policies",
        body=body,
    )
