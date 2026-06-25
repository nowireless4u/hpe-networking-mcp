"""AOS 8 → canonical AAA-chain readers.

Six unidirectional passthrough kinds — ``auth_server`` / ``server_group`` /
``dot1x_auth`` / ``mac_auth`` / ``captive_portal`` / ``aaa_profile`` — each
flattening its AOS 8 record (one-level-wrapped scalars + empty-object presence
flags) onto a Central create body. Absorbs the old ``preprocessing/aos8_*.py``
normalizers; each returns a ``CanonicalCentralProfile`` (shared shape: a Library
create + config-assignment whose ``profile-type`` equals the create type).
"""

from __future__ import annotations

from typing import Any

from hpe_networking_mcp.translations.canonical.auth import CanonicalCentralProfile
from hpe_networking_mcp.translations.readers.aos8._common import flag_unless_default as _flag
from hpe_networking_mcp.translations.readers.aos8._common import leaf

# (aos8_field, subkey, central_key, coerce) scalar spec. coerce: "int" | "str".
ScalarSpec = tuple[str, str, str, str]
# (aos8_flag_field, central_key) presence-flag spec.
FlagSpec = tuple[str, str]


def _coerce(value: Any, how: str) -> Any:
    return int(value) if how == "int" else str(value)


def _build_body(
    record: dict[str, Any],
    name: str,
    scalars: list[ScalarSpec],
    flags: list[FlagSpec],
) -> dict[str, Any]:
    """Build a Central body from scalar + presence-flag specs (drops absent fields)."""
    body: dict[str, Any] = {"name": name}
    for aos8_field, subkey, central_key, how in scalars:
        val = leaf(record.get(aos8_field), subkey)
        if val is not None:
            body[central_key] = _coerce(val, how)
    for aos8_field, central_key in flags:
        if _flag(record, aos8_field):
            body[central_key] = True
    return body


# --------------------------------------------------------------------------- #
# auth_server (RADIUS / TACACS, with CoA correlation)
# --------------------------------------------------------------------------- #
def _coa_peer(host: Any, coa_servers: Any) -> bool:
    """True when a co-located RFC 3576 (CoA) server's IP matches the RADIUS host."""
    if not host or not isinstance(coa_servers, list):
        return False
    for entry in coa_servers:
        if isinstance(entry, dict) and (entry.get("rfc3576_server") or entry.get("server_ip")) == host:
            return True
    return False


def aos8_read_auth_server(
    auth_server: dict[str, Any],
    *,
    coa_servers: list[dict] | None = None,
) -> CanonicalCentralProfile:
    """Build the Central auth-server profile from a ``rad_server`` / ``tacacs_server``.

    Folds a co-located RFC 3576 CoA server (matched by IP from ``coa_servers``,
    the aaa-profile's ``rfc3576_client[]``) onto the RADIUS server as
    ``radius-server-mode=AUTH_AND_COA`` + ``dynamic-authorization-enable`` (#322).
    """
    sd = auth_server
    is_tacacs = "tacacs_server_name" in sd or "tacacs_host" in sd

    if is_tacacs:
        name = str(sd.get("tacacs_server_name") or "")
        host = leaf(sd.get("tacacs_host"), "host")
        secret = leaf(sd.get("tacacs_key"), "key")
        body: dict[str, Any] = {"name": name, "type": "TACACS"}
        if host is not None:
            body["auth-server-address"] = str(host)
        if secret is not None:
            body["shared-secret-config"] = {"secret-type": "PLAIN_TEXT", "plaintext-value": str(secret)}
        for aos8_field, subkey, central_key, how in (
            ("tacacs_tcpport", "tcp-port", "auth-port", "int"),
            ("tacacs_timeout", "timeout", "timeout", "int"),
            ("tacacs_retransmit", "retransmit", "retransmit", "int"),
        ):
            val = leaf(sd.get(aos8_field), subkey)
            if val is not None:
                body[central_key] = _coerce(val, how)
    else:
        name = str(sd.get("rad_server_name") or "")
        host = leaf(sd.get("rad_host"), "host")
        secret = leaf(sd.get("rad_key"), "key")
        body = {"name": name, "type": "RADIUS"}
        if host is not None:
            body["auth-server-address"] = str(host)
        if secret is not None:
            body["shared-secret-config"] = {"secret-type": "PLAIN_TEXT", "plaintext-value": str(secret)}
        for aos8_field, subkey, central_key, how in (
            ("rad_authport", "authport", "auth-port", "int"),
            ("rad_acctport", "acctport", "acct-port", "int"),
            ("rad_timeout", "timeout", "timeout", "int"),
            ("rad_retransmit", "retransmit", "retransmit", "int"),
            ("rad_nasid", "nas-identifier", "nas-identifier", "str"),
            ("rad_nasip", "nas-ip", "nas-ip", "str"),
            ("rad_nasip6", "nas-ip6", "nas-ip6", "str"),
            ("radsec_port", "radsec-port", "radsec-port", "int"),
        ):
            val = leaf(sd.get(aos8_field), subkey)
            if val is not None:
                body[central_key] = _coerce(val, how)
        if _flag(sd, "radsec_enable"):
            body["enable-radsec"] = True
        if _coa_peer(host, coa_servers):
            body["radius-server-mode"] = "AUTH_AND_COA"
            body["dynamic-authorization-enable"] = True

    return CanonicalCentralProfile(kind="auth_server", profile_type="auth-servers", name=name, body=body)


