"""Generated GreenLake tools — DO NOT EDIT BY HAND.

Generated from the vendored spec ``vendor/greenlake/storage-fleet.json`` by the
maintainer-local GreenLake generator. These modules are committed and are the
runtime source of truth; regeneration is a release-time maintainer workflow
(the generator is intentionally not committed — see ``.gitignore``).

Service: ``storage-fleet``   Tag: ``system_settings``   Operations: 66
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
    name="greenlake_delete_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_alert_contacts_id",
    description="DELETE /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/alert-contacts/{id}\n\nDeviceType4AlertContactsDelete\n\nDelete Alert/Email contact for HPE Alletra Storage MP B10000 storage system identified by {id}",
    capability=Capability.WRITE_DELETE,
)
async def greenlake_delete_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_alert_contacts_id(
    ctx: Context,
    systemId: Annotated[str, Field(description="systemId of the storage system")],
    id: Annotated[str, Field(description="Unique Identifier of the alert contact")],
) -> Any:
    path = f"/storage-fleet/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/alert-contacts/{path_seg(id)}"
    return await greenlake_request(
        ctx,
        "DELETE",
        path,
    )


@tool(
    name="greenlake_delete_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_mail_settings",
    description="DELETE /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/mail-settings\n\nDeviceType4MailSettingsDelete\n\nDelete SMTP/mail server settings",
    capability=Capability.WRITE_DELETE,
)
async def greenlake_delete_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_mail_settings(
    ctx: Context,
    systemId: Annotated[str, Field(description="systemId of the storage system")],
) -> Any:
    path = f"/storage-fleet/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/mail-settings"
    return await greenlake_request(
        ctx,
        "DELETE",
        path,
    )


@tool(
    name="greenlake_delete_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_quorum_witness_replication_partner_id",
    description="DELETE /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/quorum-witness/{replicationPartnerId}\n\nDeviceType4DeleteQuorumWitness\n\nDelete quorum witness identified by {replicationPartnerId} on HPE Alletra Storage MP B10000 storage system identified by {systemId}",
    capability=Capability.WRITE_DELETE,
)
async def greenlake_delete_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_quorum_witness_replication_partner_id(
    ctx: Context,
    systemId: Annotated[str, Field(description="systemId of the storage system")],
    replicationPartnerId: Annotated[str, Field(description="ID of device-type4 replication partner")],
) -> Any:
    path = f"/storage-fleet/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/quorum-witness/{path_seg(replicationPartnerId)}"
    return await greenlake_request(
        ctx,
        "DELETE",
        path,
    )


@tool(
    name="greenlake_delete_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_snmp_mgr_id",
    description="DELETE /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/snmp-mgr/{id}\n\nDeviceType4NetworkServiceSnmpMgrDelete\n\nDelete SNMP manager settings identified by {id}",
    capability=Capability.WRITE_DELETE,
)
async def greenlake_delete_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_snmp_mgr_id(
    ctx: Context,
    systemId: Annotated[str, Field(description="systemId of the storage system")],
    id: Annotated[str, Field(description="ID of the SNMP manager")],
) -> Any:
    path = f"/storage-fleet/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/snmp-mgr/{path_seg(id)}"
    return await greenlake_request(
        ctx,
        "DELETE",
        path,
    )


@tool(
    name="greenlake_delete_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_vm_manager_settings_vcenter_setting_id",
    description="DELETE /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/vm-manager-settings/{vcenterSettingId}\n\nDeviceType4DeleteVCenterSettings\n\nDelete vCenter setting identified by {vcenterSettingId} on HPE Alletra Storage MP B10000 storage system identified by {systemId}",
    capability=Capability.WRITE_DELETE,
)
async def greenlake_delete_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_vm_manager_settings_vcenter_setting_id(
    ctx: Context,
    systemId: Annotated[str, Field(description="systemId of the storage system")],
    vcenterSettingId: Annotated[str, Field(description="UID(vcenterSettingId) of the storage system")],
) -> Any:
    path = f"/storage-fleet/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/vm-manager-settings/{path_seg(vcenterSettingId)}"
    return await greenlake_request(
        ctx,
        "DELETE",
        path,
    )


@tool(
    name="greenlake_delete_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_vvolscs_vvolsc_id",
    description="DELETE /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/vvolscs/{vvolscId}\n\nDeviceType4StorageContainerDeleteById\n\nDelete storage container of HPE Alletra Storage MP B10000 storage system identified by {id}",
    capability=Capability.WRITE_DELETE,
)
async def greenlake_delete_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_vvolscs_vvolsc_id(
    ctx: Context,
    systemId: Annotated[str, Field(description="systemId of the storage system")],
    vvolscId: Annotated[str, Field(description="Storage container UID")],
) -> Any:
    path = f"/storage-fleet/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/vvolscs/{path_seg(vvolscId)}"
    return await greenlake_request(
        ctx,
        "DELETE",
        path,
    )


@tool(
    name="greenlake_get_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_alert_contacts",
    description="GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/alert-contacts\n\nDeviceType4AlertContactsList\n\nGet alert-contact details for an HPE Alletra Storage MP B10000 storage system",
    capability=Capability.READ,
)
async def greenlake_get_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_alert_contacts(
    ctx: Context,
    systemId: Annotated[str, Field(description="systemId of the storage system")],
    limit: Annotated[int | None, Field(default=None, description="Number of items to return at a time")] = None,
    offset: Annotated[
        int | None, Field(default=None, description="The offset of the first item in the collection to return")
    ] = None,
    select: Annotated[
        str | None,
        Field(default=None, description="Query to select only the required parameters, separated by . if nested"),
    ] = None,
) -> Any:
    path = f"/storage-fleet/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/alert-contacts"
    query_params: dict[str, Any] = {}
    if limit is not None:
        query_params["limit"] = limit
    if offset is not None:
        query_params["offset"] = offset
    if select is not None:
        query_params["select"] = select
    return await greenlake_request(
        ctx,
        "GET",
        path,
        query_params=query_params or None,
    )


@tool(
    name="greenlake_get_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_alert_contacts_id",
    description="GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/alert-contacts/{id}\n\nDeviceType4AlertContactsGetById\n\nGet alert-contact details for an HPE Alletra Storage MP B10000 storage system identified by {id}",
    capability=Capability.READ,
)
async def greenlake_get_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_alert_contacts_id(
    ctx: Context,
    systemId: Annotated[str, Field(description="systemId of the storage system")],
    id: Annotated[str, Field(description="Unique Identifier of the alert contact")],
    select: Annotated[
        str | None,
        Field(default=None, description="Query to select only the required parameters, separated by . if nested"),
    ] = None,
) -> Any:
    path = f"/storage-fleet/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/alert-contacts/{path_seg(id)}"
    query_params: dict[str, Any] = {}
    if select is not None:
        query_params["select"] = select
    return await greenlake_request(
        ctx,
        "GET",
        path,
        query_params=query_params or None,
    )


@tool(
    name="greenlake_get_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_certificates",
    description="GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/certificates\n\nDeviceType4CertificatesList\n\nGet array certificates by HPE Alletra Storage MP B10000",
    capability=Capability.READ,
)
async def greenlake_get_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_certificates(
    ctx: Context,
    systemId: Annotated[str, Field(description="systemId of the storage system")],
    select: Annotated[
        str | None,
        Field(default=None, description="Query to select only the required parameters, separated by . if nested"),
    ] = None,
    limit: Annotated[int | None, Field(default=None, description="Number of items to return at a time")] = None,
    offset: Annotated[
        int | None, Field(default=None, description="The offset of the first item in the collection to return")
    ] = None,
    filter: Annotated[
        str | None, Field(default=None, description="Lucene query to filter Certificates by Key.")
    ] = None,
) -> Any:
    path = f"/storage-fleet/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/certificates"
    query_params: dict[str, Any] = {}
    if select is not None:
        query_params["select"] = select
    if limit is not None:
        query_params["limit"] = limit
    if offset is not None:
        query_params["offset"] = offset
    if filter is not None:
        query_params["filter"] = filter
    return await greenlake_request(
        ctx,
        "GET",
        path,
        query_params=query_params or None,
    )


@tool(
    name="greenlake_get_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_certificates_id",
    description="GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/certificates/{id}\n\nDeviceType4CertificatesGetById\n\nGet array certificates by HPE Alletra Storage MP B10000 identified by {id}",
    capability=Capability.READ,
)
async def greenlake_get_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_certificates_id(
    ctx: Context,
    systemId: Annotated[str, Field(description="systemId of the storage system")],
    id: Annotated[str, Field(description="ID of the certificate")],
    select: Annotated[
        str | None,
        Field(default=None, description="Query to select only the required parameters, separated by . if nested"),
    ] = None,
) -> Any:
    path = f"/storage-fleet/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/certificates/{path_seg(id)}"
    query_params: dict[str, Any] = {}
    if select is not None:
        query_params["select"] = select
    return await greenlake_request(
        ctx,
        "GET",
        path,
        query_params=query_params or None,
    )


@tool(
    name="greenlake_get_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_cim",
    description="GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/cim\n\nDeviceType4NetworkServiceCimGet\n\nGet CIM Network-Service details for an HPE Alletra Storage MP B10000 storage system",
    capability=Capability.READ,
)
async def greenlake_get_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_cim(
    ctx: Context,
    systemId: Annotated[str, Field(description="systemId of the storage system")],
    select: Annotated[
        str | None,
        Field(default=None, description="Query to select only the required parameters, separated by . if nested"),
    ] = None,
) -> Any:
    path = f"/storage-fleet/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/cim"
    query_params: dict[str, Any] = {}
    if select is not None:
        query_params["select"] = select
    return await greenlake_request(
        ctx,
        "GET",
        path,
        query_params=query_params or None,
    )


@tool(
    name="greenlake_get_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_mail_settings",
    description="GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/mail-settings\n\nDeviceType4MailSettingsGet\n\nGet the system's SMTP/Mail server settigs",
    capability=Capability.READ,
)
async def greenlake_get_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_mail_settings(
    ctx: Context,
    systemId: Annotated[str, Field(description="systemId of the storage system")],
    select: Annotated[
        str | None,
        Field(default=None, description="Query to select only the required parameters, separated by . if nested"),
    ] = None,
) -> Any:
    path = f"/storage-fleet/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/mail-settings"
    query_params: dict[str, Any] = {}
    if select is not None:
        query_params["select"] = select
    return await greenlake_request(
        ctx,
        "GET",
        path,
        query_params=query_params or None,
    )


@tool(
    name="greenlake_get_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_network_settings",
    description="GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/network-settings\n\nDeviceType4NetworkSettingsGet\n\nGet Network-Settings details for an HPE Alletra Storage MP B10000 storage system",
    capability=Capability.READ,
)
async def greenlake_get_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_network_settings(
    ctx: Context,
    systemId: Annotated[str, Field(description="systemId of the storage system")],
    select: Annotated[
        str | None,
        Field(default=None, description="Query to select only the required parameters, separated by . if nested"),
    ] = None,
) -> Any:
    path = f"/storage-fleet/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/network-settings"
    query_params: dict[str, Any] = {}
    if select is not None:
        query_params["select"] = select
    return await greenlake_request(
        ctx,
        "GET",
        path,
        query_params=query_params or None,
    )


@tool(
    name="greenlake_get_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_nodes_node_id_service_ports",
    description="GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/nodes/{nodeId}/service-ports\n\nDeviceType4NodeServicePortsGetById\n\nGet service ports for nodes of all storage systems of HPE Alletra Storage MP B10000 identified by {systemId} and {nodeId }",
    capability=Capability.READ,
)
async def greenlake_get_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_nodes_node_id_service_ports(
    ctx: Context,
    nodeId: Annotated[str, Field(description="Primary ID of the node")],
    systemId: Annotated[str, Field(description="systemId of the storage system")],
    limit: Annotated[int | None, Field(default=None, description="Number of items to return at a time")] = None,
    offset: Annotated[
        int | None, Field(default=None, description="The offset of the first item in the collection to return")
    ] = None,
    filter: Annotated[str | None, Field(default=None, description="oData query to filter systems by Key.")] = None,
    select: Annotated[
        str | None,
        Field(default=None, description="Query to select only the required parameters, separated by . if nested"),
    ] = None,
) -> Any:
    path = (
        f"/storage-fleet/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/nodes/{path_seg(nodeId)}/service-ports"
    )
    query_params: dict[str, Any] = {}
    if limit is not None:
        query_params["limit"] = limit
    if offset is not None:
        query_params["offset"] = offset
    if filter is not None:
        query_params["filter"] = filter
    if select is not None:
        query_params["select"] = select
    return await greenlake_request(
        ctx,
        "GET",
        path,
        query_params=query_params or None,
    )


@tool(
    name="greenlake_get_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_quorum_witness",
    description="GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/quorum-witness\n\nDeviceType4GetQuorumWitness\n\nGet quorum witness configuration details from HPE Alletra Storage MP B10000 storage system identified by {systemId}",
    capability=Capability.READ,
)
async def greenlake_get_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_quorum_witness(
    ctx: Context,
    systemId: Annotated[str, Field(description="systemId of the storage system")],
    limit: Annotated[int | None, Field(default=None, description="Number of items to return at a time")] = None,
    offset: Annotated[
        int | None, Field(default=None, description="The offset of the first item in the collection to return")
    ] = None,
    filter: Annotated[str | None, Field(default=None, description="oData query to filter witness by key.")] = None,
    sort: Annotated[str | None, Field(default=None, description="oData query to sort witness resource by key.")] = None,
    select: Annotated[
        str | None,
        Field(default=None, description="Query to select only the required parameters, separated by . if nested"),
    ] = None,
) -> Any:
    path = f"/storage-fleet/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/quorum-witness"
    query_params: dict[str, Any] = {}
    if limit is not None:
        query_params["limit"] = limit
    if offset is not None:
        query_params["offset"] = offset
    if filter is not None:
        query_params["filter"] = filter
    if sort is not None:
        query_params["sort"] = sort
    if select is not None:
        query_params["select"] = select
    return await greenlake_request(
        ctx,
        "GET",
        path,
        query_params=query_params or None,
    )


@tool(
    name="greenlake_get_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_quorum_witness_replication_partner_id",
    description="GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/quorum-witness/{replicationPartnerId}\n\nDeviceType4GetQuorumWitnessWithId\n\nGet details of quorum witness configured on replication partner identified by {replicationPartnerId} on HPE Alletra Storage MP B10000 storage system identified by {systemId}",
    capability=Capability.READ,
)
async def greenlake_get_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_quorum_witness_replication_partner_id(
    ctx: Context,
    systemId: Annotated[str, Field(description="systemId of the storage system")],
    replicationPartnerId: Annotated[str, Field(description="ID of device-type4 replication partner")],
    select: Annotated[
        str | None,
        Field(default=None, description="Query to select only the required parameters, separated by . if nested"),
    ] = None,
) -> Any:
    path = f"/storage-fleet/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/quorum-witness/{path_seg(replicationPartnerId)}"
    query_params: dict[str, Any] = {}
    if select is not None:
        query_params["select"] = select
    return await greenlake_request(
        ctx,
        "GET",
        path,
        query_params=query_params or None,
    )


@tool(
    name="greenlake_get_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_remotecopylinks_performance",
    description="GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/remotecopylinks-performance\n\nDeviceType4RemoteCopyLinksPerformanceHistoryGet\n\nGet details of performance metrics of remote copy links on storage system identified by {systemid}",
    capability=Capability.READ,
)
async def greenlake_get_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_remotecopylinks_performance(
    ctx: Context,
    systemId: Annotated[str, Field(description="systemId of the storage system")],
    report_type: Annotated[
        str | None,
        Field(
            default=None,
            description="parameter will be set to report type requested. For api users, set parameter as ApiUser",
        ),
    ] = None,
    range: Annotated[
        str | None,
        Field(default=None, description="range will define start and end time in which query has to be made."),
    ] = None,
    time_interval_min: Annotated[
        int | None, Field(default=None, description="It defines granularity in minutes.")
    ] = None,
    compare_by: Annotated[
        str | None,
        Field(
            default=None,
            description="compareBy will define top and compare metrics for which query has to be made. Allowed values: `linkThroughput, linkRoundTripTime, transmittedData`",
        ),
    ] = None,
    group_by: Annotated[
        str | None,
        Field(
            default=None,
            description="groupBy will define comma separated groupBy parameters. Allowed value: `replicationPartnerName, portNsp`",
        ),
    ] = None,
    metric_type: Annotated[
        str | None, Field(default=None, description="metricType will define comma separated metrics")
    ] = None,
    filter: Annotated[
        str | None,
        Field(
            default=None,
            description="filter will define objects to be filtered. Filterable columns are: * `remoteCopyLinkId` - id of the remote copy link * `targetName` - name of the replication partner",
        ),
    ] = None,
) -> Any:
    path = f"/storage-fleet/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/remotecopylinks-performance"
    query_params: dict[str, Any] = {}
    if report_type is not None:
        query_params["report-type"] = report_type
    if range is not None:
        query_params["range"] = range
    if time_interval_min is not None:
        query_params["time-interval-min"] = time_interval_min
    if compare_by is not None:
        query_params["compare-by"] = compare_by
    if group_by is not None:
        query_params["group-by"] = group_by
    if metric_type is not None:
        query_params["metric-type"] = metric_type
    if filter is not None:
        query_params["filter"] = filter
    return await greenlake_request(
        ctx,
        "GET",
        path,
        query_params=query_params or None,
    )


@tool(
    name="greenlake_get_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_replication_partners",
    description="GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/replication-partners\n\nDeviceType4GetReplicationPartners\n\nGet details of replication partners on HPE Alletra Storage MP B10000 storage system identified by {systemId}",
    capability=Capability.READ,
)
async def greenlake_get_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_replication_partners(
    ctx: Context,
    systemId: Annotated[str, Field(description="systemId of the storage system")],
    limit: Annotated[int | None, Field(default=None, description="Number of items to return at a time")] = None,
    offset: Annotated[
        int | None, Field(default=None, description="The offset of the first item in the collection to return")
    ] = None,
    filter: Annotated[
        str | None, Field(default=None, description="oData query to filter replication partners by key.")
    ] = None,
    sort: Annotated[str | None, Field(default=None, description="oData query to sort nodes resource by key.")] = None,
    include_indirect_partners: Annotated[
        bool | None,
        Field(
            default=None,
            description="Include indirect partners. Indirect partners are excluded by default. This parameter cannot be used with other query parameters.",
        ),
    ] = None,
    select: Annotated[
        str | None,
        Field(default=None, description="Query to select only the required parameters, separated by . if nested"),
    ] = None,
) -> Any:
    path = f"/storage-fleet/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/replication-partners"
    query_params: dict[str, Any] = {}
    if limit is not None:
        query_params["limit"] = limit
    if offset is not None:
        query_params["offset"] = offset
    if filter is not None:
        query_params["filter"] = filter
    if sort is not None:
        query_params["sort"] = sort
    if include_indirect_partners is not None:
        query_params["include-indirect-partners"] = include_indirect_partners
    if select is not None:
        query_params["select"] = select
    return await greenlake_request(
        ctx,
        "GET",
        path,
        query_params=query_params or None,
    )


@tool(
    name="greenlake_get_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_replication_partners_replication_partner_id",
    description="GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/replication-partners/{replicationPartnerId}\n\nDeviceType4GetReplicationPartnerWithId\n\nGet details of replication partner identified by {replicationPartnerId} on HPE Alletra Storage MP B10000 storage system identified by {systemId}",
    capability=Capability.READ,
)
async def greenlake_get_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_replication_partners_replication_partner_id(
    ctx: Context,
    systemId: Annotated[str, Field(description="systemId of the storage system")],
    replicationPartnerId: Annotated[str, Field(description="ID of device-type4 replication partner")],
    select: Annotated[
        str | None,
        Field(default=None, description="Query to select only the required parameters, separated by . if nested"),
    ] = None,
) -> Any:
    path = f"/storage-fleet/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/replication-partners/{path_seg(replicationPartnerId)}"
    query_params: dict[str, Any] = {}
    if select is not None:
        query_params["select"] = select
    return await greenlake_request(
        ctx,
        "GET",
        path,
        query_params=query_params or None,
    )


@tool(
    name="greenlake_get_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_service_ports",
    description="GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/service-ports\n\nDeviceType4NodeServicePortsList\n\nGet service ports for nodes of all storage systems of HPE Alletra Storage MP B10000 identified by {systemId}",
    capability=Capability.READ,
)
async def greenlake_get_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_service_ports(
    ctx: Context,
    systemId: Annotated[str, Field(description="systemId of the storage system")],
    limit: Annotated[int | None, Field(default=None, description="Number of items to return at a time")] = None,
    offset: Annotated[
        int | None, Field(default=None, description="The offset of the first item in the collection to return")
    ] = None,
    filter: Annotated[str | None, Field(default=None, description="oData query to filter systems by Key.")] = None,
    select: Annotated[
        str | None,
        Field(default=None, description="Query to select only the required parameters, separated by . if nested"),
    ] = None,
) -> Any:
    path = f"/storage-fleet/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/service-ports"
    query_params: dict[str, Any] = {}
    if limit is not None:
        query_params["limit"] = limit
    if offset is not None:
        query_params["offset"] = offset
    if filter is not None:
        query_params["filter"] = filter
    if select is not None:
        query_params["select"] = select
    return await greenlake_request(
        ctx,
        "GET",
        path,
        query_params=query_params or None,
    )


@tool(
    name="greenlake_get_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_snmp_mgr",
    description="GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/snmp-mgr\n\nDeviceType4NetworkServiceSnmpMgrList\n\nGet SNMP-Manager Network-Service details for an HPE Alletra Storage MP B10000 storage system",
    capability=Capability.READ,
)
async def greenlake_get_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_snmp_mgr(
    ctx: Context,
    systemId: Annotated[str, Field(description="systemId of the storage system")],
    limit: Annotated[int | None, Field(default=None, description="Number of items to return at a time")] = None,
    offset: Annotated[
        int | None, Field(default=None, description="The offset of the first item in the collection to return")
    ] = None,
    select: Annotated[
        str | None,
        Field(default=None, description="Query to select only the required parameters, separated by . if nested"),
    ] = None,
) -> Any:
    path = f"/storage-fleet/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/snmp-mgr"
    query_params: dict[str, Any] = {}
    if limit is not None:
        query_params["limit"] = limit
    if offset is not None:
        query_params["offset"] = offset
    if select is not None:
        query_params["select"] = select
    return await greenlake_request(
        ctx,
        "GET",
        path,
        query_params=query_params or None,
    )


@tool(
    name="greenlake_get_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_snmp_mgr_id",
    description="GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/snmp-mgr/{id}\n\nDeviceType4NetworkServiceSnmpMgrGetById\n\nGet a specific SNMP-Manager Network-Service details for an HPE Alletra Storage MP B10000 storage system",
    capability=Capability.READ,
)
async def greenlake_get_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_snmp_mgr_id(
    ctx: Context,
    systemId: Annotated[str, Field(description="systemId of the storage system")],
    id: Annotated[str, Field(description="ID of the SNMP manager")],
    select: Annotated[
        str | None,
        Field(default=None, description="Query to select only the required parameters, separated by . if nested"),
    ] = None,
) -> Any:
    path = f"/storage-fleet/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/snmp-mgr/{path_seg(id)}"
    query_params: dict[str, Any] = {}
    if select is not None:
        query_params["select"] = select
    return await greenlake_request(
        ctx,
        "GET",
        path,
        query_params=query_params or None,
    )


@tool(
    name="greenlake_get_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_snmp_users",
    description="GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/snmp-users\n\nDeviceType4SnmpUsersList\n\nGet SNMP users",
    capability=Capability.READ,
)
async def greenlake_get_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_snmp_users(
    ctx: Context,
    systemId: Annotated[str, Field(description="systemId of the storage system")],
    limit: Annotated[int | None, Field(default=None, description="Number of items to return at a time")] = None,
    offset: Annotated[
        int | None, Field(default=None, description="The offset of the first item in the collection to return")
    ] = None,
    select: Annotated[
        str | None,
        Field(default=None, description="Query to select only the required parameters, separated by . if nested"),
    ] = None,
    filter: Annotated[
        str | None, Field(default=None, description="oData query to filter snmpusers resource by Key.")
    ] = None,
    sort: Annotated[
        str | None, Field(default=None, description="oData query to sort snmpusers resource by Key.")
    ] = None,
) -> Any:
    path = f"/storage-fleet/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/snmp-users"
    query_params: dict[str, Any] = {}
    if limit is not None:
        query_params["limit"] = limit
    if offset is not None:
        query_params["offset"] = offset
    if select is not None:
        query_params["select"] = select
    if filter is not None:
        query_params["filter"] = filter
    if sort is not None:
        query_params["sort"] = sort
    return await greenlake_request(
        ctx,
        "GET",
        path,
        query_params=query_params or None,
    )


@tool(
    name="greenlake_get_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_snmp_users_id",
    description="GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/snmp-users/{id}\n\nDeviceType4SnmpUsersGetById\n\nGet SNMP users identified by {id}",
    capability=Capability.READ,
)
async def greenlake_get_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_snmp_users_id(
    ctx: Context,
    systemId: Annotated[str, Field(description="systemId of the storage system")],
    id: Annotated[str, Field(description="ID of the SNMP manager")],
    select: Annotated[
        str | None,
        Field(default=None, description="Query to select only the required parameters, separated by . if nested"),
    ] = None,
) -> Any:
    path = f"/storage-fleet/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/snmp-users/{path_seg(id)}"
    query_params: dict[str, Any] = {}
    if select is not None:
        query_params["select"] = select
    return await greenlake_request(
        ctx,
        "GET",
        path,
        query_params=query_params or None,
    )


@tool(
    name="greenlake_get_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_support_settings",
    description="GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/support-settings\n\nDeviceType4SupportSettingsGet\n\nGet support settings for an HPE Alletra Storage MP B10000 storage system",
    capability=Capability.READ,
)
async def greenlake_get_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_support_settings(
    ctx: Context,
    systemId: Annotated[str, Field(description="systemId of the storage system")],
    select: Annotated[
        str | None,
        Field(default=None, description="Query to select only the required parameters, separated by . if nested"),
    ] = None,
) -> Any:
    path = f"/storage-fleet/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/support-settings"
    query_params: dict[str, Any] = {}
    if select is not None:
        query_params["select"] = select
    return await greenlake_request(
        ctx,
        "GET",
        path,
        query_params=query_params or None,
    )


@tool(
    name="greenlake_get_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_sustainability_metrics",
    description="GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/sustainability-metrics\n\nDeviceType4EnclosurePowersSustainability\n\nGet details of sustainability metrics of enclosure and system power supplies in Watts on storage system identified by {systemid}",
    capability=Capability.READ,
)
async def greenlake_get_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_sustainability_metrics(
    ctx: Context,
    systemId: Annotated[str, Field(description="systemId of the storage system")],
    range: Annotated[
        str | None,
        Field(default=None, description="range will define start and end time in which query has to be made."),
    ] = None,
    time_interval_min: Annotated[
        int | None, Field(default=None, description="It defines granularity in minutes.")
    ] = None,
    group_by: Annotated[
        str | None, Field(default=None, description="groupBy will define comma separated groupby parameters")
    ] = None,
    metric_type: Annotated[
        str | None, Field(default=None, description="metricType will define comma separated metrics")
    ] = None,
    filter: Annotated[str | None, Field(default=None, description="filter will define objects to be filtered")] = None,
) -> Any:
    path = f"/storage-fleet/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/sustainability-metrics"
    query_params: dict[str, Any] = {}
    if range is not None:
        query_params["range"] = range
    if time_interval_min is not None:
        query_params["time-interval-min"] = time_interval_min
    if group_by is not None:
        query_params["group-by"] = group_by
    if metric_type is not None:
        query_params["metric-type"] = metric_type
    if filter is not None:
        query_params["filter"] = filter
    return await greenlake_request(
        ctx,
        "GET",
        path,
        query_params=query_params or None,
    )


@tool(
    name="greenlake_get_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_system_settings",
    description="GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/system-settings\n\nDeviceType4SystemSettingsList\n\nGet the system settings configuration details",
    capability=Capability.READ,
)
async def greenlake_get_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_system_settings(
    ctx: Context,
    systemId: Annotated[str, Field(description="systemId of the storage system")],
    select: Annotated[
        str | None,
        Field(default=None, description="Query to select only the required parameters, separated by . if nested"),
    ] = None,
) -> Any:
    path = f"/storage-fleet/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/system-settings"
    query_params: dict[str, Any] = {}
    if select is not None:
        query_params["select"] = select
    return await greenlake_request(
        ctx,
        "GET",
        path,
        query_params=query_params or None,
    )


@tool(
    name="greenlake_get_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_telemetry",
    description="GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/telemetry\n\nDeviceType4TelemetryGet\n\nGet telemetry status for an HPE Alletra Storage MP B10000 storage system",
    capability=Capability.READ,
)
async def greenlake_get_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_telemetry(
    ctx: Context,
    systemId: Annotated[str, Field(description="systemId of the storage system")],
    select: Annotated[
        str | None,
        Field(default=None, description="Query to select only the required parameters, separated by . if nested"),
    ] = None,
) -> Any:
    path = f"/storage-fleet/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/telemetry"
    query_params: dict[str, Any] = {}
    if select is not None:
        query_params["select"] = select
    return await greenlake_request(
        ctx,
        "GET",
        path,
        query_params=query_params or None,
    )


@tool(
    name="greenlake_get_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_trust_certificates",
    description="GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/trust-certificates\n\nDeviceType4TrustedCertificatesList\n\nGet certificates trusted by HPE Alletra Storage MP B10000",
    capability=Capability.READ,
)
async def greenlake_get_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_trust_certificates(
    ctx: Context,
    systemId: Annotated[str, Field(description="systemId of the storage system")],
    select: Annotated[
        str | None,
        Field(default=None, description="Query to select only the required parameters, separated by . if nested"),
    ] = None,
    limit: Annotated[int | None, Field(default=None, description="Number of items to return at a time")] = None,
    offset: Annotated[
        int | None, Field(default=None, description="The offset of the first item in the collection to return")
    ] = None,
    filter: Annotated[
        str | None, Field(default=None, description="Lucene query to filter Certificates by Key.")
    ] = None,
) -> Any:
    path = f"/storage-fleet/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/trust-certificates"
    query_params: dict[str, Any] = {}
    if select is not None:
        query_params["select"] = select
    if limit is not None:
        query_params["limit"] = limit
    if offset is not None:
        query_params["offset"] = offset
    if filter is not None:
        query_params["filter"] = filter
    return await greenlake_request(
        ctx,
        "GET",
        path,
        query_params=query_params or None,
    )


@tool(
    name="greenlake_get_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_trust_certificates_id",
    description="GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/trust-certificates/{id}\n\nDeviceType4TrustedCertificatesGetById\n\nGet certificates trusted by HPE Alletra Storage MP B10000 identified by {id}",
    capability=Capability.READ,
)
async def greenlake_get_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_trust_certificates_id(
    ctx: Context,
    systemId: Annotated[str, Field(description="systemId of the storage system")],
    id: Annotated[str, Field(description="ID of the certificate")],
    select: Annotated[
        str | None,
        Field(default=None, description="Query to select only the required parameters, separated by . if nested"),
    ] = None,
) -> Any:
    path = f"/storage-fleet/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/trust-certificates/{path_seg(id)}"
    query_params: dict[str, Any] = {}
    if select is not None:
        query_params["select"] = select
    return await greenlake_request(
        ctx,
        "GET",
        path,
        query_params=query_params or None,
    )


@tool(
    name="greenlake_get_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_vasa",
    description="GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/vasa\n\nDeviceType4NetworkServiceVasaGet\n\nGet VASA Network-Service details for a storage system Primera / Alletra 9K",
    capability=Capability.READ,
)
async def greenlake_get_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_vasa(
    ctx: Context,
    systemId: Annotated[str, Field(description="systemId of the storage system")],
    select: Annotated[
        str | None,
        Field(default=None, description="Query to select only the required parameters, separated by . if nested"),
    ] = None,
) -> Any:
    path = f"/storage-fleet/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/vasa"
    query_params: dict[str, Any] = {}
    if select is not None:
        query_params["select"] = select
    return await greenlake_request(
        ctx,
        "GET",
        path,
        query_params=query_params or None,
    )


@tool(
    name="greenlake_get_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_vm_manager_settings",
    description="GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/vm-manager-settings\n\nDeviceType4VMManagerSettingsList\n\nGet vCenter settings for an HPE Alletra Storage MP B10000 storage system",
    capability=Capability.READ,
)
async def greenlake_get_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_vm_manager_settings(
    ctx: Context,
    systemId: Annotated[str, Field(description="systemId of the storage system")],
    select: Annotated[
        str | None,
        Field(default=None, description="Query to select only the required parameters, separated by . if nested"),
    ] = None,
    limit: Annotated[int | None, Field(default=None, description="Number of items to return at a time")] = None,
    offset: Annotated[
        int | None, Field(default=None, description="The offset of the first item in the collection to return")
    ] = None,
) -> Any:
    path = f"/storage-fleet/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/vm-manager-settings"
    query_params: dict[str, Any] = {}
    if select is not None:
        query_params["select"] = select
    if limit is not None:
        query_params["limit"] = limit
    if offset is not None:
        query_params["offset"] = offset
    return await greenlake_request(
        ctx,
        "GET",
        path,
        query_params=query_params or None,
    )


@tool(
    name="greenlake_get_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_vm_manager_settings_vcenter_setting_id",
    description="GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/vm-manager-settings/{vcenterSettingId}\n\nDeviceType4VMManagerSettingsGetById\n\nGet vCenter setting detail for a given vCenter setting of a HPE Alletra Storage MP B10000 storage system",
    capability=Capability.READ,
)
async def greenlake_get_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_vm_manager_settings_vcenter_setting_id(
    ctx: Context,
    systemId: Annotated[str, Field(description="systemId of the storage system")],
    vcenterSettingId: Annotated[str, Field(description="UID(vcenterSettingId) of the storage system")],
    select: Annotated[
        str | None,
        Field(default=None, description="Query to select only the required parameters, separated by . if nested"),
    ] = None,
) -> Any:
    path = f"/storage-fleet/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/vm-manager-settings/{path_seg(vcenterSettingId)}"
    query_params: dict[str, Any] = {}
    if select is not None:
        query_params["select"] = select
    return await greenlake_request(
        ctx,
        "GET",
        path,
        query_params=query_params or None,
    )


@tool(
    name="greenlake_get_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_vvol",
    description="GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/vvol\n\nDeviceType4vVolGet\n\nGet vVol details for an HPE Alletra Storage MP B10000 storage system",
    capability=Capability.READ,
)
async def greenlake_get_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_vvol(
    ctx: Context,
    systemId: Annotated[str, Field(description="systemId of the storage system")],
    limit: Annotated[int | None, Field(default=None, description="Number of items to return at a time")] = None,
    offset: Annotated[
        int | None, Field(default=None, description="The offset of the first item in the collection to return")
    ] = None,
    filter: Annotated[str | None, Field(default=None, description="oData query to filter by Key.")] = None,
    sort: Annotated[str | None, Field(default=None, description="oData query to sort by Key.")] = None,
    select: Annotated[
        str | None,
        Field(default=None, description="Query to select only the required parameters, separated by . if nested"),
    ] = None,
) -> Any:
    path = f"/storage-fleet/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/vvol"
    query_params: dict[str, Any] = {}
    if limit is not None:
        query_params["limit"] = limit
    if offset is not None:
        query_params["offset"] = offset
    if filter is not None:
        query_params["filter"] = filter
    if sort is not None:
        query_params["sort"] = sort
    if select is not None:
        query_params["select"] = select
    return await greenlake_request(
        ctx,
        "GET",
        path,
        query_params=query_params or None,
    )


@tool(
    name="greenlake_get_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_vvolscs",
    description="GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/vvolscs\n\nDeviceType4StorageContainerGet\n\nGet Storage Container details for an HPE Alletra Storage MP B10000 storage system",
    capability=Capability.READ,
)
async def greenlake_get_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_vvolscs(
    ctx: Context,
    systemId: Annotated[str, Field(description="systemId of the storage system")],
    limit: Annotated[int | None, Field(default=None, description="Number of items to return at a time")] = None,
    offset: Annotated[
        int | None, Field(default=None, description="The offset of the first item in the collection to return")
    ] = None,
    filter: Annotated[str | None, Field(default=None, description="oData query to filter by Key.")] = None,
    sort: Annotated[str | None, Field(default=None, description="oData query to sort by Key.")] = None,
    select: Annotated[
        str | None,
        Field(default=None, description="Query to select only the required parameters, separated by . if nested"),
    ] = None,
) -> Any:
    path = f"/storage-fleet/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/vvolscs"
    query_params: dict[str, Any] = {}
    if limit is not None:
        query_params["limit"] = limit
    if offset is not None:
        query_params["offset"] = offset
    if filter is not None:
        query_params["filter"] = filter
    if sort is not None:
        query_params["sort"] = sort
    if select is not None:
        query_params["select"] = select
    return await greenlake_request(
        ctx,
        "GET",
        path,
        query_params=query_params or None,
    )


@tool(
    name="greenlake_post_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_alert_contacts",
    description="POST /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/alert-contacts\n\nDeviceType4AlertContactsCreate\n\nAdd Alert/Mail contact details",
    capability=Capability.WRITE,
)
async def greenlake_post_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_alert_contacts(
    ctx: Context,
    systemId: Annotated[str, Field(description="systemId of the storage system")],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    path = f"/storage-fleet/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/alert-contacts"
    return await greenlake_request(
        ctx,
        "POST",
        path,
        body=body,
    )


@tool(
    name="greenlake_post_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_certificates",
    description="POST /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/certificates\n\nDeviceType4PostCertificate\n\nCreate certificate on HPE Alletra Storage MP B10000 storage system identified by {systemId}",
    capability=Capability.WRITE,
)
async def greenlake_post_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_certificates(
    ctx: Context,
    systemId: Annotated[str, Field(description="systemId of the storage system")],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    path = f"/storage-fleet/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/certificates"
    return await greenlake_request(
        ctx,
        "POST",
        path,
        body=body,
    )


@tool(
    name="greenlake_post_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_certificates_remove",
    description="POST /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/certificates/remove\n\nDeviceType4RemoveCertificates\n\nDelete certificates from HPE Alletra Storage MP B10000 storage system identified by {systemId}",
    capability=Capability.WRITE,
)
async def greenlake_post_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_certificates_remove(
    ctx: Context,
    systemId: Annotated[str, Field(description="systemId of the storage system")],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    path = f"/storage-fleet/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/certificates/remove"
    return await greenlake_request(
        ctx,
        "POST",
        path,
        body=body,
    )


@tool(
    name="greenlake_post_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_collect_support_data",
    description="POST /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/collect-support-data\n\nDeviceType4SupportDataCollect\n\nTrigger a collection on the HPE Alletra Storage MP B10000 storage system",
    capability=Capability.WRITE,
)
async def greenlake_post_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_collect_support_data(
    ctx: Context,
    systemId: Annotated[str, Field(description="systemId of the storage system")],
    body: Annotated[list[Any], Field(description="Request body (required)")],
) -> Any:
    path = f"/storage-fleet/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/collect-support-data"
    return await greenlake_request(
        ctx,
        "POST",
        path,
        body=body,
    )


@tool(
    name="greenlake_post_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_licenses",
    description="POST /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/licenses\n\nDeviceType4SetLicense\n\nSet license of the storage system identified by {systemId}",
    capability=Capability.WRITE,
)
async def greenlake_post_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_licenses(
    ctx: Context,
    systemId: Annotated[str, Field(description="systemId of the storage system")],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    path = f"/storage-fleet/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/licenses"
    return await greenlake_request(
        ctx,
        "POST",
        path,
        body=body,
    )


@tool(
    name="greenlake_post_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_mail_settings",
    description="POST /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/mail-settings\n\nDeviceType4MailSettingsAssociate\n\nAdd SMTP/Mail server settigs",
    capability=Capability.WRITE,
)
async def greenlake_post_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_mail_settings(
    ctx: Context,
    systemId: Annotated[str, Field(description="systemId of the storage system")],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    path = f"/storage-fleet/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/mail-settings"
    return await greenlake_request(
        ctx,
        "POST",
        path,
        body=body,
    )


@tool(
    name="greenlake_post_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_network_settings",
    description="POST /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/network-settings\n\nDeviceType4NetworkSettingsAssociate\n\nPost Network-Settings details for an HPE Alletra Storage MP B10000 storage system",
    capability=Capability.WRITE,
)
async def greenlake_post_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_network_settings(
    ctx: Context,
    systemId: Annotated[str, Field(description="systemId of the storage system")],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    path = f"/storage-fleet/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/network-settings"
    return await greenlake_request(
        ctx,
        "POST",
        path,
        body=body,
    )


@tool(
    name="greenlake_post_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_quorum_witness",
    description="POST /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/quorum-witness\n\nDeviceType4PostQuorumWitness\n\nCreate quorum witness on HPE Alletra Storage MP B10000 storage system identified by {systemId}",
    capability=Capability.WRITE,
)
async def greenlake_post_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_quorum_witness(
    ctx: Context,
    systemId: Annotated[str, Field(description="systemId of the storage system")],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    path = f"/storage-fleet/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/quorum-witness"
    return await greenlake_request(
        ctx,
        "POST",
        path,
        body=body,
    )


@tool(
    name="greenlake_post_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_replication_partners",
    description="POST /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/replication-partners\n\nDeviceType4PostReplicationPartners\n\nCreate replication partners on HPE Alletra Storage MP B10000 identified by {systemId}",
    capability=Capability.WRITE,
)
async def greenlake_post_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_replication_partners(
    ctx: Context,
    systemId: Annotated[str, Field(description="systemId of the storage system")],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    path = f"/storage-fleet/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/replication-partners"
    return await greenlake_request(
        ctx,
        "POST",
        path,
        body=body,
    )


@tool(
    name="greenlake_post_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_replication_partners_remove",
    description="POST /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/replication-partners/remove\n\nDeviceType4PostRemoveReplicationPartners\n\nDelete replication partner from HPE Alletra Storage MP B10000 storage system identified by {systemId}",
    capability=Capability.WRITE,
)
async def greenlake_post_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_replication_partners_remove(
    ctx: Context,
    systemId: Annotated[str, Field(description="systemId of the storage system")],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    path = f"/storage-fleet/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/replication-partners/remove"
    return await greenlake_request(
        ctx,
        "POST",
        path,
        body=body,
    )


@tool(
    name="greenlake_post_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_snmp_mgr",
    description="POST /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/snmp-mgr\n\nDeviceType4NetworkServiceSnmpMgrCreate\n\nAdd SNMP Manager settings",
    capability=Capability.WRITE,
)
async def greenlake_post_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_snmp_mgr(
    ctx: Context,
    systemId: Annotated[str, Field(description="systemId of the storage system")],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    path = f"/storage-fleet/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/snmp-mgr"
    return await greenlake_request(
        ctx,
        "POST",
        path,
        body=body,
    )


@tool(
    name="greenlake_post_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_support_settings",
    description="POST /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/support-settings\n\nDeviceType4SupportSettingsAssociate\n\nAdd support settings for an HPE Alletra Storage MP B10000 storage system",
    capability=Capability.WRITE,
)
async def greenlake_post_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_support_settings(
    ctx: Context,
    systemId: Annotated[str, Field(description="systemId of the storage system")],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    path = f"/storage-fleet/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/support-settings"
    return await greenlake_request(
        ctx,
        "POST",
        path,
        body=body,
    )


@tool(
    name="greenlake_post_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_system_settings",
    description="POST /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/system-settings\n\nDeviceType4SystemSettingsAssociate\n\nEdit system settings configuration",
    capability=Capability.WRITE,
)
async def greenlake_post_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_system_settings(
    ctx: Context,
    systemId: Annotated[str, Field(description="systemId of the storage system")],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    path = f"/storage-fleet/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/system-settings"
    return await greenlake_request(
        ctx,
        "POST",
        path,
        body=body,
    )


@tool(
    name="greenlake_post_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_trust_certificates",
    description="POST /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/trust-certificates\n\nDeviceType4AddTrustedCertificates\n\nAdd trusted certificates for HPE Alletra Storage MP B10000 storage system identified by {systemId}",
    capability=Capability.WRITE,
)
async def greenlake_post_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_trust_certificates(
    ctx: Context,
    systemId: Annotated[str, Field(description="systemId of the storage system")],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    path = f"/storage-fleet/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/trust-certificates"
    return await greenlake_request(
        ctx,
        "POST",
        path,
        body=body,
    )


@tool(
    name="greenlake_post_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_trust_certificates_remove",
    description="POST /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/trust-certificates/remove\n\nDeviceType4RemoveTrustedCertificates\n\nDelete trusted certificates from HPE Alletra Storage MP B10000 storage system identified by {systemId}",
    capability=Capability.WRITE,
)
async def greenlake_post_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_trust_certificates_remove(
    ctx: Context,
    systemId: Annotated[str, Field(description="systemId of the storage system")],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    path = f"/storage-fleet/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/trust-certificates/remove"
    return await greenlake_request(
        ctx,
        "POST",
        path,
        body=body,
    )


@tool(
    name="greenlake_post_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_vasa_vasa_id",
    description="POST /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/vasa/{vasaId}\n\nDeviceType4NetworkServiceVasaConfigure\n\nConfigures vasa service for the specified id.",
    capability=Capability.WRITE,
)
async def greenlake_post_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_vasa_vasa_id(
    ctx: Context,
    systemId: Annotated[str, Field(description="systemId of the storage system")],
    vasaId: Annotated[str, Field(description="ID of the VASA service")],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    path = f"/storage-fleet/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/vasa/{path_seg(vasaId)}"
    return await greenlake_request(
        ctx,
        "POST",
        path,
        body=body,
    )


@tool(
    name="greenlake_post_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_vasa_vasa_id_services",
    description="POST /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/vasa/{vasaId}/services\n\nDeviceType4NetworkServiceConfigureVasaService\n\nConfigures vasa service for the specified id.",
    capability=Capability.WRITE,
)
async def greenlake_post_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_vasa_vasa_id_services(
    ctx: Context,
    systemId: Annotated[str, Field(description="systemId of the storage system")],
    vasaId: Annotated[str, Field(description="ID of the VASA service")],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    path = f"/storage-fleet/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/vasa/{path_seg(vasaId)}/services"
    return await greenlake_request(
        ctx,
        "POST",
        path,
        body=body,
    )


@tool(
    name="greenlake_post_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_vasaprovider",
    description="POST /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/vasaprovider\n\nDeviceType4VasaProviderAddressConfigure\n\nConfigure IP addresses for VASA Provider High Availability (VPHA) on a HPE Alletra Storage MP B10000 storage system",
    capability=Capability.WRITE,
)
async def greenlake_post_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_vasaprovider(
    ctx: Context,
    systemId: Annotated[str, Field(description="systemId of the storage system")],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    path = f"/storage-fleet/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/vasaprovider"
    return await greenlake_request(
        ctx,
        "POST",
        path,
        body=body,
    )


@tool(
    name="greenlake_post_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_vasaprovider_clear",
    description="POST /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/vasaprovider/clear\n\nDeviceType4VasaProviderAddressClear\n\nClear VASA Provider IP Address configuration on a HPE Alletra Storage MP B10000 storage system",
    capability=Capability.WRITE,
)
async def greenlake_post_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_vasaprovider_clear(
    ctx: Context,
    systemId: Annotated[str, Field(description="systemId of the storage system")],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    path = f"/storage-fleet/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/vasaprovider/clear"
    return await greenlake_request(
        ctx,
        "POST",
        path,
        body=body,
    )


@tool(
    name="greenlake_post_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_vm_manager_settings",
    description="POST /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/vm-manager-settings\n\nDeviceType4PostVCenterSettings\n\nAdd vCenter settings to HPE Alletra Storage MP B10000 storage system",
    capability=Capability.WRITE,
)
async def greenlake_post_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_vm_manager_settings(
    ctx: Context,
    systemId: Annotated[str, Field(description="systemId of the storage system")],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    path = f"/storage-fleet/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/vm-manager-settings"
    return await greenlake_request(
        ctx,
        "POST",
        path,
        body=body,
    )


@tool(
    name="greenlake_put_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_alert_contacts_id",
    description="PUT /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/alert-contacts/{id}\n\nDeviceType4AlertContactsUpdate\n\nEdit Alert/Email contact details of HPE Alletra Storage MP B10000 storage system identified by {id}",
    capability=Capability.WRITE,
)
async def greenlake_put_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_alert_contacts_id(
    ctx: Context,
    systemId: Annotated[str, Field(description="systemId of the storage system")],
    id: Annotated[str, Field(description="Unique Identifier of the alert contact")],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    path = f"/storage-fleet/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/alert-contacts/{path_seg(id)}"
    return await greenlake_request(
        ctx,
        "PUT",
        path,
        body=body,
    )


@tool(
    name="greenlake_put_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_certificates_id",
    description="PUT /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/certificates/{id}\n\nDeviceType4PutCertificate\n\nImport certificate identified by {id} on HPE Alletra Storage MP B10000 storage system identified by {systemId}",
    capability=Capability.WRITE,
)
async def greenlake_put_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_certificates_id(
    ctx: Context,
    systemId: Annotated[str, Field(description="systemId of the storage system")],
    id: Annotated[str, Field(description="ID of the certificate")],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    path = f"/storage-fleet/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/certificates/{path_seg(id)}"
    return await greenlake_request(
        ctx,
        "PUT",
        path,
        body=body,
    )


@tool(
    name="greenlake_put_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_cim",
    description="PUT /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/cim\n\nDeviceType4NetworkServiceCimUpdate\n\nEdit CIM network service configuration",
    capability=Capability.WRITE,
)
async def greenlake_put_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_cim(
    ctx: Context,
    systemId: Annotated[str, Field(description="systemId of the storage system")],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    path = f"/storage-fleet/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/cim"
    return await greenlake_request(
        ctx,
        "PUT",
        path,
        body=body,
    )


@tool(
    name="greenlake_put_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_mail_settings",
    description="PUT /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/mail-settings\n\nDeviceType4MailSettingsUpdate\n\nEdit SMTP/Mail server settigs",
    capability=Capability.WRITE,
)
async def greenlake_put_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_mail_settings(
    ctx: Context,
    systemId: Annotated[str, Field(description="systemId of the storage system")],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    path = f"/storage-fleet/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/mail-settings"
    return await greenlake_request(
        ctx,
        "PUT",
        path,
        body=body,
    )


@tool(
    name="greenlake_put_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_quorum_witness_replication_partner_id",
    description="PUT /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/quorum-witness/{replicationPartnerId}\n\nDeviceType4PutQuorumWitness\n\nEdit quorum witness identified by {replicationPartnerId} on HPE Alletra Storage MP B10000 storage system identified by {systemId}",
    capability=Capability.WRITE,
)
async def greenlake_put_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_quorum_witness_replication_partner_id(
    ctx: Context,
    systemId: Annotated[str, Field(description="systemId of the storage system")],
    replicationPartnerId: Annotated[str, Field(description="ID of device-type4 replication partner")],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    path = f"/storage-fleet/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/quorum-witness/{path_seg(replicationPartnerId)}"
    return await greenlake_request(
        ctx,
        "PUT",
        path,
        body=body,
    )


@tool(
    name="greenlake_put_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_replication_partners_replication_partner_id",
    description="PUT /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/replication-partners/{replicationPartnerId}\n\nDeviceType4PutReplicationPartner\n\nEdit replication partner identified by {replicationPartnerId} on HPE Alletra Storage MP B10000 identified by {systemId}",
    capability=Capability.WRITE,
)
async def greenlake_put_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_replication_partners_replication_partner_id(
    ctx: Context,
    systemId: Annotated[str, Field(description="systemId of the storage system")],
    replicationPartnerId: Annotated[str, Field(description="ID of device-type4 replication partner")],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    path = f"/storage-fleet/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/replication-partners/{path_seg(replicationPartnerId)}"
    return await greenlake_request(
        ctx,
        "PUT",
        path,
        body=body,
    )


@tool(
    name="greenlake_put_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_snmp_mgr_id",
    description="PUT /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/snmp-mgr/{id}\n\nDeviceType4NetworkServiceSnmpMgrUpdate\n\nEdit SNMP Manager settings for the specified Id",
    capability=Capability.WRITE,
)
async def greenlake_put_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_snmp_mgr_id(
    ctx: Context,
    systemId: Annotated[str, Field(description="systemId of the storage system")],
    id: Annotated[str, Field(description="ID of the SNMP manager")],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    path = f"/storage-fleet/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/snmp-mgr/{path_seg(id)}"
    return await greenlake_request(
        ctx,
        "PUT",
        path,
        body=body,
    )


@tool(
    name="greenlake_put_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_support_settings",
    description="PUT /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/support-settings\n\nDeviceType4SupportSettingsUpdate\n\nEdit support settings for an HPE Alletra Storage MP B10000 storage system",
    capability=Capability.WRITE,
)
async def greenlake_put_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_support_settings(
    ctx: Context,
    systemId: Annotated[str, Field(description="systemId of the storage system")],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    path = f"/storage-fleet/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/support-settings"
    return await greenlake_request(
        ctx,
        "PUT",
        path,
        body=body,
    )


@tool(
    name="greenlake_put_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_system_settings",
    description="PUT /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/system-settings\n\nDeviceType4SystemSettingsUpdate\n\nEdit system settings configuration",
    capability=Capability.WRITE,
)
async def greenlake_put_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_system_settings(
    ctx: Context,
    systemId: Annotated[str, Field(description="systemId of the storage system")],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    path = f"/storage-fleet/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/system-settings"
    return await greenlake_request(
        ctx,
        "PUT",
        path,
        body=body,
    )


@tool(
    name="greenlake_put_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_vm_manager_settings_vcenter_setting_id",
    description="PUT /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/vm-manager-settings/{vcenterSettingId}\n\nDeviceType4PutVCenterSettings\n\nEdit vCenter setting identified by {vcenterSettingId} on HPE Alletra Storage MP B10000 identified by {systemId}",
    capability=Capability.WRITE,
)
async def greenlake_put_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_vm_manager_settings_vcenter_setting_id(
    ctx: Context,
    systemId: Annotated[str, Field(description="systemId of the storage system")],
    vcenterSettingId: Annotated[str, Field(description="UID(vcenterSettingId) of the storage system")],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    path = f"/storage-fleet/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/vm-manager-settings/{path_seg(vcenterSettingId)}"
    return await greenlake_request(
        ctx,
        "PUT",
        path,
        body=body,
    )


@tool(
    name="greenlake_put_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_vvolscs_vvolsc_id",
    description="PUT /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/vvolscs/{vvolscId}\n\nDeviceType4StorageContainerEditById\n\nEdit storage container of HPE Alletra Storage MP B10000 storage system identified by {id}",
    capability=Capability.WRITE,
)
async def greenlake_put_storage_fleet_v1alpha1_devtype4_storage_systems_system_id_vvolscs_vvolsc_id(
    ctx: Context,
    systemId: Annotated[str, Field(description="systemId of the storage system")],
    vvolscId: Annotated[str, Field(description="Storage container UID")],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    path = f"/storage-fleet/v1alpha1/devtype4-storage-systems/{path_seg(systemId)}/vvolscs/{path_seg(vvolscId)}"
    return await greenlake_request(
        ctx,
        "PUT",
        path,
        body=body,
    )
