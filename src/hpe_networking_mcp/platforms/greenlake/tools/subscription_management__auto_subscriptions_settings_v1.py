"""Generated GreenLake tools — DO NOT EDIT BY HAND.

Generated from the vendored spec ``vendor/greenlake/subscription-management.json`` by the
maintainer-local GreenLake generator. These modules are committed and are the
runtime source of truth; regeneration is a release-time maintainer workflow
(the generator is intentionally not committed — see ``.gitignore``).

Service: ``subscription-management``   Tag: ``auto_subscriptions_settings_v1``   Operations: 3
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
    name="greenlake_get_subscriptions_v1_auto_subscription_settings",
    description="GET /subscriptions/v1/auto-subscription-settings\n\ngetAutoSubscriptionsV1\n\nGet all configured auto-subscriptions settings",
    capability=Capability.READ,
)
async def greenlake_get_subscriptions_v1_auto_subscription_settings(
    ctx: Context,
) -> Any:
    return await greenlake_request(
        ctx,
        "GET",
        "/subscriptions/v1/auto-subscription-settings",
    )


@tool(
    name="greenlake_get_subscriptions_v1_auto_subscription_settings_id",
    description="GET /subscriptions/v1/auto-subscription-settings/{id}\n\ngetAutoSubscriptionByIdV1\n\nGet configured auto-subscriptions settings per workspace",
    capability=Capability.READ,
)
async def greenlake_get_subscriptions_v1_auto_subscription_settings_id(
    ctx: Context,
    id: Annotated[str, Field(description="The unique identifier of the workspace.")],
) -> Any:
    path = f"/subscriptions/v1/auto-subscription-settings/{path_seg(id)}"
    return await greenlake_request(
        ctx,
        "GET",
        path,
    )


@tool(
    name="greenlake_patch_subscriptions_v1_auto_subscription_settings_id",
    description="PATCH /subscriptions/v1/auto-subscription-settings/{id}\n\nupdateAutoSubscriptionsV1\n\nUpdate the configured auto-subscriptions settings of a workspace",
    capability=Capability.WRITE,
)
async def greenlake_patch_subscriptions_v1_auto_subscription_settings_id(
    ctx: Context,
    id: Annotated[str, Field(description="The unique identifier of the auto subscription settings.")],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    path = f"/subscriptions/v1/auto-subscription-settings/{path_seg(id)}"
    return await greenlake_request(
        ctx,
        "PATCH",
        path,
        body=body,
    )
