"""Generated GreenLake tools — DO NOT EDIT BY HAND.

Generated from the vendored spec ``vendor/greenlake/event__webhook-v1beta1-webhook-v1beta1-nbapi.json`` by the
maintainer-local GreenLake generator. These modules are committed and are the
runtime source of truth; regeneration is a release-time maintainer workflow
(the generator is intentionally not committed — see ``.gitignore``).

Service: ``event``   Tag: ``webhooks``   Operations: 13
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
    name="greenlake_delete_events_v1beta1_system_webhooks_id",
    description="DELETE /events/v1beta1/system-webhooks/{id}\n\ndeleteWebhook\n\nDelete a webhook by ID",
    capability=Capability.WRITE_DELETE,
)
async def greenlake_delete_events_v1beta1_system_webhooks_id(
    ctx: Context,
    id: Annotated[str, Field(description="Webhook ID")],
    force: Annotated[
        bool | None,
        Field(
            default=None,
            description="The `force` query parameter is used to force deletion in situations where the webhook has one or more subscriptions.",
        ),
    ] = None,
) -> Any:
    path = f"/events/v1beta1/system-webhooks/{path_seg(id)}"
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
    name="greenlake_delete_events_v1beta1_webhooks_id",
    description="DELETE /events/v1beta1/webhooks/{id}\n\ndeleteWebhook\n\nDelete a webhook by ID",
    capability=Capability.WRITE_DELETE,
)
async def greenlake_delete_events_v1beta1_webhooks_id(
    ctx: Context,
    id: Annotated[str, Field(description="Webhook ID")],
    force: Annotated[
        bool | None,
        Field(
            default=None,
            description="The `force` query parameter is used to force deletion in situations where the webhook has one or more subscriptions.",
        ),
    ] = None,
) -> Any:
    path = f"/events/v1beta1/webhooks/{path_seg(id)}"
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
    name="greenlake_get_events_v1beta1_system_webhooks",
    description="GET /events/v1beta1/system-webhooks\n\nretrieveWebhooks\n\nGet all webhooks",
    capability=Capability.READ,
)
async def greenlake_get_events_v1beta1_system_webhooks(
    ctx: Context,
    limit: Annotated[
        int | None,
        Field(default=None, description="Specifies the number of results to be returned. The default value is 200."),
    ] = None,
    offset: Annotated[
        int | None,
        Field(
            default=None,
            description="Specifies the zero-based resource offset to start the response from. The default value is 0.",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if limit is not None:
        query_params["limit"] = limit
    if offset is not None:
        query_params["offset"] = offset
    return await greenlake_request(
        ctx,
        "GET",
        "/events/v1beta1/system-webhooks",
        query_params=query_params or None,
    )


@tool(
    name="greenlake_get_events_v1beta1_system_webhooks_id",
    description="GET /events/v1beta1/system-webhooks/{id}\n\nretrieveWebhook\n\nGet a webhook by ID",
    capability=Capability.READ,
)
async def greenlake_get_events_v1beta1_system_webhooks_id(
    ctx: Context,
    id: Annotated[str, Field(description="Webhook ID")],
) -> Any:
    path = f"/events/v1beta1/system-webhooks/{path_seg(id)}"
    return await greenlake_request(
        ctx,
        "GET",
        path,
    )


@tool(
    name="greenlake_get_events_v1beta1_webhooks",
    description="GET /events/v1beta1/webhooks\n\nretrieveWebhooks\n\nGet all webhooks",
    capability=Capability.READ,
)
async def greenlake_get_events_v1beta1_webhooks(
    ctx: Context,
    limit: Annotated[
        int | None,
        Field(default=None, description="Specifies the number of results to be returned. The default value is 200."),
    ] = None,
    offset: Annotated[
        int | None,
        Field(
            default=None,
            description="Specifies the zero-based resource offset to start the response from. The default value is 0.",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if limit is not None:
        query_params["limit"] = limit
    if offset is not None:
        query_params["offset"] = offset
    return await greenlake_request(
        ctx,
        "GET",
        "/events/v1beta1/webhooks",
        query_params=query_params or None,
    )


@tool(
    name="greenlake_get_events_v1beta1_webhooks_id",
    description="GET /events/v1beta1/webhooks/{id}\n\nretrieveWebhook\n\nGet a webhook by ID",
    capability=Capability.READ,
)
async def greenlake_get_events_v1beta1_webhooks_id(
    ctx: Context,
    id: Annotated[str, Field(description="Webhook ID")],
) -> Any:
    path = f"/events/v1beta1/webhooks/{path_seg(id)}"
    return await greenlake_request(
        ctx,
        "GET",
        path,
    )


@tool(
    name="greenlake_get_events_v1beta1_webhooks_id_recent_deliveries",
    description="GET /events/v1beta1/webhooks/{id}/recent-deliveries\n\nrecentDeliveries\n\nFetch recent webhook deliveries",
    capability=Capability.READ,
)
async def greenlake_get_events_v1beta1_webhooks_id_recent_deliveries(
    ctx: Context,
    id: Annotated[str, Field(description="Webhook ID")],
    limit: Annotated[
        int | None,
        Field(default=None, description="Specifies the number of results to be returned. The default value is 200."),
    ] = None,
    offset: Annotated[
        int | None,
        Field(
            default=None,
            description="Specifies the zero-based resource offset to start the response from. The default value is 0.",
        ),
    ] = None,
) -> Any:
    path = f"/events/v1beta1/webhooks/{path_seg(id)}/recent-deliveries"
    query_params: dict[str, Any] = {}
    if limit is not None:
        query_params["limit"] = limit
    if offset is not None:
        query_params["offset"] = offset
    return await greenlake_request(
        ctx,
        "GET",
        path,
        query_params=query_params or None,
    )


@tool(
    name="greenlake_patch_events_v1beta1_system_webhooks_id",
    description="PATCH /events/v1beta1/system-webhooks/{id}\n\nupdateWebhook\n\nUpdate a webhook by ID",
    capability=Capability.WRITE,
)
async def greenlake_patch_events_v1beta1_system_webhooks_id(
    ctx: Context,
    id: Annotated[str, Field(description="Webhook ID")],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    path = f"/events/v1beta1/system-webhooks/{path_seg(id)}"
    return await greenlake_request(
        ctx,
        "PATCH",
        path,
        body=body,
    )


@tool(
    name="greenlake_patch_events_v1beta1_webhooks_id",
    description="PATCH /events/v1beta1/webhooks/{id}\n\nupdateWebhook\n\nUpdate a webhook by ID",
    capability=Capability.WRITE,
)
async def greenlake_patch_events_v1beta1_webhooks_id(
    ctx: Context,
    id: Annotated[str, Field(description="Webhook ID")],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    path = f"/events/v1beta1/webhooks/{path_seg(id)}"
    return await greenlake_request(
        ctx,
        "PATCH",
        path,
        body=body,
    )


@tool(
    name="greenlake_post_events_v1beta1_system_webhooks",
    description="POST /events/v1beta1/system-webhooks\n\ncreateWebhook\n\nRegister a new webhook",
    capability=Capability.WRITE,
)
async def greenlake_post_events_v1beta1_system_webhooks(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await greenlake_request(
        ctx,
        "POST",
        "/events/v1beta1/system-webhooks",
        body=body,
    )


@tool(
    name="greenlake_post_events_v1beta1_webhooks",
    description="POST /events/v1beta1/webhooks\n\ncreateWebhook\n\nRegister a new webhook",
    capability=Capability.WRITE,
)
async def greenlake_post_events_v1beta1_webhooks(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await greenlake_request(
        ctx,
        "POST",
        "/events/v1beta1/webhooks",
        body=body,
    )


@tool(
    name="greenlake_post_events_v1beta1_webhooks_id_delivery_failures_failure_id_retry",
    description="POST /events/v1beta1/webhooks/{id}/delivery-failures/{failureId}/retry\n\ndeliveryFailuresRetry\n\nRetry webhook delivery failures",
    capability=Capability.WRITE,
)
async def greenlake_post_events_v1beta1_webhooks_id_delivery_failures_failure_id_retry(
    ctx: Context,
    id: Annotated[str, Field(description="Webhook ID")],
    failureId: Annotated[str, Field(description="Webhook Failure ID")],
) -> Any:
    path = f"/events/v1beta1/webhooks/{path_seg(id)}/delivery-failures/{path_seg(failureId)}/retry"
    return await greenlake_request(
        ctx,
        "POST",
        path,
    )


@tool(
    name="greenlake_post_events_v1beta1_webhooks_id_verify",
    description="POST /events/v1beta1/webhooks/{id}/verify\n\nwebhookVerification\n\nWebhook Verification Endpoint",
    capability=Capability.WRITE,
)
async def greenlake_post_events_v1beta1_webhooks_id_verify(
    ctx: Context,
    id: Annotated[str, Field(description="Webhook ID")],
) -> Any:
    path = f"/events/v1beta1/webhooks/{path_seg(id)}/verify"
    return await greenlake_request(
        ctx,
        "POST",
        path,
    )
