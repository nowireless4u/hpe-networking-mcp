"""Aruba Central WLAN SSID profile tools — read and write.

Provides tools to list, read, create, update, and delete WLAN SSID
profiles in Central's configuration library via the network-config API.
"""

from typing import Annotated

from fastmcp import Context
from fastmcp.exceptions import ToolError
from loguru import logger
from pydantic import Field

from hpe_networking_mcp.platforms._common.annotations import Capability
from hpe_networking_mcp.platforms.central._registry import tool
from hpe_networking_mcp.platforms.central.utils import get_central_conn, retry_central_command


@tool(capability=Capability.READ)
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
    conn = get_central_conn(ctx)

    api_path = f"network-config/v1alpha1/wlan-ssids/{ssid}" if ssid else "network-config/v1alpha1/wlan-ssids"

    response = await retry_central_command(
        central_conn=conn,
        api_method="GET",
        api_path=api_path,
    )
    return response.get("msg", {})


@tool(capability=Capability.WRITE_DELETE)
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
                "WLAN SSID profile payload.\n\n"
                "For 'update' (default, partial-patch): pass ONLY the fields you "
                "want to change. The tool issues PATCH against Central, which "
                "merges your payload with the existing profile server-side — "
                "untouched fields are preserved.\n\n"
                "For 'update' with replace_existing=True: payload must be the "
                "full profile. Any field not in the payload will be dropped "
                "from the stored profile. Use with extreme care.\n\n"
                "For 'create': full payload required.\n\n"
                "For 'delete': payload is ignored.\n\n"
                "Key fields and their valid values:\n"
                "- essid: {name: str} or {alias: str, use-alias: true}\n"
                "- opmode (REQUIRED on create): OPEN, WPA2_PERSONAL, WPA3_SAE, "
                "WPA2_ENTERPRISE, WPA3_ENTERPRISE_CCM_128, WPA3_ENTERPRISE_GCM_256, "
                "WPA3_ENTERPRISE_CNSA, WPA_ENTERPRISE, WPA_PERSONAL, WPA2_MPSK_AES, "
                "WPA2_MPSK_LOCAL, ENHANCED_OPEN, DPP, WPA2_PSK_AES_DPP, "
                "WPA2_AES_DPP, WPA3_SAE_DPP, WPA3_AES_CCM_128_DPP, "
                "WPA3_AES_GCM_256_DPP, BOTH_WPA_WPA2_PSK, BOTH_WPA_WPA2_DOT1X, "
                "STATIC_WEP, DYNAMIC_WEP. "
                "For PSK WLANs use WPA2_PERSONAL (not WPA2_PSK_AES which is invalid). "
                "For WPA3 PSK use WPA3_SAE. "
                "For WPA3+WPA2 transition use WPA3_SAE with wpa3-transition-mode-enable: true\n"
                "- personal-security: {passphrase-format: 'STRING', wpa-passphrase: str}\n"
                "- forward-mode: FORWARD_MODE_BRIDGE, FORWARD_MODE_L2\n"
                "- rf-band: BAND_ALL, 24GHZ_5GHZ, 5GHZ_6GHZ, 24GHZ_6GHZ, "
                "24GHZ, 5GHZ, 6GHZ, BAND_NONE\n"
                "- vlan-selector: NAMED_VLAN (with vlan-name) or VLAN_RANGES "
                "(with vlan-id-range: [str])\n"
                "- out-of-service: NONE, UPLINK_DOWN, TUNNEL_DOWN\n"
                "- broadcast-filter-ipv4: BCAST_FILTER_ARP, FILTER_NONE\n"
                "- See existing profiles via central_get_wlan_profiles for "
                "complete field reference."
            )
        ),
    ],
    replace_existing: Annotated[
        bool,
        Field(
            description=(
                "Destructive flag. When False (default), 'update' issues a "
                "PATCH that merges the payload with the existing profile — "
                "fields you don't include are preserved. When True, 'update' "
                "issues a PUT that replaces the entire profile — fields not in "
                "the payload will be dropped. Only set to True when you have "
                "the complete profile in the payload and genuinely want a "
                "wholesale swap."
            ),
            default=False,
        ),
    ] = False,
    confirmed: Annotated[
        bool,
        Field(
            description=(
                "Fallback confirmation flag — honored only when the client cannot "
                "show a confirmation prompt (the universal gate prompts otherwise)."
            ),
            default=False,
        ),
    ] = False,
) -> dict | str:
    """
    Create, update, or delete a WLAN SSID profile in Central's library.

    The SSID name is the identifier — it appears in the API path.
    Profiles are added to the Central WLAN library and must be assigned
    to scopes (Global, site collections, or sites) separately.

    Update semantics (default) use PATCH for partial updates: pass only
    the fields you want to change. Pass replace_existing=True to force a
    PUT full-replacement — use sparingly, since any field missing from
    the payload will be dropped from the stored profile.
    """
    if action_type not in ("create", "update", "delete"):
        raise ToolError(
            {
                "status_code": 400,
                "message": f"Invalid action_type: {action_type}. Must be 'create', 'update', or 'delete'.",
            }
        )

    # Validate opmode on create/update to catch cross-platform translation errors
    if action_type in ("create", "update") and "opmode" in payload:
        valid_opmodes = {
            "OPEN",
            "WPA2_PERSONAL",
            "WPA2_ENTERPRISE",
            "ENHANCED_OPEN",
            "WPA3_SAE",
            "WPA3_ENTERPRISE_CCM_128",
            "WPA3_ENTERPRISE_GCM_256",
            "WPA3_ENTERPRISE_CNSA",
            "WPA_ENTERPRISE",
            "WPA_PERSONAL",
            "WPA2_MPSK_AES",
            "WPA2_MPSK_LOCAL",
            "DPP",
            "WPA2_PSK_AES_DPP",
            "WPA2_AES_DPP",
            "WPA3_SAE_DPP",
            "WPA3_AES_CCM_128_DPP",
            "WPA3_AES_GCM_256_DPP",
            "BOTH_WPA_WPA2_PSK",
            "BOTH_WPA_WPA2_DOT1X",
            "STATIC_WEP",
            "DYNAMIC_WEP",
        }
        opmode = payload["opmode"]
        if opmode not in valid_opmodes:
            raise ToolError(
                {
                    "status_code": 400,
                    "message": (
                        f"Invalid opmode '{opmode}'. "
                        "If you are syncing a WLAN from Mist, use the "
                        "sync_wlans_mist_to_central prompt instead of calling this "
                        "tool directly — it handles opmode translation automatically. "
                        f"Valid opmodes: {', '.join(sorted(valid_opmodes))}"
                    ),
                }
            )

    api_path = f"network-config/v1alpha1/wlan-ssids/{ssid}"
    conn = get_central_conn(ctx)

    # Method selection: update defaults to PATCH (partial merge on the
    # server). replace_existing=True forces PUT (full replacement).
    method_map = {
        "create": "POST",
        "update": "PUT" if replace_existing else "PATCH",
        "delete": "DELETE",
    }
    api_method = method_map[action_type]

    api_data: dict = {}
    if action_type != "delete":
        api_data = payload

    logger.info("Central WLAN: {} '{}' — path: {}", api_method, ssid, api_path)

    response = await retry_central_command(
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
