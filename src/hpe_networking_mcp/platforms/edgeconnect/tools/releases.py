"""Generated EdgeConnect tools — DO NOT EDIT BY HAND.

Emitted by ``scripts/generate_edgeconnect_tools.py`` from
``vendor/edgeconnect/EdgeConnect-9-7-REST-API.json``. Regenerate via:

    uv run python scripts/generate_edgeconnect_tools.py

Tag: ``releases``
Operations in this file: 4
"""

# ruff: noqa: E501
from __future__ import annotations

from typing import Annotated, Any

from fastmcp import Context
from pydantic import Field

from hpe_networking_mcp.platforms._common.annotations import Capability
from hpe_networking_mcp.platforms.edgeconnect._registry import tool
from hpe_networking_mcp.platforms.edgeconnect.client import edgeconnect_request


@tool(
    name="edgeconnect_get_release",
    description="GET /release\n\ngetReleases\n\nGet all available software releases",
    capability=Capability.READ,
)
async def edgeconnect_get_release(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/release",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_release_notifications",
    description="GET /release/notifications\n\ngetReleaseNotifications\n\nGet active release upgrade notifications",
    capability=Capability.READ,
)
async def edgeconnect_get_release_notifications(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/release/notifications",
        query_params=None,
    )


@tool(
    name="edgeconnect_post_release_notifications_delay",
    description="POST /release/notifications/delay\n\ndelayReleaseNotification\n\nDelay release upgrade notifications",
    capability=Capability.WRITE,
)
async def edgeconnect_post_release_notifications_delay(
    ctx: Context,
    version: Annotated[
        str | None,
        Field(
            default=None,
            description="Target release version (e.g., '9.3.0.40000'). If omitted, delays notifications for all available releases.",
        ),
    ] = None,
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request body")] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if version is not None:
        query_params["version"] = version
    return await edgeconnect_request(
        ctx,
        "POST",
        "/release/notifications/delay",
        query_params=query_params or None,
        body=body,
    )


@tool(
    name="edgeconnect_post_release_notifications_dismiss",
    description="POST /release/notifications/dismiss\n\ndismissReleaseNotification\n\nPermanently dismiss release upgrade notifications",
    capability=Capability.WRITE,
)
async def edgeconnect_post_release_notifications_dismiss(
    ctx: Context,
    version: Annotated[
        str | None,
        Field(
            default=None,
            description="Target release version to dismiss (e.g., '9.3.0.40000'). If omitted, dismisses all Orchestrator release notifications.",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if version is not None:
        query_params["version"] = version
    return await edgeconnect_request(
        ctx,
        "POST",
        "/release/notifications/dismiss",
        query_params=query_params or None,
    )
