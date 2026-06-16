"""Generated EdgeConnect tools — DO NOT EDIT BY HAND.

Emitted by ``scripts/generate_edgeconnect_tools.py`` from
``vendor/edgeconnect/EdgeConnect-9-7-REST-API.json``. Regenerate via:

    uv run python scripts/generate_edgeconnect_tools.py

Tag: ``shell``
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
    name="edgeconnect_get_shell_shell_access_setting",
    description="GET /shell/shellAccessSetting\n\ngetShellAccessSetting556\n\nGet the current shell access security setting on Orchestrator",
    capability=Capability.READ,
)
async def edgeconnect_get_shell_shell_access_setting(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/shell/shellAccessSetting",
        query_params=None,
    )


@tool(
    name="edgeconnect_post_shell_shell_access_setting",
    description="POST /shell/shellAccessSetting\n\nsetShellAccessSetting557\n\nUpdate the shell access security setting on Orchestrator",
    capability=Capability.WRITE,
)
async def edgeconnect_post_shell_shell_access_setting(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/shell/shellAccessSetting",
        query_params=None,
        body=body,
    )
