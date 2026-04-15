"""Private helper functions for WLAN field mapping.

Internal module used by wlan_mapper.py. Not intended for direct import.
Handles RADIUS, VLAN, data rate, and auth sub-mappings.
"""

from __future__ import annotations

import re

from loguru import logger

# Template variable pattern — matches {{variable_name}}
TEMPLATE_VAR_PATTERN = re.compile(r"^\{\{.+\}\}$")


# ---------------------------------------------------------------------------
# Auth helpers
# ---------------------------------------------------------------------------

# Central opmode → Mist auth type + pairwise
CENTRAL_OPMODE_TO_MIST: dict[str, dict] = {
    "OPEN": {"type": "open"},
    "WPA2_PERSONAL": {"type": "psk", "pairwise": ["wpa2-ccmp"]},
    "WPA3_PERSONAL": {"type": "psk", "pairwise": ["wpa3"]},
    "WPA2_ENTERPRISE": {"type": "eap", "pairwise": ["wpa2-ccmp"]},
    "WPA3_ENTERPRISE_CCM_128": {"type": "eap", "pairwise": ["wpa3", "wpa2-ccmp"]},
    "WPA2_MPSK_AES": {"type": "psk"},
}

# Mist auth type → Central opmode (simple cases)
MIST_AUTH_TO_CENTRAL_OPMODE: dict[str, str] = {
    "open": "OPEN",
    "psk": "WPA2_PERSONAL",
    "eap": "WPA2_ENTERPRISE",
}


def map_central_opmode_to_mist_auth(opmode: str) -> dict:
    """Map Central opmode to Mist auth dict with pairwise."""
    base = CENTRAL_OPMODE_TO_MIST.get(opmode, {"type": "open"})
    return {k: (v.copy() if isinstance(v, list) else v) for k, v in base.items()}


def get_central_psk(profile: dict) -> str | None:
    """Extract PSK from Central profile (direct passphrase only)."""
    personal = profile.get("personal-security", {})
    return personal.get("wpa-passphrase")


def map_mist_auth_to_central_opmode(
    auth_type: str,
    pairwise: list[str],
    wlan: dict,
) -> str:
    """Map Mist auth type + pairwise to Central opmode."""
    dynamic_psk = wlan.get("dynamic_psk", {})
    if auth_type == "psk" and isinstance(dynamic_psk, dict) and dynamic_psk.get("enabled"):
        return "WPA2_MPSK_AES"
    if auth_type == "psk" and pairwise == ["wpa3"]:
        return "WPA3_PERSONAL"
    if auth_type == "eap" and "wpa3" in pairwise and "wpa2-ccmp" in pairwise:
        return "WPA3_ENTERPRISE_CCM_128"
    return MIST_AUTH_TO_CENTRAL_OPMODE.get(auth_type, "OPEN")


# ---------------------------------------------------------------------------
# RF band helpers
# ---------------------------------------------------------------------------

CENTRAL_RFBAND_TO_MIST_BANDS: dict[str, list[str]] = {
    "BAND_ALL": ["24", "5", "6"],
    "24GHZ_5GHZ": ["24", "5"],
    "24GHZ_6GHZ": ["24", "6"],
    "5GHZ_6GHZ": ["5", "6"],
    "24GHZ": ["24"],
    "5GHZ": ["5"],
    "6GHZ": ["6"],
    "BAND_NONE": [],
}

MIST_BANDS_TO_CENTRAL_RFBAND: dict[tuple[str, ...], str] = {
    ("24", "5", "6"): "BAND_ALL",
    ("24", "5"): "24GHZ_5GHZ",
    ("24", "6"): "24GHZ_6GHZ",
    ("5", "6"): "5GHZ_6GHZ",
    ("24",): "24GHZ",
    ("5",): "5GHZ",
    ("6",): "6GHZ",
}


# ---------------------------------------------------------------------------
# RADIUS helpers
# ---------------------------------------------------------------------------