# --------------------------------------------------------------------------- #
# server_group
# --------------------------------------------------------------------------- #
def aos8_read_server_group(server_group: dict[str, Any]) -> CanonicalCentralProfile:
    """Build the Central server-group from an AOS 8 ``server_group_prof`` record."""
    name = str(server_group.get("sg_name") or "")
    servers: list[dict[str, Any]] = []
    position = 1
    for member in server_group.get("auth_server") or []:
        if isinstance(member, dict) and member.get("name"):
            servers.append({"server-name": str(member["name"]), "position": position})
            position += 1
    body = {"name": name, "type": "RADIUS", "servers": servers}
    return CanonicalCentralProfile(kind="server_group", profile_type="server-groups", name=name, body=body)


# --------------------------------------------------------------------------- #
# dot1x_auth
# --------------------------------------------------------------------------- #
_DOT1X_SCALARS: list[ScalarSpec] = [
    ("reauth_period", "ra-period", "reauth-period", "int"),
    ("reauth_max_requests", "ramx-requests", "max-reauth", "int"),
    ("max_requests", "mx-requests", "eapol-max-requests", "int"),
    ("server_cert", "server-cert-name", "server-cert", "str"),
    ("ca_cert", "ca-cert-name", "ca-cert", "str"),
    ("framed_mtu", "fmtu", "framed-mtu", "int"),
    ("quiet_period", "qt-period", "quiet-period", "int"),
    ("heldstate_bypass_counter", "hs-counter", "heldstate-bypass", "int"),
    ("wep_key_size", "wk-size", "wep-key-size", "int"),
    ("wep_key_retries", "wk-retries", "wep-key-retries", "int"),
    ("tls_guest_role", "tg-role", "tls-guest-role", "str"),
    ("ukey_period", "ukr-period", "unicast-key-rotation-period", "int"),
    ("mkey_period", "mkr-period", "multicast-key-rotation-period", "int"),
    ("wpakey_period_ms", "wk-period", "wpa-key-period", "int"),
    ("wpa2key_delay", "wk-delay", "wpa2-key-delay", "int"),
    ("wpagkey_delay", "wgk-delay", "wpa-groupkey-delay", "int"),
    ("wpa_key_retries", "wpak-retries", "wpa-key-retries", "int"),
]
_DOT1X_FLAGS: list[FlagSpec] = [
    ("reauthentication", "reauth-enable"),
    ("tls_guest_access", "tls-guest-access"),
    ("enforce_suite_b_128", "enforce-suite-b-128"),
    ("enforce_suite_b_192", "enforce-suite-b-192"),
    ("validate_pmkid", "validate-pmkid"),
    ("eapol_logoff", "eapol-logoff"),
    ("dot1x_cert_cn_lookup", "cert-cn-lookup"),
    ("opp_key_caching", "opp-key-caching"),
    ("unicast_keyrotation", "unicast-keyrotation"),
    ("multicast_keyrotation", "multicast-keyrotation"),
    ("use_static_key", "use-static-key"),
    ("use_session_key", "use-session-key"),
    ("wpa_fast_handover", "wpa-fast-handover"),
]


