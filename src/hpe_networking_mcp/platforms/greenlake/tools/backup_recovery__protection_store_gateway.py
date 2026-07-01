"""Generated GreenLake tools — DO NOT EDIT BY HAND.

Generated from the vendored spec ``vendor/greenlake/backup-recovery.json`` by the
maintainer-local GreenLake generator. These modules are committed and are the
runtime source of truth; regeneration is a release-time maintainer workflow
(the generator is intentionally not committed — see ``.gitignore``).

Service: ``backup-recovery``   Tag: ``protection_store_gateway``   Operations: 20
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
    name="greenlake_delete_backup_recovery_v1beta1_protection_store_gateways_id",
    description="DELETE /backup-recovery/v1beta1/protection-store-gateways/{id}\n\nProtectionStoreGatewayDelete\n\nDeletes a Protection Store Gateway within DSCC",
    capability=Capability.WRITE_DELETE,
)
async def greenlake_delete_backup_recovery_v1beta1_protection_store_gateways_id(
    ctx: Context,
    id: Annotated[str, Field(description="The UUID of the object")],
    force: Annotated[
        bool | None,
        Field(default=None, description="Forces deletion of the Protection Store Gateway regardless of store data."),
    ] = None,
) -> Any:
    path = f"/backup-recovery/v1beta1/protection-store-gateways/{path_seg(id)}"
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
    name="greenlake_get_backup_recovery_v1beta1_protection_store_gateways",
    description="GET /backup-recovery/v1beta1/protection-store-gateways\n\nProtectionStoreGatewaysList\n\nGet a list of the Protection Store Gateways that are registered with DSCC",
    capability=Capability.READ,
)
async def greenlake_get_backup_recovery_v1beta1_protection_store_gateways(
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
            description="The *filter* query parameter is used to filter the set of resources returned in the response.  The returned set of resources will match the criteria in the filter query parameter.  A comparison compares a property name to a literal. The comparisons supported are the following:  - “eq” : Is a property equal to value. Valid for number, boolean and string properties - “gt” : Is a property greater than a value. Valid for number or string timestamp properties - “lt” : Is a property less than a value. Valid for number or string timestamp properties - “in” : Is a value in a property (that is an array of strings)  Filters are supported on following attributes:         - state - health/state - health/status  Examples:  - GET ./protection-store-gateways?filter=state eq'PSG_STATE_REGISTERING' - GET ./protection-store-gateways?filter=health/state eq 'PSG_HEALTH_STATE_UNKNOWN' - GET ./protection-store-gateways?filter=health/status eq 'PSG_HEALTH_STATUS_CONNECTED'",
        ),
    ] = None,
    sort: Annotated[
        str | None, Field(default=None, description="Comma separated list of properties defining the sort order")
    ] = None,
    select: Annotated[
        str | None,
        Field(
            default=None,
            description="The *select* query parameter is used to limit the properties returned in the GET response.  Multiple properties can be specified to be returned. The server will only return the set of properties requested by the client.  Example:  GET ./protection-store-gateways?select=displayName,state'",
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
        "/backup-recovery/v1beta1/protection-store-gateways",
        query_params=query_params or None,
    )


@tool(
    name="greenlake_get_backup_recovery_v1beta1_protection_store_gateways_id",
    description="GET /backup-recovery/v1beta1/protection-store-gateways/{id}\n\nProtectionStoreGatewayGetById\n\nGet details of a Protection Store Gateway within DSCC",
    capability=Capability.READ,
)
async def greenlake_get_backup_recovery_v1beta1_protection_store_gateways_id(
    ctx: Context,
    id: Annotated[str, Field(description="The UUID of the object")],
) -> Any:
    path = f"/backup-recovery/v1beta1/protection-store-gateways/{path_seg(id)}"
    return await greenlake_request(
        ctx,
        "GET",
        path,
    )


@tool(
    name="greenlake_patch_backup_recovery_v1beta1_protection_store_gateways_id",
    description="PATCH /backup-recovery/v1beta1/protection-store-gateways/{id}\n\nProtectionStoreGatewayUpdate\n\nModify the configuration of a Protection Store Gateway",
    capability=Capability.WRITE,
)
async def greenlake_patch_backup_recovery_v1beta1_protection_store_gateways_id(
    ctx: Context,
    id: Annotated[str, Field(description="The UUID of the object")],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    path = f"/backup-recovery/v1beta1/protection-store-gateways/{path_seg(id)}"
    return await greenlake_request(
        ctx,
        "PATCH",
        path,
        body=body,
    )


@tool(
    name="greenlake_post_backup_recovery_v1beta1_protection_store_gateway_sizer",
    description="POST /backup-recovery/v1beta1/protection-store-gateway-sizer\n\nProtectionStoreGatewaySize\n\nReturns the resource requirements that would be needed for a Protection Store Gateway.",
    capability=Capability.WRITE,
)
async def greenlake_post_backup_recovery_v1beta1_protection_store_gateway_sizer(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await greenlake_request(
        ctx,
        "POST",
        "/backup-recovery/v1beta1/protection-store-gateway-sizer",
        body=body,
    )


@tool(
    name="greenlake_post_backup_recovery_v1beta1_protection_store_gateways",
    description="POST /backup-recovery/v1beta1/protection-store-gateways\n\nProtectionStoreGatewayCreate\n\nCreate a new Protection Store Gateway within DSCC",
    capability=Capability.WRITE,
)
async def greenlake_post_backup_recovery_v1beta1_protection_store_gateways(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await greenlake_request(
        ctx,
        "POST",
        "/backup-recovery/v1beta1/protection-store-gateways",
        body=body,
    )


@tool(
    name="greenlake_post_backup_recovery_v1beta1_protection_store_gateways_id_console_user",
    description="POST /backup-recovery/v1beta1/protection-store-gateways/{id}/consoleUser\n\nProtectionStoreGatewayGetConsoleUser\n\nGets the credentials of a Protection Store Gateway console user",
    capability=Capability.WRITE,
)
async def greenlake_post_backup_recovery_v1beta1_protection_store_gateways_id_console_user(
    ctx: Context,
    id: Annotated[str, Field(description="The UUID of the object")],
) -> Any:
    path = f"/backup-recovery/v1beta1/protection-store-gateways/{path_seg(id)}/consoleUser"
    return await greenlake_request(
        ctx,
        "POST",
        path,
    )


@tool(
    name="greenlake_post_backup_recovery_v1beta1_protection_store_gateways_id_create_nic",
    description="POST /backup-recovery/v1beta1/protection-store-gateways/{id}/createNic\n\nProtectionStoreGatewayNicCreate\n\nCreates a network interface on the Protection Store Gateway",
    capability=Capability.WRITE,
)
async def greenlake_post_backup_recovery_v1beta1_protection_store_gateways_id_create_nic(
    ctx: Context,
    id: Annotated[str, Field(description="The UUID of the object")],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    path = f"/backup-recovery/v1beta1/protection-store-gateways/{path_seg(id)}/createNic"
    return await greenlake_request(
        ctx,
        "POST",
        path,
        body=body,
    )


@tool(
    name="greenlake_post_backup_recovery_v1beta1_protection_store_gateways_id_delete_nic",
    description="POST /backup-recovery/v1beta1/protection-store-gateways/{id}/deleteNic\n\nProtectionStoreGatewayNicDelete\n\nDeletes a network interface on the Protection Store Gateway",
    capability=Capability.WRITE,
)
async def greenlake_post_backup_recovery_v1beta1_protection_store_gateways_id_delete_nic(
    ctx: Context,
    id: Annotated[str, Field(description="The UUID of the object")],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    path = f"/backup-recovery/v1beta1/protection-store-gateways/{path_seg(id)}/deleteNic"
    return await greenlake_request(
        ctx,
        "POST",
        path,
        body=body,
    )


@tool(
    name="greenlake_post_backup_recovery_v1beta1_protection_store_gateways_id_generate_support_bundle",
    description="POST /backup-recovery/v1beta1/protection-store-gateways/{id}/generate-support-bundle\n\nProtectionStoreGatewayGenerateSupportBundle\n\nGenerates a support bundle",
    capability=Capability.WRITE,
)
async def greenlake_post_backup_recovery_v1beta1_protection_store_gateways_id_generate_support_bundle(
    ctx: Context,
    id: Annotated[str, Field(description="The UUID of the object")],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    path = f"/backup-recovery/v1beta1/protection-store-gateways/{path_seg(id)}/generate-support-bundle"
    return await greenlake_request(
        ctx,
        "POST",
        path,
        body=body,
    )


@tool(
    name="greenlake_post_backup_recovery_v1beta1_protection_store_gateways_id_ping",
    description="POST /backup-recovery/v1beta1/protection-store-gateways/{id}/ping\n\nProtectionStoreGatewayPing\n\nPing from the Protection Store Gateway",
    capability=Capability.WRITE,
)
async def greenlake_post_backup_recovery_v1beta1_protection_store_gateways_id_ping(
    ctx: Context,
    id: Annotated[str, Field(description="The UUID of the object")],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    path = f"/backup-recovery/v1beta1/protection-store-gateways/{path_seg(id)}/ping"
    return await greenlake_request(
        ctx,
        "POST",
        path,
        body=body,
    )


@tool(
    name="greenlake_post_backup_recovery_v1beta1_protection_store_gateways_id_power_on",
    description="POST /backup-recovery/v1beta1/protection-store-gateways/{id}/power-on\n\nProtectionStoreGatewayPowerOn\n\nPowers on the Protection Store Gateway",
    capability=Capability.WRITE,
)
async def greenlake_post_backup_recovery_v1beta1_protection_store_gateways_id_power_on(
    ctx: Context,
    id: Annotated[str, Field(description="The UUID of the object")],
) -> Any:
    path = f"/backup-recovery/v1beta1/protection-store-gateways/{path_seg(id)}/power-on"
    return await greenlake_request(
        ctx,
        "POST",
        path,
    )


@tool(
    name="greenlake_post_backup_recovery_v1beta1_protection_store_gateways_id_recover",
    description="POST /backup-recovery/v1beta1/protection-store-gateways/{id}/recover\n\nProtectionStoreGatewayRecover\n\nRecover a Protection Store Gateway within DSCC",
    capability=Capability.WRITE,
)
async def greenlake_post_backup_recovery_v1beta1_protection_store_gateways_id_recover(
    ctx: Context,
    id: Annotated[str, Field(description="The UUID of the object")],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
    force: Annotated[
        bool | None,
        Field(
            default=None,
            description="Forces recovery to be initiated even if the Protection Store Gateway is in a Connected state.",
        ),
    ] = None,
) -> Any:
    path = f"/backup-recovery/v1beta1/protection-store-gateways/{path_seg(id)}/recover"
    query_params: dict[str, Any] = {}
    if force is not None:
        query_params["force"] = force
    return await greenlake_request(
        ctx,
        "POST",
        path,
        query_params=query_params or None,
        body=body,
    )


@tool(
    name="greenlake_post_backup_recovery_v1beta1_protection_store_gateways_id_resize",
    description="POST /backup-recovery/v1beta1/protection-store-gateways/{id}/resize\n\nProtectionStoreGatewayStorage\n\nReconfigures the CPU, memory and storage requirements of the Protection Store Gateway.",
    capability=Capability.WRITE,
)
async def greenlake_post_backup_recovery_v1beta1_protection_store_gateways_id_resize(
    ctx: Context,
    id: Annotated[str, Field(description="The UUID of the object")],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    path = f"/backup-recovery/v1beta1/protection-store-gateways/{path_seg(id)}/resize"
    return await greenlake_request(
        ctx,
        "POST",
        path,
        body=body,
    )


@tool(
    name="greenlake_post_backup_recovery_v1beta1_protection_store_gateways_id_restart_guest_os",
    description="POST /backup-recovery/v1beta1/protection-store-gateways/{id}/restart-guest-os\n\nProtectionStoreGatewayRestartGuestOS\n\nRestarts the Protection Store Gateway",
    capability=Capability.WRITE,
)
async def greenlake_post_backup_recovery_v1beta1_protection_store_gateways_id_restart_guest_os(
    ctx: Context,
    id: Annotated[str, Field(description="The UUID of the object")],
) -> Any:
    path = f"/backup-recovery/v1beta1/protection-store-gateways/{path_seg(id)}/restart-guest-os"
    return await greenlake_request(
        ctx,
        "POST",
        path,
    )


@tool(
    name="greenlake_post_backup_recovery_v1beta1_protection_store_gateways_id_set_remote_support",
    description="POST /backup-recovery/v1beta1/protection-store-gateways/{id}/set-remote-support\n\nProtectionStoreGatewaySetRemoteSupport\n\nEnables remote support on the Protection Store Gateway",
    capability=Capability.WRITE,
)
async def greenlake_post_backup_recovery_v1beta1_protection_store_gateways_id_set_remote_support(
    ctx: Context,
    id: Annotated[str, Field(description="The UUID of the object")],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    path = f"/backup-recovery/v1beta1/protection-store-gateways/{path_seg(id)}/set-remote-support"
    return await greenlake_request(
        ctx,
        "POST",
        path,
        body=body,
    )


@tool(
    name="greenlake_post_backup_recovery_v1beta1_protection_store_gateways_id_shutdown_guest_os",
    description="POST /backup-recovery/v1beta1/protection-store-gateways/{id}/shutdown-guest-os\n\nProtectionStoreGatewayShutdownGuestOS\n\nShuts down the Protection Store Gateway",
    capability=Capability.WRITE,
)
async def greenlake_post_backup_recovery_v1beta1_protection_store_gateways_id_shutdown_guest_os(
    ctx: Context,
    id: Annotated[str, Field(description="The UUID of the object")],
    force: Annotated[bool | None, Field(default=None, description="Force option to forcefully shutdown")] = None,
) -> Any:
    path = f"/backup-recovery/v1beta1/protection-store-gateways/{path_seg(id)}/shutdown-guest-os"
    query_params: dict[str, Any] = {}
    if force is not None:
        query_params["force"] = force
    return await greenlake_request(
        ctx,
        "POST",
        path,
        query_params=query_params or None,
    )


@tool(
    name="greenlake_post_backup_recovery_v1beta1_protection_store_gateways_id_sizer",
    description="POST /backup-recovery/v1beta1/protection-store-gateways/{id}/sizer\n\nProtectionStoreGatewayPSGSize\n\nReturns the resource requirements that would be needed to resize an existing Protection Store Gateway.",
    capability=Capability.WRITE,
)
async def greenlake_post_backup_recovery_v1beta1_protection_store_gateways_id_sizer(
    ctx: Context,
    id: Annotated[str, Field(description="The UUID of the object")],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    path = f"/backup-recovery/v1beta1/protection-store-gateways/{path_seg(id)}/sizer"
    return await greenlake_request(
        ctx,
        "POST",
        path,
        body=body,
    )


@tool(
    name="greenlake_post_backup_recovery_v1beta1_protection_store_gateways_id_traceroute",
    description="POST /backup-recovery/v1beta1/protection-store-gateways/{id}/traceroute\n\nProtectionStoreGatewayTraceroute\n\nTraceroute from the Protection Store Gateway",
    capability=Capability.WRITE,
)
async def greenlake_post_backup_recovery_v1beta1_protection_store_gateways_id_traceroute(
    ctx: Context,
    id: Annotated[str, Field(description="The UUID of the object")],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    path = f"/backup-recovery/v1beta1/protection-store-gateways/{path_seg(id)}/traceroute"
    return await greenlake_request(
        ctx,
        "POST",
        path,
        body=body,
    )


@tool(
    name="greenlake_post_backup_recovery_v1beta1_protection_store_gateways_id_update_nic",
    description="POST /backup-recovery/v1beta1/protection-store-gateways/{id}/updateNic\n\nProtectionStoreGatewayNicUpdate\n\nModifies a network interface on the Protection Store Gateway",
    capability=Capability.WRITE,
)
async def greenlake_post_backup_recovery_v1beta1_protection_store_gateways_id_update_nic(
    ctx: Context,
    id: Annotated[str, Field(description="The UUID of the object")],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    path = f"/backup-recovery/v1beta1/protection-store-gateways/{path_seg(id)}/updateNic"
    return await greenlake_request(
        ctx,
        "POST",
        path,
        body=body,
    )
