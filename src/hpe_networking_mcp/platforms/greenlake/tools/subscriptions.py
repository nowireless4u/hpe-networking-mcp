# (c) Copyright 2025 Hewlett Packard Enterprise Development LP
"""GreenLake Subscription tools.

Ported from ``src/subscriptions/tools/implementations/getsubscriptionsv1.py``
and ``getsubscriptiondetailsbyidv1.py``.

API base path: ``/subscriptions/v1/subscriptions``
"""

from __future__ import annotations

from typing import Annotated, Any

from fastmcp import Context
from loguru import logger
from pydantic import Field

from hpe_networking_mcp.platforms.greenlake._registry import mcp
from hpe_networking_mcp.platforms.greenlake.client import GreenLakeHttpClient


def _coerce_int(value: Any, name: str) -> int:
    """Coerce a string or int value to int."""
    if isinstance(value, int) and not isinstance(value, bool):
        return value
    if isinstance(value, str):
        try:
            return int(value)
        except (ValueError, TypeError) as e:
            raise ValueError(f"Parameter '{name}' must be an integer, got '{value}'") from e
    raise ValueError(f"Parameter '{name}' must be an integer, got {type(value).__name__}")


# ---------------------------------------------------------------------------
# greenlake_get_subscriptions
# ---------------------------------------------------------------------------


@mcp.tool(
    name="greenlake_get_subscriptions",
    description=(
        "Retrieve subscriptions managed in an HPE GreenLake "
        "workspace.\n\n"
        "Supports OData-style filtering, tag filtering, sorting, "
        "field selection, and pagination. Rate limit: 60 "
        "requests/min per workspace.\n\n"
        "Filterable properties: availableQuantity, contract, "
        "createdAt, endTime, id, isEval, key, productType, "
        "quantity, sku, skuDescription, startTime, "
        "subscriptionStatus, subscriptionType, tags, tier, type, "
        "updatedAt."
    ),
    tags={"greenlake", "subscriptions"},
    annotations={
        "title": "Get GreenLake subscriptions",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def greenlake_get_subscriptions(
    ctx: Context,
    filter: Annotated[
        str | None,
        Field(
            default=None,
            description=(
                "OData filter expression. Examples:\n"
                "- ``key eq 'STIQQ4L04'``\n"
                "- ``subscriptionType in 'CENTRAL_STORAGE', "
                "'CENTRAL_CONTROLLER'``\n"
                "- ``startTime gt '2024-01-23T00:00:00.000Z' "
                "and endTime lt '2025-02-22T00:00:00.000Z'``\n"
                "All filter values must be enclosed in "
                "single quotes."
            ),
        ),
    ] = None,
    filter_tags: Annotated[
        str | None,
        Field(
            default=None,
            alias="filter-tags",
            description=("Tag filter expression. Example: ``'city' eq 'London' and 'street' eq 'Piccadilly'``."),
        ),
    ] = None,
    sort: Annotated[
        str | None,
        Field(
            default=None,
            description=("Comma-separated sort expressions. Example: ``key, quote desc``."),
        ),
    ] = None,
    select: Annotated[
        list[str] | None,
        Field(
            default=None,
            description=("List of property names to include in the response. Example: ``['id','key']``."),
        ),
    ] = None,
    limit: Annotated[
        int | str | None,
        Field(
            default=50,
            description="Number of results to return (default 50).",
        ),
    ] = 50,
    offset: Annotated[
        int | str | None,
        Field(
            default=None,
            description="Zero-based offset for pagination.",
        ),
    ] = None,
) -> dict[str, Any]:
    """List subscriptions in the GreenLake workspace."""
    logger.debug("greenlake_get_subscriptions called")

    token_manager = ctx.lifespan_context["greenlake_token_manager"]
    config = ctx.lifespan_context["config"]
    base_url = config.greenlake.api_base_url

    async with GreenLakeHttpClient(token_manager=token_manager, base_url=base_url) as client:
        params: dict[str, Any] = {}
        if filter is not None:
            params["filter"] = filter
        if filter_tags is not None:
            params["filter-tags"] = filter_tags
        if sort is not None:
            params["sort"] = sort
        if select is not None:
            params["select"] = select
        if limit is not None:
            params["limit"] = _coerce_int(limit, "limit")
        if offset is not None:
            params["offset"] = _coerce_int(offset, "offset")

        return await client.get("/subscriptions/v1/subscriptions", params=params)


# ---------------------------------------------------------------------------
# greenlake_get_subscription_details
# ---------------------------------------------------------------------------


@mcp.tool(
    name="greenlake_get_subscription_details",
    description=(
        "Get detailed information for a single HPE GreenLake "
        "subscription by ID.\n\n"
        "Rate limit: 20 requests/min per workspace."
    ),
    tags={"greenlake", "subscriptions"},
    annotations={
        "title": "Get GreenLake subscription details",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def greenlake_get_subscription_details(
    ctx: Context,
    id: Annotated[
        str,
        Field(description="The unique identifier of the subscription."),
    ],
) -> dict[str, Any]:
    """Retrieve detailed information for a single subscription."""
    logger.debug("greenlake_get_subscription_details called, id={}", id)

    if not id or not id.strip():
        raise ValueError("id is required and cannot be empty")

    token_manager = ctx.lifespan_context["greenlake_token_manager"]
    config = ctx.lifespan_context["config"]
    base_url = config.greenlake.api_base_url

    async with GreenLakeHttpClient(token_manager=token_manager, base_url=base_url) as client:
        return await client.get(f"/subscriptions/v1/subscriptions/{id}")
