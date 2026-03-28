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


class Action_type(Enum):
    ACCOUNT_INFO = "account_info"
    API_USAGE = "api_usage"
    LOGIN_FAILURES = "login_failures"


@mcp.tool(
    name="mist_get_self",
    description=(
        "This tool can be used to retrieve information about "
        "the current user and account.\n"
        "The information provided will depend on the "
        "`action_type` attribute:\n"
        "* `account_info`: will return information about the "
        "account including account ID, account name, and the "
        "list of orgs (and their respective `org_id`) the "
        "account has access to, with the permissions level "
        "(read or write) for each org\n"
        "* `api_usage`: will return information about the API "
        "usage of the account including the number of API "
        "calls made in the current hour cycle and the API "
        "call limit for the account\n"
        "* `login_failures`: will return information about the "
        "recent login failures for the account including the "
        "timestamp of the failure, the source IP address, "
        "and the reason for the failure"
    ),
    tags={"self_account"},
    annotations={
        "title": "Get self",
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": True,
        "idempotentHint": True,
    },
)
async def get_self(
    action_type: Annotated[
        Action_type,
        Field(
            description=(
                "Type of information to retrieve about the "
                "current user and account. Possible values are "
                "`account_info`, `api_usage`, and "
                "`login_failures`"
            )
        ),
    ],
) -> dict | list | str:
    """Retrieve information about the current user and account."""

    logger.debug("Tool get_self called")
    logger.debug("Input Parameters: action_type: %s", action_type)

    apisession, response_format = await get_apisession()

    try:
        object_type = action_type
        match object_type.value:
            case "account_info":
                response = mistapi.api.v1.self.self.getSelf(apisession)
                await process_response(response)
            case "api_usage":
                response = mistapi.api.v1.self.usage.getSelfApiUsage(apisession)
                await process_response(response)
            case "login_failures":
                response = mistapi.api.v1.self.login_failures.getSelfLoginFailures(apisession)
                await process_response(response)

            case _:
                raise ToolError(
                    {
                        "status_code": 400,
                        "message": (
                            f"Invalid object_type: "
                            f"{object_type.value}. Valid values "
                            f"are: "
                            f"{[e.value for e in Action_type]}"
                        ),
                    }
                )

    except ToolError:
        raise
    except Exception as _exc:
        await handle_network_error(_exc)

    return format_response(response, response_format)
