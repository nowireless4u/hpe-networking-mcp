"""Generated EdgeConnect tools — DO NOT EDIT BY HAND.

Emitted by ``scripts/generate_edgeconnect_tools.py`` from
``vendor/edgeconnect/EdgeConnect-9-7-REST-API.json``. Regenerate via:

    uv run python scripts/generate_edgeconnect_tools.py

Tag: ``gmsNotification``
Operations in this file: 3
"""

# ruff: noqa: E501, N803
from __future__ import annotations

from typing import Annotated, Any

from fastmcp import Context
from pydantic import Field

from hpe_networking_mcp.platforms._common.annotations import Capability
from hpe_networking_mcp.platforms.edgeconnect._registry import tool
from hpe_networking_mcp.platforms.edgeconnect.client import edgeconnect_request


@tool(
    name="edgeconnect_delete_notification",
    description="DELETE /notification\n\ndelNotification476\n\nDelete the Orchestrator notification banner",
    capability=Capability.WRITE_DELETE,
)
async def edgeconnect_delete_notification(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "DELETE",
        "/notification",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_notification",
    description="GET /notification\n\ngetNotification477\n\nRetrieve the Orchestrator notification banner",
    capability=Capability.READ,
)
async def edgeconnect_get_notification(
    ctx: Context,
    If_None_Match: Annotated[
        str | None,
        Field(
            default=None,
            description="ETag value from a previous response. If the notification has not changed, a 304 Not Modified response is returned.",
        ),
    ] = None,
) -> Any:
    header_params: dict[str, Any] = {}
    if If_None_Match is not None:
        header_params["If-None-Match"] = If_None_Match
    return await edgeconnect_request(
        ctx,
        "GET",
        "/notification",
        query_params=None,
        header_params=header_params or None,
    )


@tool(
    name="edgeconnect_post_notification",
    description="POST /notification\n\npostNotification478\n\nCreate or update the Orchestrator notification banner",
    capability=Capability.WRITE,
)
async def edgeconnect_post_notification(
    ctx: Context,
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request body")] = None,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/notification",
        query_params=None,
        body=body,
    )
