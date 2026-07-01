"""Generated GreenLake tools — DO NOT EDIT BY HAND.

Generated from the vendored spec ``vendor/greenlake/virtualization.json`` by the
maintainer-local GreenLake generator. These modules are committed and are the
runtime source of truth; regeneration is a release-time maintainer workflow
(the generator is intentionally not committed — see ``.gitignore``).

Service: ``virtualization``   Tag: ``virtual_machines``   Operations: 12
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
    name="greenlake_delete_virtualization_v1beta1_virtual_machines_vm_id",
    description="DELETE /virtualization/v1beta1/virtual-machines/{vm-id}\n\nVMDelete\n\nDelete a virtual machine",
    capability=Capability.WRITE_DELETE,
)
async def greenlake_delete_virtualization_v1beta1_virtual_machines_vm_id(
    ctx: Context,
    vm_id: Annotated[str, Field(description="path parameter 'vm-id'")],
) -> Any:
    path = f"/virtualization/v1beta1/virtual-machines/{path_seg(vm_id)}"
    return await greenlake_request(
        ctx,
        "DELETE",
        path,
    )


@tool(
    name="greenlake_get_virtualization_v1beta1_virtual_machines",
    description="GET /virtualization/v1beta1/virtual-machines\n\nVirtualMachinesList\n\nGet all virtual machines across registered hypervisor managers.",
    capability=Capability.READ,
)
async def greenlake_get_virtualization_v1beta1_virtual_machines(
    ctx: Context,
    offset: Annotated[
        int | None,
        Field(default=None, description="The number of items to skip before starting to collect the result set"),
    ] = None,
    limit: Annotated[int | None, Field(default=None, description="The numbers of items to return")] = None,
    filter: Annotated[
        str | None,
        Field(
            default=None,
            description='The filter query parameter is used to filter the set of resources returned in the response. The returned set of resources must match the criteria in the filter query parameter.  A comparison compares a property name to a literal. The following comparisons are supported: * “eq” : Is a property equal to value. Valid for number, boolean and string properties. * “ne” : Is a property not equal to value. Valid for number, boolean and string properties. * “gt” : Is a property greater than a value. Valid for number or string timestamp properties. * “lt” : Is a property less than a value. Valid for number or string timestamp properties * “in” : Is a value in a property (that is an array of strings)  Examples: * GET /virtualization/v1beta1/virtual-machines?filter="appType eq VMWARE" * GET /virtualization/v1beta1/virtual-machines?filter="appType eq VMWARE and status eq ERROR"  Filters are supported on the following attributes: * status * state * appType * hypervisorManagerInfo/name * hypervisorManagerInfo/displayName * hypervisorManagerInfo/id * hostInfo/id * hostInfo/name * hostInfo/displayName * clusterInfo/id * clusterInfo/name * clusterInfo/displayName * protectionJobInfo/protectionPolicyInfo/id * protectionJobInfo/protectionPolicyInfo/name * vmProtectionGroupsInfo/id * vmProtectionGroupsInfo/name * appInfo/vmware/type * appInfo/vmware/moref * appInfo/vmware/datastoresInfo/id * appInfo/vmware/datastoresInfo/name * appInfo/vmware/datastoresInfo/displayName * volumesInfo/id * volumesInfo/storageSystemInfo/id * volumesInfo/storageSystemInfo/serialNumber * volumesInfo/storageSystemInfo/name * volumesInfo/storageSystemInfo/vendorName * volumesInfo/storageFolderInfo/id * volumesInfo/storageFolderInfo/name * volumesInfo/storagePoolInfo/id * volumesInfo/storagePoolInfo/name * powerState * createdAt * name * services * allowedOperations * hciClusterUuid * id * type * capacityInBytes * computeInfo/numCpuCores * computeInfo/memorySizeInMib * vmPerfMetricInfo/cpuAllocatedInMhz * vmPerfMetricInfo/cpuUsedInMhz * vmPerfMetricInfo/storageAllocatedInKb * vmPerfMetricInfo/storageUsedInBytes * vmPerfMetricInfo/memoryAllocatedInMb * vmPerfMetricInfo/memoryUsedInMb * vmPerfMetricInfo/totalReadIops * vmPerfMetricInfo/totalWriteIops * vmPerfMetricInfo/averageReadLatency * vmPerfMetricInfo/averageWriteLatency * displayName * protectionStatus * recoveryPointsExist * vclsVm',
        ),
    ] = None,
    sort: Annotated[
        str | None,
        Field(
            default=None,
            description='A comma separated list of properties to sort by, followed by a direction indicator ("asc" or "desc"). If no direction indicator is specified, the default order is ascending.',
        ),
    ] = None,
    select: Annotated[
        str | None,
        Field(
            default=None,
            description="The select query parameter is used to limit the properties returned with a resource or collection-level GET. Multiple properties can be listed to be returned. The server must only return the set of properties requested by the client. The property “select” is the name of the select query parameter; its value is the list of properties to return separated by commas.",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if offset is not None:
        query_params["offset"] = offset
    if limit is not None:
        query_params["limit"] = limit
    if filter is not None:
        query_params["filter"] = filter
    if sort is not None:
        query_params["sort"] = sort
    if select is not None:
        query_params["select"] = select
    return await greenlake_request(
        ctx,
        "GET",
        "/virtualization/v1beta1/virtual-machines",
        query_params=query_params or None,
    )


@tool(
    name="greenlake_get_virtualization_v1beta1_virtual_machines_vm_id",
    description="GET /virtualization/v1beta1/virtual-machines/{vm-id}\n\nVirtualMachine\n\nGet a virtual machine identified by {vm-id}",
    capability=Capability.READ,
)
async def greenlake_get_virtualization_v1beta1_virtual_machines_vm_id(
    ctx: Context,
    vm_id: Annotated[str, Field(description="path parameter 'vm-id'")],
) -> Any:
    path = f"/virtualization/v1beta1/virtual-machines/{path_seg(vm_id)}"
    return await greenlake_request(
        ctx,
        "GET",
        path,
    )


@tool(
    name="greenlake_post_virtualization_v1beta1_virtual_machines",
    description="POST /virtualization/v1beta1/virtual-machines\n\nHCIDeployVM\n\nDeploy virtual machine",
    capability=Capability.WRITE,
)
async def greenlake_post_virtualization_v1beta1_virtual_machines(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await greenlake_request(
        ctx,
        "POST",
        "/virtualization/v1beta1/virtual-machines",
        body=body,
    )


@tool(
    name="greenlake_post_virtualization_v1beta1_virtual_machines_migrate",
    description="POST /virtualization/v1beta1/virtual-machines/migrate\n\nMigrateVM\n\nMigrate virtual machines",
    capability=Capability.WRITE,
)
async def greenlake_post_virtualization_v1beta1_virtual_machines_migrate(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
    parameter_type: Annotated[
        str | None, Field(default=None, description="Type of the query parameter (vms or sourceDataStoreIDs)")
    ] = None,
    vms: Annotated[
        list[str] | None,
        Field(
            default=None,
            description="A list of VM IDs to migrate or a list of SourceDatastoreIDs. If you specify the list of SourceDatastoreIDs, all VMs within the specified datastores are migrated. If you specify a list of VM IDs, only those VMs are migrated.",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if parameter_type is not None:
        query_params["parameter-type"] = parameter_type
    if vms is not None:
        query_params["vms"] = vms
    return await greenlake_request(
        ctx,
        "POST",
        "/virtualization/v1beta1/virtual-machines/migrate",
        query_params=query_params or None,
        body=body,
    )


@tool(
    name="greenlake_post_virtualization_v1beta1_virtual_machines_vm_id_power_off",
    description="POST /virtualization/v1beta1/virtual-machines/{vm-id}/power-off\n\nVMPowerOff\n\nPower off a virtual machine",
    capability=Capability.WRITE,
)
async def greenlake_post_virtualization_v1beta1_virtual_machines_vm_id_power_off(
    ctx: Context,
    vm_id: Annotated[str, Field(description="path parameter 'vm-id'")],
) -> Any:
    path = f"/virtualization/v1beta1/virtual-machines/{path_seg(vm_id)}/power-off"
    return await greenlake_request(
        ctx,
        "POST",
        path,
    )


@tool(
    name="greenlake_post_virtualization_v1beta1_virtual_machines_vm_id_power_on",
    description="POST /virtualization/v1beta1/virtual-machines/{vm-id}/power-on\n\nVMPowerOn\n\nPower on a virtual machine",
    capability=Capability.WRITE,
)
async def greenlake_post_virtualization_v1beta1_virtual_machines_vm_id_power_on(
    ctx: Context,
    vm_id: Annotated[str, Field(description="path parameter 'vm-id'")],
) -> Any:
    path = f"/virtualization/v1beta1/virtual-machines/{path_seg(vm_id)}/power-on"
    return await greenlake_request(
        ctx,
        "POST",
        path,
    )


@tool(
    name="greenlake_post_virtualization_v1beta1_virtual_machines_vm_id_refresh",
    description="POST /virtualization/v1beta1/virtual-machines/{vm-id}/refresh\n\nVMRefresh\n\nRefresh the specified virtual machine instance",
    capability=Capability.WRITE,
)
async def greenlake_post_virtualization_v1beta1_virtual_machines_vm_id_refresh(
    ctx: Context,
    vm_id: Annotated[str, Field(description="path parameter 'vm-id'")],
) -> Any:
    path = f"/virtualization/v1beta1/virtual-machines/{path_seg(vm_id)}/refresh"
    return await greenlake_request(
        ctx,
        "POST",
        path,
    )


@tool(
    name="greenlake_post_virtualization_v1beta1_virtual_machines_vm_id_reset",
    description="POST /virtualization/v1beta1/virtual-machines/{vm-id}/reset\n\nVMPowerReset\n\nReset a virtual machine",
    capability=Capability.WRITE,
)
async def greenlake_post_virtualization_v1beta1_virtual_machines_vm_id_reset(
    ctx: Context,
    vm_id: Annotated[str, Field(description="path parameter 'vm-id'")],
) -> Any:
    path = f"/virtualization/v1beta1/virtual-machines/{path_seg(vm_id)}/reset"
    return await greenlake_request(
        ctx,
        "POST",
        path,
    )


@tool(
    name="greenlake_post_virtualization_v1beta1_virtual_machines_vm_id_restart_guest_os",
    description="POST /virtualization/v1beta1/virtual-machines/{vm-id}/restart-guest-os\n\nVMRestartGuestOS\n\nRestart guest OS of a virtual machine",
    capability=Capability.WRITE,
)
async def greenlake_post_virtualization_v1beta1_virtual_machines_vm_id_restart_guest_os(
    ctx: Context,
    vm_id: Annotated[str, Field(description="path parameter 'vm-id'")],
) -> Any:
    path = f"/virtualization/v1beta1/virtual-machines/{path_seg(vm_id)}/restart-guest-os"
    return await greenlake_request(
        ctx,
        "POST",
        path,
    )


@tool(
    name="greenlake_post_virtualization_v1beta1_virtual_machines_vm_id_shutdown_guest_os",
    description="POST /virtualization/v1beta1/virtual-machines/{vm-id}/shutdown-guest-os\n\nVMShutdownGuestOS\n\nShutdown guest OS of a virtual machine",
    capability=Capability.WRITE,
)
async def greenlake_post_virtualization_v1beta1_virtual_machines_vm_id_shutdown_guest_os(
    ctx: Context,
    vm_id: Annotated[str, Field(description="path parameter 'vm-id'")],
) -> Any:
    path = f"/virtualization/v1beta1/virtual-machines/{path_seg(vm_id)}/shutdown-guest-os"
    return await greenlake_request(
        ctx,
        "POST",
        path,
    )


@tool(
    name="greenlake_post_virtualization_v1beta1_virtual_machines_vm_id_update_hardware",
    description="POST /virtualization/v1beta1/virtual-machines/{vm-id}/update-hardware\n\nEditVM\n\nReconfigure virtual machine hardware configurations",
    capability=Capability.WRITE,
)
async def greenlake_post_virtualization_v1beta1_virtual_machines_vm_id_update_hardware(
    ctx: Context,
    vm_id: Annotated[str, Field(description="path parameter 'vm-id'")],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    path = f"/virtualization/v1beta1/virtual-machines/{path_seg(vm_id)}/update-hardware"
    return await greenlake_request(
        ctx,
        "POST",
        path,
        body=body,
    )
