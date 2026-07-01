"""Generated GreenLake tools — DO NOT EDIT BY HAND.

Generated from the vendored spec ``vendor/greenlake/event__webhook-v1beta1-webhook-v1beta1-nbapi.json`` by the
maintainer-local GreenLake generator. These modules are committed and are the
runtime source of truth; regeneration is a release-time maintainer workflow
(the generator is intentionally not committed — see ``.gitignore``).

Service: ``event``   Tag: ``subscriptions``   Operations: 8
"""

# ruff: noqa: E501
from __future__ import annotations

from typing import Annotated, Any

from fastmcp import Context
from pydantic import Field

from hpe_networking_mcp.platforms._common.annotations import Capability
from hpe_networking_mcp.platforms.greenlake._registry import tool
from hpe_networking_mcp.platforms.greenlake.client import greenlake_request


@tool(
    name="greenlake_delete_events_v1beta1_subscriptions",
    description="DELETE /events/v1beta1/subscriptions\n\nDeleteSubscription\n\nDelete subscription for a webhook",
    capability=Capability.WRITE_DELETE,
)
async def greenlake_delete_events_v1beta1_subscriptions(
    ctx: Context,
    id: Annotated[list[str], Field(description="The ID of the subscription to delete.")],
) -> Any:
    query_params: dict[str, Any] = {}
    if id is not None:
        query_params["id"] = id
    return await greenlake_request(
        ctx,
        "DELETE",
        "/events/v1beta1/subscriptions",
        query_params=query_params or None,
    )


@tool(
    name="greenlake_delete_events_v1beta1_system_subscriptions",
    description="DELETE /events/v1beta1/system-subscriptions\n\nDeleteSubscription\n\nDelete subscription for a webhook",
    capability=Capability.WRITE_DELETE,
)
async def greenlake_delete_events_v1beta1_system_subscriptions(
    ctx: Context,
    id: Annotated[list[str], Field(description="The ID of the subscription to delete.")],
) -> Any:
    query_params: dict[str, Any] = {}
    if id is not None:
        query_params["id"] = id
    return await greenlake_request(
        ctx,
        "DELETE",
        "/events/v1beta1/system-subscriptions",
        query_params=query_params or None,
    )


@tool(
    name="greenlake_get_events_v1beta1_subscriptions",
    description="GET /events/v1beta1/subscriptions\n\nretrieveSubscriptions\n\nGet all subscriptions for a webhook",
    capability=Capability.READ,
)
async def greenlake_get_events_v1beta1_subscriptions(
    ctx: Context,
    filter: Annotated[
        str,
        Field(
            description="Filter subscriptions events using an [OData V4](https://www.odata.org/documentation/) formatted filter string."
        ),
    ],
    limit: Annotated[
        int | None,
        Field(default=None, description="Specifies the number of results to be returned. The default value is 10."),
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
    if filter is not None:
        query_params["filter"] = filter
    return await greenlake_request(
        ctx,
        "GET",
        "/events/v1beta1/subscriptions",
        query_params=query_params or None,
    )


@tool(
    name="greenlake_get_events_v1beta1_system_subscriptions",
    description="GET /events/v1beta1/system-subscriptions\n\nretrieveSubscriptions\n\nGet all subscriptions for a webhook",
    capability=Capability.READ,
)
async def greenlake_get_events_v1beta1_system_subscriptions(
    ctx: Context,
    filter: Annotated[
        str,
        Field(
            description="Filter subscriptions events using an [OData V4](https://www.odata.org/documentation/) formatted filter string."
        ),
    ],
    limit: Annotated[
        int | None,
        Field(default=None, description="Specifies the number of results to be returned. The default value is 10."),
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
    if filter is not None:
        query_params["filter"] = filter
    return await greenlake_request(
        ctx,
        "GET",
        "/events/v1beta1/system-subscriptions",
        query_params=query_params or None,
    )


@tool(
    name="greenlake_patch_events_v1beta1_subscriptions",
    description="PATCH /events/v1beta1/subscriptions\n\nupdateSubscription\n\nUpdate subscription with specific IDs",
    capability=Capability.WRITE,
)
async def greenlake_patch_events_v1beta1_subscriptions(
    ctx: Context,
    body: Annotated[list[Any], Field(description="Request body (required)")],
) -> Any:
    return await greenlake_request(
        ctx,
        "PATCH",
        "/events/v1beta1/subscriptions",
        body=body,
    )


@tool(
    name="greenlake_patch_events_v1beta1_system_subscriptions",
    description="PATCH /events/v1beta1/system-subscriptions\n\nupdateSubscription\n\nUpdate subscription with specific IDs",
    capability=Capability.WRITE,
)
async def greenlake_patch_events_v1beta1_system_subscriptions(
    ctx: Context,
    body: Annotated[list[Any], Field(description="Request body (required)")],
) -> Any:
    return await greenlake_request(
        ctx,
        "PATCH",
        "/events/v1beta1/system-subscriptions",
        body=body,
    )


@tool(
    name="greenlake_post_events_v1beta1_subscriptions",
    description="POST /events/v1beta1/subscriptions\n\ncreateSubscription\n\nCreate a new subscription",
    capability=Capability.WRITE,
)
async def greenlake_post_events_v1beta1_subscriptions(
    ctx: Context,
    body: Annotated[list[Any], Field(description="Request body (required)")],
) -> Any:
    return await greenlake_request(
        ctx,
        "POST",
        "/events/v1beta1/subscriptions",
        body=body,
    )


@tool(
    name="greenlake_post_events_v1beta1_system_subscriptions",
    description="POST /events/v1beta1/system-subscriptions\n\ncreateSubscription\n\nCreate a new subscription",
    capability=Capability.WRITE,
)
async def greenlake_post_events_v1beta1_system_subscriptions(
    ctx: Context,
    body: Annotated[list[Any], Field(description="Request body (required)")],
) -> Any:
    return await greenlake_request(
        ctx,
        "POST",
        "/events/v1beta1/system-subscriptions",
        body=body,
    )
