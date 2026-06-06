"""AOS 8 ``aaa_prof`` → normalized Central aaa-profile source shape.

``central:aaa_profile`` is the gateway AAA keystone — it ties the chain
together by referencing the dot1x/mac-auth profiles, server-groups, roles, and
CoA servers built by the other translations. The AOS 8 ``aaa_prof`` wraps every
value one level deep (``rad_acct_sg: {"server_group_name": ...}``) and the
Central target nests the auth/role bindings under ``authentication`` /
``authorization`` sub-objects, so this normalizer flattens the top-level fields
and pre-builds those two sub-dicts (substituted whole into the body). Field
correspondence locked against the vendored AOS 8 OAS (``/object/aaa_prof``) and
the Central aaa-profile schema.
"""

from __future__ import annotations

from typing import Any


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


# AOS 8 aaa_prof field (+ sub-key) -> Central authentication.<key>
_AUTHENTICATION_MAP = [
    ("dot1x_auth_profile", "profile-name", "dot1x-auth"),
    ("dot1x_default_role", "default-role", "dot1x-default-role"),
    ("dot1x_server_group", "srv-group", "dot1xauth-server-group"),
    ("mac_auth_profile", "profile-name", "mac-auth"),
    ("mac_default_role", "default-role", "mac-default-role"),
    ("mba_server_group", "srv-group", "macauth-server-group"),
]

# AOS 8 aaa_prof flag field -> Central top-level boolean
_FLAG_MAP = {
    "enforce_dhcp": "_enforce_dhcp",
    "enable_rad_interim_acct": "_interim_acct",
    "enable_roaming_rad_acct": "_roam_acct",
    "l2_auth_fail_through": "_l2_fail_through",
    "multiple_server_accounting": "_multi_acct",
    "open_system_rad_acc": "_open_acct",
    "incl_acct_sess_id_in_access": "_acct_sess_id",
    "integrate_pan": "_pan",
    "wired_reauth_on_vlan_change": "_reauth_vlan",
    "username_from_dhcp_opt12": "_dhcp_opt12",
    "wwroam": "_wwroam",
    "ageout_on_bridge": "_ageout_bridge",
    "devtype_classification": "_devtype",
    "download_role": "_download_role",
}


def preprocess_aaa_profile(source_data: dict, runtime_values: dict) -> dict:
    """Flatten an ``aaa_prof`` record into ``_<field>`` keys + nested sub-dicts."""
    sd = source_data
    norm: dict[str, Any] = {
        "_name": sd.get("profile-name"),
        "_acct_sg": _leaf(sd.get("rad_acct_sg"), "server_group_name"),
        "_max_ipv4": _leaf(sd.get("max_ipv4_for_wireless"), "max_ipv4_users"),
        "_user_idle": _leaf(sd.get("user_idle_timeout_aaa"), "seconds"),
        "_udr": _leaf(sd.get("udr_group"), "udr_group"),
    }
    for src_field, tgt in _FLAG_MAP.items():
        norm[tgt] = _flag(sd, src_field)

    # CoA server references (also drives auth_server's AUTH_AND_COA correlation).
    coa = [
        c["rfc3576_server"] for c in (sd.get("rfc3576_client") or []) if isinstance(c, dict) and c.get("rfc3576_server")
    ]
    norm["_coa_list"] = coa or None

    # Nested authentication block (dot1x/mac-auth profile + server-group + role refs).
    auth: dict[str, Any] = {}
    for src_field, subkey, tgt in _AUTHENTICATION_MAP:
        val = _leaf(sd.get(src_field), subkey)
        if val is not None:
            auth[tgt] = val
    norm["_authentication"] = auth or None

    # Nested authorization block. AOS 8 aaa_prof.default_user_role is the
    # profile's base/initial role -> Central pre-auth-role (semantic-verify).
    authz: dict[str, Any] = {}
    base_role = _leaf(sd.get("default_user_role"), "role")
    if base_role is not None:
        authz["pre-auth-role"] = base_role
    norm["_authorization"] = authz or None

    return {**source_data, **{k: v for k, v in norm.items() if v is not None}}
