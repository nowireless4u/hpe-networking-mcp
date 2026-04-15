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
from hpe_networking_mcp.platforms.mist.tools.guardrails import validate_site_write


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
    description=(
        "Update, create or delete a configuration object for a "
        "specified site.\n"
        "\nIMPORTANT:\n"
        "To ensure that you are not missing any existing attributes "
        "when updating the configuration object, make sure to:\n"
        "1. retrieve the current configuration object using the "
        "tools `mist_get_configuration_objects` to retrieve the "
        "object defined at the site level\n"
        "2. Modify the desired attributes\n"
        "3. Use this tool to update the configuration object with "
        "the modified attributes\n"
        "\nWhen creating a new configuration object, make sure to "
        "use the `mist_get_configuration_object_schema` tool to "
        "discover the attributes of the configuration object and "
        "which of them are required\n"
    ),
    tags={"mist_write_delete"},
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
            description=(
                "Whether the action is creating a new object, "
                "updating an existing one, or deleting an "
                "existing one. When updating or deleting, the "
                "object_id parameter must be provided."
            )
        ),
    ],
    site_id: Annotated[UUID, Field(description="Site ID")],
    object_type: Annotated[
        Object_type,
        Field(description=("Type of configuration object to create, update, or delete")),
    ],
    payload: Annotated[
        dict,
        Field(
            description=(
                "JSON payload of the configuration object to "
                "update or create. Required when action_type is "
                "'create' or 'update'. When updating an existing "
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
                "ID of the specific configuration object to "
                "update or delete. Required when action_type is "
                "'update' or 'delete'"
            ),
            default=None,
        ),
    ],
    ctx: Context,
    confirmed: Annotated[
        bool,
        Field(
            description="Set to true when the user has confirmed the operation in chat. Required for update/delete.",
            default=False,
        ),
    ],
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

    guardrails = validate_site_write(object_type.value, action_type.value, payload)
    guardrail_notice = ""
    if guardrails.warnings:
        guardrail_notice = "\n\n" + "\n".join(guardrails.warnings[:3])

    # Confirm with user for update and delete operations only
    if action_type != Action_type.CREATE and not confirmed:
        elicitation_response = await elicitation_handler(
            message=(
                f"The LLM wants to {action_wording} {object_type.value}. "
                f"Do you accept to trigger the API call?{guardrail_notice}"
            ),
            ctx=ctx,
        )
        if elicitation_response.action == "decline":
            if await ctx.get_state("elicitation_mode") == "chat_confirm":
                return {
                    "status": "confirmation_required",
                    "message": (
                        f"This operation will {action_wording} {object_type.value}. "
                        "Please confirm with the user before proceeding. "
                        "Call this tool again with the same parameters and confirmed=true after the user confirms."
                    ),
                }
            return {"message": "Action declined by user."}
        elif elicitation_response.action == "cancel":
            return {"message": "Action canceled by user."}

    site = str(site_id)
    obj = str(object_id)

    try:
        match object_type.value:
            case "devices":
                if action_type.value == "update":
                    response = mistapi.api.v1.sites.devices.updateSiteDevice(
                        apisession,
                        site_id=site,
                        device_id=obj,
                        body=payload,
                    )
                    await process_response(response)
            case "evpn_topologies":
                if action_type.value == "update":
                    response = mistapi.api.v1.sites.evpn_topologies.updateSiteEvpnTopology(
                        apisession,
                        site_id=site,
                        evpn_topology_id=obj,
                        body=payload,
                    )
                    await process_response(response)
                elif action_type.value == "create":
                    response = mistapi.api.v1.sites.evpn_topologies.createSiteEvpnTopology(
                        apisession,
                        site_id=site,
                        body=payload,
                    )
                    await process_response(response)
                else:
                    response = mistapi.api.v1.sites.evpn_topologies.deleteSiteEvpnTopology(
                        apisession,
                        site_id=site,
                        evpn_topology_id=obj,
                    )
                    await process_response(response)
            case "psks":
                if action_type.value == "update":
                    response = mistapi.api.v1.sites.psks.updateSitePsk(
                        apisession,
                        site_id=site,
                        psk_id=obj,
                        body=payload,
                    )
                    await process_response(response)
                elif action_type.value == "create":
                    response = mistapi.api.v1.sites.psks.createSitePsk(
                        apisession,
                        site_id=site,
                        body=payload,
                    )
                    await process_response(response)
                else:
                    response = mistapi.api.v1.sites.psks.deleteSitePsk(
                        apisession,
                        site_id=site,
                        psk_id=obj,
                    )
                    await process_response(response)
            case "webhooks":
                if action_type.value == "update":
                    response = mistapi.api.v1.sites.webhooks.updateSiteWebhook(
                        apisession,
                        site_id=site,
                        webhook_id=obj,
                        body=payload,
                    )
                    await process_response(response)
                elif action_type.value == "create":
                    response = mistapi.api.v1.sites.webhooks.createSiteWebhook(
                        apisession,
                        site_id=site,
                        body=payload,
                    )
                    await process_response(response)
                else:
                    response = mistapi.api.v1.sites.webhooks.deleteSiteWebhook(
                        apisession,
                        site_id=site,
                        webhook_id=obj,
                    )
                    await process_response(response)
            case "wlans":
                if action_type.value == "update":
                    response = mistapi.api.v1.sites.wlans.updateSiteWlan(
                        apisession,
                        site_id=site,
                        wlan_id=obj,
                        body=payload,
                    )
                    await process_response(response)
                elif action_type.value == "create":
                    response = mistapi.api.v1.sites.wlans.createSiteWlan(
                        apisession,
                        site_id=site,
                        body=payload,
                    )
                    await process_response(response)
                else:
                    response = mistapi.api.v1.sites.wlans.deleteSiteWlan(
                        apisession,
                        site_id=site,
                        wlan_id=obj,
                    )
                    await process_response(response)
            case "wxrules":
                if action_type.value == "update":
                    response = mistapi.api.v1.sites.wxrules.updateSiteWxRule(
                        apisession,
                        site_id=site,
                        wxrule_id=obj,
                        body=payload,
                    )
                    await process_response(response)
                elif action_type.value == "create":
                    response = mistapi.api.v1.sites.wxrules.createSiteWxRule(
                        apisession,
                        site_id=site,
                        body=payload,
                    )
                    await process_response(response)
                else:
                    response = mistapi.api.v1.sites.wxrules.deleteSiteWxRule(
                        apisession,
                        site_id=site,
                        wxrule_id=obj,
                    )
                    await process_response(response)
            case "wxtags":
                if action_type.value == "update":
                    response = mistapi.api.v1.sites.wxtags.updateSiteWxTag(
                        apisession,
                        site_id=site,
                        wxtag_id=obj,
                        body=payload,
                    )
                    await process_response(response)
                elif action_type.value == "create":
                    response = mistapi.api.v1.sites.wxtags.createSiteWxTag(
                        apisession,
                        site_id=site,
                        body=payload,
                    )
                    await process_response(response)
                else:
                    response = mistapi.api.v1.sites.wxtags.deleteSiteWxTag(
                        apisession,
                        site_id=site,
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
