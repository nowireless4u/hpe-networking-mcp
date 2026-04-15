"""Unified WLAN profile management tool.

Cross-platform entry point for all WLAN create/update/delete operations.
Checks both Mist and Central to detect cross-platform scenarios and
returns the appropriate sync workflow when needed.
"""

from typing import Annotated

import mistapi
from fastmcp import Context
from loguru import logger
from pydantic import Field

from hpe_networking_mcp.platforms.central.utils import retry_central_command

# Mist → Central sync workflow returned when SSID exists in Mist
_MIST_TO_CENTRAL_WORKFLOW = """
This SSID already exists in Mist. To sync it to Central correctly, \
follow these steps:

**STEP 1** — Call `mist_get_self(action_type=account_info)` to get the \
correct Mist org_id.

**STEP 2** — Call `mist_get_configuration_objects(org_id=<org_id>, \
object_type=org_wlans, name="{ssid}")` to get the full WLAN config. \
Note the `template_id` field.

**STEP 3** — Look up the template assignment:
a. Call `mist_get_configuration_objects(org_id=<org_id>, \
object_type=org_wlantemplates, object_id=<template_id>)` to get the \
template name, `sitegroup_ids`, and `site_ids`.
b. For each sitegroup_id, call `mist_get_configuration_objects(org_id=\
<org_id>, object_type=org_sitegroups, object_id=<sitegroup_id>)` to \
get the site group name.
c. For each site_id, call `mist_get_configuration_objects(org_id=\
<org_id>, object_type=org_sites, object_id=<site_id>)` to get the \
site name.

**STEP 4** — Map Mist fields to Central format:
- auth.type="psk" + pairwise=["wpa2-ccmp"] → opmode="WPA2_PERSONAL"
- auth.type="psk" + pairwise=["wpa3"] → opmode="WPA3_SAE"
- auth.type="eap" + pairwise=["wpa2-ccmp"] → opmode="WPA2_ENTERPRISE"
- auth.type="eap" + pairwise=["wpa3","wpa2-ccmp"] → \
opmode="WPA3_ENTERPRISE_CCM_128"
- dynamic_psk.enabled=true → opmode="WPA2_MPSK_AES"
- bands array → rf-band enum (["24","5"]→"24GHZ_5GHZ", \
["24","5","6"]→"BAND_ALL")
- vlan_id → vlan-id-range, rateset → data rate profile
- auth.psk → personal-security.wpa-passphrase
- roam_mode="11r" → dot11r=true

**STEP 5** — Call `central_manage_wlan_profile(ssid="{ssid}", \
action_type="create", payload=<mapped>)` to create the profile.

**STEP 6 — Assignment (REQUIRED — do not skip):**
Report to the user where this WLAN is assigned in Mist and where it \
needs to be assigned in Central:
- "In Mist, this WLAN is in template '<name>' assigned to site groups: \
<list> and/or sites: <list>."
- "In Central, assign the profile to matching site collections: <list> \
and/or sites: <list>."
If a matching Central site collection does not exist, tell the user it \
needs to be created first.
"""

# Central → Mist sync workflow returned when SSID exists in Central
_CENTRAL_TO_MIST_WORKFLOW = """
This SSID already exists in Central. To sync it to Mist correctly, \
follow these steps:

**STEP 1** — Call `central_get_wlan_profiles(ssid="{ssid}")` to get \
the full profile config.

**STEP 2** — Resolve Central aliases and named references:
a. If essid.use-alias is set, call `central_get_aliases(alias_name=\
<alias>)` to get the broadcasted SSID name.
b. If personal-security.wpa-passphrase-alias is set, resolve via \
`central_get_aliases`.
c. If auth-server-group is set, call `central_get_server_groups(name=\
<group>)` to get RADIUS servers. Resolve any aliased hosts via \
`central_get_aliases`.
d. If vlan-name is set, call `central_get_named_vlans(name=<vlan>)` \
to resolve the VLAN ID.

**STEP 3** — Call `mist_get_self(action_type=account_info)` to get \
the correct Mist org_id.

**STEP 4** — Map Central fields to Mist format:
- opmode="WPA2_PERSONAL" → auth.type="psk", pairwise=["wpa2-ccmp"]
- opmode="WPA3_SAE" → auth.type="psk", pairwise=["wpa3"]
- opmode="WPA2_ENTERPRISE" → auth.type="eap", pairwise=["wpa2-ccmp"]
- rf-band enum → bands array
- Use template variables ({{auth_srv1}}) for RADIUS, never hardcode IPs
- Define resolved addresses in site vars

**STEP 5** — Create a Mist WLAN template using \
`mist_change_org_configuration_objects(action_type="create", \
object_type="wlantemplates", payload=...)`, then create the WLAN \
inside it with `object_type="wlans"` and the new template_id.

**STEP 6 — Assignment (REQUIRED — do not skip):**
Check what scope/site collection the Central WLAN is assigned to. \
Assign the Mist WLAN template to matching site groups. Report: \
"In Central, this WLAN is assigned to scope: <scope>. In Mist, \
assign the template to site group: <matching group>."
"""

