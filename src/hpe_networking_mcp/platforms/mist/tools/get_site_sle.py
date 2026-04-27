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

from hpe_networking_mcp.platforms.mist._registry import tool
from hpe_networking_mcp.platforms.mist.client import (
    format_response,
    get_apisession,
    handle_network_error,
    process_response,
)


class Scope(Enum):
    CLIENT = "client"
    AP = "ap"
    GATEWAY = "gateway"
    MXEDGE = "mxedge"
    SWITCH = "switch"
    SITE = "site"


class Object_type(Enum):
    SUMMARY = "summary"
    IMPACT_SUMMARY = "impact_summary"
    SUMMARY_TREND = "summary_trend"
    IMPACTED_APPLICATIONS = "impacted_applications"
    IMPACTED_APS = "impacted_aps"
    IMPACTED_GATEWAYS = "impacted_gateways"
    IMPACTED_INTERFACES = "impacted_interfaces"
    IMPACTED_SWITCHES = "impacted_switches"
    IMPACTED_WIRELESS_CLIENTS = "impacted_wireless_clients"
    IMPACTED_WIRED_CLIENTS = "impacted_wired_clients"
    IMPACTED_CHASSIS = "impacted_chassis"
    HISTOGRAM = "histogram"
    CLASSIFIER_SUMMARY_TREND = "classifier_summary_trend"
    THRESHOLD = "threshold"


