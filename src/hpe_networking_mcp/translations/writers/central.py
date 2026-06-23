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
    AuthSourceKind,
    CanonicalWlan,
    Cipher,
    FastRoam,
    ForwardMode,
    KeyMgmt,
    MpskSource,
    VlanMode,
    WpaVersion,
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
_OVERLAY_WLAN = "network-config/v1alpha1/overlay-wlan"
_ALIASES = "network-config/v1alpha1/aliases"

# Forward modes that tunnel to a gateway cluster (need an overlay-wlan binding).
_OVERLAY_FORWARD = {ForwardMode.TUNNELED, ForwardMode.HYBRID}

# canonical ForwardMode -> Central forward-mode enum.
_FORWARD_MODE = {
    ForwardMode.BRIDGED: "FORWARD_MODE_BRIDGE",
    ForwardMode.TUNNELED: "FORWARD_MODE_L2",
    ForwardMode.HYBRID: "FORWARD_MODE_MIXED",
}

# WPA generation -> Central personal/enterprise opmode (non-WPA3 cases).
_PERSONAL_BY_WPA = {
    WpaVersion.WPA: "WPA_PERSONAL",
    WpaVersion.WPA2: "WPA2_PERSONAL",
    WpaVersion.WPA_WPA2: "BOTH_WPA_WPA2_PSK",
}
_ENTERPRISE_BY_WPA = {
    WpaVersion.WPA: "WPA_ENTERPRISE",
    WpaVersion.WPA2: "WPA2_ENTERPRISE",
    WpaVersion.WPA_WPA2: "BOTH_WPA_WPA2_DOT1X",
}
# WPA3-Enterprise opmode by cipher.
_WPA3_ENTERPRISE_BY_CIPHER = {
    Cipher.GCM_256: "WPA3_ENTERPRISE_GCM_256",
    Cipher.CNSA: "WPA3_ENTERPRISE_CNSA",
}


def server_group_name(ssid: str) -> str:
    """The Central server-group name a WLAN's enterprise/MAC auth references."""
    return f"{ssid}_nac"


def _opmode(canon: CanonicalWlan) -> str:
    """Map the neutral (key_mgmt, wpa_version, cipher) triplet → Central opmode enum."""
    sec = canon.security
    km, wpa, cipher = sec.key_mgmt, sec.wpa_version, sec.cipher

    if km == KeyMgmt.OPEN:
        return "OPEN"
    if km == KeyMgmt.OWE:
        return "ENHANCED_OPEN"
    if km == KeyMgmt.WEP_STATIC:
        return "STATIC_WEP"
    if km == KeyMgmt.WEP_DYNAMIC:
        return "DYNAMIC_WEP"
    if km == KeyMgmt.SAE:
        return "WPA3_SAE"
    if km == KeyMgmt.MPSK:
        return "WPA2_MPSK_LOCAL" if sec.mpsk_source == MpskSource.LOCAL else "WPA2_MPSK_AES"
    if km == KeyMgmt.PSK:
        return _PERSONAL_BY_WPA.get(wpa, "WPA2_PERSONAL")
    if km == KeyMgmt.ENTERPRISE:
        if wpa == WpaVersion.WPA3:
            return _WPA3_ENTERPRISE_BY_CIPHER.get(cipher, "WPA3_ENTERPRISE_CCM_128")
        return _ENTERPRISE_BY_WPA.get(wpa, "WPA2_ENTERPRISE")
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
        "forward-mode": _FORWARD_MODE.get(canon.forward, "FORWARD_MODE_BRIDGE"),
        "opmode": _opmode(canon),
    }

    # --- personal / MPSK ---
    if sec.key_mgmt in (KeyMgmt.PSK, KeyMgmt.SAE) and sec.psk:
        body["personal-security"] = {"wpa-passphrase": sec.psk, "passphrase-format": "STRING"}
    if sec.key_mgmt == KeyMgmt.MPSK and sec.mpsk_source == MpskSource.CLOUD:
        # Central manages the keys for cloud MPSK — enable cloud-auth, copy NO values.
        body["personal-security"] = {"mpsk-cloud-auth": True}
    if sec.wpa2_wpa3_transition:
        body["wpa3-transition-mode-enable"] = True

    # --- enterprise / MAC auth: reference the server-group ({ssid}_nac) ---
    # ONLY for an external-RADIUS auth source. A NAC-backed WLAN (Mist NAC) gets
    # NO {ssid}_nac reference here — that group is never created (central_radius
    # emits nothing for NAC), so referencing it would dangle. The Central NAC
    # reference is a separate (future) writer; central_write_wlan flags such a
    # WLAN as unresolved so execution blocks rather than inventing the reference.
    is_radius_group = bool(sec.auth_source and sec.auth_source.kind == AuthSourceKind.RADIUS_GROUP)
    if is_radius_group and (sec.key_mgmt == KeyMgmt.ENTERPRISE or sec.mac_auth):
        body["auth-server-group"] = server_group_name(canon.ssid)
    if sec.mac_auth:
        body["mac-authentication"] = True
    if sec.radius:
        # accounting points at the same group when acct servers are present.
        if sec.radius.acct_servers:
            body["acct-server-group"] = server_group_name(canon.ssid)
        if sec.radius.interim_interval:
            body["radius-interim-accounting-interval"] = sec.radius.interim_interval

    # --- VLAN: named → NAMED_VLAN/vlan-name; numeric id → VLAN_RANGES/vlan-id-range ---
    if canon.vlan.mode in (VlanMode.NAMED, VlanMode.DYNAMIC) and canon.vlan.name:
        body["vlan-selector"] = "NAMED_VLAN"
        body["vlan-name"] = canon.vlan.name
    elif canon.vlan.mode == VlanMode.ID and canon.vlan.id is not None:
        body["vlan-selector"] = "VLAN_RANGES"
        body["vlan-id-range"] = [str(canon.vlan.id)]
    elif canon.vlan.mode == VlanMode.NAMED and canon.vlan.id is not None:
        # named mode but only a numeric id resolved → treat as a range
        body["vlan-selector"] = "VLAN_RANGES"
        body["vlan-id-range"] = [str(canon.vlan.id)]

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


