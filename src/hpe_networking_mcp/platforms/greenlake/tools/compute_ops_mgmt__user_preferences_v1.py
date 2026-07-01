"""Generated GreenLake tools — DO NOT EDIT BY HAND.

Generated from the vendored spec ``vendor/greenlake/compute-ops-mgmt.json`` by the
maintainer-local GreenLake generator. These modules are committed and are the
runtime source of truth; regeneration is a release-time maintainer workflow
(the generator is intentionally not committed — see ``.gitignore``).

Service: ``compute-ops-mgmt``   Tag: ``user_preferences_v1``   Operations: 6
"""

# ruff: noqa: E501, N803
from __future__ import annotations

from typing import Annotated, Any

from fastmcp import Context
from pydantic import Field

from hpe_networking_mcp.platforms._common.annotations import Capability
from hpe_networking_mcp.platforms._common.url import path_seg
from hpe_networking_mcp.platforms.greenlake._registry import tool
from hpe_networking_mcp.platforms.greenlake.client import greenlake_request


@tool(
    name="greenlake_get_compute_ops_mgmt_v1_user_preferences",
    description="GET /compute-ops-mgmt/v1/user-preferences\n\nget_v1_user_preferences\n\nGet user preferences for the current user",
    capability=Capability.READ,
)
async def greenlake_get_compute_ops_mgmt_v1_user_preferences(
    ctx: Context,
    Tenant_Acid: Annotated[
        str | None,
        Field(
            default=None,
            description="Tenant-Acid header can be used by an MSP workspace to make API calls on behalf of their tenant by specifying the tenant's application customer ID.  In order to make such an API call, the Bearer token must belong to an MSP workspace and this header value must be the application customer ID of a tenant within the MSP workspace. Use the `/compute-ops-mgmt/v1beta1/accounts` API to determine the application customer IDs for your tenant accounts.",
        ),
    ] = None,
) -> Any:
    header_params: dict[str, str] = {}
    if Tenant_Acid is not None:
        header_params["Tenant-Acid"] = str(Tenant_Acid)
    return await greenlake_request(
        ctx,
        "GET",
        "/compute-ops-mgmt/v1/user-preferences",
        header_params=header_params or None,
    )


@tool(
    name="greenlake_get_compute_ops_mgmt_v1_user_preferences_id",
    description="GET /compute-ops-mgmt/v1/user-preferences/{id}\n\nget_v1_user_preference_by_id\n\nGet a specific user preference object",
    capability=Capability.READ,
)
async def greenlake_get_compute_ops_mgmt_v1_user_preferences_id(
    ctx: Context,
    id: Annotated[str, Field(description="path parameter 'id'")],
    Tenant_Acid: Annotated[
        str | None,
        Field(
            default=None,
            description="Tenant-Acid header can be used by an MSP workspace to make API calls on behalf of their tenant by specifying the tenant's application customer ID.  In order to make such an API call, the Bearer token must belong to an MSP workspace and this header value must be the application customer ID of a tenant within the MSP workspace. Use the `/compute-ops-mgmt/v1beta1/accounts` API to determine the application customer IDs for your tenant accounts.",
        ),
    ] = None,
) -> Any:
    path = f"/compute-ops-mgmt/v1/user-preferences/{path_seg(id)}"
    header_params: dict[str, str] = {}
    if Tenant_Acid is not None:
        header_params["Tenant-Acid"] = str(Tenant_Acid)
    return await greenlake_request(
        ctx,
        "GET",
        path,
        header_params=header_params or None,
    )


@tool(
    name="greenlake_post_compute_ops_mgmt_v1_user_preferences",
    description="POST /compute-ops-mgmt/v1/user-preferences\n\npost_v1_user_preferences\n\nCreate user preferences for the current user",
    capability=Capability.WRITE,
)
async def greenlake_post_compute_ops_mgmt_v1_user_preferences(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
    Tenant_Acid: Annotated[
        str | None,
        Field(
            default=None,
            description="Tenant-Acid header can be used by an MSP workspace to make API calls on behalf of their tenant by specifying the tenant's application customer ID.  In order to make such an API call, the Bearer token must belong to an MSP workspace and this header value must be the application customer ID of a tenant within the MSP workspace. Use the `/compute-ops-mgmt/v1beta1/accounts` API to determine the application customer IDs for your tenant accounts.",
        ),
    ] = None,
) -> Any:
    header_params: dict[str, str] = {}
    if Tenant_Acid is not None:
        header_params["Tenant-Acid"] = str(Tenant_Acid)
    return await greenlake_request(
        ctx,
        "POST",
        "/compute-ops-mgmt/v1/user-preferences",
        header_params=header_params or None,
        body=body,
    )


