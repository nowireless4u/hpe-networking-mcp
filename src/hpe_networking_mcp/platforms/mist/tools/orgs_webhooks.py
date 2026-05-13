"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``hpe_networking_mcp.platforms.mist._generator``
from ``vendor/mist_openapi.json``. Regenerate via:

    uv run python -m hpe_networking_mcp.platforms.mist.regenerate

Tag: ``Orgs Webhooks``
Operations in this file: 8
"""

# ruff: noqa: E501

from __future__ import annotations

from typing import Annotated, Any

from fastmcp import Context
from mcp.types import ToolAnnotations
from pydantic import Field

from hpe_networking_mcp.platforms.mist._client import mist_request
from hpe_networking_mcp.platforms.mist._registry import tool as _mcp_tool


@_mcp_tool(
    name="mist_count_org_webhooks_deliveries",
    description="GET /api/v1/orgs/{org_id}/webhooks/{webhook_id}/events/count\n\ncountOrgWebhooksDeliveries\n\nCount Org Webhooks deliveries\n\n\nTopics Supported:\n- alarms\n- audits\n- device-updowns\n- occupancy-alerts\n- ping",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_count_org_webhooks_deliveries(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    webhook_id: Annotated[str, Field(description="path parameter 'webhook_id'")],
    error: Annotated[str | None, Field(description="query parameter 'error'")] = None,
    status_code: Annotated[int | None, Field(description="query parameter 'status_code'")] = None,
    status: Annotated[Any | None, Field(description="Webhook delivery status")] = None,
    topic: Annotated[Any | None, Field(description="Webhook topic")] = None,
    distinct: Annotated[Any | None, Field(description="query parameter 'distinct'")] = None,
    start: Annotated[
        str | None, Field(description='Start time (epoch timestamp in seconds, or relative string like "-1d", "-1w")')
    ] = None,
    end: Annotated[
        str | None,
        Field(description='End time (epoch timestamp in seconds, or relative string like "-1d", "-2h", "now")'),
    ] = None,
    duration: Annotated[str, Field(description="Duration like 7d, 2w")] = "1d",
    limit: Annotated[int, Field(description="query parameter 'limit'")] = 100,
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/orgs/{org_id}/webhooks/{webhook_id}/events/count",
        path_params={"org_id": org_id, "webhook_id": webhook_id},
        query_params={
            "error": error,
            "status_code": status_code,
            "status": status,
            "topic": topic,
            "distinct": distinct,
            "start": start,
            "end": end,
            "duration": duration,
            "limit": limit,
        },
        body=None,
    )


@_mcp_tool(
    name="mist_create_org_webhook",
    description="POST /api/v1/orgs/{org_id}/webhooks\n\ncreateOrgWebhook\n\n**N.B**. For org webhooks, only alarms/audits/client-info/client-join/client-sessions/device_events/device-updowns/mxedge_events Infrastructure topics are supported.\n\n\nWebhook defines a webhook, modeled after [github\\u2019s model](https://developer.github.com/webhooks/).\n\n\nThere is two types of webhooks:\n* webhooks ([examples](https://www.postman.com/juniper-mist/workspace/mist-systems-s-public-workspace/folder/224925-be01e694-7253-4195-8563-78e2a745e114))        \n* raw data webhooks ([examples](https://www.postman.com/juniper-mist/work...",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_create_org_webhook(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request Body")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/orgs/{org_id}/webhooks",
        path_params={"org_id": org_id},
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_delete_org_webhook",
    description="DELETE /api/v1/orgs/{org_id}/webhooks/{webhook_id}\n\ndeleteOrgWebhook\n\nDelete Org Webhook",
    tags={"mist", "mist_write", "mist_write_delete"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=True),
)
async def mist_delete_org_webhook(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    webhook_id: Annotated[str, Field(description="path parameter 'webhook_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "DELETE",
        "/api/v1/orgs/{org_id}/webhooks/{webhook_id}",
        path_params={"org_id": org_id, "webhook_id": webhook_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_get_org_webhook",
    description="GET /api/v1/orgs/{org_id}/webhooks/{webhook_id}\n\ngetOrgWebhook\n\nGet Org Webhook Details",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_get_org_webhook(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    webhook_id: Annotated[str, Field(description="path parameter 'webhook_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/orgs/{org_id}/webhooks/{webhook_id}",
        path_params={"org_id": org_id, "webhook_id": webhook_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_list_org_webhooks",
    description="GET /api/v1/orgs/{org_id}/webhooks\n\nlistOrgWebhooks\n\nGet List of Org Webhooks",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_list_org_webhooks(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    limit: Annotated[int, Field(description="query parameter 'limit'")] = 100,
    page: Annotated[int, Field(description="query parameter 'page'")] = 1,
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/orgs/{org_id}/webhooks",
        path_params={"org_id": org_id},
        query_params={"limit": limit, "page": page},
        body=None,
    )


@_mcp_tool(
    name="mist_ping_org_webhook",
    description="POST /api/v1/orgs/{org_id}/webhooks/{webhook_id}/ping\n\npingOrgWebhook\n\nSend a Ping event to the webhook",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_ping_org_webhook(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    webhook_id: Annotated[str, Field(description="path parameter 'webhook_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/orgs/{org_id}/webhooks/{webhook_id}/ping",
        path_params={"org_id": org_id, "webhook_id": webhook_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_search_org_webhooks_deliveries",
    description="GET /api/v1/orgs/{org_id}/webhooks/{webhook_id}/events/search\n\nsearchOrgWebhooksDeliveries\n\nSearch Org Webhooks deliveries\n\n\nTopics Supported:\n- alarms\n- audits\n- device-updowns\n- occupancy-alerts\n- ping",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_search_org_webhooks_deliveries(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    webhook_id: Annotated[str, Field(description="path parameter 'webhook_id'")],
    error: Annotated[str | None, Field(description="query parameter 'error'")] = None,
    status_code: Annotated[int | None, Field(description="query parameter 'status_code'")] = None,
    status: Annotated[Any | None, Field(description="Webhook delivery status")] = None,
    topic: Annotated[Any | None, Field(description="Webhook topic")] = None,
    limit: Annotated[int, Field(description="query parameter 'limit'")] = 100,
    start: Annotated[
        str | None, Field(description='Start time (epoch timestamp in seconds, or relative string like "-1d", "-1w")')
    ] = None,
    end: Annotated[
        str | None,
        Field(description='End time (epoch timestamp in seconds, or relative string like "-1d", "-2h", "now")'),
    ] = None,
    duration: Annotated[str, Field(description="Duration like 7d, 2w")] = "1d",
    sort: Annotated[
        str, Field(description="On which field the list should be sorted, -prefix represents DESC order")
    ] = "timestamp",
    search_after: Annotated[
        str | None,
        Field(
            description="Pagination cursor for retrieving subsequent pages of results. This value is automatically populated by Mist in the `next` URL from the previous response and should not be manually constructed."
        ),
    ] = None,
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/orgs/{org_id}/webhooks/{webhook_id}/events/search",
        path_params={"org_id": org_id, "webhook_id": webhook_id},
        query_params={
            "error": error,
            "status_code": status_code,
            "status": status,
            "topic": topic,
            "limit": limit,
            "start": start,
            "end": end,
            "duration": duration,
            "sort": sort,
            "search_after": search_after,
        },
        body=None,
    )


@_mcp_tool(
    name="mist_update_org_webhook",
    description="PUT /api/v1/orgs/{org_id}/webhooks/{webhook_id}\n\nupdateOrgWebhook\n\nUpdate Org Webhook",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_update_org_webhook(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    webhook_id: Annotated[str, Field(description="path parameter 'webhook_id'")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request Body")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "PUT",
        "/api/v1/orgs/{org_id}/webhooks/{webhook_id}",
        path_params={"org_id": org_id, "webhook_id": webhook_id},
        query_params=None,
        body=body,
    )
