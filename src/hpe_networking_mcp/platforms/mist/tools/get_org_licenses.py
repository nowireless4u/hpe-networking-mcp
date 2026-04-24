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


class Response_type(Enum):
    CLAIM_STATUS = "claim_status"
    BY_SITE = "by_site"
    SUMMARY = "summary"


@tool(
    name="mist_get_org_licenses",
    description=("This tool can be used to retrieve information about the licenses of an org"),
    tags={"orgs"},
    annotations={
        "title": "Get org licenses",
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": True,
        "idempotentHint": True,
    },
)
async def get_org_licenses(
    ctx: Context,
    org_id: Annotated[UUID, Field(description="Organization ID")],
    response_type: Annotated[
        Response_type,
        Field(
            description=(
                "Type of license information to retrieve. "
                "`claim_status` returns the status of an "
                "asynchronous license claim operation, "
                "`by_site` returns the list of licenses for "
                "each site in the org, and `summary` returns "
                "a summary of the licenses in the org "
                "including total count and count by license "
                "type"
            )
        ),
    ],
) -> dict | list | str:
    """Retrieve information about the licenses of an org."""

    logger.debug("Tool get_org_licenses called")
    logger.debug(
        "Input Parameters: org_id: %s, response_type: %s",
        org_id,
        response_type,
    )

    apisession, response_format = await get_apisession(ctx)

    try:
        object_type = response_type
        match object_type.value:
            case "claim_status":
                response = mistapi.api.v1.orgs.claim.GetOrgLicenseAsyncClaimStatus(apisession, org_id=str(org_id))
                await process_response(response)
            case "by_site":
                response = mistapi.api.v1.orgs.licenses.getOrgLicensesBySite(apisession, org_id=str(org_id))
                await process_response(response)
            case "summary":
                response = mistapi.api.v1.orgs.licenses.getOrgLicensesSummary(apisession, org_id=str(org_id))
                await process_response(response)

            case _:
                raise ToolError(
                    {
                        "status_code": 400,
                        "message": (
                            f"Invalid object_type: "
                            f"{object_type.value}. Valid values "
                            f"are: "
                            f"{[e.value for e in Response_type]}"
                        ),
                    }
                )

    except ToolError:
        raise
    except Exception as _exc:
        await handle_network_error(_exc)

    return format_response(response, response_format)
