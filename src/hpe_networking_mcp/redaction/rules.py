"""Tokenization rules — what to tokenize and as what kind.

The rules are pure data: dictionaries and frozensets keyed by JSON field
name. The walker (``walker.py``) calls ``classify_field()`` on each
``(field_name, value)`` it encounters to decide:

* **SKIP**: leave the value alone (default for unknown fields).
* **TOKENIZE_SECRET**: this is a credential; tokenize as one of the
  secret kinds (``PSK``, ``RADSEC``, ``SNMP_COMMUNITY``, etc.).
* **TOKENIZE_IDENTIFIER**: this is a customer-identifying value; tokenize
  as one of the identifier kinds (``SITE``, ``HOSTNAME``, ``EMAIL``,
  etc.). MACs are not in this set — they are *normalized* by the MAC
  module, not tokenized.
* **SCAN_FREE_TEXT**: descriptive text field that operators sometimes
  paste secrets/identifiers into; the walker runs the regex sweep over
  the value's contents.

Per the v2.3.0.10 design, MACs are never tokenized (just normalized) and
the public-IP allowlist exempts well-known DNS / NTP / loopback /
documentation IPs from tokenization.
"""

from __future__ import annotations

import re
from enum import StrEnum


class TokenKind(StrEnum):
    """The kinds of tokens issued by the tokenizer.

    The string value becomes the prefix in the rendered token form
    ``[[KIND:uuid]]`` — keep these short and ALL CAPS so the regex stays
    tight (``[A-Z_]+``).
    """

    # --- Secrets (Tier 1) ---
    PSK = "PSK"  # WPA2/WPA3/SAE pre-shared keys, passphrases, PPSKs
    RADSEC = "RADSEC"  # RADIUS / RadSec / TACACS+ shared secrets, EAP passwords
    SNMP_COMMUNITY = "SNMP"  # SNMPv1/v2c communities, SNMPv3 auth/priv passwords
    ADMIN_PASSWORD = "PASSWORD"  # nosec B105 — token-kind label, not a credential
    VPN_PSK = "VPNPSK"  # IPSec PSK, VPN PSK
    API_TOKEN = "APITOKEN"  # nosec B105 — token-kind label, not a credential
    CERT = "CERT"  # certificates (PEM blocks)
    PRIVATE_KEY = "KEY"  # private keys (PEM blocks), keytabs

    # --- Identifiers (Tier 2) ---
    ORG = "ORG"
    SITE = "SITE"
    DEVICE = "DEVICE"
    AP = "AP"
    SWITCH = "SWITCH"
    GATEWAY = "GATEWAY"
    WLAN = "WLAN"
    TEMPLATE = "TEMPLATE"
    POLICY = "POLICY"
    TENANT = "TENANT"
    WORKSPACE = "WORKSPACE"
    SUBSCRIPTION = "SUBSCRIPTION"
    CLIENT = "CLIENT"
    HOSTNAME = "HOSTNAME"
    SSID = "SSID"
    USER = "USER"
    EMAIL = "EMAIL"
    PHONE = "PHONE"
    SERIAL = "SERIAL"
    IMEI = "IMEI"
    IMSI = "IMSI"
    ICCID = "ICCID"
    IP = "IP"
    GEO = "GEO"  # latitude/longitude/address fields
    NAME = "NAME"  # generic operator-assigned name (vlan_name, subnet_name, room, etc.)


class FieldClassification(StrEnum):
    """The walker's decision for a given (field_name, value)."""

    SKIP = "skip"
    TOKENIZE_SECRET = "tokenize_secret"  # nosec B105 — enum classification label, not a credential
    TOKENIZE_IDENTIFIER = "tokenize_identifier"
    SCAN_FREE_TEXT = "scan_free_text"


