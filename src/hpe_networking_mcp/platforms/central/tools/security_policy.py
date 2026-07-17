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
from pydantic import Field

from hpe_networking_mcp.platforms._common.url import path_seg
from hpe_networking_mcp.platforms.central.utils import get_central_conn, retry_central_command

# ---------------------------------------------------------------------------
# Shared config-read query parameters
#
# Every /network-config/v1alpha1/ GET endpoint documents the same eight query
# parameters. They are defined once here so each read tool advertises an
# identical, accurate schema. Descriptions come from the vendored OpenAPI spec.
#
# These are distinct from the write-side _SCOPE_ID_FIELD / _DEVICE_FUNCTION_FIELD
# below: on a write, scope_id selects where an object is *created*; on a read it
# selects which scope's configuration is *returned*.
# ---------------------------------------------------------------------------

_READ_VIEW_TYPE_FIELD = Field(
    description=(
        "'LOCAL' — configuration for a scope and one or more device functions "
        "(requires scope_id). 'LIBRARY' — shared objects in the library; for "
        "LIBRARY every other parameter except 'detailed' is ignored. "
        "Omit to use the API default."
    ),
    default=None,
)
_READ_OBJECT_TYPE_FIELD = Field(
    description=(
        "Retrieve 'LOCAL' or 'SHARED' configuration objects. Omit for both (the API default). "
        "This filters which objects come back — it does not select the scope; use scope_id for that."
    ),
    default=None,
)
_READ_SCOPE_ID_FIELD = Field(
    description=(
        "Return configuration at this scope ID. Mandatory when view_type='LOCAL'. "
        "Get scope IDs from central_get_scope_tree."
    ),
    default=None,
)
_READ_DEVICE_FUNCTION_FIELD = Field(
    description=(
        "Filter configuration to this device-function type. If omitted when "
        "view_type='LOCAL', the API defaults to all device functions. "
        "Valid: CAMPUS_AP, ACCESS_SWITCH, BRANCH_GW, MOBILITY_GW, CORE_SWITCH, AGG_SWITCH, ALL."
    ),
    default=None,
)
_READ_EFFECTIVE_FIELD = Field(
    description=(
        "True — return effective (hierarchically merged / inherited) configuration. "
        "False — return only the configuration committed at this scope."
    ),
    default=None,
)
_READ_DETAILED_FIELD = Field(
    description=(
        "True — annotate each returned object with its object type, scope, and device "
        "function. Useful when walking a scope hierarchy."
    ),
    default=None,
)
_READ_LIMIT_FIELD = Field(
    description="Pagination limit. Omit to use the API default page size.",
    default=None,
)
_READ_OFFSET_FIELD = Field(
    description="Pagination offset.",
    default=None,
)

# ---------------------------------------------------------------------------
# Factory helpers — avoid repeating the same CRUD logic across resources
# ---------------------------------------------------------------------------


async def _get_resource(
    ctx: Context,
    api_base: str,
    name: str | None,
    *,
    view_type: str | None = None,
    object_type: str | None = None,
    scope_id: str | None = None,
    device_function: str | None = None,
    effective: bool | None = None,
    detailed: bool | None = None,
    limit: int | None = None,
    offset: int | None = None,
) -> dict | list | str:
    """Generic GET for /network-config/v1alpha1/{api_base}[/{name}].

    The keyword-only arguments map to the query parameters documented on every
    ``network-config/v1alpha1`` GET endpoint. ``None`` values are omitted from
    the request, so the API's own defaults apply.

    Two upstream quirks are normalized here (both confirmed against the live
    API, which ignores unknown/incomplete query params rather than erroring):

    * ``limit`` is only honored when ``offset`` is also sent — on its own it is
      silently ignored and the full collection comes back. A ``limit`` without
      an ``offset`` therefore defaults the offset to 0 so the caller gets the
      page size they asked for instead of everything.
    * ``view_type='LOCAL'`` without a ``scope_id`` returns another scope's
      configuration instead of failing, so it is rejected here.

    Raises:
        ToolError: 400 when ``view_type='LOCAL'`` is requested without a
            ``scope_id``.
    """
    if view_type and view_type.upper() == "LOCAL" and not scope_id:
        raise ToolError(
            {
                "status_code": 400,
                "message": (
                    "view_type='LOCAL' requires scope_id — without it the API returns "
                    "a different scope's configuration instead of failing."
                ),
            }
        )

    if limit is not None and offset is None:
        offset = 0

    conn = get_central_conn(ctx)
    api_path = f"network-config/v1alpha1/{api_base}/{path_seg(name)}" if name else f"network-config/v1alpha1/{api_base}"
    api_params: dict = {
        "view-type": view_type,
        "object-type": object_type,
        "scope-id": scope_id,
        "device-function": device_function,
        "effective": effective,
        "detailed": detailed,
        "limit": limit,
        "offset": offset,
    }
    api_params = {k: v for k, v in api_params.items() if v is not None}
    response = await retry_central_command(
        central_conn=conn,
        api_method="GET",
        api_path=api_path,
        api_params=api_params or None,
    )
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
    api_path = f"network-config/v1alpha1/{api_base}/{path_seg(name)}" if name else f"network-config/v1alpha1/{api_base}"

    conn = get_central_conn(ctx)

    api_params: dict = {}
    if scope_id and device_function:
        api_params["object-type"] = "LOCAL"
        api_params["scope-id"] = scope_id
        api_params["device-function"] = device_function

    api_data = payload if action_type != "delete" else None

    logger.info("Central {}: {} '{}' — path: {}", resource_label, api_method, name, api_path)

    response = await retry_central_command(
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

    Confirmation is handled by the universal gate at the invoke-tool dispatch
    chokepoint (``confirmed`` is the fallback flag passed through by callers).
    Returns ``{"status": "success", ...}`` on 2xx; raises :class:`ToolError`
    (``{"status_code", "message"}``) on any non-2xx so the calling AI sees a
    real failure rather than an ok-wrapped error dict.
    """
    method = api_method.upper()
    is_write = method in ("POST", "PATCH", "PUT", "DELETE")

    conn = get_central_conn(ctx)
    # Send the request body for any write method that carries one. Unlike CRUD
    # ``_manage_resource`` (which never bodies a delete), operation endpoints
    # such as ``.../bulk`` are DELETEs whose payload (``{"items": [...]}``)
    # selects the targets, so DELETE bodies must pass through when supplied.
    api_data = payload if is_write else None

    logger.info("Central operation: {} — path: {}", method, api_path)

    response = await retry_central_command(
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
    description=(
        "Fallback confirmation flag — honored only when the client cannot "
        "show a confirmation prompt (the universal gate prompts otherwise)."
    ),
    default=False,
)
