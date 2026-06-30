"""Tokenization rules — what to tokenize and as what kind.

The rules are pure data: dictionaries and frozensets keyed by JSON field
name. The walker (``walker.py``) calls ``classify_field()`` on each
``(field_name, value)`` it encounters to decide:

* **SKIP**: leave the value alone (default for unknown fields).
* **TOKENIZE_SECRET**: this is a credential; tokenize as one of the
  secret kinds (``PSK``, ``RAD``, ``TACACS``, ``SNMP_COMMUNITY``, etc.).
* **TOKENIZE_IDENTIFIER**: this is a customer-identifying value;
  tokenize as one of the identifier kinds (``HOSTNAME``, ``EMAIL``,
  ``USER``, ``SERIAL``, ``IP``, etc.).
* **SCAN_FREE_TEXT**: descriptive text field that operators sometimes
  paste secrets/identifiers into; the walker runs the regex sweep over
  the value's contents.

The "don't tokenize" carve-outs (refined through v2.3.1.2):

* **MACs** — never tokenized, just normalized to ``aa:bb:cc:dd:ee:ff``.
  Observable to anyone in radio range.
* **SSIDs / ESSIDs** — never tokenized. Broadcast in beacon frames.
* **Platform UUIDs** (``org_id``, ``site_id``, ``device_id``,
  ``template_id``, etc.) — never tokenized. Already-opaque random
  identifiers; replacing one UUID with another adds no privacy and
  just adds context-window noise + AI confusion.
* **Geographic fields** (``address``, ``city``, ``state``, ``zip``,
  ``latitude``, ``longitude``, ``room``, ``building``, ...) — never
  tokenized. Business addresses are typically published on the
  company's website.
* **IP addresses** — never tokenized (refined in v2.3.1.2). Internal
  subnet topology is generally known to anyone on-network; tokenizing
  hurts audit utility (CIDR analysis, route checks, IP-block sanity)
  more than it adds privacy.

The "value-shape detections that fire regardless of field name"
(refined in v2.3.1.2):

* **Emails** — applied to every string value, not just free-text
  fields. Catches emails embedded in PSK ``name`` fields, ``username``
  values, etc.
* **AWS-signed URL credential markers** (``X-Amz-Security-Token``,
  ``X-Amz-Credential``, ``X-Amz-Signature``) — any value containing
  one of these strings is a temporary AWS credential and gets
  tokenized whole as ``APITOKEN``.
* **PEM blocks** — anywhere they appear in free-text fields.
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
    RAD = "RAD"  # RADIUS / RadSec shared secrets, EAP-tunneled passwords (issue #277)
    TACACS = "TACACS"  # TACACS+ shared secrets and TACACS+-tunneled passwords (issue #277)
    COA = "COA"  # CoA / RFC-3576 dynamic-authorization endpoints + shared secrets
    SNMP_COMMUNITY = "SNMP"  # SNMPv1/v2c communities, SNMPv3 auth/priv passwords
    ADMIN_PASSWORD = "PASSWORD"  # nosec B105 — token-kind label, not a credential
    VPN_PSK = "VPNPSK"  # IPSec PSK, VPN PSK
    API_TOKEN = "APITOKEN"  # nosec B105 — token-kind label, not a credential
    CERT = "CERT"  # certificates (PEM blocks)
    PRIVATE_KEY = "KEY"  # private keys (PEM blocks), keytabs

    # --- Identifiers (Tier 2) ---
    # Platform UUIDs (org_id, site_id, device_id, ...) are NOT tokenized.
    # Per the v2.3.1.1 design discussion, replacing an already-opaque UUID
    # with another opaque UUID adds no privacy and just adds noise. Same
    # for SSIDs (broadcast in beacons) and physical addresses (typically
    # public on company web pages).
    HOSTNAME = "HOSTNAME"
    USER = "USER"
    EMAIL = "EMAIL"
    PHONE = "PHONE"
    SERIAL = "SERIAL"
    IMEI = "IMEI"
    IMSI = "IMSI"
    ICCID = "ICCID"


class FieldClassification(StrEnum):
    """The walker's decision for a given (field_name, value)."""

    SKIP = "skip"
    TOKENIZE_SECRET = "tokenize_secret"  # nosec B105 — enum classification label, not a credential
    TOKENIZE_IDENTIFIER = "tokenize_identifier"
    SCAN_FREE_TEXT = "scan_free_text"
    # Source-platform-masked secret (e.g. AOS 8's "********"). The walker
    # rewrites these to the MASKED_SECRET_PLACEHOLDER directive — never a
    # token. See issue #276.
    MASKED_SECRET = "masked_secret"  # nosec B105 — enum classification label, not a credential


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
    "vrrp_passphrase": TokenKind.PSK,  # AOS 8 cluster_prof.vrrp_info shared key (issue #277)
    "wpa2_passphrase": TokenKind.PSK,
    "wpa3_psk": TokenKind.PSK,
    "sae_password": TokenKind.PSK,
    "sae_pwd": TokenKind.PSK,
    "ppsk": TokenKind.PSK,
    "wep_key": TokenKind.PSK,
    "wep_passphrase": TokenKind.PSK,
    # RADIUS / RadSec / 802.1X / CoA (RFC-3576).
    # CoA is a RADIUS extension — RFC-3576 / RFC-5176 dynamic-authorization
    # reuses the RADIUS shared secret on the same server. Joining ``coa_secret``
    # to the RAD family means the combined CoA + RADIUS migration tool (#322)
    # can emit the same plaintext in ``radius_secret`` and ``coa_secret``
    # fields and the keymap will hand back a single ``[[RAD:uuid]]`` token
    # for both (#321). CoA endpoint IPs / server names stay TokenKind.COA
    # (identifiers stay distinct per kind).
    "shared_secret": TokenKind.RAD,
    "radius_secret": TokenKind.RAD,
    "radsec_secret": TokenKind.RAD,
    "eap_password": TokenKind.RAD,
    "inner_password": TokenKind.RAD,
    "coa_secret": TokenKind.RAD,  # combined CoA+RADIUS tool field (#321 / #322)
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
    "secret": TokenKind.RAD,  # most commonly a RADIUS/auth secret
    "token": TokenKind.API_TOKEN,
    "key": TokenKind.API_TOKEN,
}


