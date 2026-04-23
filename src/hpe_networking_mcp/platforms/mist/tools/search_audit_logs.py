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


class Scope(Enum):
    SELF = "self"
    ORG = "org"


@tool(
    name="mist_search_audit_logs",
    description=("Search audit logs for the current account or an organization"),
    tags={"events"},
    annotations={
        "title": "Search audit logs",
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": True,
        "idempotentHint": True,
    },
)
async def search_audit_logs(
    scope: Annotated[
        Scope,
        Field(
            description=(
                "Whether to retrieve audit logs for the "
                "account or a specific organization. If "
                "`org` is selected, the `org_id` parameter "
                "is required"
            )
        ),
    ],
    org_id: Annotated[
        UUID,
        Field(description="Organization ID", default=None),
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
    message: Annotated[
        str,
        Field(
            description=("Message to filter audit logs by (partial search)"),
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
    """Search audit logs for the current account or an org."""

    logger.debug("Tool search_audit_logs called")
    logger.debug(
        "Input Parameters: scope: %s, org_id: %s, start: %s, end: %s, message: %s, limit: %s",
        scope,
        org_id,
        start,
        end,
        message,
        limit,
    )

    apisession, response_format = await get_apisession()

    try:
        object_type = scope

        if object_type.value == "org" and not org_id:
            raise ToolError(
                {
                    "status_code": 400,
                    "message": ('`org_id` parameter is required when `scope` is "org".'),
                }
            )

        match object_type.value:
            case "self":
                response = mistapi.api.v1.self.logs.listSelfAuditLogs(
                    apisession,
                    start=str(start) if start else None,
                    end=str(end) if end else None,
                    message=(str(message) if message else None),
                    limit=limit,
                )
                await process_response(response)
            case "org":
                response = mistapi.api.v1.orgs.logs.listOrgAuditLogs(
                    apisession,
                    org_id=str(org_id),
                    start=str(start) if start else None,
                    end=str(end) if end else None,
                    message=(str(message) if message else None),
                    limit=limit,
                )
                await process_response(response)

            case _:
                raise ToolError(
                    {
                        "status_code": 400,
                        "message": (
                            f"Invalid object_type: {object_type.value}. Valid values are: {[e.value for e in Scope]}"
                        ),
                    }
                )

    except ToolError:
        raise
    except Exception as _exc:
        await handle_network_error(_exc)

    return format_response(response, response_format)
