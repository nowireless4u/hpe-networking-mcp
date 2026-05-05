"""Aruba Central configuration assignment tools.

Provides tools to assign, read, and remove configuration profiles
(WLAN SSIDs, roles, policies, etc.) at specific scopes in the
Central hierarchy. This is how profiles created in the library
get applied to Global, site collections, sites, device groups,
or individual devices.

API: POST/GET/DELETE /network-config/v1alpha1/config-assignments
"""

from typing import Annotated

from fastmcp import Context
from fastmcp.exceptions import ToolError
from loguru import logger
from pydantic import Field

from hpe_networking_mcp.middleware.elicitation import elicitation_handler
from hpe_networking_mcp.platforms.central._registry import tool
from hpe_networking_mcp.platforms.central.tools import READ_ONLY
from hpe_networking_mcp.platforms.central.utils import retry_central_command

WRITE_DELETE = {
    "readOnlyHint": False,
    "destructiveHint": True,
    "idempotentHint": False,
    "openWorldHint": True,
}

# Valid device-function values from the API schema
VALID_DEVICE_FUNCTIONS = {
    "CAMPUS_AP",
    "MICROBRANCH_AP",
    "ACCESS_SWITCH",
    "CORE_SWITCH",
    "AGG_SWITCH",
    "AOSS_ACCESS_SWITCH",
    "AOSS_CORE_SWITCH",
    "AOSS_AGG_SWITCH",
    "BRANCH_GW",
    "MOBILITY_GW",
    "VPNC",
    "ALL",
    "SERVICE_PERSONA",
    "BRIDGE",
    "IOT",
    "HYBRID_NAC",
}


