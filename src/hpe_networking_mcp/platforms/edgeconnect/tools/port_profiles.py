"""Generated EdgeConnect tools — DO NOT EDIT BY HAND.

Emitted by ``scripts/generate_edgeconnect_tools.py`` from
``vendor/edgeconnect/EdgeConnect-9-7-REST-API.json``. Regenerate via:

    uv run python scripts/generate_edgeconnect_tools.py

Tag: ``portProfiles``
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
    name="edgeconnect_delete_port_profiles_config",
    description="DELETE /portProfiles/config\n\nportProfilesDelete499\n\nDelete a Deployment Profile template",
    capability=Capability.WRITE_DELETE,
)
async def edgeconnect_delete_port_profiles_config(
    ctx: Context,
    id: Annotated[
        str,
        Field(
            description="The unique identifier (UUID) of the Deployment Profile to delete. This is a system-generated value returned when creating or listing profiles."
        ),
    ],
) -> Any:
    query_params: dict[str, Any] = {}
    if id is not None:
        query_params["id"] = id
    return await edgeconnect_request(
        ctx,
        "DELETE",
        "/portProfiles/config",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_port_profiles_config",
    description="GET /portProfiles/config\n\nportProfilesGet500\n\nRetrieve all Deployment Profile templates",
    capability=Capability.READ,
)
async def edgeconnect_get_port_profiles_config(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/portProfiles/config",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_port_profiles_is_label_in_use",
    description="GET /portProfiles/isLabelInUse\n\nportProfilesLabelInUseGet502\n\nCheck if interface label is in use by deployment profiles",
    capability=Capability.READ,
)
async def edgeconnect_get_port_profiles_is_label_in_use(
    ctx: Context,
    id: Annotated[
        str, Field(description="The unique identifier of the interface label to check. Must not be null or empty.")
    ],
    side: Annotated[
        str,
        Field(description="Specifies which side of the interface to check. Case-insensitive comparison is performed."),
    ],
) -> Any:
    query_params: dict[str, Any] = {}
    if id is not None:
        query_params["id"] = id
    if side is not None:
        query_params["side"] = side
    return await edgeconnect_request(
        ctx,
        "GET",
        "/portProfiles/isLabelInUse",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_post_port_profiles_config",
    description="POST /portProfiles/config\n\nportProfilesPost498\n\nCreate a new Deployment Profile template",
    capability=Capability.WRITE,
)
async def edgeconnect_post_port_profiles_config(
    ctx: Context,
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request body")] = None,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/portProfiles/config",
        query_params=None,
        body=body,
    )


@tool(
    name="edgeconnect_put_port_profiles_config",
    description="PUT /portProfiles/config\n\nportProfilesPut501\n\nUpdate an existing Deployment Profile template",
    capability=Capability.WRITE,
)
async def edgeconnect_put_port_profiles_config(
    ctx: Context,
    id: Annotated[
        str,
        Field(
            description="The unique identifier (UUID) of the Deployment Profile to update. Must match an existing profile."
        ),
    ],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request body")] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if id is not None:
        query_params["id"] = id
    return await edgeconnect_request(
        ctx,
        "PUT",
        "/portProfiles/config",
        query_params=query_params or None,
        body=body,
    )
