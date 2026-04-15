"""Cross-platform WLAN field mapping between Central and Mist.

Provides translation functions to convert WLAN configuration between
Aruba Central SSID profiles and Juniper Mist WLAN objects. Used by
migration/sync prompts to automate cross-platform WLAN porting.

Only maps bridged (non-tunneled) SSIDs. Tunneled SSIDs are excluded
from migration as they require platform-specific gateway configuration.

Resolution of aliases (Central), template variables (Mist), server
groups, and named VLANs must be done by the caller before passing
data to these functions. The mapper works with resolved values only.
"""

from __future__ import annotations

from loguru import logger

from hpe_networking_mcp.platforms._wlan_helpers import (
    CENTRAL_RFBAND_TO_MIST_BANDS,
    MIST_BANDS_TO_CENTRAL_RFBAND,
    extract_coa_servers,
    get_central_psk,
    has_radsec,
    map_central_data_rates,
    map_central_opmode_to_mist_auth,
    map_central_radius_to_mist,
    map_central_vlan_to_mist,
    map_mist_auth_to_central_opmode,
    map_mist_data_rates_to_central,
    map_mist_radius_to_central,
    map_mist_vlan_to_central,
    resolve_template_var,
)

# Re-export for external callers
resolve_mist_template_var = resolve_template_var


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def is_tunneled_central(profile: dict) -> bool:
    """Check if a Central WLAN profile uses tunneled forwarding."""
    forward_mode = profile.get("forward-mode", "FORWARD_MODE_BRIDGE")
    return forward_mode != "FORWARD_MODE_BRIDGE"


def is_tunneled_mist(wlan: dict) -> bool:
    """Check if a Mist WLAN uses tunneled forwarding."""
    interface = wlan.get("interface", "")
    return interface not in ("", "all", "ethernet")


def central_to_mist(
    profile: dict,
    *,
    resolved_ssid: str | None = None,
    resolved_psk: str | None = None,
    resolved_servers: list[dict] | None = None,
    resolved_acct_servers: list[dict] | None = None,
    resolved_vlan_id: int | str | None = None,
    resolved_nas_id: str | None = None,
    resolved_nas_ip: str | None = None,
) -> dict:
    """Convert a Central WLAN SSID profile to a Mist WLAN payload.

    Callers must resolve aliases, server groups, and named VLANs
    before calling this function. Pass resolved values via keyword args.

    Args:
        profile: Central WLAN profile dict from network-config API.
        resolved_ssid: SSID name after alias resolution. Falls back to
            essid.name or profile ssid field.
        resolved_psk: PSK passphrase after alias resolution.
        resolved_servers: List of resolved auth server dicts with
            host, port, secret keys. From server group resolution.
        resolved_acct_servers: List of resolved accounting server dicts.
        resolved_vlan_id: VLAN ID after named VLAN / alias resolution.
        resolved_nas_id: NAS identifier from server config.
        resolved_nas_ip: NAS IP address from server config.

    Returns:
        Mist WLAN payload dict ready for mist_change_org_configuration_objects.
    """
    essid = profile.get("essid", {})
    ssid_name = resolved_ssid or essid.get("name", profile.get("ssid", "unknown"))

    mist_wlan: dict = {
        "ssid": ssid_name,
        "enabled": profile.get("enable", True),
        "hide_ssid": profile.get("hide-ssid", False),
    }

    # --- Auth / security ---
    opmode = profile.get("opmode", "OPEN")
    auth = map_central_opmode_to_mist_auth(opmode)

    psk = resolved_psk or get_central_psk(profile)
    if auth.get("type") == "psk" and psk:
        auth["psk"] = psk

    if profile.get("wpa3-transition-mode-enable"):
        pairwise = auth.get("pairwise", [])
        if "wpa3" not in pairwise:
            pairwise.append("wpa3")
        if "wpa2-ccmp" not in pairwise:
            pairwise.append("wpa2-ccmp")
        auth["pairwise"] = pairwise

    if opmode == "WPA2_MPSK_AES" and profile.get("personal-security", {}).get("mpsk-cloud-auth"):
        mist_wlan["dynamic_psk"] = {"enabled": True, "source": "cloud"}

    if profile.get("mac-authentication"):
        auth["enable_mac_auth"] = True

    mist_wlan["auth"] = auth

    # --- RADIUS servers ---
    map_central_radius_to_mist(profile, mist_wlan, resolved_servers, resolved_acct_servers)

    if resolved_nas_id:
        mist_wlan["auth_servers_nas_id"] = resolved_nas_id
    if resolved_nas_ip:
        mist_wlan["auth_servers_nas_ip"] = resolved_nas_ip

    acct_interval = profile.get("radius-interim-accounting-interval")
    if acct_interval:
        mist_wlan["acct_interim_interval"] = acct_interval

    coa_servers = extract_coa_servers(profile, resolved_servers)
    if coa_servers:
        mist_wlan["coa_servers"] = coa_servers

    if has_radsec(resolved_servers):
        mist_wlan["radsec"] = {"enabled": True}

    # --- VLAN ---
    map_central_vlan_to_mist(profile, mist_wlan, resolved_vlan_id)

    # --- RF band ---
    rf_band = profile.get("rf-band", "24GHZ_5GHZ")
    mist_wlan["bands"] = CENTRAL_RFBAND_TO_MIST_BANDS.get(rf_band, ["24", "5"])

    # --- Data rate profile ---
    rateset_template = map_central_data_rates(profile)
    if rateset_template:
        mist_wlan["rateset"] = {
            "24": {"template": rateset_template},
            "5": {"template": rateset_template},
        }

    # --- Performance settings ---
    mist_wlan["dtim"] = profile.get("dtim-period", 2)
    mist_wlan["max_num_clients"] = profile.get("max-clients-threshold", 0)
    mist_wlan["max_idletime"] = profile.get("inactivity-timeout", 1800)

    if profile.get("dot11r"):
        mist_wlan["roam_mode"] = "11r"

    eht = profile.get("extremely-high-throughput", {})
    if isinstance(eht, dict) and eht.get("enable") is False:
        mist_wlan["disable_11be"] = True

    # --- Client isolation / broadcast ---
    mist_wlan["isolation"] = profile.get("client-isolation", False)
    mist_wlan["limit_bcast"] = profile.get("deny-inter-user-bridging", False)

    bcast_filter = profile.get("broadcast-filter-ipv4", "FILTER_NONE")
    mist_wlan["arp_filter"] = bcast_filter != "FILTER_NONE"

    # --- WMM ---
    wmm = profile.get("wmm-cfg", {})
    mist_wlan["disable_wmm"] = not wmm.get("enable", True)
    mist_wlan["disable_uapsd"] = not wmm.get("uapsd", True)

    logger.debug("Mapped Central '{}' -> Mist WLAN payload", ssid_name)
    return mist_wlan


