"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``scripts/_mist_generator.py``
from ``vendor/mist_openapi.json``. Regenerate via:

    uv run python scripts/regenerate_mist_tools.py

Tag: ``Self API Token``
Operations in this file: 5
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
    name="mist_create_api_token",
    description="POST /api/v1/self/apitokens\n\ncreateApiToken\n\nCreate API Token\nNote that the key is only available during creation time.",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_create_api_token(
    ctx: Context,
    body: Annotated[
        dict[str, Any] | None, Field(default=None, description="Request body for POST /api/v1/self/apitokens")
    ] = None,
) -> Any:
    return await mist_request(
        ctx,
        "POST",
        "/api/v1/self/apitokens",
        path_params=None,
        query_params=None,
        body=body,
    )


@_mcp_tool(
    name="mist_delete_api_token",
    description="DELETE /api/v1/self/apitokens/{apitoken_id}\n\ndeleteApiToken\n\nDelete an API Token",
    tags={"mist", "mist_write", "mist_write_delete"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=True),
)
async def mist_delete_api_token(
    ctx: Context,
    apitoken_id: Annotated[str, Field(description="path parameter 'apitoken_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "DELETE",
        "/api/v1/self/apitokens/{apitoken_id}",
        path_params={"apitoken_id": apitoken_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_get_api_token",
    description="GET /api/v1/self/apitokens/{apitoken_id}\n\ngetApiToken\n\nGet User API Token",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_get_api_token(
    ctx: Context,
    apitoken_id: Annotated[str, Field(description="path parameter 'apitoken_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/self/apitokens/{apitoken_id}",
        path_params={"apitoken_id": apitoken_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_list_api_tokens",
    description="GET /api/v1/self/apitokens\n\nlistApiTokens\n\nGet List of Current User API Tokens",
    tags={"mist"},
    annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
)
async def mist_list_api_tokens(
    ctx: Context,
) -> Any:
    return await mist_request(
        ctx,
        "GET",
        "/api/v1/self/apitokens",
        path_params=None,
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_update_api_token",
    description="PUT /api/v1/self/apitokens/{apitoken_id}\n\nupdateApiToken\n\nUpdate User API Token",
    tags={"mist", "mist_write"},
    annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False),
)
async def mist_update_api_token(
    ctx: Context,
    apitoken_id: Annotated[str, Field(description="path parameter 'apitoken_id'")],
    body: Annotated[
        dict[str, Any] | None,
        Field(default=None, description="Request body for PUT /api/v1/self/apitokens/{apitoken_id}"),
    ] = None,
) -> Any:
    return await mist_request(
        ctx,
        "PUT",
        "/api/v1/self/apitokens/{apitoken_id}",
        path_params={"apitoken_id": apitoken_id},
        query_params=None,
        body=body,
    )
