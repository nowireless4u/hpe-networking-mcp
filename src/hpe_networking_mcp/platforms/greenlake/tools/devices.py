# (c) Copyright 2025 Hewlett Packard Enterprise Development LP
"""GreenLake Device tools.

Ported from ``src/devices/tools/implementations/getdevicesv1.py`` and
``getdevicebyidv1.py``.

API base path: ``/devices/v1/devices``
"""

from __future__ import annotations

from typing import Annotated, Any

from fastmcp import Context
from loguru import logger
from pydantic import Field

from hpe_networking_mcp.platforms.greenlake._registry import tool
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
# greenlake_get_devices
# ---------------------------------------------------------------------------


@tool(
    name="greenlake_get_devices",
    description=(
        "Retrieve a list of devices managed in an HPE GreenLake "
        "workspace.\n\n"
        "Supports OData-style filtering, tag filtering, sorting, "
        "field selection, and pagination. Rate limit: 160 "
        "requests/min per workspace.\n\n"
        "Filterable properties: application, archived, "
        "assignedState, createdAt, deviceType, id, location, "
        "macAddress, model, partNumber, region, serialNumber, "
        "subscription, tags, tenantWorkspaceId, type, updatedAt, "
        "warranty."
    ),
    tags={"greenlake", "devices"},
    annotations={
        "title": "Get GreenLake devices",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def greenlake_get_devices(
    ctx: Context,
    filter: Annotated[
        str | None,
        Field(
            default=None,
            description=(
                "OData filter expression. Examples:\n"
                "- ``deviceType in 'COMPUTE', 'STORAGE'``\n"
                "- ``serialNumber eq 'STIAPL6404'``\n"
                "- ``createdAt ge '2024-01-18T19:53:51.480Z'``\n"
                "All filter values must be enclosed in single quotes."
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
            description=("Comma-separated sort expressions. Example: ``serialNumber,macAddress desc``."),
        ),
    ] = None,
    select: Annotated[
        list[str] | None,
        Field(
            default=None,
            description=(
                "List of property names to include in the response. Example: ``['serialNumber','macAddress']``."
            ),
        ),
    ] = None,
    limit: Annotated[
        int | str | None,
        Field(
            default=2000,
            description="Number of results to return (default 2000).",
        ),
    ] = 2000,
    offset: Annotated[
        int | str | None,
        Field(
            default=None,
            description="Zero-based offset for pagination.",
        ),
    ] = None,
) -> dict[str, Any]:
    """List devices in the GreenLake workspace."""
    logger.debug("greenlake_get_devices called")

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

        return await client.get("/devices/v1/devices", params=params)


# ---------------------------------------------------------------------------
# greenlake_get_device_by_id
# ---------------------------------------------------------------------------


@tool(
    name="greenlake_get_device_by_id",
    description=(
        "Get details on a specific HPE GreenLake device by its "
        "resource ID.\n\n"
        "Rate limit: 40 requests/min per workspace."
    ),
    tags={"greenlake", "devices"},
    annotations={
        "title": "Get GreenLake device by ID",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def greenlake_get_device_by_id(
    ctx: Context,
    id: Annotated[
        str,
        Field(description="The resource ID of the device."),
    ],
) -> dict[str, Any]:
    """Retrieve details for a single device."""
    logger.debug("greenlake_get_device_by_id called, id={}", id)

    if not id or not id.strip():
        raise ValueError("id is required and cannot be empty")

    token_manager = ctx.lifespan_context["greenlake_token_manager"]
    config = ctx.lifespan_context["config"]
    base_url = config.greenlake.api_base_url

    async with GreenLakeHttpClient(token_manager=token_manager, base_url=base_url) as client:
        return await client.get(f"/devices/v1/devices/{id}")