def aos8_read_dot1x_auth(dot1x: dict[str, Any]) -> CanonicalCentralProfile:
    """Build the Central dot1x-auth profile from an AOS 8 ``dot1x_auth_profile``."""
    name = str(dot1x.get("profile-name") or "")
    body = _build_body(dot1x, name, _DOT1X_SCALARS, _DOT1X_FLAGS)
    return CanonicalCentralProfile(kind="dot1x_auth", profile_type="dot1xauth", name=name, body=body)


# --------------------------------------------------------------------------- #
# mac_auth
# --------------------------------------------------------------------------- #
_MAC_SCALARS: list[ScalarSpec] = [
    ("mac_reauth_period", "ra-period", "reauth-period", "int"),
    ("mba_maxf", "max-authentication-failures", "max-retries", "int"),
    ("mba_case", "mba_case_t", "case-type", "str"),
    ("mba_fmt", "mba_delimiter_t", "address-format", "str"),
]
_MAC_FLAGS: list[FlagSpec] = [
    ("mac_reauthentication", "reauth-enable"),
    ("mac_use_server_reauth_period", "use-server-reauth-period"),
]


def aos8_read_mac_auth(mac: dict[str, Any]) -> CanonicalCentralProfile:
    """Build the Central mac-auth profile from an AOS 8 ``mac_auth_profile``."""
    name = str(mac.get("profile-name") or "")
    body = _build_body(mac, name, _MAC_SCALARS, _MAC_FLAGS)
    return CanonicalCentralProfile(kind="mac_auth", profile_type="macauth", name=name, body=body)


# --------------------------------------------------------------------------- #
# captive_portal
# --------------------------------------------------------------------------- #
_CP_SCALARS: list[ScalarSpec] = [
    ("cp_default_guest_role", "default-guest-role", "default-guest-role", "str"),
    ("cp_default_role", "default-role", "default-role", "str"),
    ("cp_redirect_url", "redirect-url", "redirect-url", "str"),
    ("ip_addr_in_redir_url", "ip-addr-in-redirection-url", "ip-addr-in-redirection-url", "str"),
    ("cp_server_group", "server-group", "server-group", "str"),
    ("url_hash_key", "url-hash-key", "url-hash-key-value", "str"),
    ("cp_welcome_location", "welcome-page", "welcome-page", "str"),
    ("cp_min_delay", "minimum-delay", "logon-wait-min-delay", "int"),
    ("cp_max_delay", "maximum-delay", "logon-wait-max-delay", "int"),
    ("cp_load_thresh", "cpu-threshold", "logon-wait-cpu-threshold", "int"),
    ("cp_maxf", "max-authentication-failures", "max-authentication-failures", "int"),
    ("cp_redirect_pause", "redirect-pause", "redirect-pause", "int"),
    ("user_idle_timeout_cp", "seconds", "user-idle-timeout", "int"),
]
_CP_FLAGS: list[FlagSpec] = [
    ("apple_cna_bypass", "apple-cna-bypass"),
    ("ap_mac_in_redir_url", "ap-mac-in-redirection-url"),
    ("allow_guest", "guest-logon"),
    ("allow_user", "user-logon"),
    ("cp_welcome_location_enable", "enable-welcome-page"),
    ("logout_popup", "logout-popup-window"),
    ("show_aup", "show-acceptable-use-policy"),
    ("cp_show_fqdn", "show-fqdn"),
    ("single_session", "single-session"),
    ("switch_ip_in_redir_url", "switch-ip"),
    ("user_vlan_in_redir_url", "user-vlan-in-redirection-url"),
]
# AOS 8 captive_auth_t enum → Central auth-protocol enum (plain upper() mangles MSCHAPv2).
_AUTH_PROTOCOL = {"PAP": "PAP", "MSCHAPv2": "MSCHAPv2", "chap": "CHAP"}


def _names(arr: Any, subkey: str) -> list[str] | None:
    if not isinstance(arr, list):
        return None
    out = [str(i[subkey]) for i in arr if isinstance(i, dict) and i.get(subkey)]
    return out or None


