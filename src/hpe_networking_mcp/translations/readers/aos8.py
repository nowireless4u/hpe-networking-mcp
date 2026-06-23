"""AOS 8 → canonical WLAN reader.

Builds a platform-neutral ``CanonicalWlan`` from an AOS 8 ``virtual_ap`` plus the
profiles it references (``ssid_prof`` for essid/opmode, ``aaa_prof`` →
``server_group`` → ``rad_server`` for RADIUS). AOS 8 is source-only — the Central
construction lives in the Central writer.

Joins mirror the validated AOS 8 translations: the source record is one
``virtual_ap``; the referenced ``ssid_prof`` / ``aaa_prof`` / ``server_group`` /
``rad_server`` records are supplied by the caller (the migration skill fetches
them per scope) and joined by name here.

Forward mode is the **operator's** target decision (``target_mode``) — the source
``virtual_ap.forward_mode`` only *recommends* it (see the SSID-mode design memo).
"""

from __future__ import annotations

from typing import Any

from hpe_networking_mcp.translations.canonical.wlan import (
    AuthSource,
    AuthSourceKind,
    CanonicalWlan,
    Cipher,
    CoaServer,
    ForwardMode,
    KeyMgmt,
    RadiusConfig,
    RadiusServer,
    Security,
    Vlan,
    VlanMode,
    WpaVersion,
)

# AOS 8 ssid_prof opmode key → neutral (key_mgmt, wpa_version, cipher) triplet.
_OPMODE_TO_TRIPLET: dict[str, tuple[KeyMgmt, str, Cipher]] = {
    "opensystem": (KeyMgmt.OPEN, "none", Cipher.NONE),
    "enhanced-open": (KeyMgmt.OWE, "none", Cipher.NONE),
    "static-wep": (KeyMgmt.WEP_STATIC, "none", Cipher.WEP),
    "dynamic-wep": (KeyMgmt.WEP_DYNAMIC, "none", Cipher.WEP),
    "wpa-aes": (KeyMgmt.ENTERPRISE, "wpa", Cipher.AES_CCM),
    "wpa-tkip": (KeyMgmt.ENTERPRISE, "wpa", Cipher.TKIP),
    "wpa-psk-aes": (KeyMgmt.PSK, "wpa", Cipher.AES_CCM),
    "wpa-psk-tkip": (KeyMgmt.PSK, "wpa", Cipher.TKIP),
    "wpa2-aes": (KeyMgmt.ENTERPRISE, "wpa2", Cipher.AES_CCM),
    "wpa2-tkip": (KeyMgmt.ENTERPRISE, "wpa2", Cipher.TKIP),
    "wpa2-psk-aes": (KeyMgmt.PSK, "wpa2", Cipher.AES_CCM),
    "wpa2-psk-tkip": (KeyMgmt.PSK, "wpa2", Cipher.TKIP),
    "wpa3-sae-aes": (KeyMgmt.SAE, "wpa3", Cipher.AES_CCM),
    "wpa3-aes-ccm-128": (KeyMgmt.ENTERPRISE, "wpa3", Cipher.AES_CCM),
    "wpa3-aes-gcm-256": (KeyMgmt.ENTERPRISE, "wpa3", Cipher.GCM_256),
    "wpa3-cnsa": (KeyMgmt.ENTERPRISE, "wpa3", Cipher.CNSA),
    "mpsk-aes": (KeyMgmt.MPSK, "wpa2", Cipher.AES_CCM),
}

# operator target_mode → (ForwardMode, dual_mode)
_TARGET_MODE = {
    "bridged": (ForwardMode.BRIDGED, False),
    "tunneled": (ForwardMode.TUNNELED, False),
    "hybrid": (ForwardMode.HYBRID, False),
    "bridged_and_tunneled": (ForwardMode.TUNNELED, True),
}

_DEFAULT_AUTH_PORT = 1812
_DEFAULT_ACCT_PORT = 1813
_DEFAULT_COA_PORT = 3799


def _leaf(wrapped: Any, subkey: str) -> Any:
    """Unwrap a one-level AOS 8 field; None if absent or operator-default."""
    if not isinstance(wrapped, dict):
        return None
    if (wrapped.get("_flags") or {}).get("default"):
        return None
    return wrapped.get(subkey)


def _opmode_key(opmode_obj: Any) -> str | None:
    """AOS 8 opmode is ``{<mode>: true, _flags: {...}}`` — return the mode key."""
    if not isinstance(opmode_obj, dict):
        return None
    for k, v in opmode_obj.items():
        if k == "_flags":
            continue
        if v is True or v == "true":
            return k
    return None


def _index(records: list[dict] | None, *name_keys: str) -> dict[str, dict]:
    """Index records by their profile/server name (first matching key wins)."""
    out: dict[str, dict] = {}
    for r in records or []:
        if not isinstance(r, dict):
            continue
        for k in name_keys:
            if r.get(k):
                out[r[k]] = r
                break
    return out


def _members(group: dict | None) -> list[str]:
    """Member auth-server names listed on an AOS 8 server_group (``auth_server[].name``)."""
    names: list[str] = []
    for m in (group or {}).get("auth_server") or []:
        if isinstance(m, dict) and m.get("name"):
            names.append(m["name"])
    return names


def _rad_server(rec: dict, port_subkey: str, default_port: int) -> RadiusServer:
    host = _leaf(rec.get("rad_host"), "host") or ""
    port = _leaf(rec.get(f"rad_{port_subkey}"), port_subkey) or default_port
    secret = _leaf(rec.get("rad_key"), "key")
    return RadiusServer(host=host, port=int(port) if port else None, secret=secret)


