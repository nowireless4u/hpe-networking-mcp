"""AOS 8 ``virtual_ap`` (+ joined ``ssid_prof``) → normalized Central wlan-ssid
source shape.

A Central ``wlan-ssids`` profile merges the AOS 8 ``virtual_ap`` (forward-mode,
vlan, aaa-profile ref) with the ``ssid_prof`` it references (essid, opmode,
rates). The source *record* fed to the engine is one ``virtual_ap``; the matching
``ssid_prof`` is supplied via ``runtime_values['ssid_profiles']`` and joined by
name here (mirrors how ``central:policy`` takes ``role_records``).

The **target** forward mode is the operator's decision, supplied as
``runtime_values['target_mode']`` — detection only *recommends* it upstream in
the skill (see the SSID-mode design memory). v1 handles the single-profile
modes; ``bridged_and_tunneled`` (the two-profile essid-alias case) and full
bridge-mode AAA inlining are deferred to v2 (flagged).

Forward mode → Central enum:

* ``bridged``  → ``FORWARD_MODE_BRIDGE``  (local breakout; no cluster)
* ``tunneled`` → ``FORWARD_MODE_L2``      (gateway-terminated; + overlay-wlan)
* ``hybrid``   → ``FORWARD_MODE_MIXED``   (split-tunnel; + overlay-wlan)
"""

from __future__ import annotations

from typing import Any

# v1 single-profile target modes. bridged_and_tunneled is deferred to v2.
_FORWARD_MODE_BY_TARGET = {
    "bridged": "FORWARD_MODE_BRIDGE",
    "tunneled": "FORWARD_MODE_L2",
    "hybrid": "FORWARD_MODE_MIXED",
}
_DEFERRED_TARGET_MODES = {"bridged_and_tunneled"}
_OVERLAY_MODES = {"tunneled", "hybrid"}

# AOS 8 ssid_prof opmode (the True key in the opmode object) → Central opmode enum.
_OPMODE_MAP = {
    "opensystem": "OPEN",
    "enhanced-open": "ENHANCED_OPEN",
    "static-wep": "STATIC_WEP",
    "dynamic-wep": "DYNAMIC_WEP",
    "wpa-aes": "WPA_ENTERPRISE",
    "wpa-tkip": "WPA_ENTERPRISE",
    "wpa-psk-aes": "WPA_PERSONAL",
    "wpa-psk-tkip": "WPA_PERSONAL",
    "wpa2-aes": "WPA2_ENTERPRISE",
    "wpa2-tkip": "WPA2_ENTERPRISE",
    "wpa2-psk-aes": "WPA2_PERSONAL",
    "wpa2-psk-tkip": "WPA2_PERSONAL",
    "wpa3-sae-aes": "WPA3_SAE",
    "wpa3-aes-ccm-128": "WPA3_ENTERPRISE_CCM_128",
    "wpa3-aes-gcm-256": "WPA3_ENTERPRISE_GCM_256",
    "wpa3-cnsa": "WPA3_ENTERPRISE_CNSA",
    "mpsk-aes": "WPA2_MPSK_AES",
}
# Legacy/no-Central-equivalent opmodes (bSec-128 / bSec-256 / xSec) are left
# unmapped — _opmode stays None and the field is flagged for operator review.


def _leaf(wrapped: Any, subkey: str) -> Any:
    if not isinstance(wrapped, dict):
        return None
    return wrapped.get(subkey)


def _opmode_key(opmode_obj: Any) -> str | None:
    """The AOS 8 opmode is ``{<mode-name>: true, _flags: {...}}`` — return the
    mode-name key (the first non-``_flags`` truthy key)."""
    if not isinstance(opmode_obj, dict):
        return None
    for k, v in opmode_obj.items():
        if k == "_flags":
            continue
        if v is True or v == "true":
            return k
    return None


def preprocess_wlan_ssid(source_data: dict, runtime_values: dict) -> dict:
    """Join a ``virtual_ap`` with its ``ssid_prof`` and normalize for wlan-ssids.

    Raises:
        ValueError: If ``target_mode`` is missing/invalid, or names the deferred
            ``bridged_and_tunneled`` mode (engine wraps as EngineError).
    """
    target_mode = runtime_values.get("target_mode")
    if target_mode in _DEFERRED_TARGET_MODES:
        raise ValueError(
            f"target_mode {target_mode!r} (the two-profile essid-alias case) is deferred to "
            "central:wlan_ssid v2. v1 supports bridged / tunneled / hybrid."
        )
    if target_mode not in _FORWARD_MODE_BY_TARGET:
        raise ValueError(
            "preprocess_wlan_ssid requires runtime_values['target_mode'] in "
            f"{sorted(_FORWARD_MODE_BY_TARGET)}; got {target_mode!r}. The migration skill "
            "supplies this per SSID from the operator's forward-mode answer."
        )

    va = source_data

    # Join the referenced ssid_prof by name from runtime_values.
    sp_name = _leaf(va.get("ssid_prof"), "profile-name")
    ssid_profiles = runtime_values.get("ssid_profiles") or []
    ssid_prof = next(
        (s for s in ssid_profiles if isinstance(s, dict) and s.get("profile-name") == sp_name),
        None,
    )

    essid = _leaf(ssid_prof.get("essid"), "essid") if isinstance(ssid_prof, dict) else None
    opmode_key = _opmode_key(ssid_prof.get("opmode")) if isinstance(ssid_prof, dict) else None
    opmode = _OPMODE_MAP.get(opmode_key) if opmode_key else None

    # VLAN: virtual_ap.vlan.vlan is a named VLAN (NAMED_VLAN) or a numeric id (VLAN_RANGES).
    vlan_val = _leaf(va.get("vlan"), "vlan")
    vlan_name = None
    vlan_id_range = None
    vlan_selector = None
    if vlan_val is not None:
        if str(vlan_val).isdigit():
            vlan_selector = "VLAN_RANGES"
            vlan_id_range = [str(vlan_val)]
        else:
            vlan_selector = "NAMED_VLAN"
            vlan_name = str(vlan_val)

    # essid object: literal {name} in v1. The v2 dual-profile case swaps this for
    # {alias, use-alias} so two profiles can share one logical SSID.
    essid_obj = {"name": essid} if essid else None

    norm: dict[str, Any] = {
        "_name": va.get("profile-name"),
        "_essid": essid,
        "_essid_obj": essid_obj,
        "_opmode": opmode,
        "_forward_mode": _FORWARD_MODE_BY_TARGET[target_mode],
        "_vlan_selector": vlan_selector,
        "_vlan_name": vlan_name,
        "_vlan_id_range": vlan_id_range,
        "_needs_overlay": True if target_mode in _OVERLAY_MODES else None,
        # Overlay cluster bindings (gw-cluster-list) supplied by the skill from
        # detection / operator; passed straight through for the overlay emit.
        "_gw_cluster_list": runtime_values.get("gw_cluster_list") or None,
    }
    return {**source_data, **{k: v for k, v in norm.items() if v is not None}}