def aos8_read_captive_portal(cp: dict[str, Any]) -> CanonicalCentralProfile:
    """Build the Central captive-portal profile from an AOS 8 ``cp_auth_profile``."""
    name = str(cp.get("profile-name") or "")
    body = _build_body(cp, name, _CP_SCALARS, _CP_FLAGS)

    deny = _names(cp.get("cp_black_list"), "black-list")
    if deny is not None:
        body["deny-list"] = deny
    allow = _names(cp.get("cp_white_list"), "white-list")
    if allow is not None:
        body["allow-list"] = allow

    # Inverted flag: AOS 8 protocol-http present → Central use-https=False.
    if _flag(cp, "cp_proto_http"):
        body["use-https"] = False

    auth = leaf(cp.get("authentication_method"), "captive_auth_t")
    if auth:
        body["auth-protocol"] = _AUTH_PROTOCOL.get(auth, str(auth).upper())

    return CanonicalCentralProfile(kind="captive_portal", profile_type="captive-portal", name=name, body=body)


# --------------------------------------------------------------------------- #
# aaa_profile (the keystone — references the chain by name)
# --------------------------------------------------------------------------- #
_AAA_SCALARS: list[ScalarSpec] = [
    ("rad_acct_sg", "server_group_name", "acct-server-group", "str"),
    ("max_ipv4_for_wireless", "max_ipv4_users", "max-ipv4-ip-wireless", "int"),
    ("user_idle_timeout_aaa", "seconds", "user-idle-timeout", "int"),
    ("udr_group", "udr_group", "user-derivation-rule", "str"),
]
_AAA_FLAGS: list[FlagSpec] = [
    ("enforce_dhcp", "enforce-dhcp"),
    ("enable_rad_interim_acct", "interim-accounting"),
    ("enable_roaming_rad_acct", "roam-accounting"),
    ("l2_auth_fail_through", "l2-auth-fail-through"),
    ("multiple_server_accounting", "multiple-server-accounting"),
    ("open_system_rad_acc", "open-system-accounting"),
    ("incl_acct_sess_id_in_access", "acct-session-id-in-access"),
    ("integrate_pan", "pan-integration"),
    ("wired_reauth_on_vlan_change", "reauth-wired-user-vlan-change"),
    ("username_from_dhcp_opt12", "username-from-dhcp-opt12"),
    ("wwroam", "wired-to-wireless-roam"),
    ("ageout_on_bridge", "ageout-bridge-user"),
    ("devtype_classification", "devtype-classification"),
    ("download_role", "download-role"),
]
# (aos8_field, subkey, central authentication.<key>)
_AAA_AUTHENTICATION: list[ScalarSpec] = [
    ("dot1x_auth_profile", "profile-name", "dot1x-auth", "str"),
    ("dot1x_default_role", "default-role", "dot1x-default-role", "str"),
    ("dot1x_server_group", "srv-group", "dot1xauth-server-group", "str"),
    ("mac_auth_profile", "profile-name", "mac-auth", "str"),
    ("mac_default_role", "default-role", "mac-default-role", "str"),
    ("mba_server_group", "srv-group", "macauth-server-group", "str"),
]


def aos8_read_aaa_profile(aaa: dict[str, Any]) -> CanonicalCentralProfile:
    """Build the Central aaa-profile from an AOS 8 ``aaa_prof`` record.

    Pre-builds the nested ``authentication`` (dot1x/mac profile + server-group +
    role references) and ``authorization`` (pre-auth-role) sub-objects.
    """
    name = str(aaa.get("profile-name") or "")
    body = _build_body(aaa, name, _AAA_SCALARS, _AAA_FLAGS)

    coa = [
        c["rfc3576_server"]
        for c in (aaa.get("rfc3576_client") or [])
        if isinstance(c, dict) and c.get("rfc3576_server")
    ]
    if coa:
        body["rfc3576-server-list"] = coa

    authentication: dict[str, Any] = {}
    for aos8_field, subkey, central_key, _how in _AAA_AUTHENTICATION:
        val = leaf(aaa.get(aos8_field), subkey)
        if val is not None:
            authentication[central_key] = val
    if authentication:
        body["authentication"] = authentication

    base_role = leaf(aaa.get("default_user_role"), "role")
    if base_role is not None:
        body["authorization"] = {"pre-auth-role": base_role}

    return CanonicalCentralProfile(kind="aaa_profile", profile_type="aaa-profile", name=name, body=body)
