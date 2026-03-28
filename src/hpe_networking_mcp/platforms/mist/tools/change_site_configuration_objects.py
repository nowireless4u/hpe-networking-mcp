"""
--------------------------------------------------------------------------------
-------------------------------- Mist MCP SERVER -------------------------------

    Written by: Thomas Munzer (tmunzer@juniper.net)
    Github    : https://github.com/tmunzer/mistmcp

    This package is licensed under the MIT License.

--------------------------------------------------------------------------------
"""

import mistapi
from fastmcp import Context
from fastmcp.exceptions import ToolError
from hpe_networking_mcp.platforms.mist.client import get_apisession
from hpe_networking_mcp.platforms.mist.client import process_response, handle_network_error
from hpe_networking_mcp.platforms.mist.client import format_response

from hpe_networking_mcp.middleware.elicitation import elicitation_handler
from hpe_networking_mcp.platforms.mist._registry import mcp
from loguru import logger

from pydantic import Field
from typing import Annotated
from uuid import UUID
from enum import Enum


class Object_type(Enum):
    DEVICES = "devices"
    EVPN_TOPOLOGIES = "evpn_topologies"
    PSKS = "psks"
    WEBHOOKS = "webhooks"
    WLANS = "wlans"
    WXRULES = "wxrules"
    WXTAGS = "wxtags"


class Action_type(Enum):
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"