# ---------------------------------------------------------------------------
# Tier 1 — Secret field names (case-insensitive exact match)
# ---------------------------------------------------------------------------
# Maps lowercase field name -> TokenKind. Field names are matched at any
# nesting depth, regardless of parent context. The walker also runs a
# value-shape heuristic on the generic catch-alls (``password``, ``secret``,
# ``token``, ``key``) to avoid tokenizing template-style placeholder values
# like ``{"key": "ssid"}``.

SECRET_FIELD_NAMES: dict[str, TokenKind] = {
    # WPA / SAE / WEP keys
    "psk": TokenKind.PSK,
    "passphrase": TokenKind.PSK,
    "wpa_passphrase": TokenKind.PSK,
    "wpa2_passphrase": TokenKind.PSK,
    "wpa3_psk": TokenKind.PSK,
    "sae_password": TokenKind.PSK,
    "sae_pwd": TokenKind.PSK,
    "ppsk": TokenKind.PSK,
    "wep_key": TokenKind.PSK,
    "wep_passphrase": TokenKind.PSK,
    # RADIUS / RadSec / 802.1X
    "shared_secret": TokenKind.RADSEC,
    "radius_secret": TokenKind.RADSEC,
    "radsec_secret": TokenKind.RADSEC,
    "eap_password": TokenKind.RADSEC,
    "inner_password": TokenKind.RADSEC,
    # SNMP
    "community": TokenKind.SNMP_COMMUNITY,
    "community_string": TokenKind.SNMP_COMMUNITY,
    "auth_password": TokenKind.SNMP_COMMUNITY,
    "priv_password": TokenKind.SNMP_COMMUNITY,
    "snmp_v3_auth_pass": TokenKind.SNMP_COMMUNITY,
    "snmp_v3_priv_pass": TokenKind.SNMP_COMMUNITY,
    # Admin / management
    "admin_password": TokenKind.ADMIN_PASSWORD,
    "manager_password": TokenKind.ADMIN_PASSWORD,
    "support_user_password": TokenKind.ADMIN_PASSWORD,
    "enable_password": TokenKind.ADMIN_PASSWORD,
    "enable_secret": TokenKind.ADMIN_PASSWORD,
    "cli_password": TokenKind.ADMIN_PASSWORD,
    # VPN / IPSec
    "pre_shared_key": TokenKind.VPN_PSK,
    "ipsec_psk": TokenKind.VPN_PSK,
    "vpn_psk": TokenKind.VPN_PSK,
    # API tokens / OAuth in configs
    "api_token": TokenKind.API_TOKEN,
    "apitoken": TokenKind.API_TOKEN,
    "api_key": TokenKind.API_TOKEN,
    "apikey": TokenKind.API_TOKEN,
    "client_secret": TokenKind.API_TOKEN,
    "bearer_token": TokenKind.API_TOKEN,
    "access_token": TokenKind.API_TOKEN,
    "refresh_token": TokenKind.API_TOKEN,
    "webhook_secret": TokenKind.API_TOKEN,
    "webhook_token": TokenKind.API_TOKEN,
    # Certificates & keys (also content-fingerprint detected via PEM regex)
    "private_key": TokenKind.PRIVATE_KEY,
    "privkey": TokenKind.PRIVATE_KEY,
    "kerberos_keytab": TokenKind.PRIVATE_KEY,
    "keytab": TokenKind.PRIVATE_KEY,
    "cert": TokenKind.CERT,
    "certificate": TokenKind.CERT,
    "client_cert": TokenKind.CERT,
    "server_cert": TokenKind.CERT,
    "ca_cert": TokenKind.CERT,
    "chain": TokenKind.CERT,
    "pkcs12": TokenKind.CERT,
    "p12_data": TokenKind.CERT,
    "pem": TokenKind.CERT,
}

# Generic credential-shaped field names. Only tokenized when the value's
# *shape* looks credential-like (length >= 8, mixed character classes).
# Avoids false positives like ``{"key": "ssid"}`` where ``key`` is a
# template field name, not a credential.
GENERIC_CREDENTIAL_FIELD_NAMES: dict[str, TokenKind] = {
    "password": TokenKind.ADMIN_PASSWORD,
    "pwd": TokenKind.ADMIN_PASSWORD,
    "secret": TokenKind.RADSEC,  # most commonly a RADIUS/auth secret
    "token": TokenKind.API_TOKEN,
    "key": TokenKind.API_TOKEN,
}


