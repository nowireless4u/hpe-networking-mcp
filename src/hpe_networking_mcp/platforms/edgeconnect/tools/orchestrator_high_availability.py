"""Generated EdgeConnect tools — DO NOT EDIT BY HAND.

Emitted by ``scripts/generate_edgeconnect_tools.py`` from
``vendor/edgeconnect/EdgeConnect-9-7-REST-API.json``. Regenerate via:

    uv run python scripts/generate_edgeconnect_tools.py

Tag: ``Orchestrator High Availability``
Operations in this file: 10
"""

# ruff: noqa: E501
from __future__ import annotations

from typing import Annotated, Any

from fastmcp import Context
from pydantic import Field

from hpe_networking_mcp.platforms._common.annotations import Capability
from hpe_networking_mcp.platforms.edgeconnect._registry import tool
from hpe_networking_mcp.platforms.edgeconnect.client import edgeconnect_request


@tool(
    name="edgeconnect_delete_orch_ha_instances",
    description="DELETE /orch-ha/instances\n\ndeleteOrchInstance\n\nRemove an orchestrator HA instance",
    capability=Capability.WRITE_DELETE,
)
async def edgeconnect_delete_orch_ha_instances(
    ctx: Context,
    id: Annotated[
        str,
        Field(
            description="Unique identifier of the orchestrator instance to remove. Must match an existing registered instance ID."
        ),
    ],
) -> Any:
    query_params: dict[str, Any] = {}
    if id is not None:
        query_params["id"] = id
    return await edgeconnect_request(
        ctx,
        "DELETE",
        "/orch-ha/instances",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_orch_ha_info",
    description="GET /orch-ha/info\n\nhaInfoGet\n\nGet orchestrator High Availability mode and instance information",
    capability=Capability.READ,
)
async def edgeconnect_get_orch_ha_info(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/orch-ha/info",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_orch_ha_instances",
    description="GET /orch-ha/instances\n\nhaInstancesGet\n\nGet orchestrator HA instances",
    capability=Capability.READ,
)
async def edgeconnect_get_orch_ha_instances(
    ctx: Context,
    id: Annotated[
        str | None,
        Field(
            default=None,
            description="Optional instance ID to retrieve a specific orchestrator instance. If omitted, returns all registered instances.",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if id is not None:
        query_params["id"] = id
    return await edgeconnect_request(
        ctx,
        "GET",
        "/orch-ha/instances",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_orch_ha_notification_config",
    description="GET /orch-ha/notificationConfig\n\nhaNotificationConfigGet\n\nGet HA notification configuration",
    capability=Capability.READ,
)
async def edgeconnect_get_orch_ha_notification_config(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/orch-ha/notificationConfig",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_orch_ha_primary_status",
    description="GET /orch-ha/primary/status\n\nprimaryInstanceHTTPStatusGet\n\nCheck primary orchestrator HTTP reachability status",
    capability=Capability.READ,
)
async def edgeconnect_get_orch_ha_primary_status(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/orch-ha/primary/status",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_orch_ha_reachability",
    description="GET /orch-ha/reachability\n\nHAClusterReachabilityConfigGet\n\nGet HA cluster reachability configuration",
    capability=Capability.READ,
)
async def edgeconnect_get_orch_ha_reachability(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/orch-ha/reachability",
        query_params=None,
    )


@tool(
    name="edgeconnect_post_orch_ha_reachability",
    description="POST /orch-ha/reachability\n\nHAClusterReachabilityConfigPost\n\nUpdate HA cluster reachability configuration",
    capability=Capability.WRITE,
)
async def edgeconnect_post_orch_ha_reachability(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/orch-ha/reachability",
        query_params=None,
        body=body,
    )


@tool(
    name="edgeconnect_put_orch_ha_instances",
    description="PUT /orch-ha/instances\n\nhaInstancePut\n\nUpdate HA instance comment",
    capability=Capability.WRITE,
)
async def edgeconnect_put_orch_ha_instances(
    ctx: Context,
    id: Annotated[
        str,
        Field(
            description="Unique identifier of the orchestrator instance to update. Must match an existing registered instance."
        ),
    ],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    query_params: dict[str, Any] = {}
    if id is not None:
        query_params["id"] = id
    return await edgeconnect_request(
        ctx,
        "PUT",
        "/orch-ha/instances",
        query_params=query_params or None,
        body=body,
    )


@tool(
    name="edgeconnect_put_orch_ha_notification_config",
    description="PUT /orch-ha/notificationConfig\n\nhaNotificationConfigPut\n\nUpdate HA notification configuration",
    capability=Capability.WRITE,
)
async def edgeconnect_put_orch_ha_notification_config(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await edgeconnect_request(
        ctx,
        "PUT",
        "/orch-ha/notificationConfig",
        query_params=None,
        body=body,
    )


@tool(
    name="edgeconnect_put_orch_ha_primary",
    description="PUT /orch-ha/primary\n\nhaprimaryPut\n\nPromote current backup instance to primary orchestrator",
    capability=Capability.WRITE,
)
async def edgeconnect_put_orch_ha_primary(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "PUT",
        "/orch-ha/primary",
        query_params=None,
    )
