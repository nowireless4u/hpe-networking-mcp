"""Canonical → Mist WLAN writer.

Emits the ordered Mist API calls to mirror a canonical WLAN: a per-WLAN WLAN
template (carrying the scope assignment via ``applies``) + the org WLAN that
references it. Mist is ID-based — the WLAN needs the template's ``id``, which only
exists after the template is created — so the template call ``capture``s its
response ``id`` and the WLAN call ``inject``s it as ``template_id`` (the
orchestrator's executor threads it through).

RADIUS is emitted **inline** on the WLAN (Mist's native model: ``auth_servers`` /
``acct_servers`` / ``coa_servers``), not as a server-group. A ``{{var}}`` host
(from a Central alias) passes straight through — Mist resolves it per site.
Central NAC → ``mist_nac.enabled``; cloud-MPSK → ``dynamic_psk``.
"""

from __future__ import annotations

from typing import Any

from hpe_networking_mcp.translations.canonical.wlan import (
    AuthSourceKind,
    CanonicalWlan,
    KeyMgmt,
    MpskSource,
    VlanMode,
    WpaVersion,
)

# WPA generation → Mist pairwise list (personal/enterprise share the ciphers).
_PAIRWISE = {
    WpaVersion.WPA: ["wpa1-ccmp"],
    WpaVersion.WPA2: ["wpa2-ccmp"],
    WpaVersion.WPA_WPA2: ["wpa1-ccmp", "wpa2-ccmp"],
    WpaVersion.WPA3: ["wpa3"],
}


def _auth(canon: CanonicalWlan) -> dict[str, Any]:
    """Map the neutral triplet → Mist ``auth`` block."""
    sec = canon.security
    km = sec.key_mgmt
    auth: dict[str, Any] = {}

    if km in (KeyMgmt.OPEN, KeyMgmt.OWE):
        auth["type"] = "open"
        if km == KeyMgmt.OWE:
            auth["owe"] = "enabled"
    elif km == KeyMgmt.SAE:
        auth["type"] = "psk"
        auth["pairwise"] = ["wpa3"]
    elif km in (KeyMgmt.PSK, KeyMgmt.MPSK):
        auth["type"] = "psk"
        auth["pairwise"] = _PAIRWISE.get(sec.wpa_version, ["wpa2-ccmp"])
    elif km == KeyMgmt.ENTERPRISE:
        auth["type"] = "eap"
        auth["pairwise"] = _PAIRWISE.get(sec.wpa_version, ["wpa2-ccmp"])

    if sec.wpa2_wpa3_transition:
        auth["pairwise"] = sorted(set(auth.get("pairwise", [])) | {"wpa3", "wpa2-ccmp"})
    if km in (KeyMgmt.PSK, KeyMgmt.SAE) and sec.psk:
        auth["psk"] = sec.psk
    if sec.mac_auth:
        auth["enable_mac_auth"] = True
    return auth


def _radius(canon: CanonicalWlan, body: dict[str, Any]) -> None:
    """Inline the canonical RADIUS servers onto the Mist WLAN body."""
    rad = canon.security.radius
    if not rad:
        return
    if rad.auth_servers:
        body["auth_servers"] = [
            {"host": s.host, "port": s.port or 1812, "secret": s.secret or ""} for s in rad.auth_servers
        ]
        body["auth_server_selection"] = rad.server_selection or "ordered"
    if rad.acct_servers:
        body["acct_servers"] = [
            {"host": s.host, "port": s.port or 1813, "secret": s.secret or ""} for s in rad.acct_servers
        ]
    if rad.coa:
        body["coa_servers"] = [
            {"ip": c.ip, "port": c.port or 3799, "secret": c.secret or "", "enabled": True} for c in rad.coa
        ]
        body["coa_enabled"] = True


def _vlan(canon: CanonicalWlan, body: dict[str, Any]) -> None:
    v = canon.vlan
    if v.mode == VlanMode.ID and v.id is not None:
        body["vlan_enabled"] = True
        body["vlan_id"] = v.id
    elif v.mode in (VlanMode.NAMED, VlanMode.DYNAMIC) and v.name:
        body["vlan_enabled"] = True
        body["dynamic_vlan"] = {"enabled": True, "type": "standard", "vlans": {v.name: ""}}