# ---------------------------------------------------------------------------
# Tier 2 — Identifier field names
# ---------------------------------------------------------------------------

TOKENIZED_IDENTIFIER_FIELDS: dict[str, TokenKind] = {
    # Platform UUIDs
    "org_id": TokenKind.ORG,
    "msp_id": TokenKind.ORG,
    "site_id": TokenKind.SITE,
    "siteid": TokenKind.SITE,
    "device_id": TokenKind.DEVICE,
    "ap_id": TokenKind.AP,
    "switch_id": TokenKind.SWITCH,
    "gateway_id": TokenKind.GATEWAY,
    "mxedge_id": TokenKind.GATEWAY,
    "wlan_id": TokenKind.WLAN,
    "wxlan_id": TokenKind.WLAN,
    "wxtag_id": TokenKind.WLAN,
    "wxtunnel_id": TokenKind.WLAN,
    "wxrule_id": TokenKind.WLAN,
    "wxlan_tunnel_id": TokenKind.WLAN,
    "client_id": TokenKind.CLIENT,
    "mobile_id": TokenKind.CLIENT,
    "mac_id": TokenKind.CLIENT,
    "template_id": TokenKind.TEMPLATE,
    "assignment_id": TokenKind.TEMPLATE,
    "policy_id": TokenKind.POLICY,
    "psk_id": TokenKind.POLICY,
    "tenant_id": TokenKind.TENANT,
    "workspace_id": TokenKind.WORKSPACE,
    "subscription_id": TokenKind.SUBSCRIPTION,
    # Operator-assigned names
    "device_name": TokenKind.HOSTNAME,
    "ap_name": TokenKind.HOSTNAME,
    "hostname": TokenKind.HOSTNAME,
    "fqdn": TokenKind.HOSTNAME,
    "ssid": TokenKind.SSID,
    "essid": TokenKind.SSID,
    "site_name": TokenKind.NAME,
    "org_name": TokenKind.NAME,
    "vlan_name": TokenKind.NAME,
    "subnet_name": TokenKind.NAME,
    # User-identifying
    "username": TokenKind.USER,
    "user": TokenKind.USER,
    "login": TokenKind.USER,
    "email": TokenKind.EMAIL,
    "first_name": TokenKind.USER,
    "last_name": TokenKind.USER,
    "full_name": TokenKind.USER,
    "display_name": TokenKind.USER,
    "phone": TokenKind.PHONE,
    "phone_number": TokenKind.PHONE,
    "mobile": TokenKind.PHONE,
    # Hardware
    "serial": TokenKind.SERIAL,
    "serial_number": TokenKind.SERIAL,
    "sn": TokenKind.SERIAL,
    "imei": TokenKind.IMEI,
    "imsi": TokenKind.IMSI,
    "iccid": TokenKind.ICCID,
    # Geographic
    "latitude": TokenKind.GEO,
    "longitude": TokenKind.GEO,
    "address": TokenKind.GEO,
    "street": TokenKind.GEO,
    "city": TokenKind.GEO,
    "state": TokenKind.GEO,
    "zip": TokenKind.GEO,
    "postal_code": TokenKind.GEO,
    "country": TokenKind.GEO,
    "room": TokenKind.GEO,
    "floor": TokenKind.GEO,
    "building": TokenKind.GEO,
}

# Field names where ``name`` should be tokenized as HOSTNAME — only when
# the parent object looks like a device (has device-shaped sibling fields).
# The walker checks for these sibling hints before tokenizing a bare ``name``
# field, since ``name`` is an enormously common field that we'd otherwise
# tokenize too aggressively.
DEVICE_CONTEXT_HINTS: frozenset[str] = frozenset(
    {
        "mac",
        "model",
        "serial",
        "device_type",
        "hw_rev",
        "firmware",
    }
)