# Both platforms have it
_BOTH_PLATFORMS_WORKFLOW = """
This SSID exists on BOTH platforms:
- **Mist**: {mist_status}
- **Central**: {central_status}

Compare the configurations and ask the user:
1. "Use Mist as source" (update Central to match Mist)
2. "Use Central as source" (update Mist to match Central)
3. "Skip — leave both as-is"

To compare, retrieve the full config from both platforms:
- Call `mist_get_configuration_objects(org_id=<org_id>, \
object_type=org_wlans, name="{ssid}")` for Mist config
- The Central config is: {central_status}

Then show a side-by-side table of differences.
"""


def register(mcp):
    """Register the unified manage_wlan_profile tool."""

    @mcp.tool(
        annotations={
            "title": "Manage WLAN Profile",
            "readOnlyHint": False,
            "destructiveHint": True,
            "openWorldHint": True,
            "idempotentHint": False,
        },
        tags={"central_write_delete", "mist_write_delete"},
    )
    async def manage_wlan_profile(
        ctx: Context,
        ssid: Annotated[
            str,
            Field(
                description="The SSID name to create, update, delete, or sync.",
            ),
        ],
        action_type: Annotated[
            str,
            Field(
                description=(
                    "Action to perform: 'create', 'update', 'delete', or 'sync'. "
                    "Use 'sync' to compare the SSID across both platforms. "
                    "Use 'create' to add a new SSID — the tool will check both "
                    "platforms and guide you if the SSID already exists elsewhere."
                ),
            ),
        ],
        target_platform: Annotated[
            str,
            Field(
                description=(
                    "Target platform for the operation: 'central', 'mist', or "
                    "'both'. Where should the SSID be created/modified? If the "
                    "user says 'add to Central' → 'central'. If 'add to Mist' "
                    "→ 'mist'. If 'sync' or unclear → 'both'."
                ),
                default="both",
            ),
        ],
        payload: Annotated[
            dict,
            Field(
                description=(
                    "WLAN profile payload for create/update. Can be in either "
                    "Mist or Central format — the sync workflow will handle "
                    "translation. For delete/sync, pass an empty dict {}."
                ),
                default_factory=dict,
            ),
        ],
    ) -> dict:
        """Manage WLAN profiles across Mist and Central.

        This is the primary tool for all WLAN create, update, delete,
        and sync operations. It automatically detects cross-platform
        scenarios and returns the correct workflow.

        When the user asks to add, copy, port, sync, or migrate a WLAN
        between platforms, always use this tool. It checks both Mist
        and Central for the SSID and guides you through the correct
        translation and assignment steps.
        """
        if action_type not in ("create", "update", "delete", "sync"):
            return {
                "status": "error",
                "message": f"Invalid action_type '{action_type}'. Must be 'create', 'update', 'delete', or 'sync'.",
            }

        # Check both platforms for the SSID
        mist_wlan = await _find_mist_wlan(ctx, ssid)
        central_profile = _find_central_profile(ctx, ssid)

        exists_mist = mist_wlan is not None
        exists_central = central_profile is not None

        logger.info(
            "manage_wlan_profile: ssid='{}' action='{}' target='{}' exists_mist={} exists_central={}",
            ssid,
            action_type,
            target_platform,
            exists_mist,
            exists_central,
        )

        # --- Sync action: always compare both platforms ---
        if action_type == "sync":
            if exists_mist and exists_central:
                return {
                    "status": "sync_compare",
                    "message": _BOTH_PLATFORMS_WORKFLOW.format(
                        ssid=ssid,
                        mist_status="found",
                        central_status="found",
                    ),
                    "mist_wlan": mist_wlan,
                    "central_profile": central_profile,
                }
            if exists_mist and not exists_central:
                return {
                    "status": "sync_mist_to_central",
                    "message": _MIST_TO_CENTRAL_WORKFLOW.format(ssid=ssid),
                }
            if exists_central and not exists_mist:
                return {
                    "status": "sync_central_to_mist",
                    "message": _CENTRAL_TO_MIST_WORKFLOW.format(ssid=ssid),
                }
            return {
                "status": "not_found",
                "message": f"SSID '{ssid}' not found on either platform. Nothing to sync.",
            }

        # --- Create action: detect cross-platform scenarios ---
        if action_type == "create":
            if target_platform == "central" and exists_mist:
                return {
                    "status": "cross_platform_detected",
                    "message": _MIST_TO_CENTRAL_WORKFLOW.format(ssid=ssid),
                }
            if target_platform == "mist" and exists_central:
                return {
                    "status": "cross_platform_detected",
                    "message": _CENTRAL_TO_MIST_WORKFLOW.format(ssid=ssid),
                }
            if target_platform == "both":
                if exists_mist and not exists_central:
                    return {
                        "status": "cross_platform_detected",
                        "message": _MIST_TO_CENTRAL_WORKFLOW.format(ssid=ssid),
                    }
                if exists_central and not exists_mist:
                    return {
                        "status": "cross_platform_detected",
                        "message": _CENTRAL_TO_MIST_WORKFLOW.format(ssid=ssid),
                    }
                if exists_mist and exists_central:
                    return {
                        "status": "already_exists",
                        "message": _BOTH_PLATFORMS_WORKFLOW.format(
                            ssid=ssid,
                            mist_status="found",
                            central_status="found",
                        ),
                        "mist_wlan": mist_wlan,
                        "central_profile": central_profile,
                    }

            # Truly new SSID — tell AI to use the platform-specific tool
            return {
                "status": "new_ssid",
                "message": (
                    f"SSID '{ssid}' does not exist on either platform. "
                    f"Target platform: {target_platform}. "
                    "Proceed with creating the WLAN profile using the "
                    "platform-specific tool:\n"
                    "- Central: call `central_manage_wlan_profile("
                    f"ssid='{ssid}', action_type='create', "
                    "source_platform='central', payload=<config>)`\n"
                    "- Mist: call `mist_change_org_configuration_objects("
                    "action_type='create', object_type='wlans', "
                    "payload=<config>)`"
                ),
            }

        # --- Update/delete: pass through to platform-specific tools ---
        return {
            "status": "passthrough",
            "message": (
                f"For '{action_type}' operations, use the platform-specific "
                "tool directly:\n"
                "- Central: `central_manage_wlan_profile(ssid='"
                f"{ssid}', action_type='{action_type}', ...)`\n"
                "- Mist: `mist_change_org_configuration_objects("
                f"action_type='{action_type}', object_type='wlans', ...)`"
            ),
            "exists_mist": exists_mist,
            "exists_central": exists_central,
        }


