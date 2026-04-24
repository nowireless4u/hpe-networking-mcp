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


class Sle(Enum):
    WIFI = "wifi"
    WIRED = "wired"
    WAN = "wan"


@tool(
    name="mist_get_org_sites_sle",
    description=("Get SLE summary for the organization sites."),
    tags={"sles"},
    annotations={
        "title": "Get org sites sle",
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": True,
        "idempotentHint": True,
    },
)
async def get_org_sites_sle(
    ctx: Context,
    org_id: Annotated[UUID, Field(description="Organization ID")],
    sle: Annotated[
        Sle,
        Field(
            description=("Type of SLE data to retrieve for the sites. Possible values are `wifi`, `wired`, and `wan`")
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
    """Get SLE summary for the organization sites."""

    logger.debug("Tool get_org_sites_sle called")
    logger.debug(
        "Input Parameters: org_id: %s, sle: %s, start: %s, end: %s, limit: %s",
        org_id,
        sle,
        start,
        end,
        limit,
    )

    apisession, response_format = await get_apisession(ctx)

    try:
        response = mistapi.api.v1.orgs.insights.getOrgSitesSle(
            apisession,
            org_id=str(org_id),
            sle=sle.value,
            start=str(start) if start else None,
            end=str(end) if end else None,
            limit=limit,
        )
        await process_response(response)
    except ToolError:
        raise
    except Exception as _exc:
        await handle_network_error(_exc)

    return format_response(response, response_format)