@tool(
    name="greenlake_post_compute_ops_mgmt_v1_user_preferences_subscribe",
    description="POST /compute-ops-mgmt/v1/user-preferences/subscribe\n\npost_v1_user_preferences_subscribe\n\nSubscribe users",
    capability=Capability.WRITE,
)
async def greenlake_post_compute_ops_mgmt_v1_user_preferences_subscribe(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
    Tenant_Acid: Annotated[
        str | None,
        Field(
            default=None,
            description="Tenant-Acid header can be used by an MSP workspace to make API calls on behalf of their tenant by specifying the tenant's application customer ID.  In order to make such an API call, the Bearer token must belong to an MSP workspace and this header value must be the application customer ID of a tenant within the MSP workspace. Use the `/compute-ops-mgmt/v1beta1/accounts` API to determine the application customer IDs for your tenant accounts.",
        ),
    ] = None,
) -> Any:
    header_params: dict[str, str] = {}
    if Tenant_Acid is not None:
        header_params["Tenant-Acid"] = str(Tenant_Acid)
    return await greenlake_request(
        ctx,
        "POST",
        "/compute-ops-mgmt/v1/user-preferences/subscribe",
        header_params=header_params or None,
        body=body,
    )


@tool(
    name="greenlake_post_compute_ops_mgmt_v1_user_preferences_unsubscribe",
    description="POST /compute-ops-mgmt/v1/user-preferences/unsubscribe\n\npost_v1_user_preferences_unsubscribe\n\nUnsubscribe users",
    capability=Capability.WRITE,
)
async def greenlake_post_compute_ops_mgmt_v1_user_preferences_unsubscribe(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
    Tenant_Acid: Annotated[
        str | None,
        Field(
            default=None,
            description="Tenant-Acid header can be used by an MSP workspace to make API calls on behalf of their tenant by specifying the tenant's application customer ID.  In order to make such an API call, the Bearer token must belong to an MSP workspace and this header value must be the application customer ID of a tenant within the MSP workspace. Use the `/compute-ops-mgmt/v1beta1/accounts` API to determine the application customer IDs for your tenant accounts.",
        ),
    ] = None,
) -> Any:
    header_params: dict[str, str] = {}
    if Tenant_Acid is not None:
        header_params["Tenant-Acid"] = str(Tenant_Acid)
    return await greenlake_request(
        ctx,
        "POST",
        "/compute-ops-mgmt/v1/user-preferences/unsubscribe",
        header_params=header_params or None,
        body=body,
    )


@tool(
    name="greenlake_put_compute_ops_mgmt_v1_user_preferences_id",
    description="PUT /compute-ops-mgmt/v1/user-preferences/{id}\n\nput_v1_user_preferences\n\nUpdate user preferences",
    capability=Capability.WRITE,
)
async def greenlake_put_compute_ops_mgmt_v1_user_preferences_id(
    ctx: Context,
    id: Annotated[str, Field(description="path parameter 'id'")],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
    Tenant_Acid: Annotated[
        str | None,
        Field(
            default=None,
            description="Tenant-Acid header can be used by an MSP workspace to make API calls on behalf of their tenant by specifying the tenant's application customer ID.  In order to make such an API call, the Bearer token must belong to an MSP workspace and this header value must be the application customer ID of a tenant within the MSP workspace. Use the `/compute-ops-mgmt/v1beta1/accounts` API to determine the application customer IDs for your tenant accounts.",
        ),
    ] = None,
) -> Any:
    path = f"/compute-ops-mgmt/v1/user-preferences/{path_seg(id)}"
    header_params: dict[str, str] = {}
    if Tenant_Acid is not None:
        header_params["Tenant-Acid"] = str(Tenant_Acid)
    return await greenlake_request(
        ctx,
        "PUT",
        path,
        header_params=header_params or None,
        body=body,
    )
