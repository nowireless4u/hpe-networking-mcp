"""Generated GreenLake tools — DO NOT EDIT BY HAND.

Generated from the vendored spec ``vendor/greenlake/compute-ops-mgmt.json`` by the
maintainer-local GreenLake generator. These modules are committed and are the
runtime source of truth; regeneration is a release-time maintainer workflow
(the generator is intentionally not committed — see ``.gitignore``).

Service: ``compute-ops-mgmt``   Tag: ``servers_v1beta2``   Operations: 17
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
    name="greenlake_delete_compute_ops_mgmt_v1beta2_servers_id",
    description="DELETE /compute-ops-mgmt/v1beta2/servers/{id}\n\ndelete_v1beta2_server_by_id\n\nDelete a credential based server",
    capability=Capability.WRITE_DELETE,
)
async def greenlake_delete_compute_ops_mgmt_v1beta2_servers_id(
    ctx: Context,
    id: Annotated[str, Field(description="Unique Server identifier")],
) -> Any:
    path = f"/compute-ops-mgmt/v1beta2/servers/{path_seg(id)}"
    return await greenlake_request(
        ctx,
        "DELETE",
        path,
    )


@tool(
    name="greenlake_get_compute_ops_mgmt_v1beta2_servers",
    description="GET /compute-ops-mgmt/v1beta2/servers\n\nget_v1beta2_servers\n\nList all servers",
    capability=Capability.READ,
)
async def greenlake_get_compute_ops_mgmt_v1beta2_servers(
    ctx: Context,
    offset: Annotated[
        int | None, Field(default=None, description="Zero-based resource offset to start the response from")
    ] = None,
    limit: Annotated[int | None, Field(default=None, description="The maximum number of records to return.")] = None,
    filter: Annotated[
        str | None,
        Field(
            default=None,
            description="Limit the resources operated on by an endpoint or when used with a multiple-GET endpoint, return only the subset of resources that match the filter. The filter grammar is a subset of OData 4.0.  NOTE: The filter query parameter must use [URL encoding](https://en.wikipedia.org/wiki/URL_encoding). Most clients do this automatically with inputs provided to them specifically as query parameters. Encoding must be done manually for any query parameters provided as part of the URL.   The reserved characters `!` `#` `$` `&` `'` `(` `)` `*` `+` `,` `/` `:` `;` `=` `?` `@` `[` `]` must be encoded with percent encoded equivalents. Server IDs contain a `+`, which must be encoded as `%2B`.   For example: the value `P06760-B21+2M212504P8` must be encoded as `P06760-B21%2B2M212504P8` when it is used in a query parameter.  | CLASS     |  EXAMPLES                                          | |-----------|----------------------------------------------------| | Types     | integer, decimal, timestamp, string, boolean, null | | Operations| eq, ne, gt, ge, lt, le, in                         | | Logic     | and, or, not                                       |  Servers can be filtered by:   - biosFamily   - createdAt   - firmwareBundleUri   - hardware and all nested properties   - host and all nested properties   - id   - name †   - oneview and all nested properties   - platformFamily   - processorVendor   - resourceUri   - state and all nested properties  † When searching for a server using the `name` filter, you must supply the serial number of the server, not the hostname.  To filter by hostname use `host/hostname` instead of `name`  The following examples are not an exhaustive list of all possible filtering options.",
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
    header_params: dict[str, str] = {}
    if Tenant_Acid is not None:
        header_params["Tenant-Acid"] = str(Tenant_Acid)
    return await greenlake_request(
        ctx,
        "GET",
        "/compute-ops-mgmt/v1beta2/servers",
        query_params=query_params or None,
        header_params=header_params or None,
    )


@tool(
    name="greenlake_get_compute_ops_mgmt_v1beta2_servers_id",
    description="GET /compute-ops-mgmt/v1beta2/servers/{id}\n\nget_v1beta2_server_by_id\n\nGet a server",
    capability=Capability.READ,
)
async def greenlake_get_compute_ops_mgmt_v1beta2_servers_id(
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
    path = f"/compute-ops-mgmt/v1beta2/servers/{path_seg(id)}"
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
    name="greenlake_get_compute_ops_mgmt_v1beta2_servers_id_alerts",
    description="GET /compute-ops-mgmt/v1beta2/servers/{id}/alerts\n\nget_v1beta2_server_alerts\n\nList all alerts for a server",
    capability=Capability.READ,
)
async def greenlake_get_compute_ops_mgmt_v1beta2_servers_id_alerts(
    ctx: Context,
    id: Annotated[str, Field(description="Unique Server identifier")],
    offset: Annotated[
        int | None, Field(default=None, description="Zero-based resource offset to start the response from")
    ] = None,
    limit: Annotated[int | None, Field(default=None, description="The maximum number of records to return.")] = None,
    filter: Annotated[
        str | None,
        Field(
            default=None,
            description="Limit the resources operated on by an endpoint or when used with a multiple-GET endpoint, return only the subset of resources that match the filter. The filter grammar is a subset of OData 4.0.  NOTE: The filter query parameter must use [URL encoding](https://en.wikipedia.org/wiki/URL_encoding). Most clients do this automatically with inputs provided to them specifically as query parameters. Encoding must be done manually for any query parameters provided as part of the URL.   The reserved characters `!` `#` `$` `&` `'` `(` `)` `*` `+` `,` `/` `:` `;` `=` `?` `@` `[` `]` must be encoded with percent encoded equivalents. Server IDs contain a `+`, which must be encoded as `%2B`.   For example: the value `P06760-B21+2M212504P8` must be encoded as `P06760-B21%2B2M212504P8` when it is used in a query parameter.  | CLASS     |  EXAMPLES                                          | |-----------|----------------------------------------------------| | Types     | integer, decimal, timestamp, string, boolean, null | | Operations| eq, ne, gt, ge, lt, le, in                         | | Logic     | and, or, not                                       |  Servers can be filtered by:   - biosFamily   - createdAt   - firmwareBundleUri   - hardware and all nested properties   - host and all nested properties   - id   - name †   - oneview and all nested properties   - platformFamily   - processorVendor   - resourceUri   - state and all nested properties  † When searching for a server using the `name` filter, you must supply the serial number of the server, not the hostname.  To filter by hostname use `host/hostname` instead of `name`  The following examples are not an exhaustive list of all possible filtering options.",
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
    path = f"/compute-ops-mgmt/v1beta2/servers/{path_seg(id)}/alerts"
    query_params: dict[str, Any] = {}
    if offset is not None:
        query_params["offset"] = offset
    if limit is not None:
        query_params["limit"] = limit
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
    name="greenlake_get_compute_ops_mgmt_v1beta2_servers_id_external_storage_details",
    description="GET /compute-ops-mgmt/v1beta2/servers/{id}/external-storage-details\n\nget_v1beta2_server_external_storage_details\n\nGet external storage details",
    capability=Capability.READ,
)
async def greenlake_get_compute_ops_mgmt_v1beta2_servers_id_external_storage_details(
    ctx: Context,
    id: Annotated[str, Field(description="Unique server identifier")],
    Tenant_Acid: Annotated[
        str | None,
        Field(
            default=None,
            description="Tenant-Acid header can be used by an MSP workspace to make API calls on behalf of their tenant by specifying the tenant's application customer ID.  In order to make such an API call, the Bearer token must belong to an MSP workspace and this header value must be the application customer ID of a tenant within the MSP workspace. Use the `/compute-ops-mgmt/v1beta1/accounts` API to determine the application customer IDs for your tenant accounts.",
        ),
    ] = None,
) -> Any:
    path = f"/compute-ops-mgmt/v1beta2/servers/{path_seg(id)}/external-storage-details"
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
    name="greenlake_get_compute_ops_mgmt_v1beta2_servers_id_inventory",
    description="GET /compute-ops-mgmt/v1beta2/servers/{id}/inventory\n\nget_v1beta2_server_inventory\n\nList inventories for a server",
    capability=Capability.READ,
)
async def greenlake_get_compute_ops_mgmt_v1beta2_servers_id_inventory(
    ctx: Context,
    id: Annotated[str, Field(description="Unique Server identifier")],
    Tenant_Acid: Annotated[
        str | None,
        Field(
            default=None,
            description="Tenant-Acid header can be used by an MSP workspace to make API calls on behalf of their tenant by specifying the tenant's application customer ID.  In order to make such an API call, the Bearer token must belong to an MSP workspace and this header value must be the application customer ID of a tenant within the MSP workspace. Use the `/compute-ops-mgmt/v1beta1/accounts` API to determine the application customer IDs for your tenant accounts.",
        ),
    ] = None,
) -> Any:
    path = f"/compute-ops-mgmt/v1beta2/servers/{path_seg(id)}/inventory"
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
    name="greenlake_get_compute_ops_mgmt_v1beta2_servers_id_notifications",
    description="GET /compute-ops-mgmt/v1beta2/servers/{id}/notifications\n\nget_v1beta2_server_notifications\n\nGet the event and health notification status for a server",
    capability=Capability.READ,
)
async def greenlake_get_compute_ops_mgmt_v1beta2_servers_id_notifications(
    ctx: Context,
    id: Annotated[str, Field(description="path parameter 'id'")],
) -> Any:
    path = f"/compute-ops-mgmt/v1beta2/servers/{path_seg(id)}/notifications"
    return await greenlake_request(
        ctx,
        "GET",
        path,
    )


@tool(
    name="greenlake_get_compute_ops_mgmt_v1beta2_servers_id_raw_inventory",
    description="GET /compute-ops-mgmt/v1beta2/servers/{id}/raw-inventory\n\nget_v1beta2_server_raw_inventory\n\nList raw inventories for a server",
    capability=Capability.READ,
)
async def greenlake_get_compute_ops_mgmt_v1beta2_servers_id_raw_inventory(
    ctx: Context,
    id: Annotated[str, Field(description="Unique Server identifier")],
    Tenant_Acid: Annotated[
        str | None,
        Field(
            default=None,
            description="Tenant-Acid header can be used by an MSP workspace to make API calls on behalf of their tenant by specifying the tenant's application customer ID.  In order to make such an API call, the Bearer token must belong to an MSP workspace and this header value must be the application customer ID of a tenant within the MSP workspace. Use the `/compute-ops-mgmt/v1beta1/accounts` API to determine the application customer IDs for your tenant accounts.",
        ),
    ] = None,
) -> Any:
    path = f"/compute-ops-mgmt/v1beta2/servers/{path_seg(id)}/raw-inventory"
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
    name="greenlake_get_compute_ops_mgmt_v1beta2_servers_id_security_parameters",
    description="GET /compute-ops-mgmt/v1beta2/servers/{id}/security-parameters\n\nget_v1beta2_server_security_parameters\n\nGet security parameters for a server",
    capability=Capability.READ,
)
async def greenlake_get_compute_ops_mgmt_v1beta2_servers_id_security_parameters(
    ctx: Context,
    id: Annotated[str, Field(description="Unique Server identifier")],
    Tenant_Acid: Annotated[
        str | None,
        Field(
            default=None,
            description="Tenant-Acid header can be used by an MSP workspace to make API calls on behalf of their tenant by specifying the tenant's application customer ID.  In order to make such an API call, the Bearer token must belong to an MSP workspace and this header value must be the application customer ID of a tenant within the MSP workspace. Use the `/compute-ops-mgmt/v1beta1/accounts` API to determine the application customer IDs for your tenant accounts.",
        ),
    ] = None,
) -> Any:
    path = f"/compute-ops-mgmt/v1beta2/servers/{path_seg(id)}/security-parameters"
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
    name="greenlake_get_compute_ops_mgmt_v1beta2_servers_id_tor_port_mappings",
    description="GET /compute-ops-mgmt/v1beta2/servers/{id}/tor-port-mappings\n\nget_v1beta2_server_network_connectivity\n\nList of adapter to switch port mappings for a server",
    capability=Capability.READ,
)
async def greenlake_get_compute_ops_mgmt_v1beta2_servers_id_tor_port_mappings(
    ctx: Context,
    id: Annotated[str, Field(description="Unique Server identifier")],
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
    path = f"/compute-ops-mgmt/v1beta2/servers/{path_seg(id)}/tor-port-mappings"
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
        path,
        query_params=query_params or None,
        header_params=header_params or None,
    )


@tool(
    name="greenlake_patch_compute_ops_mgmt_v1beta2_servers",
    description="PATCH /compute-ops-mgmt/v1beta2/servers\n\npatch_v1beta2_servers_by_ids\n\nPatch multiple servers",
    capability=Capability.WRITE,
)
async def greenlake_patch_compute_ops_mgmt_v1beta2_servers(
    ctx: Context,
    id: Annotated[list[str], Field(description="query parameter 'id'")],
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
    query_params: dict[str, Any] = {}
    if id is not None:
        query_params["id"] = id
    header_params: dict[str, str] = {}
    if Content_Type is not None:
        header_params["Content-Type"] = str(Content_Type)
    if Tenant_Acid is not None:
        header_params["Tenant-Acid"] = str(Tenant_Acid)
    return await greenlake_request(
        ctx,
        "PATCH",
        "/compute-ops-mgmt/v1beta2/servers",
        query_params=query_params or None,
        header_params=header_params or None,
        body=body,
    )


@tool(
    name="greenlake_patch_compute_ops_mgmt_v1beta2_servers_id",
    description="PATCH /compute-ops-mgmt/v1beta2/servers/{id}\n\npatch_v1beta2_server_by_id\n\nPatch a server",
    capability=Capability.WRITE,
)
async def greenlake_patch_compute_ops_mgmt_v1beta2_servers_id(
    ctx: Context,
    id: Annotated[str, Field(description="Unique Server identifier")],
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
    path = f"/compute-ops-mgmt/v1beta2/servers/{path_seg(id)}"
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
    name="greenlake_post_compute_ops_mgmt_v1beta2_servers",
    description="POST /compute-ops-mgmt/v1beta2/servers\n\npost_v1beta2_server\n\nCreate credential based server",
    capability=Capability.WRITE,
)
async def greenlake_post_compute_ops_mgmt_v1beta2_servers(
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
        "/compute-ops-mgmt/v1beta2/servers",
        header_params=header_params or None,
        body=body,
    )


@tool(
    name="greenlake_post_compute_ops_mgmt_v1beta2_servers_id_analyze_os_install",
    description="POST /compute-ops-mgmt/v1beta2/servers/{id}/analyze-os-install\n\npost_v1beta2_analyze_os_install\n\nAnalyze server configuration for operating system installation",
    capability=Capability.WRITE,
)
async def greenlake_post_compute_ops_mgmt_v1beta2_servers_id_analyze_os_install(
    ctx: Context,
    id: Annotated[str, Field(description="Unique Server identifier")],
    Tenant_Acid: Annotated[
        str | None,
        Field(
            default=None,
            description="Tenant-Acid header can be used by an MSP workspace to make API calls on behalf of their tenant by specifying the tenant's application customer ID.  In order to make such an API call, the Bearer token must belong to an MSP workspace and this header value must be the application customer ID of a tenant within the MSP workspace. Use the `/compute-ops-mgmt/v1beta1/accounts` API to determine the application customer IDs for your tenant accounts.",
        ),
    ] = None,
) -> Any:
    path = f"/compute-ops-mgmt/v1beta2/servers/{path_seg(id)}/analyze-os-install"
    header_params: dict[str, str] = {}
    if Tenant_Acid is not None:
        header_params["Tenant-Acid"] = str(Tenant_Acid)
    return await greenlake_request(
        ctx,
        "POST",
        path,
        header_params=header_params or None,
    )


@tool(
    name="greenlake_post_compute_ops_mgmt_v1beta2_servers_id_clear_alert",
    description="POST /compute-ops-mgmt/v1beta2/servers/{id}/clear-alert\n\nclear_v1beta2_software_alerts\n\nClear power utilization alerts for a server",
    capability=Capability.WRITE,
)
async def greenlake_post_compute_ops_mgmt_v1beta2_servers_id_clear_alert(
    ctx: Context,
    id: Annotated[str, Field(description="Unique Server identifier")],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
    Tenant_Acid: Annotated[
        str | None,
        Field(
            default=None,
            description="Tenant-Acid header can be used by an MSP workspace to make API calls on behalf of their tenant by specifying the tenant's application customer ID.  In order to make such an API call, the Bearer token must belong to an MSP workspace and this header value must be the application customer ID of a tenant within the MSP workspace. Use the `/compute-ops-mgmt/v1beta1/accounts` API to determine the application customer IDs for your tenant accounts.",
        ),
    ] = None,
) -> Any:
    path = f"/compute-ops-mgmt/v1beta2/servers/{path_seg(id)}/clear-alert"
    header_params: dict[str, str] = {}
    if Tenant_Acid is not None:
        header_params["Tenant-Acid"] = str(Tenant_Acid)
    return await greenlake_request(
        ctx,
        "POST",
        path,
        header_params=header_params or None,
        body=body,
    )


@tool(
    name="greenlake_post_compute_ops_mgmt_v1beta2_servers_id_inventory",
    description="POST /compute-ops-mgmt/v1beta2/servers/{id}/inventory\n\npost_v1beta2_subset_server_inventory\n\nList subset of a Server Inventory",
    capability=Capability.WRITE,
)
async def greenlake_post_compute_ops_mgmt_v1beta2_servers_id_inventory(
    ctx: Context,
    id: Annotated[str, Field(description="Unique Server identifier")],
    format: Annotated[str, Field(description="Format for subset inventory response")],
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
    path = f"/compute-ops-mgmt/v1beta2/servers/{path_seg(id)}/inventory"
    query_params: dict[str, Any] = {}
    if format is not None:
        query_params["format"] = format
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


@tool(
    name="greenlake_put_compute_ops_mgmt_v1beta2_servers_id_notifications",
    description="PUT /compute-ops-mgmt/v1beta2/servers/{id}/notifications\n\nupdate_v1beta2_server_notifications\n\nUpdate event and health notifications for a server",
    capability=Capability.WRITE,
)
async def greenlake_put_compute_ops_mgmt_v1beta2_servers_id_notifications(
    ctx: Context,
    id: Annotated[str, Field(description="path parameter 'id'")],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    path = f"/compute-ops-mgmt/v1beta2/servers/{path_seg(id)}/notifications"
    return await greenlake_request(
        ctx,
        "PUT",
        path,
        body=body,
    )
