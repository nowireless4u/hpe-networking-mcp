"""Generated EdgeConnect tools — DO NOT EDIT BY HAND.

Generated from ``vendor/edgeconnect/EdgeConnect-9-7-REST-API.json`` by the
maintainer-local EdgeConnect generator. These generated modules are committed
and are the runtime source of truth; regeneration is a release-time maintainer
workflow (the generator is intentionally not committed — see ``.gitignore``).

Tag: ``apiKey``
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
    name="edgeconnect_delete_api_key",
    description="DELETE /apiKey\n\nDeleteApiKeyEntry37\n\nDelete API key",
    capability=Capability.WRITE_DELETE,
)
async def edgeconnect_delete_api_key(
    ctx: Context,
    name: Annotated[
        str, Field(description="The unique name of the API key to delete. Must match an existing key exactly.")
    ],
) -> Any:
    query_params: dict[str, Any] = {}
    if name is not None:
        query_params["name"] = name
    return await edgeconnect_request(
        ctx,
        "DELETE",
        "/apiKey",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_api_key",
    description="GET /apiKey\n\nGetApiKeys35\n\nGet API keys",
    capability=Capability.READ,
)
async def edgeconnect_get_api_key(
    ctx: Context,
    name: Annotated[
        str | None,
        Field(
            default=None,
            description="Filter by API key name to retrieve a specific key. If omitted, returns all API keys.",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if name is not None:
        query_params["name"] = name
    return await edgeconnect_request(
        ctx,
        "GET",
        "/apiKey",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_post_api_key",
    description="POST /apiKey\n\nAddApiKey36\n\nCreate new API key",
    capability=Capability.WRITE,
)
async def edgeconnect_post_api_key(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/apiKey",
        query_params=None,
        body=body,
    )


@tool(
    name="edgeconnect_put_api_key",
    description="PUT /apiKey\n\nUpdateApiKeyEntry39\n\nUpdate API key entry",
    capability=Capability.WRITE,
)
async def edgeconnect_put_api_key(
    ctx: Context,
    name: Annotated[
        str, Field(description="The unique name of the API key to update. Must match an existing key exactly.")
    ],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    query_params: dict[str, Any] = {}
    if name is not None:
        query_params["name"] = name
    return await edgeconnect_request(
        ctx,
        "PUT",
        "/apiKey",
        query_params=query_params or None,
        body=body,
    )
