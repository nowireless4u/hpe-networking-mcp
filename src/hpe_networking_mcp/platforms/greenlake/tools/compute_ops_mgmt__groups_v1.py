"""Generated GreenLake tools — DO NOT EDIT BY HAND.

Generated from the vendored spec ``vendor/greenlake/compute-ops-mgmt.json`` by the
maintainer-local GreenLake generator. These modules are committed and are the
runtime source of truth; regeneration is a release-time maintainer workflow
(the generator is intentionally not committed — see ``.gitignore``).

Service: ``compute-ops-mgmt``   Tag: ``groups_v1``   Operations: 11
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
    name="greenlake_delete_compute_ops_mgmt_v1_groups_group_id",
    description="DELETE /compute-ops-mgmt/v1/groups/{group-id}\n\ndelete_v1_group_by_id\n\nDelete a group",
    capability=Capability.WRITE_DELETE,
)
async def greenlake_delete_compute_ops_mgmt_v1_groups_group_id(
    ctx: Context,
    group_id: Annotated[str, Field(description="path parameter 'group-id'")],
    force: Annotated[
        bool | None,
        Field(
            default=None,
            description="If you would like to remove all devices and delete the group, provide the query parameter force=true.",
        ),
    ] = None,
) -> Any:
    path = f"/compute-ops-mgmt/v1/groups/{path_seg(group_id)}"
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
    name="greenlake_get_compute_ops_mgmt_v1_groups",
    description="GET /compute-ops-mgmt/v1/groups\n\nget_v1_groups\n\nList all groups",
    capability=Capability.READ,
)
async def greenlake_get_compute_ops_mgmt_v1_groups(
    ctx: Context,
    offset: Annotated[
        int | None, Field(default=None, description="Zero-based resource offset to start the response from")
    ] = None,
    limit: Annotated[int | None, Field(default=None, description="The maximum number of records to return.")] = None,
    filter: Annotated[
        str | None,
        Field(
            default=None,
            description="Limit the resources operated on by an endpoint or when used with a multiple-GET endpoint, return only the subset of resources that match the filter. The filter grammar is a subset of OData 4.0.  NOTE: The filter query parameter must use [URL encoding](https://en.wikipedia.org/wiki/URL_encoding). Most clients do this automatically with inputs provided to them specifically as query parameters. Encoding must be done manually for any query parameters provided as part of the URL.   The reserved characters `!` `#` `$` `&` `'` `(` `)` `*` `+` `,` `/` `:` `;` `=` `?` `@` `[` `]` must be encoded with percent encoded equivalents. Device IDs contain a `+`, which must be encoded as `%2B`.   For example: the value `P06760-B21+2M212504P8` must be encoded as `P06760-B21%2B2M212504P8` when it is used in a query parameter.  | CLASS     |  EXAMPLES                                          | |-----------|----------------------------------------------------| | Types     | integer, decimal, timestamp, string, boolean, null | | Operations| eq, ne, gt, ge, lt, le, in                         | | Logic     | and, or, not                                       |  Groups can be filtered by:   - autoAddTags   - complianceStatus   - createdAt   - description   - deviceType   - generation   - id   - name   - policies   - securityStatus   - settingsUris   - updatedAt   The following examples are not an exhaustive list of all possible filtering options.",
        ),
    ] = None,
    sort: Annotated[
        str | None,
        Field(
            default=None,
            description="The order in which to return the resources in the collection.  The value of the sort query parameter is a comma separated list of sort expressions.  Each sort expression is a property name optionally followed by a direction indicator asc (ascending) or desc  (descending).  The first sort expression in the list defines the primary sort order, the second defines the secondary sort order,  and so on. If a direciton indicator is omitted the default direction is ascending.",
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
    return await greenlake_request(
        ctx,
        "GET",
        "/compute-ops-mgmt/v1/groups",
        query_params=query_params or None,
    )


@tool(
    name="greenlake_get_compute_ops_mgmt_v1_groups_group_id",
    description="GET /compute-ops-mgmt/v1/groups/{group-id}\n\nget_v1_group_by_id\n\nGet a group by ID",
    capability=Capability.READ,
)
async def greenlake_get_compute_ops_mgmt_v1_groups_group_id(
    ctx: Context,
    group_id: Annotated[str, Field(description="path parameter 'group-id'")],
) -> Any:
    path = f"/compute-ops-mgmt/v1/groups/{path_seg(group_id)}"
    return await greenlake_request(
        ctx,
        "GET",
        path,
    )


@tool(
    name="greenlake_get_compute_ops_mgmt_v1_groups_group_id_compliance",
    description="GET /compute-ops-mgmt/v1/groups/{group-id}/compliance\n\nget_v1_group_devices_compliance\n\nList all devices compliance in a group",
    capability=Capability.READ,
)
async def greenlake_get_compute_ops_mgmt_v1_groups_group_id_compliance(
    ctx: Context,
    group_id: Annotated[str, Field(description="path parameter 'group-id'")],
    filter: Annotated[
        str | None,
        Field(
            default=None,
            description="Limit the resources operated on by an endpoint or when used with a multiple-GET endpoint, return only the subset of resources that match the filter. The filter grammar is a subset of OData 4.0.  NOTE: The filter query parameter must use [URL encoding](https://en.wikipedia.org/wiki/URL_encoding). Most clients do this automatically with inputs provided to them specifically as query parameters. Encoding must be done manually for any query parameters provided as part of the URL.   The reserved characters `!` `#` `$` `&` `'` `(` `)` `*` `+` `,` `/` `:` `;` `=` `?` `@` `[` `]` must be encoded with percent encoded equivalents. Device IDs contain a `+`, which must be encoded as `%2B`.   For example: the value `P06760-B21+2M212504P8` must be encoded as `P06760-B21%2B2M212504P8` when it is used in a query parameter.  | CLASS     |  EXAMPLES                                          | |-----------|----------------------------------------------------| | Types     | integer, decimal, timestamp, string, boolean, null | | Operations| eq, ne, gt, ge, lt, le, in                         | | Logic     | and, or, not                                       |  Group compliance can be filtered by:   - bundleId   - complianceCategory   - complianceState   - createdAt   - generation   - productId   - remediation   - score   - updatedAt   The following examples are not an exhaustive list of all possible filtering options.",
        ),
    ] = None,
) -> Any:
    path = f"/compute-ops-mgmt/v1/groups/{path_seg(group_id)}/compliance"
    query_params: dict[str, Any] = {}
    if filter is not None:
        query_params["filter"] = filter
    return await greenlake_request(
        ctx,
        "GET",
        path,
        query_params=query_params or None,
    )


@tool(
    name="greenlake_get_compute_ops_mgmt_v1_groups_group_id_compliance_compliance_id",
    description="GET /compute-ops-mgmt/v1/groups/{group-id}/compliance/{compliance-id}\n\nget_v1_compliance_by_compliance_id\n\nGet a device compliance by compliance Id",
    capability=Capability.READ,
)
async def greenlake_get_compute_ops_mgmt_v1_groups_group_id_compliance_compliance_id(
    ctx: Context,
    group_id: Annotated[str, Field(description="path parameter 'group-id'")],
    compliance_id: Annotated[str, Field(description="path parameter 'compliance-id'")],
) -> Any:
    path = f"/compute-ops-mgmt/v1/groups/{path_seg(group_id)}/compliance/{path_seg(compliance_id)}"
    return await greenlake_request(
        ctx,
        "GET",
        path,
    )


@tool(
    name="greenlake_get_compute_ops_mgmt_v1_groups_group_id_devices",
    description="GET /compute-ops-mgmt/v1/groups/{group-id}/devices\n\nget_v1_group_devices\n\nList all devices in a group",
    capability=Capability.READ,
)
async def greenlake_get_compute_ops_mgmt_v1_groups_group_id_devices(
    ctx: Context,
    group_id: Annotated[str, Field(description="path parameter 'group-id'")],
    filter: Annotated[
        str | None,
        Field(
            default=None,
            description="Limit the resources operated on by an endpoint or when used with a multiple-GET endpoint, return only the subset of resources that match the filter. The filter grammar is a subset of OData 4.0.  NOTE: The filter query parameter must use [URL encoding](https://en.wikipedia.org/wiki/URL_encoding). Most clients do this automatically with inputs provided to them specifically as query parameters. Encoding must be done manually for any query parameters provided as part of the URL.   The reserved characters `!` `#` `$` `&` `'` `(` `)` `*` `+` `,` `/` `:` `;` `=` `?` `@` `[` `]` must be encoded with percent encoded equivalents. Device IDs contain a `+`, which must be encoded as `%2B`.   For example: the value `P06760-B21+2M212504P8` must be encoded as `P06760-B21%2B2M212504P8` when it is used in a query parameter.  | CLASS     |  EXAMPLES                                          | |-----------|----------------------------------------------------| | Types     | integer, decimal, timestamp, string, boolean, null | | Operations| eq, ne, gt, ge, lt, le, in                         | | Logic     | and, or, not                                       |  Devices in a group can be filtered by:   - eTag   - groupId   - overallSecurityStatus   - productId   - serial   - subscriptionState   - subscriptionTier   The following examples are not an exhaustive list of all possible filtering options.",
        ),
    ] = None,
) -> Any:
    path = f"/compute-ops-mgmt/v1/groups/{path_seg(group_id)}/devices"
    query_params: dict[str, Any] = {}
    if filter is not None:
        query_params["filter"] = filter
    return await greenlake_request(
        ctx,
        "GET",
        path,
        query_params=query_params or None,
    )


@tool(
    name="greenlake_get_compute_ops_mgmt_v1_groups_group_id_external_storage_compliance",
    description="GET /compute-ops-mgmt/v1/groups/{group-id}/external-storage-compliance\n\nget_v1_group_external_storage_compliance\n\nGet external storage compliance",
    capability=Capability.READ,
)
async def greenlake_get_compute_ops_mgmt_v1_groups_group_id_external_storage_compliance(
    ctx: Context,
    group_id: Annotated[str, Field(description="path parameter 'group-id'")],
) -> Any:
    path = f"/compute-ops-mgmt/v1/groups/{path_seg(group_id)}/external-storage-compliance"
    return await greenlake_request(
        ctx,
        "GET",
        path,
    )


@tool(
    name="greenlake_patch_compute_ops_mgmt_v1_groups_group_id",
    description="PATCH /compute-ops-mgmt/v1/groups/{group-id}\n\npatch_v1_group_by_id\n\nPatch a group",
    capability=Capability.WRITE,
)
async def greenlake_patch_compute_ops_mgmt_v1_groups_group_id(
    ctx: Context,
    group_id: Annotated[str, Field(description="path parameter 'group-id'")],
    Content_Type: Annotated[
        str,
        Field(
            description="Content-Type header must designate 'application/merge-patch+json' in order for the request to be performed."
        ),
    ],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    path = f"/compute-ops-mgmt/v1/groups/{path_seg(group_id)}"
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
    name="greenlake_post_compute_ops_mgmt_v1_groups",
    description="POST /compute-ops-mgmt/v1/groups\n\ncreate_v1_group\n\nCreate a group",
    capability=Capability.WRITE,
)
async def greenlake_post_compute_ops_mgmt_v1_groups(
    ctx: Context,
    Content_Type: Annotated[
        str,
        Field(
            description="Content-Type header must designate 'application/json' in order for the request to be performed."
        ),
    ],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    header_params: dict[str, str] = {}
    if Content_Type is not None:
        header_params["Content-Type"] = str(Content_Type)
    return await greenlake_request(
        ctx,
        "POST",
        "/compute-ops-mgmt/v1/groups",
        header_params=header_params or None,
        body=body,
    )


@tool(
    name="greenlake_post_compute_ops_mgmt_v1_groups_group_id_devices",
    description="POST /compute-ops-mgmt/v1/groups/{group-id}/devices\n\nassign_v1_group_devices\n\nAssign device(s) to a group",
    capability=Capability.WRITE,
)
async def greenlake_post_compute_ops_mgmt_v1_groups_group_id_devices(
    ctx: Context,
    group_id: Annotated[str, Field(description="path parameter 'group-id'")],
    Content_Type: Annotated[
        str,
        Field(
            description="Content-Type header must designate 'application/json' in order for the request to be performed."
        ),
    ],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    path = f"/compute-ops-mgmt/v1/groups/{path_seg(group_id)}/devices"
    header_params: dict[str, str] = {}
    if Content_Type is not None:
        header_params["Content-Type"] = str(Content_Type)
    return await greenlake_request(
        ctx,
        "POST",
        path,
        header_params=header_params or None,
        body=body,
    )


@tool(
    name="greenlake_post_compute_ops_mgmt_v1_groups_group_id_devices_unassign",
    description="POST /compute-ops-mgmt/v1/groups/{group-id}/devices/unassign\n\nunassign_v1_group_devices\n\nUnassign device(s) from a group",
    capability=Capability.WRITE,
)
async def greenlake_post_compute_ops_mgmt_v1_groups_group_id_devices_unassign(
    ctx: Context,
    group_id: Annotated[str, Field(description="path parameter 'group-id'")],
    force: Annotated[
        bool | None,
        Field(
            default=None,
            description="If set to `true`, all devices will be unassigned from the group specified by the `group-id`. When this is `true`, do not provide a request body.",
        ),
    ] = None,
    reset_subsystems: Annotated[
        list[str] | None,
        Field(
            default=None,
            description='After the device is removed from its group, this option initiates a job to factory reset the specified Redfish subsystem(s).  This option is only valid for DIRECT_CONNECT_SERVER devices and "BIOS" is the only supported subsystem.',
        ),
    ] = None,
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request body")] = None,
) -> Any:
    path = f"/compute-ops-mgmt/v1/groups/{path_seg(group_id)}/devices/unassign"
    query_params: dict[str, Any] = {}
    if force is not None:
        query_params["force"] = force
    if reset_subsystems is not None:
        query_params["reset-subsystems"] = reset_subsystems
    return await greenlake_request(
        ctx,
        "POST",
        path,
        query_params=query_params or None,
        body=body,
    )
