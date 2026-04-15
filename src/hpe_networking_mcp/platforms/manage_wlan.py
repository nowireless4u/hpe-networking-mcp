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
**Opmode:**
- auth.type="psk" + pairwise=["wpa2-ccmp"] → opmode="WPA2_PERSONAL"
- auth.type="psk" + pairwise=["wpa3"] → opmode="WPA3_SAE"
- auth.type="eap" + pairwise=["wpa2-ccmp"] → opmode="WPA2_ENTERPRISE"
- auth.type="eap" + pairwise=["wpa3","wpa2-ccmp"] → \
opmode="WPA3_ENTERPRISE_CCM_128"
- dynamic_psk.enabled=true → opmode="WPA2_MPSK_AES"
**RF bands:**
- bands ["24","5"] → rf-band="24GHZ_5GHZ"
- bands ["24","5","6"] → rf-band="BAND_ALL"
- bands ["5"] → rf-band="5GHZ"
- bands ["5","6"] → rf-band="5GHZ_6GHZ"
**Data rates (use exact values — do NOT set custom rates):**
- rateset template="high-density" → g-legacy-rates: \
{{"basic-rates":["RATE_24MB","RATE_36MB"],"tx-rates":\
["RATE_24MB","RATE_36MB","RATE_48MB","RATE_54MB"]}}, \
a-legacy-rates: same values
- rateset template="no-legacy" → g-legacy-rates: \
{{"basic-rates":["RATE_12MB","RATE_24MB"],"tx-rates":\
["RATE_12MB","RATE_18MB","RATE_24MB","RATE_36MB","RATE_48MB",\
"RATE_54MB"]}}, a-legacy-rates: same values
- rateset template="compatible" → g-legacy-rates: \
{{"basic-rates":["RATE_1MB","RATE_2MB"],"tx-rates":\
["RATE_1MB","RATE_2MB","RATE_5_5MB","RATE_6MB","RATE_9MB",\
"RATE_11MB","RATE_12MB","RATE_18MB","RATE_24MB","RATE_36MB",\
"RATE_48MB","RATE_54MB"]}}, a-legacy-rates: {{"basic-rates":\
["RATE_6MB"],"tx-rates":["RATE_6MB","RATE_9MB","RATE_12MB",\
"RATE_18MB","RATE_24MB","RATE_36MB","RATE_48MB","RATE_54MB"]}}
**Other fields:**
- auth.psk → personal-security.wpa-passphrase
- vlan_id → vlan-id-range: ["<vlan_id>"], vlan-selector: "VLAN_RANGES"
- roam_mode="11r" → dot11r=true
- disable_11be=true → extremely-high-throughput: {{"enable": false}}
- arp_filter=true → broadcast-filter-ipv4: "BCAST_FILTER_ARP"
- isolation=true → client-isolation: true
- dtim → dtim-period
- max_idletime → inactivity-timeout
- max_num_clients → max-clients-threshold

**STEP 5** — Call `central_manage_wlan_profile(ssid="{ssid}", \
action_type="create", payload=<mapped>)` to create the profile.

**STEP 6 — Assign the profile to a scope (REQUIRED — do not skip):**
a. Call `central_get_scope_tree(view="committed")` to find the scope \
that matches the Mist template assignment from Step 3.
b. Match Mist site groups → Central site collections by name. Match \
Mist sites → Central sites by name. Note the `scope_id` for each match.
c. For each matching scope, call `central_manage_config_assignment(\
action_type="assign", scope_id=<scope_id>, \
device_function="CAMPUS_AP", profile_type="wlan-ssids", \
profile_instance="{ssid}")` to assign the WLAN profile.
d. Report: "In Mist, this WLAN is in template '<name>' assigned to \
site groups: <list>. In Central, assigned to scopes: <list>."
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
**Opmode:**
- opmode="WPA2_PERSONAL" → auth.type="psk", pairwise=["wpa2-ccmp"]
- opmode="WPA3_SAE" → auth.type="psk", pairwise=["wpa3"]
- opmode="WPA2_ENTERPRISE" → auth.type="eap", pairwise=["wpa2-ccmp"]
- opmode="WPA3_ENTERPRISE_CCM_128" → auth.type="eap", \
pairwise=["wpa3","wpa2-ccmp"]
- opmode="WPA2_MPSK_AES" → auth.type="psk", dynamic_psk.enabled=true
**RF bands:**
- rf-band="24GHZ_5GHZ" → bands=["24","5"]
- rf-band="BAND_ALL" → bands=["24","5","6"]
- rf-band="5GHZ" → bands=["5"]
- rf-band="5GHZ_6GHZ" → bands=["5","6"]
**Data rates (use exact template names — do NOT set custom rates):**
- g/a-legacy basic-rates contains RATE_24MB or higher only → \
rateset: {{"24":{{"template":"high-density"}},"5":{{"template":"high-density"}}}}
- g/a-legacy basic-rates contains RATE_12MB → \
rateset: {{"24":{{"template":"no-legacy"}},"5":{{"template":"no-legacy"}}}}
- g-legacy basic-rates contains RATE_1MB or RATE_2MB → \
rateset: {{"24":{{"template":"compatible"}},"5":{{"template":"compatible"}}}}
**Other fields:**
- personal-security.wpa-passphrase → auth.psk
- vlan-id-range → vlan_id (first entry), vlan_enabled=true
- dot11r=true → roam_mode="11r"
- extremely-high-throughput.enable=false → disable_11be=true
- broadcast-filter-ipv4="BCAST_FILTER_ARP" → arp_filter=true
- client-isolation → isolation
- dtim-period → dtim
- inactivity-timeout → max_idletime
- max-clients-threshold → max_num_clients
**RADIUS:** Use template variables ({{auth_srv1}}) for server IPs, \
never hardcode. Define resolved addresses in site vars.

**STEP 5** — Create a Mist WLAN template using \
`mist_change_org_configuration_objects(action_type="create", \
object_type="wlantemplates", payload=...)`, then create the WLAN \
inside it with `object_type="wlans"` and the new template_id.

**STEP 6 — Assign the template to site groups (REQUIRED — do not skip):**
a. Call `central_get_config_assignments(device_function="CAMPUS_AP")` \
to find where the Central WLAN is assigned. Look for entries with \
profile_instance="{ssid}" to find the scope.
b. Match Central scopes → Mist site groups by name.
c. For each matching site group, update the site group to include the \
new template using `mist_change_org_configuration_objects`.
d. Report: "In Central, this WLAN is assigned to scope: <scope>. In \
Mist, assigned template to site groups: <list>."
"""

# Both platforms have it
_BOTH_PLATFORMS_WORKFLOW = """
This SSID "{ssid}" exists on BOTH platforms. The full configs from \
each platform are included in this response under `mist_wlan` and \
`central_profile`.

You MUST ask the user which source to use before making any changes:
1. "Use Mist as source" → update Central to match Mist
2. "Use Central as source" → update Mist to match Central
3. "Leave both as-is"

Show a comparison table of key fields (auth type, PSK, VLAN, bands, \
etc.) so the user can see the differences before deciding.

Do NOT proceed with any create or update until the user chooses.
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
