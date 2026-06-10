"""Aruba Central Roles & Policy shared CRUD helpers.

This module is now **helpers-only**. The CRUD tool surface for the
security-policy stack (net-groups, net-services, object-groups,
role-ACLs, policies, policy-groups, role-GPIDs, roles) is owned by the
generated modules (``security.py``, ``roles_policy.py``, …), which all
import the shared ``_get_resource`` / ``_manage_resource`` helpers and
field constants defined here.

Keep this file import-stable: the generated modules depend on the
helper signatures and ``_*_FIELD`` constants below.

All resources use the same CRUD pattern at /network-config/v1alpha1/.
"""

from fastmcp import Context
from fastmcp.exceptions import ToolError
from loguru import logger
from mcp.types import ToolAnnotations
from pydantic import Field

from hpe_networking_mcp.middleware.elicitation import elicitation_handler
from hpe_networking_mcp.platforms.central.utils import get_central_conn, retry_central_command

WRITE_DELETE = ToolAnnotations(
    readOnlyHint=False,
    destructiveHint=True,
    idempotentHint=False,
    openWorldHint=True,
)


# ---------------------------------------------------------------------------
# Factory helpers — avoid repeating the same CRUD logic across resources
# ---------------------------------------------------------------------------


async def _get_resource(ctx: Context, api_base: str, name: str | None) -> dict | list | str:
    """Generic GET for /network-config/v1alpha1/{api_base}[/{name}]."""
    conn = get_central_conn(ctx)
    api_path = f"network-config/v1alpha1/{api_base}/{name}" if name else f"network-config/v1alpha1/{api_base}"
    response = retry_central_command(central_conn=conn, api_method="GET", api_path=api_path)
    code = response.get("code", 0)
    if code and not 200 <= code < 300:
        raise ToolError(
            {"status_code": code or 502, "message": f"GET {api_path} failed: {response.get('msg', 'Unknown error')}"}
        )
    return response.get("msg", {})


async def _manage_resource(
    ctx: Context,
    api_base: str,
    resource_label: str,
    name: str | None,
    action_type: str,
    payload: dict,
    scope_id: str | None,
    device_function: str | None,
    confirmed: bool,
) -> dict | str:
    """Generic POST/PATCH/DELETE for /network-config/v1alpha1/{api_base}[/{name}].

    When ``name`` is ``None`` or empty, the URL omits the trailing
    ``/{name}`` segment so singleton config objects (e.g. ``system-info``,
    ``firmware-compliance``) can use the same helper.
    """
    if action_type not in ("create", "update", "delete"):
        raise ToolError(
            {
                "status_code": 400,
                "message": f"Invalid action_type: {action_type}. Must be 'create', 'update', or 'delete'.",
            }
        )

    method_map = {"create": "POST", "update": "PATCH", "delete": "DELETE"}
    api_method = method_map[action_type]
    api_path = f"network-config/v1alpha1/{api_base}/{name}" if name else f"network-config/v1alpha1/{api_base}"

    action_wording = {"create": "create a new", "update": "update an existing", "delete": "delete an existing"}[
        action_type
    ]

    target_phrase = f"{resource_label} '{name}'" if name else f"singleton {resource_label}"
    if action_type != "create" and not confirmed:
        elicitation_response = await elicitation_handler(
            message=f"The LLM wants to {action_wording} {target_phrase}. Do you accept?",
            ctx=ctx,
        )
        if elicitation_response.action == "decline":
            if await ctx.get_state("elicitation_mode") == "chat_confirm":
                return {
                    "status": "confirmation_required",
                    "message": (
                        f"This operation will {action_wording} {target_phrase}. "
                        "Please confirm with the user before proceeding. "
                        "Call this tool again with confirmed=true after the user confirms."
                    ),
                }
            return {"message": "Action declined by user."}
        elif elicitation_response.action == "cancel":
            return {"message": "Action canceled by user."}

    conn = get_central_conn(ctx)

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

    msg = response.get("msg", "Unknown error")
    raise ToolError({"status_code": code or 502, "message": f"{action_type} {resource_label} {name!r} failed: {msg}"})


async def _operation_request(
    ctx: Context,
    api_method: str,
    api_path: str,
    payload: dict | None = None,
    confirmed: bool = False,
    label: str = "",
) -> dict | str:
    """Generic single-shot request for an irregular Central operation endpoint.

    Unlike :func:`_manage_resource`, this helper targets a fully-formed
    ``api_path`` (the caller has already substituted any path params and chosen
    the version prefix) and a fixed ``api_method`` — there is no
    ``action_type``/CRUD verb mapping. Used by the generated operation tools
    (fixed-verb actions like ``revoke``/``upload``/``import``/``export``/``bulk``
    and job/status reads).

    For write methods (POST/PATCH/PUT/DELETE) when ``not confirmed``, runs the
    same elicitation flow ``_manage_resource`` uses (respecting ``chat_confirm``
    state). GET requests skip elicitation. Returns ``{"status": "success", ...}``
    on 2xx; raises :class:`ToolError` (``{"status_code", "message"}``) on any
    non-2xx so the calling AI sees a real failure rather than an ok-wrapped
    error dict (elicitation decline/cancel still return ordinary dicts).
    """
    method = api_method.upper()
    is_write = method in ("POST", "PATCH", "PUT", "DELETE")

    if is_write and not confirmed:
        target_phrase = label or api_path
        elicitation_response = await elicitation_handler(
            message=f"The LLM wants to perform '{method}' on {target_phrase}. Do you accept?",
            ctx=ctx,
        )
        if elicitation_response.action == "decline":
            if await ctx.get_state("elicitation_mode") == "chat_confirm":
                return {
                    "status": "confirmation_required",
                    "message": (
                        f"This operation will perform '{method}' on {target_phrase}. "
                        "Please confirm with the user before proceeding. "
                        "Call this tool again with confirmed=true after the user confirms."
                    ),
                }
            return {"message": "Action declined by user."}
        elif elicitation_response.action == "cancel":
            return {"message": "Action canceled by user."}

    conn = get_central_conn(ctx)
    # Send the request body for any write method that carries one. Unlike CRUD
    # ``_manage_resource`` (which never bodies a delete), operation endpoints
    # such as ``.../bulk`` are DELETEs whose payload (``{"items": [...]}``)
    # selects the targets, so DELETE bodies must pass through when supplied.
    api_data = payload if is_write else None

    logger.info("Central operation: {} — path: {}", method, api_path)

    response = retry_central_command(
        central_conn=conn,
        api_method=method,
        api_path=api_path,
        api_data=api_data,
    )

    code = response.get("code", 0)
    if 200 <= code < 300:
        return {"status": "success", "method": method, "path": api_path, "data": response.get("msg", {})}

    msg = response.get("msg", "Unknown error")
    raise ToolError({"status_code": code or 502, "message": f"{method} {api_path} failed: {msg}"})


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
