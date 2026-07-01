"""Generated GreenLake tools — DO NOT EDIT BY HAND.

Generated from the vendored spec ``vendor/greenlake/compute-ops-mgmt.json`` by the
maintainer-local GreenLake generator. These modules are committed and are the
runtime source of truth; regeneration is a release-time maintainer workflow
(the generator is intentionally not committed — see ``.gitignore``).

Service: ``compute-ops-mgmt``   Tag: ``accounts_v1beta1``   Operations: 2
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
    name="greenlake_get_compute_ops_mgmt_v1beta1_accounts_id",
    description="GET /compute-ops-mgmt/v1beta1/accounts/{id}\n\nget_accounts\n\nGet account details",
    capability=Capability.READ,
)
async def greenlake_get_compute_ops_mgmt_v1beta1_accounts_id(
    ctx: Context,
    id: Annotated[str, Field(description="Application Customer ID")],
    Tenant_Acid: Annotated[
        str | None,
        Field(
            default=None,
            description="Tenant-Acid header can be used by an MSP workspace to make API calls on behalf of their tenant by specifying the tenant's application customer ID.  In order to make such an API call, the Bearer token must belong to an MSP workspace and this header value must be the application customer ID of a tenant within the MSP workspace. Use the `/compute-ops-mgmt/v1beta1/accounts` API to determine the application customer IDs for your tenant accounts.",
        ),
    ] = None,
) -> Any:
    path = f"/compute-ops-mgmt/v1beta1/accounts/{path_seg(id)}"
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
    name="greenlake_get_compute_ops_mgmt_v1beta1_accounts_id_tenants",
    description="GET /compute-ops-mgmt/v1beta1/accounts/{id}/tenants\n\nget_uidoorway_v1_tenant_details_by_id\n\nGet list of tenant accounts",
    capability=Capability.READ,
)
async def greenlake_get_compute_ops_mgmt_v1beta1_accounts_id_tenants(
    ctx: Context,
    id: Annotated[str, Field(description="Application customer ID")],
    fields: Annotated[
        list[str] | None,
        Field(
            default=None,
            description="Names of fields within the customers. Returns details of all customers for the application customer ID",
        ),
    ] = None,
    Tenant_Acid: Annotated[
        str | None,
        Field(
            default=None,
            description="Tenant-Acid header can be used by an MSP workspace to make API calls on behalf of their tenant by specifying the tenant's application customer ID.  In order to make such an API call, the Bearer token must belong to an MSP workspace and this header value must be the application customer ID of a tenant within the MSP workspace. Use the `/compute-ops-mgmt/v1beta1/accounts` API to determine the application customer IDs for your tenant accounts.",
        ),
    ] = None,
) -> Any:
    path = f"/compute-ops-mgmt/v1beta1/accounts/{path_seg(id)}/tenants"
    query_params: dict[str, Any] = {}
    if fields is not None:
        query_params["fields[]"] = fields
    header_params: dict[str, str] = {}
    if Tenant_Acid is not None:
        header_params["Tenant-Acid"] = str(Tenant_Acid)
    return await greenlake_request(
        ctx,
        "GET",
        path,
        query_params=query_params or None,
        header_params=header_params or None,
    )
