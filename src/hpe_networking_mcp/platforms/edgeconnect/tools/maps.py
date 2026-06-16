"""Generated EdgeConnect tools — DO NOT EDIT BY HAND.

Emitted by ``scripts/generate_edgeconnect_tools.py`` from
``vendor/edgeconnect/EdgeConnect-9-7-REST-API.json``. Regenerate via:

    uv run python scripts/generate_edgeconnect_tools.py

Tag: ``maps``
Operations in this file: 2
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
    name="edgeconnect_get_maps_get_uploaded_maps",
    description="GET /maps/getUploadedMaps\n\ngetUploadedMaps461\n\nRetrieve list of uploaded custom topology map images",
    capability=Capability.READ,
)
async def edgeconnect_get_maps_get_uploaded_maps(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/maps/getUploadedMaps",
        query_params=None,
    )


@tool(
    name="edgeconnect_post_maps_delete_uploaded_map",
    description="POST /maps/deleteUploadedMap\n\ndeleteUploadedMap460\n\nDelete an uploaded custom topology map image",
    capability=Capability.WRITE,
)
async def edgeconnect_post_maps_delete_uploaded_map(
    ctx: Context,
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request body")] = None,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/maps/deleteUploadedMap",
        query_params=None,
        body=body,
    )