# ---------------------------------------------------------------------------
# Tier 2 — Identifier field names
# ---------------------------------------------------------------------------

TOKENIZED_IDENTIFIER_FIELDS: dict[str, TokenKind] = {
    # Operator-assigned names — strings that reveal customer infrastructure
    # naming patterns. Hostnames / FQDNs / device names go through DNS, but
    # the threat model is "don't ship customer names to the AI provider."
    # SSIDs and ESSIDs are NOT tokenized — they are broadcast in beacon
    # frames, observable to anyone in radio range.
    "device_name": TokenKind.HOSTNAME,
    "ap_name": TokenKind.HOSTNAME,
    "hostname": TokenKind.HOSTNAME,
    "host_name": TokenKind.HOSTNAME,  # AOS 8 client tables use "Host Name"
    # AOS 8 AAA-server detail (after transposed-table flatten); RADIUS/TACACS/LDAP
    # server IP/FQDN. Carve-out from the v2.3.1.2 "internal IPs not tokenized"
    # rule — AAA infrastructure is auth-fabric-critical (issue #235).
    "host": TokenKind.HOSTNAME,
    "controller_name": TokenKind.HOSTNAME,  # AOS 8 controller / MM identifier
    "switch_name": TokenKind.HOSTNAME,  # AOS 8 / Central switch identifier
    "fqdn": TokenKind.HOSTNAME,
    # NOTE: ``site_name``, ``org_name``, ``vlan_name``, and ``subnet_name``
    # are intentionally absent (v3.0.1.12 privacy-model refinement).
    # ``org_name`` and ``site_name`` are typically findable on the company's
    # public website or partner directories — tokenizing them buys little
    # privacy while costing audit utility. ``vlan_name`` and ``subnet_name``
    # are schema labels describing network architecture, not people; they
    # rarely encode customer-identifying information beyond what
    # ``scope_name``/``device_group_name`` already carry, both of which we
    # also pass through cleartext per the v2.3.1.3 design.
    # User-identifying
    "username": TokenKind.USER,
    "user": TokenKind.USER,
    "user_name": TokenKind.USER,  # Central uses snake_case alongside camelCase userName
    "login": TokenKind.USER,
    "email": TokenKind.EMAIL,
    "first_name": TokenKind.USER,
    "last_name": TokenKind.USER,
    "full_name": TokenKind.USER,
    "display_name": TokenKind.USER,
    "updated_by": TokenKind.USER,  # Central audit logs: who modified config
    "created_by": TokenKind.USER,  # Central audit logs: who created
    "phone": TokenKind.PHONE,
    "phone_number": TokenKind.PHONE,
    "mobile": TokenKind.PHONE,
    # Hardware identifiers — tie back to purchase records
    "serial": TokenKind.SERIAL,
    "serial_number": TokenKind.SERIAL,
    "serialnumber": TokenKind.SERIAL,  # GreenLake camelCase ``serialNumber`` (normalizer lowercases, no camel split)
    "sn": TokenKind.SERIAL,
    "imei": TokenKind.IMEI,
    "imsi": TokenKind.IMSI,
    "iccid": TokenKind.ICCID,
    # NOTE: platform UUID *_id fields (org_id, site_id, device_id,
    # template_id, scope_id, ...) are intentionally absent — they are
    # already opaque random UUIDs in Mist's and Central's APIs; replacing
    # one UUID with another adds no privacy. Geographic fields (address,
    # city, state, zip, latitude, longitude, etc.) are also absent —
    # addresses for business sites are typically findable on the company's
    # website. Central-specific organizational structures (device_group_name,
    # scope_name) are also absent — they describe network architecture
    # rather than people, and audit utility benefits from cleartext.
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
        "version",  # AOS 8 controller / switch records use ``Version``
        "release_type",  # Aruba-specific (LSR / SSR / UNCLASSIFIED) — strong device-shape signal
    }
)


