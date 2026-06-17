"""Generated EdgeConnect tools — DO NOT EDIT BY HAND.

Generated from ``vendor/edgeconnect/EdgeConnect-9-7-REST-API.json`` by the
maintainer-local EdgeConnect generator. These generated modules are committed
and are the runtime source of truth; regeneration is a release-time maintainer
workflow (the generator is intentionally not committed — see ``.gitignore``).

Tag: ``thirdPartyServices``
Operations in this file: 200
"""

# ruff: noqa: E501, N803
from __future__ import annotations

from typing import Annotated, Any

from fastmcp import Context
from pydantic import Field

from hpe_networking_mcp.platforms._common.annotations import Capability
from hpe_networking_mcp.platforms.edgeconnect._registry import tool
from hpe_networking_mcp.platforms.edgeconnect.client import edgeconnect_request


@tool(
    name="edgeconnect_delete_third_party_services_aruba_central_subscription",
    description="DELETE /thirdPartyServices/arubaCentral/subscription\n\narubaCentralSubscriptionDelete757\n\nDelete HPE Aruba Networking Central Subscription",
    capability=Capability.WRITE_DELETE,
)
async def edgeconnect_delete_third_party_services_aruba_central_subscription(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "DELETE",
        "/thirdPartyServices/arubaCentral/subscription",
        query_params=None,
    )


