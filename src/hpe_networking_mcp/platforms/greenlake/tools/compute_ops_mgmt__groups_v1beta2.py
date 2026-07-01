"""Generated GreenLake tools — DO NOT EDIT BY HAND.

Generated from the vendored spec ``vendor/greenlake/compute-ops-mgmt.json`` by the
maintainer-local GreenLake generator. These modules are committed and are the
runtime source of truth; regeneration is a release-time maintainer workflow
(the generator is intentionally not committed — see ``.gitignore``).

Service: ``compute-ops-mgmt``   Tag: ``groups_v1beta2``   Operations: 14
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
    name="greenlake_delete_compute_ops_v1beta2_groups_group_id",
    description="DELETE /compute-ops/v1beta2/groups/{group-id}\n\ndelete_v1beta2_group_by_id\n\nDelete a group",
    capability=Capability.WRITE_DELETE,
)
async def greenlake_delete_compute_ops_v1beta2_groups_group_id(
    ctx: Context,
    group_id: Annotated[str, Field(description="path parameter 'group-id'")],
    force: Annotated[bool | None, Field(default=None, description="query parameter 'force'")] = None,
    Tenant_Acid: Annotated[
        str | None,
        Field(
            default=None,
            description="Tenant-Acid header can be used by an MSP workspace to make API calls on behalf of their tenant by specifying the tenant's application customer ID.  In order to make such an API call, the Bearer token must belong to an MSP workspace and this header value must be the application customer ID of a tenant within the MSP workspace. Use the `/compute-ops-mgmt/v1beta1/accounts` API to determine the application customer IDs for your tenant accounts.",
        ),
    ] = None,
) -> Any:
    path = f"/compute-ops/v1beta2/groups/{path_seg(group_id)}"
    query_params: dict[str, Any] = {}
    if force is not None:
        query_params["force"] = force
    header_params: dict[str, str] = {}
    if Tenant_Acid is not None:
        header_params["Tenant-Acid"] = str(Tenant_Acid)
    return await greenlake_request(
        ctx,
        "DELETE",
        path,
        query_params=query_params or None,
        header_params=header_params or None,
    )


@tool(
    name="greenlake_delete_compute_ops_v1beta2_groups_group_id_devices",
    description="DELETE /compute-ops/v1beta2/groups/{group-id}/devices\n\nunassign_v1beta2_group_devices\n\nBulk unassign devices from a group",
    capability=Capability.WRITE_DELETE,
)
async def greenlake_delete_compute_ops_v1beta2_groups_group_id_devices(
    ctx: Context,
    group_id: Annotated[str, Field(description="path parameter 'group-id'")],
    id: Annotated[list[str] | None, Field(default=None, description="query parameter 'id'")] = None,
    force: Annotated[bool | None, Field(default=None, description="query parameter 'force'")] = None,
    reset_subsystems: Annotated[
        list[str] | None,
        Field(
            default=None,
            description='After the device is removed from its group, this option initiates a job to factory reset the specified Redfish subsystem(s).  This option is only valid for servers and "BIOS" is the only supported subsystem.',
        ),
    ] = None,
    filter: Annotated[
        str | None,
        Field(
            default=None,
            description="Limit the resources operated on by an endpoint or when used with a multiple-GET endpoint, return only the subset of resources that match the filter. The filter grammar is a subset of OData 4.0.  NOTE: The filter query parameter must use [URL encoding](https://en.wikipedia.org/wiki/URL_encoding). Most clients do this automatically with inputs provided to them specifically as query parameters. Encoding must be done manually for any query parameters provided as part of the URL.   The reserved characters `!` `#` `$` `&` `'` `(` `)` `*` `+` `,` `/` `:` `;` `=` `?` `@` `[` `]` must be encoded with percent encoded equivalents. Server IDs contain a `+`, which must be encoded as `%2B`.   For example: the value `P06760-B21+2M212504P8` must be encoded as `P06760-B21%2B2M212504P8` when it is used in a query parameter.  | CLASS     |  EXAMPLES                                          | |-----------|----------------------------------------------------| | Types     | integer, decimal, timestamp, string, boolean, null | | Operations| eq, ne, gt, ge, lt, le, in                         | | Logic     | and, or, not                                       |  Groups can be filtered by:   - autoAddServerTags   - autoFwUpdateOnAdd   - createdAt   - description   - generation   - groupComplianceStatus   - id   - name   - platformFamily   - serverPolicies   - serverSettingsUris   - updatedAt   The following examples are not an exhaustive list of all possible filtering options.",
        ),
    ] = None,
    Tenant_Acid: Annotated[
        str | None,
        Field(
            default=None,
            description="Tenant-Acid header can be used by an MSP workspace to make API calls on behalf of their tenant by specifying the tenant's application customer ID.  In order to make such an API call, the Bearer token must belong to an MSP workspace and this header value must be the application customer ID of a tenant within the MSP workspace. Use the `/compute-ops-mgmt/v1beta1/accounts` API to determine the application customer IDs for your tenant accounts.",
        ),
    ] = None,
) -> Any:
    path = f"/compute-ops/v1beta2/groups/{path_seg(group_id)}/devices"
    query_params: dict[str, Any] = {}
    if id is not None:
        query_params["id"] = id
    if force is not None:
        query_params["force"] = force
    if reset_subsystems is not None:
        query_params["reset-subsystems"] = reset_subsystems
    if filter is not None:
        query_params["filter"] = filter
    header_params: dict[str, str] = {}
    if Tenant_Acid is not None:
        header_params["Tenant-Acid"] = str(Tenant_Acid)
    return await greenlake_request(
        ctx,
        "DELETE",
        path,
        query_params=query_params or None,
        header_params=header_params or None,
    )


@tool(
    name="greenlake_delete_compute_ops_v1beta2_groups_group_id_devices_device_id",
    description="DELETE /compute-ops/v1beta2/groups/{group-id}/devices/{device-id}\n\nunassign_v1beta2_group_device_by_id\n\nUnassign a device from a group",
    capability=Capability.WRITE_DELETE,
)
async def greenlake_delete_compute_ops_v1beta2_groups_group_id_devices_device_id(
    ctx: Context,
    group_id: Annotated[str, Field(description="path parameter 'group-id'")],
    device_id: Annotated[str, Field(description="path parameter 'device-id'")],
    reset_subsystems: Annotated[
        list[str] | None,
        Field(
            default=None,
            description='After the device is removed from its group, this option initiates a job to factory reset the specified Redfish subsystem(s).  This option is only valid for servers and "BIOS" is the only supported subsystem.',
        ),
    ] = None,
    Tenant_Acid: Annotated[
        str | None,
        Field(
            default=None,
            description="Tenant-Acid header can be used by an MSP workspace to make API calls on behalf of their tenant by specifying the tenant's application customer ID.  In order to make such an API call, the Bearer token must belong to an MSP workspace and this header value must be the application customer ID of a tenant within the MSP workspace. Use the `/compute-ops-mgmt/v1beta1/accounts` API to determine the application customer IDs for your tenant accounts.",
        ),
    ] = None,
) -> Any:
    path = f"/compute-ops/v1beta2/groups/{path_seg(group_id)}/devices/{path_seg(device_id)}"
    query_params: dict[str, Any] = {}
    if reset_subsystems is not None:
        query_params["reset-subsystems"] = reset_subsystems
    header_params: dict[str, str] = {}
    if Tenant_Acid is not None:
        header_params["Tenant-Acid"] = str(Tenant_Acid)
    return await greenlake_request(
        ctx,
        "DELETE",
        path,
        query_params=query_params or None,
        header_params=header_params or None,
    )


@tool(
    name="greenlake_get_compute_ops_v1beta2_groups",
    description="GET /compute-ops/v1beta2/groups\n\nget_v1beta2_groups\n\nList all groups",
    capability=Capability.READ,
)
async def greenlake_get_compute_ops_v1beta2_groups(
    ctx: Context,
    offset: Annotated[
        int | None, Field(default=None, description="Zero-based resource offset to start the response from")
    ] = None,
    limit: Annotated[int | None, Field(default=None, description="The maximum number of records to return.")] = None,
    filter: Annotated[
        str | None,
        Field(
            default=None,
            description="Limit the resources operated on by an endpoint or when used with a multiple-GET endpoint, return only the subset of resources that match the filter. The filter grammar is a subset of OData 4.0.  NOTE: The filter query parameter must use [URL encoding](https://en.wikipedia.org/wiki/URL_encoding). Most clients do this automatically with inputs provided to them specifically as query parameters. Encoding must be done manually for any query parameters provided as part of the URL.   The reserved characters `!` `#` `$` `&` `'` `(` `)` `*` `+` `,` `/` `:` `;` `=` `?` `@` `[` `]` must be encoded with percent encoded equivalents. Server IDs contain a `+`, which must be encoded as `%2B`.   For example: the value `P06760-B21+2M212504P8` must be encoded as `P06760-B21%2B2M212504P8` when it is used in a query parameter.  | CLASS     |  EXAMPLES                                          | |-----------|----------------------------------------------------| | Types     | integer, decimal, timestamp, string, boolean, null | | Operations| eq, ne, gt, ge, lt, le, in                         | | Logic     | and, or, not                                       |  Groups can be filtered by:   - autoAddServerTags   - autoFwUpdateOnAdd   - createdAt   - description   - generation   - groupComplianceStatus   - id   - name   - platformFamily   - serverPolicies   - serverSettingsUris   - updatedAt   The following examples are not an exhaustive list of all possible filtering options.",
        ),
    ] = None,
    sort: Annotated[
        str | None,
        Field(
            default=None,
            description="The order in which to return the resources in the collection.  The value of the sort query parameter is a comma separated list of sort expressions.  Each sort expression is a property name optionally followed by a direction indicator asc (ascending) or desc  (descending).  The first sort expression in the list defines the primary sort order, the second defines the secondary sort order,  and so on. If a direciton indicator is omitted the default direction is ascending.",
        ),
    ] = None,
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
    if filter is not None:
        query_params["filter"] = filter
    if sort is not None:
        query_params["sort"] = sort
    header_params: dict[str, str] = {}
    if Tenant_Acid is not None:
        header_params["Tenant-Acid"] = str(Tenant_Acid)
    return await greenlake_request(
        ctx,
        "GET",
        "/compute-ops/v1beta2/groups",
        query_params=query_params or None,
        header_params=header_params or None,
    )


@tool(
    name="greenlake_get_compute_ops_v1beta2_groups_group_id",
    description="GET /compute-ops/v1beta2/groups/{group-id}\n\nget_v1beta2_group_by_id\n\nGet a group by ID",
    capability=Capability.READ,
)
async def greenlake_get_compute_ops_v1beta2_groups_group_id(
    ctx: Context,
    group_id: Annotated[str, Field(description="path parameter 'group-id'")],
    Tenant_Acid: Annotated[
        str | None,
        Field(
            default=None,
            description="Tenant-Acid header can be used by an MSP workspace to make API calls on behalf of their tenant by specifying the tenant's application customer ID.  In order to make such an API call, the Bearer token must belong to an MSP workspace and this header value must be the application customer ID of a tenant within the MSP workspace. Use the `/compute-ops-mgmt/v1beta1/accounts` API to determine the application customer IDs for your tenant accounts.",
        ),
    ] = None,
) -> Any:
    path = f"/compute-ops/v1beta2/groups/{path_seg(group_id)}"
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
    name="greenlake_get_compute_ops_v1beta2_groups_group_id_compliance",
    description="GET /compute-ops/v1beta2/groups/{group-id}/compliance\n\nget_v1beta2_group_devices_compliance\n\nList all devices compliance in a group",
    capability=Capability.READ,
)
async def greenlake_get_compute_ops_v1beta2_groups_group_id_compliance(
    ctx: Context,
    group_id: Annotated[str, Field(description="path parameter 'group-id'")],
    filter: Annotated[
        str | None,
        Field(
            default=None,
            description="Limit the resources operated on by an endpoint or when used with a multiple-GET endpoint, return only the subset of resources that match the filter. The filter grammar is a subset of OData 4.0.  NOTE: The filter query parameter must use [URL encoding](https://en.wikipedia.org/wiki/URL_encoding). Most clients do this automatically with inputs provided to them specifically as query parameters. Encoding must be done manually for any query parameters provided as part of the URL.   The reserved characters `!` `#` `$` `&` `'` `(` `)` `*` `+` `,` `/` `:` `;` `=` `?` `@` `[` `]` must be encoded with percent encoded equivalents. Server IDs contain a `+`, which must be encoded as `%2B`.   For example: the value `P06760-B21+2M212504P8` must be encoded as `P06760-B21%2B2M212504P8` when it is used in a query parameter.  | CLASS     |  EXAMPLES                                          | |-----------|----------------------------------------------------| | Types     | integer, decimal, timestamp, string, boolean, null | | Operations| eq, ne, gt, ge, lt, le, in                         | | Logic     | and, or, not                                       |  Groups can be filtered by:   - autoAddServerTags   - autoFwUpdateOnAdd   - createdAt   - description   - generation   - groupComplianceStatus   - id   - name   - platformFamily   - serverPolicies   - serverSettingsUris   - updatedAt   The following examples are not an exhaustive list of all possible filtering options.",
        ),
    ] = None,
    Tenant_Acid: Annotated[
        str | None,
        Field(
            default=None,
            description="Tenant-Acid header can be used by an MSP workspace to make API calls on behalf of their tenant by specifying the tenant's application customer ID.  In order to make such an API call, the Bearer token must belong to an MSP workspace and this header value must be the application customer ID of a tenant within the MSP workspace. Use the `/compute-ops-mgmt/v1beta1/accounts` API to determine the application customer IDs for your tenant accounts.",
        ),
    ] = None,
) -> Any:
    path = f"/compute-ops/v1beta2/groups/{path_seg(group_id)}/compliance"
    query_params: dict[str, Any] = {}
    if filter is not None:
        query_params["filter"] = filter
    header_params: dict[str, str] = {}
    if Tenant_Acid is not None:
        header_params["Tenant-Acid"] = str(Tenant_Acid)
    return await greenlake_request(
        ctx,
        "GET",
        path,
        query_params=query_params or None,
        header_params=header_params or None,
    )


@tool(
    name="greenlake_get_compute_ops_v1beta2_groups_group_id_compliance_compliance_id",
    description="GET /compute-ops/v1beta2/groups/{group-id}/compliance/{compliance-id}\n\nget_v1beta2_compliance_by_compliance_id\n\nGet a device compliance by compliance Id",
    capability=Capability.READ,
)
async def greenlake_get_compute_ops_v1beta2_groups_group_id_compliance_compliance_id(
    ctx: Context,
    group_id: Annotated[str, Field(description="path parameter 'group-id'")],
    compliance_id: Annotated[str, Field(description="path parameter 'compliance-id'")],
    Tenant_Acid: Annotated[
        str | None,
        Field(
            default=None,
            description="Tenant-Acid header can be used by an MSP workspace to make API calls on behalf of their tenant by specifying the tenant's application customer ID.  In order to make such an API call, the Bearer token must belong to an MSP workspace and this header value must be the application customer ID of a tenant within the MSP workspace. Use the `/compute-ops-mgmt/v1beta1/accounts` API to determine the application customer IDs for your tenant accounts.",
        ),
    ] = None,
) -> Any:
    path = f"/compute-ops/v1beta2/groups/{path_seg(group_id)}/compliance/{path_seg(compliance_id)}"
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
    name="greenlake_get_compute_ops_v1beta2_groups_group_id_devices",
    description="GET /compute-ops/v1beta2/groups/{group-id}/devices\n\nget_v1beta2_group_devices\n\nList all devices in a group",
    capability=Capability.READ,
)
async def greenlake_get_compute_ops_v1beta2_groups_group_id_devices(
    ctx: Context,
    group_id: Annotated[str, Field(description="path parameter 'group-id'")],
    filter: Annotated[
        str | None,
        Field(
            default=None,
            description="Limit the resources operated on by an endpoint or when used with a multiple-GET endpoint, return only the subset of resources that match the filter. The filter grammar is a subset of OData 4.0.  NOTE: The filter query parameter must use [URL encoding](https://en.wikipedia.org/wiki/URL_encoding). Most clients do this automatically with inputs provided to them specifically as query parameters. Encoding must be done manually for any query parameters provided as part of the URL.   The reserved characters `!` `#` `$` `&` `'` `(` `)` `*` `+` `,` `/` `:` `;` `=` `?` `@` `[` `]` must be encoded with percent encoded equivalents. Server IDs contain a `+`, which must be encoded as `%2B`.   For example: the value `P06760-B21+2M212504P8` must be encoded as `P06760-B21%2B2M212504P8` when it is used in a query parameter.  | CLASS     |  EXAMPLES                                          | |-----------|----------------------------------------------------| | Types     | integer, decimal, timestamp, string, boolean, null | | Operations| eq, ne, gt, ge, lt, le, in                         | | Logic     | and, or, not                                       |  Groups can be filtered by:   - autoAddServerTags   - autoFwUpdateOnAdd   - createdAt   - description   - generation   - groupComplianceStatus   - id   - name   - platformFamily   - serverPolicies   - serverSettingsUris   - updatedAt   The following examples are not an exhaustive list of all possible filtering options.",
        ),
    ] = None,
    Tenant_Acid: Annotated[
        str | None,
        Field(
            default=None,
            description="Tenant-Acid header can be used by an MSP workspace to make API calls on behalf of their tenant by specifying the tenant's application customer ID.  In order to make such an API call, the Bearer token must belong to an MSP workspace and this header value must be the application customer ID of a tenant within the MSP workspace. Use the `/compute-ops-mgmt/v1beta1/accounts` API to determine the application customer IDs for your tenant accounts.",
        ),
    ] = None,
) -> Any:
    path = f"/compute-ops/v1beta2/groups/{path_seg(group_id)}/devices"
    query_params: dict[str, Any] = {}
    if filter is not None:
        query_params["filter"] = filter
    header_params: dict[str, str] = {}
    if Tenant_Acid is not None:
        header_params["Tenant-Acid"] = str(Tenant_Acid)
    return await greenlake_request(
        ctx,
        "GET",
        path,
        query_params=query_params or None,
        header_params=header_params or None,
    )


@tool(
    name="greenlake_get_compute_ops_v1beta2_groups_group_id_external_storage_compliance",
    description="GET /compute-ops/v1beta2/groups/{group-id}/external-storage-compliance\n\nget_v1beta2_group_external_storage_compliance\n\nGet external storage compliance",
    capability=Capability.READ,
)
async def greenlake_get_compute_ops_v1beta2_groups_group_id_external_storage_compliance(
    ctx: Context,
    group_id: Annotated[str, Field(description="path parameter 'group-id'")],
    Tenant_Acid: Annotated[
        str | None,
        Field(
            default=None,
            description="Tenant-Acid header can be used by an MSP workspace to make API calls on behalf of their tenant by specifying the tenant's application customer ID.  In order to make such an API call, the Bearer token must belong to an MSP workspace and this header value must be the application customer ID of a tenant within the MSP workspace. Use the `/compute-ops-mgmt/v1beta1/accounts` API to determine the application customer IDs for your tenant accounts.",
        ),
    ] = None,
) -> Any:
    path = f"/compute-ops/v1beta2/groups/{path_seg(group_id)}/external-storage-compliance"
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
    name="greenlake_get_compute_ops_v1beta2_groups_group_id_ilo_settings_compliance",
    description="GET /compute-ops/v1beta2/groups/{group-id}/ilo-settings-compliance\n\nget_v1beta2_group_ilo_settings_compliance\n\nGet iLO Settings compliance",
    capability=Capability.READ,
)
async def greenlake_get_compute_ops_v1beta2_groups_group_id_ilo_settings_compliance(
    ctx: Context,
    group_id: Annotated[str, Field(description="path parameter 'group-id'")],
) -> Any:
    path = f"/compute-ops/v1beta2/groups/{path_seg(group_id)}/ilo-settings-compliance"
    return await greenlake_request(
        ctx,
        "GET",
        path,
    )


@tool(
    name="greenlake_get_compute_ops_v1beta2_groups_group_id_ilo_settings_compliance_ilo_settings_compliance_id",
    description="GET /compute-ops/v1beta2/groups/{group-id}/ilo-settings-compliance/{ilo-settings-compliance-id}\n\nget_v1beta2_ilo_settings_compliance_by_compliance_id\n\nGet a device iLO Settings compliance by iLO Settings compliance Id",
    capability=Capability.READ,
)
async def greenlake_get_compute_ops_v1beta2_groups_group_id_ilo_settings_compliance_ilo_settings_compliance_id(
    ctx: Context,
    group_id: Annotated[str, Field(description="path parameter 'group-id'")],
    ilo_settings_compliance_id: Annotated[str, Field(description="path parameter 'ilo-settings-compliance-id'")],
) -> Any:
    path = f"/compute-ops/v1beta2/groups/{path_seg(group_id)}/ilo-settings-compliance/{path_seg(ilo_settings_compliance_id)}"
    return await greenlake_request(
        ctx,
        "GET",
        path,
    )


@tool(
    name="greenlake_patch_compute_ops_v1beta2_groups_group_id",
    description="PATCH /compute-ops/v1beta2/groups/{group-id}\n\npatch_v1beta2_group_by_id\n\nPatch a group",
    capability=Capability.WRITE,
)
async def greenlake_patch_compute_ops_v1beta2_groups_group_id(
    ctx: Context,
    group_id: Annotated[str, Field(description="path parameter 'group-id'")],
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
    path = f"/compute-ops/v1beta2/groups/{path_seg(group_id)}"
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
    name="greenlake_post_compute_ops_v1beta2_groups",
    description="POST /compute-ops/v1beta2/groups\n\ncreate_v1beta2_group\n\nCreate a group",
    capability=Capability.WRITE,
)
async def greenlake_post_compute_ops_v1beta2_groups(
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
        "/compute-ops/v1beta2/groups",
        header_params=header_params or None,
        body=body,
    )


@tool(
    name="greenlake_post_compute_ops_v1beta2_groups_group_id_devices",
    description="POST /compute-ops/v1beta2/groups/{group-id}/devices\n\nassign_v1beta2_group_devices\n\nAssign a device to a group",
    capability=Capability.WRITE,
)
async def greenlake_post_compute_ops_v1beta2_groups_group_id_devices(
    ctx: Context,
    group_id: Annotated[str, Field(description="path parameter 'group-id'")],
    Content_Type: Annotated[
        str,
        Field(
            description="Content-Type header must designate 'application/json' in order for the request to be performed."
        ),
    ],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
    dry_run: Annotated[
        bool | None,
        Field(
            default=None,
            description="When set to `false`, servers will be assigned or moved to the group specified by `group-id` barring any errors.  When set to `true`, servers will not be assigned or moved to the specified group. This `dry-run` request will return useful information about the servers involved in the request, such as the latest eTags.",
        ),
    ] = None,
    Tenant_Acid: Annotated[
        str | None,
        Field(
            default=None,
            description="Tenant-Acid header can be used by an MSP workspace to make API calls on behalf of their tenant by specifying the tenant's application customer ID.  In order to make such an API call, the Bearer token must belong to an MSP workspace and this header value must be the application customer ID of a tenant within the MSP workspace. Use the `/compute-ops-mgmt/v1beta1/accounts` API to determine the application customer IDs for your tenant accounts.",
        ),
    ] = None,
) -> Any:
    path = f"/compute-ops/v1beta2/groups/{path_seg(group_id)}/devices"
    query_params: dict[str, Any] = {}
    if dry_run is not None:
        query_params["dry-run"] = dry_run
    header_params: dict[str, str] = {}
    if Content_Type is not None:
        header_params["Content-Type"] = str(Content_Type)
    if Tenant_Acid is not None:
        header_params["Tenant-Acid"] = str(Tenant_Acid)
    return await greenlake_request(
        ctx,
        "POST",
        path,
        query_params=query_params or None,
        header_params=header_params or None,
        body=body,
    )