# ---------------------------------------------------------------------------
# Tier 1.5 — Structural-context secret rules (parent_field_name + child)
# ---------------------------------------------------------------------------
# Some platforms wrap secrets under a parent dict where the *child* field
# name is too generic to tokenize unconditionally (e.g. ``key`` is also
# used in template references like ``{"key": "ssid"}``). The shape-check
# heuristic guards against false positives, but it leaks short single-class
# values like ``{"rad_key": {"key": "protocol"}}`` — verified live against
# AOS 8 in issue #277.
#
# These rules pair the *wrapping* field name with the child field name so
# tokenization can fire unconditionally when the wrapping context strongly
# implies the field is a credential.

STRUCTURAL_SECRET_CONTEXTS: dict[tuple[str, str], TokenKind] = {
    # AOS 8 RADIUS shared secret (verified live in issue #277).
    ("rad_key", "key"): TokenKind.RAD,
    # AOS 8 TACACS+ shared secret — same wrapper shape (Aruba schema family).
    ("tacacs_key", "key"): TokenKind.TACACS,
    # Mist coa_servers: list under "coa_servers" with each element
    # {"ip": "...", "port": 3799, "secret": "...", "enabled": True}. The
    # CoA shared secret is auth-fabric-critical — tokenize unconditionally.
    # See schemas_data.py "coa_servers" entry (v3.0.1.12).
    #
    # Issue #321: realigned from TokenKind.COA → TokenKind.RAD so that
    # plaintexts coming through ``radius_secret`` / ``coa_secret`` /
    # ``coa_servers[].secret`` all dedupe to a single ``[[RAD:uuid]]`` token
    # via the existing keymap. CoA is a RADIUS extension and the secret is
    # frequently reused on co-located RADIUS/CoA servers; one token across
    # forms is what the migration tooling needs.
    ("coa_servers", "secret"): TokenKind.RAD,
}


# ---------------------------------------------------------------------------
# Tier 1.6 — Structural-context identifier rules (parent_field_name + child)
# ---------------------------------------------------------------------------
# Same idea as STRUCTURAL_SECRET_CONTEXTS, but for non-credential identifiers.
# Some platforms wrap identifiers under a parent dict + list shape where the
# *child* field name is too generic to tokenize unconditionally (e.g. ``name``
# is also used for endpoint paths, configuration keys, etc.). The wrapping
# context strongly implies the child holds a sensitive identifier — so pair
# them and tokenize unconditionally.
#
# Concrete motivation (v3.0.1.12): CoA / RFC-3576 dynamic-authorization
# servers carry the auth-fabric secret + endpoint IP/FQDN under generic
# field names (``Name``, ``ip``, ``secret``) inside a parent list. They
# would otherwise slip through cleartext because we explicitly *don't*
# tokenize bare IPs and there's no top-level ``ip`` / ``name`` rule.

