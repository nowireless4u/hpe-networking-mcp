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
from fastmcp.exceptions import ToolError
from loguru import logger
from pydantic import Field

from hpe_networking_mcp.platforms._common.annotations import Capability
from hpe_networking_mcp.platforms._common.url import path_seg
from hpe_networking_mcp.platforms.greenlake._registry import tool
from hpe_networking_mcp.platforms.greenlake.client import get_greenlake_client

# ---------------------------------------------------------------------------
# greenlake_get_workspace
# ---------------------------------------------------------------------------


@tool(
    name="greenlake_get_workspace",
    description=("Retrieve basic workspace information for a given HPE GreenLake workspace ID."),
    tags={"greenlake", "workspaces"},
    capability=Capability.READ,
)
async def greenlake_get_workspace(
    ctx: Context,
    workspaceId: Annotated[  # noqa: N803
        str,
        Field(
            description=("The unique identifier of the workspace. Example: 7600415a-8876-5722-9f3c-b0fd11112283"),
        ),
    ],
) -> dict[str, Any]:
    """Retrieve basic information for a single workspace."""
    logger.debug(
        "greenlake_get_workspace called, workspaceId={}",
        workspaceId,
    )

    if not workspaceId or not workspaceId.strip():
        raise ToolError({"status_code": 400, "message": "workspaceId is required and cannot be empty"})

    async with get_greenlake_client(ctx) as client:
        return await client.get(f"/workspaces/v1/workspaces/{path_seg(workspaceId)}")


# ---------------------------------------------------------------------------
# greenlake_get_workspace_details
# ---------------------------------------------------------------------------


@tool(
    name="greenlake_get_workspace_details",
    description=("Retrieve detailed contact information for an HPE GreenLake workspace."),
    tags={"greenlake", "workspaces"},
    capability=Capability.READ,
)
async def greenlake_get_workspace_details(
    ctx: Context,
    workspaceId: Annotated[  # noqa: N803
        str,
        Field(
            description=("The unique identifier of the workspace. Example: 7600415a-8876-5722-9f3c-b0fd11112283"),
        ),
    ],
) -> dict[str, Any]:
    """Retrieve detailed workspace information (contact info)."""
    logger.debug(
        "greenlake_get_workspace_details called, workspaceId={}",
        workspaceId,
    )

    if not workspaceId or not workspaceId.strip():
        raise ToolError({"status_code": 400, "message": "workspaceId is required and cannot be empty"})

    async with get_greenlake_client(ctx) as client:
        return await client.get(f"/workspaces/v1/workspaces/{path_seg(workspaceId)}/contact")