# ---------------------------------------------------------------------------
# Tier 3 — Free-text fields scanned for embedded secrets/identifiers
# ---------------------------------------------------------------------------

FREE_TEXT_FIELD_NAMES: frozenset[str] = frozenset(
    {
        "description",
        "notes",
        "comment",
        "comments",
        "remarks",
        "details",
    }
)


# ---------------------------------------------------------------------------
# Public IP allowlist — well-known infrastructure IPs preserved verbatim
# ---------------------------------------------------------------------------

PUBLIC_IP_ALLOWLIST: frozenset[str] = frozenset(
    {
        # Loopback / unspecified
        "127.0.0.1",
        "0.0.0.0",
        "::1",
        "::",
        # Google Public DNS
        "8.8.8.8",
        "8.8.4.4",
        "2001:4860:4860::8888",
        "2001:4860:4860::8844",
        # Cloudflare DNS
        "1.1.1.1",
        "1.0.0.1",
        "2606:4700:4700::1111",
        "2606:4700:4700::1001",
        # Quad9
        "9.9.9.9",
        "149.112.112.112",
        # OpenDNS
        "208.67.222.222",
        "208.67.220.220",
        # RFC 5737 documentation
        "192.0.2.0",
        "198.51.100.0",
        "203.0.113.0",
    }
)

# Documentation / reserved address ranges that are also preserved.
# These are CIDR-checked rather than equality-checked.
PUBLIC_IP_ALLOWLIST_RANGES: tuple[str, ...] = (
    "192.0.2.0/24",  # RFC 5737 TEST-NET-1
    "198.51.100.0/24",  # RFC 5737 TEST-NET-2
    "203.0.113.0/24",  # RFC 5737 TEST-NET-3
    "224.0.0.0/4",  # IPv4 multicast (mDNS, link-local)
    "ff00::/8",  # IPv6 multicast (NDP etc.)
    "fe80::/10",  # IPv6 link-local
)


# ---------------------------------------------------------------------------
# Regex patterns (compiled once at import)
# ---------------------------------------------------------------------------

# IPv4 address (does not validate octet ranges; that's handled by the
# ipaddress module on match candidates).
IPV4_RE: re.Pattern[str] = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}(?:/\d{1,2})?\b")

# IPv6 address — conservative; matches typical full + compressed forms.
# Combined with ipaddress.ip_address() validation in the walker to weed
# out false positives. Includes optional CIDR.
IPV6_RE: re.Pattern[str] = re.compile(
    r"\b("
    r"(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}"  # full form
    r"|(?:[0-9a-fA-F]{1,4}:)+:(?:[0-9a-fA-F]{1,4}:?)+"  # compressed
    r"|::(?:[0-9a-fA-F]{1,4}:?)+"  # leading ::
    r")(?:/\d{1,3})?\b"
)

# Email
EMAIL_RE: re.Pattern[str] = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")

# PEM block (certificate or key) — match the entire block including markers.
# Used for content-fingerprint detection so PEM data in unexpected fields
# still gets tokenized.
PEM_BLOCK_RE: re.Pattern[str] = re.compile(r"-----BEGIN [A-Z0-9 ]+-----[\s\S]+?-----END [A-Z0-9 ]+-----")

# UUID (canonical 8-4-4-4-12 hex form, lowercase or uppercase).
UUID_RE: re.Pattern[str] = re.compile(
    r"\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-"
    r"[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\b"
)

# Token form: ``[[KIND:uuid]]`` — kind is uppercase letters/underscores,
# UUID is canonical.
TOKEN_RE: re.Pattern[str] = re.compile(
    r"\[\[([A-Z_]+):"
    r"([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})"
    r"\]\]"
)


# ---------------------------------------------------------------------------
# Value-shape heuristics
# ---------------------------------------------------------------------------