def _radius(
    aaa_prof: dict | None,
    server_groups: dict[str, dict],
    auth_servers: dict[str, dict],
) -> RadiusConfig | None:
    """Walk aaa_prof → server-groups → rad_servers into a canonical RadiusConfig."""
    if not aaa_prof:
        return None
    dot1x_sg = _leaf(aaa_prof.get("dot1x_server_group"), "srv-group")
    mba_sg = _leaf(aaa_prof.get("mba_server_group"), "srv-group")
    acct_sg = _leaf(aaa_prof.get("rad_acct_sg"), "server_group_name")
    coa_ips = [
        c["rfc3576_server"]
        for c in (aaa_prof.get("rfc3576_client") or [])
        if isinstance(c, dict) and c.get("rfc3576_server")
    ]

    def servers_of(sg_name: str | None, port_subkey: str, default_port: int) -> list[RadiusServer]:
        out: list[RadiusServer] = []
        for m in _members(server_groups.get(sg_name or "")):
            rec = auth_servers.get(m)
            if rec:
                out.append(_rad_server(rec, port_subkey, default_port))
        return out

    auth = servers_of(dot1x_sg or mba_sg, "authport", _DEFAULT_AUTH_PORT)
    acct = servers_of(acct_sg, "acctport", _DEFAULT_ACCT_PORT)
    coa = [CoaServer(ip=ip, port=_DEFAULT_COA_PORT) for ip in coa_ips]

    if not (auth or acct or coa):
        return None
    return RadiusConfig(auth_servers=auth, acct_servers=acct, coa=coa)


def _vlan(virtual_ap: dict) -> Vlan:
    val = _leaf(virtual_ap.get("vlan"), "vlan")
    if val is None:
        return Vlan(mode=VlanMode.NONE)
    if str(val).isdigit():
        return Vlan(mode=VlanMode.ID, id=int(val))
    return Vlan(mode=VlanMode.NAMED, name=str(val))


def _security(ssid_prof: dict, aaa_prof: dict | None, server_groups, auth_servers) -> Security:
    triplet = _OPMODE_TO_TRIPLET.get(_opmode_key(ssid_prof.get("opmode")) or "")
    if triplet:
        km, wpa, cipher = triplet
    else:
        km, wpa, cipher = KeyMgmt.OPEN, "none", Cipher.NONE

    sec = Security(key_mgmt=km, wpa_version=WpaVersion(wpa), cipher=cipher)
    mba = _leaf((aaa_prof or {}).get("mba_server_group"), "srv-group")
    sec.mac_auth = bool(mba)

    if km in (KeyMgmt.PSK, KeyMgmt.SAE):
        psk = _leaf(ssid_prof.get("wpa_passphrase"), "wpa-passphrase")
        if psk:
            sec.psk = psk

    if km == KeyMgmt.ENTERPRISE or sec.mac_auth:
        sec.auth_source = AuthSource(kind=AuthSourceKind.RADIUS_GROUP, ref=None)
        sec.radius = _radius(aaa_prof, server_groups, auth_servers)
    return sec


def aos8_read_wlan(
    virtual_ap: dict[str, Any],
    *,
    ssid_profiles: list[dict] | None = None,
    aaa_profiles: list[dict] | None = None,
    server_groups: list[dict] | None = None,
    auth_servers: list[dict] | None = None,
    target_mode: str = "bridged",
    gateway_clusters: list[str] | None = None,
) -> CanonicalWlan:
    """Build a ``CanonicalWlan`` from an AOS 8 ``virtual_ap`` + referenced profiles.

    Args:
        virtual_ap: the source VAP record (the WLAN broadcast definition).
        ssid_profiles: candidate ``ssid_prof`` records (joined by name → essid/opmode).
        aaa_profiles: candidate ``aaa_prof`` records (joined by name → RADIUS chain).
        server_groups: candidate ``server_group`` records (member auth-server names).
        auth_servers: candidate ``rad_server`` records (host/secret/ports).
        target_mode: operator forward-mode decision — bridged / tunneled / hybrid /
            bridged_and_tunneled (the source forward_mode only recommends).
        gateway_clusters: neutral cluster names for tunneled/hybrid/dual overlay.
    """
    sp_by = _index(ssid_profiles, "profile-name")
    aaa_by = _index(aaa_profiles, "profile-name")
    # AOS 8 server-groups (server_group_prof) key on ``sg_name``, not profile-name.
    sg_by = _index(server_groups, "sg_name", "profile-name")
    as_by = _index(auth_servers, "rad_server_name", "tacacs_server_name")

    sp_name = _leaf(virtual_ap.get("ssid_prof"), "profile-name")
    ssid_prof = sp_by.get(sp_name or "", {})
    aaa_name = _leaf(virtual_ap.get("aaa_prof"), "profile-name")
    aaa_prof = aaa_by.get(aaa_name or "")

    essid = _leaf(ssid_prof.get("essid"), "essid") or virtual_ap.get("profile-name", "")
    forward, dual = _TARGET_MODE.get(target_mode, (ForwardMode.BRIDGED, False))

    return CanonicalWlan(
        ssid=essid,
        profile_name=virtual_ap.get("profile-name"),
        enabled=True,
        hidden=bool(_leaf(ssid_prof.get("hide_ssid"), "hide-ssid")),
        security=_security(ssid_prof, aaa_prof, sg_by, as_by),
        vlan=_vlan(virtual_ap),
        forward=forward,
        dual_mode=dual,
        gateway_clusters=list(gateway_clusters or []),
    )
