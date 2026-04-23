"""
--------------------------------------------------------------------------------
-------------------------------- Mist MCP SERVER -------------------------------

    Written by: Thomas Munzer (tmunzer@juniper.net)
    Github    : https://github.com/tmunzer/mistmcp

    This package is licensed under the MIT License.

--------------------------------------------------------------------------------
"""

from enum import Enum
from typing import Annotated, Any
from uuid import UUID

import mistapi
from fastmcp.exceptions import ToolError
from loguru import logger
from mistapi.__api_response import APIResponse as _APIResponse
from pydantic import Field
from requests.structures import CaseInsensitiveDict

from hpe_networking_mcp.platforms.mist._registry import tool
from hpe_networking_mcp.platforms.mist.client import (
    format_response,
    get_apisession,
    handle_network_error,
    process_response,
    validate_org_id,
)


class Object_type(Enum):
    ORG = "org"
    ORG_ALARMTEMPLATES = "org_alarmtemplates"
    ORG_WLANS = "org_wlans"
    ORG_SITEGROUPS = "org_sitegroups"
    ORG_AVPROFILES = "org_avprofiles"
    ORG_DEVICEPROFILES = "org_deviceprofiles"
    ORG_EVPN_TOPOLOGIES = "org_evpn_topologies"
    ORG_GATEWAYTEMPLATES = "org_gatewaytemplates"
    ORG_IDPPROFILES = "org_idpprofiles"
    ORG_AAMWPROFILES = "org_aamwprofiles"
    ORG_MXCLUSTERS = "org_mxclusters"
    ORG_MXEDGES = "org_mxedges"
    ORG_MXTUNNELS = "org_mxtunnels"
    ORG_NACTAGS = "org_nactags"
    ORG_NACRULES = "org_nacrules"
    ORG_NETWORKTEMPLATES = "org_networktemplates"
    ORG_NETWORKS = "org_networks"
    ORG_PSKS = "org_psks"
    ORG_RFTEMPLATES = "org_rftemplates"
    ORG_SERVICES = "org_services"
    ORG_SERVICEPOLICIES = "org_servicepolicies"
    ORG_SITES = "org_sites"
    ORG_SITETEMPLATES = "org_sitetemplates"
    ORG_VPNS = "org_vpns"
    ORG_WEBHOOKS = "org_webhooks"
    ORG_WLANTEMPLATES = "org_wlantemplates"
    ORG_WXRULES = "org_wxrules"
    ORG_WXTAGS = "org_wxtags"
    SITE_EVPN_TOPOLOGIES = "site_evpn_topologies"
    SITE_MAPS = "site_maps"
    SITE_MXEDGES = "site_mxedges"
    SITE_PSKS = "site_psks"
    SITE_WEBHOOKS = "site_webhooks"
    SITE_WLANS = "site_wlans"
    SITE_WXRULES = "site_wxrules"
    SITE_WXTAGS = "site_wxtags"
    SITE_DEVICES = "site_devices"


NETWORK_TEMPLATE_FIELDS = [
    "auto_upgrade_linecard",
    "acl_policies",
    "acl_tags",
    "additional_config_cmds",
    "dhcp_snooping",
    "disabled_system_defined_port_usages",
    "dns_servers",
    "dns_suffix",
    "extra_routes",
    "extra_routes6",
    "fips_enabled",
    "id",
    "mist_nac",
    "networks",
    "ntp_servers",
    "port_mirroring",
    "port_usages",
    "radius_config",
    "remote_syslog",
    "snmp_config",
    "routing_policies",
    "switch_matching",
    "switch_mgmt",
    "vrf_config",
    "vrf_instances",
]


def _name_id_list(data: list) -> list:
    """Extract name+id pairs from a list of dicts."""
    return [{"name": item.get("name"), "id": item.get("id")} for item in data if item.get("name")]


