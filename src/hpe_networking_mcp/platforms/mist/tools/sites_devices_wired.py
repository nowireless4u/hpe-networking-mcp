"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``scripts/_mist_generator.py`` from
``vendor/mist/mist_openapi.json``. Regenerate via:

    uv run python scripts/regenerate_mist_tools.py

Tag: ``Sites Devices - Wired``
Operations in this file: 2
"""

# ruff: noqa: E501

from __future__ import annotations

from typing import Annotated, Any

from fastmcp import Context
from pydantic import Field

from hpe_networking_mcp.platforms._common.annotations import Capability
from hpe_networking_mcp.platforms.mist._client import mist_request
from hpe_networking_mcp.platforms.mist._registry import tool as _mcp_tool


@_mcp_tool(
    name="mist_delete_site_local_switch_port_config",
    description="DELETE /api/v1/sites/{site_id}/devices/{device_id}/local_port_config\n\ndeleteSiteLocalSwitchPortConfig\n\nAPI Calls delete all the existing port config local overrides, and reapply the configured planed at the device level \n(with site / template heritance).",
    capability=Capability.WRITE_DELETE,
)
async def mist_delete_site_local_switch_port_config(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    device_id: Annotated[str, Field(description="path parameter 'device_id'")],
) -> Any:
    return await mist_request(
        ctx,
        "DELETE",
        "/api/v1/sites/{site_id}/devices/{device_id}/local_port_config",
        path_params={"site_id": site_id, "device_id": device_id},
        query_params=None,
        body=None,
    )


@_mcp_tool(
    name="mist_update_site_local_switch_port_config",
    description="PUT /api/v1/sites/{site_id}/devices/{device_id}/local_port_config\n\nupdateSiteLocalSwitchPortConfig\n\nAPI Calls to add port config local overrides. This can be used by Switch Port Operators or Helpdesk administrators\nto change a Switch Port configuration without having to change the switch configuration.\n\n\nThe local overrides configured for the switchports with `no_local_overwrite`==`true` won't be applied to the switch configuration. \n\n\n> NOTE:\n>\n> When using the API Call, it is required to put send all overrides in the PUT request Payload, even the existing once. \n>\n> The current overrides ...",
    capability=Capability.WRITE,
)
async def mist_update_site_local_switch_port_config(
    ctx: Context,
    site_id: Annotated[str, Field(description="path parameter 'site_id'")],
    device_id: Annotated[str, Field(description="path parameter 'device_id'")],
    body: Annotated[
        dict[str, Any] | None,
        Field(
            default=None,
            description="Request body for PUT /api/v1/sites/{site_id}/devices/{device_id}/local_port_config",
        ),
    ] = None,
) -> Any:
    return await mist_request(
        ctx,
        "PUT",
        "/api/v1/sites/{site_id}/devices/{device_id}/local_port_config",
        path_params={"site_id": site_id, "device_id": device_id},
        query_params=None,
        body=body,
    )
