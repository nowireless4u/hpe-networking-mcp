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


class Event_source(Enum):
    DEVICE = "device"
    MXEDGE = "mxedge"
    WAN_CLIENT = "wan_client"
    WIRELESS_CLIENT = "wireless_client"
    NAC_CLIENT = "nac_client"
    ROAMING = "roaming"
    ROGUE = "rogue"


@tool(
    name="mist_search_events",
    description=(
        "Search for events across an organization or site "
        "with flexible filtering options.\n"
        "\nThis tool queries events from various sources "
        "including devices, MX Edge instances, and clients. "
        "You can:\n"
        "- Filter by time range using `start` and `end` "
        "(epoch seconds)\n"
        "- Filter by event type (use `mist_get_constants` "
        "tool first to discover available event types)\n"
        "- Apply source-specific filters (MAC address, "
        "text search, SSID, etc.)\n"
        "\nIMPORTANT: Always specify an `event_type` to "
        "limit results. Use `mist_get_constants` with:\n"
        "- `object_type=device_events` for device events\n"
        "- `object_type=mxedge_events` for MX Edge events\n"
        "- `object_type=client_events` for WAN/wireless "
        "client events\n"
        "- `object_type=nac_events` for NAC client events"
    ),
    tags={"events"},
    annotations={
        "title": "Search events",
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": True,
        "idempotentHint": True,
    },
)
async def search_events(
    ctx: Context,
    event_source: Annotated[
        Event_source,
        Field(
            description=(
                "Event source type: device, mxedge, "
                "wan_client, wireless_client, nac_client, "
                "roaming (requires site_id), or rogue "
                "(requires site_id)"
            )
        ),
    ],
    org_id: Annotated[UUID, Field(description="Organization ID")],
    event_type: Annotated[
        str,
        Field(
            description=(
                "Comma-separated event types to filter by. "
                "The list of possible event types can be "
                "obtained with the `mist_get_constants` tool "
                "with `object_type=device_events` when "
                "`event_source` is `device`, "
                "`object_type=mxedge_events` when "
                "`event_source` is `mxedge`, "
                "`object_type=client_events` when "
                "`event_source` is `wan_client` or "
                "`wireless_client`, `object_type=nac_events` "
                "when `event_source` is `nac_client`"
            ),
            default=None,
        ),
    ],
    site_id: Annotated[UUID, Field(description="Site ID", default=None)],
    mac: Annotated[
        str,
        Field(
            description=("MAC address to filter by (device/WAN client/NAC client/rogue events only)"),
            default=None,
        ),
    ],
    text: Annotated[
        str,
        Field(
            description=("Text search in event details (device/NAC client events only)"),
            default=None,
        ),
    ],
    ssid: Annotated[
        str,
        Field(
            description=("SSID filter (wireless_client/nac_client/rogue events only)"),
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
    """Search for events across an org or site."""

    logger.debug("Tool search_events called")
    logger.debug(
        "Input Parameters: event_source: %s, org_id: %s, "
        "event_type: %s, site_id: %s, mac: %s, text: %s, "
        "ssid: %s, start: %s, end: %s, limit: %s",
        event_source,
        org_id,
        event_type,
        site_id,
        mac,
        text,
        ssid,
        start,
        end,
        limit,
    )

    apisession, response_format = await get_apisession(ctx)

    try:
        object_type = event_source

        if object_type.value == "roaming" and not site_id:
            raise ToolError(
                {
                    "status_code": 400,
                    "message": ('`site_id` parameter is required when `event_source` is "roaming".'),
                }
            )

        if object_type.value == "rogue" and not site_id:
            raise ToolError(
                {
                    "status_code": 400,
                    "message": ('`site_id` parameter is required when `event_source` is "rogue".'),
                }
            )

        if text and event_source.value not in [
            "device",
            "nac_client",
        ]:
            raise ToolError(
                {
                    "status_code": 400,
                    "message": ('`text` parameter can only be used when `event_source` is in "device", "nac_client".'),
                }
            )

        if ssid and event_source.value not in [
            "wireless_client",
            "nac_client",
            "rogue",
        ]:
            raise ToolError(
                {
                    "status_code": 400,
                    "message": (
                        "`ssid` parameter can only be used "
                        "when `event_source` is in "
                        '"wireless_client", "nac_client", '
                        '"rogue".'
                    ),
                }
            )

        match object_type.value:
            case "device":
                if site_id:
                    response = mistapi.api.v1.sites.devices.searchSiteDeviceEvents(
                        apisession,
                        site_id=str(site_id),
                        start=(str(start) if start else None),
                        end=str(end) if end else None,
                        type=(str(event_type) if event_type else None),
                        mac=str(mac) if mac else None,
                        text=str(text) if text else None,
                        limit=limit,
                    )
                    await process_response(response)
                else:
                    response = mistapi.api.v1.orgs.devices.searchOrgDeviceEvents(
                        apisession,
                        org_id=str(org_id),
                        start=(str(start) if start else None),
                        end=str(end) if end else None,
                        type=(str(event_type) if event_type else None),
                        mac=str(mac) if mac else None,
                        text=str(text) if text else None,
                        limit=limit,
                    )
                    await process_response(response)
            case "mxedge":
                mxedge_id = f"00000000-0000-0000-1000-{str(mac)}" if mac else None
                if site_id:
                    response = mistapi.api.v1.sites.mxedges.searchSiteMistEdgeEvents(
                        apisession,
                        site_id=str(site_id),
                        start=(str(start) if start else None),
                        end=str(end) if end else None,
                        type=(str(event_type) if event_type else None),
                        mxedge_id=mxedge_id,
                        limit=limit,
                    )
                    await process_response(response)
                else:
                    response = mistapi.api.v1.orgs.mxedges.searchOrgMistEdgeEvents(
                        apisession,
                        org_id=str(org_id),
                        start=(str(start) if start else None),
                        end=str(end) if end else None,
                        type=(str(event_type) if event_type else None),
                        mxedge_id=mxedge_id,
                        limit=limit,
                    )
                    await process_response(response)
            case "wan_client":
                if site_id:
                    response = mistapi.api.v1.sites.wan_clients.searchSiteWanClientEvents(
                        apisession,
                        site_id=str(site_id),
                        start=(str(start) if start else None),
                        end=str(end) if end else None,
                        type=(str(event_type) if event_type else None),
                        mac=str(mac) if mac else None,
                        limit=limit,
                    )
                    await process_response(response)
                else:
                    response = mistapi.api.v1.orgs.wan_clients.searchOrgWanClientEvents(
                        apisession,
                        org_id=str(org_id),
                        start=(str(start) if start else None),
                        end=str(end) if end else None,
                        type=(str(event_type) if event_type else None),
                        mac=str(mac) if mac else None,
                        limit=limit,
                    )
                    await process_response(response)
            case "wireless_client":
                if site_id:
                    response = mistapi.api.v1.sites.clients.searchSiteWirelessClientEvents(
                        apisession,
                        site_id=str(site_id),
                        start=(str(start) if start else None),
                        end=str(end) if end else None,
                        type=(str(event_type) if event_type else None),
                        ssid=str(ssid) if ssid else None,
                        limit=limit,
                    )
                    await process_response(response)
                else:
                    response = mistapi.api.v1.orgs.clients.searchOrgWirelessClientEvents(
                        apisession,
                        org_id=str(org_id),
                        start=(str(start) if start else None),
                        end=str(end) if end else None,
                        type=(str(event_type) if event_type else None),
                        ssid=str(ssid) if ssid else None,
                        limit=limit,
                    )
                    await process_response(response)
            case "nac_client":
                if site_id:
                    response = mistapi.api.v1.sites.nac_clients.searchSiteNacClientEvents(
                        apisession,
                        site_id=str(site_id),
                        start=(str(start) if start else None),
                        end=str(end) if end else None,
                        type=(str(event_type) if event_type else None),
                        mac=str(mac) if mac else None,
                        text=str(text) if text else None,
                        ssid=str(ssid) if ssid else None,
                        limit=limit,
                    )
                    await process_response(response)
                else:
                    response = mistapi.api.v1.orgs.nac_clients.searchOrgNacClientEvents(
                        apisession,
                        org_id=str(org_id),
                        start=(str(start) if start else None),
                        end=str(end) if end else None,
                        type=(str(event_type) if event_type else None),
                        mac=str(mac) if mac else None,
                        text=str(text) if text else None,
                        ssid=str(ssid) if ssid else None,
                        limit=limit,
                    )
                    await process_response(response)
            case "roaming":
                response = mistapi.api.v1.sites.events.listSiteRoamingEvents(
                    apisession,
                    site_id=str(site_id),
                    start=str(start) if start else None,
                    end=str(end) if end else None,
                    type=(str(event_type) if event_type else None),
                    limit=limit,
                )
                await process_response(response)
            case "rogue":
                response = mistapi.api.v1.sites.rogues.searchSiteRogueEvents(
                    apisession,
                    site_id=str(site_id),
                    start=str(start) if start else None,
                    end=str(end) if end else None,
                    type=(str(event_type) if event_type else None),
                    ssid=str(ssid) if ssid else None,
                    ap_mac=str(mac) if mac else None,
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
                            f"{[e.value for e in Event_source]}"
                        ),
                    }
                )

    except ToolError:
        raise
    except Exception as _exc:
        await handle_network_error(_exc)

    return format_response(response, response_format)