def map_central_radius_to_mist(
    profile: dict,
    mist_wlan: dict,
    resolved_servers: list[dict] | None,
    resolved_acct_servers: list[dict] | None,
) -> None:
    """Map Central RADIUS config to Mist auth_servers / acct_servers."""
    opmode = profile.get("opmode", "OPEN")
    is_enterprise = opmode in (
        "WPA2_ENTERPRISE",
        "WPA3_ENTERPRISE_CCM_128",
        "WPA_ENTERPRISE",
    )
    has_mac_auth = profile.get("mac-authentication", False)

    if not (is_enterprise or has_mac_auth):
        return

    auth_servers = resolved_servers or _inline_servers(
        profile, "primary-auth-server", "backup-auth-server", 1812
    )
    if auth_servers:
        mist_wlan["auth_servers"] = auth_servers
        mist_wlan["auth_server_selection"] = "ordered"

    if profile.get("radius-accounting"):
        acct_servers = resolved_acct_servers or _inline_servers(
            profile, "primary-acct-server", "backup-acct-server", 1813
        )
        if acct_servers:
            mist_wlan["acct_servers"] = acct_servers


def _inline_servers(
    profile: dict,
    primary_key: str,
    backup_key: str,
    default_port: int,
) -> list[dict]:
    """Build server list from inline primary/backup fields."""
    servers = []
    if profile.get(primary_key):
        servers.append({"host": profile[primary_key], "port": default_port})
    if profile.get(backup_key):
        servers.append({"host": profile[backup_key], "port": default_port})
    return servers


def extract_coa_servers(
    profile: dict,
    resolved_servers: list[dict] | None,
) -> list[dict]:
    """Extract CoA server entries from resolved servers with DAC enabled."""
    coa_servers = []
    for server in (resolved_servers or []):
        if server.get("dynamic-authorization-enable"):
            coa_servers.append({
                "ip": server.get("host", ""),
                "port": server.get("coa-port", 3799),
                "secret": server.get("secret", ""),
            })
    return coa_servers


def has_radsec(resolved_servers: list[dict] | None) -> bool:
    """Check if any resolved server has RadSec enabled."""
    return any(server.get("enable-radsec") for server in (resolved_servers or []))


def map_mist_radius_to_central(
    wlan: dict,
    profile: dict,
    resolved_auth_hosts: list[str] | None,
    resolved_acct_hosts: list[str] | None,
) -> None:
    """Map Mist RADIUS servers to Central primary/backup fields."""
    auth_servers = wlan.get("auth_servers", [])
    if auth_servers:
        hosts = resolved_auth_hosts or [s.get("host", "") for s in auth_servers]
        if hosts:
            profile["primary-auth-server"] = hosts[0]
        if len(hosts) > 1:
            profile["backup-auth-server"] = hosts[1]

    acct_servers = wlan.get("acct_servers", [])
    if acct_servers:
        profile["radius-accounting"] = True
        hosts = resolved_acct_hosts or [s.get("host", "") for s in acct_servers]
        if hosts:
            profile["primary-acct-server"] = hosts[0]
        if len(hosts) > 1:
            profile["backup-acct-server"] = hosts[1]


# ---------------------------------------------------------------------------
# VLAN helpers
# ---------------------------------------------------------------------------


def map_central_vlan_to_mist(
    profile: dict,
    mist_wlan: dict,
    resolved_vlan_id: int | str | None,
) -> None:
    """Map Central VLAN config to Mist dynamic_vlan structure."""
    vlan_name = profile.get("vlan-name")
    if not vlan_name and not resolved_vlan_id:
        return

    mist_wlan["vlan_enabled"] = True

    if resolved_vlan_id is not None:
        mist_wlan["dynamic_vlan"] = {
            "enabled": True,
            "type": "airespace-interface-name",
            "default_vlan_ids": [resolved_vlan_id],
            "vlans": {str(resolved_vlan_id): vlan_name or ""},
        }
    elif vlan_name:
        mist_wlan["vlan_id"] = vlan_name


