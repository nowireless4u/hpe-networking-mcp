"""Generated GreenLake tools — DO NOT EDIT BY HAND.

Generated from the vendored spec ``vendor/greenlake/data-services.json`` by the
maintainer-local GreenLake generator. These modules are committed and are the
runtime source of truth; regeneration is a release-time maintainer workflow
(the generator is intentionally not committed — see ``.gitignore``).

Service: ``data-services``   Tag: ``software_upgrades``   Operations: 1
"""

# ruff: noqa: E501
from __future__ import annotations

from typing import Annotated, Any

from fastmcp import Context
from pydantic import Field

from hpe_networking_mcp.platforms._common.annotations import Capability
from hpe_networking_mcp.platforms.greenlake._registry import tool
from hpe_networking_mcp.platforms.greenlake.client import greenlake_request


@tool(
    name="greenlake_get_data_services_v1beta1_software_upgrades",
    description="GET /data-services/v1beta1/software-upgrades\n\nSoftwareUpgradesList\n\nList upgrades for a Software Release",
    capability=Capability.READ,
)
async def greenlake_get_data_services_v1beta1_software_upgrades(
    ctx: Context,
    software_component_id: Annotated[str, Field(description="The ID of a Software Component.")],
    version: Annotated[str, Field(description="The version of an installed Software Release that is being upgraded.")],
    serial_number: Annotated[
        str | None,
        Field(
            default=None,
            description="The serial number of the hardware being upgraded. Either `agent-id` or `serial-number` must be supplied.",
        ),
    ] = None,
    agent_id: Annotated[
        str | None,
        Field(
            default=None,
            description="The identifier for the virtual machine being upgraded. Either `agent-id` or `serial-number` must be supplied.",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if software_component_id is not None:
        query_params["software-component-id"] = software_component_id
    if version is not None:
        query_params["version"] = version
    if serial_number is not None:
        query_params["serial-number"] = serial_number
    if agent_id is not None:
        query_params["agent-id"] = agent_id
    return await greenlake_request(
        ctx,
        "GET",
        "/data-services/v1beta1/software-upgrades",
        query_params=query_params or None,
    )
