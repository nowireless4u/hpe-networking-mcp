"""Aruba Central role configuration tools.

Provides read and write access to Central's role system. Roles define
network access for clients and can be assigned to WLAN profiles, switch
ports, NAC policies, and firewall rules. Roles contain VLAN assignments,
QoS settings, ACLs, bandwidth contracts, and classification rules.

API: GET/POST/PATCH/DELETE /network-config/v1alpha1/roles
"""

from typing import Annotated

from fastmcp import Context
from fastmcp.exceptions import ToolError
from loguru import logger
from mcp.types import ToolAnnotations
from pydantic import Field

from hpe_networking_mcp.middleware.elicitation import elicitation_handler
from hpe_networking_mcp.platforms.central._registry import mcp
from hpe_networking_mcp.platforms.central.tools import READ_ONLY
from hpe_networking_mcp.platforms.central.utils import retry_central_command

WRITE_DELETE = ToolAnnotations(
    readOnlyHint=False,
    destructiveHint=True,
    idempotentHint=False,
    openWorldHint=True,
)


@mcp.tool(annotations=READ_ONLY)
async def central_get_roles(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """
    Get role configurations from Aruba Central.

    Roles define network access for clients — VLAN assignments, QoS,
    ACLs, bandwidth contracts, and classification rules. They are used
    in WLAN profiles (default-role, pre-auth-role), switch port configs,
    NAC policies, and firewall rules.

    Parameters:
        name: Specific role name to retrieve. If omitted, returns all roles.

    Returns:
        Single role dict if name specified, or list of all roles.
    """
    conn = ctx.lifespan_context["central_conn"]
    api_path = f"network-config/v1alpha1/roles/{name}" if name else "network-config/v1alpha1/roles"

    response = retry_central_command(
        central_conn=conn,
        api_method="GET",
        api_path=api_path,
    )
    return response.get("msg", {})


@mcp.tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_role(
    ctx: Context,
    name: Annotated[
        str,
        Field(description="The role name. Used as the identifier in the API path."),
    ],
    action_type: Annotated[
        str,
        Field(description="Action to perform: 'create', 'update', or 'delete'."),
    ],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Role configuration payload. For delete: pass empty dict {}. "
                "For create/update, key fields include:\n"
                "- vlan: VLAN assignment for the role (ID or name)\n"
                "- access-list: ACL rules applied to this role\n"
                "- bandwidth-contract: bandwidth limits\n"
                "- qos: QoS settings\n"
                "- captive-portal: captive portal profile\n"
                "- session-timeout: session timeout in seconds\n"
                "- description: role description (CX switches only)\n"
                "Use central_get_roles to see existing role structures "
                "as a reference for the payload format."
            )
        ),
    ],
    scope_id: Annotated[
        str | None,
        Field(
            description=(
                "Scope ID for scoped (LOCAL) roles. If provided, creates "
                "a local role at this scope. If omitted, creates a shared "
                "(SHARED/library) role. Get scope IDs from central_get_scope_tree."
            ),
            default=None,
        ),
    ],
    device_function: Annotated[
        str | None,
        Field(
            description=(
                "Device function for scoped roles. Required when scope_id "
                "is provided. Valid values: CAMPUS_AP, ACCESS_SWITCH, "
                "BRANCH_GW, MOBILITY_GW, CORE_SWITCH, AGG_SWITCH, ALL."
            ),
            default=None,
        ),
    ],
    confirmed: Annotated[
        bool,
        Field(
            description="Set to true when the user has confirmed the operation in chat.",
            default=False,
        ),
    ],
) -> dict | str:
    """
    Create, update, or delete a role in Central.

    Roles define network access for clients and are used across WLAN
    profiles, switch ports, NAC policies, and firewall rules. The role
    name is the identifier in the API path.

    Roles can be shared (library-level, available everywhere) or local
    (scoped to a specific site/collection/device). Use scope_id and
    device_function to create local roles.

    After creating a role, use central_manage_config_assignment to
    assign it to a scope if needed.
    """
    if action_type not in ("create", "update", "delete"):
        raise ToolError(f"Invalid action_type: {action_type}. Must be 'create', 'update', or 'delete'.")

    api_path = f"network-config/v1alpha1/roles/{name}"
    method_map = {"create": "POST", "update": "PATCH", "delete": "DELETE"}
    api_method = method_map[action_type]

    action_wording = {
        "create": "create a new",
        "update": "update an existing",
        "delete": "delete an existing",
    }[action_type]

    # Confirm for update and delete only
    if action_type != "create" and not confirmed:
        elicitation_response = await elicitation_handler(
            message=f"The LLM wants to {action_wording} role '{name}'. Do you accept?",
            ctx=ctx,
        )
        if elicitation_response.action == "decline":
            if await ctx.get_state("elicitation_mode") == "chat_confirm":
                return {
                    "status": "confirmation_required",
                    "message": (
                        f"This operation will {action_wording} role '{name}'. "
                        "Please confirm with the user before proceeding. "
                        "Call this tool again with confirmed=true after the user confirms."
                    ),
                }
            return {"message": "Action declined by user."}
        elif elicitation_response.action == "cancel":
            return {"message": "Action canceled by user."}

    conn = ctx.lifespan_context["central_conn"]

    # Build query params for scoped operations
    api_params: dict = {}
    if scope_id and device_function:
        api_params["object-type"] = "LOCAL"
        api_params["scope-id"] = scope_id
        api_params["device-function"] = device_function

    api_data: dict = {}
    if action_type != "delete":
        api_data = payload

    logger.info("Central role: {} '{}' — path: {}", api_method, name, api_path)

    response = retry_central_command(
        central_conn=conn,
        api_method=api_method,
        api_path=api_path,
        api_data=api_data if api_data else None,
        api_params=api_params if api_params else None,
    )

    code = response.get("code", 0)
    if 200 <= code < 300:
        return {
            "status": "success",
            "action": action_type,
            "name": name,
            "data": response.get("msg", {}),
        }

    return {
        "status": "error",
        "code": code,
        "message": response.get("msg", "Unknown error"),
    }
