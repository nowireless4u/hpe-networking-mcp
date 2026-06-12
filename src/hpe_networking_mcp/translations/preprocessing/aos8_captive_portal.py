"""AOS 8 ``cp_auth_profile`` → normalized Central captive-portal source shape.

``central:captive_portal`` flattens the AOS 8 ``cp_auth_profile`` record into a
single ``_<param>`` shape the per-field key_mappings consume. The AOS 8 record
mixes one-level-wrapped scalars (``cp_redirect_url: {"redirect-url": ...}``),
empty-object presence flags (``apple_cna_bypass: {}`` = enabled), the
``protocol-http`` flag that INVERTS to Central's ``use-https``, an auth-protocol
enum, and black/white-list arrays — none of which fit a shared per-field
``key_mapping``. Field/param correspondence + transforms + defaults are taken
from the HPE LLD captive-portal mapping (``aaa authentication captive-portal``
→ ``/captive-portal/{name}``).
"""

from __future__ import annotations

from typing import Any

# AOS 8 captive_auth_t enum (['PAP', 'MSCHAPv2', 'chap']) → Central auth-protocol
# enum (PAP / MSCHAPv2 / CHAP). Explicit map (plain upper() would mangle MSCHAPv2).
_AUTH_PROTOCOL = {"PAP": "PAP", "MSCHAPv2": "MSCHAPv2", "chap": "CHAP"}


def _leaf(wrapped: Any, subkey: str) -> Any:
    """Unwrap a one-level AOS 8 field; ``None`` if absent or ``_flags.default``."""
    if not isinstance(wrapped, dict):
        return None
    if (wrapped.get("_flags") or {}).get("default"):
        return None
    return wrapped.get(subkey)


def _flag(source: dict, key: str) -> bool | None:
    """AOS 8 empty-object presence flag → ``True`` when operator-set, else ``None``."""
    obj = source.get(key)
    if not isinstance(obj, dict):
        return None
    if (obj.get("_flags") or {}).get("default"):
        return None
    return True


def _names(arr: Any, subkey: str) -> list[str] | None:
    """Collect ``subkey`` values from an AOS 8 list-of-wrapped-names → list / None."""
    if not isinstance(arr, list):
        return None
    out = [str(i[subkey]) for i in arr if isinstance(i, dict) and i.get(subkey)]
    return out or None


def preprocess_captive_portal(source_data: dict, runtime_values: dict) -> dict:
    """Flatten a ``cp_auth_profile`` record into ``_<param>`` keys (LLD mapping)."""
    sd = source_data
    norm: dict[str, Any] = {
        "_name": sd.get("profile-name"),
        # scalars
        "_default_guest_role": _leaf(sd.get("cp_default_guest_role"), "default-guest-role"),
        "_default_role": _leaf(sd.get("cp_default_role"), "default-role"),
        "_redirect_url": _leaf(sd.get("cp_redirect_url"), "redirect-url"),
        "_ip_addr_in_redir": _leaf(sd.get("ip_addr_in_redir_url"), "ip-addr-in-redirection-url"),
        "_server_group": _leaf(sd.get("cp_server_group"), "server-group"),
        "_url_hash_key": _leaf(sd.get("url_hash_key"), "url-hash-key"),
        "_welcome_page": _leaf(sd.get("cp_welcome_location"), "welcome-page"),
        # ints
        "_logon_min": _leaf(sd.get("cp_min_delay"), "minimum-delay"),
        "_logon_max": _leaf(sd.get("cp_max_delay"), "maximum-delay"),
        "_logon_cpu": _leaf(sd.get("cp_load_thresh"), "cpu-threshold"),
        "_max_auth_fail": _leaf(sd.get("cp_maxf"), "max-authentication-failures"),
        "_redirect_pause": _leaf(sd.get("cp_redirect_pause"), "redirect-pause"),
        "_user_idle": _leaf(sd.get("user_idle_timeout_cp"), "seconds"),
        # presence flags
        "_apple_cna": _flag(sd, "apple_cna_bypass"),
        "_ap_mac_redir": _flag(sd, "ap_mac_in_redir_url"),
        "_guest_logon": _flag(sd, "allow_guest"),
        "_user_logon": _flag(sd, "allow_user"),
        "_enable_welcome": _flag(sd, "cp_welcome_location_enable"),
        "_logout_popup": _flag(sd, "logout_popup"),
        "_show_aup": _flag(sd, "show_aup"),
        "_show_fqdn": _flag(sd, "cp_show_fqdn"),
        "_single_session": _flag(sd, "single_session"),
        "_switch_ip": _flag(sd, "switch_ip_in_redir_url"),
        "_user_vlan_redir": _flag(sd, "user_vlan_in_redir_url"),
        # arrays
        "_deny_list": _names(sd.get("cp_black_list"), "black-list"),
        "_allow_list": _names(sd.get("cp_white_list"), "white-list"),
    }

    # Inverted flag: AOS 8 protocol-http (present = use plain HTTP) -> Central
    # use-https=False. Absent/default -> omit (Central default use-https=True).
    if _flag(sd, "cp_proto_http"):
        norm["_use_https"] = False

    # Enum: authentication_method.captive_auth_t -> auth-protocol.
    auth = _leaf(sd.get("authentication_method"), "captive_auth_t")
    if auth:
        norm["_auth_protocol"] = _AUTH_PROTOCOL.get(auth, str(auth).upper())

    return {**source_data, **{k: v for k, v in norm.items() if v is not None}}