@tool(
    name="mist_get_configuration_objects",
    description=(
        "Use this tool to retrieve configuration objects "
        "from a specified organization or site.\n"
        "\nThis tool fetches configuration objects such as "
        "WLANs, device profiles, network templates and "
        "device configurations. For site-level configuration "
        "objects, set `computed=true` to retrieve the "
        "computed configuration, which includes all "
        "configuration objects defined at the organization "
        "level and inherited by the site.\n"
        "\nYou can retrieve all objects of a specified type, "
        "or filter results by:\n"
        "- `object_id`: Retrieve a single object by its ID\n"
        "- `name`: Retrieve objects by name "
        "(case-insensitive, supports wildcard matching "
        "with `*`)\n"
        "\n**Pagination Note:** Pagination is not supported "
        "when `name` is provided. Results are limited to "
        "the first entries up to the `limit` value "
        "(default: 20, maximum: 1000).\n"
        "\nReturns:\n"
        "    A dictionary, list, or string containing the "
        "retrieved configuration objects.\n"
        "\nRaises:\n"
        "    ToolError: If `site_id` is not provided when "
        "required, or if the API call fails."
    ),
    tags={"configuration"},
    annotations={
        "title": "Get configuration objects",
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": True,
        "idempotentHint": True,
    },
)
async def get_configuration_objects(
    org_id: Annotated[UUID, Field(description="Organization ID")],
    object_type: Annotated[
        Object_type,
        Field(description=("Type of configuration object to retrieve")),
    ],
    site_id: Annotated[
        UUID,
        Field(
            default=None,
            description=(
                "ID of the site to retrieve configuration "
                "objects from. Required when object_type is "
                "starting with `site_`, optional if "
                "object_type is 'org_sites' to retrieve a "
                "single site"
            ),
        ),
    ],
    object_id: Annotated[
        UUID,
        Field(
            default=None,
            description=(
                "ID of the specific configuration object "
                "to retrieve. If not provided, all objects "
                "of the specified type will be retrieved"
            ),
        ),
    ],
    name: Annotated[
        str,
        Field(
            default=None,
            description=(
                "Name of the specific configuration object "
                "to retrieve. Not supported when "
                "`object_type` is `site_devices` (use the "
                "`mist_search_device` tool if you need to "
                "find a specific device). If not provided, "
                "all objects of the specified type will be "
                "retrieved. Case insensitive. Use `prefix*` "
                "for prefix search or `*substring*` for "
                "contains search (e.g. `aabbcc*` and "
                "`*bbcc*` match `aabbccddeeff`). "
                "Suffix-only wildcards (e.g. "
                "`*bccddeeff`) are not supported"
            ),
        ),
    ],
    computed: Annotated[
        bool,
        Field(
            default=None,
            description=(
                "Whether to retrieve the computed "
                "configuration object with all inherited "
                "settings applied. Only considered when "
                "object_type is `org_sites` and "
                "`site_devices` when a single object is "
                "returned, or when object_type is "
                "`site_wlans`"
            ),
        ),
    ],
    limit: Annotated[
        int,
        Field(
            default=20,
            description=("Max number of results per page. Default is 20, Max is 1000"),
        ),
    ] = 20,
) -> dict | list | str:
    """Retrieve configuration objects from an org or site."""

    logger.debug("Tool get_configuration_objects called")
    logger.debug(
        "Input Parameters: org_id=%s, object_type=%s, site_id=%s, object_id=%s, name=%s, computed=%s, limit=%s",
        org_id,
        object_type,
        site_id,
        object_id,
        name,
        computed,
        limit,
    )

    validate_org_id(str(org_id))
    apisession, response_format = await get_apisession()

    response = None
    try:
        if object_type.value.startswith("site_"):
            if not site_id:
                raise ToolError("site_id is required when object_type starts with 'site_'")
            else:
                response = await _site_config_getter(
                    apisession=apisession,
                    object_type=object_type.value,
                    org_id=str(org_id),
                    site_id=str(site_id),
                    object_id=(str(object_id) if object_id else None),
                    name=name if name else None,
                    computed=computed,
                    limit=limit if limit else 20,
                )
        else:
            response = await _org_config_getter(
                apisession=apisession,
                object_type=object_type.value,
                org_id=str(org_id),
                site_id=(str(site_id) if site_id else None),
                object_id=(str(object_id) if object_id else None),
                name=name if name else None,
                limit=limit if limit else 20,
            )

    except ToolError:
        raise
    except Exception as _exc:
        await handle_network_error(_exc)

    if response is None:
        raise ToolError(
            {
                "status_code": 503,
                "message": ("API call failed: No response object was created due to an error."),
            }
        )
    return format_response(response, response_format)


# ---- helpers for org-level getter with 3-letter aliases ----


def _org_api(mod: str, func: str):
    """Resolve mistapi.api.v1.orgs.<mod>.<func>."""
    return getattr(getattr(mistapi.api.v1.orgs, mod), func)


def _site_api(mod: str, func: str):
    """Resolve mistapi.api.v1.sites.<mod>.<func>."""
    return getattr(getattr(mistapi.api.v1.sites, mod), func)


