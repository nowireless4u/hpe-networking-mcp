# (c) Copyright 2025 Hewlett Packard Enterprise Development LP
"""GreenLake User tools.

Ported from ``src/users/tools/implementations/get_users_identity_v1_users_get.py``
and ``get_user_detailed_identity_v1_users_id_get.py``.

API base path: ``/identity/v1/users``
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
# greenlake_get_users
# ---------------------------------------------------------------------------

@mcp.tool(
    name="greenlake_get_users",
    description=(
        "Retrieve a list of users in an HPE GreenLake workspace.\n\n"
        "Supports OData-style filtering and pagination. All users are returned "
        "when no filters are provided.\n\n"
        "Filterable properties: id, username, userStatus, createdAt, updatedAt, lastLogin.\n"
        "userStatus values (case-sensitive): UNVERIFIED, VERIFIED, BLOCKED, "
        "DELETE_IN_PROGRESS, DELETED, SUSPENDED.\n\n"
        "Rate limit: 300 requests/min per workspace."
    ),
    tags={"greenlake", "users"},
    annotations={
        "title": "Get GreenLake users",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def greenlake_get_users(
    ctx: Context,
    filter: Annotated[
        str | None,
        Field(
            default=None,
            description=(
                "OData filter expression. Examples:\n"
                "- ``username eq 'user@example.com'``\n"
                "- ``userStatus ne 'UNVERIFIED'``\n"
                "- ``createdAt gt '2020-09-21T14:19:09.769747'``\n"
                "All filter values must be enclosed in single quotes."
            ),
        ),
    ] = None,
    limit: Annotated[
        int | str | None,
        Field(
            default=300,
            description="Maximum number of entries per page (max 600, default 300).",
        ),
    ] = 300,
    offset: Annotated[
        int | str | None,
        Field(
            default=None,
            description="Pagination offset (number of pages to skip).",
        ),
    ] = None,
) -> dict[str, Any]:
    """List users in the GreenLake workspace."""
    logger.debug("greenlake_get_users called")

    token_manager = ctx.lifespan_context["greenlake_token_manager"]
    config = ctx.lifespan_context["config"]
    base_url = config.greenlake.api_base_url

    async with GreenLakeHttpClient(token_manager=token_manager, base_url=base_url) as client:
        params: dict[str, Any] = {}
        if filter is not None:
            params["filter"] = filter
        if limit is not None:
            params["limit"] = _coerce_int(limit, "limit")
        if offset is not None:
            params["offset"] = _coerce_int(offset, "offset")

        return await client.get("/identity/v1/users", params=params)


# ---------------------------------------------------------------------------
# greenlake_get_user_details
# ---------------------------------------------------------------------------

@mcp.tool(
    name="greenlake_get_user_details",
    description="Retrieve a single HPE GreenLake user by user ID.",
    tags={"greenlake", "users"},
    annotations={
        "title": "Get GreenLake user details",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def greenlake_get_user_details(
    ctx: Context,
    id: Annotated[
        str,
        Field(
            description="The unique identifier of the user. Example: 7600415a-8876-5722-9f3c-b0fd11112283",
        ),
    ],
) -> dict[str, Any]:
    """Retrieve detailed information for a single user."""
    logger.debug("greenlake_get_user_details called, id={}", id)

    if not id or not id.strip():
        raise ValueError("id is required and cannot be empty")

    token_manager = ctx.lifespan_context["greenlake_token_manager"]
    config = ctx.lifespan_context["config"]
    base_url = config.greenlake.api_base_url

    async with GreenLakeHttpClient(token_manager=token_manager, base_url=base_url) as client:
        return await client.get(f"/identity/v1/users/{id}")
