"""Generated EdgeConnect tools — DO NOT EDIT BY HAND.

Generated from ``vendor/edgeconnect/EdgeConnect-9-7-REST-API.json`` by the
maintainer-local EdgeConnect generator. These generated modules are committed
and are the runtime source of truth; regeneration is a release-time maintainer
workflow (the generator is intentionally not committed — see ``.gitignore``).

Tag: ``actionLog``
Operations in this file: 4
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
    name="edgeconnect_get_action",
    description="GET /action\n\ngetActionLogs\n\nGet action/audit log entries",
    capability=Capability.READ,
)
async def edgeconnect_get_action(
    ctx: Context,
    startTime: Annotated[
        int,
        Field(
            description="Start time boundary in milliseconds since EPOCH (Unix timestamp). Required unless format=csv."
        ),
    ],
    endTime: Annotated[
        int,
        Field(
            description="End time boundary in milliseconds since EPOCH (Unix timestamp). Must be greater than or equal to startTime."
        ),
    ],
    limit: Annotated[
        int | None,
        Field(
            default=None,
            description="Maximum number of log entries to return. Capped at 10000 if not specified or exceeds limit.",
        ),
    ] = None,
    logLevel: Annotated[
        int | None,
        Field(
            default=None,
            description="Minimum log level filter: 0=Debug (all logs), 1=Info (Info+Error), 2=Error (only errors). Defaults to 1 (Info).",
        ),
    ] = None,
    appliance: Annotated[
        str | None,
        Field(
            default=None,
            description="Filter by appliance ID (nePk). Supports SQL LIKE wildcards (%) when not specified, returns all appliances.",
        ),
    ] = None,
    username: Annotated[
        str | None,
        Field(
            default=None,
            description="Filter by username. Supports wildcard (*) at start or end of string for partial matching.",
        ),
    ] = None,
    format: Annotated[
        str | None,
        Field(
            default=None,
            description="Set to 'csv' to export all action logs as CSV file. When set, startTime and endTime are ignored.",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if startTime is not None:
        query_params["startTime"] = startTime
    if endTime is not None:
        query_params["endTime"] = endTime
    if limit is not None:
        query_params["limit"] = limit
    if logLevel is not None:
        query_params["logLevel"] = logLevel
    if appliance is not None:
        query_params["appliance"] = appliance
    if username is not None:
        query_params["username"] = username
    if format is not None:
        query_params["format"] = format
    return await edgeconnect_request(
        ctx,
        "GET",
        "/action",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_action_in_progress",
    description="GET /action/inProgress\n\nareActionsInProgress\n\nCheck if user has actions in progress or queued",
    capability=Capability.READ,
)
async def edgeconnect_get_action_in_progress(
    ctx: Context,
    user: Annotated[
        str,
        Field(
            description="Username to check for active actions. Must match the 'user' field in action logs exactly (case-sensitive)."
        ),
    ],
) -> Any:
    query_params: dict[str, Any] = {}
    if user is not None:
        query_params["user"] = user
    return await edgeconnect_request(
        ctx,
        "GET",
        "/action/inProgress",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_action_status",
    description="GET /action/status\n\ngetActionStatus\n\nGet action status by GUID key",
    capability=Capability.READ,
)
async def edgeconnect_get_action_status(
    ctx: Context,
    key: Annotated[
        str,
        Field(
            description="GUID key identifying the action group. Obtained from endpoints that return poll handles (e.g., appliance upgrades, restores, bulk configuration operations)."
        ),
    ],
) -> Any:
    query_params: dict[str, Any] = {}
    if key is not None:
        query_params["key"] = key
    return await edgeconnect_request(
        ctx,
        "GET",
        "/action/status",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_post_action_cancel",
    description="POST /action/cancel\n\ncancelActions\n\nCancel queued or in-progress actions by GUID",
    capability=Capability.WRITE,
)
async def edgeconnect_post_action_cancel(
    ctx: Context,
    key: Annotated[
        str,
        Field(
            description="GUID key identifying the action group to cancel. Obtained from endpoints that return a poll handle (e.g., appliance upgrades, restores, bulk operations)."
        ),
    ],
) -> Any:
    query_params: dict[str, Any] = {}
    if key is not None:
        query_params["key"] = key
    return await edgeconnect_request(
        ctx,
        "POST",
        "/action/cancel",
        query_params=query_params or None,
    )