async def _org_list_or_get(
    apisession,
    mod,
    get_func,
    list_func,
    org_id,
    id_kwarg,
    object_id,
    name,
    name_attr,
    limit,
    strip_to_name_id=True,
):
    """Common pattern: get-by-id / search-by-name / list."""
    if object_id:
        response = _org_api(mod, get_func)(
            apisession,
            org_id=org_id,
            **{id_kwarg: object_id},
        )
        await process_response(response)
    elif name:
        response = _org_api(mod, list_func)(
            apisession,
            org_id=org_id,
            limit=1000,
        )
        data_in = mistapi.get_all(apisession, response)
        response = _search_object(
            data_in,
            name,
            name_attr,
            limit=limit,
        )
        await process_response(response)
    else:
        response = _org_api(mod, list_func)(
            apisession,
            org_id=org_id,
            limit=limit,
        )
        await process_response(response)
        if strip_to_name_id:
            response.data = _name_id_list(response.data)
    return response


async def _org_config_getter(
    apisession: mistapi.APISession,
    object_type: str,
    org_id: str,
    site_id: str | None = None,
    object_id: str | None = None,
    name: str | None = None,
    computed: bool | None = None,
    limit: int = 20,
) -> _APIResponse:
    match object_type:
        case "org":
            response = mistapi.api.v1.orgs.setting.getOrgSettings(
                apisession,
                org_id=org_id,
            )
            await process_response(response)
        case "org_alarmtemplates":
            response = await _org_list_or_get(
                apisession,
                "alarmtemplates",
                "getOrgAlarmTemplate",
                "listOrgAlarmTemplates",
                org_id,
                "alarmtemplate_id",
                object_id,
                name,
                "name",
                limit,
            )
        case "org_wlans":
            if object_id:
                response = _org_api("wlans", "getOrgWLAN")(
                    apisession,
                    org_id=org_id,
                    wlan_id=object_id,
                )
                await process_response(response)
            elif name:
                response = _org_api("wlans", "listOrgWlans")(apisession, org_id=org_id, limit=1000)
                data_in = mistapi.get_all(
                    apisession,
                    response,
                )
                response = _search_object(
                    data_in,
                    name,
                    "ssid",
                )
                await process_response(response)
            else:
                response = _org_api("wlans", "listOrgWlans")(apisession, org_id=org_id, limit=limit)
                await process_response(response)
                response.data = [
                    {
                        "ssid": item.get("ssid"),
                        "id": item.get("id"),
                    }
                    for item in response.data
                    if item.get("ssid")
                ]
        case "org_sitegroups":
            response = await _org_list_or_get(
                apisession,
                "sitegroups",
                "getOrgSiteGroup",
                "listOrgSiteGroups",
                org_id,
                "sitegroup_id",
                object_id,
                name,
                "name",
                limit,
                strip_to_name_id=False,
            )
        case "org_avprofiles":
            response = await _org_list_or_get(
                apisession,
                "avprofiles",
                "getOrgAntivirusProfile",
                "listOrgAntivirusProfiles",
                org_id,
                "avprofile_id",
                object_id,
                name,
                "name",
                limit,
            )
        case "org_deviceprofiles":
            response = await _org_list_or_get(
                apisession,
                "deviceprofiles",
                "getOrgDeviceProfile",
                "listOrgDeviceProfiles",
                org_id,
                "deviceprofile_id",
                object_id,
                name,
                "name",
                limit,
            )
        case "org_evpn_topologies":
            response = await _org_list_or_get(
                apisession,
                "evpn_topologies",
                "getOrgEvpnTopology",
                "listOrgEvpnTopologies",
                org_id,
                "evpn_topology_id",
                object_id,
                name,
                "name",
                limit,
            )
        case "org_gatewaytemplates":
            response = await _org_list_or_get(
                apisession,
                "gatewaytemplates",
                "getOrgGatewayTemplate",
                "listOrgGatewayTemplates",
                org_id,
                "gatewaytemplate_id",
                object_id,
                name,
                "name",
                limit,
            )
        case "org_idpprofiles":
            response = await _org_list_or_get(
                apisession,
                "idpprofiles",
                "getOrgIdpProfile",
                "listOrgIdpProfiles",
                org_id,
                "idpprofile_id",
                object_id,
                name,
                "name",
                limit,
            )
        case "org_aamwprofiles":
            if object_id:
                response = _org_api("aamwprofiles", "getOrgAAMWProfile")(
                    apisession,
                    org_id=org_id,
                    aamwprofile_id=object_id,
                )
                await process_response(response)
            elif name:
                response = _org_api("aamwprofiles", "listOrgAAMWProfiles")(apisession, org_id=org_id)
                data_in = mistapi.get_all(
                    apisession,
                    response,
                )
                response = _search_object(
                    data_in,
                    name,
                    "name",
                    limit=limit,
                )
                await process_response(response)
            else:
                response = _org_api("aamwprofiles", "listOrgAAMWProfiles")(apisession, org_id=org_id)
                await process_response(response)
                response.data = _name_id_list(response.data)
        case "org_mxclusters":
            response = await _org_list_or_get(
                apisession,
                "mxclusters",
                "getOrgMxEdgeCluster",
                "listOrgMxEdgeClusters",
                org_id,
                "mxcluster_id",
                object_id,
                name,
                "name",
                limit,
            )
        case "org_mxedges":
            response = await _org_list_or_get(
                apisession,
                "mxedges",
                "getOrgMxEdge",
                "listOrgMxEdges",
                org_id,
                "mxedge_id",
                object_id,
                name,
                "name",
                limit,
            )
        case "org_mxtunnels":
            response = await _org_list_or_get(
                apisession,
                "mxtunnels",
                "getOrgMxTunnel",
                "listOrgMxTunnels",
                org_id,
                "mxtunnel_id",
                object_id,
                name,
                "name",
                limit,
            )
        case "org_nactags":
            response = await _org_list_or_get(
                apisession,
                "nactags",
                "getOrgNacTag",
                "listOrgNacTags",
                org_id,
                "nactag_id",
                object_id,
                name,
                "name",
                limit,
                strip_to_name_id=False,
            )
        case "org_nacrules":
            response = await _org_list_or_get(
                apisession,
                "nacrules",
                "getOrgNacRule",
                "listOrgNacRules",
                org_id,
                "nacrule_id",
                object_id,
                name,
                "name",
                limit,
                strip_to_name_id=False,
            )
        case "org_networktemplates":
            response = await _org_list_or_get(
                apisession,
                "networktemplates",
                "getOrgNetworkTemplate",
                "listOrgNetworkTemplates",
                org_id,
                "networktemplate_id",
                object_id,
                name,
                "name",
                limit,
            )
        case "org_networks":
            response = await _org_list_or_get(
                apisession,
                "networks",
                "getOrgNetwork",
                "listOrgNetworks",
                org_id,
                "network_id",
                object_id,
                name,
                "name",
                limit,
                strip_to_name_id=False,
            )
        case "org_psks":
            response = await _org_list_or_get(
                apisession,
                "psks",
                "getOrgPsk",
                "listOrgPsks",
                org_id,
                "psk_id",
                object_id,
                name,
                "name",
                limit,
                strip_to_name_id=False,
            )
        case "org_rftemplates":
            response = await _org_list_or_get(
                apisession,
                "rftemplates",
                "getOrgRfTemplate",
                "listOrgRfTemplates",
                org_id,
                "rftemplate_id",
                object_id,
                name,
                "name",
                limit,
            )
        case "org_services":
            if object_id:
                response = _org_api("services", "getOrgService")(
                    apisession,
                    org_id=org_id,
                    service_id=object_id,
                )
                await process_response(response)
            elif name:
                response = _org_api(
                    "networktemplates",
                    "listOrgNetworkTemplates",
                )(apisession, org_id=org_id, limit=1000)
                data_in = mistapi.get_all(
                    apisession,
                    response,
                )
                response = _search_object(
                    data_in,
                    name,
                    "name",
                    limit=limit,
                )
                await process_response(response)
            else:
                response = _org_api("services", "listOrgServices")(apisession, org_id=org_id, limit=limit)
                await process_response(response)
                response.data = _name_id_list(response.data)
        case "org_servicepolicies":
            response = await _org_list_or_get(
                apisession,
                "servicepolicies",
                "getOrgServicePolicy",
                "listOrgServicePolicies",
                org_id,
                "servicepolicy_id",
                object_id,
                name,
                "name",
                limit,
            )
        case "org_sites":
            if object_id:
                site_id = object_id
            if site_id:
                if computed:
                    response = _site_api(
                        "setting",
                        "getSiteSettingDerived",
                    )(apisession, site_id=site_id)
                    await process_response(response)
                else:
                    response = _site_api(
                        "setting",
                        "getSiteSetting",
                    )(apisession, site_id=site_id)
                    await process_response(response)
            elif name:
                response = _org_api("sites", "searchOrgSites")(
                    apisession,
                    org_id=org_id,
                    limit=limit,
                    name=name,
                )
                await process_response(response)
            else:
                response = _org_api("sites", "listOrgSites")(
                    apisession,
                    org_id=org_id,
                    limit=limit,
                )
                await process_response(response)
                response.data = _name_id_list(response.data)
        case "org_sitetemplates":
            response = await _org_list_or_get(
                apisession,
                "sitetemplates",
                "getOrgSiteTemplate",
                "listOrgSiteTemplates",
                org_id,
                "sitetemplate_id",
                object_id,
                name,
                "name",
                limit,
            )
        case "org_vpns":
            if object_id:
                response = _org_api("vpns", "getOrgVpn")(
                    apisession,
                    org_id=org_id,
                    vpn_id=object_id,
                )
                await process_response(response)
            elif name:
                response = _org_api("vpns", "listOrgVpns")(apisession, org_id=org_id)
                data_in = mistapi.get_all(
                    apisession,
                    response,
                )
                response = _search_object(
                    data_in,
                    name,
                    "name",
                    limit=limit,
                )
                await process_response(response)
            else:
                response = _org_api("vpns", "listOrgVpns")(
                    apisession,
                    org_id=org_id,
                    limit=limit,
                )
                await process_response(response)
        case "org_webhooks":
            response = await _org_list_or_get(
                apisession,
                "webhooks",
                "getOrgWebhook",
                "listOrgWebhooks",
                org_id,
                "webhook_id",
                object_id,
                name,
                "name",
                limit,
            )
        case "org_wlantemplates":
            response = await _org_list_or_get(
                apisession,
                "templates",
                "getOrgTemplate",
                "listOrgTemplates",
                org_id,
                "template_id",
                object_id,
                name,
                "name",
                limit,
            )
        case "org_wxrules":
            if object_id:
                response = _org_api("wxrules", "getOrgWxRule")(
                    apisession,
                    org_id=org_id,
                    wxrule_id=object_id,
                )
                await process_response(response)
            else:
                response = _org_api("wxrules", "listOrgWxRules")(
                    apisession,
                    org_id=org_id,
                    limit=limit,
                )
                await process_response(response)
        case "org_wxtags":
            response = await _org_list_or_get(
                apisession,
                "wxtags",
                "getOrgWxTag",
                "listOrgWxTags",
                org_id,
                "wxtag_id",
                object_id,
                name,
                "name",
                limit,
                strip_to_name_id=False,
            )
        case _:
            raise ToolError(
                {
                    "status_code": 400,
                    "message": (
                        f"Invalid object_type: {object_type}. Valid values are: {[e.value for e in Object_type]}"
                    ),
                }
            )
    return response