@tool(
    name="edgeconnect_delete_third_party_services_awstgnm_subscription",
    description="DELETE /thirdPartyServices/awstgnm/subscription\n\nawsTgnmSubscriptionDelete772\n\nDelete AWS Transit Gateway Network Manager Subscription",
    capability=Capability.WRITE_DELETE,
)
async def edgeconnect_delete_third_party_services_awstgnm_subscription(
    ctx: Context,
    deletionType: Annotated[
        str | None,
        Field(
            default=None,
            description="Controls the deletion behavior. Use 'forceDeleteSubscription' to remove all AWS configurations including appliance associations, segment firewall associations, TGW configs, CNE configs, and VTI subnets. If omitted or set to 'deleteSubscription', performs a standard deletion that only removes the subscription.",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if deletionType is not None:
        query_params["deletionType"] = deletionType
    return await edgeconnect_request(
        ctx,
        "DELETE",
        "/thirdPartyServices/awstgnm/subscription",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_delete_third_party_services_axis_pop_override",
    description="DELETE /thirdPartyServices/axis/popOverride\n\naxisRemoteEndpointExceptionDelete872\n\nDelete HPE SSE POP override configuration",
    capability=Capability.WRITE_DELETE,
)
async def edgeconnect_delete_third_party_services_axis_pop_override(
    ctx: Context,
    nePk: Annotated[
        str,
        Field(
            description="Network Element Primary Key - unique appliance identifier assigned by Orchestrator. Format: '<id>.NE' (e.g., '0.NE', '10.NE')."
        ),
    ],
    labelId: Annotated[
        str,
        Field(
            description="ID of the WAN interface label for which to delete the POP override. Must be a valid WAN interface label ID."
        ),
    ],
) -> Any:
    query_params: dict[str, Any] = {}
    if nePk is not None:
        query_params["nePk"] = nePk
    if labelId is not None:
        query_params["labelId"] = labelId
    return await edgeconnect_request(
        ctx,
        "DELETE",
        "/thirdPartyServices/axis/popOverride",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_delete_third_party_services_axis_sub_location_config",
    description="DELETE /thirdPartyServices/axis/subLocationConfig\n\naxisSubLocationDelete874\n\nDelete HPE SSE Sub-Location Configuration",
    capability=Capability.WRITE_DELETE,
)
async def edgeconnect_delete_third_party_services_axis_sub_location_config(
    ctx: Context,
    id: Annotated[
        int,
        Field(
            description="Unique identifier of the HPE SSE sub-location configuration to delete. Must be a valid positive integer ID from an existing configuration."
        ),
    ],
) -> Any:
    query_params: dict[str, Any] = {}
    if id is not None:
        query_params["id"] = id
    return await edgeconnect_request(
        ctx,
        "DELETE",
        "/thirdPartyServices/axis/subLocationConfig",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_delete_third_party_services_axis_subscription",
    description="DELETE /thirdPartyServices/axis/subscription\n\naxisSubscriptionDelete874\n\nDelete HPE SSE Subscription",
    capability=Capability.WRITE_DELETE,
)
async def edgeconnect_delete_third_party_services_axis_subscription(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "DELETE",
        "/thirdPartyServices/axis/subscription",
        query_params=None,
    )


@tool(
    name="edgeconnect_delete_third_party_services_azure_lan_side_connectivity_lan_side_subscription",
    description="DELETE /thirdPartyServices/azure/lan-side-connectivity/lanSideSubscription\n\nazureLanSideConnnectivityLanSideSubscriptionDelete788\n\nDelete Azure LAN-side subscription",
    capability=Capability.WRITE_DELETE,
)
async def edgeconnect_delete_third_party_services_azure_lan_side_connectivity_lan_side_subscription(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "DELETE",
        "/thirdPartyServices/azure/lan-side-connectivity/lanSideSubscription",
        query_params=None,
    )


@tool(
    name="edgeconnect_delete_third_party_services_azure_subscription",
    description="DELETE /thirdPartyServices/azure/subscription\n\nazureSubscriptionDelete790\n\nDelete Azure Virtual WAN Subscription",
    capability=Capability.WRITE_DELETE,
)
async def edgeconnect_delete_third_party_services_azure_subscription(
    ctx: Context,
    deletionType: Annotated[
        str | None,
        Field(
            default=None,
            description="Controls the type of deletion. Use 'forceDeleteSubscription' to remove all Azure GMS configurations along with the subscription, or omit for standard deletion.",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if deletionType is not None:
        query_params["deletionType"] = deletionType
    return await edgeconnect_request(
        ctx,
        "DELETE",
        "/thirdPartyServices/azure/subscription",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_delete_third_party_services_clearpass_accounts",
    description="DELETE /thirdPartyServices/clearpass/accounts\n\ndeleteClearPassSubscription\n\nDelete ClearPass Policy Manager account",
    capability=Capability.WRITE_DELETE,
)
async def edgeconnect_delete_third_party_services_clearpass_accounts(
    ctx: Context,
    id: Annotated[
        int,
        Field(description="Unique identifier of the ClearPass account to delete. Must be a valid existing account ID."),
    ],
) -> Any:
    query_params: dict[str, Any] = {}
    if id is not None:
        query_params["id"] = id
    return await edgeconnect_request(
        ctx,
        "DELETE",
        "/thirdPartyServices/clearpass/accounts",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_delete_third_party_services_netskope_pop_override",
    description="DELETE /thirdPartyServices/netskope/popOverride\n\ndeletePopOverride873\n\nDelete Netskope service edge POP override",
    capability=Capability.WRITE_DELETE,
)
async def edgeconnect_delete_third_party_services_netskope_pop_override(
    ctx: Context,
    nePk: Annotated[
        str,
        Field(
            description="Network Element Primary Key - unique appliance identifier assigned by Orchestrator. Format: '<id>.NE' (e.g., '0.NE', '10.NE')."
        ),
    ],
    labelId: Annotated[
        str, Field(description="WAN interface label ID. Must be a valid WAN label configured in interface labels.")
    ],
) -> Any:
    query_params: dict[str, Any] = {}
    if nePk is not None:
        query_params["nePk"] = nePk
    if labelId is not None:
        query_params["labelId"] = labelId
    return await edgeconnect_request(
        ctx,
        "DELETE",
        "/thirdPartyServices/netskope/popOverride",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_delete_third_party_services_netskope_subscription",
    description="DELETE /thirdPartyServices/netskope/subscription\n\nnetskopeSubscriptionDelete874\n\nDelete Netskope Subscription",
    capability=Capability.WRITE_DELETE,
)
async def edgeconnect_delete_third_party_services_netskope_subscription(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "DELETE",
        "/thirdPartyServices/netskope/subscription",
        query_params=None,
    )


@tool(
    name="edgeconnect_delete_third_party_services_service_orchestration_remote_endpoints",
    description="DELETE /thirdPartyServices/serviceOrchestration/remoteEndpoints\n\ndeleteRemoteEndpointEntry840\n\nDelete Remote Endpoint entries for a Service Provider",
    capability=Capability.WRITE_DELETE,
)
async def edgeconnect_delete_third_party_services_service_orchestration_remote_endpoints(
    ctx: Context,
    serviceId: Annotated[
        str,
        Field(
            description="The unique identifier of the service provider. Must reference an existing service provider configuration."
        ),
    ],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    query_params: dict[str, Any] = {}
    if serviceId is not None:
        query_params["serviceId"] = serviceId
    return await edgeconnect_request(
        ctx,
        "DELETE",
        "/thirdPartyServices/serviceOrchestration/remoteEndpoints",
        query_params=query_params or None,
        body=body,
    )


@tool(
    name="edgeconnect_delete_third_party_services_zscaler_remote_endpoint_exception",
    description="DELETE /thirdPartyServices/zscaler/remoteEndpointException\n\nzscalerRemoteEndpointExceptionDelete872\n\nDelete Zscaler ZEN override configuration",
    capability=Capability.WRITE_DELETE,
)
async def edgeconnect_delete_third_party_services_zscaler_remote_endpoint_exception(
    ctx: Context,
    nePk: Annotated[
        str,
        Field(
            description="Network Element Primary Key - unique appliance identifier assigned by Orchestrator. Format: '<id>.NE' (e.g., '0.NE', '10.NE')."
        ),
    ],
    labelId: Annotated[
        str,
        Field(
            description="Numeric identifier for the WAN interface label. Must be a valid WAN interface label configured in the system."
        ),
    ],
) -> Any:
    query_params: dict[str, Any] = {}
    if nePk is not None:
        query_params["nePk"] = nePk
    if labelId is not None:
        query_params["labelId"] = labelId
    return await edgeconnect_request(
        ctx,
        "DELETE",
        "/thirdPartyServices/zscaler/remoteEndpointException",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_delete_third_party_services_zscaler_subscription",
    description="DELETE /thirdPartyServices/zscaler/subscription\n\nzscalerSubscriptionDelete874\n\nDelete Zscaler Subscription",
    capability=Capability.WRITE_DELETE,
)
async def edgeconnect_delete_third_party_services_zscaler_subscription(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "DELETE",
        "/thirdPartyServices/zscaler/subscription",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_gms_vti_cidr",
    description="GET /gms/vti/cidr\n\ngetAzuretiCidr791\n\nGet VTI Subnet and Mask for the Azure Subnet Global Pool",
    capability=Capability.READ,
)
async def edgeconnect_get_gms_vti_cidr(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/gms/vti/cidr",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_third_party_services_aruba_central_sites_mapping",
    description="GET /thirdPartyServices/arubaCentral/sitesMapping\n\ngetArubaCentralSiteMapping755\n\nGet HPE ANW Central site-to-appliance mappings",
    capability=Capability.READ,
)
async def edgeconnect_get_third_party_services_aruba_central_sites_mapping(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/thirdPartyServices/arubaCentral/sitesMapping",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_third_party_services_aruba_central_subscription",
    description="GET /thirdPartyServices/arubaCentral/subscription\n\narubaCentralSubscriptionGet758\n\nGet HPE Aruba Networking Central Subscription",
    capability=Capability.READ,
)
async def edgeconnect_get_third_party_services_aruba_central_subscription(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/thirdPartyServices/arubaCentral/subscription",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_third_party_services_awstgnm_aws_appliance_artifact_config",
    description="GET /thirdPartyServices/awstgnm/awsApplianceArtifactConfig\n\nawsApplianceArtifactConfigGet760\n\nRetrieves all AWS Transit Gateway appliance artifact configuration rules.",
    capability=Capability.READ,
)
async def edgeconnect_get_third_party_services_awstgnm_aws_appliance_artifact_config(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/thirdPartyServices/awstgnm/awsApplianceArtifactConfig",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_third_party_services_awstgnm_aws_artifacts",
    description="GET /thirdPartyServices/awstgnm/awsArtifacts\n\ngetAwsArtifacts\n\nRetrieve AWS Transit Gateway Network Manager EC2 artifacts",
    capability=Capability.READ,
)
async def edgeconnect_get_third_party_services_awstgnm_aws_artifacts(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/thirdPartyServices/awstgnm/awsArtifacts",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_third_party_services_awstgnm_aws_segments",
    description="GET /thirdPartyServices/awstgnm/awsSegments\n\nawsSegmentGet760\n\nGet AWS Segments List",
    capability=Capability.READ,
)
async def edgeconnect_get_third_party_services_awstgnm_aws_segments(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/thirdPartyServices/awstgnm/awsSegments",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_third_party_services_awstgnm_awsconfigurations",
    description="GET /thirdPartyServices/awstgnm/awsconfigurations\n\ngetAWSConfigurationEntries\n\nRetrieve AWS Transit Gateway and Cloud Network Edge configurations",
    capability=Capability.READ,
)
async def edgeconnect_get_third_party_services_awstgnm_awsconfigurations(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/thirdPartyServices/awstgnm/awsconfigurations",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_third_party_services_awstgnm_connection_status",
    description="GET /thirdPartyServices/awstgnm/connectionStatus\n\ngetConnectionStatus761\n\nGet AWS VPN Connection BGP Peer Status",
    capability=Capability.READ,
)
async def edgeconnect_get_third_party_services_awstgnm_connection_status(
    ctx: Context,
    nePk: Annotated[
        str,
        Field(
            description="Network Element Primary Key - unique appliance identifier assigned by Orchestrator. Format: '<id>.NE' (e.g., '0.NE', '10.NE')."
        ),
    ],
    interfaceLabel: Annotated[
        str | None,
        Field(
            default=None,
            description="Interface label ID to filter BGP peer status for a specific VPN connection. If omitted, returns status for all interface labels.",
        ),
    ] = None,
    tgwId: Annotated[
        str | None,
        Field(
            default=None,
            description="AWS Transit Gateway ID to filter BGP peer status for a specific Transit Gateway. If omitted, returns status for all associated Transit Gateways.",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if nePk is not None:
        query_params["nePk"] = nePk
    if interfaceLabel is not None:
        query_params["interfaceLabel"] = interfaceLabel
    if tgwId is not None:
        query_params["tgwId"] = tgwId
    return await edgeconnect_request(
        ctx,
        "GET",
        "/thirdPartyServices/awstgnm/connectionStatus",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_third_party_services_awstgnm_connectivity",
    description="GET /thirdPartyServices/awstgnm/connectivity\n\nawsTgnmConnectivityGet762\n\nCheck AWS Transit Gateway Network Manager connectivity status",
    capability=Capability.READ,
)
async def edgeconnect_get_third_party_services_awstgnm_connectivity(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/thirdPartyServices/awstgnm/connectivity",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_third_party_services_awstgnm_core_networks_with_cnedges",
    description="GET /thirdPartyServices/awstgnm/coreNetworksWithCNEdges\n\ncoreNetworksWithCNEdgesGet760\n\nGet AWS Core Networks with CN-Edges",
    capability=Capability.READ,
)
async def edgeconnect_get_third_party_services_awstgnm_core_networks_with_cnedges(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/thirdPartyServices/awstgnm/coreNetworksWithCNEdges",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_third_party_services_awstgnm_default_tunnel_setting",
    description="GET /thirdPartyServices/awstgnm/defaultTunnelSetting\n\nawsTgnmDefaultTunnelSettingGet763\n\nGet default tunnel settings for AWS Transit Gateway Network Manager",
    capability=Capability.READ,
)
async def edgeconnect_get_third_party_services_awstgnm_default_tunnel_setting(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/thirdPartyServices/awstgnm/defaultTunnelSetting",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_third_party_services_awstgnm_global_network_to_cne_association",
    description="GET /thirdPartyServices/awstgnm/globalNetworkToCneAssociation\n\ngetGlobalNetworkToCneAssociation\n\nRetrieve Global Network to Core Network Edge associations",
    capability=Capability.READ,
)
async def edgeconnect_get_third_party_services_awstgnm_global_network_to_cne_association(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/thirdPartyServices/awstgnm/globalNetworkToCneAssociation",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_third_party_services_awstgnm_global_network_to_transit_gateway_association",
    description="GET /thirdPartyServices/awstgnm/globalNetworkToTransitGatewayAssociation\n\nglobalNetworksInfoGet764\n\nGet Global Network to Transit Gateway associations",
    capability=Capability.READ,
)
async def edgeconnect_get_third_party_services_awstgnm_global_network_to_transit_gateway_association(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/thirdPartyServices/awstgnm/globalNetworkToTransitGatewayAssociation",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_third_party_services_awstgnm_global_network_to_transit_gateway_association_refresh",
    description="GET /thirdPartyServices/awstgnm/globalNetworkToTransitGatewayAssociation/refresh\n\ntgwAssociationGet765\n\nGet AWS Transit Gateway to Global Network Associations (Refresh)",
    capability=Capability.READ,
)
async def edgeconnect_get_third_party_services_awstgnm_global_network_to_transit_gateway_association_refresh(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/thirdPartyServices/awstgnm/globalNetworkToTransitGatewayAssociation/refresh",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_third_party_services_awstgnm_global_networks_info",
    description="GET /thirdPartyServices/awstgnm/globalNetworksInfo\n\nglobalNetworksInfoGet766\n\nGet AWS Global Networks ID to Name mapping",
    capability=Capability.READ,
)
async def edgeconnect_get_third_party_services_awstgnm_global_networks_info(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/thirdPartyServices/awstgnm/globalNetworksInfo",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_third_party_services_awstgnm_interfaces",
    description="GET /thirdPartyServices/awstgnm/interfaces\n\ngetAwsTgnmInterfaces767\n\nGet AWS TGNM interface label configuration for VPN orchestration.",
    capability=Capability.READ,
)
async def edgeconnect_get_third_party_services_awstgnm_interfaces(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/thirdPartyServices/awstgnm/interfaces",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_third_party_services_awstgnm_pause_orchestration",
    description="GET /thirdPartyServices/awstgnm/pauseOrchestration\n\npauseOrchestrationGet769\n\nGet AWS Transit Gateway Network Manager orchestration pause state",
    capability=Capability.READ,
)
async def edgeconnect_get_third_party_services_awstgnm_pause_orchestration(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/thirdPartyServices/awstgnm/pauseOrchestration",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_third_party_services_awstgnm_polling_interval",
    description="GET /thirdPartyServices/awstgnm/pollingInterval\n\nawsTgnmPollingIntervalGet771\n\nGet AWS Transit Gateway Network Manager polling interval",
    capability=Capability.READ,
)
async def edgeconnect_get_third_party_services_awstgnm_polling_interval(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/thirdPartyServices/awstgnm/pollingInterval",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_third_party_services_awstgnm_subscription",
    description="GET /thirdPartyServices/awstgnm/subscription\n\nawsTgnmSubscriptionGet773\n\nGet AWS Transit Gateway Network Manager Subscription",
    capability=Capability.READ,
)
async def edgeconnect_get_third_party_services_awstgnm_subscription(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/thirdPartyServices/awstgnm/subscription",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_third_party_services_awstgnm_tgw_association",
    description="GET /thirdPartyServices/awstgnm/tgwAssociation\n\ntgwAssociationGet775\n\nGet all AWS Transit Gateway and Core Network Edge associations for appliances",
    capability=Capability.READ,
)
async def edgeconnect_get_third_party_services_awstgnm_tgw_association(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/thirdPartyServices/awstgnm/tgwAssociation",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_third_party_services_awstgnm_tgw_id_to_name",
    description="GET /thirdPartyServices/awstgnm/tgwIdToName\n\ntgwIdToNameGet760\n\nRetrieve AWS Transit Gateway ID to Name mappings",
    capability=Capability.READ,
)
async def edgeconnect_get_third_party_services_awstgnm_tgw_id_to_name(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/thirdPartyServices/awstgnm/tgwIdToName",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_third_party_services_awstgnm_tgw_not_in_global_network",
    description="GET /thirdPartyServices/awstgnm/tgwNotInGlobalNetwork\n\ntgwNotInGlobalNetworkGet760\n\nGet AWS Transit Gateways not in Global Network",
    capability=Capability.READ,
)
async def edgeconnect_get_third_party_services_awstgnm_tgw_not_in_global_network(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/thirdPartyServices/awstgnm/tgwNotInGlobalNetwork",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_third_party_services_awstgnm_tunnel_setting",
    description="GET /thirdPartyServices/awstgnm/tunnelSetting\n\ngetAwsTgnmTunnelSettings777\n\nGet AWS TGNM tunnel settings per interface label",
    capability=Capability.READ,
)
async def edgeconnect_get_third_party_services_awstgnm_tunnel_setting(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/thirdPartyServices/awstgnm/tunnelSetting",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_third_party_services_awstgnm_vti_cidr",
    description="GET /thirdPartyServices/awstgnm/vti/cidr\n\ngetAwsTgnmVtiCidr779\n\nGet AWS VTI IP Pool Settings",
    capability=Capability.READ,
)
async def edgeconnect_get_third_party_services_awstgnm_vti_cidr(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/thirdPartyServices/awstgnm/vti/cidr",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_third_party_services_awstgnm_vti_cidr_subnets",
    description="GET /thirdPartyServices/awstgnm/vti/cidr/subnets\n\ngetReservedSubnets781\n\nGet VTI Subnets from AWS Subnet Global Pool",
    capability=Capability.READ,
)
async def edgeconnect_get_third_party_services_awstgnm_vti_cidr_subnets(
    ctx: Context,
    reserved: Annotated[
        str | None,
        Field(
            default=None,
            description="Filter subnets by reservation status. When 'true', returns only reserved subnets. When 'false', returns only unreserved subnets. When omitted or null, returns all subnets.",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if reserved is not None:
        query_params["reserved"] = reserved
    return await edgeconnect_request(
        ctx,
        "GET",
        "/thirdPartyServices/awstgnm/vti/cidr/subnets",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_third_party_services_awstgnm_zone",
    description="GET /thirdPartyServices/awstgnm/zone\n\ngetAWSZone\n\nRetrieve AWS Transit Gateway zone configurations",
    capability=Capability.READ,
)
async def edgeconnect_get_third_party_services_awstgnm_zone(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/thirdPartyServices/awstgnm/zone",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_third_party_services_awstgnm_zone_for_default_segment",
    description="GET /thirdPartyServices/awstgnm/zoneForDefaultSegment\n\nzoneForDefaultSegmentGet760\n\nGet VRF zones mapped by segment for AWS Transit Gateway integration",
    capability=Capability.READ,
)
async def edgeconnect_get_third_party_services_awstgnm_zone_for_default_segment(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/thirdPartyServices/awstgnm/zoneForDefaultSegment",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_third_party_services_axis_appliance_association",
    description="GET /thirdPartyServices/axis/applianceAssociation\n\naxisAssociationGet849\n\nRetrieve HPE SSE appliance associations",
    capability=Capability.READ,
)
async def edgeconnect_get_third_party_services_axis_appliance_association(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/thirdPartyServices/axis/applianceAssociation",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_third_party_services_axis_connectivity",
    description="GET /thirdPartyServices/axis/connectivity\n\naxisConnectivityGet853\n\nGet HPE SSE (Axis) Connectivity Status",
    capability=Capability.READ,
)
async def edgeconnect_get_third_party_services_axis_connectivity(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/thirdPartyServices/axis/connectivity",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_third_party_services_axis_default_tunnel_setting",
    description="GET /thirdPartyServices/axis/defaultTunnelSetting\n\naxisDefaultTunnelSettingGet858\n\nGet HPE SSE default tunnel settings",
    capability=Capability.READ,
)
async def edgeconnect_get_third_party_services_axis_default_tunnel_setting(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/thirdPartyServices/axis/defaultTunnelSetting",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_third_party_services_axis_interfaces",
    description="GET /thirdPartyServices/axis/interfaces\n\ngetAxisInterfaces\n\nRetrieve HPE SSE interface label order configuration",
    capability=Capability.READ,
)
async def edgeconnect_get_third_party_services_axis_interfaces(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/thirdPartyServices/axis/interfaces",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_third_party_services_axis_ipsla_rule_destination",
    description="GET /thirdPartyServices/axis/ipslaRuleDestination\n\naxisIpslaRuleDestinationGet858\n\nRetrieve HPE SSE IPSLA rule destination configuration",
    capability=Capability.READ,
)
async def edgeconnect_get_third_party_services_axis_ipsla_rule_destination(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/thirdPartyServices/axis/ipslaRuleDestination",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_third_party_services_axis_ipsla_setting",
    description="GET /thirdPartyServices/axis/ipslaSetting\n\ngetAxisIpslaSetting\n\nGet HPE SSE IP SLA Setting",
    capability=Capability.READ,
)
async def edgeconnect_get_third_party_services_axis_ipsla_setting(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/thirdPartyServices/axis/ipslaSetting",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_third_party_services_axis_pause_orchestration",
    description="GET /thirdPartyServices/axis/pauseOrchestration\n\naxisPauseOrchestrationGet868\n\nGet HPE SSE orchestration pause status",
    capability=Capability.READ,
)
async def edgeconnect_get_third_party_services_axis_pause_orchestration(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/thirdPartyServices/axis/pauseOrchestration",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_third_party_services_axis_polling_interval",
    description="GET /thirdPartyServices/axis/pollingInterval\n\naxisPollingIntervalGet870\n\nGet HPE SSE polling interval for location synchronization",
    capability=Capability.READ,
)
async def edgeconnect_get_third_party_services_axis_polling_interval(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/thirdPartyServices/axis/pollingInterval",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_third_party_services_axis_pop_override",
    description="GET /thirdPartyServices/axis/popOverride\n\naxisRemoteEndpointExceptionGet871\n\nGet all HPE SSE POP override configurations",
    capability=Capability.READ,
)
async def edgeconnect_get_third_party_services_axis_pop_override(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/thirdPartyServices/axis/popOverride",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_third_party_services_axis_sub_location_config",
    description="GET /thirdPartyServices/axis/subLocationConfig\n\naxisSubLocationConfigGet863\n\nGet All HPE SSE Sub-Location Configurations",
    capability=Capability.READ,
)
async def edgeconnect_get_third_party_services_axis_sub_location_config(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/thirdPartyServices/axis/subLocationConfig",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_third_party_services_axis_subscription",
    description="GET /thirdPartyServices/axis/subscription\n\naxisSubscriptionGet875\n\nGet HPE SSE Subscription",
    capability=Capability.READ,
)
async def edgeconnect_get_third_party_services_axis_subscription(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/thirdPartyServices/axis/subscription",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_third_party_services_axis_tunnel_settings",
    description="GET /thirdPartyServices/axis/tunnelSettings\n\ngetAxisTunnelSettings\n\nGet HPE SSE tunnel settings for VPN connections",
    capability=Capability.READ,
)
async def edgeconnect_get_third_party_services_axis_tunnel_settings(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/thirdPartyServices/axis/tunnelSettings",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_third_party_services_azure_azureconfigurations",
    description="GET /thirdPartyServices/azure/azureconfigurations\n\ngetAzureConfigurationEntries\n\nRetrieve Azure VPN Site configurations for Virtual WAN",
    capability=Capability.READ,
)
async def edgeconnect_get_third_party_services_azure_azureconfigurations(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/thirdPartyServices/azure/azureconfigurations",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_third_party_services_azure_connection_status",
    description="GET /thirdPartyServices/azure/connectionStatus\n\ngetConnectionStatus783\n\nGet Azure VWAN VPN Connection BGP Peer Status",
    capability=Capability.READ,
)
async def edgeconnect_get_third_party_services_azure_connection_status(
    ctx: Context,
    nePk: Annotated[
        str,
        Field(
            description="Network Element Primary Key - unique appliance identifier assigned by Orchestrator. Format: '<id>.NE' (e.g., '0.NE', '10.NE')."
        ),
    ],
    interfaceLabel: Annotated[
        str | None,
        Field(
            default=None,
            description="Interface label ID to filter BGP peer status for a specific VPN connection. When omitted, returns status for all interface labels.",
        ),
    ] = None,
    siteId: Annotated[
        str | None,
        Field(
            default=None,
            description="Azure VPN Site ID to filter BGP peer status for a specific VPN connection. When omitted, returns status for all sites.",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if nePk is not None:
        query_params["nePk"] = nePk
    if interfaceLabel is not None:
        query_params["interfaceLabel"] = interfaceLabel
    if siteId is not None:
        query_params["siteId"] = siteId
    return await edgeconnect_request(
        ctx,
        "GET",
        "/thirdPartyServices/azure/connectionStatus",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_third_party_services_azure_connectivity",
    description="GET /thirdPartyServices/azure/connectivity\n\nazureConnectivityGet784\n\nCheck Azure VWAN connectivity status",
    capability=Capability.READ,
)
async def edgeconnect_get_third_party_services_azure_connectivity(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/thirdPartyServices/azure/connectivity",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_third_party_services_azure_default_tunnel_setting",
    description="GET /thirdPartyServices/azure/defaultTunnelSetting\n\nazureDefaultTunnelSettingGet785\n\nGet Azure default tunnel settings",
    capability=Capability.READ,
)
async def edgeconnect_get_third_party_services_azure_default_tunnel_setting(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/thirdPartyServices/azure/defaultTunnelSetting",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_third_party_services_azure_interfaces",
    description="GET /thirdPartyServices/azure/interfaces\n\ngetAzureInterfaces786\n\nGet Azure VWAN interface label order",
    capability=Capability.READ,
)
async def edgeconnect_get_third_party_services_azure_interfaces(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/thirdPartyServices/azure/interfaces",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_third_party_services_azure_lan_interfaces",
    description="GET /thirdPartyServices/azure/lanInterfaces\n\nazureLanSideConnectivityLanInterfacesGet780\n\nGet Azure LAN-side connectivity interface label configuration",
    capability=Capability.READ,
)
async def edgeconnect_get_third_party_services_azure_lan_interfaces(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/thirdPartyServices/azure/lanInterfaces",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_third_party_services_azure_lan_side_connectivity_appliance_association",
    description="GET /thirdPartyServices/azure/lan-side-connectivity/applianceAssociation\n\nazureLanSideConnnectivityAssociationGet775\n\nRetrieve Azure LAN-side appliance associations",
    capability=Capability.READ,
)
async def edgeconnect_get_third_party_services_azure_lan_side_connectivity_appliance_association(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/thirdPartyServices/azure/lan-side-connectivity/applianceAssociation",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_third_party_services_azure_lan_side_connectivity_azure_configuration",
    description="GET /thirdPartyServices/azure/lan-side-connectivity/azureConfiguration\n\nazureLanSideConnnectivityAzureConfigurationGet784\n\nGet Azure LAN-side resource configurations for cloud-deployed EdgeConnect appliances",
    capability=Capability.READ,
)
async def edgeconnect_get_third_party_services_azure_lan_side_connectivity_azure_configuration(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/thirdPartyServices/azure/lan-side-connectivity/azureConfiguration",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_third_party_services_azure_lan_side_connectivity_azure_lan_configurations",
    description="GET /thirdPartyServices/azure/lan-side-connectivity/azureLanConfigurations\n\nazureLanSideConnnectivityLanConfigurationGet781\n\nRetrieve all Azure LAN-side connectivity configurations",
    capability=Capability.READ,
)
async def edgeconnect_get_third_party_services_azure_lan_side_connectivity_azure_lan_configurations(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/thirdPartyServices/azure/lan-side-connectivity/azureLanConfigurations",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_third_party_services_azure_lan_side_connectivity_connection_status",
    description="GET /thirdPartyServices/azure/lan-side-connectivity/connectionStatus\n\nAzureLanSideGetConnectionStatus791\n\nRetrieve Azure LAN-side BGP connection status for an appliance",
    capability=Capability.READ,
)
async def edgeconnect_get_third_party_services_azure_lan_side_connectivity_connection_status(
    ctx: Context,
    nePk: Annotated[
        str,
        Field(
            description="Network Element Primary Key - unique appliance identifier assigned by Orchestrator. Format: '<id>.NE' (e.g., '0.NE', '10.NE')."
        ),
    ],
) -> Any:
    query_params: dict[str, Any] = {}
    if nePk is not None:
        query_params["nePk"] = nePk
    return await edgeconnect_request(
        ctx,
        "GET",
        "/thirdPartyServices/azure/lan-side-connectivity/connectionStatus",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_third_party_services_azure_lan_side_connectivity_connectivity",
    description="GET /thirdPartyServices/azure/lan-side-connectivity/connectivity\n\ngetLanSideConnectivity\n\nGet Azure LAN-side connectivity status for Virtual Hub, Route Server, and Load Balancer",
    capability=Capability.READ,
)
async def edgeconnect_get_third_party_services_azure_lan_side_connectivity_connectivity(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/thirdPartyServices/azure/lan-side-connectivity/connectivity",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_third_party_services_azure_lan_side_connectivity_lan_side_subscription",
    description="GET /thirdPartyServices/azure/lan-side-connectivity/lanSideSubscription\n\nazureLanSideConnnectivityLanSideSubscriptionGet786\n\nRetrieves Azure LAN-side subscription configuration",
    capability=Capability.READ,
)
async def edgeconnect_get_third_party_services_azure_lan_side_connectivity_lan_side_subscription(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/thirdPartyServices/azure/lan-side-connectivity/lanSideSubscription",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_third_party_services_azure_lan_side_connectivity_load_balancers",
    description="GET /thirdPartyServices/azure/lan-side-connectivity/loadBalancers\n\nazureLanSideConnnectivityLoadBalancersGet779\n\nGet Azure Load Balancers for LAN-side connectivity",
    capability=Capability.READ,
)
async def edgeconnect_get_third_party_services_azure_lan_side_connectivity_load_balancers(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/thirdPartyServices/azure/lan-side-connectivity/loadBalancers",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_third_party_services_azure_lan_side_connectivity_pause_orchestration",
    description="GET /thirdPartyServices/azure/lan-side-connectivity/pauseOrchestration\n\ngetAzureLanSidePauseOrchestration\n\nGet Azure LAN Side Connectivity orchestration pause state",
    capability=Capability.READ,
)
async def edgeconnect_get_third_party_services_azure_lan_side_connectivity_pause_orchestration(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/thirdPartyServices/azure/lan-side-connectivity/pauseOrchestration",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_third_party_services_azure_lan_side_connectivity_polling_interval",
    description="GET /thirdPartyServices/azure/lan-side-connectivity/pollingInterval\n\nazureLanSidePollingIntervalGet790\n\nGet the Azure LAN-side connectivity polling interval",
    capability=Capability.READ,
)
async def edgeconnect_get_third_party_services_azure_lan_side_connectivity_polling_interval(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/thirdPartyServices/azure/lan-side-connectivity/pollingInterval",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_third_party_services_azure_lan_side_connectivity_regions",
    description="GET /thirdPartyServices/azure/lan-side-connectivity/regions\n\nazureLanSideConnnectivityRegionsGet782\n\nGet Azure regions mapping for LAN-side connectivity",
    capability=Capability.READ,
)
async def edgeconnect_get_third_party_services_azure_lan_side_connectivity_regions(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/thirdPartyServices/azure/lan-side-connectivity/regions",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_third_party_services_azure_lan_side_connectivity_route_servers",
    description="GET /thirdPartyServices/azure/lan-side-connectivity/routeServers\n\nazureLanSideConnnectivityRouteServersGet778\n\nRetrieve Azure Route Servers",
    capability=Capability.READ,
)
async def edgeconnect_get_third_party_services_azure_lan_side_connectivity_route_servers(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/thirdPartyServices/azure/lan-side-connectivity/routeServers",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_third_party_services_azure_lan_side_connectivity_virtual_hubs",
    description="GET /thirdPartyServices/azure/lan-side-connectivity/virtualHubs\n\ngetAzureVirtualHubsWithVWAN\n\nGet Azure Virtual Hubs grouped by Virtual WAN",
    capability=Capability.READ,
)
async def edgeconnect_get_third_party_services_azure_lan_side_connectivity_virtual_hubs(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/thirdPartyServices/azure/lan-side-connectivity/virtualHubs",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_third_party_services_azure_pause_orchestration",
    description="GET /thirdPartyServices/azure/pauseOrchestration\n\npauseOrchestrationGet788\n\nGet Azure VWAN orchestration pause state",
    capability=Capability.READ,
)
async def edgeconnect_get_third_party_services_azure_pause_orchestration(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/thirdPartyServices/azure/pauseOrchestration",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_third_party_services_azure_subscription",
    description="GET /thirdPartyServices/azure/subscription\n\nazureSubscriptionGet791\n\nGet Azure Virtual WAN Subscription Configuration",
    capability=Capability.READ,
)
async def edgeconnect_get_third_party_services_azure_subscription(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/thirdPartyServices/azure/subscription",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_third_party_services_azure_tunnel_setting",
    description="GET /thirdPartyServices/azure/tunnelSetting\n\ngetAzureTunnelSettings793\n\nGet Azure Virtual WAN tunnel settings",
    capability=Capability.READ,
)
async def edgeconnect_get_third_party_services_azure_tunnel_setting(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/thirdPartyServices/azure/tunnelSetting",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_third_party_services_azure_virtual_wan_association",
    description="GET /thirdPartyServices/azure/virtualWanAssociation\n\nvirtualWanAssociationGet795\n\nGet Azure Virtual WAN to appliance associations",
    capability=Capability.READ,
)
async def edgeconnect_get_third_party_services_azure_virtual_wan_association(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/thirdPartyServices/azure/virtualWanAssociation",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_third_party_services_clearpass_accounts",
    description="GET /thirdPartyServices/clearpass/accounts\n\ngetClearPassAccountById818\n\nRetrieve ClearPass Policy Manager account(s)",
    capability=Capability.READ,
)
async def edgeconnect_get_third_party_services_clearpass_accounts(
    ctx: Context,
    id: Annotated[
        int | None,
        Field(
            default=None,
            description="Unique identifier of a specific ClearPass account to retrieve. If omitted, all accounts are returned.",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if id is not None:
        query_params["id"] = id
    return await edgeconnect_request(
        ctx,
        "GET",
        "/thirdPartyServices/clearpass/accounts",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_third_party_services_clearpass_configurations",
    description="GET /thirdPartyServices/clearpass/configurations\n\ngetAllClearPassConfigurationList820\n\nGet ClearPass Policy Manager configurations",
    capability=Capability.READ,
)
async def edgeconnect_get_third_party_services_clearpass_configurations(
    ctx: Context,
    id: Annotated[
        int | None,
        Field(
            default=None,
            description="The unique identifier of a specific ClearPass configuration. When omitted, all configurations are returned.",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if id is not None:
        query_params["id"] = id
    return await edgeconnect_request(
        ctx,
        "GET",
        "/thirdPartyServices/clearpass/configurations",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_third_party_services_clearpass_connectivity",
    description="GET /thirdPartyServices/clearpass/connectivity\n\ngetConnectivity821\n\nGet ClearPass Policy Manager account connectivity status",
    capability=Capability.READ,
)
async def edgeconnect_get_third_party_services_clearpass_connectivity(
    ctx: Context,
    id: Annotated[
        int,
        Field(
            description="The unique identifier of the ClearPass Policy Manager account configuration to test connectivity for. Must correspond to an existing account."
        ),
    ],
) -> Any:
    query_params: dict[str, Any] = {}
    if id is not None:
        query_params["id"] = id
    return await edgeconnect_request(
        ctx,
        "GET",
        "/thirdPartyServices/clearpass/connectivity",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_third_party_services_clearpass_events_filter",
    description="GET /thirdPartyServices/clearpass/events/filter\n\ngetAllClearPassConfigurationList824\n\nFilter ClearPass Policy Manager events",
    capability=Capability.READ,
)
async def edgeconnect_get_third_party_services_clearpass_events_filter(
    ctx: Context,
    startTime: Annotated[
        int,
        Field(
            description="Start of the time range as epoch timestamp in milliseconds. Must be provided and less than or equal to endTime."
        ),
    ],
    endTime: Annotated[
        int,
        Field(
            description="End of the time range as epoch timestamp in milliseconds. Must be greater than or equal to startTime."
        ),
    ],
    ip: Annotated[
        str | None,
        Field(
            default=None,
            description="Filter by client IP address. Supports wildcard (*) at start or end for partial matching (e.g., '192.168.*' or '*10.1').",
        ),
    ] = None,
    username: Annotated[
        str | None,
        Field(
            default=None,
            description="Filter by username. Supports wildcard (*) at start or end for partial matching (e.g., 'admin*' or '*@domain.com').",
        ),
    ] = None,
    limit: Annotated[
        int | None,
        Field(
            default=None,
            description="Maximum number of events to return. If not specified or exceeds 10000, defaults to 10000.",
        ),
    ] = None,
    type: Annotated[
        str | None,
        Field(
            default=None,
            description="Event filter type. 'All' returns all events, 'Active' returns only sessions without logout (end_time=0), 'Historical' returns completed sessions with logout timestamp.",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if startTime is not None:
        query_params["startTime"] = startTime
    if endTime is not None:
        query_params["endTime"] = endTime
    if ip is not None:
        query_params["ip"] = ip
    if username is not None:
        query_params["username"] = username
    if limit is not None:
        query_params["limit"] = limit
    if type is not None:
        query_params["type"] = type
    return await edgeconnect_request(
        ctx,
        "GET",
        "/thirdPartyServices/clearpass/events/filter",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_third_party_services_clearpass_events_filter_userinfo",
    description="GET /thirdPartyServices/clearpass/events/filter/userinfo\n\ngetUsernameAndRoleListByIpAndTime825\n\nGet usernames and roles for given IP and time range",
    capability=Capability.READ,
)
async def edgeconnect_get_third_party_services_clearpass_events_filter_userinfo(
    ctx: Context,
    ip: Annotated[
        str,
        Field(description="The IP address to query for associated usernames and roles. Must be a valid IPv4 address."),
    ],
    startTime: Annotated[
        int,
        Field(
            description="Start of the time range as epoch timestamp in milliseconds. Events are filtered based on this value."
        ),
    ],
    endTime: Annotated[
        int,
        Field(
            description="End of the time range as epoch timestamp in milliseconds. Must be greater than or equal to startTime."
        ),
    ],
    type: Annotated[
        str | None,
        Field(
            default=None,
            description="Query type for filtering events. Use 'flow' to filter events where the flow time falls within the range (start_time <= startTime AND end_time >= endTime). Default behavior returns events that started within the range.",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if ip is not None:
        query_params["ip"] = ip
    if type is not None:
        query_params["type"] = type
    if startTime is not None:
        query_params["startTime"] = startTime
    if endTime is not None:
        query_params["endTime"] = endTime
    return await edgeconnect_request(
        ctx,
        "GET",
        "/thirdPartyServices/clearpass/events/filter/userinfo",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_third_party_services_clearpass_pause_orchestration",
    description="GET /thirdPartyServices/clearpass/pauseOrchestration\n\nisPauseCPOrchestration826\n\nGet ClearPass orchestration pause status",
    capability=Capability.READ,
)
async def edgeconnect_get_third_party_services_clearpass_pause_orchestration(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/thirdPartyServices/clearpass/pauseOrchestration",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_third_party_services_clearpass_service_status",
    description="GET /thirdPartyServices/clearpass/service/status\n\ngetServiceStatus829\n\nGet ClearPass Policy Manager service endpoint status",
    capability=Capability.READ,
)
async def edgeconnect_get_third_party_services_clearpass_service_status(
    ctx: Context,
    id: Annotated[
        int,
        Field(
            description="Unique identifier of the ClearPass Policy Manager configuration account. Must reference an existing configuration."
        ),
    ],
) -> Any:
    query_params: dict[str, Any] = {}
    if id is not None:
        query_params["id"] = id
    return await edgeconnect_request(
        ctx,
        "GET",
        "/thirdPartyServices/clearpass/service/status",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_third_party_services_netskope_appliance_association",
    description="GET /thirdPartyServices/netskope/applianceAssociation\n\ngetNetskopeApplianceAssociation\n\nRetrieve Netskope appliance associations",
    capability=Capability.READ,
)
async def edgeconnect_get_third_party_services_netskope_appliance_association(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/thirdPartyServices/netskope/applianceAssociation",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_third_party_services_netskope_connection_status",
    description="GET /thirdPartyServices/netskope/connectionStatus\n\ngetConnectionStatus785\n\nGet Netskope tunnel connection status for an appliance",
    capability=Capability.READ,
)
async def edgeconnect_get_third_party_services_netskope_connection_status(
    ctx: Context,
    nePk: Annotated[
        str,
        Field(
            description="Network Element Primary Key - unique appliance identifier assigned by Orchestrator. Format: '<id>.NE' (e.g., '0.NE', '10.NE')."
        ),
    ],
    interfaceLabel: Annotated[
        str | None,
        Field(
            default=None,
            description="The WAN interface label ID to filter results. Currently unused but reserved for future filtering.",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if nePk is not None:
        query_params["nePk"] = nePk
    if interfaceLabel is not None:
        query_params["interfaceLabel"] = interfaceLabel
    return await edgeconnect_request(
        ctx,
        "GET",
        "/thirdPartyServices/netskope/connectionStatus",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_third_party_services_netskope_connectivity",
    description="GET /thirdPartyServices/netskope/connectivity\n\nnetskopeConnectivityGet853\n\nGet Netskope connectivity status",
    capability=Capability.READ,
)
async def edgeconnect_get_third_party_services_netskope_connectivity(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/thirdPartyServices/netskope/connectivity",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_third_party_services_netskope_default_tunnel_setting",
    description="GET /thirdPartyServices/netskope/defaultTunnelSetting\n\ngetNetskopeDefaultTunnelSetting\n\nRetrieve default IPsec tunnel settings for Netskope Cloud integration",
    capability=Capability.READ,
)
async def edgeconnect_get_third_party_services_netskope_default_tunnel_setting(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/thirdPartyServices/netskope/defaultTunnelSetting",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_third_party_services_netskope_interface_tunnel_setting",
    description="GET /thirdPartyServices/netskope/interfaceTunnelSetting\n\ngetNetskopeInterfaceTunnelSetting\n\nRetrieve Netskope tunnel settings for all WAN interface labels",
    capability=Capability.READ,
)
async def edgeconnect_get_third_party_services_netskope_interface_tunnel_setting(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/thirdPartyServices/netskope/interfaceTunnelSetting",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_third_party_services_netskope_interfaces",
    description="GET /thirdPartyServices/netskope/interfaces\n\nnetskopeConfigurationGet851\n\nRetrieve Netskope interface configuration and tunnel settings",
    capability=Capability.READ,
)
async def edgeconnect_get_third_party_services_netskope_interfaces(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/thirdPartyServices/netskope/interfaces",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_third_party_services_netskope_ipsla_rule_destination",
    description="GET /thirdPartyServices/netskope/ipslaRuleDestination\n\nnetskopeIpslaRuleDestinationGet858\n\nRetrieve Netskope IPSLA rule destination configuration",
    capability=Capability.READ,
)
async def edgeconnect_get_third_party_services_netskope_ipsla_rule_destination(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/thirdPartyServices/netskope/ipslaRuleDestination",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_third_party_services_netskope_ipsla_setting",
    description="GET /thirdPartyServices/netskope/ipslaSetting\n\nnetskopeIpslaSettingGet858\n\nRetrieve Netskope IP SLA orchestration settings",
    capability=Capability.READ,
)
async def edgeconnect_get_third_party_services_netskope_ipsla_setting(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/thirdPartyServices/netskope/ipslaSetting",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_third_party_services_netskope_netskope_task_status",
    description="GET /thirdPartyServices/netskope/netskopeTaskStatus\n\nnetskopeTaskStatusGet870\n\nGet Netskope Task Manager status for appliances",
    capability=Capability.READ,
)
async def edgeconnect_get_third_party_services_netskope_netskope_task_status(
    ctx: Context,
    filter: Annotated[
        str | None,
        Field(
            default=None,
            description="Filter appliances by orchestration status. When omitted, returns all appliances with their respective statuses.",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if filter is not None:
        query_params["filter"] = filter
    return await edgeconnect_request(
        ctx,
        "GET",
        "/thirdPartyServices/netskope/netskopeTaskStatus",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_third_party_services_netskope_pause_orchestration",
    description="GET /thirdPartyServices/netskope/pauseOrchestration\n\nnetskopePauseOrchestrationGet868\n\nGet Netskope orchestration pause status",
    capability=Capability.READ,
)
async def edgeconnect_get_third_party_services_netskope_pause_orchestration(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/thirdPartyServices/netskope/pauseOrchestration",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_third_party_services_netskope_polling_interval",
    description="GET /thirdPartyServices/netskope/pollingInterval\n\nNetskopePollingIntervalGet870\n\nGet Netskope location polling interval",
    capability=Capability.READ,
)
async def edgeconnect_get_third_party_services_netskope_polling_interval(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/thirdPartyServices/netskope/pollingInterval",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_third_party_services_netskope_pop_override",
    description="GET /thirdPartyServices/netskope/popOverride\n\ngetPopOverride871\n\nRetrieve all Netskope service edge POP override configurations",
    capability=Capability.READ,
)
async def edgeconnect_get_third_party_services_netskope_pop_override(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/thirdPartyServices/netskope/popOverride",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_third_party_services_netskope_subscription",
    description="GET /thirdPartyServices/netskope/subscription\n\nnetskopeSubscriptionGet875\n\nGet Netskope Subscription",
    capability=Capability.READ,
)
async def edgeconnect_get_third_party_services_netskope_subscription(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/thirdPartyServices/netskope/subscription",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_third_party_services_service_orchestration_bio_breakout",
    description="GET /thirdPartyServices/serviceOrchestration/bioBreakout\n\nbioBreakoutGet830\n\nGet BIO Breakout state for a service provider",
    capability=Capability.READ,
)
async def edgeconnect_get_third_party_services_service_orchestration_bio_breakout(
    ctx: Context,
    serviceId: Annotated[
        str,
        Field(
            description="Unique identifier of the service provider. Must reference an existing service provider in the database."
        ),
    ],
) -> Any:
    query_params: dict[str, Any] = {}
    if serviceId is not None:
        query_params["serviceId"] = serviceId
    return await edgeconnect_request(
        ctx,
        "GET",
        "/thirdPartyServices/serviceOrchestration/bioBreakout",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_third_party_services_service_orchestration_connection_status",
    description="GET /thirdPartyServices/serviceOrchestration/connectionStatus\n\ngetConnectionStatus790\n\nGet service orchestration tunnel connection status for an appliance",
    capability=Capability.READ,
)
async def edgeconnect_get_third_party_services_service_orchestration_connection_status(
    ctx: Context,
    serviceId: Annotated[
        str,
        Field(
            description="Unique identifier for the third-party service provider. Must reference an existing service provider configuration."
        ),
    ],
    nePk: Annotated[
        str,
        Field(
            description="Network Element Primary Key - unique appliance identifier assigned by Orchestrator. Format: '<id>.NE' (e.g., '0.NE', '10.NE')."
        ),
    ],
    interfaceLabel: Annotated[
        str | None,
        Field(
            default=None, description="Optional WAN interface label filter. Not currently used in response filtering."
        ),
    ] = None,
    remoteId: Annotated[
        str | None,
        Field(
            default=None,
            description="Optional remote endpoint identifier filter. Not currently used in response filtering.",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if serviceId is not None:
        query_params["serviceId"] = serviceId
    if nePk is not None:
        query_params["nePk"] = nePk
    if interfaceLabel is not None:
        query_params["interfaceLabel"] = interfaceLabel
    if remoteId is not None:
        query_params["remoteId"] = remoteId
    return await edgeconnect_request(
        ctx,
        "GET",
        "/thirdPartyServices/serviceOrchestration/connectionStatus",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_third_party_services_service_orchestration_default_tunnel_setting",
    description="GET /thirdPartyServices/serviceOrchestration/defaultTunnelSetting\n\nserviceOrchDefaultTunnelSettingGet832\n\nGet default tunnel settings for Service Orchestration",
    capability=Capability.READ,
)
async def edgeconnect_get_third_party_services_service_orchestration_default_tunnel_setting(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/thirdPartyServices/serviceOrchestration/defaultTunnelSetting",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_third_party_services_service_orchestration_interfaces",
    description="GET /thirdPartyServices/serviceOrchestration/interfaces\n\ngetServiceProviderInterfaces833\n\nGet primary and backup interface labels for a Service Provider.",
    capability=Capability.READ,
)
async def edgeconnect_get_third_party_services_service_orchestration_interfaces(
    ctx: Context,
    serviceId: Annotated[
        int,
        Field(
            description="Unique identifier of the service provider. Must be a valid existing service provider ID from the service orchestration configuration."
        ),
    ],
) -> Any:
    query_params: dict[str, Any] = {}
    if serviceId is not None:
        query_params["serviceId"] = serviceId
    return await edgeconnect_request(
        ctx,
        "GET",
        "/thirdPartyServices/serviceOrchestration/interfaces",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_third_party_services_service_orchestration_ipsla_rule_destination",
    description="GET /thirdPartyServices/serviceOrchestration/ipslaRuleDestination\n\nServiceOrchestrationIpslaRuleDestinationGet858\n\nRetrieve IPSLA Rule Destination settings for a Service Provider",
    capability=Capability.READ,
)
async def edgeconnect_get_third_party_services_service_orchestration_ipsla_rule_destination(
    ctx: Context,
    serviceId: Annotated[
        str,
        Field(
            description="Unique identifier of the third-party service provider. Must reference an existing service provider configuration."
        ),
    ],
) -> Any:
    query_params: dict[str, Any] = {}
    if serviceId is not None:
        query_params["serviceId"] = serviceId
    return await edgeconnect_request(
        ctx,
        "GET",
        "/thirdPartyServices/serviceOrchestration/ipslaRuleDestination",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_third_party_services_service_orchestration_ipsla_setting",
    description="GET /thirdPartyServices/serviceOrchestration/ipslaSetting\n\nserviceOrchestrationIpslaSettingGet858\n\nRetrieve IP SLA settings for a service provider",
    capability=Capability.READ,
)
async def edgeconnect_get_third_party_services_service_orchestration_ipsla_setting(
    ctx: Context,
    serviceId: Annotated[
        str,
        Field(
            description="Unique identifier of the service provider. Must reference an existing service provider configuration."
        ),
    ],
) -> Any:
    query_params: dict[str, Any] = {}
    if serviceId is not None:
        query_params["serviceId"] = serviceId
    return await edgeconnect_request(
        ctx,
        "GET",
        "/thirdPartyServices/serviceOrchestration/ipslaSetting",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_third_party_services_service_orchestration_pause_orchestration",
    description="GET /thirdPartyServices/serviceOrchestration/pauseOrchestration\n\ngetPauseOrchestrationState\n\nGet Service Orchestration pause state",
    capability=Capability.READ,
)
async def edgeconnect_get_third_party_services_service_orchestration_pause_orchestration(
    ctx: Context,
    serviceId: Annotated[
        int,
        Field(
            description="The unique identifier of the third-party service provider. This ID is assigned when the service provider is created via the /serviceProviders endpoint."
        ),
    ],
) -> Any:
    query_params: dict[str, Any] = {}
    if serviceId is not None:
        query_params["serviceId"] = serviceId
    return await edgeconnect_request(
        ctx,
        "GET",
        "/thirdPartyServices/serviceOrchestration/pauseOrchestration",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_third_party_services_service_orchestration_remote_end_point_associations",
    description="GET /thirdPartyServices/serviceOrchestration/remoteEndPointAssociations\n\ngetRemoteEndpointAssociation837\n\nRetrieve appliance-to-remote-endpoint associations for a service provider",
    capability=Capability.READ,
)
async def edgeconnect_get_third_party_services_service_orchestration_remote_end_point_associations(
    ctx: Context,
    serviceId: Annotated[
        str,
        Field(
            description="The unique identifier of the service provider. Must reference a valid existing service provider configuration."
        ),
    ],
) -> Any:
    query_params: dict[str, Any] = {}
    if serviceId is not None:
        query_params["serviceId"] = serviceId
    return await edgeconnect_request(
        ctx,
        "GET",
        "/thirdPartyServices/serviceOrchestration/remoteEndPointAssociations",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_third_party_services_service_orchestration_remote_endpoints",
    description="GET /thirdPartyServices/serviceOrchestration/remoteEndpoints\n\ngetRemoteEndpoints841\n\nRetrieve remote endpoints for a service provider",
    capability=Capability.READ,
)
async def edgeconnect_get_third_party_services_service_orchestration_remote_endpoints(
    ctx: Context,
    serviceId: Annotated[
        str,
        Field(
            description="Unique identifier of the service provider. Must reference an existing service provider configuration."
        ),
    ],
) -> Any:
    query_params: dict[str, Any] = {}
    if serviceId is not None:
        query_params["serviceId"] = serviceId
    return await edgeconnect_request(
        ctx,
        "GET",
        "/thirdPartyServices/serviceOrchestration/remoteEndpoints",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_third_party_services_service_orchestration_service_configuration_entries",
    description="GET /thirdPartyServices/serviceOrchestration/serviceConfigurationEntries\n\ngetServiceConfigurationEntries\n\nRetrieve service configuration entries for a service provider",
    capability=Capability.READ,
)
async def edgeconnect_get_third_party_services_service_orchestration_service_configuration_entries(
    ctx: Context,
    serviceId: Annotated[
        int,
        Field(
            description="Unique identifier of the service provider. Must reference an existing service provider configuration."
        ),
    ],
) -> Any:
    query_params: dict[str, Any] = {}
    if serviceId is not None:
        query_params["serviceId"] = serviceId
    return await edgeconnect_request(
        ctx,
        "GET",
        "/thirdPartyServices/serviceOrchestration/serviceConfigurationEntries",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_third_party_services_service_orchestration_service_id_to_name",
    description="GET /thirdPartyServices/serviceOrchestration/serviceIdToName\n\ngetServiceProviderIdToName844\n\nGet service provider ID to name mapping",
    capability=Capability.READ,
)
async def edgeconnect_get_third_party_services_service_orchestration_service_id_to_name(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/thirdPartyServices/serviceOrchestration/serviceIdToName",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_third_party_services_service_orchestration_service_providers",
    description="GET /thirdPartyServices/serviceOrchestration/serviceProviders\n\ngetServiceProviders845\n\nRetrieve service providers for Third Party Orchestration",
    capability=Capability.READ,
)
async def edgeconnect_get_third_party_services_service_orchestration_service_providers(
    ctx: Context,
    serviceId: Annotated[
        str | None,
        Field(
            default=None,
            description="Unique identifier for a specific service provider. If omitted, returns all providers.",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if serviceId is not None:
        query_params["serviceId"] = serviceId
    return await edgeconnect_request(
        ctx,
        "GET",
        "/thirdPartyServices/serviceOrchestration/serviceProviders",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_third_party_services_service_orchestration_tunnel_identifiers",
    description="GET /thirdPartyServices/serviceOrchestration/tunnelIdentifiers\n\ngetServiceIdentifiers790\n\nRetrieve tunnel IKE identifiers for a service provider",
    capability=Capability.READ,
)
async def edgeconnect_get_third_party_services_service_orchestration_tunnel_identifiers(
    ctx: Context,
    serviceId: Annotated[
        str,
        Field(
            description="Unique identifier of the service provider. Must reference an existing service provider in the system."
        ),
    ],
) -> Any:
    query_params: dict[str, Any] = {}
    if serviceId is not None:
        query_params["serviceId"] = serviceId
    return await edgeconnect_request(
        ctx,
        "GET",
        "/thirdPartyServices/serviceOrchestration/tunnelIdentifiers",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_third_party_services_service_orchestration_tunnel_setting",
    description="GET /thirdPartyServices/serviceOrchestration/tunnelSetting\n\ngetServiceOrchTunnelSettings847\n\nGet tunnel settings for a Service Provider",
    capability=Capability.READ,
)
async def edgeconnect_get_third_party_services_service_orchestration_tunnel_setting(
    ctx: Context,
    serviceId: Annotated[
        int,
        Field(
            description="Unique identifier of the Service Provider. Must be a valid integer corresponding to an existing service provider entry."
        ),
    ],
) -> Any:
    query_params: dict[str, Any] = {}
    if serviceId is not None:
        query_params["serviceId"] = serviceId
    return await edgeconnect_request(
        ctx,
        "GET",
        "/thirdPartyServices/serviceOrchestration/tunnelSetting",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_third_party_services_zscaler_appliance_association",
    description="GET /thirdPartyServices/zscaler/applianceAssociation\n\nzscalerAssociationGet849\n\nGet Zscaler appliance associations",
    capability=Capability.READ,
)
async def edgeconnect_get_third_party_services_zscaler_appliance_association(
    ctx: Context,
    If_None_Match: Annotated[
        str | None,
        Field(
            default=None,
            description="ETag value from previous response for cache validation. If matches current state, returns 304 Not Modified.",
        ),
    ] = None,
) -> Any:
    header_params: dict[str, Any] = {}
    if If_None_Match is not None:
        header_params["If-None-Match"] = If_None_Match
    return await edgeconnect_request(
        ctx,
        "GET",
        "/thirdPartyServices/zscaler/applianceAssociation",
        query_params=None,
        header_params=header_params or None,
    )


@tool(
    name="edgeconnect_get_third_party_services_zscaler_configuration",
    description="GET /thirdPartyServices/zscaler/configuration\n\nzscalerConfigurationGet851\n\nGet Zscaler Configuration",
    capability=Capability.READ,
)
async def edgeconnect_get_third_party_services_zscaler_configuration(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/thirdPartyServices/zscaler/configuration",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_third_party_services_zscaler_connection_status",
    description="GET /thirdPartyServices/zscaler/connectionStatus\n\ngetConnectionStatus78\n\nGets all Zscaler Tunnels with IP SLA's status of the appliance. The response contains <nePk_labelId>, <connectionStatus> map.",
    capability=Capability.READ,
)
async def edgeconnect_get_third_party_services_zscaler_connection_status(
    ctx: Context,
    nePk: Annotated[
        str,
        Field(
            description="Network Element Primary Key - unique appliance identifier assigned by Orchestrator. Format: '<id>.NE' (e.g., '0.NE', '10.NE')."
        ),
    ],
    interfaceLabel: Annotated[
        str | None,
        Field(
            default=None,
            description="Optional interface label filter. This parameter exists in the API but is currently not utilized in the implementation. Tunnel status is returned for all configured Zscaler interfaces on the specified appliance regardless of this parameter.",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if nePk is not None:
        query_params["nePk"] = nePk
    if interfaceLabel is not None:
        query_params["interfaceLabel"] = interfaceLabel
    return await edgeconnect_request(
        ctx,
        "GET",
        "/thirdPartyServices/zscaler/connectionStatus",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_third_party_services_zscaler_connectivity",
    description="GET /thirdPartyServices/zscaler/connectivity\n\nzscalerConnectivityGet853\n\nGet Zscaler connectivity status",
    capability=Capability.READ,
)
async def edgeconnect_get_third_party_services_zscaler_connectivity(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/thirdPartyServices/zscaler/connectivity",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_third_party_services_zscaler_countries",
    description="GET /thirdPartyServices/zscaler/countries\n\ngetZscalerCountries\n\nRetrieve Zscaler country code mappings",
    capability=Capability.READ,
)
async def edgeconnect_get_third_party_services_zscaler_countries(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/thirdPartyServices/zscaler/countries",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_third_party_services_zscaler_default_countries",
    description="GET /thirdPartyServices/zscaler/defaultCountries\n\ngetZscalerDefaultCountries\n\nGet default ISO-2 country code to Zscaler country enum mappings",
    capability=Capability.READ,
)
async def edgeconnect_get_third_party_services_zscaler_default_countries(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/thirdPartyServices/zscaler/defaultCountries",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_third_party_services_zscaler_default_timezones",
    description="GET /thirdPartyServices/zscaler/defaultTimezones\n\ngetZscalerDefaultTimezones\n\nGet default Zscaler timezone mappings",
    capability=Capability.READ,
)
async def edgeconnect_get_third_party_services_zscaler_default_timezones(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/thirdPartyServices/zscaler/defaultTimezones",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_third_party_services_zscaler_default_tunnel_setting",
    description="GET /thirdPartyServices/zscaler/defaultTunnelSetting\n\nzscalerDefaultTunnelSettingGet858\n\nGet default Zscaler tunnel settings",
    capability=Capability.READ,
)
async def edgeconnect_get_third_party_services_zscaler_default_tunnel_setting(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/thirdPartyServices/zscaler/defaultTunnelSetting",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_third_party_services_zscaler_gateway_options_appliance",
    description="GET /thirdPartyServices/zscaler/gatewayOptionsAppliance\n\ngatewayOptionsAppliance860\n\nGet computed Zscaler locations and gateway options for an appliance",
    capability=Capability.READ,
)
async def edgeconnect_get_third_party_services_zscaler_gateway_options_appliance(
    ctx: Context,
    nePk: Annotated[
        str,
        Field(
            description="Network Element Primary Key - unique appliance identifier assigned by Orchestrator. Format: '<id>.NE' (e.g., '0.NE', '10.NE')."
        ),
    ],
) -> Any:
    query_params: dict[str, Any] = {}
    if nePk is not None:
        query_params["nePk"] = nePk
    return await edgeconnect_request(
        ctx,
        "GET",
        "/thirdPartyServices/zscaler/gatewayOptionsAppliance",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_third_party_services_zscaler_interface_tunnel_setting",
    description="GET /thirdPartyServices/zscaler/interfaceTunnelSetting\n\ngetZscalerInterfaceTunnelSetting\n\nRetrieve Zscaler tunnel settings for all WAN interface labels",
    capability=Capability.READ,
)
async def edgeconnect_get_third_party_services_zscaler_interface_tunnel_setting(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/thirdPartyServices/zscaler/interfaceTunnelSetting",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_third_party_services_zscaler_ipsla_rule_destination",
    description="GET /thirdPartyServices/zscaler/ipslaRuleDestination\n\nzscalerIpslaRuleDestinationGet\n\nRetrieve Zscaler IP SLA rule destination configuration",
    capability=Capability.READ,
)
async def edgeconnect_get_third_party_services_zscaler_ipsla_rule_destination(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/thirdPartyServices/zscaler/ipslaRuleDestination",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_third_party_services_zscaler_ipsla_setting",
    description="GET /thirdPartyServices/zscaler/ipslaSetting\n\ngetZscalerIpslaSetting\n\nRetrieve Zscaler IP SLA orchestration settings",
    capability=Capability.READ,
)
async def edgeconnect_get_third_party_services_zscaler_ipsla_setting(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/thirdPartyServices/zscaler/ipslaSetting",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_third_party_services_zscaler_location_config",
    description="GET /thirdPartyServices/zscaler/locationConfig\n\nzscalerLocationConfigGet863\n\nRetrieve Zscaler Location and Sub-Location gateway options and bandwidth control configurations",
    capability=Capability.READ,
)
async def edgeconnect_get_third_party_services_zscaler_location_config(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/thirdPartyServices/zscaler/locationConfig",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_third_party_services_zscaler_orchestrate_gateway_options",
    description="GET /thirdPartyServices/zscaler/orchestrateGatewayOptions\n\nzscalerOrchestrateGatewayOptionsGet865\n\nGet Zscaler gateway options orchestration status",
    capability=Capability.READ,
)
async def edgeconnect_get_third_party_services_zscaler_orchestrate_gateway_options(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/thirdPartyServices/zscaler/orchestrateGatewayOptions",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_third_party_services_zscaler_pause_orchestration",
    description="GET /thirdPartyServices/zscaler/pauseOrchestration\n\nzscalerPauseOrchestrationGet868\n\nGet Zscaler orchestration pause status",
    capability=Capability.READ,
)
async def edgeconnect_get_third_party_services_zscaler_pause_orchestration(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/thirdPartyServices/zscaler/pauseOrchestration",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_third_party_services_zscaler_polling_interval",
    description="GET /thirdPartyServices/zscaler/pollingInterval\n\ngetZscalerPollingInterval\n\nGet Zscaler location data synchronization interval",
    capability=Capability.READ,
)
async def edgeconnect_get_third_party_services_zscaler_polling_interval(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/thirdPartyServices/zscaler/pollingInterval",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_third_party_services_zscaler_remote_endpoint_exception",
    description="GET /thirdPartyServices/zscaler/remoteEndpointException\n\nzscalerRemoteEndpointExceptionGet871\n\nRetrieve all Zscaler ZEN override configurations",
    capability=Capability.READ,
)
async def edgeconnect_get_third_party_services_zscaler_remote_endpoint_exception(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/thirdPartyServices/zscaler/remoteEndpointException",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_third_party_services_zscaler_subscription",
    description="GET /thirdPartyServices/zscaler/subscription\n\nzscalerSubscriptionGet875\n\nGet Zscaler Subscription",
    capability=Capability.READ,
)
async def edgeconnect_get_third_party_services_zscaler_subscription(
    ctx: Context,
    If_None_Match: Annotated[
        str | None,
        Field(
            default=None,
            description="ETag value from previous response for cache validation. Returns 304 if unchanged.",
        ),
    ] = None,
) -> Any:
    header_params: dict[str, Any] = {}
    if If_None_Match is not None:
        header_params["If-None-Match"] = If_None_Match
    return await edgeconnect_request(
        ctx,
        "GET",
        "/thirdPartyServices/zscaler/subscription",
        query_params=None,
        header_params=header_params or None,
    )


@tool(
    name="edgeconnect_get_third_party_services_zscaler_timezones",
    description="GET /thirdPartyServices/zscaler/timezones\n\ngetZscalerTimezones\n\nGet Zscaler timezone mappings",
    capability=Capability.READ,
)
async def edgeconnect_get_third_party_services_zscaler_timezones(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/thirdPartyServices/zscaler/timezones",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_third_party_services_zscaler_zdx_vpn_locations",
    description="GET /thirdPartyServices/zscaler/zdxVpnLocations\n\ngetZscalerZdxVpnLocations\n\nGet Zscaler ZDX VPN locations for appliances",
    capability=Capability.READ,
)
async def edgeconnect_get_third_party_services_zscaler_zdx_vpn_locations(
    ctx: Context,
    nePk: Annotated[
        str | None,
        Field(
            default=None,
            description="Network Element Primary Key - unique appliance identifier assigned by Orchestrator. Format: '<id>.NE' (e.g., '0.NE', '10.NE'). When omitted, results are returned for all appliances.",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if nePk is not None:
        query_params["nePk"] = nePk
    return await edgeconnect_request(
        ctx,
        "GET",
        "/thirdPartyServices/zscaler/zdxVpnLocations",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_third_party_services_zscaler_zscaler_task_status",
    description="GET /thirdPartyServices/zscaler/zscalerTaskStatus\n\nzscalerTaskStatusGet870\n\nGet Zscaler Task Manager status for appliances",
    capability=Capability.READ,
)
async def edgeconnect_get_third_party_services_zscaler_zscaler_task_status(
    ctx: Context,
    filter: Annotated[
        str | None,
        Field(
            default=None,
            description="Filter appliances by orchestration status. When omitted, returns all appliances with their respective statuses.",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if filter is not None:
        query_params["filter"] = filter
    return await edgeconnect_request(
        ctx,
        "GET",
        "/thirdPartyServices/zscaler/zscalerTaskStatus",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_post_gms_vti_cidr",
    description="POST /gms/vti/cidr\n\npostAzureVtiCidr791\n\nConfigure VTI IP Pool Subnet for Azure vWAN Tunnel Interfaces",
    capability=Capability.WRITE,
)
async def edgeconnect_post_gms_vti_cidr(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/gms/vti/cidr",
        query_params=None,
        body=body,
    )


@tool(
    name="edgeconnect_post_third_party_services_aruba_central_sites_mapping",
    description="POST /thirdPartyServices/arubaCentral/sitesMapping\n\npostAssignAppliancetoSite756\n\nAssign appliance to HPE ANW Central site",
    capability=Capability.WRITE,
)
async def edgeconnect_post_third_party_services_aruba_central_sites_mapping(
    ctx: Context,
    nePk: Annotated[
        str,
        Field(
            description="Network Element Primary Key - unique appliance identifier assigned by Orchestrator. Format: '<id>.NE' (e.g., '0.NE', '10.NE')."
        ),
    ],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    query_params: dict[str, Any] = {}
    if nePk is not None:
        query_params["nePk"] = nePk
    return await edgeconnect_request(
        ctx,
        "POST",
        "/thirdPartyServices/arubaCentral/sitesMapping",
        query_params=query_params or None,
        body=body,
    )


@tool(
    name="edgeconnect_post_third_party_services_aruba_central_subscription",
    description="POST /thirdPartyServices/arubaCentral/subscription\n\narubaCentralSubscriptionPost759\n\nCreate or Update HPE Aruba Networking Central Subscription",
    capability=Capability.WRITE,
)
async def edgeconnect_post_third_party_services_aruba_central_subscription(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/thirdPartyServices/arubaCentral/subscription",
        query_params=None,
        body=body,
    )


@tool(
    name="edgeconnect_post_third_party_services_awstgnm_aws_appliance_artifact_config",
    description="POST /thirdPartyServices/awstgnm/awsApplianceArtifactConfig\n\nsetawsApplianceArtifactConfig768\n\nCreates, updates, or deletes AWS appliance artifact configuration rules.",
    capability=Capability.WRITE,
)
async def edgeconnect_post_third_party_services_awstgnm_aws_appliance_artifact_config(
    ctx: Context,
    body: Annotated[list[Any], Field(description="Request body (required)")],
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/thirdPartyServices/awstgnm/awsApplianceArtifactConfig",
        query_params=None,
        body=body,
    )


@tool(
    name="edgeconnect_post_third_party_services_awstgnm_interfaces",
    description="POST /thirdPartyServices/awstgnm/interfaces\n\nsetAwsTgnmInterfaces768\n\nConfigure WAN interface labels for AWS TGNM VPN orchestration.",
    capability=Capability.WRITE,
)
async def edgeconnect_post_third_party_services_awstgnm_interfaces(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/thirdPartyServices/awstgnm/interfaces",
        query_params=None,
        body=body,
    )


@tool(
    name="edgeconnect_post_third_party_services_awstgnm_pause_orchestration",
    description="POST /thirdPartyServices/awstgnm/pauseOrchestration\n\nsetAwsTgnmPauseOrchestration770\n\nSet AWS Transit Gateway Network Manager orchestration pause state",
    capability=Capability.WRITE,
)
async def edgeconnect_post_third_party_services_awstgnm_pause_orchestration(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/thirdPartyServices/awstgnm/pauseOrchestration",
        query_params=None,
        body=body,
    )


@tool(
    name="edgeconnect_post_third_party_services_awstgnm_subscription",
    description="POST /thirdPartyServices/awstgnm/subscription\n\nawsTgnmSubscriptionPost774\n\nCreate or Update AWS Transit Gateway Network Manager Subscription",
    capability=Capability.WRITE,
)
async def edgeconnect_post_third_party_services_awstgnm_subscription(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/thirdPartyServices/awstgnm/subscription",
        query_params=None,
        body=body,
    )


@tool(
    name="edgeconnect_post_third_party_services_awstgnm_tgw_association",
    description="POST /thirdPartyServices/awstgnm/tgwAssociation\n\ntgwAssociationPost776\n\nCreate or update appliance-to-AWS Transit Gateway and Core Network Edge associations",
    capability=Capability.WRITE,
)
async def edgeconnect_post_third_party_services_awstgnm_tgw_association(
    ctx: Context,
    body: Annotated[list[Any], Field(description="Request body (required)")],
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/thirdPartyServices/awstgnm/tgwAssociation",
        query_params=None,
        body=body,
    )


@tool(
    name="edgeconnect_post_third_party_services_awstgnm_tunnel_setting",
    description="POST /thirdPartyServices/awstgnm/tunnelSetting\n\nsetAwsTgnmTunnelSettings778\n\nUpdate AWS TGNM tunnel settings per interface label",
    capability=Capability.WRITE,
)
async def edgeconnect_post_third_party_services_awstgnm_tunnel_setting(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/thirdPartyServices/awstgnm/tunnelSetting",
        query_params=None,
        body=body,
    )


@tool(
    name="edgeconnect_post_third_party_services_awstgnm_vti_cidr",
    description="POST /thirdPartyServices/awstgnm/vti/cidr\n\npostAwsTgnmVtiCidr780\n\nUpdate AWS VTI IP Pool Settings",
    capability=Capability.WRITE,
)
async def edgeconnect_post_third_party_services_awstgnm_vti_cidr(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/thirdPartyServices/awstgnm/vti/cidr",
        query_params=None,
        body=body,
    )


@tool(
    name="edgeconnect_post_third_party_services_awstgnm_zone",
    description="POST /thirdPartyServices/awstgnm/zone\n\nsaveAwsSegmentZoneAssociation\n\nConfigure AWS Transit Gateway zone associations",
    capability=Capability.WRITE,
)
async def edgeconnect_post_third_party_services_awstgnm_zone(
    ctx: Context,
    body: Annotated[list[Any], Field(description="Request body (required)")],
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/thirdPartyServices/awstgnm/zone",
        query_params=None,
        body=body,
    )


@tool(
    name="edgeconnect_post_third_party_services_axis_appliance_association",
    description="POST /thirdPartyServices/axis/applianceAssociation\n\naxisAssociationPost850\n\nUpdate HPE SSE appliance associations",
    capability=Capability.WRITE,
)
async def edgeconnect_post_third_party_services_axis_appliance_association(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/thirdPartyServices/axis/applianceAssociation",
        query_params=None,
        body=body,
    )


@tool(
    name="edgeconnect_post_third_party_services_axis_interfaces",
    description="POST /thirdPartyServices/axis/interfaces\n\nsaveAxisInterfaces\n\nSave HPE SSE interface label order configuration",
    capability=Capability.WRITE,
)
async def edgeconnect_post_third_party_services_axis_interfaces(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/thirdPartyServices/axis/interfaces",
        query_params=None,
        body=body,
    )


@tool(
    name="edgeconnect_post_third_party_services_axis_ipsla_rule_destination",
    description="POST /thirdPartyServices/axis/ipslaRuleDestination\n\nAxisIPSLARules855\n\nSave HPE SSE IPSLA rule destination configuration",
    capability=Capability.WRITE,
)
async def edgeconnect_post_third_party_services_axis_ipsla_rule_destination(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/thirdPartyServices/axis/ipslaRuleDestination",
        query_params=None,
        body=body,
    )


@tool(
    name="edgeconnect_post_third_party_services_axis_ipsla_setting",
    description="POST /thirdPartyServices/axis/ipslaSetting\n\nsetAxisIpslaSetting\n\nUpdate HPE SSE IP SLA Setting",
    capability=Capability.WRITE,
)
async def edgeconnect_post_third_party_services_axis_ipsla_setting(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/thirdPartyServices/axis/ipslaSetting",
        query_params=None,
        body=body,
    )


@tool(
    name="edgeconnect_post_third_party_services_axis_locations",
    description="POST /thirdPartyServices/axis/locations\n\ngetAxisSitesInfo\n\nGet HPE SSE site information for specified appliances",
    capability=Capability.WRITE,
)
async def edgeconnect_post_third_party_services_axis_locations(
    ctx: Context,
    body: Annotated[list[Any], Field(description="Request body (required)")],
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/thirdPartyServices/axis/locations",
        query_params=None,
        body=body,
    )


@tool(
    name="edgeconnect_post_third_party_services_axis_pause_orchestration",
    description="POST /thirdPartyServices/axis/pauseOrchestration\n\naxisPauseOrchestrationPost869\n\nPause or resume HPE SSE orchestration",
    capability=Capability.WRITE,
)
async def edgeconnect_post_third_party_services_axis_pause_orchestration(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/thirdPartyServices/axis/pauseOrchestration",
        query_params=None,
        body=body,
    )


@tool(
    name="edgeconnect_post_third_party_services_axis_polling_interval",
    description="POST /thirdPartyServices/axis/pollingInterval\n\nAxisPollingInterval855\n\nUpdate HPE SSE polling interval for location synchronization",
    capability=Capability.WRITE,
)
async def edgeconnect_post_third_party_services_axis_polling_interval(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/thirdPartyServices/axis/pollingInterval",
        query_params=None,
        body=body,
    )


@tool(
    name="edgeconnect_post_third_party_services_axis_pop_override",
    description="POST /thirdPartyServices/axis/popOverride\n\naxisRemoteEndpointExceptionPost873\n\nAdd or update HPE SSE POP override configuration",
    capability=Capability.WRITE,
)
async def edgeconnect_post_third_party_services_axis_pop_override(
    ctx: Context,
    nePk: Annotated[
        str,
        Field(
            description="Network Element Primary Key - unique appliance identifier assigned by Orchestrator. Format: '<id>.NE' (e.g., '0.NE', '10.NE')."
        ),
    ],
    labelId: Annotated[
        str,
        Field(
            description="ID of the WAN interface label for which to configure the POP override. Must be a valid WAN interface label ID."
        ),
    ],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    query_params: dict[str, Any] = {}
    if nePk is not None:
        query_params["nePk"] = nePk
    if labelId is not None:
        query_params["labelId"] = labelId
    return await edgeconnect_request(
        ctx,
        "POST",
        "/thirdPartyServices/axis/popOverride",
        query_params=query_params or None,
        body=body,
    )


@tool(
    name="edgeconnect_post_third_party_services_axis_sub_location_config",
    description="POST /thirdPartyServices/axis/subLocationConfig\n\naxisSubLocationConfigPost864\n\nCreate or Update HPE SSE Sub-Location Configurations",
    capability=Capability.WRITE,
)
async def edgeconnect_post_third_party_services_axis_sub_location_config(
    ctx: Context,
    body: Annotated[list[Any], Field(description="Request body (required)")],
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/thirdPartyServices/axis/subLocationConfig",
        query_params=None,
        body=body,
    )


@tool(
    name="edgeconnect_post_third_party_services_axis_subscription",
    description="POST /thirdPartyServices/axis/subscription\n\naxisSubscriptionPost876\n\nCreate or Update HPE SSE Subscription",
    capability=Capability.WRITE,
)
async def edgeconnect_post_third_party_services_axis_subscription(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/thirdPartyServices/axis/subscription",
        query_params=None,
        body=body,
    )


@tool(
    name="edgeconnect_post_third_party_services_axis_tunnel_settings",
    description="POST /thirdPartyServices/axis/tunnelSettings\n\nsaveAxisTunnelSettings\n\nSave HPE SSE tunnel settings",
    capability=Capability.WRITE,
)
async def edgeconnect_post_third_party_services_axis_tunnel_settings(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/thirdPartyServices/axis/tunnelSettings",
        query_params=None,
        body=body,
    )


@tool(
    name="edgeconnect_post_third_party_services_azure_interfaces",
    description="POST /thirdPartyServices/azure/interfaces\n\nsetAzureInterfaces787\n\nSet Azure VWAN interface label order configuration",
    capability=Capability.WRITE,
)
async def edgeconnect_post_third_party_services_azure_interfaces(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/thirdPartyServices/azure/interfaces",
        query_params=None,
        body=body,
    )


@tool(
    name="edgeconnect_post_third_party_services_azure_lan_interfaces",
    description="POST /thirdPartyServices/azure/lanInterfaces\n\nazureLanSideConnectivityLanInterfacesPost781\n\nConfigure Azure LAN-side connectivity interface labels",
    capability=Capability.WRITE,
)
async def edgeconnect_post_third_party_services_azure_lan_interfaces(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/thirdPartyServices/azure/lanInterfaces",
        query_params=None,
        body=body,
    )


@tool(
    name="edgeconnect_post_third_party_services_azure_lan_side_connectivity_appliance_association",
    description="POST /thirdPartyServices/azure/lan-side-connectivity/applianceAssociation\n\nazureLanSideConnnectivityAssociationPost776\n\nCreate or update Azure LAN-side appliance associations",
    capability=Capability.WRITE,
)
async def edgeconnect_post_third_party_services_azure_lan_side_connectivity_appliance_association(
    ctx: Context,
    body: Annotated[list[Any], Field(description="Request body (required)")],
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/thirdPartyServices/azure/lan-side-connectivity/applianceAssociation",
        query_params=None,
        body=body,
    )


@tool(
    name="edgeconnect_post_third_party_services_azure_lan_side_connectivity_azure_configuration",
    description="POST /thirdPartyServices/azure/lan-side-connectivity/azureConfiguration\n\nazureLanSideConnnectivityAzureConfigurationPost785\n\nSave Azure LAN-side resource configurations (upsert operation)",
    capability=Capability.WRITE,
)
async def edgeconnect_post_third_party_services_azure_lan_side_connectivity_azure_configuration(
    ctx: Context,
    body: Annotated[list[Any], Field(description="Request body (required)")],
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/thirdPartyServices/azure/lan-side-connectivity/azureConfiguration",
        query_params=None,
        body=body,
    )


@tool(
    name="edgeconnect_post_third_party_services_azure_lan_side_connectivity_lan_side_subscription",
    description="POST /thirdPartyServices/azure/lan-side-connectivity/lanSideSubscription\n\nazureLanSideConnnectivityLanSideSubscriptionPost787\n\nCreate or update Azure LAN-side subscription",
    capability=Capability.WRITE,
)
async def edgeconnect_post_third_party_services_azure_lan_side_connectivity_lan_side_subscription(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/thirdPartyServices/azure/lan-side-connectivity/lanSideSubscription",
        query_params=None,
        body=body,
    )


@tool(
    name="edgeconnect_post_third_party_services_azure_lan_side_connectivity_pause_orchestration",
    description="POST /thirdPartyServices/azure/lan-side-connectivity/pauseOrchestration\n\nsetAzureLanSidePauseOrchestration\n\nSet Azure LAN Side Connectivity orchestration pause state",
    capability=Capability.WRITE,
)
async def edgeconnect_post_third_party_services_azure_lan_side_connectivity_pause_orchestration(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/thirdPartyServices/azure/lan-side-connectivity/pauseOrchestration",
        query_params=None,
        body=body,
    )


@tool(
    name="edgeconnect_post_third_party_services_azure_pause_orchestration",
    description="POST /thirdPartyServices/azure/pauseOrchestration\n\npauseOrchestrationPost789\n\nSet Azure VWAN orchestration pause state",
    capability=Capability.WRITE,
)
async def edgeconnect_post_third_party_services_azure_pause_orchestration(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/thirdPartyServices/azure/pauseOrchestration",
        query_params=None,
        body=body,
    )


@tool(
    name="edgeconnect_post_third_party_services_azure_subscription",
    description="POST /thirdPartyServices/azure/subscription\n\nazureSubscriptionPost792\n\nCreate or Update Azure Virtual WAN Subscription",
    capability=Capability.WRITE,
)
async def edgeconnect_post_third_party_services_azure_subscription(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/thirdPartyServices/azure/subscription",
        query_params=None,
        body=body,
    )


@tool(
    name="edgeconnect_post_third_party_services_azure_tunnel_setting",
    description="POST /thirdPartyServices/azure/tunnelSetting\n\nsetAzureTunnelSettings794\n\nSet Azure Virtual WAN tunnel settings",
    capability=Capability.WRITE,
)
async def edgeconnect_post_third_party_services_azure_tunnel_setting(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/thirdPartyServices/azure/tunnelSetting",
        query_params=None,
        body=body,
    )


@tool(
    name="edgeconnect_post_third_party_services_azure_virtual_wan_association",
    description="POST /thirdPartyServices/azure/virtualWanAssociation\n\nvirtualWanAssociationPost796\n\nSave Azure Virtual WAN to appliance associations",
    capability=Capability.WRITE,
)
async def edgeconnect_post_third_party_services_azure_virtual_wan_association(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/thirdPartyServices/azure/virtualWanAssociation",
        query_params=None,
        body=body,
    )


@tool(
    name="edgeconnect_post_third_party_services_clearpass_accounts",
    description="POST /thirdPartyServices/clearpass/accounts\n\nsaveClearPassAccount815\n\nAdd new ClearPass Policy Manager account",
    capability=Capability.WRITE,
)
async def edgeconnect_post_third_party_services_clearpass_accounts(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/thirdPartyServices/clearpass/accounts",
        query_params=None,
        body=body,
    )


@tool(
    name="edgeconnect_post_third_party_services_clearpass_event_login",
    description="POST /thirdPartyServices/clearpass/event/login\n\npostLoginInfoFromCPPM822\n\nPosts ClearPass Policy Manager login event",
    capability=Capability.WRITE,
)
async def edgeconnect_post_third_party_services_clearpass_event_login(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/thirdPartyServices/clearpass/event/login",
        query_params=None,
        body=body,
    )


@tool(
    name="edgeconnect_post_third_party_services_clearpass_event_logout",
    description="POST /thirdPartyServices/clearpass/event/logout\n\npostLogoutInfoFromCPPM823\n\nPost ClearPass Policy Manager logout event",
    capability=Capability.WRITE,
)
async def edgeconnect_post_third_party_services_clearpass_event_logout(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/thirdPartyServices/clearpass/event/logout",
        query_params=None,
        body=body,
    )


@tool(
    name="edgeconnect_post_third_party_services_clearpass_pause_orchestration",
    description="POST /thirdPartyServices/clearpass/pauseOrchestration\n\nsavePauseCPOrchestration827\n\nSet ClearPass orchestration pause status",
    capability=Capability.WRITE,
)
async def edgeconnect_post_third_party_services_clearpass_pause_orchestration(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/thirdPartyServices/clearpass/pauseOrchestration",
        query_params=None,
        body=body,
    )


@tool(
    name="edgeconnect_post_third_party_services_netskope_appliance_association",
    description="POST /thirdPartyServices/netskope/applianceAssociation\n\nsaveNetskopeApplianceAssociation\n\nSave Netskope appliance associations",
    capability=Capability.WRITE,
)
async def edgeconnect_post_third_party_services_netskope_appliance_association(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/thirdPartyServices/netskope/applianceAssociation",
        query_params=None,
        body=body,
    )


@tool(
    name="edgeconnect_post_third_party_services_netskope_interface_tunnel_setting",
    description="POST /thirdPartyServices/netskope/interfaceTunnelSetting\n\nsaveNetskopeInterfaceTunnelSetting\n\nSave Netskope tunnel settings for WAN interface labels",
    capability=Capability.WRITE,
)
async def edgeconnect_post_third_party_services_netskope_interface_tunnel_setting(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/thirdPartyServices/netskope/interfaceTunnelSetting",
        query_params=None,
        body=body,
    )


@tool(
    name="edgeconnect_post_third_party_services_netskope_interfaces",
    description="POST /thirdPartyServices/netskope/interfaces\n\nnetskopeConfigurationPost852\n\nSave Netskope interface configuration and tunnel settings",
    capability=Capability.WRITE,
)
async def edgeconnect_post_third_party_services_netskope_interfaces(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/thirdPartyServices/netskope/interfaces",
        query_params=None,
        body=body,
    )


@tool(
    name="edgeconnect_post_third_party_services_netskope_ipsla_rule_destination",
    description="POST /thirdPartyServices/netskope/ipslaRuleDestination\n\nsaveNetskopeIpslaRuleDestination\n\nSave Netskope IPSLA rule destination",
    capability=Capability.WRITE,
)
async def edgeconnect_post_third_party_services_netskope_ipsla_rule_destination(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/thirdPartyServices/netskope/ipslaRuleDestination",
        query_params=None,
        body=body,
    )


@tool(
    name="edgeconnect_post_third_party_services_netskope_ipsla_setting",
    description="POST /thirdPartyServices/netskope/ipslaSetting\n\nNetskopeIPSLASetting855\n\nUpdate Netskope IP SLA orchestration settings",
    capability=Capability.WRITE,
)
async def edgeconnect_post_third_party_services_netskope_ipsla_setting(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/thirdPartyServices/netskope/ipslaSetting",
        query_params=None,
        body=body,
    )


@tool(
    name="edgeconnect_post_third_party_services_netskope_orchestrated_list",
    description="POST /thirdPartyServices/netskope/orchestratedList\n\ngetNetskopeOrchestratedList\n\nGet Netskope configuration entries for specified appliances",
    capability=Capability.WRITE,
)
async def edgeconnect_post_third_party_services_netskope_orchestrated_list(
    ctx: Context,
    body: Annotated[list[Any], Field(description="Request body (required)")],
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/thirdPartyServices/netskope/orchestratedList",
        query_params=None,
        body=body,
    )


@tool(
    name="edgeconnect_post_third_party_services_netskope_pause_orchestration",
    description="POST /thirdPartyServices/netskope/pauseOrchestration\n\nnetskopePauseOrchestrationPost869\n\nSet Netskope orchestration pause status",
    capability=Capability.WRITE,
)
async def edgeconnect_post_third_party_services_netskope_pause_orchestration(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/thirdPartyServices/netskope/pauseOrchestration",
        query_params=None,
        body=body,
    )


@tool(
    name="edgeconnect_post_third_party_services_netskope_pop_override",
    description="POST /thirdPartyServices/netskope/popOverride\n\nsavePopOverride872\n\nCreate or update Netskope service edge POP override",
    capability=Capability.WRITE,
)
async def edgeconnect_post_third_party_services_netskope_pop_override(
    ctx: Context,
    nePk: Annotated[
        str,
        Field(
            description="Network Element Primary Key - unique appliance identifier assigned by Orchestrator. Format: '<id>.NE' (e.g., '0.NE', '10.NE')."
        ),
    ],
    labelId: Annotated[
        str, Field(description="WAN interface label ID. Must be a valid WAN label configured in interface labels.")
    ],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    query_params: dict[str, Any] = {}
    if nePk is not None:
        query_params["nePk"] = nePk
    if labelId is not None:
        query_params["labelId"] = labelId
    return await edgeconnect_request(
        ctx,
        "POST",
        "/thirdPartyServices/netskope/popOverride",
        query_params=query_params or None,
        body=body,
    )


@tool(
    name="edgeconnect_post_third_party_services_netskope_subscription",
    description="POST /thirdPartyServices/netskope/subscription\n\nnetskopeSubscriptionPost876\n\nCreate or Update Netskope Subscription",
    capability=Capability.WRITE,
)
async def edgeconnect_post_third_party_services_netskope_subscription(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/thirdPartyServices/netskope/subscription",
        query_params=None,
        body=body,
    )


@tool(
    name="edgeconnect_post_third_party_services_service_orchestration_bio_breakout",
    description="POST /thirdPartyServices/serviceOrchestration/bioBreakout\n\nsetServiceProviderBioBreakout831\n\nSet BIO Breakout state for a service provider",
    capability=Capability.WRITE,
)
async def edgeconnect_post_third_party_services_service_orchestration_bio_breakout(
    ctx: Context,
    serviceId: Annotated[
        str,
        Field(
            description="Unique identifier of the service provider. Must be a valid numeric ID referencing an existing service provider in the serviceorchestrationproviders table."
        ),
    ],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    query_params: dict[str, Any] = {}
    if serviceId is not None:
        query_params["serviceId"] = serviceId
    return await edgeconnect_request(
        ctx,
        "POST",
        "/thirdPartyServices/serviceOrchestration/bioBreakout",
        query_params=query_params or None,
        body=body,
    )


@tool(
    name="edgeconnect_post_third_party_services_service_orchestration_interfaces",
    description="POST /thirdPartyServices/serviceOrchestration/interfaces\n\nsetServiceProviderInterfaces834\n\nSet primary and backup interface labels for a Service Provider.",
    capability=Capability.WRITE,
)
async def edgeconnect_post_third_party_services_service_orchestration_interfaces(
    ctx: Context,
    serviceId: Annotated[
        int,
        Field(
            description="Unique identifier of the service provider. Must be a valid existing service provider ID from the service orchestration configuration."
        ),
    ],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    query_params: dict[str, Any] = {}
    if serviceId is not None:
        query_params["serviceId"] = serviceId
    return await edgeconnect_request(
        ctx,
        "POST",
        "/thirdPartyServices/serviceOrchestration/interfaces",
        query_params=query_params or None,
        body=body,
    )


@tool(
    name="edgeconnect_post_third_party_services_service_orchestration_ipsla_rule_destination",
    description="POST /thirdPartyServices/serviceOrchestration/ipslaRuleDestination\n\nServiceOrchestrationIPSLARules855\n\nUpdate IPSLA Rule Destination for a Service Provider",
    capability=Capability.WRITE,
)
async def edgeconnect_post_third_party_services_service_orchestration_ipsla_rule_destination(
    ctx: Context,
    serviceId: Annotated[
        str,
        Field(
            description="Unique identifier of the third-party service provider to update. Must reference an existing service provider configuration."
        ),
    ],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    query_params: dict[str, Any] = {}
    if serviceId is not None:
        query_params["serviceId"] = serviceId
    return await edgeconnect_request(
        ctx,
        "POST",
        "/thirdPartyServices/serviceOrchestration/ipslaRuleDestination",
        query_params=query_params or None,
        body=body,
    )


@tool(
    name="edgeconnect_post_third_party_services_service_orchestration_ipsla_setting",
    description="POST /thirdPartyServices/serviceOrchestration/ipslaSetting\n\nServiceOrchestrationIPSLASetting855\n\nUpdate IP SLA settings for a service provider",
    capability=Capability.WRITE,
)
async def edgeconnect_post_third_party_services_service_orchestration_ipsla_setting(
    ctx: Context,
    serviceId: Annotated[
        str,
        Field(
            description="Unique identifier of the service provider to update. Must reference an existing service provider."
        ),
    ],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    query_params: dict[str, Any] = {}
    if serviceId is not None:
        query_params["serviceId"] = serviceId
    return await edgeconnect_request(
        ctx,
        "POST",
        "/thirdPartyServices/serviceOrchestration/ipslaSetting",
        query_params=query_params or None,
        body=body,
    )


@tool(
    name="edgeconnect_post_third_party_services_service_orchestration_pause_orchestration",
    description="POST /thirdPartyServices/serviceOrchestration/pauseOrchestration\n\nsetPauseOrchestrationState\n\nSet Service Orchestration pause state",
    capability=Capability.WRITE,
)
async def edgeconnect_post_third_party_services_service_orchestration_pause_orchestration(
    ctx: Context,
    serviceId: Annotated[
        int,
        Field(
            description="Unique identifier of the third-party service provider. Obtained from the /serviceProviders endpoint."
        ),
    ],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    query_params: dict[str, Any] = {}
    if serviceId is not None:
        query_params["serviceId"] = serviceId
    return await edgeconnect_request(
        ctx,
        "POST",
        "/thirdPartyServices/serviceOrchestration/pauseOrchestration",
        query_params=query_params or None,
        body=body,
    )


@tool(
    name="edgeconnect_post_third_party_services_service_orchestration_remote_end_point_associations",
    description="POST /thirdPartyServices/serviceOrchestration/remoteEndPointAssociations\n\nsetRemoteEndpointAssociation838\n\nSave appliance-to-remote-endpoint associations for third-party tunnel orchestration",
    capability=Capability.WRITE,
)
async def edgeconnect_post_third_party_services_service_orchestration_remote_end_point_associations(
    ctx: Context,
    serviceId: Annotated[
        str,
        Field(
            description="Unique numeric identifier of the service provider. Must reference an existing service provider created via POST /thirdPartyServices/serviceOrchestration/serviceProviders."
        ),
    ],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    query_params: dict[str, Any] = {}
    if serviceId is not None:
        query_params["serviceId"] = serviceId
    return await edgeconnect_request(
        ctx,
        "POST",
        "/thirdPartyServices/serviceOrchestration/remoteEndPointAssociations",
        query_params=query_params or None,
        body=body,
    )


@tool(
    name="edgeconnect_post_third_party_services_service_orchestration_remote_endpoints",
    description="POST /thirdPartyServices/serviceOrchestration/remoteEndpoints\n\nupdateRemoteEndpointEntry842\n\nAdd, update, or remove remote endpoints for a service provider",
    capability=Capability.WRITE,
)
async def edgeconnect_post_third_party_services_service_orchestration_remote_endpoints(
    ctx: Context,
    serviceId: Annotated[
        str,
        Field(
            description="Unique identifier of the service provider. Must reference an existing service provider configuration."
        ),
    ],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    query_params: dict[str, Any] = {}
    if serviceId is not None:
        query_params["serviceId"] = serviceId
    return await edgeconnect_request(
        ctx,
        "POST",
        "/thirdPartyServices/serviceOrchestration/remoteEndpoints",
        query_params=query_params or None,
        body=body,
    )


@tool(
    name="edgeconnect_post_third_party_services_service_orchestration_remote_endpoints_add_endpoints",
    description="POST /thirdPartyServices/serviceOrchestration/remoteEndpoints/addEndpoints\n\naddRemoteEndpointEntry839\n\nAdd new remote endpoints to a service provider",
    capability=Capability.WRITE,
)
async def edgeconnect_post_third_party_services_service_orchestration_remote_endpoints_add_endpoints(
    ctx: Context,
    serviceId: Annotated[
        int,
        Field(
            description="Unique identifier of the service provider to add endpoints to. Must reference an existing service provider."
        ),
    ],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    query_params: dict[str, Any] = {}
    if serviceId is not None:
        query_params["serviceId"] = serviceId
    return await edgeconnect_request(
        ctx,
        "POST",
        "/thirdPartyServices/serviceOrchestration/remoteEndpoints/addEndpoints",
        query_params=query_params or None,
        body=body,
    )


@tool(
    name="edgeconnect_post_third_party_services_service_orchestration_service_providers",
    description="POST /thirdPartyServices/serviceOrchestration/serviceProviders\n\naddServiceProvider846\n\nCreate or update a third-party service provider",
    capability=Capability.WRITE,
)
async def edgeconnect_post_third_party_services_service_orchestration_service_providers(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
    serviceId: Annotated[
        str | None,
        Field(
            default=None,
            description="Numeric ID of service provider for update operations. Omit this parameter to create a new provider.",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if serviceId is not None:
        query_params["serviceId"] = serviceId
    return await edgeconnect_request(
        ctx,
        "POST",
        "/thirdPartyServices/serviceOrchestration/serviceProviders",
        query_params=query_params or None,
        body=body,
    )


@tool(
    name="edgeconnect_post_third_party_services_service_orchestration_tunnel_setting",
    description="POST /thirdPartyServices/serviceOrchestration/tunnelSetting\n\nsetServiceOrchTunnelSettings848\n\nUpdate tunnel settings for a Service Provider",
    capability=Capability.WRITE,
)
async def edgeconnect_post_third_party_services_service_orchestration_tunnel_setting(
    ctx: Context,
    serviceId: Annotated[
        int,
        Field(
            description="Unique identifier of the Service Provider. Must be a valid integer corresponding to an existing service provider entry."
        ),
    ],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    query_params: dict[str, Any] = {}
    if serviceId is not None:
        query_params["serviceId"] = serviceId
    return await edgeconnect_request(
        ctx,
        "POST",
        "/thirdPartyServices/serviceOrchestration/tunnelSetting",
        query_params=query_params or None,
        body=body,
    )


@tool(
    name="edgeconnect_post_third_party_services_zscaler_appliance_association",
    description="POST /thirdPartyServices/zscaler/applianceAssociation\n\nzscalerAssociationPost850\n\nSave Zscaler appliance associations",
    capability=Capability.WRITE,
)
async def edgeconnect_post_third_party_services_zscaler_appliance_association(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/thirdPartyServices/zscaler/applianceAssociation",
        query_params=None,
        body=body,
    )


@tool(
    name="edgeconnect_post_third_party_services_zscaler_configuration",
    description="POST /thirdPartyServices/zscaler/configuration\n\nzscalerConfigurationPost852\n\nUpdate Zscaler Configuration",
    capability=Capability.WRITE,
)
async def edgeconnect_post_third_party_services_zscaler_configuration(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/thirdPartyServices/zscaler/configuration",
        query_params=None,
        body=body,
    )


@tool(
    name="edgeconnect_post_third_party_services_zscaler_countries",
    description="POST /thirdPartyServices/zscaler/countries\n\nsaveZscalerCountries\n\nSave custom ISO Alpha-2 to Zscaler country code mappings",
    capability=Capability.WRITE,
)
async def edgeconnect_post_third_party_services_zscaler_countries(
    ctx: Context,
    body: Annotated[str, Field(description="Request body (required)")],
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/thirdPartyServices/zscaler/countries",
        query_params=None,
        body=body,
        body_mode="text",
    )


@tool(
    name="edgeconnect_post_third_party_services_zscaler_interface_tunnel_setting",
    description="POST /thirdPartyServices/zscaler/interfaceTunnelSetting\n\nsaveZscalerInterfaceTunnelSetting\n\nSave Zscaler IPSec/GRE tunnel settings per WAN interface label",
    capability=Capability.WRITE,
)
async def edgeconnect_post_third_party_services_zscaler_interface_tunnel_setting(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/thirdPartyServices/zscaler/interfaceTunnelSetting",
        query_params=None,
        body=body,
    )


@tool(
    name="edgeconnect_post_third_party_services_zscaler_ipsla_rule_destination",
    description="POST /thirdPartyServices/zscaler/ipslaRuleDestination\n\nzscalerIpslaRuleDestinationPost\n\nSave Zscaler IP SLA rule destination configuration",
    capability=Capability.WRITE,
)
async def edgeconnect_post_third_party_services_zscaler_ipsla_rule_destination(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/thirdPartyServices/zscaler/ipslaRuleDestination",
        query_params=None,
        body=body,
    )


@tool(
    name="edgeconnect_post_third_party_services_zscaler_ipsla_setting",
    description="POST /thirdPartyServices/zscaler/ipslaSetting\n\nsetZscalerIpslaSetting\n\nUpdate Zscaler IP SLA orchestration settings",
    capability=Capability.WRITE,
)
async def edgeconnect_post_third_party_services_zscaler_ipsla_setting(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/thirdPartyServices/zscaler/ipslaSetting",
        query_params=None,
        body=body,
    )


@tool(
    name="edgeconnect_post_third_party_services_zscaler_location_config",
    description="POST /thirdPartyServices/zscaler/locationConfig\n\nzscalerLocationConfigPost864\n\nSave Zscaler location and sub-location configurations",
    capability=Capability.WRITE,
)
async def edgeconnect_post_third_party_services_zscaler_location_config(
    ctx: Context,
    body: Annotated[list[Any], Field(description="Request body (required)")],
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/thirdPartyServices/zscaler/locationConfig",
        query_params=None,
        body=body,
    )


@tool(
    name="edgeconnect_post_third_party_services_zscaler_orchestrate_gateway_options",
    description="POST /thirdPartyServices/zscaler/orchestrateGatewayOptions\n\nzscalerOrchestrateGatewayOptionsPost866\n\nUpdate Zscaler gateway options orchestration setting",
    capability=Capability.WRITE,
)
async def edgeconnect_post_third_party_services_zscaler_orchestrate_gateway_options(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/thirdPartyServices/zscaler/orchestrateGatewayOptions",
        query_params=None,
        body=body,
    )


@tool(
    name="edgeconnect_post_third_party_services_zscaler_orchestrated_list",
    description="POST /thirdPartyServices/zscaler/orchestratedList\n\ngetZscalerOrchestratedList\n\nGet Zscaler orchestrated configuration for appliances",
    capability=Capability.WRITE,
)
async def edgeconnect_post_third_party_services_zscaler_orchestrated_list(
    ctx: Context,
    body: Annotated[list[Any], Field(description="Request body (required)")],
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/thirdPartyServices/zscaler/orchestratedList",
        query_params=None,
        body=body,
    )


@tool(
    name="edgeconnect_post_third_party_services_zscaler_pause_orchestration",
    description="POST /thirdPartyServices/zscaler/pauseOrchestration\n\nzscalerPauseOrchestrationPost869\n\nSet Zscaler orchestration pause status",
    capability=Capability.WRITE,
)
async def edgeconnect_post_third_party_services_zscaler_pause_orchestration(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/thirdPartyServices/zscaler/pauseOrchestration",
        query_params=None,
        body=body,
    )


@tool(
    name="edgeconnect_post_third_party_services_zscaler_remote_endpoint_exception",
    description="POST /thirdPartyServices/zscaler/remoteEndpointException\n\nzscalerRemoteEndpointExceptionPost873\n\nCreate or update Zscaler ZEN override configuration",
    capability=Capability.WRITE,
)
async def edgeconnect_post_third_party_services_zscaler_remote_endpoint_exception(
    ctx: Context,
    nePk: Annotated[
        str,
        Field(
            description="Network Element Primary Key - unique appliance identifier assigned by Orchestrator. Format: '<id>.NE' (e.g., '0.NE', '10.NE')."
        ),
    ],
    labelId: Annotated[
        str,
        Field(
            description="Numeric identifier for the WAN interface label. Must be a valid WAN interface label configured in the system."
        ),
    ],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    query_params: dict[str, Any] = {}
    if nePk is not None:
        query_params["nePk"] = nePk
    if labelId is not None:
        query_params["labelId"] = labelId
    return await edgeconnect_request(
        ctx,
        "POST",
        "/thirdPartyServices/zscaler/remoteEndpointException",
        query_params=query_params or None,
        body=body,
    )


@tool(
    name="edgeconnect_post_third_party_services_zscaler_subscription",
    description="POST /thirdPartyServices/zscaler/subscription\n\nzscalerSubscriptionPost876\n\nCreate or Update Zscaler Subscription",
    capability=Capability.WRITE,
)
async def edgeconnect_post_third_party_services_zscaler_subscription(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/thirdPartyServices/zscaler/subscription",
        query_params=None,
        body=body,
    )


@tool(
    name="edgeconnect_post_third_party_services_zscaler_timezones",
    description="POST /thirdPartyServices/zscaler/timezones\n\nsaveZscalerTimezones\n\nSave Zscaler timezone mappings",
    capability=Capability.WRITE,
)
async def edgeconnect_post_third_party_services_zscaler_timezones(
    ctx: Context,
    body: Annotated[str, Field(description="Request body (required)")],
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/thirdPartyServices/zscaler/timezones",
        query_params=None,
        body=body,
        body_mode="text",
    )


@tool(
    name="edgeconnect_put_third_party_services_clearpass_accounts",
    description="PUT /thirdPartyServices/clearpass/accounts\n\nupdateClearPassAccount819\n\nUpdate ClearPass Policy Manager account configuration",
    capability=Capability.WRITE,
)
async def edgeconnect_put_third_party_services_clearpass_accounts(
    ctx: Context,
    id: Annotated[
        int,
        Field(description="Unique identifier of the ClearPass account to update. Must reference an existing account."),
    ],
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    query_params: dict[str, Any] = {}
    if id is not None:
        query_params["id"] = id
    return await edgeconnect_request(
        ctx,
        "PUT",
        "/thirdPartyServices/clearpass/accounts",
        query_params=query_params or None,
        body=body,
    )


@tool(
    name="edgeconnect_put_third_party_services_clearpass_accounts_pause",
    description="PUT /thirdPartyServices/clearpass/accounts/pause\n\nupdateServicePauseStatus816\n\nPause or resume ClearPass Policy Manager account orchestration",
    capability=Capability.WRITE,
)
async def edgeconnect_put_third_party_services_clearpass_accounts_pause(
    ctx: Context,
    id: Annotated[
        int,
        Field(
            description="Unique identifier of the ClearPass Policy Manager account configuration. Must reference an existing configuration in the system."
        ),
    ],
    isPaused: Annotated[
        bool,
        Field(
            description="Set to true to pause orchestration (stop processing events) or false to resume orchestration for the specified account."
        ),
    ],
) -> Any:
    query_params: dict[str, Any] = {}
    if id is not None:
        query_params["id"] = id
    if isPaused is not None:
        query_params["isPaused"] = isPaused
    return await edgeconnect_request(
        ctx,
        "PUT",
        "/thirdPartyServices/clearpass/accounts/pause",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_put_third_party_services_clearpass_service_reset",
    description="PUT /thirdPartyServices/clearpass/service/reset\n\nresetServiceEndpoint828\n\nReset ClearPass Policy Manager service endpoint",
    capability=Capability.WRITE,
)
async def edgeconnect_put_third_party_services_clearpass_service_reset(
    ctx: Context,
    id: Annotated[
        int,
        Field(
            description="The unique identifier of the ClearPass Policy Manager account configuration. Must reference an existing CPPM account."
        ),
    ],
    service: Annotated[
        str,
        Field(
            description="The service endpoint type to reset. Determines which CPPM integration component will be recreated."
        ),
    ],
) -> Any:
    query_params: dict[str, Any] = {}
    if id is not None:
        query_params["id"] = id
    if service is not None:
        query_params["service"] = service
    return await edgeconnect_request(
        ctx,
        "PUT",
        "/thirdPartyServices/clearpass/service/reset",
        query_params=query_params or None,
    )
