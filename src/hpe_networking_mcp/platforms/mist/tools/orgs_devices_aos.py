"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``scripts/_mist_generator.py`` from
``vendor/mist_openapi.json``. Regenerate via:

    uv run python scripts/regenerate_mist_tools.py

Tag: ``Orgs Devices - AOS``
Operations in this file: 1
"""

# ruff: noqa: E501

from __future__ import annotations

from typing import Annotated, Any

from fastmcp import Context
from mcp.types import ToolAnnotations
from pydantic import Field

from hpe_networking_mcp.platforms.mist._client import mist_request
from hpe_networking_mcp.platforms.mist._registry import tool as _mcp_tool


@_mcp_tool(
    name="mist_get_org_aos_register_cmd",
    description="GET /api/v1/orgs/{org_id}/aos/register_cmd\n\ngetOrgAosRegisterCmd\n\nGenerates a registration challenge token for TPM-based brownfield registration of AOS devices. The returned command string can be copied and pasted directly into an AOS device to register it with Mist.",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_get_org_aos_register_cmd(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/orgs/{org_id}/aos/register_cmd",
        path_params={"org_id": org_id},
        query_params=None,
        body=None,
    )