async def _site_list_or_get(
    apisession,
    mod,
    get_func,
    list_func,
    site_id,
    id_kwarg,
    object_id,
    name,
    name_attr,
    limit,
    strip_to_name_id=True,
):
    """Common pattern for site-level objects."""
    if object_id:
        response = _site_api(mod, get_func)(
            apisession,
            site_id=site_id,
            **{id_kwarg: object_id},
        )
        await process_response(response)
    elif name:
        response = _site_api(mod, list_func)(
            apisession,
            site_id=site_id,
            limit=1000,
        )
        data_in = mistapi.get_all(apisession, response)
        response = _search_object(
            data_in,
            name,
            name_attr,
            limit=limit,
        )
        await process_response(response)
    else:
        response = _site_api(mod, list_func)(
            apisession,
            site_id=site_id,
            limit=limit,
        )
        await process_response(response)
        if strip_to_name_id:
            response.data = _name_id_list(response.data)
    return response


async def _site_config_getter(
    apisession: mistapi.APISession,
    object_type: str,
    org_id: str,
    site_id: str,
    object_id: str | None = None,
    name: str | None = None,
    computed: bool | None = None,
    limit: int = 20,
) -> _APIResponse:
    match object_type:
        case "site_devices":
            return await _get_site_devices(
                apisession,
                org_id,
                site_id,
                object_id,
                name,
                computed,
                limit,
            )
        case "site_evpn_topologies":
            response = await _site_list_or_get(
                apisession,
                "evpn_topologies",
                "getSiteEvpnTopology",
                "listSiteEvpnTopologies",
                site_id,
                "evpn_topology_id",
                object_id,
                name,
                "name",
                limit,
            )
        case "site_maps":
            response = await _site_list_or_get(
                apisession,
                "maps",
                "getSiteMap",
                "listSiteMaps",
                site_id,
                "map_id",
                object_id,
                name,
                "name",
                limit,
            )
        case "site_mxedges":
            response = await _site_list_or_get(
                apisession,
                "mxedges",
                "getSiteMxEdge",
                "listSiteMxEdges",
                site_id,
                "mxedge_id",
                object_id,
                name,
                "name",
                limit,
            )
        case "site_psks":
            response = await _site_list_or_get(
                apisession,
                "psks",
                "getSitePsk",
                "listSitePsks",
                site_id,
                "psk_id",
                object_id,
                name,
                "name",
                limit,
                strip_to_name_id=False,
            )
        case "site_webhooks":
            response = await _site_list_or_get(
                apisession,
                "webhooks",
                "getSiteWebhook",
                "listSiteWebhooks",
                site_id,
                "webhook_id",
                object_id,
                name,
                "name",
                limit,
            )
        case "site_wlans":
            return await _get_site_wlans(
                apisession,
                org_id,
                site_id,
                object_id,
                name,
                computed,
                limit,
            )
        case "site_wxrules":
            if object_id:
                response = _site_api("wxrules", "getSiteWxRule")(
                    apisession,
                    site_id=site_id,
                    wxrule_id=object_id,
                )
                await process_response(response)
            else:
                response = _site_api("wxrules", "listSiteWxRules")(
                    apisession,
                    site_id=site_id,
                    limit=limit,
                )
                await process_response(response)
        case "site_wxtags":
            response = await _site_list_or_get(
                apisession,
                "wxtags",
                "getSiteWxTag",
                "listSiteWxTags",
                site_id,
                "wxtag_id",
                object_id,
                name,
                "name",
                limit,
                strip_to_name_id=False,
            )
        case _:
            raise ToolError(
                {
                    "status_code": 400,
                    "message": (
                        f"Invalid object_type: {object_type}. Valid values are: {[e.value for e in Object_type]}"
                    ),
                }
            )
    return response