def mist_to_central(
    wlan: dict,
    *,
    resolved_auth_hosts: list[str] | None = None,
    resolved_acct_hosts: list[str] | None = None,
) -> dict:
    """Convert a Mist WLAN object to a Central WLAN SSID profile payload.

    Callers must resolve template variables (e.g. {{auth_srv1}}) from
    site settings vars before calling. Pass resolved hosts if the WLAN
    uses template variables.

    Args:
        wlan: Mist WLAN dict from mist_get_configuration_objects.
        resolved_auth_hosts: Resolved auth server hostnames/IPs if the
            WLAN uses template variables in auth_servers[].host.
        resolved_acct_hosts: Resolved acct server hostnames/IPs.

    Returns:
        Central WLAN profile payload dict ready for central_manage_wlan_profile.
    """
    ssid_name = wlan.get("ssid", "unknown")

    profile: dict = {
        "ssid": ssid_name,
        "essid": {"name": ssid_name, "use-alias": False, "alias": ""},
        "enable": wlan.get("enabled", True),
        "hide-ssid": wlan.get("hide_ssid", False),
        "forward-mode": "FORWARD_MODE_BRIDGE",
    }

    # --- Auth / security ---
    auth = wlan.get("auth", {})
    auth_type = auth.get("type", "open")
    pairwise = auth.get("pairwise", [])

    profile["opmode"] = map_mist_auth_to_central_opmode(auth_type, pairwise, wlan)

    if auth_type == "psk" and auth.get("psk"):
        profile["personal-security"] = {
            "wpa-passphrase": auth["psk"],
            "passphrase-format": "STRING",
        }

    if "wpa3" in pairwise and "wpa2-ccmp" in pairwise:
        profile["wpa3-transition-mode-enable"] = True

    if auth.get("enable_mac_auth"):
        profile["mac-authentication"] = True

    # --- RADIUS servers ---
    map_mist_radius_to_central(wlan, profile, resolved_auth_hosts, resolved_acct_hosts)

    if wlan.get("auth_servers_nas_id"):
        profile["nas-identifier"] = wlan["auth_servers_nas_id"]
    if wlan.get("auth_servers_nas_ip"):
        profile["nas-ip-address"] = wlan["auth_servers_nas_ip"]

    if wlan.get("acct_interim_interval"):
        profile["radius-interim-accounting-interval"] = wlan["acct_interim_interval"]

    if wlan.get("coa_servers"):
        profile["dynamic-authorization-enable"] = True

    radsec = wlan.get("radsec", {})
    if isinstance(radsec, dict) and radsec.get("enabled"):
        profile["enable-radsec"] = True

    # --- VLAN ---
    map_mist_vlan_to_central(wlan, profile)

    # --- RF band ---
    bands = wlan.get("bands", ["24", "5"])
    bands_key = tuple(sorted(bands))
    profile["rf-band"] = MIST_BANDS_TO_CENTRAL_RFBAND.get(bands_key, "24GHZ_5GHZ")

    # --- Data rate profile ---
    map_mist_data_rates_to_central(wlan, profile)

    # --- Performance ---
    profile["dtim-period"] = wlan.get("dtim", 2)
    profile["max-clients-threshold"] = wlan.get("max_num_clients", 64)
    profile["inactivity-timeout"] = wlan.get("max_idletime", 1800)

    roam_mode = wlan.get("roam_mode", "NONE")
    if roam_mode == "11r":
        profile["dot11r"] = True

    if wlan.get("disable_11be") is True:
        profile["extremely-high-throughput"] = {"enable": False}

    # --- Client isolation / broadcast ---
    profile["client-isolation"] = wlan.get("isolation", False)
    profile["deny-inter-user-bridging"] = wlan.get("limit_bcast", False)

    if wlan.get("arp_filter"):
        profile["broadcast-filter-ipv4"] = "BCAST_FILTER_ARP"

    # --- WMM ---
    profile["wmm-cfg"] = {
        "enable": not wlan.get("disable_wmm", False),
        "uapsd": not wlan.get("disable_uapsd", False),
    }

    logger.debug("Mapped Mist '{}' -> Central WLAN profile payload", ssid_name)
    return profile
