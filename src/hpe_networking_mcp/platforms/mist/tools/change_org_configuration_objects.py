"""
--------------------------------------------------------------------------------
-------------------------------- Mist MCP SERVER -------------------------------

    Written by: Thomas Munzer (tmunzer@juniper.net)
    Github    : https://github.com/tmunzer/mistmcp

    This package is licensed under the MIT License.

--------------------------------------------------------------------------------
"""

from enum import Enum
from typing import Annotated
from uuid import UUID

import mistapi
from fastmcp import Context
from fastmcp.exceptions import ToolError
from loguru import logger
from pydantic import Field

from hpe_networking_mcp.middleware.elicitation import elicitation_handler
from hpe_networking_mcp.platforms.mist._registry import mcp
from hpe_networking_mcp.platforms.mist.client import (
    format_response,
    get_apisession,
    handle_network_error,
    process_response,
)
from hpe_networking_mcp.platforms.mist.tools.guardrails import validate_org_write


class Object_type(Enum):
    ALARMTEMPLATES = "alarmtemplates"
    SITES = "sites"
    WLANS = "wlans"
    SITEGROUPS = "sitegroups"
    AVPROFILES = "avprofiles"
    DEVICEPROFILES = "deviceprofiles"
    GATEWAYTEMPLATES = "gatewaytemplates"
    IDPPROFILES = "idpprofiles"
    AAMWPROFILES = "aamwprofiles"
    NACTAGS = "nactags"
    NACRULES = "nacrules"
    NETWORKTEMPLATES = "networktemplates"
    NETWORKS = "networks"
    PSKS = "psks"
    RFTEMPLATES = "rftemplates"
    SERVICES = "services"
    SERVICEPOLICIES = "servicepolicies"
    SITETEMPLATES = "sitetemplates"
    VPNS = "vpns"
    WEBHOOKS = "webhooks"
    WLANTEMPLATES = "wlantemplates"
    WXRULES = "wxrules"
    WXTAGS = "wxtags"


class Action_type(Enum):
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"