#############################################
# SITE DEVICE RELATED FUNCTIONS
#############################################


async def _get_site_devices(
    apisession: mistapi.APISession,
    org_id: str,
    site_id: str,
    object_id: str | None = None,
    name: str | None = None,
    computed: bool | None = None,
    limit: int = 20,
) -> _APIResponse:
    if object_id:
        if computed:
            response = await _get_computed_device_config(
                apisession=apisession,
                org_id=org_id,
                site_id=site_id,
                device_id=object_id,
            )
            return response
        else:
            response = mistapi.api.v1.sites.devices.getSiteDevice(
                apisession,
                site_id=site_id,
                device_id=object_id,
            )
            await process_response(response)
            return response
    elif name:
        response = mistapi.api.v1.sites.devices.searchSiteDevices(
            apisession,
            site_id=site_id,
            hostname=name,
            limit=1000,
            type="all",
        )
        await process_response(response)
        if isinstance(response.data, dict) and len(response.data.get("results", [])) == 1 and computed:
            response.data = response.data["results"][0]
            response = await _get_computed_device_config(
                apisession=apisession,
                org_id=org_id,
                site_id=site_id,
                device_data=response,
            )
        return response
    else:
        response = mistapi.api.v1.sites.devices.listSiteDevices(
            apisession,
            site_id=site_id,
            limit=limit,
            type="all",
        )
        await process_response(response)
        return response