STRUCTURAL_IDENTIFIER_CONTEXTS: dict[tuple[str, str], TokenKind] = {
    # AOS 8 RFC-3576 / CoA server list. Live verified via
    # ``show aaa rfc-3576-server``:
    #   {"RFC 3576 Server List": [{"Name": "192.168.20.70", ...}, ...]}
    # Walker normalizes "RFC 3576 Server List" → "rfc_3576_server_list"
    # and "Name" → "name", so the pair below matches.
    ("rfc_3576_server_list", "name"): TokenKind.COA,
    # Mist coa_servers: list under "coa_servers" with each element
    # {"ip": "...", "port": 3799, "secret": "...", "enabled": True}.
    # Tokenize the endpoint IP so CoA infrastructure topology doesn't leak.
    ("coa_servers", "ip"): TokenKind.COA,
}


# ---------------------------------------------------------------------------
# Tier 1.7 — Wrapper-key patterns (dict keys with embedded sensitive values)
# ---------------------------------------------------------------------------
# Some platforms surface single-record detail blocks under a wrapper dict
# key that embeds the record identifier (e.g. AOS 8's
# ``show aaa rfc-3576-server <ip>`` returns ``{"RFC 3576 Server <ip>": [...]}``).
# The structural-context rules only consult NORMALIZED field names, so the
# original key string carrying the IP still surfaces to the AI verbatim.
#
# Each pattern has ONE regex capture group identifying the variable suffix
# to tokenize. The walker rewrites the key by tokenizing the captured
# substring in place; the rewritten key form is ``"<prefix> [[KIND:uuid]]"``.
# Round-trippable via the keymap on inbound arguments (the detokenize walk
# is extended to walk keys, not just values).
#
# Token-kind alignment matters: when the same IP/identifier also appears
# under a list-form structural rule (e.g. ``rfc_3576_server_list[].name``
# tokenizes as COA), the pattern here MUST use the same kind so the
# keymap deduplicates to a single token across both shapes (issue #319).

WRAPPER_KEY_PATTERNS: list[tuple[re.Pattern[str], TokenKind]] = [
    # AOS 8 single rfc-3576-server detail wrapper (issue #319).
    # ``show aaa rfc-3576-server <name>`` → ``{"RFC 3576 Server <name>": [...]}``
    # where ``<name>`` is typically the server IP (matches the ``Name`` field
    # in the list form). Same TokenKind.COA as the list-form rule so both
    # shapes deduplicate to a single token per server.
    #
    # Negative lookahead ``(?!List$)`` excludes the list-form wrapper
    # (``"RFC 3576 Server List"`` itself) — that wrapper is handled by the
    # ``rfc_3576_server_list`` structural rule on the list ELEMENTS, not
    # the wrapper key. ``\S+`` keeps server names to a single token (AOS 8
    # rejects names with spaces at config time).
    (re.compile(r"^RFC 3576 Server (?!List$)(\S+)$"), TokenKind.COA),
]


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
        # Raw device CLI output blob from show-command tools
        # (``central_show_commands`` and AOS 8 equivalents return
        # ``results[].output`` holding a ``show run`` / ``show ...`` dump).
        # Without this the blob classifies SKIP and only the universal scan
        # (emails / AWS-signed URLs) runs over it, so PEM cert/key blocks and
        # MACs embedded in CLI text pass through unswept (issue #411). As a
        # free-text field it now gets the full ``_scan_free_text`` sweep
        # (PEM → email → MAC normalize). Note: field-name-keyed secrets
        # (PSKs, shared secrets) have no value-shape regex and are not
        # detectable inside an opaque CLI blob — that requires a dedicated
        # CLI-grammar sweep and stays out of scope here.
        "output",
    }
)


# ---------------------------------------------------------------------------
# Regex patterns (compiled once at import)
# ---------------------------------------------------------------------------

# Email — applied to every string value as part of the universal scan
# (v2.3.1.2), not just free-text fields. Catches emails embedded in
# PSK ``name`` fields, ``username`` values, etc.
EMAIL_RE: re.Pattern[str] = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")

