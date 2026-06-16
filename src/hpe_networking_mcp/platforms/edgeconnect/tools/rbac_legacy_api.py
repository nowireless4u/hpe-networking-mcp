"""Generated EdgeConnect tools — DO NOT EDIT BY HAND.

Emitted by ``scripts/generate_edgeconnect_tools.py`` from
``vendor/edgeconnect/EdgeConnect-9-7-REST-API.json``. Regenerate via:

    uv run python scripts/generate_edgeconnect_tools.py

Tag: ``rbacLegacyApi``
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
    name="edgeconnect_delete_rbac_legacy_api",
    description="DELETE /rbac/legacyApi\n\nDeleteLegacyApiEntry37\n\nDelete legacy API transformation entry",
    capability=Capability.WRITE_DELETE,
)
async def edgeconnect_delete_rbac_legacy_api(
    ctx: Context,
    id: Annotated[
        str,
        Field(
            description="Database ID of the legacy API entry to delete. Must be a non-null, non-empty string representing an existing entry's primary key."
        ),
    ],
) -> Any:
    query_params: dict[str, Any] = {}
    if id is not None:
        query_params["id"] = id
    return await edgeconnect_request(
        ctx,
        "DELETE",
        "/rbac/legacyApi",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_rbac_legacy_api",
    description="GET /rbac/legacyApi\n\nGetLegacyApi35\n\nGet list of all legacy APIs",
    capability=Capability.READ,
)
async def edgeconnect_get_rbac_legacy_api(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/rbac/legacyApi",
        query_params=None,
    )


@tool(
    name="edgeconnect_post_rbac_legacy_api",
    description="POST /rbac/legacyApi\n\nAddLegacyApi36\n\nAdd new legacy API transformation entry",
    capability=Capability.WRITE,
)
async def edgeconnect_post_rbac_legacy_api(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/rbac/legacyApi",
        query_params=None,
        body=body,
    )


@tool(
    name="edgeconnect_put_rbac_legacy_api",
    description="PUT /rbac/legacyApi\n\nUpdateLegacyApiEntry39\n\nUpdate legacy API transformation entry",
    capability=Capability.WRITE,
)
async def edgeconnect_put_rbac_legacy_api(
    ctx: Context,
    id: Annotated[
        str,
        Field(
            description="Database ID of the legacy API entry to update. Must be a non-empty string representing a valid existing entry."
        ),
    ],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    query_params: dict[str, Any] = {}
    if id is not None:
        query_params["id"] = id
    return await edgeconnect_request(
        ctx,
        "PUT",
        "/rbac/legacyApi",
        query_params=query_params or None,
        body=body,
    )
