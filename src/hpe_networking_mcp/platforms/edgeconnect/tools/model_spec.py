"""Generated EdgeConnect tools — DO NOT EDIT BY HAND.

Emitted by ``scripts/generate_edgeconnect_tools.py`` from
``vendor/edgeconnect/EdgeConnect-9-7-REST-API.json``. Regenerate via:

    uv run python scripts/generate_edgeconnect_tools.py

Tag: ``modelSpec``
Operations in this file: 2
"""

from __future__ import annotations

from typing import Annotated, Any

from fastmcp import Context
from pydantic import Field

from hpe_networking_mcp.platforms._common.annotations import Capability
from hpe_networking_mcp.platforms.edgeconnect._registry import tool
from hpe_networking_mcp.platforms.edgeconnect.client import edgeconnect_request


@tool(
    name="edgeconnect_post_model_spec",
    description="POST /modelSpec\n\ngetModelSpec\n\nRetrieve appliance model specifications",
    capability=Capability.WRITE,
)
async def edgeconnect_post_model_spec(
    ctx: Context,
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request body")] = None,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/modelSpec",
        query_params=None,
        body=body,
    )


@tool(
    name="edgeconnect_post_model_spec_port_list",
    description="POST /modelSpec/portList\n\ngetPhysicalPortNames\n\nGet physical port names for appliance models",
    capability=Capability.WRITE,
)
async def edgeconnect_post_model_spec_port_list(
    ctx: Context,
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request body")] = None,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/modelSpec/portList",
        query_params=None,
        body=body,
    )