# PEM block (certificate or key) — match the entire block including markers.
# Used for content-fingerprint detection so PEM data in unexpected fields
# still gets tokenized.
PEM_BLOCK_RE: re.Pattern[str] = re.compile(r"-----BEGIN [A-Z0-9 ]+-----[\s\S]+?-----END [A-Z0-9 ]+-----")

# AWS Signature v4 pre-signed URL credential markers (v2.3.1.2). Any
# string value containing one of these is a temporary AWS credential —
# tokenize the whole value as APITOKEN. Mist embeds these in
# ``portal_template_url`` and similar fields to let operators preview
# captive-portal pages directly from S3 without proxying through Mist.
# The AI doesn't need to see them.
AWS_SIGNED_URL_RE: re.Pattern[str] = re.compile(
    r"X-Amz-(Security-Token|Credential|Signature)",
    re.IGNORECASE,
)

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


def is_masked_placeholder(value: str) -> bool:
    """Return True if ``value`` is a source-platform-side masked placeholder.

    AOS 8 (and similar systems) returns shared secrets, passwords, and other
    sensitive fields as runs of asterisks (``"********"``) rather than the
    cleartext value. The real secret never leaves the source platform.

    Such placeholders must NEVER be tokenized: a tokenized placeholder
    creates a *dangerous illusion* — the AI sees ``[[APITOKEN:uuid]]`` and
    believes it has a real tokenized secret it can pass to a write tool.
    The detokenize round-trip restores only the placeholder ``"********"``,
    which downstream platforms accept as a literal value. The result is a
    silent production failure (RADIUS auth breaks the next time a client
    tries to associate) rather than the loud failure of "AI can't get the
    secret, must ask operator".

    Returns True for all-asterisk strings of length 4 or more. Other
    common masked patterns (``<hidden>``, ``[REDACTED]``, etc.) can be
    added as they surface.

    See [issue #235](https://github.com/nowireless4u/hpe-networking-mcp/issues/235)
    for the AOS 8 ``Key: "********"`` case, and
    [issue #276](https://github.com/nowireless4u/hpe-networking-mcp/issues/276)
    for the rewrite-to-``REPLACE_ME`` behaviour the walker applies on top.
    """
    if not isinstance(value, str) or not value:
        return False
    return len(value) >= 4 and all(c == "*" for c in value)


# The literal directive the walker substitutes for a source-masked secret
# (e.g. AOS 8's "********"). It is NOT a token — it is an unambiguous
# "operator must set this" marker that flows through to migration output.
# "********" reads as "redacted/hidden" (ambiguous — is there a recoverable
# value behind it?); "REPLACE_ME" is an explicit directive. See issue #276.
MASKED_SECRET_PLACEHOLDER = "REPLACE_ME"  # nosec B105 — directive string, not a credential


def is_known_placeholder(value: str) -> bool:
    """Return True if ``value`` is the walker-emitted ``REPLACE_ME`` directive.

    Once the walker rewrites a source-masked ``********`` to ``REPLACE_ME``,
    that literal must never be tokenized — even when it lands in an
    exact-match secret field like ``coa_secret`` or ``shared_secret``.
    Tokenizing it would bury the "operator must set this" signal behind an
    opaque token. This guard also keeps the walk idempotent: a second walk
    sees ``REPLACE_ME`` (not ``********``), classifies it ``SKIP``, and
    leaves it alone.

    See [issue #276](https://github.com/nowireless4u/hpe-networking-mcp/issues/276).
    """
    return isinstance(value, str) and value == MASKED_SECRET_PLACEHOLDER


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


def _normalize_field_name(field_name: str) -> str:
    """Lower-case, hyphen→underscore, space→underscore.

    AOS 8 ``showcommand`` responses use space-separated headers
    (``"IP Address"``, ``"AP name"``, ``"Wired MAC Address"``) — treat
    those identically to snake_case. Mist/Central API responses don't
    ship space-separated keys, so this is a no-op for them. (Issue #235.)
    """
    return field_name.lower().replace("-", "_").replace(" ", "_")


