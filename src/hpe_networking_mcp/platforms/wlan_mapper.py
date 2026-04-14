"""Cross-platform WLAN field mapping between Central and Mist.

Provides translation functions to convert WLAN configuration between
Aruba Central SSID profiles and Juniper Mist WLAN objects. Used by
migration/sync prompts to automate cross-platform WLAN porting.

Only maps bridged (non-tunneled) SSIDs. Tunneled SSIDs are excluded
from migration as they require platform-specific gateway configuration.
"""

from __future__ import annotations

from loguru import logger

# ---------------------------------------------------------------------------
# Central opmode → Mist auth mapping
# ---------------------------------------------------------------------------

_CENTRAL_OPMODE_TO_MIST = {
    "OPEN": {"type": "open"},
    "WPA3_PERSONAL": {"type": "psk", "psk": None},
    "WPA2_PERSONAL": {"type": "psk", "psk": None},
    "WPA_PERSONAL": {"type": "psk", "psk": None},
    "WPA3_ENTERPRISE": {"type": "eap"},
    "WPA2_ENTERPRISE": {"type": "eap"},
    "WPA_ENTERPRISE": {"type": "eap"},
}

_MIST_AUTH_TO_CENTRAL_OPMODE = {
    "open": "OPEN",
    "psk": "WPA2_PERSONAL",
    "eap": "WPA2_ENTERPRISE",
}

# ---------------------------------------------------------------------------
# RF band mapping
# ---------------------------------------------------------------------------

_CENTRAL_RFBAND_TO_MIST = {
    "24GHZ_5GHZ": "all",
    "24GHZ": "2.4ghz",
    "5GHZ": "5ghz",
    "6GHZ": "6ghz",
    "24GHZ_5GHZ_6GHZ": "all",
    "5GHZ_6GHZ": "5ghz",
}

_MIST_INTERFACE_TO_CENTRAL = {
    "all": "24GHZ_5GHZ",
    "5ghz": "5GHZ",
    "2.4ghz": "24GHZ",
    "6ghz": "6GHZ",
}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def is_tunneled_central(profile: dict) -> bool:
    """Check if a Central WLAN profile uses tunneled forwarding."""
    forward_mode = profile.get("forward-mode", "FORWARD_MODE_BRIDGE")
    return forward_mode != "FORWARD_MODE_BRIDGE"


def is_tunneled_mist(wlan: dict) -> bool:
    """Check if a Mist WLAN uses tunneled forwarding."""
    interface = wlan.get("interface", "all")
    return interface not in ("all", "ethernet")


def central_to_mist(profile: dict) -> dict:
    """Convert a Central WLAN SSID profile to a Mist WLAN payload.

    Args:
        profile: Central WLAN profile dict from network-config API.

    Returns:
        Mist WLAN payload dict ready for mist_change_org_configuration_objects.
    """
    essid = profile.get("essid", {})
    ssid_name = essid.get("name", profile.get("ssid", "unknown"))

    mist_wlan: dict = {
        "ssid": ssid_name,
        "enabled": profile.get("enable", True),
        "hide_ssid": profile.get("hide-ssid", False),
    }

    # Auth / security
    opmode = profile.get("opmode", "OPEN")
    auth = _CENTRAL_OPMODE_TO_MIST.get(opmode, {"type": "open"}).copy()

    personal = profile.get("personal-security", {})
    if auth.get("type") == "psk" and personal.get("wpa-passphrase"):
        auth["psk"] = personal["wpa-passphrase"]
    mist_wlan["auth"] = auth

    # RADIUS servers
    if profile.get("dot1x") or opmode in ("WPA2_ENTERPRISE", "WPA3_ENTERPRISE", "WPA_ENTERPRISE"):
        servers = []
        if profile.get("primary-auth-server"):
            servers.append({"host": profile["primary-auth-server"], "port": 1812})
        if profile.get("backup-auth-server"):
            servers.append({"host": profile["backup-auth-server"], "port": 1812})
        if servers:
            mist_wlan["auth_servers"] = servers

        if profile.get("radius-accounting"):
            acct_servers = []
            if profile.get("primary-acct-server"):
                acct_servers.append({"host": profile["primary-acct-server"], "port": 1813})
            if profile.get("backup-acct-server"):
                acct_servers.append({"host": profile["backup-acct-server"], "port": 1813})
            if acct_servers:
                mist_wlan["acct_servers"] = acct_servers

    # VLAN
    if profile.get("vlan-name"):
        mist_wlan["vlan_enabled"] = True
        mist_wlan["vlan_id"] = profile["vlan-name"]

    # RF band
    rf_band = profile.get("rf-band", "24GHZ_5GHZ")
    mist_wlan["interface"] = _CENTRAL_RFBAND_TO_MIST.get(rf_band, "all")

    # Performance settings
    mist_wlan["dtim"] = profile.get("dtim-period", 2)
    mist_wlan["max_num_clients"] = profile.get("max-clients-threshold", 0)
    mist_wlan["max_idletime"] = profile.get("inactivity-timeout", 1800)

    # 802.11r fast roaming
    if profile.get("dot11r"):
        mist_wlan["roam_mode"] = "OKC"

    # Client isolation
    mist_wlan["isolation"] = profile.get("client-isolation", False)

    # WMM
    wmm = profile.get("wmm-cfg", {})
    mist_wlan["disable_wmm"] = not wmm.get("enable", True)
    mist_wlan["disable_uapsd"] = not wmm.get("uapsd", True)

    # ARP filter
    bcast_filter = profile.get("broadcast-filter-ipv4", "FILTER_NONE")
    mist_wlan["arp_filter"] = bcast_filter != "FILTER_NONE"

    # Broadcast limiting
    mist_wlan["limit_bcast"] = profile.get("deny-inter-user-bridging", False)

    logger.debug("Mapped Central '{}' → Mist WLAN payload", ssid_name)
    return mist_wlan


