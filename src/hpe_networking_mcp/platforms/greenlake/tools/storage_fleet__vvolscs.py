"""Generated GreenLake tools — DO NOT EDIT BY HAND.

Generated from the vendored spec ``vendor/greenlake/storage-fleet.json`` by the
maintainer-local GreenLake generator. These modules are committed and are the
runtime source of truth; regeneration is a release-time maintainer workflow
(the generator is intentionally not committed — see ``.gitignore``).

Service: ``storage-fleet``   Tag: ``vvolscs``   Operations: 3
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
    name="greenlake_post_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_vvolscs",
    description="POST /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/vvolscs\n\nDeviceType4CreatevVolSC\n\nCreates VMware storage container on HPE Alletra Storage MP B10000 storage system identified by {systemId}",
    capability=Capability.WRITE,
)
async def greenlake_post_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_vvolscs(
    ctx: Context,
    systemId: Annotated[str, Field(description="systemId of the storage system")],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    path = f"/storage-fleet/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/vvolscs"
    return await greenlake_request(
        ctx,
        "POST",
        path,
        body=body,
    )


@tool(
    name="greenlake_post_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_vvolscs_vvolsc_id_attach",
    description="POST /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/vvolscs/{vvolscId}/attach\n\nDeviceType4AttachVolSC\n\nAttach host to storage container identified by {vvolscId} from HPE Alletra Storage MP B10000",
    capability=Capability.WRITE,
)
async def greenlake_post_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_vvolscs_vvolsc_id_attach(
    ctx: Context,
    systemId: Annotated[str, Field(description="systemId of the storage system")],
    vvolscId: Annotated[str, Field(description="Storage container UID")],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    path = f"/storage-fleet/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/vvolscs/{path_seg(vvolscId)}/attach"
    return await greenlake_request(
        ctx,
        "POST",
        path,
        body=body,
    )


@tool(
    name="greenlake_post_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_vvolscs_vvolsc_id_detach",
    description="POST /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/vvolscs/{vvolscId}/detach\n\nDeviceType4DetachVolSC\n\nDetach host from storage container identified by {vvolscId} from HPE Alletra Storage MP B10000",
    capability=Capability.WRITE,
)
async def greenlake_post_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_vvolscs_vvolsc_id_detach(
    ctx: Context,
    systemId: Annotated[str, Field(description="systemId of the storage system")],
    vvolscId: Annotated[str, Field(description="Storage container UID")],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    path = f"/storage-fleet/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/vvolscs/{path_seg(vvolscId)}/detach"
    return await greenlake_request(
        ctx,
        "POST",
        path,
        body=body,
    )
