"""Generated GreenLake tools — DO NOT EDIT BY HAND.

Generated from the vendored spec ``vendor/greenlake/compute-ops-mgmt.json`` by the
maintainer-local GreenLake generator. These modules are committed and are the
runtime source of truth; regeneration is a release-time maintainer workflow
(the generator is intentionally not committed — see ``.gitignore``).

Service: ``compute-ops-mgmt``   Tag: ``user_preferences_v1beta1``   Operations: 4
"""

# ruff: noqa: E501
from __future__ import annotations

from typing import Annotated, Any

from fastmcp import Context
from pydantic import Field

from hpe_networking_mcp.platforms._common.annotations import Capability
from hpe_networking_mcp.platforms._common.url import path_seg
from hpe_networking_mcp.platforms.greenlake._registry import tool
from hpe_networking_mcp.platforms.greenlake.client import greenlake_request


@tool(
    name="greenlake_get_compute_ops_mgmt_v1beta1_user_preferences",
    description="GET /compute-ops-mgmt/v1beta1/user-preferences\n\nget_v1beta1_user_preferences\n\nGet user preferences for the current user",
    capability=Capability.READ,
)
async def greenlake_get_compute_ops_mgmt_v1beta1_user_preferences(
    ctx: Context,
) -> Any:
    return await greenlake_request(
        ctx,
        "GET",
        "/compute-ops-mgmt/v1beta1/user-preferences",
    )


@tool(
    name="greenlake_get_compute_ops_mgmt_v1beta1_user_preferences_id",
    description="GET /compute-ops-mgmt/v1beta1/user-preferences/{id}\n\nget_v1beta1_user_preference_by_id\n\nGet a specific user preference object",
    capability=Capability.READ,
)
async def greenlake_get_compute_ops_mgmt_v1beta1_user_preferences_id(
    ctx: Context,
    id: Annotated[str, Field(description="path parameter 'id'")],
) -> Any:
    path = f"/compute-ops-mgmt/v1beta1/user-preferences/{path_seg(id)}"
    return await greenlake_request(
        ctx,
        "GET",
        path,
    )


@tool(
    name="greenlake_post_compute_ops_mgmt_v1beta1_user_preferences",
    description="POST /compute-ops-mgmt/v1beta1/user-preferences\n\npost_v1beta1_user_preferences\n\nCreate user preferences for the current user",
    capability=Capability.WRITE,
)
async def greenlake_post_compute_ops_mgmt_v1beta1_user_preferences(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await greenlake_request(
        ctx,
        "POST",
        "/compute-ops-mgmt/v1beta1/user-preferences",
        body=body,
    )


@tool(
    name="greenlake_put_compute_ops_mgmt_v1beta1_user_preferences_id",
    description="PUT /compute-ops-mgmt/v1beta1/user-preferences/{id}\n\nput_v1beta1_user_preferences\n\nUpdate user preferences",
    capability=Capability.WRITE,
)
async def greenlake_put_compute_ops_mgmt_v1beta1_user_preferences_id(
    ctx: Context,
    id: Annotated[str, Field(description="path parameter 'id'")],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    path = f"/compute-ops-mgmt/v1beta1/user-preferences/{path_seg(id)}"
    return await greenlake_request(
        ctx,
        "PUT",
        path,
        body=body,
    )
