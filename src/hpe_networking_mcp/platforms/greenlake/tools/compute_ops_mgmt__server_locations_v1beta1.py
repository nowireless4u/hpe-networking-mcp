"""Generated GreenLake tools — DO NOT EDIT BY HAND.

Generated from the vendored spec ``vendor/greenlake/compute-ops-mgmt.json`` by the
maintainer-local GreenLake generator. These modules are committed and are the
runtime source of truth; regeneration is a release-time maintainer workflow
(the generator is intentionally not committed — see ``.gitignore``).

Service: ``compute-ops-mgmt``   Tag: ``server_locations_v1beta1``   Operations: 3
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
    name="greenlake_delete_compute_ops_mgmt_v1beta1_server_locations_location_id_servers",
    description="DELETE /compute-ops-mgmt/v1beta1/server-locations/{location_id}/servers\n\ndelete_v1beta1_server_locations\n\nRemove location of servers",
    capability=Capability.WRITE_DELETE,
)
async def greenlake_delete_compute_ops_mgmt_v1beta1_server_locations_location_id_servers(
    ctx: Context,
    location_id: Annotated[str, Field(description="ID of the location in HPE GreenLake")],
    id: Annotated[list[str], Field(description="query parameter 'id'")],
) -> Any:
    path = f"/compute-ops-mgmt/v1beta1/server-locations/{path_seg(location_id)}/servers"
    query_params: dict[str, Any] = {}
    if id is not None:
        query_params["id"] = id
    return await greenlake_request(
        ctx,
        "DELETE",
        path,
        query_params=query_params or None,
    )


@tool(
    name="greenlake_get_compute_ops_mgmt_v1beta1_server_locations_location_id",
    description="GET /compute-ops-mgmt/v1beta1/server-locations/{location_id}\n\nget_v1beta1_server_locations\n\nGet location details",
    capability=Capability.READ,
)
async def greenlake_get_compute_ops_mgmt_v1beta1_server_locations_location_id(
    ctx: Context,
    location_id: Annotated[str, Field(description="Location ID")],
) -> Any:
    path = f"/compute-ops-mgmt/v1beta1/server-locations/{path_seg(location_id)}"
    return await greenlake_request(
        ctx,
        "GET",
        path,
    )


@tool(
    name="greenlake_post_compute_ops_mgmt_v1beta1_server_locations_location_id_servers",
    description="POST /compute-ops-mgmt/v1beta1/server-locations/{location_id}/servers\n\npost_v1beta1_server_locations\n\nAssign location to servers",
    capability=Capability.WRITE,
)
async def greenlake_post_compute_ops_mgmt_v1beta1_server_locations_location_id_servers(
    ctx: Context,
    location_id: Annotated[str, Field(description="ID of the location in HPE GreenLake")],
    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request body")] = None,
) -> Any:
    path = f"/compute-ops-mgmt/v1beta1/server-locations/{path_seg(location_id)}/servers"
    return await greenlake_request(
        ctx,
        "POST",
        path,
        body=body,
    )