@mcp.tool(
    name="mist_change_site_configuration_objects",
    description="""Update, create or delete a configuration object for a specified site.\n
IMPORTANT:\n
To ensure that you are not missing any existing attributes when updating the configuration object, make sure to :\n
1. retrieve the current configuration object using the tools `mist_get_configuration_objects` to retrieve the object defined at the site level\n
2. Modify the desired attributes\n
3. Use this tool to update the configuration object with the modified attributes\n
\n
When creating a new configuration object, make sure to use the`mist_get_configuration_object_schema` tool to discover the attributes of the configuration object and which of them are required\n""",
    tags={"write_delete"},
    annotations={
        "title": "Change site configuration objects",
        "readOnlyHint": False,
        "destructiveHint": True,
        "openWorldHint": True,
        "idempotentHint": False,
    },
)
async def change_site_configuration_objects(
    action_type: Annotated[
        Action_type,
        Field(
            description="Whether the action is creating a new object, updating an existing one, or deleting an existing one. When updating or deleting, the object_id parameter must be provided."
        ),
    ],
    site_id: Annotated[UUID, Field(description="""Site ID""")],
    object_type: Annotated[
        Object_type,
        Field(
            description="""Type of configuration object to create, update, or delete"""
        ),
    ],
    payload: Annotated[
        dict,
        Field(
            description="""JSON payload of the configuration object to update or create. Required when action_type is 'create' or 'update'. When updating an existing object, make sure to include all required attributes in the payload. It is recommended to first retrieve the current configuration object using the`mist_get_configuration_objects` tool and use the retrieved object as a base for the payload, modifying only the desired attributes"""
        ),
    ],
    object_id: Annotated[
        UUID,
        Field(
            description="""ID of the specific configuration object to update or delete. Required when action_type is 'update' or 'delete'""",
            default=None,
        ),
    ],
    ctx: Context,
) -> dict | list | str:
    """Update, create or delete a configuration object for a specified site."""

    logger.debug("Tool change_site_configuration_objects called")
    logger.debug(
        "Input Parameters: site_id: %s, object_type: %s, payload: %s, object_id: %s",
        site_id,
        object_type,
        payload,
        object_id,
    )

    apisession, response_format = await get_apisession()

    action_wording = "create a new"
    if action_type == Action_type.UPDATE:
        if not object_id:
            raise ToolError({"status_code": 400, "message": "object_id parameter is required when action_type is 'update'."})
        action_wording = "update an existing"
    elif action_type == Action_type.DELETE:
        if not object_id:
            raise ToolError({"status_code": 400, "message": "object_id parameter is required when action_type is 'delete'."})
        action_wording = "delete an existing"

    if ctx:
        try:
            elicitation_response = await elicitation_handler(
                message=f"""The LLM wants to {action_wording} {object_type.value}. Do you accept to trigger the API call?""",
                ctx=ctx,
            )
        except Exception as exc:
            raise ToolError(
                {
                    "status_code": 400,
                    "message": (
                        "AI App does not support elicitation. You cannot use it to "
                        "modify configuration objects. Please use the Mist API "
                        "directly or use an AI App with elicitation support to "
                        "modify configuration objects."
                    ),
                }
            ) from exc

        if elicitation_response.action == "decline":
            return {"message": "Action declined by user."}
        elif elicitation_response.action == "cancel":
            return {"message": "Action canceled by user."}

    try:
        match object_type.value:
            case "devices":
                if action_type.value == "update":
                    response = mistapi.api.v1.sites.devices.updateSiteDevice(apisession, site_id=str(site_id), device_id=str(object_id), body=payload)
                    await process_response(response)
            case "evpn_topologies":
                if action_type.value == "update":
                    response = mistapi.api.v1.sites.evpn_topologies.updateSiteEvpnTopology(apisession, site_id=str(site_id), evpn_topology_id=str(object_id), body=payload)
                    await process_response(response)
                elif action_type.value == "create":
                    response = mistapi.api.v1.sites.evpn_topologies.createSiteEvpnTopology(apisession, site_id=str(site_id), body=payload)
                    await process_response(response)
                else:
                    response = mistapi.api.v1.sites.evpn_topologies.deleteSiteEvpnTopology(apisession, site_id=str(site_id), evpn_topology_id=str(object_id))
                    await process_response(response)
            case "psks":
                if action_type.value == "update":
                    response = mistapi.api.v1.sites.psks.updateSitePsk(apisession, site_id=str(site_id), psk_id=str(object_id), body=payload)
                    await process_response(response)
                elif action_type.value == "create":
                    response = mistapi.api.v1.sites.psks.createSitePsk(apisession, site_id=str(site_id), body=payload)
                    await process_response(response)
                else:
                    response = mistapi.api.v1.sites.psks.deleteSitePsk(apisession, site_id=str(site_id), psk_id=str(object_id))
                    await process_response(response)
            case "webhooks":
                if action_type.value == "update":
                    response = mistapi.api.v1.sites.webhooks.updateSiteWebhook(apisession, site_id=str(site_id), webhook_id=str(object_id), body=payload)
                    await process_response(response)
                elif action_type.value == "create":
                    response = mistapi.api.v1.sites.webhooks.createSiteWebhook(apisession, site_id=str(site_id), body=payload)
                    await process_response(response)
                else:
                    response = mistapi.api.v1.sites.webhooks.deleteSiteWebhook(apisession, site_id=str(site_id), webhook_id=str(object_id))
                    await process_response(response)
            case "wlans":
                if action_type.value == "update":
                    response = mistapi.api.v1.sites.wlans.updateSiteWlan(apisession, site_id=str(site_id), wlan_id=str(object_id), body=payload)
                    await process_response(response)
                elif action_type.value == "create":
                    response = mistapi.api.v1.sites.wlans.createSiteWlan(apisession, site_id=str(site_id), body=payload)
                    await process_response(response)
                else:
                    response = mistapi.api.v1.sites.wlans.deleteSiteWlan(apisession, site_id=str(site_id), wlan_id=str(object_id))
                    await process_response(response)
            case "wxrules":
                if action_type.value == "update":
                    response = mistapi.api.v1.sites.wxrules.updateSiteWxRule(apisession, site_id=str(site_id), wxrule_id=str(object_id), body=payload)
                    await process_response(response)
                elif action_type.value == "create":
                    response = mistapi.api.v1.sites.wxrules.createSiteWxRule(apisession, site_id=str(site_id), body=payload)
                    await process_response(response)
                else:
                    response = mistapi.api.v1.sites.wxrules.deleteSiteWxRule(apisession, site_id=str(site_id), wxrule_id=str(object_id))
                    await process_response(response)
            case "wxtags":
                if action_type.value == "update":
                    response = mistapi.api.v1.sites.wxtags.updateSiteWxTag(apisession, site_id=str(site_id), wxtag_id=str(object_id), body=payload)
                    await process_response(response)
                elif action_type.value == "create":
                    response = mistapi.api.v1.sites.wxtags.createSiteWxTag(apisession, site_id=str(site_id), body=payload)
                    await process_response(response)
                else:
                    response = mistapi.api.v1.sites.wxtags.deleteSiteWxTag(apisession, site_id=str(site_id), wxtag_id=str(object_id))
                    await process_response(response)

            case _:
                raise ToolError(
                    {
                        "status_code": 400,
                        "message": f"Invalid object_type: {object_type.value}. Valid values are: {[e.value for e in Object_type]}",
                    }
                )

    except ToolError:
        raise
    except Exception as _exc:
        await handle_network_error(_exc)

    return format_response(response, response_format)