def map_mist_vlan_to_central(wlan: dict, profile: dict) -> None:
    """Map Mist VLAN config to Central named VLAN fields."""
    dynamic_vlan = wlan.get("dynamic_vlan", {})
    if isinstance(dynamic_vlan, dict) and dynamic_vlan.get("enabled"):
        vlans_map = dynamic_vlan.get("vlans", {})
        if vlans_map:
            first_id = next(iter(vlans_map))
            first_name = vlans_map[first_id]
            profile["vlan-selector"] = "NAMED_VLAN"
            profile["vlan-name"] = first_name if first_name else first_id
        elif dynamic_vlan.get("default_vlan_ids"):
            profile["vlan-selector"] = "NAMED_VLAN"
            profile["vlan-name"] = str(dynamic_vlan["default_vlan_ids"][0])
    elif wlan.get("vlan_enabled") and wlan.get("vlan_id"):
        profile["vlan-selector"] = "NAMED_VLAN"
        profile["vlan-name"] = str(wlan["vlan_id"])


# ---------------------------------------------------------------------------
# Data rate helpers
# ---------------------------------------------------------------------------


def mbr_to_rateset_template(mbr_mbps: int) -> str:
    """Map a Central minimum basic rate (Mbps) to a Mist rateset template.

    Args:
        mbr_mbps: Minimum basic rate in Mbps from Central data rate config.

    Returns:
        Mist rateset template name.
    """
    if mbr_mbps <= 2:
        return "compatible"
    if mbr_mbps <= 12:
        return "no-legacy"
    return "high-density"


def map_central_data_rates(profile: dict) -> str | None:
    """Map Central data rate config to a Mist rateset template name.

    Returns:
        Mist rateset template name, or None if no rate info available.
    """
    g_rates = profile.get("g-legacy-rates", {})
    a_rates = profile.get("a-legacy-rates", {})

    basic_rates = g_rates.get("basic-rates") or a_rates.get("basic-rates")
    if not basic_rates:
        return None

    if isinstance(basic_rates, list) and basic_rates:
        try:
            mbr = min(int(r) for r in basic_rates)
            return mbr_to_rateset_template(mbr)
        except (ValueError, TypeError):
            return None
    return None


def map_mist_data_rates_to_central(wlan: dict, profile: dict) -> None:
    """Map Mist rateset template to Central data rate fields.

    Only maps named templates (compatible, no-legacy, high-density).
    Custom Mist ratesets are not mapped.
    """
    rateset = wlan.get("rateset", {})
    if not isinstance(rateset, dict):
        return

    for band_key in ("24", "5"):
        band = rateset.get(band_key, {})
        if isinstance(band, dict) and band.get("template"):
            template = band["template"]
            if template == "compatible":
                profile.setdefault("g-legacy-rates", {})["basic-rates"] = ["1", "2"]
                profile.setdefault("a-legacy-rates", {})["basic-rates"] = ["6"]
            elif template == "no-legacy":
                profile.setdefault("g-legacy-rates", {})["basic-rates"] = ["12"]
                profile.setdefault("a-legacy-rates", {})["basic-rates"] = ["12"]
            elif template == "high-density":
                profile.setdefault("g-legacy-rates", {})["basic-rates"] = ["24"]
                profile.setdefault("a-legacy-rates", {})["basic-rates"] = ["24"]
            return


def resolve_template_var(host: str, site_vars: dict[str, str]) -> str:
    """Resolve a Mist template variable to its actual value.

    Args:
        host: The host field value, e.g. "{{auth_srv1}}" or "10.1.1.1".
        site_vars: The vars dict from site settings.

    Returns:
        Resolved host value. Returns original if not a template variable
        or if the variable is not found in site_vars.
    """
    if not TEMPLATE_VAR_PATTERN.match(host):
        return host
    var_name = host.strip("{}")
    resolved = site_vars.get(var_name, host)
    if resolved == host:
        logger.warning("Template variable '{}' not found in site vars", host)
    return resolved
