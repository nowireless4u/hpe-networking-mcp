"""AOS 8 ``mac_auth_profile`` → normalized Central mac-auth source shape.

Small profile (8 fields). The normalizer unwraps the one-level-wrapped values
and presence flags into ``_<field>`` keys for ``central:mac_auth``'s per-field
key_mappings. Referenced by name from the gateway aaa-profile
(``authentication.mac-auth``).
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


def preprocess_mac_auth(source_data: dict, runtime_values: dict) -> dict:
    """Flatten a ``mac_auth_profile`` record into ``_<field>`` keys."""
    sd = source_data
    norm: dict[str, Any] = {
        "_name": sd.get("profile-name"),
        "_reauth_period": _leaf(sd.get("mac_reauth_period"), "ra-period"),
        "_max_retries": _leaf(sd.get("mba_maxf"), "max-authentication-failures"),
        # MAC address formatting enums (AOS value passed through; Central enum
        # spelling not yet live-verified — see draft_notes).
        "_case_type": _leaf(sd.get("mba_case"), "mba_case_t"),
        "_address_format": _leaf(sd.get("mba_fmt"), "mba_delimiter_t"),
        # presence flags
        "_reauth_enable": _flag(sd, "mac_reauthentication"),
        "_use_server_reauth": _flag(sd, "mac_use_server_reauth_period"),
    }
    return {**source_data, **{k: v for k, v in norm.items() if v is not None}}