def classify_field(
    field_name: str,
    value: object,
    *,
    parent_keys: frozenset[str] | None = None,
    parent_field_name: str | None = None,
) -> tuple[FieldClassification, TokenKind | None]:
    """Decide how the walker should handle this (field, value).

    Args:
        field_name: The JSON key. Compared case-insensitively, with
            hyphens normalized to underscores so that hyphenated API
            keys (e.g. Aruba Central's ``wpa-passphrase`` inside
            ``personal-security``) match the same ruleset entries as
            their snake_case equivalents (added in v2.3.1.3).
        value: The value at that key — used for shape heuristics on
            generic credential field names.
        parent_keys: The set of sibling keys in the same dict, used to
            disambiguate ambiguous fields (``name`` is a hostname only
            when the parent object also has device-shaped fields).
        parent_field_name: The wrapping key under which this dict was
            found — e.g. when classifying ``"key": "protocol"`` inside
            ``{"rad_key": {"key": "protocol"}}``, ``parent_field_name``
            is ``"rad_key"``. Used by the structural-context rules to
            tokenize generic field names unconditionally when the
            wrapping context strongly implies a credential (issue #277).

    Returns:
        ``(classification, kind)`` where ``kind`` is None for SKIP/SCAN
        results.
    """
    if not isinstance(field_name, str):
        return FieldClassification.SKIP, None
    name = _normalize_field_name(field_name)

    # The walker-emitted ``REPLACE_ME`` directive must never be re-classified
    # — not tokenized (even in an exact-match secret field), not re-rewritten.
    # Checked before everything else so it survives a second walk intact and
    # the loud operator signal is preserved (issue #276).
    if isinstance(value, str) and is_known_placeholder(value):
        return FieldClassification.SKIP, None

    # Source-platform-masked placeholders (e.g. AOS 8's ``"********"``) are
    # rewritten by the walker to the ``REPLACE_ME`` directive — never a token,
    # regardless of which rule path matches the field name. See
    # ``is_masked_placeholder`` for the rationale (a tokenized placeholder is
    # a dangerous illusion; the round-trip restores only the mask).
    if isinstance(value, str) and is_masked_placeholder(value):
        return FieldClassification.MASKED_SECRET, None

    # Structural-context rules — when a generic field name (e.g. ``key``) is
    # nested under a wrapping key that strongly implies a credential
    # (e.g. ``rad_key``), tokenize unconditionally. Bypasses the shape check
    # that would otherwise leak short single-class shared secrets like
    # ``"protocol"`` (issue #277). Same pattern for identifiers — when an
    # identifier-class field-name rule (e.g. ``vlan_name``) wraps a list of
    # dicts each carrying ``{"name": "..."}``, the identifier rule never
    # fires on the wrapper but the child ``name`` field needs tokenizing
    # (issue #289).
    if parent_field_name is not None:
        parent_normalized = _normalize_field_name(parent_field_name)
        struct_secret_kind = STRUCTURAL_SECRET_CONTEXTS.get((parent_normalized, name))
        if struct_secret_kind is not None:
            return FieldClassification.TOKENIZE_SECRET, struct_secret_kind
        struct_identifier_kind = STRUCTURAL_IDENTIFIER_CONTEXTS.get((parent_normalized, name))
        if struct_identifier_kind is not None:
            return FieldClassification.TOKENIZE_IDENTIFIER, struct_identifier_kind

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

    # Bare ``name`` becomes HOSTNAME only when the parent object looks
    # like a device — at least 2 device-shaped sibling fields (refined
    # in v2.3.1.2 from "any 1 hint" to fix wxtag false positives, where
    # the parent has a single ``mac`` field for client-MAC matching).
    # Parent keys come in raw and may carry AOS 8 spacing/casing
    # (e.g. ``"Model"``, ``"IP Address"``); normalize them before the
    # intersection so the heuristic fires on AOS 8 controller / AP
    # records (issue #235).
    if name == "name" and parent_keys:
        normalized_parents = frozenset(_normalize_field_name(k) for k in parent_keys if isinstance(k, str))
        if len(normalized_parents & DEVICE_CONTEXT_HINTS) >= 2:
            return FieldClassification.TOKENIZE_IDENTIFIER, TokenKind.HOSTNAME

    # Free-text fields
    if name in FREE_TEXT_FIELD_NAMES:
        return FieldClassification.SCAN_FREE_TEXT, None

    return FieldClassification.SKIP, None