@mcp.tool(
    name="mist_change_org_configuration_objects",
    description=(
        "Update, create or delete configuration object for a specified org.\n"
        "\nIMPORTANT:\n"
        "To ensure that you are not missing any existing attributes "
        "when updating the configuration object, make sure to:\n"
        "1. retrieve the current configuration object using the tools "
        "`mist_get_configuration_objects` to retrieve the object "
        "defined at the site level\n"
        "2. Modify the desired attributes\n"
        "3. Use this tool to update the configuration object with "
        "the modified attributes\n"
        "\nWhen creating a new configuration object, make sure to use "
        "the `mist_get_configuration_object_schema` tool to discover "
        "the attributes of the configuration object and which of "
        "them are required.\n"
        "\nWhen deleting a WLAN Template, make sure to delete all "
        "WLANs that are using the template before deleting it, "
        "otherwise the deletion will fail\n"
        "When creating a WLAN, make sure to set the `template_id` "
        "attribute in the payload to the ID of an existing WLAN "
        "Template. If needed, create a new WLAN Template using this "
        "tool before creating the WLAN and use the ID of the newly "
        "created template in the WLAN payload\n"
    ),
    tags={"mist_write_delete"},
    annotations={
        "title": "Change org configuration objects",
        "readOnlyHint": False,
        "destructiveHint": True,
        "openWorldHint": True,
        "idempotentHint": False,
    },
)
async def change_org_configuration_objects(
    action_type: Annotated[
        Action_type,
        Field(
            description=(
                "Whether the action is creating a new object, "
                "updating an existing one, or deleting an existing "
                "one. When updating or deleting, the object_id "
                "parameter must be provided."
            )
        ),
    ],
    org_id: Annotated[
        UUID,
        Field(description="Organization ID"),
    ],
    object_type: Annotated[
        Object_type,
        Field(description=("Type of configuration object to create, update, or delete")),
    ],
    payload: Annotated[
        dict,
        Field(
            description=(
                "JSON payload of the configuration object to "
                "update or create. When updating an existing "
                "object, make sure to include all required "
                "attributes in the payload. It is recommended to "
                "first retrieve the current configuration object "
                "using the `mist_get_configuration_objects` tool "
                "and use the retrieved object as a base for the "
                "payload, modifying only the desired attributes"
            )
        ),
    ],
    object_id: Annotated[
        UUID,
        Field(
            description=(
                "ID of the specific configuration object to update. Required when action_type is 'update' or 'delete'"
            ),
            default=None,
        ),
    ],
    ctx: Context,
) -> dict | list | str:
    """Update, create or delete configuration object for a specified org."""

    logger.debug("Tool change_org_configuration_objects called")
    logger.debug(
        "Input Parameters: org_id: %s, object_type: %s, payload: %s, object_id: %s",
        org_id,
        object_type,
        payload,
        object_id,
    )

    apisession, response_format = await get_apisession()

    action_wording = "create a new"
    if action_type == Action_type.UPDATE:
        if not object_id:
            raise ToolError(
                {
                    "status_code": 400,
                    "message": ("object_id parameter is required when action_type is 'update'."),
                }
            )
        action_wording = "update an existing"
    elif action_type == Action_type.DELETE:
        if not object_id:
            raise ToolError(
                {
                    "status_code": 400,
                    "message": ("object_id parameter is required when action_type is 'delete'."),
                }
            )
        action_wording = "delete an existing"

    guardrails = validate_org_write(object_type.value, action_type.value, payload)
    guardrail_notice = ""
    if guardrails.warnings:
        guardrail_notice = "\n\n" + "\n".join(guardrails.warnings[:3])

    if ctx:
        try:
            elicitation_response = await elicitation_handler(
                message=(
                    f"The LLM wants to {action_wording} {object_type.value}. "
                    f"Do you accept to trigger the API call?{guardrail_notice}"
                ),
                ctx=ctx,
            )
        except Exception as exc:
            raise ToolError(
                {
                    "status_code": 400,
                    "message": (
                        "AI App does not support elicitation. "
                        "You cannot use it to modify "
                        "configuration objects. Please use the "
                        "Mist API directly or use an AI App "
                        "with elicitation support to modify "
                        "configuration objects."
                    ),
                }
            ) from exc

        if elicitation_response.action == "decline":
            return {"message": "Action declined by user."}
        elif elicitation_response.action == "cancel":
            return {"message": "Action canceled by user."}

    org = str(org_id)
    obj = str(object_id)

    try:
        match object_type.value:
            case "alarmtemplates":
                if action_type.value == "update":
                    response = mistapi.api.v1.orgs.alarmtemplates.updateOrgAlarmTemplate(
                        apisession,
                        org_id=org,
                        alarmtemplate_id=obj,
                        body=payload,
                    )
                    await process_response(response)
                elif action_type.value == "create":
                    response = mistapi.api.v1.orgs.alarmtemplates.createOrgAlarmTemplate(
                        apisession, org_id=org, body=payload
                    )
                    await process_response(response)
                else:
                    response = mistapi.api.v1.orgs.alarmtemplates.deleteOrgAlarmTemplate(
                        apisession,
                        org_id=org,
                        alarmtemplate_id=obj,
                    )
                    await process_response(response)
            case "sites":
                if action_type.value == "update":
                    response = mistapi.api.v1.sites.sites.updateSiteInfo(
                        apisession,
                        site_id=obj,
                        body=payload,
                    )
                    await process_response(response)
                elif action_type.value == "create":
                    response = mistapi.api.v1.orgs.sites.createOrgSite(apisession, org_id=org, body=payload)
                    await process_response(response)
                else:
                    response = mistapi.api.v1.sites.sites.deleteSite(apisession, site_id=obj)
                    await process_response(response)
            case "wlans":
                if action_type.value == "update":
                    response = mistapi.api.v1.orgs.wlans.updateOrgWlan(
                        apisession,
                        org_id=org,
                        wlan_id=obj,
                        body=payload,
                    )
                    await process_response(response)
                elif action_type.value == "create":
                    response = mistapi.api.v1.orgs.wlans.createOrgWlan(apisession, org_id=org, body=payload)
                    await process_response(response)
                else:
                    response = mistapi.api.v1.orgs.wlans.deleteOrgWlan(apisession, org_id=org, wlan_id=obj)
                    await process_response(response)
            case "sitegroups":
                if action_type.value == "update":
                    response = mistapi.api.v1.orgs.sitegroups.updateOrgSiteGroup(
                        apisession,
                        org_id=org,
                        sitegroup_id=obj,
                        body=payload,
                    )
                    await process_response(response)
                elif action_type.value == "create":
                    response = mistapi.api.v1.orgs.sitegroups.createOrgSiteGroup(apisession, org_id=org, body=payload)
                    await process_response(response)
                else:
                    response = mistapi.api.v1.orgs.sitegroups.deleteOrgSiteGroup(
                        apisession,
                        org_id=org,
                        sitegroup_id=obj,
                    )
                    await process_response(response)
            case "avprofiles":
                if action_type.value == "update":
                    response = mistapi.api.v1.orgs.avprofiles.updateOrgAntivirusProfile(
                        apisession,
                        org_id=org,
                        avprofile_id=obj,
                        body=payload,
                    )
                    await process_response(response)
                elif action_type.value == "create":
                    response = mistapi.api.v1.orgs.avprofiles.createOrgAntivirusProfile(
                        apisession, org_id=org, body=payload
                    )
                    await process_response(response)
                else:
                    response = mistapi.api.v1.orgs.avprofiles.deleteOrgAntivirusProfile(
                        apisession,
                        org_id=org,
                        avprofile_id=obj,
                    )
                    await process_response(response)
            case "deviceprofiles":
                if action_type.value == "update":
                    response = mistapi.api.v1.orgs.deviceprofiles.updateOrgDeviceProfile(
                        apisession,
                        org_id=org,
                        deviceprofile_id=obj,
                        body=payload,
                    )
                    await process_response(response)
                elif action_type.value == "create":
                    response = mistapi.api.v1.orgs.deviceprofiles.createOrgDeviceProfile(
                        apisession, org_id=org, body=payload
                    )
                    await process_response(response)
                else:
                    response = mistapi.api.v1.orgs.deviceprofiles.deleteOrgDeviceProfile(
                        apisession,
                        org_id=org,
                        deviceprofile_id=obj,
                    )
                    await process_response(response)
            case "gatewaytemplates":
                if action_type.value == "update":
                    response = mistapi.api.v1.orgs.gatewaytemplates.updateOrgGatewayTemplate(
                        apisession,
                        org_id=org,
                        gatewaytemplate_id=obj,
                        body=payload,
                    )
                    await process_response(response)
                elif action_type.value == "create":
                    response = mistapi.api.v1.orgs.gatewaytemplates.createOrgGatewayTemplate(
                        apisession, org_id=org, body=payload
                    )
                    await process_response(response)
                else:
                    response = mistapi.api.v1.orgs.gatewaytemplates.deleteOrgGatewayTemplate(
                        apisession,
                        org_id=org,
                        gatewaytemplate_id=obj,
                    )
                    await process_response(response)
            case "idpprofiles":
                if action_type.value == "update":
                    response = mistapi.api.v1.orgs.idpprofiles.updateOrgIdpProfile(
                        apisession,
                        org_id=org,
                        idpprofile_id=obj,
                        body=payload,
                    )
                    await process_response(response)
                elif action_type.value == "create":
                    response = mistapi.api.v1.orgs.idpprofiles.createOrgIdpProfile(apisession, org_id=org, body=payload)
                    await process_response(response)
                else:
                    response = mistapi.api.v1.orgs.idpprofiles.deleteOrgIdpProfile(
                        apisession,
                        org_id=org,
                        idpprofile_id=obj,
                    )
                    await process_response(response)
            case "aamwprofiles":
                if action_type.value == "update":
                    response = mistapi.api.v1.orgs.aamwprofiles.updateOrgAAMWProfile(
                        apisession,
                        org_id=org,
                        aamwprofile_id=obj,
                        body=payload,
                    )
                    await process_response(response)
                elif action_type.value == "create":
                    response = mistapi.api.v1.orgs.aamwprofiles.createOrgAAMWProfile(
                        apisession, org_id=org, body=payload
                    )
                    await process_response(response)
                else:
                    response = mistapi.api.v1.orgs.aamwprofiles.deleteOrgAAMWProfile(
                        apisession,
                        org_id=org,
                        aamwprofile_id=obj,
                    )
                    await process_response(response)
            case "nactags":
                if action_type.value == "update":
                    response = mistapi.api.v1.orgs.nactags.updateOrgNacTag(
                        apisession,
                        org_id=org,
                        nactag_id=obj,
                        body=payload,
                    )
                    await process_response(response)
                elif action_type.value == "create":
                    response = mistapi.api.v1.orgs.nactags.createOrgNacTag(apisession, org_id=org, body=payload)
                    await process_response(response)
                else:
                    response = mistapi.api.v1.orgs.nactags.deleteOrgNacTag(
                        apisession,
                        org_id=org,
                        nactag_id=obj,
                    )
                    await process_response(response)
            case "nacrules":
                if action_type.value == "update":
                    response = mistapi.api.v1.orgs.nacrules.updateOrgNacRule(
                        apisession,
                        org_id=org,
                        nacrule_id=obj,
                        body=payload,
                    )
                    await process_response(response)
                elif action_type.value == "create":
                    response = mistapi.api.v1.orgs.nacrules.createOrgNacRule(apisession, org_id=org, body=payload)
                    await process_response(response)
                else:
                    response = mistapi.api.v1.orgs.nacrules.deleteOrgNacRule(
                        apisession,
                        org_id=org,
                        nacrule_id=obj,
                    )
                    await process_response(response)
            case "networktemplates":
                if action_type.value == "update":
                    response = mistapi.api.v1.orgs.networktemplates.updateOrgNetworkTemplate(
                        apisession,
                        org_id=org,
                        networktemplate_id=obj,
                        body=payload,
                    )
                    await process_response(response)
                elif action_type.value == "create":
                    response = mistapi.api.v1.orgs.networktemplates.createOrgNetworkTemplate(
                        apisession, org_id=org, body=payload
                    )
                    await process_response(response)
                else:
                    response = mistapi.api.v1.orgs.networktemplates.deleteOrgNetworkTemplate(
                        apisession,
                        org_id=org,
                        networktemplate_id=obj,
                    )
                    await process_response(response)
            case "networks":
                if action_type.value == "update":
                    response = mistapi.api.v1.orgs.networks.updateOrgNetwork(
                        apisession,
                        org_id=org,
                        network_id=obj,
                        body=payload,
                    )
                    await process_response(response)
                elif action_type.value == "create":
                    response = mistapi.api.v1.orgs.networks.createOrgNetwork(apisession, org_id=org, body=payload)
                    await process_response(response)
                else:
                    response = mistapi.api.v1.orgs.networks.deleteOrgNetwork(
                        apisession,
                        org_id=org,
                        network_id=obj,
                    )
                    await process_response(response)
            case "psks":
                if action_type.value == "update":
                    response = mistapi.api.v1.orgs.psks.updateOrgPsk(
                        apisession,
                        org_id=org,
                        psk_id=obj,
                        body=payload,
                    )
                    await process_response(response)
                elif action_type.value == "create":
                    response = mistapi.api.v1.orgs.psks.createOrgPsk(apisession, org_id=org, body=payload)
                    await process_response(response)
                else:
                    response = mistapi.api.v1.orgs.psks.deleteOrgPsk(apisession, org_id=org, psk_id=obj)
                    await process_response(response)
            case "rftemplates":
                if action_type.value == "update":
                    response = mistapi.api.v1.orgs.rftemplates.updateOrgRfTemplate(
                        apisession,
                        org_id=org,
                        rftemplate_id=obj,
                        body=payload,
                    )
                    await process_response(response)
                elif action_type.value == "create":
                    response = mistapi.api.v1.orgs.rftemplates.createOrgRfTemplate(apisession, org_id=org, body=payload)
                    await process_response(response)
                else:
                    response = mistapi.api.v1.orgs.rftemplates.deleteOrgRfTemplate(
                        apisession,
                        org_id=org,
                        rftemplate_id=obj,
                    )
                    await process_response(response)
            case "services":
                if action_type.value == "update":
                    response = mistapi.api.v1.orgs.services.updateOrgService(
                        apisession,
                        org_id=org,
                        service_id=obj,
                        body=payload,
                    )
                    await process_response(response)
                elif action_type.value == "create":
                    response = mistapi.api.v1.orgs.services.createOrgService(apisession, org_id=org, body=payload)
                    await process_response(response)
                else:
                    response = mistapi.api.v1.orgs.services.deleteOrgService(
                        apisession,
                        org_id=org,
                        service_id=obj,
                    )
                    await process_response(response)
            case "servicepolicies":
                if action_type.value == "update":
                    response = mistapi.api.v1.orgs.servicepolicies.updateOrgServicePolicy(
                        apisession,
                        org_id=org,
                        servicepolicy_id=obj,
                        body=payload,
                    )
                    await process_response(response)
                elif action_type.value == "create":
                    response = mistapi.api.v1.orgs.servicepolicies.createOrgServicePolicy(
                        apisession, org_id=org, body=payload
                    )
                    await process_response(response)
                else:
                    response = mistapi.api.v1.orgs.servicepolicies.deleteOrgServicePolicy(
                        apisession,
                        org_id=org,
                        servicepolicy_id=obj,
                    )
                    await process_response(response)
            case "sitetemplates":
                if action_type.value == "update":
                    response = mistapi.api.v1.orgs.sitetemplates.updateOrgSiteTemplate(
                        apisession,
                        org_id=org,
                        sitetemplate_id=obj,
                        body=payload,
                    )
                    await process_response(response)
                elif action_type.value == "create":
                    response = mistapi.api.v1.orgs.sitetemplates.createOrgSiteTemplate(
                        apisession, org_id=org, body=payload
                    )
                    await process_response(response)
                else:
                    response = mistapi.api.v1.orgs.sitetemplates.deleteOrgSiteTemplate(
                        apisession,
                        org_id=org,
                        sitetemplate_id=obj,
                    )
                    await process_response(response)
            case "vpns":
                if action_type.value == "update":
                    response = mistapi.api.v1.orgs.vpns.updateOrgVpn(
                        apisession,
                        org_id=org,
                        vpn_id=obj,
                        body=payload,
                    )
                    await process_response(response)
                elif action_type.value == "create":
                    response = mistapi.api.v1.orgs.vpns.createOrgVpn(apisession, org_id=org, body=payload)
                    await process_response(response)
                else:
                    response = mistapi.api.v1.orgs.vpns.deleteOrgVpn(apisession, org_id=org, vpn_id=obj)
                    await process_response(response)
            case "webhooks":
                if action_type.value == "update":
                    response = mistapi.api.v1.orgs.webhooks.updateOrgWebhook(
                        apisession,
                        org_id=org,
                        webhook_id=obj,
                        body=payload,
                    )
                    await process_response(response)
                elif action_type.value == "create":
                    response = mistapi.api.v1.orgs.webhooks.createOrgWebhook(apisession, org_id=org, body=payload)
                    await process_response(response)
                else:
                    response = mistapi.api.v1.orgs.webhooks.deleteOrgWebhook(
                        apisession,
                        org_id=org,
                        webhook_id=obj,
                    )
                    await process_response(response)
            case "wlantemplates":
                if action_type.value == "update":
                    response = mistapi.api.v1.orgs.templates.updateOrgTemplate(
                        apisession,
                        org_id=org,
                        template_id=obj,
                        body=payload,
                    )
                    await process_response(response)
                elif action_type.value == "create":
                    response = mistapi.api.v1.orgs.templates.createOrgTemplate(apisession, org_id=org, body=payload)
                    await process_response(response)
                else:
                    response = mistapi.api.v1.orgs.templates.deleteOrgTemplate(
                        apisession,
                        org_id=org,
                        template_id=obj,
                    )
                    await process_response(response)
            case "wxrules":
                if action_type.value == "update":
                    response = mistapi.api.v1.orgs.wxrules.updateOrgWxRule(
                        apisession,
                        org_id=org,
                        wxrule_id=obj,
                        body=payload,
                    )
                    await process_response(response)
                elif action_type.value == "create":
                    response = mistapi.api.v1.orgs.wxrules.createOrgWxRule(apisession, org_id=org, body=payload)
                    await process_response(response)
                else:
                    response = mistapi.api.v1.orgs.wxrules.deleteOrgWxRule(
                        apisession,
                        org_id=org,
                        wxrule_id=obj,
                    )
                    await process_response(response)
            case "wxtags":
                if action_type.value == "update":
                    response = mistapi.api.v1.orgs.wxtags.updateOrgWxTag(
                        apisession,
                        org_id=org,
                        wxtag_id=obj,
                        body=payload,
                    )
                    await process_response(response)
                elif action_type.value == "create":
                    response = mistapi.api.v1.orgs.wxtags.createOrgWxTag(apisession, org_id=org, body=payload)
                    await process_response(response)
                else:
                    response = mistapi.api.v1.orgs.wxtags.deleteOrgWxTag(
                        apisession,
                        org_id=org,
                        wxtag_id=obj,
                    )
                    await process_response(response)

            case _:
                raise ToolError(
                    {
                        "status_code": 400,
                        "message": (
                            f"Invalid object_type: "
                            f"{object_type.value}. Valid values "
                            f"are: "
                            f"{[e.value for e in Object_type]}"
                        ),
                    }
                )

    except ToolError:
        raise
    except Exception as _exc:
        await handle_network_error(_exc)

    result = format_response(response, response_format)
    if guardrails.suggestions and isinstance(result, dict):
        result["_best_practice_suggestions"] = guardrails.suggestions
    return result
