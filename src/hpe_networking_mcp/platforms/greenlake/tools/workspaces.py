# (c) Copyright 2025 Hewlett Packard Enterprise Development LP
"""GreenLake Workspace tools.

Ported from ``src/workspaces/tools/implementations/
get_workspace_workspaces_v1_workspaces_workspaceid_get.py`` and
``get_workspace_detailed_info_workspaces_v1_workspaces_wo_5c14f2bc.py``.

API base path: ``/workspaces/v1/workspaces``
"""

from __future__ import annotations

from typing import Annotated, Any

from fastmcp import Context
from loguru import logger
from pydantic import Field

from hpe_networking_mcp.platforms.greenlake._registry import mcp
from hpe_networking_mcp.platforms.greenlake.client import GreenLakeHttpClient


# ---------------------------------------------------------------------------
# greenlake_get_workspace
# ---------------------------------------------------------------------------

@mcp.tool(
    name="greenlake_get_workspace",
    description="Retrieve basic workspace information for a given HPE GreenLake workspace ID.",
    tags={"greenlake", "workspaces"},
    annotations={
        "title": "Get GreenLake workspace",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def greenlake_get_workspace(
    ctx: Context,
    workspaceId: Annotated[
        str,
        Field(
            description="The unique identifier of the workspace. Example: 7600415a-8876-5722-9f3c-b0fd11112283",
        ),
    ],
) -> dict[str, Any]:
    """Retrieve basic information for a single workspace."""
    logger.debug("greenlake_get_workspace called, workspaceId={}", workspaceId)

    if not workspaceId or not workspaceId.strip():
        raise ValueError("workspaceId is required and cannot be empty")

    token_manager = ctx.lifespan_context["greenlake_token_manager"]
    config = ctx.lifespan_context["config"]
    base_url = config.greenlake.api_base_url

    async with GreenLakeHttpClient(token_manager=token_manager, base_url=base_url) as client:
        return await client.get(f"/workspaces/v1/workspaces/{workspaceId}")


# ---------------------------------------------------------------------------
# greenlake_get_workspace_details
# ---------------------------------------------------------------------------

@mcp.tool(
    name="greenlake_get_workspace_details",
    description="Retrieve detailed contact information for an HPE GreenLake workspace.",
    tags={"greenlake", "workspaces"},
    annotations={
        "title": "Get GreenLake workspace details",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def greenlake_get_workspace_details(
    ctx: Context,
    workspaceId: Annotated[
        str,
        Field(
            description="The unique identifier of the workspace. Example: 7600415a-8876-5722-9f3c-b0fd11112283",
        ),
    ],
) -> dict[str, Any]:
    """Retrieve detailed workspace information (contact info)."""
    logger.debug("greenlake_get_workspace_details called, workspaceId={}", workspaceId)

    if not workspaceId or not workspaceId.strip():
        raise ValueError("workspaceId is required and cannot be empty")

    token_manager = ctx.lifespan_context["greenlake_token_manager"]
    config = ctx.lifespan_context["config"]
    base_url = config.greenlake.api_base_url

    async with GreenLakeHttpClient(token_manager=token_manager, base_url=base_url) as client:
        return await client.get(f"/workspaces/v1/workspaces/{workspaceId}/contact")
