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

import mistapi
from fastmcp.exceptions import ToolError
from loguru import logger
from pydantic import Field

from hpe_networking_mcp.platforms.mist._registry import tool
from hpe_networking_mcp.platforms.mist.client import (
    format_response,
    get_apisession,
    handle_network_error,
    process_response,
)


class Object_type(Enum):
    FINGERPRINT_TYPES = "fingerprint_types"
    INSIGHT_METRICS = "insight_metrics"
    LICENSE_TYPES = "license_types"
    WEBHOOK_TOPICS = "webhook_topics"
    DEVICE_MODELS = "device_models"
    DEVICE_EVENTS = "device_events"
    MXEDGE_MODELS = "mxedge_models"
    ALARM_DEFINITIONS = "alarm_definitions"
    CLIENT_EVENTS = "client_events"
    MXEDGE_EVENTS = "mxedge_events"
    NAC_EVENTS = "nac_events"


@tool(
    name="mist_get_constants",
    description=(
        "Retrieve Mist platform constants including insight "
        "metrics, webhook topics, alarm definitions, device "
        "models, events definitions, and license types. Use this "
        "to understand available options and configurations for "
        "the Mist API."
    ),
    tags={"constants"},
    annotations={
        "title": "Get constants",
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": True,
        "idempotentHint": True,
    },
)
async def get_constants(
    object_type: Annotated[
        Object_type,
        Field(
            description=(
                "Type of constant to retrieve: "
                "fingerprint_types, insight_metrics, "
                "license_types, webhook_topics, device_models, "
                "device_events, mxedge_models, "
                "alarm_definitions, client_events, "
                "mxedge_events, or nac_events"
            )
        ),
    ],
) -> dict | list | str:
    """Retrieve Mist platform constants."""

    logger.debug("Tool get_constants called")
    logger.debug("Input Parameters: object_type: %s", object_type)

    apisession, response_format = await get_apisession()

    try:
        match object_type.value:
            case "fingerprint_types":
                response = mistapi.api.v1.const.fingerprint_types.listFingerprintTypes(apisession)
                await process_response(response)
            case "insight_metrics":
                response = mistapi.api.v1.const.insight_metrics.listInsightMetrics(apisession)
                await process_response(response)
            case "license_types":
                response = mistapi.api.v1.const.license_types.listLicenseTypes(apisession)
                await process_response(response)
            case "webhook_topics":
                response = mistapi.api.v1.const.webhook_topics.listWebhookTopics(apisession)
                await process_response(response)
            case "device_models":
                response = mistapi.api.v1.const.device_models.listDeviceModels(apisession)
                await process_response(response)
            case "device_events":
                response = mistapi.api.v1.const.device_events.listDeviceEventsDefinitions(apisession)
                await process_response(response)
            case "mxedge_models":
                response = mistapi.api.v1.const.mxedge_models.listMxEdgeModels(apisession)
                await process_response(response)
            case "alarm_definitions":
                response = mistapi.api.v1.const.alarm_defs.listAlarmDefinitions(apisession)
                await process_response(response)
            case "client_events":
                response = mistapi.api.v1.const.client_events.listClientEventsDefinitions(apisession)
                await process_response(response)
            case "mxedge_events":
                response = mistapi.api.v1.const.mxedge_events.listMxEdgeEventsDefinitions(apisession)
                await process_response(response)
            case "nac_events":
                response = mistapi.api.v1.const.nac_events.listNacEventsDefinitions(apisession)
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

    return format_response(response, response_format)
