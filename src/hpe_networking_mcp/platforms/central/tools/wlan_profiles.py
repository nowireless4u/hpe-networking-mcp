"""Aruba Central WLAN SSID profile tools — read and write.

Provides tools to list, read, create, update, and delete WLAN SSID
profiles in Central's configuration library via the network-config API.
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
async def central_get_wlan_profiles(
    ctx: Context,
    ssid: str | None = None,
) -> dict | list | str:
    """
    Get WLAN SSID profiles from Central's configuration library.

    Returns the full configuration data for WLAN profiles, including
    auth settings, VLAN, encryption, radio bands, and all profile options.

    Use this tool when you need WLAN configuration details for migration,
    comparison, or auditing. For monitoring data (connected clients, health),
    use central_get_wlans instead.

    Parameters:
        ssid: Specific SSID name to retrieve. If omitted, returns all profiles.

    Returns:
        Single profile dict if ssid specified, or list of all profiles.
    """
    conn = ctx.lifespan_context["central_conn"]

    api_path = f"network-config/v1alpha1/wlan-ssids/{ssid}" if ssid else "network-config/v1alpha1/wlan-ssids"

    response = retry_central_command(
        central_conn=conn,
        api_method="GET",
        api_path=api_path,
    )
    return response.get("msg", {})


@mcp.tool(annotations=WRITE_DELETE, tags={"central_write_delete"})
async def central_manage_wlan_profile(
    ctx: Context,
    ssid: Annotated[
        str,
        Field(description="The SSID name. Used as the identifier in the API path."),
    ],
    action_type: Annotated[
        str,
        Field(description="Action to perform: 'create', 'update', or 'delete'."),
    ],
    payload: Annotated[
        dict,
        Field(
            description=(
                "WLAN SSID profile payload. For create/update: the full or partial "
                "profile configuration. Key fields include essid.name, opmode, "
                "forward-mode, vlan-name, personal-security, dot1x, rf-band. "
                "For delete: payload is ignored."
            )
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
    Create, update, or delete a WLAN SSID profile in Central's library.

    The SSID name is the identifier — it appears in the API path.
    Profiles created here are added to the Central WLAN library.
    They must be assigned to scopes (Global, site collections, or sites)
    separately to take effect on APs.

    IMPORTANT: Do not migrate tunneled SSIDs (forward-mode != FORWARD_MODE_BRIDGE).
    """
    if action_type not in ("create", "update", "delete"):
        raise ToolError(f"Invalid action_type: {action_type}. Must be 'create', 'update', or 'delete'.")

    api_path = f"network-config/v1alpha1/wlan-ssids/{ssid}"

    action_wording = {
        "create": "create a new",
        "update": "update an existing",
        "delete": "delete an existing",
    }[action_type]

    # Confirm for update and delete only
    if action_type != "create" and not confirmed:
        elicitation_response = await elicitation_handler(
            message=(f"The LLM wants to {action_wording} WLAN profile '{ssid}'. Do you accept?"),
            ctx=ctx,
        )
        if elicitation_response.action == "decline":
            if await ctx.get_state("elicitation_mode") == "chat_confirm":
                return {
                    "status": "confirmation_required",
                    "message": (
                        f"This operation will {action_wording} WLAN profile '{ssid}'. "
                        "Please confirm with the user before proceeding. "
                        "Call this tool again with confirmed=true after the user confirms."
                    ),
                }
            return {"message": "Action declined by user."}
        elif elicitation_response.action == "cancel":
            return {"message": "Action canceled by user."}

    conn = ctx.lifespan_context["central_conn"]

    method_map = {"create": "POST", "update": "PUT", "delete": "DELETE"}
    api_method = method_map[action_type]

    api_data: dict = {}
    if action_type != "delete":
        api_data = payload

    logger.info("Central WLAN: {} '{}' — path: {}", api_method, ssid, api_path)

    response = retry_central_command(
        central_conn=conn,
        api_method=api_method,
        api_path=api_path,
        api_data=api_data,
    )

    code = response.get("code", 0)
    if 200 <= code < 300:
        return {
            "status": "success",
            "action": action_type,
            "ssid": ssid,
            "data": response.get("msg", {}),
        }

    return {
        "status": "error",
        "code": code,
        "message": response.get("msg", "Unknown error"),
    }
