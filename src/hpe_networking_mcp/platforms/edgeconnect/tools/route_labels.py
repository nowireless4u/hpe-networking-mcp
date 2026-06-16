"""Generated EdgeConnect tools — DO NOT EDIT BY HAND.

Emitted by ``scripts/generate_edgeconnect_tools.py`` from
``vendor/edgeconnect/EdgeConnect-9-7-REST-API.json``. Regenerate via:

    uv run python scripts/generate_edgeconnect_tools.py

Tag: ``routeLabels``
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
    name="edgeconnect_get_route_labels",
    description="GET /routeLabels\n\ngetRouteLabels\n\nGet all route labels",
    capability=Capability.READ,
)
async def edgeconnect_get_route_labels(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/routeLabels",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_route_labels_next_id",
    description="GET /routeLabels/nextId\n\ngetLabelNextId\n\nGet next available route label ID",
    capability=Capability.READ,
)
async def edgeconnect_get_route_labels_next_id(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/routeLabels/nextId",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_route_labels_version_counter",
    description="GET /routeLabels/versionCounter\n\ngetLabelVersionCounter\n\nGet next version counter for route labels",
    capability=Capability.READ,
)
async def edgeconnect_get_route_labels_version_counter(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/routeLabels/versionCounter",
        query_params=None,
    )


@tool(
    name="edgeconnect_post_route_labels",
    description="POST /routeLabels\n\naddRouteLabels\n\nCreate or update route labels",
    capability=Capability.WRITE,
)
async def edgeconnect_post_route_labels(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/routeLabels",
        query_params=None,
        body=body,
    )
