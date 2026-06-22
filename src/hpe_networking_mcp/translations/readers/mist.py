"""Mist → canonical WLAN reader.

Extracts a platform-neutral ``CanonicalWlan`` from a Mist WLAN object (org- or
site-level) plus, optionally, its WLAN template (for the assignment facet).
Mirrors the field map in ``docs/mappings/WLAN.md`` and the validated
``platforms/wlan_mapper.py`` logic, but produces canonical — the Central
construction lives in the Central *writer*, not here.
"""

from __future__ import annotations

from typing import Any

from hpe_networking_mcp.translations.canonical.wlan import (
    Assignment,
    AssignmentExceptions,
    AuthSource,
    AuthSourceKind,
    CanonicalWlan,
    CoaServer,
    FastRoam,
    ForwardMode,
    Isolation,
    MpskSource,
    Performance,
    RadiusConfig,
    RadiusServer,
    Rates,
    Security,
    SecurityMode,
    Vlan,
    VlanMode,
    Wmm,
)

# Mist interface values that mean "bridged" (everything else = tunneled).
_BRIDGED_INTERFACES = {"", "all", "ethernet"}


def _security(wlan: dict[str, Any]) -> Security:
    auth = wlan.get("auth") or {}
    atype = auth.get("type", "open")
    pairwise = auth.get("pairwise") or []
    mist_nac = bool((wlan.get("mist_nac") or {}).get("enabled"))
    dyn_psk = wlan.get("dynamic_psk")
    has_dyn_psk = bool(dyn_psk) and dyn_psk not in ({}, [])
    transition = ("wpa3" in pairwise) and ("wpa2-ccmp" in pairwise)

    sec = Security(mode=SecurityMode.OPEN)

    if atype == "open":
        sec.mode = SecurityMode.OPEN
    elif atype == "psk":
        if has_dyn_psk:
            sec.mode = SecurityMode.MPSK
            source = None
            if isinstance(dyn_psk, dict):
                source = dyn_psk.get("source")
            sec.mpsk_source = MpskSource.LOCAL if source == "local" else MpskSource.CLOUD
        elif pairwise == ["wpa3"]:
            sec.mode = SecurityMode.SAE
        else:
            sec.mode = SecurityMode.PSK
    elif atype == "eap":
        sec.mode = SecurityMode.ENTERPRISE

    sec.wpa2_wpa3_transition = transition
    sec.mac_auth = bool(auth.get("enable_mac_auth"))

    if sec.mode in (SecurityMode.PSK, SecurityMode.SAE):
        psk = auth.get("psk")
        if psk:
            sec.psk = psk

    # Enterprise auth source: Mist NAC → the separate NAC translation; otherwise
    # external RADIUS server group. The actual NAC/server-group object is its own
    # canonical+writer; here we only record the reference + any inline RADIUS.
    if sec.mode == SecurityMode.ENTERPRISE or sec.mac_auth:
        if mist_nac:
            sec.auth_source = AuthSource(kind=AuthSourceKind.NAC, ref=None)
        else:
            sec.auth_source = AuthSource(kind=AuthSourceKind.RADIUS_GROUP, ref=None)
            sec.radius = _radius(wlan)

    return sec


def _radius(wlan: dict[str, Any]) -> RadiusConfig | None:
    auth_servers = wlan.get("auth_servers") or []
    acct_servers = wlan.get("acct_servers") or []
    coa = wlan.get("coa_servers") or []
    radsec = bool((wlan.get("radsec") or {}).get("enabled"))
    nas_id = wlan.get("auth_servers_nas_id") or None
    nas_ip = wlan.get("auth_servers_nas_ip") or None
    interim = wlan.get("acct_interim_interval") or None

    if not (auth_servers or acct_servers or coa or radsec or nas_id or nas_ip):
        return None

    def _srv(s: dict[str, Any]) -> RadiusServer:
        return RadiusServer(host=s.get("host", ""), port=s.get("port"), secret=s.get("secret"))

    return RadiusConfig(
        auth_servers=[_srv(s) for s in auth_servers],
        acct_servers=[_srv(s) for s in acct_servers],
        server_selection=wlan.get("auth_server_selection"),
        nas_id=nas_id,
        nas_ip=nas_ip,
        coa=[CoaServer(ip=c.get("ip", ""), port=c.get("port"), secret=c.get("secret")) for c in coa],
        radsec=radsec,
        interim_interval=interim,
    )


