"""Generated EdgeConnect tools — DO NOT EDIT BY HAND.

Emitted by ``scripts/generate_edgeconnect_tools.py`` from
``vendor/edgeconnect/EdgeConnect-9-7-REST-API.json``. Regenerate via:

    uv run python scripts/generate_edgeconnect_tools.py

Tag: ``End Entity Profiles``
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
    name="edgeconnect_delete_security_end_entity_profiles",
    description="DELETE /security/endEntityProfiles\n\ndeleteEndEntityProfile\n\nDelete an existing End Entity Profile by label.",
    capability=Capability.WRITE_DELETE,
)
async def edgeconnect_delete_security_end_entity_profiles(
    ctx: Context,
    label: Annotated[
        str,
        Field(
            description="Unique label identifier of the End Entity Profile to delete. Must match an existing profile (case-sensitive)."
        ),
    ],
) -> Any:
    query_params: dict[str, Any] = {}
    if label is not None:
        query_params["label"] = label
    return await edgeconnect_request(
        ctx,
        "DELETE",
        "/security/endEntityProfiles",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_security_end_entity_profiles",
    description="GET /security/endEntityProfiles\n\ngetEndEntityProfiles\n\nRetrieve all End Entity Profiles configured in the Orchestrator.",
    capability=Capability.READ,
)
async def edgeconnect_get_security_end_entity_profiles(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/security/endEntityProfiles",
        query_params=None,
    )


@tool(
    name="edgeconnect_post_security_end_entity_profiles",
    description="POST /security/endEntityProfiles\n\ncreateEndEntityProfile\n\nCreate a new End Entity Profile for certificate enrollment configuration.",
    capability=Capability.WRITE,
)
async def edgeconnect_post_security_end_entity_profiles(
    ctx: Context,
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request body")] = None,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/security/endEntityProfiles",
        query_params=None,
        body=body,
    )


@tool(
    name="edgeconnect_put_security_end_entity_profiles",
    description="PUT /security/endEntityProfiles\n\nupdateEndEntityProfile\n\nUpdate an existing End Entity Profile's configuration.",
    capability=Capability.WRITE,
)
async def edgeconnect_put_security_end_entity_profiles(
    ctx: Context,
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request body")] = None,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "PUT",
        "/security/endEntityProfiles",
        query_params=None,
        body=body,
    )
