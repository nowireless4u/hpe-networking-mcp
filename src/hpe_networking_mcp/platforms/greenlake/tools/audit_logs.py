# (c) Copyright 2025 Hewlett Packard Enterprise Development LP
"""GreenLake Audit Logs tools.

Ported from ``src/audit-logs/tools/implementations/getauditlogs.py`` and
``getauditlogdetails.py``.

API base path: ``/audit-log/v1/logs``
"""

from __future__ import annotations

from typing import Annotated, Any

from fastmcp import Context
from loguru import logger
from pydantic import Field

from hpe_networking_mcp.platforms.greenlake._registry import mcp
from hpe_networking_mcp.platforms.greenlake.client import GreenLakeHttpClient


def _coerce_int(value: Any, name: str) -> int:
    """Coerce a string or int value to int (LLM clients sometimes send strings)."""
    if isinstance(value, int) and not isinstance(value, bool):
        return value
    if isinstance(value, str):
        try:
            return int(value)
        except (ValueError, TypeError) as e:
            raise ValueError(f"Parameter '{name}' must be an integer, got '{value}'") from e
    raise ValueError(f"Parameter '{name}' must be an integer, got {type(value).__name__}")


# ---------------------------------------------------------------------------
# greenlake_get_audit_logs
# ---------------------------------------------------------------------------

@mcp.tool(
    name="greenlake_get_audit_logs",
    description=(
        "Retrieve HPE GreenLake audit logs with optional filtering and pagination.\n\n"
        "Filter expressions use OData-style syntax: ``key eq 'value'``, "
        "``contains(key, 'value')``, ``key in ('v1','v2')`` joined by ``and``.\n\n"
        "Filterable fields: createdAt, category, description, additionalInfo/ipAddress, "
        "user/username, workspace/workspaceName, application/id, region, hasDetails."
    ),
    tags={"greenlake", "audit_logs"},
    annotations={
        "title": "Get GreenLake audit logs",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def greenlake_get_audit_logs(
    ctx: Context,
    filter: Annotated[
        str | None,
        Field(
            default=None,
            description=(
                "OData filter expression. Example: ``category eq 'User Management' "
                "and contains(description, 'logged out')``.\n"
                "All filter values must be enclosed in single quotes."
            ),
        ),
    ] = None,
    select: Annotated[
        str | None,
        Field(
            default=None,
            description=(
                "Comma-separated list of properties to include in the response. "
                "Supported: additionalInfo, createdAt, category, hasDetails, "
                "workspace/workspaceName, description, user/username."
            ),
        ),
    ] = None,
    all: Annotated[
        str | None,
        Field(
            default=None,
            description="Free-text search across all audit log properties.",
        ),
    ] = None,
    limit: Annotated[
        int | str | None,
        Field(
            default=50,
            description="Maximum number of items to return (max 2000).",
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
    """Retrieve audit logs from HPE GreenLake."""
    logger.debug("greenlake_get_audit_logs called")

    token_manager = ctx.lifespan_context["greenlake_token_manager"]
    config = ctx.lifespan_context["config"]
    base_url = config.greenlake.api_base_url

    async with GreenLakeHttpClient(token_manager=token_manager, base_url=base_url) as client:
        params: dict[str, Any] = {}
        if filter is not None:
            params["filter"] = filter
        if select is not None:
            params["select"] = select
        if all is not None:
            params["all"] = all
        if limit is not None:
            params["limit"] = _coerce_int(limit, "limit")
        if offset is not None:
            params["offset"] = _coerce_int(offset, "offset")

        return await client.get("/audit-log/v1/logs", params=params)


# ---------------------------------------------------------------------------
# greenlake_get_audit_log_details
# ---------------------------------------------------------------------------

@mcp.tool(
    name="greenlake_get_audit_log_details",
    description="Get additional detail of an HPE GreenLake audit log entry.",
    tags={"greenlake", "audit_logs"},
    annotations={
        "title": "Get GreenLake audit log details",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def greenlake_get_audit_log_details(
    ctx: Context,
    id: Annotated[
        str,
        Field(
            description=(
                "ID of the audit log record whose ``hasDetails`` value is ``true``."
            ),
        ),
    ],
) -> dict[str, Any]:
    """Retrieve detailed information for a single audit log entry."""
    logger.debug("greenlake_get_audit_log_details called, id={}", id)

    if not id or not id.strip():
        raise ValueError("id is required and cannot be empty")

    token_manager = ctx.lifespan_context["greenlake_token_manager"]
    config = ctx.lifespan_context["config"]
    base_url = config.greenlake.api_base_url

    async with GreenLakeHttpClient(token_manager=token_manager, base_url=base_url) as client:
        return await client.get(f"/audit-log/v1/logs/{id}/detail")