def _vlan(wlan: dict[str, Any]) -> Vlan:
    dyn = wlan.get("dynamic_vlan") or {}
    if dyn.get("enabled"):
        vlans = dyn.get("vlans") or {}
        name = None
        vid = None
        # dynamic_vlan.vlans is {vlan_id_or_name: label}; default_vlan_ids[0] is the id.
        default_ids = dyn.get("default_vlan_ids") or []
        if default_ids:
            try:
                vid = int(str(default_ids[0]))
            except (ValueError, TypeError):
                vid = None
        if vlans:
            # first value is the VLAN name
            name = next(iter(vlans.values())) if vlans else None
        return Vlan(mode=VlanMode.NAMED if name else VlanMode.DYNAMIC, name=name, id=vid, dynamic=dyn)
    if wlan.get("vlan_enabled") and wlan.get("vlan_id") is not None:
        try:
            return Vlan(mode=VlanMode.ID, id=int(str(wlan["vlan_id"])))
        except (ValueError, TypeError):
            return Vlan(mode=VlanMode.NONE)
    return Vlan(mode=VlanMode.NONE)


def _rates(wlan: dict[str, Any]) -> Rates:
    rs = wlan.get("rateset") or {}
    b24 = (rs.get("24") or {}).get("template")
    b5 = (rs.get("5") or {}).get("template")
    return Rates(band_24=b24, band_5=b5)


def _fast_roam(wlan: dict[str, Any]) -> FastRoam:
    rm = wlan.get("roam_mode", "NONE")
    if rm == "11r":
        return FastRoam.DOT11R
    if rm == "OKC":
        return FastRoam.OKC
    return FastRoam.NONE


def _assignment(
    template: dict[str, Any] | None,
    site_id_to_name: dict[str, str] | None,
    sitegroup_id_to_name: dict[str, str] | None,
    deviceprofile_id_to_name: dict[str, str] | None,
) -> Assignment:
    a = Assignment()
    if not template:
        return a
    site_map = site_id_to_name or {}
    sg_map = sitegroup_id_to_name or {}
    dp_map = deviceprofile_id_to_name or {}
    applies = template.get("applies") or {}
    exc = template.get("exceptions") or {}

    # org-wide: applies carries org_id and no site/sitegroup targets
    if applies.get("org_id") and not applies.get("site_ids") and not applies.get("sitegroup_ids"):
        a.org_wide = True
    a.sites = [site_map.get(sid, sid) for sid in applies.get("site_ids", [])]
    a.site_collections = [sg_map.get(g, g) for g in applies.get("sitegroup_ids", [])]
    if template.get("filter_by_deviceprofile"):
        a.device_groups = [dp_map.get(d, d) for d in template.get("deviceprofile_ids", [])]
    a.exceptions = AssignmentExceptions(
        sites=[site_map.get(sid, sid) for sid in exc.get("site_ids", [])],
        site_collections=[sg_map.get(g, g) for g in exc.get("sitegroup_ids", [])],
    )
    return a


def mist_read_wlan(
    wlan: dict[str, Any],
    *,
    template: dict[str, Any] | None = None,
    site_id_to_name: dict[str, str] | None = None,
    sitegroup_id_to_name: dict[str, str] | None = None,
    deviceprofile_id_to_name: dict[str, str] | None = None,
) -> CanonicalWlan:
    """Build a ``CanonicalWlan`` from a Mist WLAN (+ optional template for assignment)."""
    ssid = wlan.get("ssid", "")
    interface = wlan.get("interface", "")
    forward = ForwardMode.BRIDGED if interface in _BRIDGED_INTERFACES else ForwardMode.TUNNELED

    return CanonicalWlan(
        ssid=ssid,
        profile_name=ssid,
        enabled=bool(wlan.get("enabled", True)),
        hidden=bool(wlan.get("hide_ssid", False)),
        security=_security(wlan),
        vlan=_vlan(wlan),
        bands=list(wlan.get("bands") or []),
        rates=_rates(wlan),
        performance=Performance(
            dtim=wlan.get("dtim"),
            max_clients=wlan.get("max_num_clients"),
            idle_timeout=wlan.get("max_idletime"),
            fast_roam=_fast_roam(wlan),
            wifi7_11be=(not wlan["disable_11be"]) if "disable_11be" in wlan else None,
        ),
        isolation=Isolation(
            client_isolation=bool(wlan.get("isolation", False)),
            limit_bcast=bool(wlan.get("limit_bcast", False)),
            arp_filter=bool(wlan.get("arp_filter", False)),
        ),
        wmm=Wmm(
            enabled=not bool(wlan.get("disable_wmm", False)),
            uapsd=not bool(wlan.get("disable_uapsd", False)),
        ),
        forward=forward,
        portal_deferred=bool((wlan.get("portal") or {}).get("enabled")),
        assignment=_assignment(template, site_id_to_name, sitegroup_id_to_name, deviceprofile_id_to_name),
    )
