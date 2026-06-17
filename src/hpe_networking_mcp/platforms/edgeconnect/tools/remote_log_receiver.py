"""Generated EdgeConnect tools — DO NOT EDIT BY HAND.

Generated from ``vendor/edgeconnect/EdgeConnect-9-7-REST-API.json`` by the
maintainer-local EdgeConnect generator. These generated modules are committed
and are the runtime source of truth; regeneration is a release-time maintainer
workflow (the generator is intentionally not committed — see ``.gitignore``).

Tag: ``remoteLogReceiver``
Operations in this file: 7
"""

# ruff: noqa: E501, N803
from __future__ import annotations

from typing import Annotated, Any

from fastmcp import Context
from pydantic import Field

from hpe_networking_mcp.platforms._common.annotations import Capability
from hpe_networking_mcp.platforms.edgeconnect._registry import tool
from hpe_networking_mcp.platforms.edgeconnect.client import edgeconnect_request


@tool(
    name="edgeconnect_delete_remote_log_receiver",
    description="DELETE /remoteLogReceiver\n\nRemoteLogReceiverDelete539\n\nDelete a remote log receiver configuration",
    capability=Capability.WRITE_DELETE,
)
async def edgeconnect_delete_remote_log_receiver(
    ctx: Context,
    receiverId: Annotated[
        int, Field(description="Unique identifier of the receiver to delete. Must be a valid existing receiver ID.")
    ],
) -> Any:
    query_params: dict[str, Any] = {}
    if receiverId is not None:
        query_params["receiverId"] = receiverId
    return await edgeconnect_request(
        ctx,
        "DELETE",
        "/remoteLogReceiver",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_remote_log_receiver",
    description="GET /remoteLogReceiver\n\nRemoteLogReceiverSingleGet540\n\nRetrieve remote log receiver configurations",
    capability=Capability.READ,
)
async def edgeconnect_get_remote_log_receiver(
    ctx: Context,
    receiverId: Annotated[
        int | None,
        Field(
            default=None,
            description="Unique identifier of a specific receiver to retrieve. If omitted, all receivers are returned.",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if receiverId is not None:
        query_params["receiverId"] = receiverId
    return await edgeconnect_request(
        ctx,
        "GET",
        "/remoteLogReceiver",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_remote_log_receiver_sequence_id_latest",
    description="GET /remoteLogReceiver/sequenceId/latest\n\nlatestSequenceIdGet538\n\nRetrieve the latest sequence ID for alarms or audit logs",
    capability=Capability.READ,
)
async def edgeconnect_get_remote_log_receiver_sequence_id_latest(
    ctx: Context,
    logType: Annotated[
        str,
        Field(
            description="Type of log to retrieve the latest sequence ID for. Use 'alarm' for alarm events or 'auditLog' (case-insensitive) for audit log entries."
        ),
    ],
) -> Any:
    query_params: dict[str, Any] = {}
    if logType is not None:
        query_params["logType"] = logType
    return await edgeconnect_request(
        ctx,
        "GET",
        "/remoteLogReceiver/sequenceId/latest",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_remote_log_receiver_websocket_status",
    description="GET /remoteLogReceiver/websocket/status\n\nsocketStatusGet537\n\nRetrieve WebSocket receiver connection status",
    capability=Capability.READ,
)
async def edgeconnect_get_remote_log_receiver_websocket_status(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/remoteLogReceiver/websocket/status",
        query_params=None,
    )


@tool(
    name="edgeconnect_post_remote_log_receiver",
    description="POST /remoteLogReceiver\n\nRemoteLogReceiverAdd535\n\nCreate one or more remote log receivers",
    capability=Capability.WRITE,
)
async def edgeconnect_post_remote_log_receiver(
    ctx: Context,
    body: Annotated[list[Any], Field(description="Request body (required)")],
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/remoteLogReceiver",
        query_params=None,
        body=body,
    )


@tool(
    name="edgeconnect_post_remote_log_receiver_subscribe",
    description="POST /remoteLogReceiver/subscribe\n\nRemoteLogReceiverSubscribe541\n\nRequest resubmission of specific log messages by sequence ID",
    capability=Capability.WRITE,
)
async def edgeconnect_post_remote_log_receiver_subscribe(
    ctx: Context,
    receiverId: Annotated[
        int,
        Field(
            description="Unique identifier of an existing remote log receiver. Must reference a valid, configured receiver."
        ),
    ],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    query_params: dict[str, Any] = {}
    if receiverId is not None:
        query_params["receiverId"] = receiverId
    return await edgeconnect_request(
        ctx,
        "POST",
        "/remoteLogReceiver/subscribe",
        query_params=query_params or None,
        body=body,
    )


@tool(
    name="edgeconnect_put_remote_log_receiver",
    description="PUT /remoteLogReceiver\n\nRemoteLogReceiverPut536\n\nUpdate existing remote log receiver configurations",
    capability=Capability.WRITE,
)
async def edgeconnect_put_remote_log_receiver(
    ctx: Context,
    body: Annotated[list[Any], Field(description="Request body (required)")],
) -> Any:
    return await edgeconnect_request(
        ctx,
        "PUT",
        "/remoteLogReceiver",
        query_params=None,
        body=body,
    )
