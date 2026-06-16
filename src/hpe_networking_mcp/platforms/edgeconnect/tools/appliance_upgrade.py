"""Generated EdgeConnect tools — DO NOT EDIT BY HAND.

Emitted by ``scripts/generate_edgeconnect_tools.py`` from
``vendor/edgeconnect/EdgeConnect-9-7-REST-API.json``. Regenerate via:

    uv run python scripts/generate_edgeconnect_tools.py

Tag: ``applianceUpgrade``
Operations in this file: 2
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
    name="edgeconnect_delete_vxoa_images",
    description="DELETE /vxoaImages\n\nVXOAImagesDelete936\n\nDelete ECOS/VXOA image",
    capability=Capability.WRITE_DELETE,
)
async def edgeconnect_delete_vxoa_images(
    ctx: Context,
    imageFile: Annotated[
        str,
        Field(
            description="The filename of the ECOS/VXOA image to delete from the Orchestrator. Must be a valid filename that exists in the images directory."
        ),
    ],
) -> Any:
    query_params: dict[str, Any] = {}
    if imageFile is not None:
        query_params["imageFile"] = imageFile
    return await edgeconnect_request(
        ctx,
        "DELETE",
        "/vxoaImages",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_vxoa_images",
    description="GET /vxoaImages\n\nVXOAImagesGet935\n\nList available ECOS/VXOA software images",
    capability=Capability.READ,
)
async def edgeconnect_get_vxoa_images(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/vxoaImages",
        query_params=None,
    )