def looks_like_credential(value: str) -> bool:
    """Heuristic: does ``value`` look like a credential rather than an enum?

    Used as a guard on the generic catch-all field names (``password``,
    ``secret``, ``token``, ``key``) to suppress tokenization of
    template-style placeholder values like ``{"key": "ssid"}`` or
    ``{"secret": "auto"}``.

    Returns True when:
    * length >= 8, AND
    * contains at least two of {lowercase, uppercase, digit, special}, OR
    * contains at least one non-alphanumeric character

    Length-only check is too lax (an 8-char enum like ``disabled`` slips
    through); character-class diversity is the discriminator.
    """
    if not isinstance(value, str) or len(value) < 8:
        return False
    has_lower = any(c.islower() for c in value)
    has_upper = any(c.isupper() for c in value)
    has_digit = any(c.isdigit() for c in value)
    has_special = any(not c.isalnum() and not c.isspace() for c in value)
    classes = sum((has_lower, has_upper, has_digit, has_special))
    return classes >= 2 or has_special


def is_known_enum_value(value: str) -> bool:
    """Quick sanity check: is ``value`` an obvious enum/keyword?

    Returns True for short uppercase tokens or known network-config
    keywords. Used to short-circuit ``looks_like_credential`` for very
    short obvious-non-secret strings.
    """
    if not isinstance(value, str):
        return False
    lowered = value.lower()
    return lowered in _COMMON_ENUM_VALUES


_COMMON_ENUM_VALUES: frozenset[str] = frozenset(
    {
        "auto",
        "manual",
        "none",
        "default",
        "enabled",
        "disabled",
        "true",
        "false",
        "any",
        "all",
        "open",
        "closed",
        "wpa2",
        "wpa3",
        "psk",
        "eap",
        "sae",
        "online",
        "offline",
        "connected",
        "disconnected",
    }
)


# ---------------------------------------------------------------------------
# Field classification API
# ---------------------------------------------------------------------------


def classify_field(
    field_name: str,
    value: object,
    *,
    parent_keys: frozenset[str] | None = None,
) -> tuple[FieldClassification, TokenKind | None]:
    """Decide how the walker should handle this (field, value).

    Args:
        field_name: The JSON key. Compared case-insensitively.
        value: The value at that key — used for shape heuristics on
            generic credential field names.
        parent_keys: The set of sibling keys in the same dict, used to
            disambiguate ambiguous fields (``name`` is a hostname only
            when the parent object also has device-shaped fields).

    Returns:
        ``(classification, kind)`` where ``kind`` is None for SKIP/SCAN
        results.
    """
    if not isinstance(field_name, str):
        return FieldClassification.SKIP, None
    name = field_name.lower()

    # Exact-match secret fields
    if name in SECRET_FIELD_NAMES:
        return FieldClassification.TOKENIZE_SECRET, SECRET_FIELD_NAMES[name]

    # Generic credential field names — only tokenize when value passes shape check
    if name in GENERIC_CREDENTIAL_FIELD_NAMES:
        if isinstance(value, str) and looks_like_credential(value) and not is_known_enum_value(value):
            return (
                FieldClassification.TOKENIZE_SECRET,
                GENERIC_CREDENTIAL_FIELD_NAMES[name],
            )
        return FieldClassification.SKIP, None

    # Identifier fields
    if name in TOKENIZED_IDENTIFIER_FIELDS:
        return (
            FieldClassification.TOKENIZE_IDENTIFIER,
            TOKENIZED_IDENTIFIER_FIELDS[name],
        )

    # Bare ``name`` becomes HOSTNAME only when the parent object looks like a device
    if name == "name" and parent_keys and (parent_keys & DEVICE_CONTEXT_HINTS):
        return FieldClassification.TOKENIZE_IDENTIFIER, TokenKind.HOSTNAME

    # Free-text fields
    if name in FREE_TEXT_FIELD_NAMES:
        return FieldClassification.SCAN_FREE_TEXT, None

    return FieldClassification.SKIP, None
