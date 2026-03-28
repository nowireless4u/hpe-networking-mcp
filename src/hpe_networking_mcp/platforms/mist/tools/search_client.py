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

from hpe_networking_mcp.platforms.mist._registry import mcp
from hpe_networking_mcp.platforms.mist.client import (
    format_response,
    get_apisession,
    handle_network_error,
    process_response,
)


class Client_type(Enum):
    WAN = "wan"
    WIRED = "wired"
    WIRELESS = "wireless"
    NAC = "nac"


class Band(Enum):
    B24 = "24"
    B5 = "5"
    B6 = "6"


@mcp.tool(
    name="mist_search_client",
    description=(
        "Search for clients across an organization or "
        "specific site. Supports searching by client type "
        "(WAN, wired, wireless, NAC), MAC address, hostname, "
        "IP address, and more. Use wildcards (*) for partial "
        "matches on MAC address, hostname, IP, and text "
        "fields. Different client types support different "
        "filter parameters - the tool will validate "
        "compatibility."
    ),
    tags={"clients"},
    annotations={
        "title": "Search client",
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": True,
        "idempotentHint": True,
    },
)
async def search_client(
    client_type: Annotated[
        Client_type,
        Field(description=("Type of client: WAN, wired, wireless, or NAC")),
    ],
    org_id: Annotated[UUID, Field(description="Organization ID")],
    site_id: Annotated[UUID, Field(description="Site ID", default=None)],
    device_mac: Annotated[
        str,
        Field(
            description=(
                "Partial / full MAC Address of the Access "
                "Point or the Switch. Use `prefix*` for "
                "prefix search or `*substring*` for contains "
                "search (e.g. `aabbcc*` and `*bbcc*` match "
                "`aabbccddeeff`). Suffix-only wildcards "
                "(e.g. `*bccddeeff`) are not supported"
            ),
            default=None,
        ),
    ],
    band: Annotated[
        Band,
        Field(
            description=("802.11 band (24 or 5 or 6 GHz). Wireless clients only"),
            default=None,
        ),
    ],
    ssid: Annotated[
        str,
        Field(
            description=("SSID name. Wireless or NAC clients only"),
            default=None,
        ),
    ],
    mac: Annotated[
        str,
        Field(
            description=(
                "Partial / full Client MAC Address. Use "
                "`prefix*` for prefix search or "
                "`*substring*` for contains search (e.g. "
                "`aabbcc*` and `*bbcc*` match "
                "`aabbccddeeff`). Suffix-only wildcards "
                "(e.g. `*bccddeeff`) are not supported"
            ),
            default=None,
        ),
    ],
    hostname: Annotated[
        str,
        Field(
            description=(
                "Partial / full Client hostname. Use "
                "`prefix*` for prefix search or "
                "`*substring*` for contains search (e.g. "
                "`everest*` and `*rest*` match "
                "`my-everest-client`). Suffix-only wildcards "
                "(e.g. `*everest`) are not supported. Not "
                "applicable for WAN or wired clients"
            ),
            default=None,
        ),
    ],
    ip: Annotated[
        str,
        Field(
            description=(
                "Partial / full Client IP Address. Use "
                "`prefix*` for prefix search or "
                "`*substring*` for contains search (e.g. "
                "`10.100.10.*` and `*100.10.*` match "
                "`10.100.10.54`). Suffix-only wildcards "
                "(e.g. `*.54`) are not supported. Not "
                "applicable for NAC clients"
            ),
            default=None,
        ),
    ],
    text: Annotated[
        str,
        Field(
            description=("Free text search in client details (supports * wildcard). Not applicable for WAN clients"),
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
    """Search for clients across an org or specific site."""

    logger.debug("Tool search_client called")
    logger.debug(
        "Input Parameters: client_type: %s, org_id: %s, "
        "site_id: %s, device_mac: %s, band: %s, ssid: %s, "
        "mac: %s, hostname: %s, ip: %s, text: %s, "
        "start: %s, end: %s, limit: %s",
        client_type,
        org_id,
        site_id,
        device_mac,
        band,
        ssid,
        mac,
        hostname,
        ip,
        text,
        start,
        end,
        limit,
    )

    apisession, response_format = await get_apisession()

    try:
        object_type = client_type

        if band and client_type.value not in ["wireless"]:
            raise ToolError(
                {
                    "status_code": 400,
                    "message": ('`band` parameter can only be used when `client_type` is "wireless".'),
                }
            )

        if ssid and client_type.value not in [
            "wireless",
            "nac",
        ]:
            raise ToolError(
                {
                    "status_code": 400,
                    "message": ('`ssid` parameter can only be used when `client_type` is in "wireless", "nac".'),
                }
            )

        match object_type.value:
            case "wan":
                response = mistapi.api.v1.orgs.wan_clients.searchOrgWanClients(
                    apisession,
                    org_id=str(org_id),
                    site_id=(str(site_id) if site_id else None),
                    mac=str(mac) if mac else None,
                    hostname=(str(hostname) if hostname else None),
                    ip=str(ip) if ip else None,
                    start=str(start) if start else None,
                    end=str(end) if end else None,
                    limit=limit,
                )
                await process_response(response)
            case "wired":
                response = mistapi.api.v1.orgs.wired_clients.searchOrgWiredClients(
                    apisession,
                    org_id=str(org_id),
                    site_id=(str(site_id) if site_id else None),
                    device_mac=(str(device_mac) if device_mac else None),
                    mac=str(mac) if mac else None,
                    ip=str(ip) if ip else None,
                    start=str(start) if start else None,
                    end=str(end) if end else None,
                    limit=limit,
                )
                await process_response(response)
            case "wireless":
                response = mistapi.api.v1.orgs.clients.searchOrgWirelessClients(
                    apisession,
                    org_id=str(org_id),
                    site_id=(str(site_id) if site_id else None),
                    ap=(str(device_mac) if device_mac else None),
                    band=str(band) if band else None,
                    ssid=str(ssid) if ssid else None,
                    mac=str(mac) if mac else None,
                    hostname=(str(hostname) if hostname else None),
                    ip=str(ip) if ip else None,
                    start=str(start) if start else None,
                    end=str(end) if end else None,
                    limit=limit,
                )
                await process_response(response)
            case "nac":
                response = mistapi.api.v1.orgs.nac_clients.searchOrgNacClients(
                    apisession,
                    org_id=str(org_id),
                    site_id=(str(site_id) if site_id else None),
                    ssid=str(ssid) if ssid else None,
                    mac=str(mac) if mac else None,
                    hostname=(str(hostname) if hostname else None),
                    text=str(text) if text else None,
                    start=str(start) if start else None,
                    end=str(end) if end else None,
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
                            f"{[e.value for e in Client_type]}"
                        ),
                    }
                )

    except ToolError:
        raise
    except Exception as _exc:
        await handle_network_error(_exc)

    return format_response(response, response_format)
