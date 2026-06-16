"""Generated EdgeConnect tools — DO NOT EDIT BY HAND.

Emitted by ``scripts/generate_edgeconnect_tools.py`` from
``vendor/edgeconnect/EdgeConnect-9-7-REST-API.json``. Regenerate via:

    uv run python scripts/generate_edgeconnect_tools.py

Tag: ``spPortal``
Operations in this file: 53
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
    name="edgeconnect_delete_sp_portal_account_old_key",
    description="DELETE /spPortal/account/oldKey\n\nspPortalDeleteOldKeySecondary951\n\nDelete old account key from Portal",
    capability=Capability.WRITE_DELETE,
)
async def edgeconnect_delete_sp_portal_account_old_key(
    ctx: Context,
    secondaryAccountName: Annotated[
        str | None,
        Field(
            default=None,
            description="Name of the secondary account to delete old key for. When omitted or empty, operates on the primary account.",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if secondaryAccountName is not None:
        query_params["secondaryAccountName"] = secondaryAccountName
    return await edgeconnect_request(
        ctx,
        "DELETE",
        "/spPortal/account/oldKey",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_sp_portal_account_key_change_count",
    description="GET /spPortal/account/key/changeCount\n\nspPortalAccountKeyChangeCount948\n\nGet account key rotation count",
    capability=Capability.READ,
)
async def edgeconnect_get_sp_portal_account_key_change_count(
    ctx: Context,
    secondaryAccountName: Annotated[
        str | None,
        Field(
            default=None,
            description="Name of the secondary account to query. Leave empty or omit to query the primary account.",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if secondaryAccountName is not None:
        query_params["secondaryAccountName"] = secondaryAccountName
    return await edgeconnect_request(
        ctx,
        "GET",
        "/spPortal/account/key/changeCount",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_sp_portal_account_key_change_status",
    description="GET /spPortal/account/key/changeStatus\n\ngetAccountKeyChangeStatus\n\nGet account key change status",
    capability=Capability.READ,
)
async def edgeconnect_get_sp_portal_account_key_change_status(
    ctx: Context,
    secondaryAccountName: Annotated[
        str | None,
        Field(
            default=None,
            description="Name of the secondary account to retrieve key change status for. Leave empty or omit to get primary account status.",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if secondaryAccountName is not None:
        query_params["secondaryAccountName"] = secondaryAccountName
    return await edgeconnect_request(
        ctx,
        "GET",
        "/spPortal/account/key/changeStatus",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_sp_portal_account_license_appliance_ecsp_status",
    description="GET /spPortal/account/license/appliance/ecsp/status\n\nspPortalECSPLicensesGet564\n\nGet EC-SP license status from Portal",
    capability=Capability.READ,
)
async def edgeconnect_get_sp_portal_account_license_appliance_ecsp_status(
    ctx: Context,
    cached: Annotated[
        bool | None,
        Field(
            default=None,
            description="When true, returns cached license data from OrchestrationStore if available. When false or omitted, fetches fresh data directly from Cloud Portal.",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if cached is not None:
        query_params["cached"] = cached
    return await edgeconnect_request(
        ctx,
        "GET",
        "/spPortal/account/license/appliance/ecsp/status",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_sp_portal_account_license_feature",
    description="GET /spPortal/account/license/feature\n\nspPortalAccountLicenseFeatureGet566\n\nGet account license features from Portal",
    capability=Capability.READ,
)
async def edgeconnect_get_sp_portal_account_license_feature(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/spPortal/account/license/feature",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_sp_portal_account_license_type",
    description="GET /spPortal/account/license/type\n\nspPortalAccountLicenseTypeGet567\n\nGet account license type from Portal",
    capability=Capability.READ,
)
async def edgeconnect_get_sp_portal_account_license_type(
    ctx: Context,
    cached: Annotated[
        bool | None,
        Field(
            default=None,
            description="When true, returns cached license type data from OrchestrationStore if available. When false or omitted, fetches fresh data from Portal.",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if cached is not None:
        query_params["cached"] = cached
    return await edgeconnect_request(
        ctx,
        "GET",
        "/spPortal/account/license/type",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_sp_portal_app_express_app_config",
    description="GET /spPortal/appExpressAppConfig\n\ngetAppExpressAppConfigTemplate\n\nGet default AppExpress application configurations from Cloud Portal",
    capability=Capability.READ,
)
async def edgeconnect_get_sp_portal_app_express_app_config(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/spPortal/appExpressAppConfig",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_sp_portal_appliance_wsstatus",
    description="GET /spPortal/applianceWSStatus\n\ncheckApplianceReachabilityUsingWSGet569\n\nCheck appliance WebSocket reachability",
    capability=Capability.READ,
)
async def edgeconnect_get_sp_portal_appliance_wsstatus(
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
        "/spPortal/applianceWSStatus",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_sp_portal_application_tags",
    description="GET /spPortal/applicationTags\n\ngetApplicationTags\n\nGet application groups from portal",
    capability=Capability.READ,
)
async def edgeconnect_get_sp_portal_application_tags(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/spPortal/applicationTags",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_sp_portal_application_tags_info",
    description="GET /spPortal/applicationTags/info\n\ngetApplicationTagsInfo\n\nGet application tags version hash",
    capability=Capability.READ,
)
async def edgeconnect_get_sp_portal_application_tags_info(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/spPortal/applicationTags/info",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_sp_portal_broadcast_message",
    description="GET /spPortal/broadcastMessage\n\nbroadcastMessageGet572\n\nGet Broadcast Messages from Portal",
    capability=Capability.READ,
)
async def edgeconnect_get_sp_portal_broadcast_message(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/spPortal/broadcastMessage",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_sp_portal_compound_classification",
    description="GET /spPortal/compoundClassification\n\ngetCompoundClassification\n\nGet compound application classification definitions from portal",
    capability=Capability.READ,
)
async def edgeconnect_get_sp_portal_compound_classification(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/spPortal/compoundClassification",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_sp_portal_compound_classification_info",
    description="GET /spPortal/compoundClassification/info\n\ngetCompoundClassificationInfo\n\nGet compound classification version hash",
    capability=Capability.READ,
)
async def edgeconnect_get_sp_portal_compound_classification_info(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/spPortal/compoundClassification/info",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_sp_portal_config",
    description="GET /spPortal/config\n\nspPortalConfigGet575\n\nRetrieve Cloud Portal registration configuration",
    capability=Capability.READ,
)
async def edgeconnect_get_sp_portal_config(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/spPortal/config",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_sp_portal_connectivity",
    description="GET /spPortal/connectivity\n\nconnectivityGet577\n\nGet Orchestrator to Silver Peak Cloud Portal connectivity status",
    capability=Capability.READ,
)
async def edgeconnect_get_sp_portal_connectivity(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/spPortal/connectivity",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_sp_portal_connectivity_appliance",
    description="GET /spPortal/connectivity/appliance\n\nportalConnectivityAppliances\n\nCheck appliance connectivity to Cloud Portal",
    capability=Capability.READ,
)
async def edgeconnect_get_sp_portal_connectivity_appliance(
    ctx: Context,
    portalUrl: Annotated[
        str,
        Field(
            description="The Cloud Portal hostname or URL that appliances will attempt to connect to. Must not be empty."
        ),
    ],
) -> Any:
    query_params: dict[str, Any] = {}
    if portalUrl is not None:
        query_params["portalUrl"] = portalUrl
    return await edgeconnect_request(
        ctx,
        "GET",
        "/spPortal/connectivity/appliance",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_sp_portal_connectivity_orchestrator",
    description="GET /spPortal/connectivity/orchestrator\n\nportalConnectivityOrchestrator\n\nTest Orchestrator to Cloud Portal connectivity",
    capability=Capability.READ,
)
async def edgeconnect_get_sp_portal_connectivity_orchestrator(
    ctx: Context,
    portalUrl: Annotated[
        str,
        Field(
            description="The Portal hostname/URL to test connectivity against. The Orchestrator will combine this with its stored port configuration to construct the full Portal URL."
        ),
    ],
) -> Any:
    query_params: dict[str, Any] = {}
    if portalUrl is not None:
        query_params["portalUrl"] = portalUrl
    return await edgeconnect_request(
        ctx,
        "GET",
        "/spPortal/connectivity/orchestrator",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_sp_portal_dns_classification",
    description="GET /spPortal/dnsClassification\n\ngetDnsClassification\n\nGet DNS-based application classification definitions",
    capability=Capability.READ,
)
async def edgeconnect_get_sp_portal_dns_classification(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/spPortal/dnsClassification",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_sp_portal_dns_classification_info",
    description="GET /spPortal/dnsClassification/info\n\ngetDnsClassificationInfo\n\nGet DNS classification version hash",
    capability=Capability.READ,
)
async def edgeconnect_get_sp_portal_dns_classification_info(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/spPortal/dnsClassification/info",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_sp_portal_internet_db_geo_locate_ip",
    description="GET /spPortal/internetDb/geoLocateIp\n\ngeoLocationGet582\n\nGet geolocation for single IP address",
    capability=Capability.READ,
)
async def edgeconnect_get_sp_portal_internet_db_geo_locate_ip(
    ctx: Context,
    ip: Annotated[
        str,
        Field(
            description="IP address to geolocate, provided as a 32-bit unsigned integer (0 to 4294967295). Convert standard IPv4 notation to integer format."
        ),
    ],
) -> Any:
    query_params: dict[str, Any] = {}
    if ip is not None:
        query_params["ip"] = ip
    return await edgeconnect_request(
        ctx,
        "GET",
        "/spPortal/internetDb/geoLocateIp",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_sp_portal_internet_db_ip_intelligence",
    description="GET /spPortal/internetDb/ipIntelligence\n\nipIntelligenceTmpGet583\n\nGet IP Intelligence Data for Address Map",
    capability=Capability.READ,
)
async def edgeconnect_get_sp_portal_internet_db_ip_intelligence(
    ctx: Context,
    start: Annotated[
        int,
        Field(description="The starting offset for pagination. Values less than 0 are automatically adjusted to 0."),
    ],
    limit: Annotated[
        int, Field(description="Maximum number of records to return. Values <= 0 or > 10000 default to 10000.")
    ],
) -> Any:
    query_params: dict[str, Any] = {}
    if start is not None:
        query_params["start"] = start
    if limit is not None:
        query_params["limit"] = limit
    return await edgeconnect_request(
        ctx,
        "GET",
        "/spPortal/internetDb/ipIntelligence",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_sp_portal_internet_db_ip_intelligence_info",
    description="GET /spPortal/internetDb/ipIntelligence/info\n\ngetIpIntelligenceUpdateTime\n\nGet IP Intelligence data last update timestamp",
    capability=Capability.READ,
)
async def edgeconnect_get_sp_portal_internet_db_ip_intelligence_info(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/spPortal/internetDb/ipIntelligence/info",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_sp_portal_internet_db_ip_intelligence_search",
    description="GET /spPortal/internetDb/ipIntelligence/search\n\nsearchIpIntelligenceTmp\n\nSearch IP intelligence data for Address Map",
    capability=Capability.READ,
)
async def edgeconnect_get_sp_portal_internet_db_ip_intelligence_search(
    ctx: Context,
    ip: Annotated[
        int | None,
        Field(
            default=None,
            description="IPv4 address as a 32-bit unsigned integer (0 to 4294967295). Ignored if filter parameter is provided. Searches for IP intelligence entries where the IP falls within the ip_start and ip_end range.",
        ),
    ] = None,
    filter: Annotated[
        str | None,
        Field(
            default=None,
            description="Text search string (case-insensitive) to match against app name, description, country, organization, and subattributes. Takes priority over ip parameter when both are provided. Special characters '_' and '%' are escaped automatically.",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if ip is not None:
        query_params["ip"] = ip
    if filter is not None:
        query_params["filter"] = filter
    return await edgeconnect_request(
        ctx,
        "GET",
        "/spPortal/internetDb/ipIntelligence/search",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_sp_portal_internet_db_ip_intelligence_total",
    description="GET /spPortal/internetDb/ipIntelligence/total\n\nipIntelligenceTmpTotal586\n\nGet IP intelligence record count",
    capability=Capability.READ,
)
async def edgeconnect_get_sp_portal_internet_db_ip_intelligence_total(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/spPortal/internetDb/ipIntelligence/total",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_sp_portal_internet_db_service_id_to_saas_id",
    description="GET /spPortal/internetDb/serviceIdToSaasId\n\nserviceIdToSaasIdGet587\n\nGet service ID to SaaS application details mapping",
    capability=Capability.READ,
)
async def edgeconnect_get_sp_portal_internet_db_service_id_to_saas_id(
    ctx: Context,
    matchAny: Annotated[
        str | None,
        Field(
            default=None,
            description="Case-insensitive wildcard match on country, org, and saasAppName fields. Takes priority over 'org' parameter when both are provided.",
        ),
    ] = None,
    org: Annotated[
        str | None,
        Field(
            default=None,
            description="Case-insensitive wildcard match on organization name only. Ignored if 'matchAny' is provided.",
        ),
    ] = None,
    serviceIds: Annotated[
        str | None,
        Field(
            default=None,
            description="Comma-separated list of service IDs to retrieve. When provided, returns exact matches for the specified IDs only, ignoring other filter parameters.",
        ),
    ] = None,
    top: Annotated[
        int | None,
        Field(
            default=None,
            description="Maximum number of results to return. Default is 100 if not specified. Ignored when 'serviceIds' parameter is provided.",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if matchAny is not None:
        query_params["matchAny"] = matchAny
    if org is not None:
        query_params["org"] = org
    if serviceIds is not None:
        query_params["serviceIds"] = serviceIds
    if top is not None:
        query_params["top"] = top
    return await edgeconnect_request(
        ctx,
        "GET",
        "/spPortal/internetDb/serviceIdToSaasId",
        query_params=query_params or None,
    )


@tool(
    name="edgeconnect_get_sp_portal_internet_db_service_id_to_saas_id_count",
    description="GET /spPortal/internetDb/serviceIdToSaasId/count\n\nserviceIdToSaasIdCountGet588\n\nGet Internet Service Mapping Count",
    capability=Capability.READ,
)
async def edgeconnect_get_sp_portal_internet_db_service_id_to_saas_id_count(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/spPortal/internetDb/serviceIdToSaasId/count",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_sp_portal_internet_db_service_id_to_saas_id_countries",
    description="GET /spPortal/internetDb/serviceIdToSaasId/countries\n\nserviceIdToSaasIdCountriesGet589\n\nGet unique countries from the internet services database",
    capability=Capability.READ,
)
async def edgeconnect_get_sp_portal_internet_db_service_id_to_saas_id_countries(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/spPortal/internetDb/serviceIdToSaasId/countries",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_sp_portal_internet_db_service_id_to_saas_id_saas_apps",
    description="GET /spPortal/internetDb/serviceIdToSaasId/saasApps\n\nserviceIdToSaasIdSaasAppGet590\n\nGet unique SaaS application names",
    capability=Capability.READ,
)
async def edgeconnect_get_sp_portal_internet_db_service_id_to_saas_id_saas_apps(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/spPortal/internetDb/serviceIdToSaasId/saasApps",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_sp_portal_ip_protocol_numbers",
    description="GET /spPortal/ipProtocolNumbers\n\nipProtocolNumbersGet591\n\nGet IP Protocol Numbers mapping data",
    capability=Capability.READ,
)
async def edgeconnect_get_sp_portal_ip_protocol_numbers(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/spPortal/ipProtocolNumbers",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_sp_portal_meter_flow_classification",
    description="GET /spPortal/meterFlowClassification\n\ngetMeterFlowClassification\n\nGet Meter Flow Classification definitions for DPI application identification",
    capability=Capability.READ,
)
async def edgeconnect_get_sp_portal_meter_flow_classification(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/spPortal/meterFlowClassification",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_sp_portal_meter_flow_classification_info",
    description="GET /spPortal/meterFlowClassification/info\n\ngetMeterFlowClassificationInfo\n\nGet meter flow classification version hash",
    capability=Capability.READ,
)
async def edgeconnect_get_sp_portal_meter_flow_classification_info(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/spPortal/meterFlowClassification/info",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_sp_portal_port_protocol_classification",
    description="GET /spPortal/portProtocolClassification\n\ngetPortProtocolClassificationTemplate\n\nGet port and protocol to application classification mappings",
    capability=Capability.READ,
)
async def edgeconnect_get_sp_portal_port_protocol_classification(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/spPortal/portProtocolClassification",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_sp_portal_port_protocol_classification_info",
    description="GET /spPortal/portProtocolClassification/info\n\ngetPortProtocolClassificationInfo\n\nGet port protocol classification version hash",
    capability=Capability.READ,
)
async def edgeconnect_get_sp_portal_port_protocol_classification_info(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/spPortal/portProtocolClassification/info",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_sp_portal_registration",
    description="GET /spPortal/registration\n\ngmsPortalRegistrationGet596\n\nGet Orchestrator-Portal registration status",
    capability=Capability.READ,
)
async def edgeconnect_get_sp_portal_registration(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/spPortal/registration",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_sp_portal_registration_account",
    description="GET /spPortal/registration/account\n\ngmsPortalRegistrationSecondaryAccountGet597\n\nGet secondary account Portal registration status",
    capability=Capability.READ,
)
async def edgeconnect_get_sp_portal_registration_account(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/spPortal/registration/account",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_sp_portal_saas_classification",
    description="GET /spPortal/saasClassification\n\ngetSaasClassificationTemplate\n\nGet SaaS application classification definitions from portal",
    capability=Capability.READ,
)
async def edgeconnect_get_sp_portal_saas_classification(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/spPortal/saasClassification",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_sp_portal_saas_classification_info",
    description="GET /spPortal/saasClassification/info\n\ngetSaasClassificationTemplateInfo\n\nGet SaaS classification data version hash",
    capability=Capability.READ,
)
async def edgeconnect_get_sp_portal_saas_classification_info(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/spPortal/saasClassification/info",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_sp_portal_status",
    description="GET /spPortal/status\n\nspPortalStatusGet600\n\nGet Portal Services Status",
    capability=Capability.READ,
)
async def edgeconnect_get_sp_portal_status(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/spPortal/status",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_sp_portal_tcp_udp_ports",
    description="GET /spPortal/tcpUdpPorts\n\ngetTcpUdpPorts\n\nRetrieve TCP/UDP port to application mappings",
    capability=Capability.READ,
)
async def edgeconnect_get_sp_portal_tcp_udp_ports(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/spPortal/tcpUdpPorts",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_sp_portal_top_sites",
    description="GET /spPortal/topSites\n\ntopSitesGet602\n\nGet top internet sites list",
    capability=Capability.READ,
)
async def edgeconnect_get_sp_portal_top_sites(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/spPortal/topSites",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_sp_portal_traffic_behavior",
    description="GET /spPortal/trafficBehavior\n\ngetTrafficBehavior\n\nGet traffic behavior categories and configuration",
    capability=Capability.READ,
)
async def edgeconnect_get_sp_portal_traffic_behavior(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/spPortal/trafficBehavior",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_sp_portal_traffic_behavior_info",
    description="GET /spPortal/trafficBehavior/info\n\ngetTrafficBehaviorInfo\n\nGet traffic behavior category version hash from Cloud Portal",
    capability=Capability.READ,
)
async def edgeconnect_get_sp_portal_traffic_behavior_info(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/spPortal/trafficBehavior/info",
        query_params=None,
    )


@tool(
    name="edgeconnect_get_sp_portal_ztp",
    description="GET /spPortal/ztp\n\ngetZtp605\n\nGet Zero Touch Provisioning configuration",
    capability=Capability.READ,
)
async def edgeconnect_get_sp_portal_ztp(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "GET",
        "/spPortal/ztp",
        query_params=None,
    )


@tool(
    name="edgeconnect_post_sp_portal_account_license_appliance_ecsp_assign",
    description="POST /spPortal/account/license/appliance/ecsp/assign\n\nspPortalECSPLicenseAssign563\n\nAssign EC-SP licenses to appliances on Portal",
    capability=Capability.WRITE,
)
async def edgeconnect_post_sp_portal_account_license_appliance_ecsp_assign(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/spPortal/account/license/appliance/ecsp/assign",
        query_params=None,
        body=body,
    )


@tool(
    name="edgeconnect_post_sp_portal_account_license_appliance_ecsp_unassign",
    description="POST /spPortal/account/license/appliance/ecsp/unassign\n\nspPortalECSPLicenseUnassign565\n\nUnassign EC-SP licenses on Portal",
    capability=Capability.WRITE,
)
async def edgeconnect_post_sp_portal_account_license_appliance_ecsp_unassign(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/spPortal/account/license/appliance/ecsp/unassign",
        query_params=None,
        body=body,
    )


@tool(
    name="edgeconnect_post_sp_portal_account_secondary",
    description="POST /spPortal/account/secondary\n\nspPortalAccountSecondaryPost579\n\nUpdate secondary accounts configuration for Cloud Portal registration",
    capability=Capability.WRITE,
)
async def edgeconnect_post_sp_portal_account_secondary(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/spPortal/account/secondary",
        query_params=None,
        body=body,
    )


@tool(
    name="edgeconnect_post_sp_portal_config",
    description="POST /spPortal/config\n\nspPortalConfigPost576\n\nUpdate Cloud Portal registration configuration",
    capability=Capability.WRITE,
)
async def edgeconnect_post_sp_portal_config(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/spPortal/config",
        query_params=None,
        body=body,
    )


@tool(
    name="edgeconnect_post_sp_portal_create_case_with_portal",
    description="POST /spPortal/createCaseWithPortal\n\nspPortalCreateCasePost578\n\nCreate a technical support case",
    capability=Capability.WRITE,
)
async def edgeconnect_post_sp_portal_create_case_with_portal(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/spPortal/createCaseWithPortal",
        query_params=None,
        body=body,
    )


@tool(
    name="edgeconnect_post_sp_portal_internet_db_geo_locate_ip",
    description="POST /spPortal/internetDb/geoLocateIp\n\ngeoLocationPost581\n\nBatch geolocation lookup for multiple IP addresses",
    capability=Capability.WRITE,
)
async def edgeconnect_post_sp_portal_internet_db_geo_locate_ip(
    ctx: Context,
    body: Annotated[list[Any], Field(description="Request body (required)")],
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/spPortal/internetDb/geoLocateIp",
        query_params=None,
        body=body,
    )


@tool(
    name="edgeconnect_post_sp_portal_registration",
    description="POST /spPortal/registration\n\ngmsPortalRegistrationPost597\n\nInitiate Orchestrator-Portal Registration",
    capability=Capability.WRITE,
)
async def edgeconnect_post_sp_portal_registration(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/spPortal/registration",
        query_params=None,
    )


@tool(
    name="edgeconnect_post_sp_portal_registration_account",
    description="POST /spPortal/registration/account\n\ngmsPortalRegistrationPost598\n\nInitiate secondary account Portal registration",
    capability=Capability.WRITE,
)
async def edgeconnect_post_sp_portal_registration_account(
    ctx: Context,
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/spPortal/registration/account",
        query_params=None,
    )


@tool(
    name="edgeconnect_post_sp_portal_ztp",
    description="POST /spPortal/ztp\n\nsetZTP606\n\nUpdate Zero Touch Provisioning configuration",
    capability=Capability.WRITE,
)
async def edgeconnect_post_sp_portal_ztp(
    ctx: Context,
    body: Annotated[dict[str, Any], Field(description="Request body (required)")],
) -> Any:
    return await edgeconnect_request(
        ctx,
        "POST",
        "/spPortal/ztp",
        query_params=None,
        body=body,
    )


@tool(
    name="edgeconnect_put_sp_portal_account_key_generate",
    description="PUT /spPortal/account/key/generate\n\nspPortalAccountKeyGeneratePut950\n\nGenerate a new Portal account key",
    capability=Capability.WRITE,
)
async def edgeconnect_put_sp_portal_account_key_generate(
    ctx: Context,
    secondaryAccountName: Annotated[
        str | None,
        Field(
            default=None,
            description="Name of the secondary account to generate a key for. Leave empty or omit to generate a key for the primary account.",
        ),
    ] = None,
) -> Any:
    query_params: dict[str, Any] = {}
    if secondaryAccountName is not None:
        query_params["secondaryAccountName"] = secondaryAccountName
    return await edgeconnect_request(
        ctx,
        "PUT",
        "/spPortal/account/key/generate",
        query_params=query_params or None,
    )
