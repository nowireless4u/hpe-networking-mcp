"""AOS 8 ``dot1x_auth_profile`` → normalized Central dot1x-auth source shape.

The AOS 8 dot1x profile has 53 fields (mostly advanced 802.1X tuning). This v1
normalizer maps the confident core (the fields with an unambiguous Central
``dot1xauth`` counterpart) and leaves the nested machine-auth / dot1x-termination
objects and a handful of uncertain knobs for v2 (flagged in the spec's
unmapped_fields). The maintainer's dot1x profiles are all-default, so the
mapped field names come from the Central OAS schema (authoritative) but the
AOS-8→Central field PAIRING for non-default values is preview-confirm.
"""

from __future__ import annotations

from typing import Any


def _leaf(wrapped: Any, subkey: str) -> Any:
    if not isinstance(wrapped, dict):
        return None
    if (wrapped.get("_flags") or {}).get("default"):
        return None
    return wrapped.get(subkey)


def _flag(source: dict, key: str) -> bool | None:
    obj = source.get(key)
    if not isinstance(obj, dict):
        return None
    if (obj.get("_flags") or {}).get("default"):
        return None
    return True


# (aos8_field, subkey, normalized_key) — confident scalar mappings.
_SCALARS = [
    ("reauth_period", "ra-period", "_reauth_period"),
    ("reauth_max_requests", "ramx-requests", "_max_reauth"),
    ("max_requests", "mx-requests", "_eapol_max_requests"),
    ("server_cert", "server-cert-name", "_server_cert"),
    ("ca_cert", "ca-cert-name", "_ca_cert"),
    ("framed_mtu", "fmtu", "_framed_mtu"),
    ("quiet_period", "qt-period", "_quiet_period"),
    ("heldstate_bypass_counter", "hs-counter", "_heldstate_bypass"),
    ("wep_key_size", "wk-size", "_wep_key_size"),
    ("wep_key_retries", "wk-retries", "_wep_key_retries"),
    ("tls_guest_role", "tg-role", "_tls_guest_role"),
    ("ukey_period", "ukr-period", "_unicast_key_rotation_period"),
    ("mkey_period", "mkr-period", "_multicast_key_rotation_period"),
    ("wpakey_period_ms", "wk-period", "_wpa_key_period"),
    ("wpa2key_delay", "wk-delay", "_wpa2_key_delay"),
    ("wpagkey_delay", "wgk-delay", "_wpa_groupkey_delay"),
    ("wpa_key_retries", "wpak-retries", "_wpa_key_retries"),
]

# aos8 presence-flag field -> normalized_key (Central boolean).
_FLAGS = {
    "reauthentication": "_reauth_enable",
    "tls_guest_access": "_tls_guest_access",
    "enforce_suite_b_128": "_suite_b_128",
    "enforce_suite_b_192": "_suite_b_192",
    "validate_pmkid": "_validate_pmkid",
    "eapol_logoff": "_eapol_logoff",
    "dot1x_cert_cn_lookup": "_cert_cn_lookup",
    "opp_key_caching": "_opp_key_caching",
    "unicast_keyrotation": "_unicast_keyrotation",
    "multicast_keyrotation": "_multicast_keyrotation",
    "use_static_key": "_use_static_key",
    "use_session_key": "_use_session_key",
    "wpa_fast_handover": "_wpa_fast_handover",
}


def preprocess_dot1x_auth(source_data: dict, runtime_values: dict) -> dict:
    """Flatten a ``dot1x_auth_profile`` record into ``_<field>`` keys (core subset)."""
    sd = source_data
    norm: dict[str, Any] = {"_name": sd.get("profile-name")}
    for src_field, subkey, key in _SCALARS:
        norm[key] = _leaf(sd.get(src_field), subkey)
    for src_field, key in _FLAGS.items():
        norm[key] = _flag(sd, src_field)
    return {**source_data, **{k: v for k, v in norm.items() if v is not None}}
