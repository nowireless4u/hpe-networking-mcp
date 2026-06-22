"""Canonical → Central WLAN writer.

Produces the Central ``wlan-ssids`` create call (global) plus scope
assignment(s), from a ``CanonicalWlan``. The field construction is the
validated ``platforms/wlan_mapper.mist_to_central`` logic + ``docs/mappings/WLAN.md``,
re-housed to read the canonical model.

Auth source: an enterprise/MAC-auth WLAN references a Central server-group by
name (``{ssid}_nac``); creating/ensuring that server-group (and its aliases for
variable-based hosts) is a separate translation — this writer only references it.
"""

from __future__ import annotations

from typing import Any

from hpe_networking_mcp.translations.canonical.wlan import (
    CanonicalWlan,
    FastRoam,
    MpskSource,
    SecurityMode,
    VlanMode,
)

# canonical band set -> Central rf-band enum
_BANDS_TO_RFBAND: dict[tuple[str, ...], str] = {
    ("24", "5", "6"): "BAND_ALL",
    ("24", "5"): "24GHZ_5GHZ",
    ("24", "6"): "24GHZ_6GHZ",
    ("5", "6"): "5GHZ_6GHZ",
    ("24",): "24GHZ",
    ("5",): "5GHZ",
    ("6",): "6GHZ",
}

# per-band rateset template -> Central legacy basic-rates.
# Central's g/a-legacy-rates basic-rates is an enum of RATE_<n>MB tokens
# (vendor/central/config/wireless.json), NOT bare integers — live-confirmed:
# bare "1" → HTTP 400 "Invalid enumeration value '1'".
_RATE_TEMPLATE_TO_CENTRAL: dict[str, dict[str, list[str]]] = {
    "compatible": {"g": ["RATE_1MB", "RATE_2MB"], "a": ["RATE_6MB"]},
    "no-legacy": {"g": ["RATE_12MB"], "a": ["RATE_12MB"]},
    "high-density": {"g": ["RATE_24MB"], "a": ["RATE_24MB"]},
}

_WLAN_SSIDS = "network-config/v1alpha1/wlan-ssids"
_CONFIG_ASSIGNMENTS = "network-config/v1alpha1/config-assignments"


def server_group_name(ssid: str) -> str:
    """The Central server-group name a WLAN's enterprise/MAC auth references."""
    return f"{ssid}_nac"


def _opmode(canon: CanonicalWlan) -> str:
    sec = canon.security
    if sec.mode == SecurityMode.OPEN:
        return "OPEN"
    if sec.mode == SecurityMode.PSK:
        return "WPA2_PERSONAL"
    if sec.mode == SecurityMode.SAE:
        return "WPA3_PERSONAL"
    if sec.mode == SecurityMode.MPSK:
        return "WPA2_MPSK_AES"
    if sec.mode == SecurityMode.ENTERPRISE:
        return "WPA3_ENTERPRISE_CCM_128" if sec.wpa2_wpa3_transition else "WPA2_ENTERPRISE"
    return "OPEN"


def _wlan_body(canon: CanonicalWlan) -> dict[str, Any]:
    sec = canon.security
    body: dict[str, Any] = {
        "ssid": canon.profile_name or canon.ssid,
        # use-alias=false → send the literal name only. An empty "alias": "" makes
        # Central resolve an alias named '' (live-confirmed 400), so omit it.
        "essid": {"name": canon.ssid, "use-alias": False},
        "enable": canon.enabled,
        "hide-ssid": canon.hidden,
        "forward-mode": "FORWARD_MODE_BRIDGE",
        "opmode": _opmode(canon),
    }

    # --- personal / MPSK ---
    if sec.mode in (SecurityMode.PSK, SecurityMode.SAE) and sec.psk:
        body["personal-security"] = {"wpa-passphrase": sec.psk, "passphrase-format": "STRING"}
    if sec.mode == SecurityMode.MPSK and sec.mpsk_source == MpskSource.CLOUD:
        # Central manages the keys for cloud MPSK — enable cloud-auth, copy NO values.
        body["personal-security"] = {"mpsk-cloud-auth": True}
    if sec.wpa2_wpa3_transition:
        body["wpa3-transition-mode-enable"] = True

    # --- enterprise / MAC auth: reference the server-group ({ssid}_nac) ---
    # The group itself (+ its auth-servers) is built by the separate RADIUS
    # writer; here the WLAN only references it by name.
    if sec.mode == SecurityMode.ENTERPRISE or sec.mac_auth:
        body["auth-server-group"] = server_group_name(canon.ssid)
    if sec.mac_auth:
        body["mac-authentication"] = True
    if sec.radius:
        # accounting points at the same group when acct servers are present.
        if sec.radius.acct_servers:
            body["acct-server-group"] = server_group_name(canon.ssid)
        if sec.radius.interim_interval:
            body["radius-interim-accounting-interval"] = sec.radius.interim_interval

    # --- VLAN ---
    if canon.vlan.mode in (VlanMode.NAMED, VlanMode.DYNAMIC) and (canon.vlan.name or canon.vlan.id is not None):
        body["vlan-selector"] = "NAMED_VLAN"
        body["vlan-name"] = canon.vlan.name or str(canon.vlan.id)
    elif canon.vlan.mode == VlanMode.ID and canon.vlan.id is not None:
        body["vlan-selector"] = "NAMED_VLAN"
        body["vlan-name"] = str(canon.vlan.id)

    # --- RF band ---
    if canon.bands:
        rfband = _BANDS_TO_RFBAND.get(tuple(sorted(canon.bands)))
        if rfband:
            body["rf-band"] = rfband

    # --- data rates (per band) ---
    for tmpl in (canon.rates.band_5, canon.rates.band_24):
        if tmpl in _RATE_TEMPLATE_TO_CENTRAL:
            rates = _RATE_TEMPLATE_TO_CENTRAL[tmpl]
            body["g-legacy-rates"] = {"basic-rates": rates["g"]}
            body["a-legacy-rates"] = {"basic-rates": rates["a"]}
            break

    # --- performance ---
    p = canon.performance
    if p.dtim is not None:
        body["dtim-period"] = p.dtim
    if p.max_clients is not None:
        body["max-clients-threshold"] = p.max_clients
    if p.idle_timeout is not None:
        body["inactivity-timeout"] = p.idle_timeout
    if p.fast_roam == FastRoam.DOT11R:
        body["dot11r"] = True
    if p.wifi7_11be is False:
        body["extremely-high-throughput"] = {"enable": False}

    # --- isolation / broadcast ---
    body["client-isolation"] = canon.isolation.client_isolation
    body["deny-inter-user-bridging"] = canon.isolation.limit_bcast
    if canon.isolation.arp_filter:
        body["broadcast-filter-ipv4"] = "BCAST_FILTER_ARP"

    # --- WMM ---
    body["wmm-cfg"] = {"enable": canon.wmm.enabled, "uapsd": canon.wmm.uapsd}

    return body


