"""Aruba Central Gateway Cluster Intent Service (GCIS) tools.

GCIS enables policy-driven orchestration of gateway clusters across
organizational scopes (global / Site Collection / Site). An intent
profile declares cluster behavior (cluster-mode CM_SITE vs CM_MANUAL,
multicast VLAN, heartbeat threshold, persona / device-type, redundancy
mode, CoA-VRRP) and Central auto-forms realized cluster profiles per
the intent — see central_get_gateway_clusters / central_manage_gateway_cluster
for the realized side.

For AOS 8 → AOS 10 migration: each AOS 8 cluster_prof becomes a
gw-cluster-intent profile. The cluster-mode is derived from AP-adoption
signals (see aos-migration skill, Stage 7 Step 4).

API: GET/POST/PATCH/DELETE /network-config/v1alpha1/gw-cluster-intent-config
"""

from typing import Annotated

from fastmcp import Context
from fastmcp.exceptions import ToolError
from loguru import logger
from mcp.types import ToolAnnotations
from pydantic import Field

from hpe_networking_mcp.middleware.elicitation import elicitation_handler
from hpe_networking_mcp.platforms.central._registry import tool
from hpe_networking_mcp.platforms.central.tools import READ_ONLY
from hpe_networking_mcp.platforms.central.utils import retry_central_command

WRITE_DELETE = ToolAnnotations(
    readOnlyHint=False,
    destructiveHint=True,
    idempotentHint=False,
    openWorldHint=True,
)


@tool(annotations=READ_ONLY)
async def central_get_gateway_cluster_intent_profiles(
    ctx: Context,
    name: str | None = None,
    scope_id: str | None = None,
) -> dict | list | str:
    """Get Gateway Cluster Intent (GCIS) profile configurations from Central.

    GCIS profiles define cluster orchestration policy at a scope.
    Key fields per profile:
      - cluster-mode: CM_SITE (auto-clustering at Site level) or CM_MANUAL
        (auto-formation disabled)
      - device-type: persona — MOBILITY_GW (default), BRANCH_GW, VPNC, etc.
      - multicast-vlan, heartbeat-threshold, ipv6-enable, coa-enable
      - default-gateway-mode: 1:1 redundancy (active/standby pair)
      - uplink-tracking, uplink-sharing, coa-vrrp

    Parameters:
        name: Specific profile name to retrieve. If omitted, returns all
            profiles at the queried scope.
        scope_id: Optional scope ID to query. If omitted, queries the
            org root (SHARED scope). Get scope IDs from
            central_get_scope_tree.

    Returns:
        Single profile dict if name specified, else list of all profiles.
    """
    conn = ctx.lifespan_context["central_conn"]
    api_path = (
        f"network-config/v1alpha1/gw-cluster-intent-config/{name}"
        if name
        else "network-config/v1alpha1/gw-cluster-intent-config"
    )

    api_params: dict = {}
    if scope_id:
        api_params["scope-id"] = scope_id

    response = retry_central_command(
        central_conn=conn,
        api_method="GET",
        api_path=api_path,
        api_params=api_params if api_params else None,
    )
    return response.get("msg", {})


@tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_gateway_cluster_intent_profile(
    ctx: Context,
    name: Annotated[
        str,
        Field(description="The GCIS intent profile name. Used as the identifier in the API path."),
    ],
    action_type: Annotated[
        str,
        Field(description="Action to perform: 'create', 'update', or 'delete'."),
    ],
    payload: Annotated[
        dict,
        Field(
            description=(
                "GCIS profile payload. For delete: pass empty dict {}. "
                "For create/update, key fields:\n"
                "- cluster-mode: 'CM_SITE' (auto-cluster at Site level) or "
                "'CM_MANUAL' (disabled — operator creates clusters manually)\n"
                "- device-type: persona, defaults to 'MOBILITY_GW'. Other "
                "wireless-relevant values: 'BRANCH_GW', 'VPNC', 'CAMPUS_AP', "
                "'MICROBRANCH_AP'.\n"
                "- multicast-vlan: VLAN ID (1-4094) for upstream multicast forwarding\n"
                "- heartbeat-threshold: ms (500-65535)\n"
                "- ipv6-enable: bool\n"
                "- coa-enable: bool — enable CoA (Change of Authorization)\n"
                "- coa-vrrp: {vlan, id, passphrase} when CoA-VRRP is needed\n"
                "- default-gateway-mode: bool — enable 1:1 redundancy (only 2 gateways "
                "per profile, leader+standby). Required for BRANCH_GW.\n"
                "- uplink-tracking, uplink-sharing: bool — for BRANCH_GW with "
                "default-gateway-mode enabled\n"
                "- description: user comment\n"
                "Use central_get_gateway_cluster_intent_profiles to inspect "
                "existing profiles as reference."
            )
        ),
    ],
    scope_id: Annotated[
        str | None,
        Field(
            description=(
                "Scope ID for scoped (LOCAL) intent profiles. If omitted, "
                "creates a SHARED (org-root) profile. Get scope IDs from "
                "central_get_scope_tree. Site-scoped intent profiles are "
                "the typical pattern for CM_SITE clusters at a specific Site."
            ),
            default=None,
        ),
    ],
    device_function: Annotated[
        str | None,
        Field(
            description=(
                "Device function for scoped profiles. Required when scope_id "
                "is provided. Same enum as the device-type field (MOBILITY_GW, "
                "BRANCH_GW, VPNC, CAMPUS_AP, MICROBRANCH_AP, ALL, etc.)."
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
    """Create, update, or delete a Gateway Cluster Intent profile in Central.

    GCIS intent profiles drive auto-formation of gateway clusters at the
    bound scope. Setting cluster-mode=CM_SITE causes Central to
    auto-create realized cluster profiles (named auto_*) for each Site
    under the scope. CM_MANUAL disables auto-formation; operators create
    realized cluster profiles manually via central_manage_gateway_cluster.
    """
    if action_type not in ("create", "update", "delete"):
        raise ToolError(f"Invalid action_type: {action_type}. Must be 'create', 'update', or 'delete'.")

    api_path = f"network-config/v1alpha1/gw-cluster-intent-config/{name}"
    method_map = {"create": "POST", "update": "PATCH", "delete": "DELETE"}
    api_method = method_map[action_type]

    action_wording = {
        "create": "create a new",
        "update": "update an existing",
        "delete": "delete an existing",
    }[action_type]

    if action_type != "create" and not confirmed:
        elicitation_response = await elicitation_handler(
            message=(f"The LLM wants to {action_wording} GCIS intent profile '{name}'. Do you accept?"),
            ctx=ctx,
        )
        if elicitation_response.action == "decline":
            if await ctx.get_state("elicitation_mode") == "chat_confirm":
                return {
                    "status": "confirmation_required",
                    "message": (
                        f"This operation will {action_wording} GCIS intent profile '{name}'. "
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

    api_data: dict = {}
    if action_type != "delete":
        api_data = payload

    logger.info("Central GCIS intent profile: {} '{}' — path: {}", api_method, name, api_path)

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