@tool(annotations=READ_ONLY)
async def central_get_config_assignments(
    ctx: Context,
    scope_id: Annotated[
        str | None,
        Field(
            description=(
                "Scope ID to filter assignments. Get scope IDs from "
                "central_get_scope_tree. If omitted, returns all assignments."
            ),
            default=None,
        ),
    ],
    device_function: Annotated[
        str | None,
        Field(
            description=(
                "Device function filter. For WLAN profiles use 'CAMPUS_AP'. "
                "Valid values: CAMPUS_AP, ACCESS_SWITCH, BRANCH_GW, "
                "MOBILITY_GW, CORE_SWITCH, AGG_SWITCH, ALL, etc."
            ),
            default=None,
        ),
    ],
) -> dict | list | str:
    """
    Get configuration assignments from Aruba Central.

    Shows which configuration profiles are assigned to which scopes
    and device functions. Use this to check where a WLAN profile,
    role, or policy is currently assigned in the hierarchy.

    Parameters:
        scope_id: Filter by scope ID. Get IDs from central_get_scope_tree.
        device_function: Filter by device function (e.g. CAMPUS_AP for WLANs).

    Returns:
        List of config-assignment entries with scope-id, device-function,
        profile-type, profile-instance, scope-name, and scope-type.
    """
    conn = ctx.lifespan_context["central_conn"]

    api_params: dict = {}
    if scope_id:
        api_params["scope-id"] = scope_id
    if device_function:
        api_params["device-function"] = device_function

    response = retry_central_command(
        central_conn=conn,
        api_method="GET",
        api_path="network-config/v1alpha1/config-assignments",
        api_params=api_params,
    )
    return response.get("msg", {})


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_config_assignment(
    ctx: Context,
    action_type: Annotated[
        str,
        Field(
            description="Action to perform: 'assign' or 'remove'.",
        ),
    ],
    scope_id: Annotated[
        str,
        Field(
            description=(
                "Scope ID where the profile should be assigned/removed. "
                "Get scope IDs from central_get_scope_tree. Examples: "
                "Global scope ID, a site collection ID, or a site ID."
            ),
        ),
    ],
    device_function: Annotated[
        str,
        Field(
            description=(
                "Device function for the assignment. For WLAN profiles "
                "use 'CAMPUS_AP'. Valid values: CAMPUS_AP, ACCESS_SWITCH, "
                "BRANCH_GW, MOBILITY_GW, CORE_SWITCH, AGG_SWITCH, ALL, "
                "MICROBRANCH_AP, VPNC, SERVICE_PERSONA, BRIDGE, IOT, "
                "HYBRID_NAC, AOSS_ACCESS_SWITCH, AOSS_CORE_SWITCH, "
                "AOSS_AGG_SWITCH."
            ),
        ),
    ],
    profile_type: Annotated[
        str,
        Field(
            description=(
                "Type of profile to assign. For WLAN SSIDs use 'wlan-ssids'. "
                "Other examples: 'roles', 'policies', 'auth-server-groups', "
                "'named-vlans', 'aliases'."
            ),
        ),
    ],
    profile_instance: Annotated[
        str,
        Field(
            description=(
                "Name of the specific profile to assign. For WLAN SSIDs "
                "this is the SSID name (e.g. 'TEST-SSID'). For roles "
                "this is the role name, etc."
            ),
        ),
    ],
    confirmed: Annotated[
        bool,
        Field(
            description="Set to true when the user has confirmed the operation.",
            default=False,
        ),
    ],
) -> dict | str:
    """
    Assign or remove a configuration profile at a scope in Central's hierarchy.

    This is how profiles created in the library (WLAN SSIDs, roles,
    policies, etc.) get applied to scopes in the hierarchy. For example,
    to make a WLAN profile active at a site, assign it with:
    - scope_id = the site's scope ID (from central_get_scope_tree)
    - device_function = "CAMPUS_AP"
    - profile_type = "wlan-ssids"
    - profile_instance = "TEST-SSID"

    To find the scope_id, call central_get_scope_tree and look up the
    target scope (Global, site collection, or site) by name.
    """
    if action_type not in ("assign", "remove"):
        raise ToolError(f"Invalid action_type: {action_type}. Must be 'assign' or 'remove'.")

    if device_function not in VALID_DEVICE_FUNCTIONS:
        raise ToolError(
            f"Invalid device_function: {device_function}. Valid values: {', '.join(sorted(VALID_DEVICE_FUNCTIONS))}"
        )

    conn = ctx.lifespan_context["central_conn"]

    if action_type == "assign":
        action_wording = f"assign profile '{profile_instance}' ({profile_type}) to scope '{scope_id}'"

        if not confirmed:
            elicitation_response = await elicitation_handler(
                message=f"The LLM wants to {action_wording}. Do you accept?",
                ctx=ctx,
            )
            if elicitation_response.action == "decline":
                if await ctx.get_state("elicitation_mode") == "chat_confirm":
                    return {
                        "status": "confirmation_required",
                        "message": (
                            f"This operation will {action_wording}. "
                            "Please confirm with the user before proceeding. "
                            "Call this tool again with confirmed=true after the user confirms."
                        ),
                    }
                return {"message": "Action declined by user."}
            elif elicitation_response.action == "cancel":
                return {"message": "Action canceled by user."}

        payload = {
            "config-assignment": [
                {
                    "scope-id": scope_id,
                    "device-function": device_function,
                    "profile-type": profile_type,
                    "profile-instance": profile_instance,
                }
            ]
        }

        logger.info(
            "Central config-assignment: assign '{}' ({}) to scope '{}' as {}",
            profile_instance,
            profile_type,
            scope_id,
            device_function,
        )

        response = retry_central_command(
            central_conn=conn,
            api_method="POST",
            api_path="network-config/v1alpha1/config-assignments",
            api_data=payload,
        )

    else:  # remove
        action_wording = f"remove profile '{profile_instance}' ({profile_type}) from scope '{scope_id}'"

        if not confirmed:
            elicitation_response = await elicitation_handler(
                message=f"The LLM wants to {action_wording}. Do you accept?",
                ctx=ctx,
            )
            if elicitation_response.action == "decline":
                if await ctx.get_state("elicitation_mode") == "chat_confirm":
                    return {
                        "status": "confirmation_required",
                        "message": (
                            f"This operation will {action_wording}. "
                            "Please confirm with the user before proceeding. "
                            "Call this tool again with confirmed=true after the user confirms."
                        ),
                    }
                return {"message": "Action declined by user."}
            elif elicitation_response.action == "cancel":
                return {"message": "Action canceled by user."}

        base = "network-config/v1alpha1/config-assignments"
        api_path = f"{base}/{scope_id}/{device_function}/{profile_type}/{profile_instance}"

        logger.info(
            "Central config-assignment: remove '{}' ({}) from scope '{}' as {}",
            profile_instance,
            profile_type,
            scope_id,
            device_function,
        )

        response = retry_central_command(
            central_conn=conn,
            api_method="DELETE",
            api_path=api_path,
        )

    code = response.get("code", 0)
    if 200 <= code < 300:
        return {
            "status": "success",
            "action": action_type,
            "scope_id": scope_id,
            "device_function": device_function,
            "profile_type": profile_type,
            "profile_instance": profile_instance,
            "data": response.get("msg", {}),
        }

    return {
        "status": "error",
        "code": code,
        "message": response.get("msg", "Unknown error"),
    }