async def _get_computed_device_config(
    apisession: mistapi.APISession,
    org_id: str,
    site_id: str,
    device_id: str | None = None,
    device_data: _APIResponse | None = None,
) -> _APIResponse:
    logger.debug("func _get_device_configuration called")
    if device_id:
        device_data = mistapi.api.v1.sites.devices.getSiteDevice(
            apisession,
            site_id=site_id,
            device_id=device_id,
        )
        await process_response(device_data)
    elif not device_data:
        raise ToolError(
            {
                "status_code": 400,
                "message": ("Either device_id or device_data must be provided"),
            }
        )
    data: dict[str, Any] = {}
    if isinstance(device_data.data, dict):
        match device_data.data.get("type"):
            case "switch":
                sw_name = device_data.data.get("name", "")
                sw_model = device_data.data.get("model", "")
                sw_role = device_data.data.get("role", "")
                switch_data: dict[str, Any] = {}
                site_config = mistapi.api.v1.sites.setting.getSiteSettingDerived(
                    apisession,
                    site_id=site_id,
                )
                await process_response(site_config)
                if isinstance(site_config.data, dict):
                    switch_data = _process_switch_template(
                        site_config.data,
                        sw_name,
                        sw_model,
                        sw_role,
                        switch_data,
                    )
                for key, value in device_data.data.items():
                    if key == "port_config":
                        port_config = _process_switch_interface(value)
                        switch_data[key] = {
                            **data.get(key, {}),
                            **port_config,
                        }
                    elif isinstance(value, dict) and isinstance(switch_data.get(key, {}), dict):
                        switch_data[key] = {
                            **switch_data.get(key, {}),
                            **value,
                        }
                    elif isinstance(value, list) and isinstance(switch_data.get(key, []), list):
                        switch_data[key] = switch_data.get(key, []) + value
                    else:
                        switch_data[key] = value
                device_data.data = switch_data
            case "gateway":
                gateway_data = {}
                site_data = mistapi.api.v1.sites.sites.getSiteInfo(
                    apisession,
                    site_id=site_id,
                )
                await process_response(site_data)
                if isinstance(site_data.data, dict):
                    gw_tmpl_id = site_data.data.get("gatewaytemplate_id")
                    if gw_tmpl_id:
                        response = mistapi.api.v1.orgs.gatewaytemplates.getOrgGatewayTemplate(
                            apisession,
                            org_id=org_id,
                            gatewaytemplate_id=str(gw_tmpl_id),
                        )
                        await process_response(response)
                        gateway_data = response.data
                if isinstance(gateway_data, dict):
                    for key, value in device_data.data.items():
                        if key in NETWORK_TEMPLATE_FIELDS:
                            if isinstance(value, dict) and isinstance(
                                gateway_data.get(key, {}),
                                dict,
                            ):
                                gateway_data[key] = {
                                    **gateway_data.get(key, {}),
                                    **value,
                                }
                            elif isinstance(value, list) and isinstance(
                                gateway_data.get(key, []),
                                list,
                            ):
                                gateway_data[key] = gateway_data.get(key, []) + value
                            else:
                                gateway_data[key] = value
                device_data.data = gateway_data
    return device_data