async def _find_mist_wlan(ctx: Context, ssid: str) -> dict | None:
    """Check if an SSID exists in Mist. Returns WLAN dict or None."""
    session = ctx.lifespan_context.get("mist_session")
    org_id = ctx.lifespan_context.get("mist_org_id")
    if not session or not org_id:
        return None

    try:
        response = mistapi.api.v1.orgs.wlans.listOrgWlans(
            session,
            org_id=org_id,
        )
        if response.status_code == 200 and isinstance(response.data, list):
            for wlan in response.data:
                if wlan.get("ssid") == ssid:
                    return wlan
    except Exception as e:
        logger.warning("manage_wlan: failed to check Mist for '{}' — {}", ssid, e)
    return None


def _find_central_profile(ctx: Context, ssid: str) -> dict | None:
    """Check if an SSID exists in Central. Returns profile dict or None."""
    conn = ctx.lifespan_context.get("central_conn")
    if not conn:
        return None

    try:
        response = retry_central_command(
            central_conn=conn,
            api_method="GET",
            api_path=f"network-config/v1alpha1/wlan-ssids/{ssid}",
        )
        code = response.get("code", 0)
        if 200 <= code < 300:
            return response.get("msg", {})
    except Exception as e:
        logger.warning("manage_wlan: failed to check Central for '{}' — {}", ssid, e)
    return None
