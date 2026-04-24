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
    ORG = "org"
    SITE = "site"
    SUPPRESSED = "suppressed"


@tool(
    name="mist_search_alarms",
    description=(
        "Search for raised alarms in an organization or site "
        "with optional filtering.\n"
        "\nScopes:\n"
        "- `org`: Search all alarms across the organization\n"
        "- `site`: Search alarms in a specific site "
        "(requires `site_id`)\n"
        "- `suppressed`: View temporarily disabled alarms "
        "across the organization\n"
        "\nAlarm groups: `infrastructure` (network "
        "device/connectivity issues), `marvis` (AI-driven "
        "network detections), `security` (security events)\n"
        "\nCommon Marvis alarm types: `bad_cable`, "
        "`bad_wan_uplink`, `dns_failure`, `arp_failure`, "
        "`auth_failure`, `dhcp_failure`, `missing_vlan`, "
        "`negotiation_mismatch`, `port_flap`\n"
        "\nFor a complete list of alarm types, use "
        "`mist_get_constants` with "
        "`object_type=alarm_definitions`."
    ),
    tags={"events"},
    annotations={
        "title": "Search alarms",
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": True,
        "idempotentHint": True,
    },
)
async def search_alarms(
    ctx: Context,
    org_id: Annotated[UUID, Field(description="Organization ID")],
    scope: Annotated[
        Scope,
        Field(
            description=(
                "Search scope: `org` (organization-wide), "
                "`site` (specific site, requires site_id), "
                "or `suppressed` (disabled alarms)"
            )
        ),
    ],
    site_id: Annotated[UUID, Field(description="Site ID", default=None)],
    group: Annotated[
        str,
        Field(
            description=(
                "Only for org/site scope. Alarm group. "
                "enum: `infrastructure`, `marvis`, "
                "`security`. The `marvis` group is used "
                "to retrieve AI-driven network issue "
                "detections."
            ),
            default=None,
        ),
    ],
    severity: Annotated[
        str,
        Field(
            description=(
                "Only for org/site scope. Severity of the alarm. enum: `critical`, `major`, `minor`, `warn`, `info`"
            ),
            default=None,
        ),
    ],
    alarm_type: Annotated[
        str,
        Field(
            description=(
                "Only for org/site scope. Comma separated "
                "list of types of the alarm (e.g., "
                "'bad_cable,auth_failure'). IMPORTANT: use "
                "the `mist_get_constants` tool with "
                "`object_type=alarm_definitions` to get the "
                "list of possible alarm types"
            ),
            default=None,
        ),
    ],
    acked: Annotated[
        bool,
        Field(
            description=(
                "Only for org/site scope. Whether to filter for acknowledged (true) or unacknowledged (false) alarms"
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
    """Search for raised alarms in an org or site."""

    logger.debug("Tool search_alarms called")
    logger.debug(
        "Input Parameters: org_id: %s, scope: %s, "
        "site_id: %s, group: %s, severity: %s, "
        "alarm_type: %s, acked: %s, start: %s, end: %s, "
        "limit: %s",
        org_id,
        scope,
        site_id,
        group,
        severity,
        alarm_type,
        acked,
        start,
        end,
        limit,
    )

    apisession, response_format = await get_apisession(ctx)

    try:
        object_type = scope

        if object_type.value == "site" and not site_id:
            raise ToolError(
                {
                    "status_code": 400,
                    "message": ('`site_id` parameter is required when `scope` is "site".'),
                }
            )

        org_site_scopes = ["org", "site"]

        if group and scope.value not in org_site_scopes:
            raise ToolError(
                {
                    "status_code": 400,
                    "message": ('`group` parameter can only be used when `scope` is in "org", "site".'),
                }
            )

        if severity and scope.value not in org_site_scopes:
            raise ToolError(
                {
                    "status_code": 400,
                    "message": ('`severity` parameter can only be used when `scope` is in "org", "site".'),
                }
            )

        if alarm_type and scope.value not in org_site_scopes:
            raise ToolError(
                {
                    "status_code": 400,
                    "message": ('`alarm_type` parameter can only be used when `scope` is in "org", "site".'),
                }
            )

        if acked and scope.value not in org_site_scopes:
            raise ToolError(
                {
                    "status_code": 400,
                    "message": ('`acked` parameter can only be used when `scope` is in "org", "site".'),
                }
            )

        match object_type.value:
            case "org":
                response = mistapi.api.v1.orgs.alarms.searchOrgAlarms(
                    apisession,
                    org_id=str(org_id),
                    group=group if group else None,
                    severity=(severity if severity else None),
                    type=(alarm_type if alarm_type else None),
                    acked=acked if acked else None,
                    start=str(start) if start else None,
                    end=str(end) if end else None,
                    limit=limit,
                )
                await process_response(response)
            case "site":
                response = mistapi.api.v1.sites.alarms.searchSiteAlarms(
                    apisession,
                    site_id=str(site_id),
                    group=group if group else None,
                    severity=(severity if severity else None),
                    type=(alarm_type if alarm_type else None),
                    acked=acked if acked else None,
                    start=str(start) if start else None,
                    end=str(end) if end else None,
                    limit=limit,
                )
                await process_response(response)
            case "suppressed":
                response = mistapi.api.v1.orgs.alarmtemplates.listOrgSuppressedAlarms(apisession, org_id=str(org_id))
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