#############################################
# SWITCH RELATED FUNCTIONS
#############################################


def _process_switch_template(
    template: dict,
    switch_name: str,
    switch_model: str,
    switch_role: str,
    data: dict,
) -> dict:
    for key, value in template.items():
        if key in NETWORK_TEMPLATE_FIELDS:
            if key == "name":
                continue
            elif key == "switch_matching" and value.get("enable"):
                data = _process_switch_rule(
                    value.get("rules", []),
                    switch_name,
                    switch_model,
                    switch_role,
                    data,
                )
            elif isinstance(value, dict) and isinstance(data.get(key, {}), dict):
                data[key] = {
                    **data.get(key, {}),
                    **value,
                }
            elif isinstance(value, list) and isinstance(data.get(key, []), list):
                data[key] = data.get(key, []) + value
            else:
                data[key] = value
    return data


def _process_switch_rule(
    rules: list,
    switch_name: str,
    switch_model: str,
    switch_role: str,
    data: dict,
) -> dict:
    for rule in rules:
        rule_cleansed = rule.copy()
        del rule_cleansed["name"]
        match_name_true = False
        match_name_enabled = False
        match_model_true = False
        match_model_enabled = False
        match_role_true = False
        match_role_enabled = False
        for k, v in rule.items():
            if k.startswith("match_name"):
                match_name_enabled = True
                del rule_cleansed[k]
                match_name_true = _process_switch_rule_match(switch_name, k, v)
            elif k.startswith("match_model"):
                match_model_enabled = True
                del rule_cleansed[k]
                match_model_true = _process_switch_rule_match(switch_model, k, v)
            elif k == "match_role":
                match_role_enabled = True
                match_role_true = _process_switch_rule_match(switch_role, k, v)
        if (
            (not match_name_enabled or match_name_true)
            and (not match_model_enabled or match_model_true)
            and (not match_role_enabled or match_role_true)
        ):
            for key, value in rule_cleansed.items():
                if key == "port_config":
                    port_config = _process_switch_interface(value)
                    data[key] = {
                        **data.get(key, {}),
                        **port_config,
                    }
                elif isinstance(value, dict) and isinstance(data.get(key, {}), dict):
                    data[key] = {
                        **data.get(key, {}),
                        **value,
                    }
                elif isinstance(value, list) and isinstance(data.get(key, []), list):
                    data[key] = data.get(key, []) + value
                else:
                    data[key] = value
            return data
    return data


def _process_switch_rule_match(
    switch_value: str,
    match_key: str,
    match_value: str,
) -> bool:
    if ":" in match_key:
        range_part = match_key.replace("]", "").split("[")[1]
        match_start, match_stop = range_part.split(":")
        try:
            start_i = int(match_start)
            stop_i = int(match_stop)
            if len(switch_value) > stop_i and switch_value[start_i:stop_i].lower() == match_value.lower():
                return True
        except Exception:
            return False
    elif switch_value.lower() == match_value.lower():
        return True
    return False


