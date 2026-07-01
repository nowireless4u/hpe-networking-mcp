"""Generated GreenLake tools — DO NOT EDIT BY HAND.

Generated from the vendored spec ``vendor/greenlake/virtualization.json`` by the
maintainer-local GreenLake generator. These modules are committed and are the
runtime source of truth; regeneration is a release-time maintainer workflow
(the generator is intentionally not committed — see ``.gitignore``).

Service: ``virtualization``   Tag: ``csp_machine_instances``   Operations: 4
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
    name="greenlake_delete_virtualization_v1beta1_csp_machine_instances_id",
    description="DELETE /virtualization/v1beta1/csp-machine-instances/{id}\n\nTerminateCSPVMInstance\n\nTerminate a CSP Machine Instance",
    capability=Capability.WRITE_DELETE,
)
async def greenlake_delete_virtualization_v1beta1_csp_machine_instances_id(
    ctx: Context,
    id: Annotated[str, Field(description="Unique identifier of a CSP machine instance")],
) -> Any:
    path = f"/virtualization/v1beta1/csp-machine-instances/{path_seg(id)}"
    return await greenlake_request(
        ctx,
        "DELETE",
        path,
    )


@tool(
    name="greenlake_post_virtualization_v1beta1_csp_machine_instances",
    description="POST /virtualization/v1beta1/csp-machine-instances\n\nCreateCSPMachineInstance\n\nCreate CSP Machine Instance",
    capability=Capability.WRITE,
)
async def greenlake_post_virtualization_v1beta1_csp_machine_instances(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await greenlake_request(
        ctx,
        "POST",
        "/virtualization/v1beta1/csp-machine-instances",
        body=body,
    )


@tool(
    name="greenlake_post_virtualization_v1beta1_csp_machine_instances_id_power_off",
    description="POST /virtualization/v1beta1/csp-machine-instances/{id}/power-off\n\nPowerOffCSPVMInstance\n\nPower Off CSP Machine Instance",
    capability=Capability.WRITE,
)
async def greenlake_post_virtualization_v1beta1_csp_machine_instances_id_power_off(
    ctx: Context,
    id: Annotated[str, Field(description="Unique identifier of a CSP machine instance")],
) -> Any:
    path = f"/virtualization/v1beta1/csp-machine-instances/{path_seg(id)}/power-off"
    return await greenlake_request(
        ctx,
        "POST",
        path,
    )


@tool(
    name="greenlake_post_virtualization_v1beta1_csp_machine_instances_id_power_on",
    description="POST /virtualization/v1beta1/csp-machine-instances/{id}/power-on\n\nPowerOnCSPVMInstance\n\nPower On CSP Machine Instance",
    capability=Capability.WRITE,
)
async def greenlake_post_virtualization_v1beta1_csp_machine_instances_id_power_on(
    ctx: Context,
    id: Annotated[str, Field(description="Unique identifier of a CSP machine instance")],
) -> Any:
    path = f"/virtualization/v1beta1/csp-machine-instances/{path_seg(id)}/power-on"
    return await greenlake_request(
        ctx,
        "POST",
        path,
    )
