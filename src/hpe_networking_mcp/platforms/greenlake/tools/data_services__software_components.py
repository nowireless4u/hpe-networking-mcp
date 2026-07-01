"""Generated GreenLake tools — DO NOT EDIT BY HAND.

Generated from the vendored spec ``vendor/greenlake/data-services.json`` by the
maintainer-local GreenLake generator. These modules are committed and are the
runtime source of truth; regeneration is a release-time maintainer workflow
(the generator is intentionally not committed — see ``.gitignore``).

Service: ``data-services``   Tag: ``software_components``   Operations: 1
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
    name="greenlake_get_data_services_v1beta1_software_components_id_install_release",
    description="GET /data-services/v1beta1/software-components/{id}/install-release\n\nSoftwareComponentsInstall\n\nFind a Software Release to install.",
    capability=Capability.READ,
)
async def greenlake_get_data_services_v1beta1_software_components_id_install_release(
    ctx: Context,
    id: Annotated[str, Field(description="The ID of a Software Component.")],
) -> Any:
    path = f"/data-services/v1beta1/software-components/{path_seg(id)}/install-release"
    return await greenlake_request(
        ctx,
        "GET",
        path,
    )
