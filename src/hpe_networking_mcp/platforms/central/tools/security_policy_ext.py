"""Aruba Central policy groups and role GPID tools.

Extension of security_policy.py — split to stay under 500-line limit.
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
from hpe_networking_mcp.platforms.central.tools.security_policy import (
    _CONFIRMED_FIELD,
    _DEVICE_FUNCTION_FIELD,
    _SCOPE_ID_FIELD,
    _get_resource,
    _manage_resource,
)
from hpe_networking_mcp.platforms.central.utils import retry_central_command

WRITE_DELETE = ToolAnnotations(
    readOnlyHint=False,
    destructiveHint=True,
    idempotentHint=False,
    openWorldHint=True,
)


# ---------------------------------------------------------------------------
# Policy Groups
# ---------------------------------------------------------------------------


@mcp.tool(annotations=READ_ONLY)
async def central_get_policy_groups(
    ctx: Context,
) -> dict | list | str:
    """
    Get policy group configuration from Central.

    Policy groups define the evaluation sequence for all firewall
    policies. They control the order in which policies are applied
    to traffic. This is a global configuration — there is no
    per-name lookup.
    """
    return await _get_resource(ctx, "policy-groups", None)


@mcp.tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_policy_group(
    ctx: Context,
    action_type: Annotated[
        str,
        Field(
            description="'create', 'update', or 'delete'. Operates on the entire policy-group collection.",
        ),
    ],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Policy-group payload. Contains policy-group-list array "
                "with name, position, and description for each entry. "
                "Controls the order policies are evaluated. "
                "Use central_get_policy_groups to see the current structure."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete the policy group configuration.

    Unlike other resources, policy-groups operate at the collection
    level — there is no per-name path. The payload defines the entire
    policy evaluation order.
    """
    if action_type not in ("create", "update", "delete"):
        raise ToolError(f"Invalid action_type: {action_type}. Must be 'create', 'update', or 'delete'.")

    method_map = {"create": "POST", "update": "PATCH", "delete": "DELETE"}
    api_method = method_map[action_type]
    api_path = "network-config/v1alpha1/policy-groups"

    action_wording = {"create": "create", "update": "update", "delete": "delete"}[action_type]

    if action_type != "create" and not confirmed:
        elicitation_response = await elicitation_handler(
            message=f"The LLM wants to {action_wording} the policy-group configuration. Do you accept?",
            ctx=ctx,
        )
        if elicitation_response.action == "decline":
            if await ctx.get_state("elicitation_mode") == "chat_confirm":
                return {
                    "status": "confirmation_required",
                    "message": (
                        f"This operation will {action_wording} the policy-group configuration. "
                        "Please confirm with the user before proceeding. "
                        "Call this tool again with confirmed=true after the user confirms."
                    ),
                }
            return {"message": "Action declined by user."}
        elif elicitation_response.action == "cancel":
            return {"message": "Action canceled by user."}

    conn = ctx.lifespan_context["central_conn"]

    api_params: dict = {}
    if scope_id and device_function:
        api_params["object-type"] = "LOCAL"
        api_params["scope-id"] = scope_id
        api_params["device-function"] = device_function

    api_data = payload if action_type != "delete" else None

    logger.info("Central policy-group: {} — path: {}", api_method, api_path)

    response = retry_central_command(
        central_conn=conn,
        api_method=api_method,
        api_path=api_path,
        api_data=api_data,
        api_params=api_params if api_params else None,
    )

    code = response.get("code", 0)
    if 200 <= code < 300:
        return {"status": "success", "action": action_type, "data": response.get("msg", {})}

    return {"status": "error", "code": code, "message": response.get("msg", "Unknown error")}


# ---------------------------------------------------------------------------
# Role GPIDs
# ---------------------------------------------------------------------------


@mcp.tool(annotations=READ_ONLY)
async def central_get_role_gpids(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """
    Get role GPID (group policy ID) configurations from Central.

    Role GPIDs map roles to policy group IDs. When a role is created
    it gets a default GPID — use this to read or customize which
    policy group ID is assigned to each role.

    Parameters:
        name: Specific role name. If omitted, returns all role-GPIDs.
    """
    return await _get_resource(ctx, "role-gpids", name)


@mcp.tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_role_gpid(
    ctx: Context,
    name: Annotated[str, Field(description="Role name for the GPID mapping.")],
    action_type: Annotated[str, Field(description="'create', 'update', or 'delete'.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Role-GPID payload. Key fields: gpid (the policy group ID "
                "to assign to this role), description. "
                "Use central_get_role_gpids to see existing structures."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a role GPID mapping in Central."""
    return await _manage_resource(
        ctx, "role-gpids", "role-gpid", name, action_type, payload, scope_id, device_function, confirmed
    )
