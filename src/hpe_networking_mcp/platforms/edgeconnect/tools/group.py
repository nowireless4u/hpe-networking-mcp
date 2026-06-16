"""Generated EdgeConnect tools — DO NOT EDIT BY HAND.

Emitted by ``scripts/generate_edgeconnect_tools.py`` from
``vendor/edgeconnect/EdgeConnect-9-7-REST-API.json``. Regenerate via:

    uv run python scripts/generate_edgeconnect_tools.py

Tag: ``group``
Operations in this file: 5
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
    name="edgeconnect_delete_gms_group",
    description="DELETE /gms/group\n\ngroupDelete282\n\nDelete a user-defined group",
    capability=Capability.WRITE_DELETE,
)
async def edgeconnect_delete_gms_group(
    ctx: Context,
    id: Annotated[
        str,
        Field(
            description="Unique identifier of the group to delete in format '{number}.Network'. Only user-defined groups (3.Network onwards) can be deleted."
        ),
    ],
) -> Any:
    query_params: dict[str, Any] = {}
    if id is not None:
        query_params["id"] = id
    return await edgeconnect_request(
        ctx,
        "DELETE",
        "/gms/group",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_gms_group",
    description="GET /gms/group\n\ngroupGet283\n\nGet group(s) by ID or retrieve all groups",
    capability=Capability.READ,
)
async def edgeconnect_get_gms_group(
    ctx: Context,
    id: Annotated[
        str | None,
        Field(
            default=None,
            description="Group identifier in format '{number}.Network'. When omitted, returns all groups; when provided, returns the specific group.",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if id is not None:
        query_params["id"] = id
    return await edgeconnect_request(
        ctx,
        "GET",
        "/gms/group",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_gms_group_root",
    description="GET /gms/group/root\n\nrootGroupGet281\n\nGet the root group of the network hierarchy",
    capability=Capability.READ,
)
async def edgeconnect_get_gms_group_root(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/gms/group/root",
        query_params=None,
    )


@tool(
    name="edgeconnect_post_gms_group",
    description="POST /gms/group\n\ngroupUpdate284\n\nUpdate a user-defined group",
    capability=Capability.WRITE,
)
async def edgeconnect_post_gms_group(
    ctx: Context,
    id: Annotated[
        str,
        Field(
            description="Unique identifier of the group to update in format '{number}.Network'. Only user-defined groups (3.Network onwards) can be updated."
        ),
    ],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request body")] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if id is not None:
        query_params["id"] = id
    return await edgeconnect_request(
        ctx,
        "POST",
        "/gms/group",
        query_params=query_params or None,
        body=body,
    )


@tool(
    name="edgeconnect_post_gms_group_new",
    description="POST /gms/group/new\n\ngroupAdd280\n\nCreate a new user-defined group",
    capability=Capability.WRITE,
)
async def edgeconnect_post_gms_group_new(
    ctx: Context,
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request body")] = None,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/gms/group/new",
        query_params=None,
        body=body,
    )