def _assign_call(profile: str, scope_id: str | None, kind: str, name: str, depends_on: list[int]) -> dict[str, Any]:
    """One config-assignment call descriptor.

    The body shape is identical for every scope-type — Central infers the
    scope-type (GLOBAL / SITE_COLLECTION / SITE / DEVICE_COLLECTION) from the
    scope-id, so only the id varies (live-confirmed against the SITE path).
    ``unresolved`` carries the unresolved scope name when the caller couldn't
    map it, so the consuming skill can create the scope first. ``depends_on`` is
    the prerequisite that must exist before assigning — the WLAN create for a
    bridged SSID, or the overlay binding for a tunneled/hybrid one (so a failed
    overlay blocks the assignment rather than activating an unbound WLAN).
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
        "depends_on": list(depends_on),
        "unresolved": None if scope_id else {"kind": kind, "name": name},
    }


def _overlay_call(
    profile: str,
    essid: str,
    gw_cluster_list: list[dict[str, Any]] | None,
    *,
    use_alias: bool = False,
    depends_on: list[int] | None = None,
) -> dict[str, Any]:
    """One overlay-wlan call binding a tunneled/hybrid SSID to its gateway cluster(s).

    ``gw-cluster-list`` entries are resolved by the caller (neutral cluster names →
    Central ``{cluster, cluster-type, cluster-scope-id, cluster-redundancy-type,
    tunnel-type}``). ``unresolved_clusters`` flags a missing/empty list — a
    tunneled SSID with no cluster binding is incomplete.
    """
    body: dict[str, Any] = {
        "profile": profile,
        "overlay-profile-type": "WIRELESS_PROFILE",
        "use-essid-alias": use_alias,
        "gw-cluster-list": gw_cluster_list or [],
    }
    body["essid-alias-name" if use_alias else "essid-name"] = essid
    return {
        "method": "POST",
        "path": f"{_OVERLAY_WLAN}/{profile}",
        "query": {},
        "body": body,
        "purpose": f"Bind '{profile}' to gateway cluster(s) (overlay-wlan)",
        "depends_on": depends_on or [],
        "unresolved_clusters": not gw_cluster_list,
    }


def _dual_mode_calls(
    canon: CanonicalWlan,
    gw_cluster_list: list[dict[str, Any]] | None,
) -> list[dict[str, Any]]:
    """AOS8 bridged_and_tunneled: one SSID as two profiles sharing an ESSID alias.

    Emits: the ESSID alias, a bridge profile + a tunnel profile (both referencing
    the alias), and the tunnel variant's overlay-wlan cluster binding. Scope
    placement (which sites bridge vs tunnel) is the consuming skill's job via
    config-assignment of each variant — kept out of the writer.
    """
    profile = canon.profile_name or canon.ssid
    essid = canon.ssid
    name_bridge, name_tunnel = f"{profile}-bridge", f"{profile}-tunnel"
    calls: list[dict[str, Any]] = []

    # 0) ESSID alias both profiles reference (so one SSID exists in two modes)
    calls.append(
        {
            "method": "POST",
            "path": f"{_ALIASES}/{essid}",
            "query": {},
            "body": {"type": "ALIAS_ESSID", "default-value": {"essid-value": {"name": essid}}},
            "purpose": f"Create ESSID alias '{essid}' (dual-mode)",
            "depends_on": [],
        }
    )
    # 1) bridge variant, 2) tunnel variant — both reference the alias
    for nm, fwd in ((name_bridge, ForwardMode.BRIDGED), (name_tunnel, ForwardMode.TUNNELED)):
        body = _wlan_body(canon)
        body["ssid"] = nm
        body["essid"] = {"use-alias": True, "alias": essid}
        body["forward-mode"] = _FORWARD_MODE[fwd]
        calls.append(
            {
                "method": "POST",
                "path": f"{_WLAN_SSIDS}/{nm}",
                "query": {},
                "body": body,
                "purpose": f"Create dual {fwd.value} profile '{nm}'",
                "depends_on": [0],
            }
        )
    # 3) overlay binding for the tunnel variant (references the alias)
    calls.append(_overlay_call(name_tunnel, essid, gw_cluster_list, use_alias=True, depends_on=[2]))
    return calls


def central_write_wlan(
    canon: CanonicalWlan,
    *,
    global_scope_id: str | None = None,
    site_name_to_scope_id: dict[str, str] | None = None,
    site_collection_name_to_scope_id: dict[str, str] | None = None,
    device_group_name_to_scope_id: dict[str, str] | None = None,
    gateway_cluster_list: list[dict[str, Any]] | None = None,
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
    # Dual-mode (AOS8 bridged_and_tunneled) has its own shape: alias + two
    # profiles + tunnel overlay. Scope placement is the skill's job.
    if canon.dual_mode:
        return _dual_mode_calls(canon, gateway_cluster_list)

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
    # A NAC-backed auth source has no Central writer yet (NAC is its own future
    # canonical+writer) — flag the create as unresolved so execution blocks
    # rather than creating an enterprise WLAN with no valid auth backend.
    sec = canon.security
    create_call: dict[str, Any] = {
        "method": "POST",
        "path": f"{_WLAN_SSIDS}/{profile}",
        "query": {},
        "body": _wlan_body(canon),
        "purpose": f"Create Central wlan-ssids '{profile}' (library)",
        "depends_on": [],
    }
    if sec.auth_source and sec.auth_source.kind == AuthSourceKind.NAC:
        create_call["unresolved"] = {"kind": "nac_profile", "name": canon.ssid}
    calls.append(create_call)

    # 1b) tunneled / hybrid SSIDs bind to their gateway cluster(s) via overlay-wlan.
    # Assignments must then depend on the overlay (not just the WLAN create): a
    # failed overlay must block the assignment, or we'd activate a tunneled WLAN
    # with no gateway-cluster binding. Bridged WLANs depend on the create only.
    if canon.forward in _OVERLAY_FORWARD:
        calls.append(_overlay_call(profile, canon.ssid, gateway_cluster_list, depends_on=[0]))
        assign_dep = [len(calls) - 1]
    else:
        assign_dep = [0]

    # 2) assignment(s) — one config-assignment per resolved scope facet.
    if asg.org_wide:
        calls.append(_assign_call(profile, global_scope_id, "global", "GLOBAL", assign_dep))
    for name in asg.sites:
        calls.append(_assign_call(profile, sites.get(name), "site", name, assign_dep))
    for name in asg.site_collections:
        calls.append(_assign_call(profile, collections.get(name), "site-collection", name, assign_dep))
    for name in asg.device_groups:
        calls.append(_assign_call(profile, groups.get(name), "device-group", name, assign_dep))

    return calls
