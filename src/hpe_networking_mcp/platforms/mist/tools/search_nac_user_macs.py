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
from hpe_networking_mcp.platforms.mist._registry import mcp
from loguru import logger

from pydantic import Field
from typing import Annotated, List
from uuid import UUID


@mcp.tool(
    name="mist_search_nac_user_macs",
    description="""Search for NAC user MAC addresses in an organization or site, with optional filters for associated SSID and time range. User MACs are used to perform MAC Authentication with Juniper Mist NAC.""",
    tags={"orgs_nac"},
    annotations={
        "title": "Search nac user macs",
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": True,
        "idempotentHint": True,
    },
)
async def search_nac_user_macs(
    org_id: Annotated[UUID, Field(description="""Organization ID""")],
    usermac_id: Annotated[
        str,
        Field(
            description="""ID of the User MAC address to return details for. If specified, other filters are ignored and details for the specified User MAC address is returned if it exists""",
            default=None,
        ),
    ],
    mac: Annotated[
        str,
        Field(
            description="""Partial / full Client MAC Address. Use `prefix*` for prefix search or `*substring*` for contains search (e.g. `aabbcc*` and `*bbcc*` match `aabbccddeeff`). Suffix-only wildcards (e.g. `*bccddeeff`) are not supported""",
            default=None,
        ),
    ],
    labels: Annotated[
        List[str],
        Field(
            description="""Comma separated list of labels to filter NAC endpoints by. A NAC endpoint must have all the specified labels to be included in the results""",
            default=None,
        ),
    ],
    limit: Annotated[
        int, Field(description="""Max number of results per page""", default=20)
    ] = 20,
) -> dict | list | str:
    """Search for NAC user MAC addresses in an organization or site, with optional filters for associated SSID and time range. User MACs are used to perform MAC Authentication with Juniper Mist NAC."""

    logger.debug("Tool search_nac_user_macs called")
    logger.debug(
        "Input Parameters: org_id: %s, usermac_id: %s, mac: %s, labels: %s, limit: %s",
        org_id,
        usermac_id,
        mac,
        labels,
        limit,
    )

    apisession, response_format = await get_apisession()

    try:
        if usermac_id:
            response = mistapi.api.v1.orgs.usermacs.getOrgUserMac(
                apisession, org_id=str(org_id), usermac_id=str(usermac_id)
            )
            await process_response(response)
        else:
            response = mistapi.api.v1.orgs.usermacs.searchOrgUserMacs(
                apisession,
                org_id=str(org_id),
                mac=str(mac) if mac else None,
                labels=labels if labels else None,
                limit=limit,
            )
            await process_response(response)
    except ToolError:
        raise
    except Exception as _exc:
        await handle_network_error(_exc)

    return format_response(response, response_format)
