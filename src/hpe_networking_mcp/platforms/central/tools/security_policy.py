"""Aruba Central Roles & Policy configuration tools.

Provides read and write access to Central's security policy stack:
net-groups (netdestinations), net-services, object-groups, role-ACLs,
policies, policy-groups, and role-GPIDs.

All resources use the same CRUD pattern at /network-config/v1alpha1/
except policy-groups which operates at the collection level only.
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


# ---------------------------------------------------------------------------
# Factory helpers — avoid repeating the same CRUD logic 7 times
# ---------------------------------------------------------------------------


async def _get_resource(ctx: Context, api_base: str, name: str | None) -> dict | list | str:
    """Generic GET for /network-config/v1alpha1/{api_base}[/{name}]."""
    conn = ctx.lifespan_context["central_conn"]
    api_path = f"network-config/v1alpha1/{api_base}/{name}" if name else f"network-config/v1alpha1/{api_base}"
    response = retry_central_command(central_conn=conn, api_method="GET", api_path=api_path)
    return response.get("msg", {})


async def _manage_resource(
    ctx: Context,
    api_base: str,
    resource_label: str,
    name: str,
    action_type: str,
    payload: dict,
    scope_id: str | None,
    device_function: str | None,
    confirmed: bool,
) -> dict | str:
    """Generic POST/PATCH/DELETE for /network-config/v1alpha1/{api_base}/{name}."""
    if action_type not in ("create", "update", "delete"):
        raise ToolError(f"Invalid action_type: {action_type}. Must be 'create', 'update', or 'delete'.")

    method_map = {"create": "POST", "update": "PATCH", "delete": "DELETE"}
    api_method = method_map[action_type]
    api_path = f"network-config/v1alpha1/{api_base}/{name}"

    action_wording = {"create": "create a new", "update": "update an existing", "delete": "delete an existing"}[
        action_type
    ]

    if action_type != "create" and not confirmed:
        elicitation_response = await elicitation_handler(
            message=f"The LLM wants to {action_wording} {resource_label} '{name}'. Do you accept?",
            ctx=ctx,
        )
        if elicitation_response.action == "decline":
            if await ctx.get_state("elicitation_mode") == "chat_confirm":
                return {
                    "status": "confirmation_required",
                    "message": (
                        f"This operation will {action_wording} {resource_label} '{name}'. "
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

    logger.info("Central {}: {} '{}' — path: {}", resource_label, api_method, name, api_path)

    response = retry_central_command(
        central_conn=conn,
        api_method=api_method,
        api_path=api_path,
        api_data=api_data,
        api_params=api_params if api_params else None,
    )

    code = response.get("code", 0)
    if 200 <= code < 300:
        return {"status": "success", "action": action_type, "name": name, "data": response.get("msg", {})}

    return {"status": "error", "code": code, "message": response.get("msg", "Unknown error")}


# Common field definitions reused across write tools
_SCOPE_ID_FIELD = Field(
    description=(
        "Scope ID for local (scoped) objects. If provided, creates a "
        "local object at this scope. Omit for shared/library objects. "
        "Get scope IDs from central_get_scope_tree."
    ),
    default=None,
)
_DEVICE_FUNCTION_FIELD = Field(
    description=(
        "Device function for scoped objects. Required when scope_id "
        "is provided. Valid: CAMPUS_AP, ACCESS_SWITCH, BRANCH_GW, "
        "MOBILITY_GW, CORE_SWITCH, AGG_SWITCH, ALL."
    ),
    default=None,
)
_CONFIRMED_FIELD = Field(
    description="Set to true when the user has confirmed the operation in chat.",
    default=False,
)


# ---------------------------------------------------------------------------
# Net Groups (netdestinations)
# ---------------------------------------------------------------------------


@mcp.tool(annotations=READ_ONLY)
async def central_get_net_groups(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """
    Get network group (netdestination) configurations from Central.

    Netdestinations are reusable named objects that define sets of
    network destinations (hosts, FQDNs, subnets, IP ranges, VLANs,
    ports) for use in firewall policies and session ACLs. When an
    ACL rule references a netdestination by name, traffic is matched
    against all entries in that group.

    Parameters:
        name: Specific net-group name. If omitted, returns all.
    """
    return await _get_resource(ctx, "net-groups", name)


@mcp.tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_net_group(
    ctx: Context,
    name: Annotated[str, Field(description="Net-group (netdestination) name.")],
    action_type: Annotated[str, Field(description="'create', 'update', or 'delete'.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Net-group payload. Entry types: HOST (address), FQDN (fqdn), "
                "ADDRESS_RANGE (address-range), NETWORK (prefix), VLAN, PORT, "
                "INTERFACE. Each entry has a type and corresponding value field. "
                "Use central_get_net_groups to see existing structures."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a network group (netdestination) in Central."""
    return await _manage_resource(
        ctx,
        "net-groups",
        "net-group",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ---------------------------------------------------------------------------
# Net Services
# ---------------------------------------------------------------------------


@mcp.tool(annotations=READ_ONLY)
async def central_get_net_services(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """
    Get network service definitions from Central.

    Net-services define protocol and port combinations used to identify
    specific types of network traffic in firewall policies and ACL rules.
    Each service specifies a protocol (TCP, UDP, etc.) and ports or
    port ranges.

    Parameters:
        name: Specific net-service name. If omitted, returns all.
    """
    return await _get_resource(ctx, "net-services", name)


@mcp.tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_net_service(
    ctx: Context,
    name: Annotated[str, Field(description="Net-service name.")],
    action_type: Annotated[str, Field(description="'create', 'update', or 'delete'.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Net-service payload. Key fields: protocol (TCP, UDP, etc.), "
                "ports or port ranges, optional ALG processing. "
                "Use central_get_net_services to see existing structures."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a network service definition in Central."""
    return await _manage_resource(
        ctx,
        "net-services",
        "net-service",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ---------------------------------------------------------------------------
# Object Groups
# ---------------------------------------------------------------------------


@mcp.tool(annotations=READ_ONLY)
async def central_get_object_groups(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """
    Get object group configurations from Central.

    Object groups are named collections of objects (addresses, services,
    etc.) that can be referenced in ACL rules and policies. They
    simplify policy management by grouping related items.

    Parameters:
        name: Specific object-group name. If omitted, returns all.
    """
    return await _get_resource(ctx, "object-groups", name)


@mcp.tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_object_group(
    ctx: Context,
    name: Annotated[str, Field(description="Object-group name.")],
    action_type: Annotated[str, Field(description="'create', 'update', or 'delete'.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Object-group payload. Contains named collections of "
                "addresses, services, or other objects for ACL references. "
                "Use central_get_object_groups to see existing structures."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete an object group in Central."""
    return await _manage_resource(
        ctx,
        "object-groups",
        "object-group",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ---------------------------------------------------------------------------
# Role ACLs
# ---------------------------------------------------------------------------


@mcp.tool(annotations=READ_ONLY)
async def central_get_role_acls(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """
    Get role ACL configurations from Central.

    Role ACLs define access control rules based on network roles.
    They reference net-groups (as source/destination aliases) and
    net-services to permit or deny specific traffic patterns.

    Parameters:
        name: Specific role-ACL name. If omitted, returns all.
    """
    return await _get_resource(ctx, "role-acls", name)


@mcp.tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_role_acl(
    ctx: Context,
    name: Annotated[str, Field(description="Role-ACL name.")],
    action_type: Annotated[str, Field(description="'create', 'update', or 'delete'.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Role-ACL payload. Key fields: acl-type, rules (ordered "
                "list of permit/deny entries referencing net-groups and "
                "net-services). Use central_get_role_acls to see existing structures."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a role ACL in Central."""
    return await _manage_resource(
        ctx,
        "role-acls",
        "role-acl",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# ---------------------------------------------------------------------------
# Policies
# ---------------------------------------------------------------------------


@mcp.tool(annotations=READ_ONLY)
async def central_get_policies(
    ctx: Context,
    name: str | None = None,
) -> dict | list | str:
    """
    Get firewall policy configurations from Central.

    Policies define ordered sets of rules that match network traffic
    and apply actions (permit, deny, NAT, redirect, policy-based
    routing). Policies reference net-groups and net-services in
    their rules.

    Parameters:
        name: Specific policy name. If omitted, returns all.
    """
    return await _get_resource(ctx, "policies", name)


@mcp.tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_policy(
    ctx: Context,
    name: Annotated[str, Field(description="Policy name.")],
    action_type: Annotated[str, Field(description="'create', 'update', or 'delete'.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Policy payload. Key fields: type, rules (ordered list "
                "with source/destination aliases, services, and actions). "
                "Use central_get_policies to see existing structures."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a firewall policy in Central."""
    return await _manage_resource(
        ctx,
        "policies",
        "policy",
        name,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )


# Policy Groups and Role GPIDs are in security_policy_ext.py
# to keep this file under the 500-line limit.
