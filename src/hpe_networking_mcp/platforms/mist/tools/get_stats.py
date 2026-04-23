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


class Stats_type(Enum):
    ORG = "org"
    SITES = "sites"
    ORG_MXEDGES = "org_mxedges"
    ORG_DEVICES = "org_devices"
    ORG_BGP = "org_bgp"
    ORG_OSPF = "org_ospf"
    ORG_PEER_PATHS = "org_peer_paths"
    ORG_PORTS = "org_ports"
    SITE_MXEDGES = "site_mxedges"
    SITE_WIRELESS_CLIENTS = "site_wireless_clients"
    SITE_DEVICES = "site_devices"
    SITE_BGP = "site_bgp"
    SITE_OSPF = "site_ospf"
    SITE_PORTS = "site_ports"


class Device_type(Enum):
    AP = "ap"
    SWITCH = "switch"
    GATEWAY = "gateway"


@tool(
    name="mist_get_stats",
    description=(
        "Use this tool to retrieve various statistics from "
        "Mist infrastructure including organization and "
        "site-level data. Supports stats for MxEdges, "
        "devices, BGP, OSPF, peer paths, ports, and wireless "
        "clients. Use object_id to filter results by device "
        "ID or MAC address (format varies by stats_type)."
    ),
    tags={"stats"},
    annotations={
        "title": "Get stats",
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": True,
        "idempotentHint": True,
    },
)
async def get_stats(
    stats_type: Annotated[
        Stats_type,
        Field(
            description=(
                "Type of statistics to retrieve: org, sites, "
                "org_mxedges, org_wireless_clients, "
                "org_devices, org_bgp, org_ospf, "
                "org_peer_paths, org_ports, site_mxedges, "
                "site_wireless_clients, site_devices, "
                "site_bgp, site_ospf, or site_ports"
            )
        ),
    ],
    org_id: Annotated[UUID, Field(description="Organization ID")],
    site_id: Annotated[UUID, Field(description="Site ID", default=None)],
    device_type: Annotated[
        Device_type,
        Field(
            description=(
                "Device type filter (ap, switch, gateway). "
                "Only applicable when stats_type is "
                "org_devices or site_devices"
            ),
            default=None,
        ),
    ],
    object_id: Annotated[
        str,
        Field(
            description=(
                "Filter by specific object ID or MAC address "
                "(format depends on stats_type): Mist Edge "
                "ID for mxedges, device ID for devices, MAC "
                "address for BGP/OSPF/peer_paths/ports, "
                "client MAC for wireless_clients, site ID "
                "for sites"
            ),
            default=None,
        ),
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
    limit: Annotated[
        int,
        Field(
            description="Max number of results per page",
            default=20,
        ),
    ] = 20,
) -> dict | list | str:
    """Retrieve various statistics from Mist infrastructure."""

    logger.debug("Tool get_stats called")
    logger.debug(
        "Input Parameters: stats_type: %s, org_id: %s, "
        "site_id: %s, device_type: %s, object_id: %s, "
        "start: %s, end: %s, limit: %s",
        stats_type,
        org_id,
        site_id,
        device_type,
        object_id,
        start,
        end,
        limit,
    )

    apisession, response_format = await get_apisession()

    try:
        object_type = stats_type

        site_required_types = [
            "site_mxedges",
            "site_wireless_clients",
            "site_devices",
            "site_bgp",
            "site_ospf",
            "site_ports",
        ]
        if object_type.value in site_required_types and not site_id:
            raise ToolError(
                {
                    "status_code": 400,
                    "message": (f'`site_id` parameter is required when `stats_type` is "{object_type.value}".'),
                }
            )

        if device_type and stats_type.value not in [
            "org_devices",
            "site_devices",
        ]:
            raise ToolError(
                {
                    "status_code": 400,
                    "message": (
                        "`device_type` parameter can only be "
                        "used when `stats_type` is in "
                        '"org_devices", "site_devices".'
                    ),
                }
            )

        match object_type.value:
            case "org":
                response = mistapi.api.v1.orgs.stats.getOrgStats(
                    apisession,
                    org_id=str(org_id),
                    start=str(start) if start else None,
                    end=str(end) if end else None,
                )
                await process_response(response)
            case "sites":
                if object_id:
                    response = mistapi.api.v1.sites.stats.getSiteStats(
                        apisession,
                        site_id=str(object_id),
                    )
                    await process_response(response)
                else:
                    response = mistapi.api.v1.orgs.stats.listOrgSiteStats(
                        apisession,
                        org_id=str(org_id),
                        start=(str(start) if start else None),
                        end=str(end) if end else None,
                        limit=limit,
                    )
                    await process_response(response)
            case "org_mxedges":
                if object_id:
                    response = mistapi.api.v1.orgs.stats.getOrgMxEdgeStats(
                        apisession,
                        org_id=str(org_id),
                        mxedge_id=str(object_id),
                    )
                    await process_response(response)
                else:
                    response = mistapi.api.v1.orgs.stats.listOrgMxEdgesStats(
                        apisession,
                        org_id=str(org_id),
                        start=(str(start) if start else None),
                        end=str(end) if end else None,
                        limit=limit,
                    )
                    await process_response(response)
            case "org_devices":
                response = mistapi.api.v1.orgs.stats.listOrgDevicesStats(
                    apisession,
                    org_id=str(org_id),
                    type=(device_type.value if device_type else None),
                    start=str(start) if start else None,
                    end=str(end) if end else None,
                    mac=str(object_id),
                    limit=limit,
                )
                await process_response(response)
            case "org_bgp":
                response = mistapi.api.v1.orgs.stats.searchOrgBgpStats(
                    apisession,
                    org_id=str(org_id),
                    start=str(start) if start else None,
                    end=str(end) if end else None,
                    mac=(str(object_id) if object_id else None),
                    limit=limit,
                )
                await process_response(response)
            case "org_ospf":
                response = mistapi.api.v1.orgs.stats.searchOrgOspfStats(
                    apisession,
                    org_id=str(org_id),
                    start=str(start) if start else None,
                    end=str(end) if end else None,
                    mac=(str(object_id) if object_id else None),
                )
                await process_response(response)
            case "org_peer_paths":
                response = mistapi.api.v1.orgs.stats.searchOrgPeerPathStats(
                    apisession,
                    org_id=str(org_id),
                    start=str(start) if start else None,
                    end=str(end) if end else None,
                    mac=(str(object_id) if object_id else None),
                    limit=limit,
                )
                await process_response(response)
            case "org_ports":
                response = mistapi.api.v1.orgs.stats.searchOrgSwOrGwPorts(
                    apisession,
                    org_id=str(org_id),
                    mac=(str(object_id) if object_id else None),
                    limit=limit,
                )
                await process_response(response)
            case "site_mxedges":
                if object_id:
                    response = mistapi.api.v1.sites.stats.getSiteMxEdgeStats(
                        apisession,
                        site_id=str(site_id),
                        start=(str(start) if start else None),
                        end=str(end) if end else None,
                        mxedge_id=str(object_id),
                    )
                    await process_response(response)
                else:
                    response = mistapi.api.v1.sites.stats.listSiteMxEdgesStats(
                        apisession,
                        site_id=str(site_id),
                        start=(str(start) if start else None),
                        end=str(end) if end else None,
                        limit=limit,
                    )
                    await process_response(response)
            case "site_wireless_clients":
                if object_id:
                    response = mistapi.api.v1.sites.stats.getSiteWirelessClientStats(
                        apisession,
                        site_id=str(site_id),
                        client_mac=str(object_id),
                    )
                    await process_response(response)
                else:
                    response = mistapi.api.v1.sites.stats.listSiteWirelessClientsStats(
                        apisession,
                        site_id=str(site_id),
                        start=(str(start) if start else None),
                        end=str(end) if end else None,
                        limit=limit,
                    )
                    await process_response(response)
            case "site_devices":
                if object_id:
                    response = mistapi.api.v1.sites.stats.getSiteDeviceStats(
                        apisession,
                        site_id=str(site_id),
                        device_id=str(object_id),
                    )
                    await process_response(response)
                else:
                    response = mistapi.api.v1.sites.stats.listSiteDevicesStats(
                        apisession,
                        site_id=str(site_id),
                        type=(device_type.value if device_type else None),
                        limit=limit,
                    )
                    await process_response(response)
            case "site_bgp":
                response = mistapi.api.v1.sites.stats.searchSiteBgpStats(
                    apisession,
                    site_id=str(site_id),
                    start=str(start) if start else None,
                    end=str(end) if end else None,
                    mac=(str(object_id) if object_id else None),
                    limit=limit,
                )
                await process_response(response)
            case "site_ospf":
                response = mistapi.api.v1.sites.stats.searchSiteOspfStats(
                    apisession,
                    site_id=str(site_id),
                    start=str(start) if start else None,
                    end=str(end) if end else None,
                    mac=(str(object_id) if object_id else None),
                    limit=limit,
                )
                await process_response(response)
            case "site_ports":
                response = mistapi.api.v1.sites.stats.searchSiteSwOrGwPorts(
                    apisession,
                    site_id=str(site_id),
                    mac=(str(object_id) if object_id else None),
                    limit=limit,
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
                            f"{[e.value for e in Stats_type]}"
                        ),
                    }
                )

    except ToolError:
        raise
    except Exception as _exc:
        await handle_network_error(_exc)

    return format_response(response, response_format)
