"""Aruba Central realized Gateway Cluster profile tools.

Realized gateway cluster profiles bind specific gateway members (by MAC)
into a cluster operating as a single entity for HA + service continuity.
For auto-cluster (CM_SITE) profiles, Central populates these
automatically from a GCIS intent profile (auto_* naming prefix). For
manual clusters (CM_MANUAL), operators create the profile and add
member gateways explicitly.

For AOS 8 → AOS 10 migration: each AOS 8 cluster_prof translates to a
gw-cluster profile; cluster_prof.cluster_controller[].ip resolves via
Central inventory to MACs on ipv4-gateways[].mac. VRRP, heartbeat,
multicast-VLAN, and CoA-VRRP fields map directly. See central_manage_gateway_cluster_intent_profile
for the policy/intent layer that drives auto-cluster formation.

API: GET/POST/PATCH/DELETE /network-config/v1alpha1/gateway-clusters
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
async def central_get_gateway_clusters(
    ctx: Context,
    name: str | None = None,
    scope_id: str | None = None,
) -> dict | list | str:
    """Get realized Gateway Cluster profile configurations from Central.

    Realized cluster profiles contain the actual member gateways and
    cluster runtime configuration. Key fields per profile:
      - name: cluster profile name (auto_* prefix indicates GCIS-managed
        auto-cluster; non-auto names are manual clusters)
      - auto-cluster: bool — true for GCIS-managed clusters; false for
        manual cluster profiles
      - ipv4-gateways / ipv6-gateways: list of member gateways keyed by MAC
        (up to 12 per profile; some platforms restrict further)
      - one-to-one-redundancy: bool — 1:1 active/standby redundancy
      - heartbeat-threshold: ms (500-65535)
      - multicast-vlan, coa-vrrp, ipv6-enable
      - uplink-tracking: leader selection by active uplink count

    Parameters:
        name: Specific cluster profile name. If omitted, returns all
            cluster profiles at the queried scope.
        scope_id: Optional scope ID. If omitted, queries the org root.
            Get scope IDs from central_get_scope_tree.

    Returns:
        Single profile dict if name specified, else list of all profiles.
    """
    conn = ctx.lifespan_context["central_conn"]
    api_path = (
        f"network-config/v1alpha1/gateway-clusters/{name}" if name else "network-config/v1alpha1/gateway-clusters"
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
async def central_manage_gateway_cluster(
    ctx: Context,
    name: Annotated[
        str,
        Field(
            description=(
                "The gateway cluster profile name. Used as the identifier "
                "in the API path. Manual cluster profile names must NOT "
                "start with 'auto_' (reserved for GCIS-managed clusters) "
                "and must not contain spaces. Max 31 chars."
            )
        ),
    ],
    action_type: Annotated[
        str,
        Field(description="Action to perform: 'create', 'update', or 'delete'."),
    ],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Cluster profile payload. For delete: pass empty dict {}. "
                "For create/update, key fields:\n"
                "- ipv4-gateways: list of {mac, ...} entries — gateway members "
                "by MAC address. Up to 12 per profile (fewer on some platforms).\n"
                "- ipv6-gateways: list of {mac, ...} entries for IPv6\n"
                "- auto-cluster: bool. False for MANUAL clusters; true is "
                "reserved for GCIS-managed clusters and should not be set "
                "manually.\n"
                "- one-to-one-redundancy: bool — only 2 gateways allowed when "
                "true (active+standby)\n"
                "- multicast-vlan: VLAN ID (1-4094)\n"
                "- heartbeat-threshold: ms (500-65535)\n"
                "- ipv6-enable: bool — cannot be toggled after profile creation\n"
                "- uplink-tracking: bool — leader selected by active uplinks "
                "(1:1 redundancy only)\n"
                "- coa-vrrp: {vlan, id, passphrase} when CoA-VRRP needed\n"
                "- description: user comment\n"
                "Use central_get_gateway_clusters to inspect existing profiles "
                "as reference."
            )
        ),
    ],
    scope_id: Annotated[
        str | None,
        Field(
            description=(
                "Scope ID for scoped (LOCAL) cluster profiles. If omitted, "
                "creates a SHARED (org-root) profile. Get scope IDs from "
                "central_get_scope_tree."
            ),
            default=None,
        ),
    ],
    device_function: Annotated[
        str | None,
        Field(
            description=(
                "Device function for scoped profiles. Required when scope_id "
                "is provided. Typically 'MOBILITY_GW', 'BRANCH_GW', or 'VPNC' "
                "for cluster profiles."
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
    """Create, update, or delete a realized Gateway Cluster profile in Central.

    For auto-clusters (GCIS-managed via central_manage_gateway_cluster_intent_profile),
    Central creates and maintains the realized profile automatically (auto_* names).
    Manual clusters are created here directly with explicit member gateways.
    """
    if action_type not in ("create", "update", "delete"):
        raise ToolError(f"Invalid action_type: {action_type}. Must be 'create', 'update', or 'delete'.")

    api_path = f"network-config/v1alpha1/gateway-clusters/{name}"
    method_map = {"create": "POST", "update": "PATCH", "delete": "DELETE"}
    api_method = method_map[action_type]

    action_wording = {
        "create": "create a new",
        "update": "update an existing",
        "delete": "delete an existing",
    }[action_type]

    if action_type != "create" and not confirmed:
        elicitation_response = await elicitation_handler(
            message=(f"The LLM wants to {action_wording} gateway cluster profile '{name}'. Do you accept?"),
            ctx=ctx,
        )
        if elicitation_response.action == "decline":
            if await ctx.get_state("elicitation_mode") == "chat_confirm":
                return {
                    "status": "confirmation_required",
                    "message": (
                        f"This operation will {action_wording} gateway cluster profile '{name}'. "
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

    logger.info("Central gateway cluster: {} '{}' — path: {}", api_method, name, api_path)

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
