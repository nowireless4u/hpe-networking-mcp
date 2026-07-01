"""Generated GreenLake tools — DO NOT EDIT BY HAND.

Generated from the vendored spec ``vendor/greenlake/subscription-management.json`` by the
maintainer-local GreenLake generator. These modules are committed and are the
runtime source of truth; regeneration is a release-time maintainer workflow
(the generator is intentionally not committed — see ``.gitignore``).

Service: ``subscription-management``   Tag: ``subscriptions_v2beta1``   Operations: 1
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
    name="greenlake_delete_subscriptions_v2beta1_subscriptions_bulk",
    description="DELETE /subscriptions/v2beta1/subscriptions/bulk\n\ndeleteSubscriptionsBulkV2Beta1\n\nUnclaim subscriptions in bulk",
    capability=Capability.WRITE_DELETE,
)
async def greenlake_delete_subscriptions_v2beta1_subscriptions_bulk(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await greenlake_request(
        ctx,
        "DELETE",
        "/subscriptions/v2beta1/subscriptions/bulk",
        body=body,
    )
