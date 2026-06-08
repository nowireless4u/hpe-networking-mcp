"""AOS 8 ``virtual_ap`` (+ joined ``ssid_prof``) → normalized Central wlan-ssid
source shape.

A Central ``wlan-ssids`` profile merges the AOS 8 ``virtual_ap`` (forward-mode,
vlan, aaa-profile ref) with the ``ssid_prof`` it references (essid, opmode,
rates). The source *record* fed to the engine is one ``virtual_ap``; the matching
``ssid_prof`` is supplied via ``runtime_values['ssid_profiles']`` and joined by
name here (mirrors how ``central:policy`` takes ``role_records``).

The **target** forward mode is the operator's decision, supplied as
``runtime_values['target_mode']`` — detection only *recommends* it upstream in
the skill (see the SSID-mode design memory).

Four per-SSID target modes (the questionnaire options):

* ``bridged``  → one profile, ``FORWARD_MODE_BRIDGE`` (local breakout; no cluster)
* ``tunneled`` → one profile, ``FORWARD_MODE_L2``     (+ overlay-wlan cluster bind)
* ``hybrid``   → one profile, ``FORWARD_MODE_MIXED``  (split-tunnel; + overlay)
* ``bridged_and_tunneled`` → the same SSID in BOTH modes at once: an ESSID alias
  + a bridge profile + a tunnel profile (both referencing the alias) + the
  tunnel overlay. The bridge variant lands at ``bridge_scope_id``, the tunnel
  variant at ``tunnel_scope_id`` (large campus tunneled, smaller sites bridged).

Inline bridge-mode AAA, radio/QoS tuning, and the PSK secret remain deferred
(flagged in the spec's unmapped_fields).
"""

from __future__ import annotations

from typing import Any

_SINGLE_FORWARD_MODE = {
    "bridged": "FORWARD_MODE_BRIDGE",
    "tunneled": "FORWARD_MODE_L2",
    "hybrid": "FORWARD_MODE_MIXED",
}
_SINGLE_OVERLAY_MODES = {"tunneled", "hybrid"}
_DUAL_MODE = "bridged_and_tunneled"
_ALL_MODES = set(_SINGLE_FORWARD_MODE) | {_DUAL_MODE}
# Modes that emit an overlay-wlan binding → a non-empty gw_cluster_list is REQUIRED
# (a tunneled/hybrid/dual SSID with no gateway cluster to tunnel to is invalid).
_OVERLAY_MODES = _SINGLE_OVERLAY_MODES | {_DUAL_MODE}

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
# Legacy/no-Central-equivalent opmodes (bSec-128 / bSec-256 / xSec) stay unmapped.


def _leaf(wrapped: Any, subkey: str) -> Any:
    if not isinstance(wrapped, dict):
        return None
    return wrapped.get(subkey)


def _opmode_key(opmode_obj: Any) -> str | None:
    """AOS 8 opmode is ``{<mode-name>: true, _flags: {...}}`` — return the
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
        ValueError: If ``target_mode`` is missing/invalid; if an overlay mode
            (``tunneled`` / ``hybrid`` / ``bridged_and_tunneled``) is missing a
            non-empty ``gw_cluster_list``; or — for ``bridged_and_tunneled`` — if
            ``bridge_scope_id`` / ``tunnel_scope_id`` are absent (engine wraps as
            EngineError).
    """
    target_mode = runtime_values.get("target_mode")
    if target_mode not in _ALL_MODES:
        raise ValueError(
            "preprocess_wlan_ssid requires runtime_values['target_mode'] in "
            f"{sorted(_ALL_MODES)}; got {target_mode!r}. The migration skill supplies this "
            "per SSID from the operator's forward-mode answer."
        )

    # Overlay modes (tunneled / hybrid / bridged_and_tunneled) emit an overlay-wlan
    # binding — they MUST have a non-empty gw_cluster_list (the gateway cluster(s) the
    # SSID tunnels to). Without it the overlay would emit with the binding null-stripped,
    # producing a structurally-incomplete preview that looks valid (issue #438).
    if target_mode in _OVERLAY_MODES and not runtime_values.get("gw_cluster_list"):
        raise ValueError(
            f"target_mode {target_mode!r} emits a gateway-cluster overlay and requires a "
            "non-empty runtime_values['gw_cluster_list'] (the cluster binding the SSID "
            "tunnels to). bridged is the only mode that needs no cluster."
        )

    va = source_data
    profile_name = va.get("profile-name")

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

    # VLAN: virtual_ap.vlan.vlan is a named VLAN (NAMED_VLAN) or numeric id (VLAN_RANGES).
    vlan_val = _leaf(va.get("vlan"), "vlan")
    vlan_name = vlan_id_range = vlan_selector = None
    if vlan_val is not None:
        if str(vlan_val).isdigit():
            vlan_selector, vlan_id_range = "VLAN_RANGES", [str(vlan_val)]
        else:
            vlan_selector, vlan_name = "NAMED_VLAN", str(vlan_val)

    norm: dict[str, Any] = {
        "_name": profile_name,
        "_essid": essid,
        "_opmode": opmode,
        "_vlan_selector": vlan_selector,
        "_vlan_name": vlan_name,
        "_vlan_id_range": vlan_id_range,
        # Overlay cluster bindings (gw-cluster-list) supplied by the skill from
        # detection / operator; passed straight through for the overlay emit(s).
        "_gw_cluster_list": runtime_values.get("gw_cluster_list") or None,
    }

    if target_mode == _DUAL_MODE:
        if not runtime_values.get("bridge_scope_id") or not runtime_values.get("tunnel_scope_id"):
            raise ValueError(
                "target_mode 'bridged_and_tunneled' requires runtime_values['bridge_scope_id'] "
                "and runtime_values['tunnel_scope_id'] (the scopes where each variant applies)."
            )
        # The same SSID in both modes → an ESSID alias both profiles reference.
        norm.update(
            {
                "_emit_dual": True,
                "_essid_alias": essid,
                "_essid_obj_alias": ({"use-alias": True, "alias": essid} if essid else None),
                "_name_bridge": f"{profile_name}-bridge" if profile_name else None,
                "_name_tunnel": f"{profile_name}-tunnel" if profile_name else None,
            }
        )
    else:
        norm.update(
            {
                "_emit_single": True,
                "_essid_obj": ({"name": essid} if essid else None),
                "_forward_mode": _SINGLE_FORWARD_MODE[target_mode],
                "_needs_overlay": (True if target_mode in _SINGLE_OVERLAY_MODES else None),
            }
        )

    return {**source_data, **{k: v for k, v in norm.items() if v is not None}}