@tool(
    name="mist_get_site_sle",
    description=(
        "Provides Information about the Service Level "
        "Expectations (SLEs) for a given site. The SLEs are "
        "derived from the insight metrics and can be used to "
        "monitor the network user experience of the site "
        "against the defined SLEs"
    ),
    tags={"sles"},
    annotations={
        "title": "Get site sle",
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": True,
        "idempotentHint": True,
    },
)
async def get_site_sle(
    ctx: Context,
    site_id: Annotated[UUID, Field(description="Site ID")],
    scope: Annotated[
        Scope,
        Field(
            description=(
                "Scope of the SLEs to retrieve. Can be 'client', 'ap', 'gateway', 'mxedge', 'switch' or 'site'"
            )
        ),
    ],
    scope_id: Annotated[str, Field(description="ID of the Mist Scope")],
    metric: Annotated[
        str,
        Field(
            description=(
                "Name of the SLE metric to retrieve "
                "(e.g. `wifi-coverage`, `wired-throughput`, "
                "`wan-link-health`). The valid set is "
                "tenant-specific and per-scope. Discover the "
                "available metrics for the chosen scope via "
                "`mist_list_site_sle_info` with "
                "`query_type=metrics`. Note: the broader "
                "`mist_get_constants(object_type='insight_metrics')` "
                "is a DIFFERENT set (insight time-series) — do NOT "
                "use it for SLE metrics."
            )
        ),
    ],
    object_type: Annotated[
        Object_type,
        Field(description=("Type of object to retrieve metrics for")),
    ],
    start: Annotated[
        int,
        Field(
            description="Start of time range (epoch seconds)",
            default=None,
        ),
    ],
    end: Annotated[
        int,
        Field(
            description="End of time range (epoch seconds)",
            default=None,
        ),
    ],
    classifier: Annotated[
        str,
        Field(
            description=("Classifier name. Required when object_type is 'classifier_summary_trend'"),
            default=None,
        ),
    ],
    duration: Annotated[
        str,
        Field(
            description="Time range duration (e.g. 1d, 1h, 10m)",
            default=None,
        ),
    ],
) -> dict | list | str:
    """Provides Information about the SLEs for a given site."""

    logger.debug("Tool get_site_sle called")
    logger.debug(
        "Input Parameters: site_id: %s, scope: %s, "
        "scope_id: %s, metric: %s, object_type: %s, "
        "start: %s, end: %s, classifier: %s, duration: %s",
        site_id,
        scope,
        scope_id,
        metric,
        object_type,
        start,
        end,
        classifier,
        duration,
    )

    apisession, response_format = await get_apisession(ctx)

    try:
        if object_type.value == "classifier_summary_trend" and not classifier:
            raise ToolError(
                {
                    "status_code": 400,
                    "message": ('`classifier` parameter is required when `test` is "classifier_summary_trend".'),
                }
            )

        match object_type.value:
            case "summary":
                response = mistapi.api.v1.sites.sle.getSiteSleSummary(
                    apisession,
                    site_id=str(site_id),
                    scope=scope.value,
                    scope_id=scope_id,
                    metric=metric,
                    start=str(start) if start else None,
                    end=str(end) if end else None,
                    duration=(duration if duration else None),
                )
                await process_response(response)
            case "impact_summary":
                response = mistapi.api.v1.sites.sle.getSiteSleImpactSummary(
                    apisession,
                    site_id=str(site_id),
                    scope=scope.value,
                    scope_id=scope_id,
                    metric=metric,
                    start=str(start) if start else None,
                    end=str(end) if end else None,
                    duration=(duration if duration else None),
                )
                await process_response(response)
            case "summary_trend":
                response = mistapi.api.v1.sites.sle.getSiteSleSummaryTrend(
                    apisession,
                    site_id=str(site_id),
                    scope=scope.value,
                    scope_id=scope_id,
                    metric=metric,
                    start=str(start) if start else None,
                    end=str(end) if end else None,
                    duration=(duration if duration else None),
                )
                await process_response(response)
            case "impacted_applications":
                response = mistapi.api.v1.sites.sle.listSiteSleImpactedApplications(
                    apisession,
                    site_id=str(site_id),
                    scope=scope.value,
                    scope_id=scope_id,
                    metric=metric,
                    start=str(start) if start else None,
                    end=str(end) if end else None,
                    duration=(duration if duration else None),
                )
                await process_response(response)
            case "impacted_aps":
                response = mistapi.api.v1.sites.sle.listSiteSleImpactedAps(
                    apisession,
                    site_id=str(site_id),
                    scope=scope.value,
                    scope_id=scope_id,
                    metric=metric,
                    start=str(start) if start else None,
                    end=str(end) if end else None,
                    duration=(duration if duration else None),
                )
                await process_response(response)
            case "impacted_gateways":
                response = mistapi.api.v1.sites.sle.listSiteSleImpactedGateways(
                    apisession,
                    site_id=str(site_id),
                    scope=scope.value,
                    scope_id=scope_id,
                    metric=metric,
                    start=str(start) if start else None,
                    end=str(end) if end else None,
                    duration=(duration if duration else None),
                )
                await process_response(response)
            case "impacted_interfaces":
                response = mistapi.api.v1.sites.sle.listSiteSleImpactedInterfaces(
                    apisession,
                    site_id=str(site_id),
                    scope=scope.value,
                    scope_id=scope_id,
                    metric=metric,
                    start=str(start) if start else None,
                    end=str(end) if end else None,
                    duration=(duration if duration else None),
                )
                await process_response(response)
            case "impacted_switches":
                response = mistapi.api.v1.sites.sle.listSiteSleImpactedSwitches(
                    apisession,
                    site_id=str(site_id),
                    scope=scope.value,
                    scope_id=scope_id,
                    metric=metric,
                    start=str(start) if start else None,
                    end=str(end) if end else None,
                    duration=(duration if duration else None),
                )
                await process_response(response)
            case "impacted_wireless_clients":
                response = mistapi.api.v1.sites.sle.listSiteSleImpactedWirelessClients(
                    apisession,
                    site_id=str(site_id),
                    scope=scope.value,
                    scope_id=scope_id,
                    metric=metric,
                    start=str(start) if start else None,
                    end=str(end) if end else None,
                    duration=(duration if duration else None),
                )
                await process_response(response)
            case "impacted_wired_clients":
                response = mistapi.api.v1.sites.sle.listSiteSleImpactedWiredClients(
                    apisession,
                    site_id=str(site_id),
                    scope=scope.value,
                    scope_id=scope_id,
                    metric=metric,
                    start=str(start) if start else None,
                    end=str(end) if end else None,
                    duration=(duration if duration else None),
                )
                await process_response(response)
            case "impacted_chassis":
                response = mistapi.api.v1.sites.sle.listSiteSleImpactedChassis(
                    apisession,
                    site_id=str(site_id),
                    scope=scope.value,
                    scope_id=scope_id,
                    metric=metric,
                    start=str(start) if start else None,
                    end=str(end) if end else None,
                    duration=(duration if duration else None),
                )
                await process_response(response)
            case "histogram":
                response = mistapi.api.v1.sites.sle.getSiteSleHistogram(
                    apisession,
                    site_id=str(site_id),
                    scope=scope.value,
                    scope_id=scope_id,
                    metric=metric,
                    start=str(start) if start else None,
                    end=str(end) if end else None,
                    duration=(duration if duration else None),
                )
                await process_response(response)
            case "classifier_summary_trend":
                response = mistapi.api.v1.sites.sle.getSiteSleClassifierSummaryTrend(
                    apisession,
                    site_id=str(site_id),
                    scope=scope.value,
                    scope_id=scope_id,
                    metric=metric,
                    classifier=classifier,
                    start=str(start) if start else None,
                    end=str(end) if end else None,
                    duration=(duration if duration else None),
                )
                await process_response(response)
            case "threshold":
                response = mistapi.api.v1.sites.sle.getSiteSleThreshold(
                    apisession,
                    site_id=str(site_id),
                    scope=scope.value,
                    scope_id=scope_id,
                    metric=metric,
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

    return format_response(response, response_format)
