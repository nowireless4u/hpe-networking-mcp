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


class Info_type(Enum):
    ORG = "org"
    SITE = "site"


@tool(
    name="mist_get_org_or_site_info",
    description=("Search information about the organizations or sites"),
    tags={"info"},
    annotations={
        "title": "Get org or site info",
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": True,
        "idempotentHint": True,
    },
)
async def get_org_or_site_info(
    ctx: Context,
    info_type: Annotated[
        Info_type,
        Field(description=("Type of information to search for. Possible values are `org` and `site`")),
    ],
    org_id: Annotated[UUID, Field(description="Organization ID")],
    site_id: Annotated[UUID, Field(description="Site ID", default=None)],
) -> dict | list | str:
    """Search information about the organizations or sites."""

    logger.debug("Tool get_org_or_site_info called")
    logger.debug(
        "Input Parameters: info_type: %s, org_id: %s, site_id: %s",
        info_type,
        org_id,
        site_id,
    )

    apisession, response_format = await get_apisession(ctx)

    try:
        object_type = info_type
        match object_type.value:
            case "org":
                response = mistapi.api.v1.orgs.orgs.getOrg(apisession, org_id=str(org_id))
                await process_response(response)
            case "site":
                if site_id:
                    response = mistapi.api.v1.sites.sites.getSiteInfo(apisession, site_id=str(site_id))
                    await process_response(response)
                else:
                    response = mistapi.api.v1.orgs.sites.listOrgSites(apisession, org_id=str(org_id))
                    await process_response(response)

            case _:
                raise ToolError(
                    {
                        "status_code": 400,
                        "message": (
                            f"Invalid object_type: "
                            f"{object_type.value}. Valid values "
                            f"are: "
                            f"{[e.value for e in Info_type]}"
                        ),
                    }
                )

    except ToolError:
        raise
    except Exception as _exc:
        await handle_network_error(_exc)

    return format_response(response, response_format)
