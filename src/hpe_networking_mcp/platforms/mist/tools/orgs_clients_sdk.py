"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``hpe_networking_mcp.platforms.mist._generator``
from ``vendor/mist_openapi.json``. Regenerate via:

    uv run python -m hpe_networking_mcp.platforms.mist.regenerate

Tag: ``Orgs Clients - SDK``
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
    name="mist_update_sdk_client",
    description="PUT /api/v1/orgs/{org_id}/sdkclients/{sdkclient_id}\n\nupdateSdkClient\n\nUpdate SDK Client",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_update_sdk_client(
    ctx: Context,
    org_id: Annotated[str, Field(description="path parameter 'org_id'")],
    sdkclient_id: Annotated[str, Field(description="path parameter 'sdkclient_id'")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request Body")] = None,
) -> Any:
    return await mist_request(
        ctx,
        "PUT",
        "/api/v1/orgs/{org_id}/sdkclients/{sdkclient_id}",
        path_params={"org_id": org_id, "sdkclient_id": sdkclient_id},
        query_params=None,
        body=body,
    )