def _wlan_body(canon: CanonicalWlan) -> dict[str, Any]:
    sec = canon.security
    body: dict[str, Any] = {
        "ssid": canon.ssid,
        "enabled": canon.enabled,
        "hide_ssid": canon.hidden,
        "auth": _auth(canon),
    }
    # Mist NAC vs external RADIUS vs cloud-MPSK
    if sec.auth_source and sec.auth_source.kind == AuthSourceKind.NAC:
        body["mist_nac"] = {"enabled": True}
    else:
        _radius(canon, body)
    if sec.key_mgmt == KeyMgmt.MPSK and sec.mpsk_source == MpskSource.CLOUD:
        body["dynamic_psk"] = {"enabled": True, "source": "cloud"}

    _vlan(canon, body)
    if canon.performance.dtim is not None:
        body["dtim"] = canon.performance.dtim
    if canon.performance.max_clients is not None:
        body["max_num_clients"] = canon.performance.max_clients
    if canon.isolation.client_isolation:
        body["isolation"] = True
    return body


def _applies(canon: CanonicalWlan, *, org_id, sites, sitegroups, deviceprofiles) -> tuple[dict[str, Any], list[dict]]:
    """Build the template ``applies`` block + any unresolved-scope flags."""
    asg = canon.assignment
    applies: dict[str, Any] = {}
    unresolved: list[dict] = []

    if asg.org_wide:
        applies["org_id"] = org_id

    def resolve(names: list[str], mapping: dict[str, str], kind: str) -> list[str]:
        ids: list[str] = []
        for n in names:
            mid = (mapping or {}).get(n)
            if mid:
                ids.append(mid)
            else:
                unresolved.append({"kind": kind, "name": n})
        return ids

    site_ids = resolve(asg.sites, sites, "site")
    if site_ids:
        applies["site_ids"] = site_ids
    sg_ids = resolve(asg.site_collections, sitegroups, "sitegroup")
    if sg_ids:
        applies["sitegroup_ids"] = sg_ids
    dp_ids = resolve(asg.device_groups, deviceprofiles, "deviceprofile")
    if dp_ids:
        applies["deviceprofile_ids"] = dp_ids
    return applies, unresolved


def mist_write_wlan(
    canon: CanonicalWlan,
    *,
    org_id: str | None = None,
    site_name_to_id: dict[str, str] | None = None,
    sitegroup_name_to_id: dict[str, str] | None = None,
    deviceprofile_name_to_id: dict[str, str] | None = None,
) -> list[dict[str, Any]]:
    """Emit the ordered Mist calls: create a per-WLAN template, then the WLAN.

    The WLAN's ``template_id`` is injected from the template create's response
    ``id`` by the executor (Mist is ID-based). Names in the canonical assignment
    are resolved to Mist site / sitegroup / deviceprofile ids via the supplied
    maps; unresolved names are flagged so execution blocks.
    """
    ssid = canon.ssid
    base = f"/api/v1/orgs/{org_id}/templates"
    applies, unresolved = _applies(
        canon,
        org_id=org_id,
        sites=site_name_to_id,
        sitegroups=sitegroup_name_to_id,
        deviceprofiles=deviceprofile_name_to_id,
    )
    template_body: dict[str, Any] = {"name": f"{ssid}-template", "applies": applies}
    if canon.assignment.device_groups:
        # device-group targeting requires the per-device-profile filter on the template
        template_body["filter_by_deviceprofile"] = True
        template_body["deviceprofile_ids"] = applies.get("deviceprofile_ids", [])

    template_call = {
        "method": "POST",
        "path": base,
        "query": {},
        "body": template_body,
        "purpose": f"Create Mist WLAN template '{ssid}-template'",
        "depends_on": [],
        "capture": "template_id",  # save response.id under this key
        "idempotent": False,  # Mist creates POST to a collection (no GET-by-path)
        "unresolved": unresolved or None,
    }

    wlan_call: dict[str, Any] = {
        "method": "POST",
        "path": f"/api/v1/orgs/{org_id}/wlans",
        "query": {},
        "body": _wlan_body(canon),
        "purpose": f"Create Mist WLAN '{ssid}'",
        "depends_on": [0],
        "inject": {"template_id": "template_id"},  # body[template_id] = captured.template_id
        "idempotent": False,
    }
    # WEP has no clean Mist mapping in this writer — block rather than emit an
    # empty/invalid auth block (a silent create with unintended auth defaults).
    if canon.security.key_mgmt in (KeyMgmt.WEP_STATIC, KeyMgmt.WEP_DYNAMIC):
        wlan_call["unresolved"] = [
            {"kind": "unsupported_auth", "name": f"{ssid} (WEP is not supported by the Mist writer)"}
        ]
    return [template_call, wlan_call]
