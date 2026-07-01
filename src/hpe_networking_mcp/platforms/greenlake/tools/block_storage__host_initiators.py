"""Generated GreenLake tools — DO NOT EDIT BY HAND.

Generated from the vendored spec ``vendor/greenlake/block-storage.json`` by the
maintainer-local GreenLake generator. These modules are committed and are the
runtime source of truth; regeneration is a release-time maintainer workflow
(the generator is intentionally not committed — see ``.gitignore``).

Service: ``block-storage``   Tag: ``host_initiators``   Operations: 15
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
    name="greenlake_delete_block_storage_v1alpha1_host_initiators_host_id",
    description="DELETE /block-storage/v1alpha1/host-initiators/{hostId}\n\nHostDelete\n\nDelete a host by {hostId}",
    capability=Capability.WRITE_DELETE,
)
async def greenlake_delete_block_storage_v1alpha1_host_initiators_host_id(
    ctx: Context,
    hostId: Annotated[str, Field(description="Id of the Host.")],
    force: Annotated[bool | None, Field(default=None, description="Forceful delete option")] = None,
    delete_associated_empty_hg: Annotated[
        bool | None,
        Field(default=None, description="Delete the resulting empty host group associated to this host option"),
    ] = None,
) -> Any:
    path = f"/block-storage/v1alpha1/host-initiators/{path_seg(hostId)}"
    query_params: dict[str, Any] = {}
    if force is not None:
        query_params["force"] = force
    if delete_associated_empty_hg is not None:
        query_params["delete-associated-empty-hg"] = delete_associated_empty_hg
    return await greenlake_request(
        ctx,
        "DELETE",
        path,
        query_params=query_params or None,
    )


@tool(
    name="greenlake_delete_block_storage_v1alpha1_initiators_initiator_id",
    description="DELETE /block-storage/v1alpha1/initiators/{initiatorId}\n\nHostInitiatorDelete\n\nDelete initiator by {initiatorId}",
    capability=Capability.WRITE_DELETE,
)
async def greenlake_delete_block_storage_v1alpha1_initiators_initiator_id(
    ctx: Context,
    initiatorId: Annotated[str, Field(description="UID of Initiator.")],
) -> Any:
    path = f"/block-storage/v1alpha1/initiators/{path_seg(initiatorId)}"
    return await greenlake_request(
        ctx,
        "DELETE",
        path,
    )


@tool(
    name="greenlake_get_block_storage_v1alpha1_host_initiators",
    description="GET /block-storage/v1alpha1/host-initiators\n\nHostList\n\nGet the list of hosts",
    capability=Capability.READ,
)
async def greenlake_get_block_storage_v1alpha1_host_initiators(
    ctx: Context,
    filter: Annotated[str | None, Field(default=None, description="oData query to filter hostservice by Key.")] = None,
    sort: Annotated[str | None, Field(default=None, description="oData query to sort hostservice by Key.")] = None,
    limit: Annotated[int | None, Field(default=None, description="Number of items to return at a time")] = None,
    offset: Annotated[
        int | None, Field(default=None, description="The offset of the first item in the collection to return")
    ] = None,
    select: Annotated[
        str | None,
        Field(default=None, description="Query to select only the required parameters, separated by . if nested"),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if filter is not None:
        query_params["filter"] = filter
    if sort is not None:
        query_params["sort"] = sort
    if limit is not None:
        query_params["limit"] = limit
    if offset is not None:
        query_params["offset"] = offset
    if select is not None:
        query_params["select"] = select
    return await greenlake_request(
        ctx,
        "GET",
        "/block-storage/v1alpha1/host-initiators",
        query_params=query_params or None,
    )


@tool(
    name="greenlake_get_block_storage_v1alpha1_host_initiators_host_id",
    description="GET /block-storage/v1alpha1/host-initiators/{hostId}\n\nHostGetById\n\nGet the host details by {hostId}",
    capability=Capability.READ,
)
async def greenlake_get_block_storage_v1alpha1_host_initiators_host_id(
    ctx: Context,
    hostId: Annotated[str, Field(description="Id of the Host.")],
) -> Any:
    path = f"/block-storage/v1alpha1/host-initiators/{path_seg(hostId)}"
    return await greenlake_request(
        ctx,
        "GET",
        path,
    )


@tool(
    name="greenlake_get_block_storage_v1alpha1_host_initiators_host_id_chap",
    description="GET /block-storage/v1alpha1/host-initiators/{hostId}/chap\n\nGetHostChapById\n\nGet Host CHAP details by {hostId}",
    capability=Capability.READ,
)
async def greenlake_get_block_storage_v1alpha1_host_initiators_host_id_chap(
    ctx: Context,
    hostId: Annotated[str, Field(description="Id of the Host.")],
) -> Any:
    path = f"/block-storage/v1alpha1/host-initiators/{path_seg(hostId)}/chap"
    return await greenlake_request(
        ctx,
        "GET",
        path,
    )


@tool(
    name="greenlake_get_block_storage_v1alpha1_host_initiators_host_id_mapped_devices",
    description="GET /block-storage/v1alpha1/host-initiators/{hostId}/mapped-devices\n\nHostMappedDevice\n\nGet details of a host identified by {hostId} across its associated systems",
    capability=Capability.READ,
)
async def greenlake_get_block_storage_v1alpha1_host_initiators_host_id_mapped_devices(
    ctx: Context,
    hostId: Annotated[str, Field(description="Id of the Host.")],
) -> Any:
    path = f"/block-storage/v1alpha1/host-initiators/{path_seg(hostId)}/mapped-devices"
    return await greenlake_request(
        ctx,
        "GET",
        path,
    )


@tool(
    name="greenlake_get_block_storage_v1alpha1_host_initiators_host_id_storage_performance_history",
    description="GET /block-storage/v1alpha1/host-initiators/{hostId}/storage-performance-history\n\nHostVolumePerformanceHistoryGet\n\nGet the volume performance history data associated with a host identified by {uid}",
    capability=Capability.READ,
)
async def greenlake_get_block_storage_v1alpha1_host_initiators_host_id_storage_performance_history(
    ctx: Context,
    hostId: Annotated[str, Field(description="Id of the Host.")],
    select: Annotated[
        str | None,
        Field(default=None, description="Query to select only the required parameters, separated by . if nested"),
    ] = None,
    range: Annotated[
        str | None,
        Field(default=None, description="range will define start and end time in which query has to be made."),
    ] = None,
    time_interval_min: Annotated[
        int | None, Field(default=None, description="It defines granularity in minutes.")
    ] = None,
    top_volumes_count: Annotated[
        int | None, Field(default=None, description="The number of top volumes to return. Defaults to 5.")
    ] = None,
) -> Any:
    path = f"/block-storage/v1alpha1/host-initiators/{path_seg(hostId)}/storage-performance-history"
    query_params: dict[str, Any] = {}
    if select is not None:
        query_params["select"] = select
    if range is not None:
        query_params["range"] = range
    if time_interval_min is not None:
        query_params["time-interval-min"] = time_interval_min
    if top_volumes_count is not None:
        query_params["top-volumes-count"] = top_volumes_count
    return await greenlake_request(
        ctx,
        "GET",
        path,
        query_params=query_params or None,
    )


@tool(
    name="greenlake_get_block_storage_v1alpha1_host_initiators_host_id_volumes",
    description="GET /block-storage/v1alpha1/host-initiators/{hostId}/volumes\n\nHostVolumesGet\n\nGet details of volumes associated with a host identified by {uid}",
    capability=Capability.READ,
)
async def greenlake_get_block_storage_v1alpha1_host_initiators_host_id_volumes(
    ctx: Context,
    hostId: Annotated[str, Field(description="Id of the Host.")],
    select: Annotated[
        str | None,
        Field(default=None, description="Query to select only the required parameters, separated by . if nested"),
    ] = None,
) -> Any:
    path = f"/block-storage/v1alpha1/host-initiators/{path_seg(hostId)}/volumes"
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
    name="greenlake_get_block_storage_v1alpha1_initiators",
    description="GET /block-storage/v1alpha1/initiators\n\nHostInitiatorList\n\nGet the list of initiators",
    capability=Capability.READ,
)
async def greenlake_get_block_storage_v1alpha1_initiators(
    ctx: Context,
    filter: Annotated[str | None, Field(default=None, description="oData query to filter hostservice by Key.")] = None,
    sort: Annotated[str | None, Field(default=None, description="oData query to sort hostservice by Key.")] = None,
    limit: Annotated[int | None, Field(default=None, description="Number of items to return at a time")] = None,
    offset: Annotated[
        int | None, Field(default=None, description="The offset of the first item in the collection to return")
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if filter is not None:
        query_params["filter"] = filter
    if sort is not None:
        query_params["sort"] = sort
    if limit is not None:
        query_params["limit"] = limit
    if offset is not None:
        query_params["offset"] = offset
    return await greenlake_request(
        ctx,
        "GET",
        "/block-storage/v1alpha1/initiators",
        query_params=query_params or None,
    )


@tool(
    name="greenlake_get_block_storage_v1alpha1_initiators_initiator_id",
    description="GET /block-storage/v1alpha1/initiators/{initiatorId}\n\nHostInitiatorGetById\n\nGet the initiator details by {initiatorId}",
    capability=Capability.READ,
)
async def greenlake_get_block_storage_v1alpha1_initiators_initiator_id(
    ctx: Context,
    initiatorId: Annotated[str, Field(description="UID of Initiator.")],
) -> Any:
    path = f"/block-storage/v1alpha1/initiators/{path_seg(initiatorId)}"
    return await greenlake_request(
        ctx,
        "GET",
        path,
    )


@tool(
    name="greenlake_post_block_storage_v1alpha1_host_initiators",
    description="POST /block-storage/v1alpha1/host-initiators\n\nHostCreate\n\nCreate a host",
    capability=Capability.WRITE,
)
async def greenlake_post_block_storage_v1alpha1_host_initiators(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await greenlake_request(
        ctx,
        "POST",
        "/block-storage/v1alpha1/host-initiators",
        body=body,
    )


@tool(
    name="greenlake_post_block_storage_v1alpha1_host_initiators_host_id_chapkey",
    description="POST /block-storage/v1alpha1/host-initiators/{hostId}/chapkey\n\nGenerateChapKeyById\n\nGenerate a DH-HMAC-CHAP host key usable for NVMe In-Band Authentication for Host by {hostId}",
    capability=Capability.WRITE,
)
async def greenlake_post_block_storage_v1alpha1_host_initiators_host_id_chapkey(
    ctx: Context,
    hostId: Annotated[str, Field(description="Id of the Host.")],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    path = f"/block-storage/v1alpha1/host-initiators/{path_seg(hostId)}/chapkey"
    return await greenlake_request(
        ctx,
        "POST",
        path,
        body=body,
    )


@tool(
    name="greenlake_post_block_storage_v1alpha1_initiators",
    description="POST /block-storage/v1alpha1/initiators\n\nHostInitiatorCreate\n\nCreate initiator",
    capability=Capability.WRITE,
)
async def greenlake_post_block_storage_v1alpha1_initiators(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await greenlake_request(
        ctx,
        "POST",
        "/block-storage/v1alpha1/initiators",
        body=body,
    )


@tool(
    name="greenlake_put_block_storage_v1alpha1_host_initiators_host_id",
    description="PUT /block-storage/v1alpha1/host-initiators/{hostId}\n\nHostUpdateById\n\nUpdate Host by {hostId}",
    capability=Capability.WRITE,
)
async def greenlake_put_block_storage_v1alpha1_host_initiators_host_id(
    ctx: Context,
    hostId: Annotated[str, Field(description="Id of the Host.")],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    path = f"/block-storage/v1alpha1/host-initiators/{path_seg(hostId)}"
    return await greenlake_request(
        ctx,
        "PUT",
        path,
        body=body,
    )


@tool(
    name="greenlake_put_block_storage_v1alpha1_host_initiators_host_id_chap",
    description="PUT /block-storage/v1alpha1/host-initiators/{hostId}/chap\n\nUpdateHostChapById\n\nUpdate Host CHAP by {hostId}",
    capability=Capability.WRITE,
)
async def greenlake_put_block_storage_v1alpha1_host_initiators_host_id_chap(
    ctx: Context,
    hostId: Annotated[str, Field(description="Id of the Host.")],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    path = f"/block-storage/v1alpha1/host-initiators/{path_seg(hostId)}/chap"
    return await greenlake_request(
        ctx,
        "PUT",
        path,
        body=body,
    )
