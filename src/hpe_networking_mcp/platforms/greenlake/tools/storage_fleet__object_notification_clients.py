"""Generated GreenLake tools — DO NOT EDIT BY HAND.

Generated from the vendored spec ``vendor/greenlake/storage-fleet.json`` by the
maintainer-local GreenLake generator. These modules are committed and are the
runtime source of truth; regeneration is a release-time maintainer workflow
(the generator is intentionally not committed — see ``.gitignore``).

Service: ``storage-fleet``   Tag: ``object_notification_clients``   Operations: 5
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
    name="greenlake_delete_storage_fleet_v1alpha1_devtype7_storage_systems_system_id_object_notification_clients_client_id",
    description="DELETE /storage-fleet/v1alpha1/devtype7-storage-systems/{systemId}/object-notification-clients/{clientId}\n\nDeviceType7DeleteStorageSystemObjectNotificationClientSettingsById\n\nDelete Object Notification Client settings of HPE Alletra Storage MP X10000 system identified by {clientId}",
    capability=Capability.WRITE_DELETE,
)
async def greenlake_delete_storage_fleet_v1alpha1_devtype7_storage_systems_system_id_object_notification_clients_client_id(
    ctx: Context,
    systemId: Annotated[str, Field(description="ID of the Storage system")],
    clientId: Annotated[str, Field(description="ID of the Object Notification Client")],
) -> Any:
    path = f"/storage-fleet/v1alpha1/devtype7-storage-systems/{path_seg(systemId)}/object-notification-clients/{path_seg(clientId)}"
    return await greenlake_request(
        ctx,
        "DELETE",
        path,
    )


@tool(
    name="greenlake_get_storage_fleet_v1alpha1_devtype7_storage_systems_system_id_object_notification_clients",
    description="GET /storage-fleet/v1alpha1/devtype7-storage-systems/{systemId}/object-notification-clients\n\nDeviceType7GetStorageClusterObjectNotificationClientBySystemId\n\nGet all Object Notification Client config for HPE Alletra Storage MP X10000 system identified by {systemId}",
    capability=Capability.READ,
)
async def greenlake_get_storage_fleet_v1alpha1_devtype7_storage_systems_system_id_object_notification_clients(
    ctx: Context,
    systemId: Annotated[str, Field(description="ID of the Storage system")],
    select: Annotated[
        str | None,
        Field(default=None, description="Query to select only the required parameters, separated by . if nested"),
    ] = None,
    limit: Annotated[int | None, Field(default=None, description="Number of items to return at a time")] = None,
    offset: Annotated[
        int | None, Field(default=None, description="The offset of the first item in the collection to return")
    ] = None,
    filter: Annotated[str | None, Field(default=None, description="Lucene query to filter systems by Key.")] = None,
    sort: Annotated[str | None, Field(default=None, description="Lucene query to sort systems by Key.")] = None,
) -> Any:
    path = f"/storage-fleet/v1alpha1/devtype7-storage-systems/{path_seg(systemId)}/object-notification-clients"
    query_params: dict[str, Any] = {}
    if select is not None:
        query_params["select"] = select
    if limit is not None:
        query_params["limit"] = limit
    if offset is not None:
        query_params["offset"] = offset
    if filter is not None:
        query_params["filter"] = filter
    if sort is not None:
        query_params["sort"] = sort
    return await greenlake_request(
        ctx,
        "GET",
        path,
        query_params=query_params or None,
    )


@tool(
    name="greenlake_get_storage_fleet_v1alpha1_devtype7_storage_systems_system_id_object_notification_clients_client_id",
    description="GET /storage-fleet/v1alpha1/devtype7-storage-systems/{systemId}/object-notification-clients/{clientId}\n\nDeviceType7GetStorageClusterObjectNotificationClientById\n\nGet Object Notification Client config for HPE Alletra Storage MP X10000 system identified by {clientId}",
    capability=Capability.READ,
)
async def greenlake_get_storage_fleet_v1alpha1_devtype7_storage_systems_system_id_object_notification_clients_client_id(
    ctx: Context,
    systemId: Annotated[str, Field(description="ID of the Storage system")],
    clientId: Annotated[str, Field(description="ID of the Object Notification Client")],
    select: Annotated[
        str | None,
        Field(default=None, description="Query to select only the required parameters, separated by . if nested"),
    ] = None,
) -> Any:
    path = f"/storage-fleet/v1alpha1/devtype7-storage-systems/{path_seg(systemId)}/object-notification-clients/{path_seg(clientId)}"
    query_params: dict[str, Any] = {}
    if select is not None:
        query_params["select"] = select
    return await greenlake_request(
        ctx,
        "GET",
        path,
        query_params=query_params or None,
    )


@tool(
    name="greenlake_post_storage_fleet_v1alpha1_devtype7_storage_systems_system_id_object_notification_clients",
    description="POST /storage-fleet/v1alpha1/devtype7-storage-systems/{systemId}/object-notification-clients\n\nDeviceType7AddStorageSystemObjectNotificationClientSettingsById\n\nAdd Object Notification Client settings of HPE Alletra Storage MP X10000 system identified by {systemId}",
    capability=Capability.WRITE,
)
async def greenlake_post_storage_fleet_v1alpha1_devtype7_storage_systems_system_id_object_notification_clients(
    ctx: Context,
    systemId: Annotated[str, Field(description="ID of the Storage system")],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    path = f"/storage-fleet/v1alpha1/devtype7-storage-systems/{path_seg(systemId)}/object-notification-clients"
    return await greenlake_request(
        ctx,
        "POST",
        path,
        body=body,
    )


@tool(
    name="greenlake_put_storage_fleet_v1alpha1_devtype7_storage_systems_system_id_object_notification_clients_client_id",
    description="PUT /storage-fleet/v1alpha1/devtype7-storage-systems/{systemId}/object-notification-clients/{clientId}\n\nDeviceType7EditStorageSystemObjectNotificationClientSettingsById\n\nEdit Object Notification Client settings of HPE Alletra Storage MP X10000 system identified by {clientId}",
    capability=Capability.WRITE,
)
async def greenlake_put_storage_fleet_v1alpha1_devtype7_storage_systems_system_id_object_notification_clients_client_id(
    ctx: Context,
    systemId: Annotated[str, Field(description="ID of the Storage system")],
    clientId: Annotated[str, Field(description="ID of the Object Notification Client")],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    path = f"/storage-fleet/v1alpha1/devtype7-storage-systems/{path_seg(systemId)}/object-notification-clients/{path_seg(clientId)}"
    return await greenlake_request(
        ctx,
        "PUT",
        path,
        body=body,
    )