def mist_to_central(wlan: dict) -> dict:
    """Convert a Mist WLAN object to a Central WLAN SSID profile payload.

    Args:
        wlan: Mist WLAN dict from mist_get_configuration_objects.

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

    # Auth / security
    auth = wlan.get("auth", {})
    auth_type = auth.get("type", "open")
    profile["opmode"] = _MIST_AUTH_TO_CENTRAL_OPMODE.get(auth_type, "OPEN")

    if auth_type == "psk" and auth.get("psk"):
        profile["personal-security"] = {
            "wpa-passphrase": auth["psk"],
            "passphrase-format": "STRING",
        }

    if auth_type == "eap":
        profile["dot1x"] = True

    # RADIUS servers
    auth_servers = wlan.get("auth_servers", [])
    if auth_servers:
        profile["primary-auth-server"] = auth_servers[0].get("host", "")
        if len(auth_servers) > 1:
            profile["backup-auth-server"] = auth_servers[1].get("host", "")

    acct_servers = wlan.get("acct_servers", [])
    if acct_servers:
        profile["radius-accounting"] = True
        profile["primary-acct-server"] = acct_servers[0].get("host", "")
        if len(acct_servers) > 1:
            profile["backup-acct-server"] = acct_servers[1].get("host", "")

    # VLAN
    if wlan.get("vlan_enabled") and wlan.get("vlan_id"):
        profile["vlan-selector"] = "NAMED_VLAN"
        profile["vlan-name"] = str(wlan["vlan_id"])

    # RF band
    interface = wlan.get("interface", "all")
    profile["rf-band"] = _MIST_INTERFACE_TO_CENTRAL.get(interface, "24GHZ_5GHZ")

    # Performance
    profile["dtim-period"] = wlan.get("dtim", 2)
    profile["max-clients-threshold"] = wlan.get("max_num_clients", 64)
    profile["inactivity-timeout"] = wlan.get("max_idletime", 1800)

    # 802.11r
    if wlan.get("roam_mode") and wlan["roam_mode"] != "NONE":
        profile["dot11r"] = True

    # Client isolation
    profile["client-isolation"] = wlan.get("isolation", False)

    # WMM
    profile["wmm-cfg"] = {
        "enable": not wlan.get("disable_wmm", False),
        "uapsd": not wlan.get("disable_uapsd", False),
    }

    # ARP filter → broadcast filter
    if wlan.get("arp_filter"):
        profile["broadcast-filter-ipv4"] = "BCAST_FILTER_ARP"

    # Broadcast limiting
    profile["deny-inter-user-bridging"] = wlan.get("limit_bcast", False)

    logger.debug("Mapped Mist '{}' → Central WLAN profile payload", ssid_name)
    return profile