def _assign_call(profile: str, scope_id: str | None, kind: str, name: str) -> dict[str, Any]:
    """One config-assignment call descriptor.

    The body shape is identical for every scope-type — Central infers the
    scope-type (GLOBAL / SITE_COLLECTION / SITE / DEVICE_COLLECTION) from the
    scope-id, so only the id varies (live-confirmed against the SITE path).
    ``unresolved`` carries the unresolved scope name when the caller couldn't
    map it, so the consuming skill can create the scope first.
    """
    return {
        "method": "POST",
        "path": _CONFIG_ASSIGNMENTS,
        "query": {},
        "body": {
            "config-assignment": [
                {
                    "scope-id": scope_id,
                    "device-function": "CAMPUS_AP",
                    "profile-type": "wlan-ssids",
                    "profile-instance": profile,
                }
            ]
        },
        "purpose": f"Assign '{profile}' to {kind} '{name}'",
        "depends_on": [0],
        "unresolved": None if scope_id else {"kind": kind, "name": name},
    }


def central_write_wlan(
    canon: CanonicalWlan,
    *,
    global_scope_id: str | None = None,
    site_name_to_scope_id: dict[str, str] | None = None,
    site_collection_name_to_scope_id: dict[str, str] | None = None,
    device_group_name_to_scope_id: dict[str, str] | None = None,
) -> list[dict[str, Any]]:
    """Emit the ordered Central calls to mirror a WLAN: create + assign.

    A library wlan-ssids broadcasts nowhere until it is config-assigned to a
    scope. Each canonical assignment facet maps to a Central scope-type whose
    config-assignment shares one body shape (only the scope-id varies):

    ===================  ==================  ============================
    canonical facet      Central scope-type  resolver arg
    ===================  ==================  ============================
    ``org_wide``         GLOBAL              ``global_scope_id``
    ``sites``            SITE                ``site_name_to_scope_id``
    ``site_collections`` SITE_COLLECTION     ``site_collection_name_to_scope_id``
    ``device_groups``    DEVICE_COLLECTION   ``device_group_name_to_scope_id``
    ===================  ==================  ============================

    Args:
        canon: the platform-neutral WLAN.
        global_scope_id: the tenant's GLOBAL scope-id (resolved from the scope
            tree by the caller) — required to make an ``org_wide`` WLAN effective.
        site_name_to_scope_id: resolves ``assignment.sites`` names → scope ids.
        site_collection_name_to_scope_id: resolves ``assignment.site_collections``.
        device_group_name_to_scope_id: resolves ``assignment.device_groups``.

    Any name the caller could not resolve is surfaced in that call's
    ``unresolved`` field (the consuming skill creates the scope first).

    Returns:
        A list of call descriptors: ``{method, path, query, body, purpose, depends_on}``.
    """
    profile = canon.profile_name or canon.ssid
    sites = site_name_to_scope_id or {}
    collections = site_collection_name_to_scope_id or {}
    groups = device_group_name_to_scope_id or {}
    asg = canon.assignment
    calls: list[dict[str, Any]] = []

    # 1) create the wlan-ssids profile in the Central WLAN library.
    # The no-query POST adds it to the library (live-confirmed, and matches the
    # validated central_manage_wlan_profile tool). The library profile is then
    # made effective by config-assignment to a scope in step 2.
    calls.append(
        {
            "method": "POST",
            "path": f"{_WLAN_SSIDS}/{profile}",
            "query": {},
            "body": _wlan_body(canon),
            "purpose": f"Create Central wlan-ssids '{profile}' (library)",
            "depends_on": [],
        }
    )

    # 2) assignment(s) — one config-assignment per resolved scope facet.
    if asg.org_wide:
        calls.append(_assign_call(profile, global_scope_id, "global", "GLOBAL"))
    for name in asg.sites:
        calls.append(_assign_call(profile, sites.get(name), "site", name))
    for name in asg.site_collections:
        calls.append(_assign_call(profile, collections.get(name), "site-collection", name))
    for name in asg.device_groups:
        calls.append(_assign_call(profile, groups.get(name), "device-group", name))

    return calls