def _process_switch_interface(
    port_config: dict,
) -> dict:
    port_config_tmp = {}
    for key, value in port_config.items():
        if "," in key:
            keys = [k.strip() for k in key.split(",")]
            for k in keys:
                port_config_tmp[k] = value
        else:
            port_config_tmp[key] = value
    port_config_cleansed = {}
    for key, value in port_config_tmp.items():
        if key.count("-") > 1:
            prefix, interfaces = key.split("-", 1)
            fpc, pic, port = interfaces.split("/")
            if "-" in fpc:
                fpc_s, fpc_e = fpc.split("-")
                for n in range(int(fpc_s), int(fpc_e) + 1):
                    k = f"{prefix}-{n}/{pic}/{port}"
                    port_config_cleansed[k] = value
            elif "-" in pic:
                pic_s, pic_e = pic.split("-")
                for n in range(int(pic_s), int(pic_e) + 1):
                    k = f"{prefix}-{fpc}/{n}/{port}"
                    port_config_cleansed[k] = value
            elif "-" in port:
                port_s, port_e = port.split("-")
                for n in range(int(port_s), int(port_e) + 1):
                    k = f"{prefix}-{fpc}/{pic}/{n}"
                    port_config_cleansed[k] = value
        else:
            port_config_cleansed[key] = value
    return port_config_cleansed


#############################################
# SITE WLANS FUNCTIONS
#############################################


async def _get_site_wlans(
    apisession: mistapi.APISession,
    org_id: str,
    site_id: str,
    object_id: str | None = None,
    name: str | None = None,
    computed: bool | None = None,
    limit: int = 20,
) -> _APIResponse:
    if object_id:
        response = mistapi.api.v1.sites.wlans.getSiteWlan(
            apisession,
            site_id=site_id,
            wlan_id=object_id,
        )
        await process_response(response)
    elif computed:
        site_data = mistapi.api.v1.sites.sites.getSiteInfo(
            apisession,
            site_id=site_id,
        )
        await process_response(site_data)
        sitegroup_ids = site_data.data.get("sitegroup_ids", []) if isinstance(site_data.data, dict) else []
        assigned_template_ids = []
        assigned_wlans = []
        org_wlan_templates = mistapi.api.v1.orgs.templates.listOrgTemplates(
            apisession,
            org_id=org_id,
            limit=limit,
        )
        await process_response(org_wlan_templates)
        for template in org_wlan_templates.data:
            applies = template.get("applies", {})
            tmpl_org_id = applies.get("org_id", "")
            tmpl_site_ids = applies.get("site_ids", []) or []
            tmpl_sg_ids = applies.get("sitegroup_ids", []) or []
            if site_id in tmpl_site_ids or (set(tmpl_sg_ids) & set(sitegroup_ids)) or tmpl_org_id == org_id:
                assigned_template_ids.append(template.get("id"))
        org_wlans = mistapi.api.v1.orgs.wlans.listOrgWlans(
            apisession,
            org_id=org_id,
            limit=limit,
        )
        await process_response(org_wlans)
        for wlan in org_wlans.data:
            if wlan.get("template_id") in (assigned_template_ids):
                assigned_wlans.append(wlan)
        site_wlans = mistapi.api.v1.sites.wlans.listSiteWlans(
            apisession,
            site_id=site_id,
            limit=limit,
        )
        await process_response(site_wlans)
        if name:
            response = mistapi.api.v1.sites.wxtags.listSiteWxTags(
                apisession,
                site_id=site_id,
                limit=1000,
            )
            data_in = mistapi.get_all(
                apisession,
                response,
            )
            response = _search_object(
                data_in,
                name,
                "ssid",
                limit=limit,
            )
            await process_response(response)
        for wlan in site_wlans.data:
            assigned_wlans.append(wlan)
        site_wlans.data = assigned_wlans
        response = site_wlans
    else:
        response = mistapi.api.v1.sites.wlans.listSiteWlans(
            apisession,
            site_id=site_id,
            limit=limit,
        )
        await process_response(response)
        response.data = [
            {
                "ssid": item.get("ssid"),
                "id": item.get("id"),
            }
            for item in response.data
            if item.get("ssid")
        ]
    return response


def _search_object(
    data_in: list,
    name: str,
    attribute: str = "name",
    limit: int = 20,
) -> _APIResponse:
    data_out = []
    for entry in data_in:
        attr_val = entry.get(attribute, "")
        if name.startswith("*") and name.endswith("*"):
            if name[1:-1].lower() in attr_val.lower():
                data_out.append(entry)
        elif name.startswith("*"):
            if attr_val.lower().endswith(name[1:].lower()):
                data_out.append(entry)
        elif name.endswith("*"):
            if attr_val.lower().startswith(name[:-1].lower()):
                data_out.append(entry)
        else:
            if name.lower() in attr_val.lower():
                data_out.append(entry)
    response = _APIResponse(url="", response=None)
    response.data = data_out[:limit]
    response.status_code = 200
    response.headers = CaseInsensitiveDict(
        {
            "X-Page-Total": str(len(data_out)),
            "X-Page-Limit": str(limit),
        }
    )
    return response
