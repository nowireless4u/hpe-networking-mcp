"""Unit tests for the PII tokenization + MAC normalization layer."""

from __future__ import annotations

import json
import re

import pytest

from hpe_networking_mcp.redaction.mac_normalizer import (
    canonicalize_mac,
    is_mac_address,
    normalize_macs_in_value,
)
from hpe_networking_mcp.redaction.rules import (
    MASKED_SECRET_PLACEHOLDER,
    TOKEN_RE,
    FieldClassification,
    TokenKind,
    classify_field,
    is_known_enum_value,
    is_known_placeholder,
    is_masked_placeholder,
    looks_like_credential,
)
from hpe_networking_mcp.redaction.token_store import (
    SessionKeymap,
    TokenStore,
    allocate_token,
)
from hpe_networking_mcp.redaction.tokenizer import Tokenizer, detokenize_string
from hpe_networking_mcp.redaction.walker import (
    detokenize_arguments,
    tokenize_response,
)

UUID_PART = r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"


# ---------------------------------------------------------------------------
# MAC normalization
# ---------------------------------------------------------------------------


class TestMacNormalization:
    @pytest.mark.parametrize(
        "value,expected",
        [
            ("aa:bb:cc:dd:ee:ff", "aa:bb:cc:dd:ee:ff"),
            ("AA:BB:CC:DD:EE:FF", "aa:bb:cc:dd:ee:ff"),
            ("aabb.ccdd.eeff", "aa:bb:cc:dd:ee:ff"),
            ("AABB.CCDD.EEFF", "aa:bb:cc:dd:ee:ff"),
            ("AA-BB-CC-DD-EE-FF", "aa:bb:cc:dd:ee:ff"),
            ("aabbccddeeff", "aa:bb:cc:dd:ee:ff"),
            ("AABBCCDDEEFF", "aa:bb:cc:dd:ee:ff"),
        ],
    )
    def test_canonicalize_every_format(self, value: str, expected: str) -> None:
        assert canonicalize_mac(value) == expected

    def test_non_mac_passes_through(self) -> None:
        assert canonicalize_mac("not-a-mac") == "not-a-mac"
        assert canonicalize_mac("") == ""

    def test_is_mac_recognizes_each_format(self) -> None:
        assert is_mac_address("aa:bb:cc:dd:ee:ff")
        assert is_mac_address("AABB.CCDD.EEFF")
        assert is_mac_address("aa-bb-cc-dd-ee-ff")
        assert is_mac_address("aabbccddeeff")

    def test_is_mac_rejects_invalid(self) -> None:
        assert not is_mac_address("aa:bb:cc:dd:ee:gg")  # 'g' not hex
        assert not is_mac_address("aa:bb:cc:dd:ee")  # too short
        assert not is_mac_address("not-a-mac")
        assert not is_mac_address("")

    def test_normalize_inside_free_text(self) -> None:
        text = "Client AA-BB-CC-DD-EE-FF disconnected from AP aabb.ccdd.eeff at 12:00"
        result = normalize_macs_in_value(text)
        assert "aa:bb:cc:dd:ee:ff" in result
        assert "AA-BB-CC-DD-EE-FF" not in result
        assert "aabb.ccdd.eeff" not in result
        # Surrounding text preserved
        assert "Client" in result
        assert "disconnected from AP" in result
        assert "at 12:00" in result

    def test_bare_hex_not_normalized_in_free_text(self) -> None:
        # A 12-char hex string in free text could be a serial, hash, etc.
        # Free-text normalization explicitly skips bare-hex.
        text = "ID 0123456789ab is interesting"
        assert normalize_macs_in_value(text) == text


# ---------------------------------------------------------------------------
# Field classification
# ---------------------------------------------------------------------------


class TestFieldClassification:
    def test_psk_classified_as_secret(self) -> None:
        cls, kind = classify_field("psk", "Welcome2024!")
        assert cls == FieldClassification.TOKENIZE_SECRET
        assert kind == TokenKind.PSK

    def test_passphrase_classified_as_psk(self) -> None:
        cls, kind = classify_field("passphrase", "longSecret!23")
        assert cls == FieldClassification.TOKENIZE_SECRET
        assert kind == TokenKind.PSK

    def test_ssid_passes_through(self) -> None:
        # SSIDs are broadcast in beacon frames — observable to anyone in
        # radio range. Tokenizing them adds context-window cost without
        # security gain. Refined in v2.3.1.1.
        cls, _ = classify_field("ssid", "Corp-Wifi")
        assert cls == FieldClassification.SKIP

    def test_essid_passes_through(self) -> None:
        cls, _ = classify_field("essid", "Corp-Wifi")
        assert cls == FieldClassification.SKIP

    def test_platform_uuid_ids_pass_through(self) -> None:
        # Platform UUIDs (org_id, site_id, device_id, ...) are already
        # opaque random UUIDs — replacing them with our own UUIDs adds
        # no privacy. Refined in v2.3.1.1.
        for field in (
            "org_id",
            "site_id",
            "device_id",
            "ap_id",
            "switch_id",
            "wlan_id",
            "client_id",
            "template_id",
            "tenant_id",
            "workspace_id",
            "subscription_id",
        ):
            cls, _ = classify_field(field, "abc-123")
            assert cls == FieldClassification.SKIP, field

    def test_geographic_fields_pass_through(self) -> None:
        # Business addresses are typically published on the company's
        # website. The privacy gain doesn't justify the audit-utility
        # loss. Refined in v2.3.1.1.
        for field in (
            "address",
            "city",
            "state",
            "zip",
            "country",
            "latitude",
            "longitude",
            "room",
            "building",
        ):
            cls, _ = classify_field(field, "anything")
            assert cls == FieldClassification.SKIP, field

    def test_hostname_still_tokenized(self) -> None:
        cls, kind = classify_field("hostname", "production-db-01.corp.example.com")
        assert cls == FieldClassification.TOKENIZE_IDENTIFIER
        assert kind == TokenKind.HOSTNAME

    # ---- AOS 8 space-separated-key normalization (issue #235) ------------

    def test_aos8_ip_address_field_normalizes(self) -> None:
        """AOS 8 ``"IP Address"`` lookalike normalizes to the same key as
        ``ip-address`` / ``ip_address``. IPs are intentionally not in any
        rule, so all three resolve to SKIP — but they must all resolve to
        the *same* SKIP, not behave as different fields."""
        a, _ = classify_field("IP Address", "192.0.2.21")
        b, _ = classify_field("ip-address", "192.0.2.21")
        c, _ = classify_field("ip_address", "192.0.2.21")
        assert a == b == c == FieldClassification.SKIP

    def test_aos8_ap_name_with_space_tokenizes_as_hostname(self) -> None:
        """AOS 8 ``show ap database`` returns ``"AP name"`` as the column
        header; with space normalization that becomes ``ap_name`` and
        matches the existing HOSTNAME rule."""
        cls, kind = classify_field("AP name", "Building1-Floor2-AP-07")
        assert cls == FieldClassification.TOKENIZE_IDENTIFIER
        assert kind == TokenKind.HOSTNAME

    def test_aos8_host_name_field_tokenizes_as_hostname(self) -> None:
        """AOS 8 client tables use ``"Host Name"``."""
        cls, kind = classify_field("Host Name", "alice-laptop")
        assert cls == FieldClassification.TOKENIZE_IDENTIFIER
        assert kind == TokenKind.HOSTNAME

    def test_aos8_controller_name_via_bare_name_with_device_siblings(self) -> None:
        """AOS 8 ``show switches`` returns a flat record where the controller
        identifier is just ``"Name"``, with siblings ``"Model"``, ``"Version"``,
        and ``"Release Type"``. The bare-``name`` heuristic must fire on this
        exact live shape (issue #237 — original v2.4.0.5 fix used a rigged
        ``"firmware"`` key in the test, masking that ``Version`` and
        ``Release Type`` weren't yet device-context hints)."""
        cls, kind = classify_field(
            "Name",
            "MM-01",
            parent_keys=frozenset(
                {
                    "Config ID",
                    "Configuration State",
                    "IP Address",
                    "Location",
                    "Model",
                    "Name",
                    "Release Type",
                    "Status",
                    "Type",
                    "Version",
                }
            ),
        )
        assert cls == FieldClassification.TOKENIZE_IDENTIFIER
        assert kind == TokenKind.HOSTNAME

    def test_unknown_field_skipped(self) -> None:
        cls, _ = classify_field("status", "online")
        assert cls == FieldClassification.SKIP

    def test_description_marked_as_free_text(self) -> None:
        cls, _ = classify_field("description", "anything")
        assert cls == FieldClassification.SCAN_FREE_TEXT

    def test_generic_key_with_short_value_skipped(self) -> None:
        # 'key': 'ssid' is a template-style use, NOT a credential
        cls, _ = classify_field("key", "ssid")
        assert cls == FieldClassification.SKIP

    def test_generic_secret_with_credential_shape_tokenized(self) -> None:
        cls, kind = classify_field("secret", "L0ng-StRong-S3cret!")
        assert cls == FieldClassification.TOKENIZE_SECRET
        assert kind == TokenKind.RAD

    def test_generic_password_with_enum_value_skipped(self) -> None:
        # 'password': 'disabled' would be a config flag, not a credential
        cls, _ = classify_field("password", "disabled")
        assert cls == FieldClassification.SKIP

    def test_bare_name_in_device_context_becomes_hostname(self) -> None:
        # Real device shape: 3 device hints (mac, model, serial). The
        # v2.3.1.2 threshold is 2+, so this still triggers HOSTNAME.
        cls, kind = classify_field(
            "name",
            "AP-Floor-3",
            parent_keys=frozenset({"name", "mac", "model", "serial"}),
        )
        assert cls == FieldClassification.TOKENIZE_IDENTIFIER
        assert kind == TokenKind.HOSTNAME

    def test_bare_name_outside_device_context_skipped(self) -> None:
        cls, _ = classify_field(
            "name",
            "TestThing",
            parent_keys=frozenset({"name", "value", "type"}),
        )
        assert cls == FieldClassification.SKIP

    def test_wxtag_shape_does_not_trigger_hostname(self) -> None:
        # wxtag has a single ``mac`` field for client-MAC matching but
        # is not a device. Pre-v2.3.1.2 this incorrectly triggered
        # HOSTNAME tokenization on the wxtag's display name. The 2+
        # device-hints threshold (v2.3.1.2) closes the false positive.
        cls, _ = classify_field(
            "name",
            "DHCP/DNS Ports",
            parent_keys=frozenset(
                {
                    "op",
                    "values",
                    "id",
                    "name",
                    "for_site",
                    "site_id",
                    "org_id",
                    "type",
                    "match",
                    "resource_mac",
                    "mac",
                }
            ),
        )
        assert cls == FieldClassification.SKIP

    def test_single_device_hint_no_longer_triggers_hostname(self) -> None:
        # Threshold is 2+ in v2.3.1.2. A single hint isn't enough.
        cls, _ = classify_field(
            "name",
            "Generic-1",
            parent_keys=frozenset({"name", "mac"}),
        )
        assert cls == FieldClassification.SKIP

    def test_two_device_hints_still_triggers_hostname(self) -> None:
        cls, kind = classify_field(
            "name",
            "Generic-2",
            parent_keys=frozenset({"name", "mac", "model"}),
        )
        assert cls == FieldClassification.TOKENIZE_IDENTIFIER
        assert kind == TokenKind.HOSTNAME

    # --- Central additions (v2.3.1.3) ---

    def test_central_user_name_tokenized(self) -> None:
        # Central uses snake_case `user_name` alongside Mist-style `username`
        cls, kind = classify_field("user_name", "alice")
        assert cls == FieldClassification.TOKENIZE_IDENTIFIER
        assert kind == TokenKind.USER

    def test_central_updated_by_tokenized(self) -> None:
        cls, kind = classify_field("updated_by", "admin@corp.com")
        assert cls == FieldClassification.TOKENIZE_IDENTIFIER
        assert kind == TokenKind.USER

    def test_central_created_by_tokenized(self) -> None:
        cls, kind = classify_field("created_by", "automation-bot")
        assert cls == FieldClassification.TOKENIZE_IDENTIFIER
        assert kind == TokenKind.USER

    def test_central_device_group_name_passes_through(self) -> None:
        # Per v2.3.1.3 design discussion: organizational structure, not
        # customer-identifying. Operators benefit from cleartext.
        cls, _ = classify_field("device_group_name", "Indianapolis Stores")
        assert cls == FieldClassification.SKIP

    def test_central_scope_name_passes_through(self) -> None:
        cls, _ = classify_field("scope_name", "Global")
        assert cls == FieldClassification.SKIP

    def test_hyphenated_wpa_passphrase_tokenized_as_psk(self) -> None:
        # Central's central_get_wlan_profiles returns raw API payloads
        # with hyphenated keys (e.g. `wpa-passphrase` inside
        # `personal-security`). The v2.3.1.3 hyphen normalization in
        # classify_field maps these to the same ruleset entries as
        # their snake_case equivalents.
        cls, kind = classify_field("wpa-passphrase", "Welcome2024!")
        assert cls == FieldClassification.TOKENIZE_SECRET
        assert kind == TokenKind.PSK

    def test_hyphenated_shared_secret_tokenized(self) -> None:
        cls, kind = classify_field("shared-secret", "RadiusSharedSecret123!")
        assert cls == FieldClassification.TOKENIZE_SECRET
        assert kind == TokenKind.RAD


class TestCredentialShapeHeuristic:
    def test_long_mixed_string_looks_credential(self) -> None:
        assert looks_like_credential("Welcome2024!")
        assert looks_like_credential("MyP@ssw0rd123")

    def test_short_string_does_not(self) -> None:
        assert not looks_like_credential("short")
        assert not looks_like_credential("abc")

    def test_long_uniform_string_does_not(self) -> None:
        # No character-class diversity, no special chars
        assert not looks_like_credential("alllowercase")
        assert not looks_like_credential("ALLUPPERCASE")
        assert not looks_like_credential("12345678")

    def test_special_char_alone_is_enough(self) -> None:
        assert looks_like_credential("password!23")  # special bumps it past length

    def test_known_enum_values_recognized(self) -> None:
        assert is_known_enum_value("auto")
        assert is_known_enum_value("DISABLED")
        assert not is_known_enum_value("Welcome2024!")


# ---------------------------------------------------------------------------
# TokenStore + Tokenizer
# ---------------------------------------------------------------------------


class TestTokenStoreLifecycle:
    def test_session_isolation(self) -> None:
        store = TokenStore()
        keymap_a = store.get_or_create("session-a")
        keymap_b = store.get_or_create("session-b")
        assert keymap_a is not keymap_b
        assert store.session_count() == 2

    def test_get_or_create_idempotent(self) -> None:
        store = TokenStore()
        first = store.get_or_create("session-a")
        again = store.get_or_create("session-a")
        assert first is again

    def test_end_session_purges(self) -> None:
        store = TokenStore()
        keymap = store.get_or_create("session-a")
        keymap.by_token["[[PSK:abc]]"] = None  # type: ignore[assignment]
        dropped = store.end_session("session-a")
        assert dropped == 1
        assert store.get("session-a") is None

    def test_allocate_token_format(self) -> None:
        token = allocate_token(TokenKind.PSK, "anything")
        assert re.match(rf"\[\[PSK:{UUID_PART}\]\]", token)


class TestIsMaskedPlaceholder:
    """is_masked_placeholder() recognizes source-platform-masked values.

    These must never be tokenized — a tokenized placeholder is a dangerous
    illusion (issue #235). Since issue #276 the walker goes further: it
    rewrites the masked value to the literal ``REPLACE_ME`` directive so the
    operator gets a loud, actionable marker in migration output."""

    def test_eight_asterisks_is_placeholder(self) -> None:
        assert is_masked_placeholder("********")

    def test_four_asterisks_is_placeholder(self) -> None:
        assert is_masked_placeholder("****")

    def test_three_asterisks_too_short(self) -> None:
        # Conservative lower bound — three '*' could be a regex artifact
        # in a description field, etc. Real AOS 8 placeholder is 8 chars.
        assert not is_masked_placeholder("***")

    def test_real_credential_with_asterisks_not_placeholder(self) -> None:
        # An asterisk *inside* a real credential doesn't trigger the
        # placeholder rule — the rule only matches all-asterisk strings.
        assert not is_masked_placeholder("Welcome*123!")

    def test_empty_string_not_placeholder(self) -> None:
        assert not is_masked_placeholder("")

    def test_non_string_not_placeholder(self) -> None:
        assert not is_masked_placeholder(None)
        assert not is_masked_placeholder(42)

    def test_classify_field_masked_secret_field_returns_masked_secret(self) -> None:
        # ``shared_secret`` is in SECRET_FIELD_NAMES — would normally
        # tokenize unconditionally. A masked placeholder must short-circuit
        # to MASKED_SECRET (walker rewrites to REPLACE_ME), not tokenize.
        cls, _ = classify_field("shared_secret", "********")
        assert cls == FieldClassification.MASKED_SECRET

    def test_classify_field_masked_generic_credential_field_returns_masked_secret(self) -> None:
        # ``key`` is in GENERIC_CREDENTIAL_FIELD_NAMES with shape-check.
        # Even though ``********`` passes looks_like_credential, the
        # placeholder check fires first → MASKED_SECRET.
        cls, _ = classify_field("key", "********")
        assert cls == FieldClassification.MASKED_SECRET

    def test_classify_field_still_tokenizes_real_credential(self) -> None:
        # Sanity: the placeholder path must not affect real values.
        cls, kind = classify_field("shared_secret", "MyRealSecret123!")
        assert cls == FieldClassification.TOKENIZE_SECRET
        assert kind == TokenKind.RAD


class TestMaskedSecretRewrite:
    """Issue #276 — source-masked ``********`` values are rewritten to the
    literal ``REPLACE_ME`` directive by the walker (never tokenized), giving
    the operator a loud, actionable marker in migration output. The walk is
    idempotent and ``REPLACE_ME`` is never tokenized even in an exact-match
    secret field."""

    def _tokenizer(self, label: str) -> Tokenizer:
        return Tokenizer(SessionKeymap(), session_id=f"test-session-276-{label}", max_entries=100)

    def test_is_known_placeholder_recognizes_replace_me(self) -> None:
        assert is_known_placeholder("REPLACE_ME")
        assert is_known_placeholder(MASKED_SECRET_PLACEHOLDER)

    def test_is_known_placeholder_rejects_other_values(self) -> None:
        assert not is_known_placeholder("********")
        assert not is_known_placeholder("replace_me")  # case-sensitive
        assert not is_known_placeholder("MyRealSecret123!")
        assert not is_known_placeholder(None)

    def test_classify_field_replace_me_is_skipped(self) -> None:
        # REPLACE_ME landing in an exact-match secret field must NOT
        # tokenize — the is_known_placeholder guard returns SKIP.
        cls, kind = classify_field("shared_secret", "REPLACE_ME")
        assert cls == FieldClassification.SKIP
        assert kind is None

    def test_walker_rewrites_masked_secret_to_replace_me(self) -> None:
        tokenizer = self._tokenizer("rewrite")
        response = {"shared_secret": "********", "auth_port": "1812"}
        out = tokenize_response(response, tokenizer)
        assert out["shared_secret"] == "REPLACE_ME"
        # Non-masked siblings untouched.
        assert out["auth_port"] == "1812"

    def test_walker_rewrites_masked_secret_in_any_field(self) -> None:
        # The masked check fires regardless of field name — a transposed
        # AOS 8 row carries the masked secret in a generic ``Value`` field.
        tokenizer = self._tokenizer("anyfield")
        response = {"Parameter": "Key", "Value": "********"}
        out = tokenize_response(response, tokenizer)
        assert out["Value"] == "REPLACE_ME"

    def test_walk_is_idempotent_on_replace_me(self) -> None:
        # A second walk sees REPLACE_ME (not ********) and leaves it alone.
        tokenizer = self._tokenizer("idempotent")
        response = {"shared_secret": "********"}
        first = tokenize_response(response, tokenizer)
        second = tokenize_response(first, tokenizer)
        assert first["shared_secret"] == "REPLACE_ME"
        assert second["shared_secret"] == "REPLACE_ME"

    def test_replace_me_not_tokenized_in_exact_match_secret_field(self) -> None:
        # A tool emitting REPLACE_ME directly into coa_secret (an exact-match
        # SECRET_FIELD_NAMES entry) must not have it tokenized — that would
        # bury the operator signal behind an opaque token.
        tokenizer = self._tokenizer("guard")
        response = {"coa_secret": "REPLACE_ME"}
        out = tokenize_response(response, tokenizer)
        assert out["coa_secret"] == "REPLACE_ME"
        assert TOKEN_RE.fullmatch(out["coa_secret"]) is None

    def test_real_secret_still_tokenizes_alongside_masked_one(self) -> None:
        # Mixed response: one masked secret, one cleartext secret. The
        # masked one becomes REPLACE_ME; the real one still tokenizes.
        tokenizer = self._tokenizer("mixed")
        response = {"radius_secret": "********", "coa_secret": "RealCoaSecret123!"}
        out = tokenize_response(response, tokenizer)
        assert out["radius_secret"] == "REPLACE_ME"
        assert TOKEN_RE.fullmatch(out["coa_secret"]).group(1) == "RAD"

    def test_detokenize_arguments_leaves_replace_me_untouched(self) -> None:
        # REPLACE_ME is a literal, not a token — the inbound walker leaves
        # it alone and does not flag it as an unknown token.
        tokenizer = self._tokenizer("inbound")
        args = {"payload": {"coa_secret": "REPLACE_ME"}}
        restored, unknown = detokenize_arguments(args, tokenizer)
        assert restored["payload"]["coa_secret"] == "REPLACE_ME"
        assert unknown == []


class TestStructuralSecretContexts:
    """Issue #277 — wrappings like ``rad_key`` make a generic ``key`` field
    unambiguously a credential. Walker passes the wrapping name down so
    classify_field can short-circuit the shape-check that would otherwise
    leak short single-class shared secrets like ``"protocol"``.
    """

    def test_rad_key_key_tokenizes_unconditionally_short_value(self) -> None:
        # ``"protocol"`` — 8 chars, all lowercase, 1 char class — would FAIL
        # ``looks_like_credential`` and skip without the structural rule.
        cls, kind = classify_field("key", "protocol", parent_field_name="rad_key")
        assert cls == FieldClassification.TOKENIZE_SECRET
        assert kind == TokenKind.RAD

    def test_rad_key_key_tokenizes_long_value_too(self) -> None:
        cls, kind = classify_field("key", "nowireless4u", parent_field_name="rad_key")
        assert cls == FieldClassification.TOKENIZE_SECRET
        assert kind == TokenKind.RAD

    def test_tacacs_key_key_classifies_as_tacacs(self) -> None:
        cls, kind = classify_field("key", "tacsecret", parent_field_name="tacacs_key")
        assert cls == FieldClassification.TOKENIZE_SECRET
        assert kind == TokenKind.TACACS

    def test_bare_key_outside_known_wrapper_still_skipped(self) -> None:
        # ``{"key": "ssid"}`` template-style usage — no wrapper context —
        # must still pass through SKIP (preserves the existing false-positive guard).
        cls, _ = classify_field("key", "ssid")
        assert cls == FieldClassification.SKIP

    def test_bare_key_under_unknown_wrapper_still_uses_shape_check(self) -> None:
        # Wrapper isn't in STRUCTURAL_SECRET_CONTEXTS — falls through to
        # the generic-credential rule, which applies the shape check.
        cls, _ = classify_field("key", "ssid", parent_field_name="some_unknown_wrapper")
        assert cls == FieldClassification.SKIP

    def test_masked_placeholder_under_rad_key_returns_masked_secret(self) -> None:
        # The masked-placeholder check runs BEFORE the structural rule so an
        # AOS-8 masked secret nested under rad_key doesn't get tokenized.
        # Since issue #276 it classifies MASKED_SECRET (walker rewrites to
        # REPLACE_ME) rather than the bare SKIP from PR #275.
        cls, _ = classify_field("key", "********", parent_field_name="rad_key")
        assert cls == FieldClassification.MASKED_SECRET


class TestSchemaLabelPassthrough:
    """v3.0.1.12 privacy-model refinement — ``vlan_name``, ``subnet_name``,
    ``org_name``, ``site_name`` are no longer tokenized. They are schema
    labels describing network architecture (or publicly-findable corporate
    identifiers) and audit utility benefits from cleartext. Companion
    fixture-level test in ``TestRealisticCentralFixture.test_wlan_profile_walk``
    asserts the same for the Central profile shape.
    """

    @pytest.mark.parametrize(
        "field_name,value",
        [
            ("vlan_name", "Corporate"),
            ("subnet_name", "Guest-Subnet"),
            ("org_name", "Acme Networks"),
            ("site_name", "HQ"),
        ],
    )
    def test_schema_label_fields_pass_through(self, field_name: str, value: str) -> None:
        cls, kind = classify_field(field_name, value)
        assert cls == FieldClassification.SKIP
        assert kind is None

    def test_inner_name_under_vlan_name_wrapper_no_longer_tokenized(self) -> None:
        # Companion to the removed ``(vlan_name, name)`` structural rule —
        # the AOS 8 list shape ``{"vlan_name": [{"name": "guest"}]}``
        # now passes through cleartext, matching the policy.
        cls, _ = classify_field("name", "guest", parent_field_name="vlan_name")
        assert cls == FieldClassification.SKIP


class TestStructuralCoaContexts:
    """v3.0.1.12 — CoA / RFC-3576 dynamic-authorization endpoints and
    shared secrets are auth-fabric-critical, so we tokenize them under
    ``TokenKind.COA``. Two structural rules cover the two known wrapper
    shapes:

    * AOS 8 ``rfc_3576_server_list`` carries the endpoint IP under
      ``Name``. Verified live via ``show aaa rfc-3576-server``.
    * Mist ``coa_servers`` carries the endpoint under ``ip`` and the
      shared secret under ``secret``. Documented in
      ``schemas_data.py``.
    """

    def test_rfc_3576_name_classifies_as_coa(self) -> None:
        cls, kind = classify_field("name", "192.168.20.70", parent_field_name="rfc_3576_server_list")
        assert cls == FieldClassification.TOKENIZE_IDENTIFIER
        assert kind == TokenKind.COA

    def test_coa_servers_ip_classifies_as_coa(self) -> None:
        cls, kind = classify_field("ip", "10.50.10.20", parent_field_name="coa_servers")
        assert cls == FieldClassification.TOKENIZE_IDENTIFIER
        assert kind == TokenKind.COA

    def test_coa_servers_secret_classifies_as_rad_secret(self) -> None:
        # Issue #321: CoA secrets joined the RAD family so the combined
        # CoA + RADIUS migration tool (#322) can emit the same plaintext
        # in radius_secret + coa_secret + coa_servers[].secret and have
        # the keymap return a single [[RAD:uuid]] for all three.
        cls, kind = classify_field("secret", "MyCoaSecret123!", parent_field_name="coa_servers")
        assert cls == FieldClassification.TOKENIZE_SECRET
        assert kind == TokenKind.RAD

    def test_coa_secret_flat_field_classifies_as_rad(self) -> None:
        # Issue #321: the flat ``coa_secret`` field name is what the
        # combined migration tool emits in its output structure.
        cls, kind = classify_field("coa_secret", "MyCoaSecret123!")
        assert cls == FieldClassification.TOKENIZE_SECRET
        assert kind == TokenKind.RAD

    def test_bare_ip_outside_coa_wrapper_still_passes_through(self) -> None:
        # Per v2.3.1.2: plain ``ip`` is not a tokenized field. Only the
        # structural rule under ``coa_servers`` fires.
        cls, _ = classify_field("ip", "10.50.10.20")
        assert cls == FieldClassification.SKIP


class TestStructuralCoaContextsEndToEnd:
    """Walker end-to-end tests for v3.0.1.12 CoA rules — verify the actual
    AOS 8 + Mist response shapes plug their leaks through the full
    ``tokenize_response`` pipeline.
    """

    def test_aos8_rfc_3576_server_list_response_shape_tokenizes_name(self) -> None:
        keymap = SessionKeymap()
        tokenizer = Tokenizer(keymap, session_id="test-session-coa-aos8", max_entries=100)

        # Live-captured AOS 8 response shape from ``show aaa rfc-3576-server``.
        # Walker normalizes "RFC 3576 Server List" → "rfc_3576_server_list"
        # and "Name" → "name" before the structural rule consults the table.
        response = {
            "RFC 3576 Server List": [
                {"Name": "192.168.20.70", "Profile Status": None, "References": "0"},
                {"Name": "192.168.20.75", "Profile Status": None, "References": "0"},
            ],
            "_data": ["2"],
        }
        out = tokenize_response(response, tokenizer)
        records = out["RFC 3576 Server List"]
        for record in records:
            assert TOKEN_RE.fullmatch(record["Name"]) is not None
            assert TOKEN_RE.fullmatch(record["Name"]).group(1) == "COA"
        assert len({r["Name"] for r in records}) == 2

    def test_mist_coa_servers_shape_tokenizes_ip_as_coa_and_secret_as_rad(self) -> None:
        # Issue #321: split CoA endpoint identifier (COA prefix) from
        # CoA shared secret (RAD prefix, joining the RADIUS family).
        keymap = SessionKeymap()
        tokenizer = Tokenizer(keymap, session_id="test-session-coa-mist", max_entries=100)

        # Mist WLAN coa_servers shape from schemas_data.py.
        response = {
            "coa_servers": [
                {"ip": "10.50.10.20", "port": 3799, "enabled": True, "secret": "CoaSharedSecret!"},
                {"ip": "10.50.10.21", "port": 3799, "enabled": True, "secret": "AnotherCoaSecret!"},
            ]
        }
        out = tokenize_response(response, tokenizer)
        servers = out["coa_servers"]
        for server in servers:
            # IP — identifier — keeps COA prefix.
            assert TOKEN_RE.fullmatch(server["ip"]) is not None
            assert TOKEN_RE.fullmatch(server["ip"]).group(1) == "COA"
            # Secret — joined to RAD family for combined-tool dedup (#321 / #322).
            assert TOKEN_RE.fullmatch(server["secret"]) is not None
            assert TOKEN_RE.fullmatch(server["secret"]).group(1) == "RAD"
        # Operational metadata passes through.
        assert servers[0]["port"] == 3799
        assert servers[0]["enabled"] is True

    def test_radius_secret_and_coa_secret_share_token_when_same_plaintext(self) -> None:
        """Issue #321 / #322 — the combined CoA + RADIUS migration tool
        emits the same plaintext in both ``radius_secret`` and ``coa_secret``
        fields when servers are co-located. Both fields now classify as
        ``TokenKind.RAD``, so the keymap returns a single token for both,
        and the AI sees the secret reused literally across the structure.
        """
        keymap = SessionKeymap()
        tokenizer = Tokenizer(keymap, session_id="test-session-321-shared", max_entries=100)

        response = {
            "radius_server": "192.168.20.70",
            "radius_secret": "aruba123!",
            "coa_endpoint": "192.168.20.70",
            "coa_secret": "aruba123!",
            "co_located": True,
        }
        out = tokenize_response(response, tokenizer)

        # Same plaintext + same TokenKind → same token via keymap.
        assert out["radius_secret"] == out["coa_secret"]
        assert TOKEN_RE.fullmatch(out["radius_secret"]).group(1) == "RAD"


class TestWrapperKeyRewrite:
    """Issue #319 — when a platform surfaces a single-record detail block
    under a wrapper key embedding the record identifier (e.g. AOS 8's
    ``show aaa rfc-3576-server <ip>`` returns ``{"RFC 3576 Server <ip>":
    [...]}``), the walker must rewrite the key so the embedded value is
    tokenized.

    The structural rules only consult NORMALIZED field names, so the raw
    key string carrying the IP would otherwise surface verbatim. The fix
    is keyed off ``WRAPPER_KEY_PATTERNS`` in ``rules.py`` and applies
    in ``_walk_dict``; round-trip detokenization is extended to dict
    keys in ``_detokenize_walk``.
    """

    def test_aos8_rfc_3576_detail_wrapper_key_gets_rewritten(self) -> None:
        keymap = SessionKeymap()
        tokenizer = Tokenizer(keymap, session_id="test-session-319-detail", max_entries=100)

        # Live-captured AOS 8 shape from ``show aaa rfc-3576-server 192.168.20.70``.
        response = {
            "RFC 3576 Server 192.168.20.70": [
                {"Parameter": "Key", "Value": "********"},
                {"Parameter": "RadSec", "Value": "Disabled"},
                {"Parameter": "Window Duration", "Value": "300"},
            ],
        }
        out = tokenize_response(response, tokenizer)

        # The original IP-bearing key is gone.
        assert "RFC 3576 Server 192.168.20.70" not in out
        # A rewritten key with a COA token is present.
        rewritten_keys = list(out.keys())
        assert len(rewritten_keys) == 1
        rewritten_key = rewritten_keys[0]
        assert rewritten_key.startswith("RFC 3576 Server ")
        token_part = rewritten_key[len("RFC 3576 Server ") :]
        match = TOKEN_RE.fullmatch(token_part)
        assert match is not None, f"expected COA token, got {token_part!r}"
        assert match.group(1) == "COA"

    def test_same_ip_in_list_and_detail_forms_share_a_token(self) -> None:
        """Migration tooling depends on the same IP across list-form and
        detail-form wrappers getting the same token — fans out correctly
        when the AI references the server by either shape.
        """
        keymap = SessionKeymap()
        tokenizer = Tokenizer(keymap, session_id="test-session-319-correlate", max_entries=100)

        # List form first (matches the existing ``rfc_3576_server_list[].name``
        # structural rule → COA).
        list_resp = {
            "RFC 3576 Server List": [
                {"Name": "192.168.20.70", "Profile Status": None, "References": "0"},
            ],
        }
        list_out = tokenize_response(list_resp, tokenizer)
        list_token = list_out["RFC 3576 Server List"][0]["Name"]
        assert TOKEN_RE.fullmatch(list_token).group(1) == "COA"

        # Detail form second — same IP. New wrapper-key rewrite must use
        # the SAME token via the keymap (same kind, same plaintext).
        detail_resp = {
            "RFC 3576 Server 192.168.20.70": [{"Parameter": "Key", "Value": "********"}],
        }
        detail_out = tokenize_response(detail_resp, tokenizer)
        detail_key = next(iter(detail_out.keys()))
        detail_token = detail_key[len("RFC 3576 Server ") :]
        assert detail_token == list_token, "list-form and detail-form must share the COA token"

    def test_wrapper_key_round_trips_via_detokenize_arguments(self) -> None:
        """If the AI passes the rewritten wrapper-key dict back as an
        argument, the inbound walker must restore the cleartext IP before
        the call hits the downstream platform.
        """
        keymap = SessionKeymap()
        tokenizer = Tokenizer(keymap, session_id="test-session-319-roundtrip", max_entries=100)

        response = {
            "RFC 3576 Server 192.168.20.70": [{"Parameter": "Key", "Value": "********"}],
        }
        tokenized = tokenize_response(response, tokenizer)
        rewritten_key = next(iter(tokenized.keys()))

        # AI hands the dict back as an argument.
        arguments = {"payload": tokenized}
        restored_args, unknown = detokenize_arguments(arguments, tokenizer)

        assert unknown == []
        restored_payload = restored_args["payload"]
        assert "RFC 3576 Server 192.168.20.70" in restored_payload
        assert rewritten_key not in restored_payload

    def test_wrapper_pattern_no_match_is_noop(self) -> None:
        """A dict whose keys don't match any wrapper pattern is unchanged."""
        keymap = SessionKeymap()
        tokenizer = Tokenizer(keymap, session_id="test-session-319-noop", max_entries=100)

        response = {"some_unrelated_key": {"inner": "value"}}
        out = tokenize_response(response, tokenizer)
        assert "some_unrelated_key" in out
        assert out["some_unrelated_key"] == {"inner": "value"}


class TestKeymapReplayOnSkipPath:
    """Issue #291 — walker keymap-replay on SKIP path. When a tool emits
    a previously-tokenized cleartext value at a field that carries no
    rule (e.g. ``central_translation_preview``'s ``record_id``), the
    walker should consult the session keymap and restore the existing
    token. Closes the round-trip leak where tools detokenize inputs,
    process cleartext internally, and re-emit values that have lost
    their original structural context.

    (Rewritten in v3.0.1.12 to use the AOS 8 ``rfc_3576_server_list``
    structural rule as setup — the previous ``(vlan_name, name)`` rule
    was removed as part of the privacy-model refinement.)
    """

    def _new_tokenizer(self):
        from hpe_networking_mcp.redaction.token_store import SessionKeymap
        from hpe_networking_mcp.redaction.tokenizer import Tokenizer

        return Tokenizer(SessionKeymap(), session_id="test-session-291", max_entries=100)

    def _seed_coa_token(self, tokenizer, value: str) -> str:
        """Helper: tokenize ``value`` via the AOS 8 CoA structural rule
        and return the issued token.
        """
        from hpe_networking_mcp.redaction.walker import tokenize_response

        out = tokenize_response(
            {"RFC 3576 Server List": [{"Name": value}]},
            tokenizer,
        )
        return out["RFC 3576 Server List"][0]["Name"]

    def test_value_tokenized_then_replayed_at_unrelated_field(self) -> None:
        """The classic round-trip: a structural rule tokenizes an IP; later,
        an unrelated tool emits the same IP at a generic ``record_id`` field
        with no rule. The replay should restore the original token.
        """
        from hpe_networking_mcp.redaction.walker import tokenize_response

        tokenizer = self._new_tokenizer()
        original_token = self._seed_coa_token(tokenizer, "192.168.20.70")
        assert TOKEN_RE.fullmatch(original_token) is not None
        assert original_token.startswith("[[COA:")

        second = tokenize_response(
            {"results": [{"record_id": "192.168.20.70", "call_count": 7}]},
            tokenizer,
        )
        assert second["results"][0]["record_id"] == original_token

    def test_value_replayed_inside_nested_unrelated_structure(self) -> None:
        """Round-trip survives when the same cleartext appears inside a
        nested dict with no structural context (e.g. inside a TargetCall
        body emitted by ``central_translation_preview``).
        """
        from hpe_networking_mcp.redaction.walker import tokenize_response

        tokenizer = self._new_tokenizer()
        seeded = self._seed_coa_token(tokenizer, "192.168.20.70")

        nested = tokenize_response(
            {"sample_body": {"host": "192.168.20.70", "auth": {"target-host": "192.168.20.70"}}},
            tokenizer,
        )
        body = nested["sample_body"]
        # ``host`` has its own HOSTNAME rule, so it tokenizes there; the
        # kind-agnostic dedup returns the *existing* COA token rather than
        # allocating a fresh HOSTNAME entry for the same plaintext.
        assert body["host"] == seeded
        # ``target-host`` carries no rule — replay restores the same token.
        assert body["auth"]["target-host"] == seeded

    def test_value_never_tokenized_stays_cleartext(self) -> None:
        """Negative: a string that was never tokenized in this session must
        not be touched by the replay pass. No false positives from random
        keymap collisions.
        """
        from hpe_networking_mcp.redaction.walker import tokenize_response

        tokenizer = self._new_tokenizer()
        result = tokenize_response({"results": [{"record_id": "never-seen-before"}]}, tokenizer)
        assert result["results"][0]["record_id"] == "never-seen-before"

    def test_existing_token_not_double_tokenized(self) -> None:
        """Idempotency: a value that's already a ``[[KIND:uuid]]`` token
        passes through the replay pass unchanged.
        """
        from hpe_networking_mcp.redaction.walker import tokenize_response

        tokenizer = self._new_tokenizer()
        original_token = self._seed_coa_token(tokenizer, "192.168.20.70")

        result = tokenize_response({"results": [{"record_id": original_token}]}, tokenizer)
        assert result["results"][0]["record_id"] == original_token

    def test_token_for_existing_cleartext_lookup_method(self) -> None:
        """Direct API check on the lookup method."""
        tokenizer = self._new_tokenizer()
        # Empty / non-string / not-yet-tokenized: None.
        assert tokenizer.token_for_existing_cleartext("") is None
        assert tokenizer.token_for_existing_cleartext("never-seen") is None
        # After tokenizing, returns the same token.
        from hpe_networking_mcp.redaction.tokenizer import tokenize_value

        token = tokenize_value(tokenizer, TokenKind.PSK, "MySharedKey123!")
        assert tokenizer.token_for_existing_cleartext("MySharedKey123!") == token
        # Idempotency: passing a token through the lookup returns None
        # (we never want to "tokenize" a token-shaped value).
        assert tokenizer.token_for_existing_cleartext(token) is None

    def test_translation_preview_record_id_round_trip(self) -> None:
        """End-to-end shape that mirrors the actual leak from issue #291:
        a structural rule tokenizes a value at read; then the
        ``central_translation_preview`` response shape carries the same
        cleartext at ``results[].record_id`` (a SKIP-classified field)
        AND inside a nested TargetCall body. Both must restore the
        original token via replay.
        """
        from hpe_networking_mcp.redaction.walker import tokenize_response

        tokenizer = self._new_tokenizer()
        # Seed two CoA endpoints via the AOS 8 structural rule.
        out = tokenize_response(
            {
                "RFC 3576 Server List": [
                    {"Name": "192.168.20.70"},
                    {"Name": "192.168.20.75"},
                ]
            },
            tokenizer,
        )
        token_a = out["RFC 3576 Server List"][0]["Name"]
        token_b = out["RFC 3576 Server List"][1]["Name"]
        assert token_a.startswith("[[COA:")
        assert token_b.startswith("[[COA:")

        preview_response = {
            "translation_id": "central:auth_server",
            "results": [
                {
                    "record_id": "192.168.20.70",
                    "call_count": 7,
                    "target_calls": [
                        {
                            "endpoint": "/network-config/v1alpha1/auth-server/192.168.20.70",
                            "body": {"target-host": "192.168.20.70"},
                        }
                    ],
                },
                {"record_id": "192.168.20.75", "call_count": 9, "target_calls": []},
            ],
        }
        result = tokenize_response(preview_response, tokenizer)
        assert result["results"][0]["record_id"] == token_a
        assert result["results"][1]["record_id"] == token_b
        body = result["results"][0]["target_calls"][0]["body"]
        assert body["target-host"] == token_a


class TestKindAgnosticDedup:
    """v3.0.1.12 — ``Tokenizer.tokenize`` deduplicates by plaintext across
    kinds. Concrete motivation: a CoA shared secret typically reuses the
    RADIUS shared secret on the same auth fabric. Once one rule has
    issued a token for that plaintext, the other rule must return the
    same token, not allocate a parallel one.
    """

    def _new_tokenizer(self):
        return Tokenizer(SessionKeymap(), session_id="test-session-dedup", max_entries=100)

    def test_same_plaintext_under_different_kinds_returns_same_token(self) -> None:
        tokenizer = self._new_tokenizer()
        rad_token = tokenizer.tokenize(TokenKind.RAD, "SharedSecret123!")
        coa_token = tokenizer.tokenize(TokenKind.COA, "SharedSecret123!")
        assert rad_token == coa_token
        # And one keymap entry, not two.
        assert len(tokenizer.keymap) == 1

    def test_dedup_preserves_original_kind_label(self) -> None:
        """The first kind to allocate wins — subsequent same-plaintext
        requests inherit the original kind prefix in the token string.
        That's intentional: the AI sees a stable, single token regardless
        of which rule encountered the value first.
        """
        tokenizer = self._new_tokenizer()
        rad_token = tokenizer.tokenize(TokenKind.RAD, "SharedSecret123!")
        coa_token = tokenizer.tokenize(TokenKind.COA, "SharedSecret123!")
        assert rad_token.startswith("[[RAD:")
        assert coa_token == rad_token  # not [[COA:...]]

    def test_dedup_then_detokenize_returns_original_plaintext(self) -> None:
        tokenizer = self._new_tokenizer()
        plaintext = "SharedSecret123!"
        coa_token = tokenizer.tokenize(TokenKind.COA, plaintext)
        # Tokenize again via different kind to exercise the dedup path.
        rad_token = tokenizer.tokenize(TokenKind.RAD, plaintext)
        assert rad_token == coa_token
        # Round-trip works on the single shared token.
        assert tokenizer.detokenize(coa_token) == plaintext

    def test_dedup_walker_e2e_radius_and_coa_share_one_token(self) -> None:
        """End-to-end: a tool response that contains the same shared
        secret under both ``shared_secret`` (RAD rule) and inside a
        ``coa_servers`` element (COA structural rule) produces a single
        consistent token across both fields. Mirrors the live scenario
        Jon described: "That server would use the same secret as the
        radius servers since they are typically the same."
        """
        from hpe_networking_mcp.redaction.walker import tokenize_response

        tokenizer = self._new_tokenizer()
        plaintext = "OurFabricRadSecret!"
        response = {
            "radius_servers": [{"host": "10.50.10.10", "shared_secret": plaintext}],
            "coa_servers": [{"ip": "10.50.10.10", "secret": plaintext, "port": 3799}],
        }
        out = tokenize_response(response, tokenizer)

        rad_secret_token = out["radius_servers"][0]["shared_secret"]
        coa_secret_token = out["coa_servers"][0]["secret"]
        assert rad_secret_token == coa_secret_token
        assert TOKEN_RE.fullmatch(rad_secret_token) is not None
        # Walker traversal order: top-level keys in insertion order, so
        # radius_servers fires first and the RAD kind wins the allocation.
        assert rad_secret_token.startswith("[[RAD:")

    def test_different_plaintexts_still_get_different_tokens(self) -> None:
        """Negative: dedup only fires for identical plaintext. Different
        secrets must still get different tokens even under the same kind.
        """
        tokenizer = self._new_tokenizer()
        a = tokenizer.tokenize(TokenKind.RAD, "SecretA")
        b = tokenizer.tokenize(TokenKind.RAD, "SecretB")
        assert a != b


class TestVrrpPassphraseRule:
    """Issue #277 — AOS 8 cluster_prof.vrrp_info.vrrp_passphrase is a shared
    key between cluster members. Live captures show it as the deterministic-
    encrypted form (~48 hex chars). Tokenize unconditionally as PSK.
    """

    def test_vrrp_passphrase_tokenizes_as_psk(self) -> None:
        cls, kind = classify_field("vrrp_passphrase", "8590c58ea2da22474eef003b5c4ee6b42524d2e44a631b87")
        assert cls == FieldClassification.TOKENIZE_SECRET
        assert kind == TokenKind.PSK


class TestStructuralWalkerEndToEnd:
    """End-to-end: walking a realistic AOS 8 rad_server response should
    tokenize the rad_key.key shared secret correctly, even when the value
    is short and single-class."""

    def test_rad_server_record_with_short_secret_tokenizes(self) -> None:
        keymap = SessionKeymap()
        tokenizer = Tokenizer(keymap, session_id="test-session-rad", max_entries=100)
        # Mirrors the live shape captured from /v1/configuration/object/rad_server
        data = {
            "_data": {
                "rad_server": [
                    {
                        "rad_server_name": "AG_CPPM_PUB",
                        "rad_host": {"host": "192.168.20.70"},
                        "rad_key": {"key": "protocol"},
                    },
                    {
                        "rad_server_name": "CPPM-PUB",
                        "rad_host": {"host": "192.168.20.70"},
                        "rad_key": {"key": "nowireless4u"},
                    },
                ]
            }
        }
        result = tokenize_response(data, tokenizer)
        records = result["_data"]["rad_server"]

        # Both shared secrets tokenized as RAD — even the short single-class one
        for rec in records:
            secret_token = rec["rad_key"]["key"]
            assert secret_token != rec["rad_key"]["key"][0]  # not cleartext
            match = TOKEN_RE.fullmatch(secret_token)
            assert match is not None
            assert match.group(1) == "RAD"

        # Cleartext secrets must not survive anywhere in the response
        flat = json.dumps(result)
        assert "protocol" not in flat
        assert "nowireless4u" not in flat

        # Hosts tokenized as HOSTNAME (the carve-out from PR #275)
        for rec in records:
            host_token = rec["rad_host"]["host"]
            assert TOKEN_RE.fullmatch(host_token).group(1) == "HOSTNAME"


class TestTokenizer:
    def _make(self, max_entries: int = 100) -> Tokenizer:
        keymap = SessionKeymap()
        return Tokenizer(keymap, session_id="test-session-12345", max_entries=max_entries)

    def test_same_value_same_token(self) -> None:
        tk = self._make()
        a = tk.tokenize(TokenKind.PSK, "Welcome2024!")
        b = tk.tokenize(TokenKind.PSK, "Welcome2024!")
        assert a == b

    def test_different_values_different_tokens(self) -> None:
        tk = self._make()
        a = tk.tokenize(TokenKind.PSK, "First!")
        b = tk.tokenize(TokenKind.PSK, "Second!")
        assert a != b

    def test_same_value_different_kinds_dedups_to_one_token(self) -> None:
        # v3.0.1.12 — kind-agnostic dedup: same plaintext under any kind
        # returns the same token. The first kind to allocate wins the
        # label. Detailed coverage in ``TestKindAgnosticDedup``.
        tk = self._make()
        psk = tk.tokenize(TokenKind.PSK, "shared-value-12345")
        api = tk.tokenize(TokenKind.API_TOKEN, "shared-value-12345")
        assert psk == api
        assert TOKEN_RE.fullmatch(psk).group(1) == "PSK"

    def test_idempotent_on_existing_token(self) -> None:
        tk = self._make()
        token = tk.tokenize(TokenKind.PSK, "abc12345!")
        again = tk.tokenize(TokenKind.PSK, token)
        assert again == token

    def test_empty_or_none_pass_through(self) -> None:
        tk = self._make()
        assert tk.tokenize(TokenKind.PSK, "") == ""
        # Type ignored — runtime should still safely handle.
        assert tk.tokenize(TokenKind.PSK, None) is None  # type: ignore[arg-type]

    def test_detokenize_returns_plaintext(self) -> None:
        tk = self._make()
        token = tk.tokenize(TokenKind.PSK, "Welcome2024!")
        assert tk.detokenize(token) == "Welcome2024!"

    def test_detokenize_unknown_returns_none(self) -> None:
        tk = self._make()
        assert tk.detokenize("[[PSK:ffffffff-ffff-ffff-ffff-ffffffffffff]]") is None

    def test_cap_hit_falls_through(self) -> None:
        tk = self._make(max_entries=2)
        tk.tokenize(TokenKind.PSK, "first1234")
        tk.tokenize(TokenKind.PSK, "second12345")
        # Third allocation should hit the cap. Tokenizer raises;
        # walker layer catches and returns plaintext unchanged.
        from hpe_networking_mcp.redaction.token_store import KeymapFullError

        with pytest.raises(KeymapFullError):
            tk.tokenize(TokenKind.PSK, "third12345")


class TestDetokenizeString:
    def test_replaces_token_in_string(self) -> None:
        keymap = SessionKeymap()
        tk = Tokenizer(keymap, session_id="s", max_entries=10)
        token = tk.tokenize(TokenKind.PSK, "Welcome2024!")
        replaced, unknown = detokenize_string(tk, f"PSK is {token} for site")
        assert "Welcome2024!" in replaced
        assert "[[PSK:" not in replaced
        assert unknown == []

    def test_unknown_token_collected(self) -> None:
        keymap = SessionKeymap()
        tk = Tokenizer(keymap, session_id="s", max_entries=10)
        bogus = "[[PSK:00000000-0000-0000-0000-000000000000]]"
        replaced, unknown = detokenize_string(tk, f"reference {bogus}")
        # Unknown token is preserved in the string (not substituted to garbage)
        assert bogus in replaced
        assert unknown == [bogus]


# ---------------------------------------------------------------------------
# Walker (recursive structure)
# ---------------------------------------------------------------------------


@pytest.fixture
def tokenizer() -> Tokenizer:
    return Tokenizer(SessionKeymap(), session_id="walker-tests", max_entries=1000)


class TestTokenizeResponse:
    def test_psk_in_dict_replaced(self, tokenizer: Tokenizer) -> None:
        result = tokenize_response({"psk": "Welcome2024!"}, tokenizer)
        assert isinstance(result, dict)
        assert result["psk"] != "Welcome2024!"
        assert TOKEN_RE.fullmatch(result["psk"]).group(1) == "PSK"

    def test_nested_psk_replaced(self, tokenizer: Tokenizer) -> None:
        data = {"wlan": {"auth": {"psk": "DeepNested!Pass"}}}
        result = tokenize_response(data, tokenizer)
        assert result["wlan"]["auth"]["psk"] != "DeepNested!Pass"

    def test_list_of_secrets_each_tokenized(self, tokenizer: Tokenizer) -> None:
        data = {"radius_servers": [{"shared_secret": "first1234!"}, {"shared_secret": "second12345!"}]}
        result = tokenize_response(data, tokenizer)
        a = result["radius_servers"][0]["shared_secret"]
        b = result["radius_servers"][1]["shared_secret"]
        assert a != b
        assert TOKEN_RE.fullmatch(a)
        assert TOKEN_RE.fullmatch(b)

    def test_same_psk_same_token(self, tokenizer: Tokenizer) -> None:
        data = {"a": {"psk": "Welcome2024!"}, "b": {"psk": "Welcome2024!"}}
        result = tokenize_response(data, tokenizer)
        assert result["a"]["psk"] == result["b"]["psk"]

    def test_aos8_controller_record_tokenizes_name(self, tokenizer: Tokenizer) -> None:
        """End-to-end regression for issues #235 + #237.

        This is the EXACT shape live ``aos8_get_controllers`` returns —
        captured directly from a real Mobility Conductor. The original
        v2.4.0.5 fixture rigged a ``"firmware"`` key (which IS in
        ``DEVICE_CONTEXT_HINTS``); live AOS 8 returns ``"Version"`` and
        ``"Release Type"`` instead, neither of which were hints — so the
        fix passed unit tests but failed in production. v2.4.0.6 adds
        ``version`` + ``release_type`` to the hint set; this test now
        uses the real shape with no rigging.
        """
        data = {
            "All Switches": [
                {
                    "Config ID": "1728",
                    "Config Sync Time (sec)": "0",
                    "Configuration State": "UPDATE SUCCESSFUL",
                    "IP Address": "192.0.2.21",
                    "IPv6 Address": "None",
                    "Location": "Building1.floor1",
                    "Model": "ArubaMM-VA",
                    "Name": "MM-01",
                    "Release Type": "SSR",
                    "Status": "up",
                    "Type": "conductor",
                    "Version": "8.12.0.5_92330",
                }
            ]
        }
        result = tokenize_response(data, tokenizer)
        record = result["All Switches"][0]
        # Name tokenized — does not equal cleartext, matches HOSTNAME prefix.
        assert record["Name"] != "MM-01"
        match = TOKEN_RE.fullmatch(record["Name"])
        assert match is not None
        assert match.group(1) == "HOSTNAME"
        # IP Address remains cleartext (intentional: IPs not tokenized).
        assert record["IP Address"] == "192.0.2.21"
        # Geographic / model / status fields remain cleartext.
        assert record["Model"] == "ArubaMM-VA"
        assert record["Location"] == "Building1.floor1"

    def test_aos8_aaa_radius_detail_after_flatten_tokenizes_host(self, tokenizer: Tokenizer) -> None:
        """End-to-end regression for issue #235.

        AOS 8 ``show aaa authentication-server radius <name>`` returns a
        transposed key/value table. The ``run_show()`` helper flattens
        ``[{Parameter: k, Value: v}, ...]`` rows into a regular dict
        before the tokenizer sees the response. After flattening, the
        ``Host`` field carries the RADIUS server's IP/FQDN and must be
        tokenized as HOSTNAME — even though general IPs pass through
        per the v2.3.1.2 carve-out, AAA infrastructure is auth-fabric-
        critical (issue #235 carve-out).
        """
        # Post-flatten shape, as run_show() returns it
        flattened = {
            "RADIUS Server ClearPass70": {
                "Host": "192.168.20.70",
                "Key": "********",
                "Auth Port": "1812",
                "NAS IP": "N/A",
            }
        }
        result = tokenize_response(flattened, tokenizer)
        record = result["RADIUS Server ClearPass70"]

        # Host tokenized as HOSTNAME (the issue #235 carve-out)
        assert record["Host"] != "192.168.20.70"
        match = TOKEN_RE.fullmatch(record["Host"])
        assert match is not None
        assert match.group(1) == "HOSTNAME"

        # ``Key: "********"`` is a source-platform-masked placeholder.
        # AOS 8 returns this for any retrieved shared secret — the real
        # value never leaves the controller. The walker MUST NOT tokenize
        # it: a tokenized placeholder creates the dangerous illusion that
        # the AI has a real tokenized secret it can pass to a write tool.
        # Since issue #276 the walker rewrites the masked value to the
        # literal ``REPLACE_ME`` directive — an unambiguous "operator must
        # set this" marker, never a token. Central / AOS 10 would still
        # reject ``REPLACE_ME`` loudly if it were ever committed, and the
        # aos-migration skill is preview-first so it surfaces in the plan.
        assert record["Key"] == "REPLACE_ME"

        # Non-PII config values stay cleartext.
        assert record["Auth Port"] == "1812"
        assert record["NAS IP"] == "N/A"

    def test_aos8_mac_address_with_space_normalized(self, tokenizer: Tokenizer) -> None:
        """AOS 8 ``"MAC Address"`` and ``"Wired MAC Address"`` columns
        should reach the MAC canonicalizer the same as ``mac`` /
        ``wired_mac`` (issue #235)."""
        data = {
            "Mac Address": "AA-BB-CC-DD-EE-FF",
            "Wired MAC Address": "aabb.ccdd.eeff",
        }
        result = tokenize_response(data, tokenizer)
        assert result["Mac Address"] == "aa:bb:cc:dd:ee:ff"
        assert result["Wired MAC Address"] == "aa:bb:cc:dd:ee:ff"

    def test_macs_normalized_not_tokenized(self, tokenizer: Tokenizer) -> None:
        data = {"mac": "AA-BB-CC-DD-EE-FF", "client_mac": "aabb.ccdd.eeff"}
        result = tokenize_response(data, tokenizer)
        assert result["mac"] == "aa:bb:cc:dd:ee:ff"
        assert result["client_mac"] == "aa:bb:cc:dd:ee:ff"
        # No token brackets
        assert "[[" not in result["mac"]
        assert "[[" not in result["client_mac"]

    def test_ips_pass_through_in_all_contexts(self, tokenizer: Tokenizer) -> None:
        # v2.3.1.2: IPs are no longer tokenized anywhere. Internal
        # subnet topology is generally known to anyone on-network; the
        # audit-utility loss outweighs the privacy gain.
        data = {
            "dns_servers": ["8.8.8.8", "1.1.1.1"],
            "wxtag_values": ["10.10.10.0/8", "192.168.0.0/16", "172.16.0.0/12"],
            "description": "Gateway is 10.50.10.1 inside the LAN",
            "wan_ip": "203.0.113.42",
        }
        result = tokenize_response(data, tokenizer)
        assert result["dns_servers"] == ["8.8.8.8", "1.1.1.1"]
        assert result["wxtag_values"] == ["10.10.10.0/8", "192.168.0.0/16", "172.16.0.0/12"]
        assert "10.50.10.1" in result["description"]
        assert result["wan_ip"] == "203.0.113.42"

    def test_email_in_free_text_tokenized(self, tokenizer: Tokenizer) -> None:
        result = tokenize_response(
            {"description": "contact admin@example.com for help"},
            tokenizer,
        )
        assert "admin@example.com" not in result["description"]
        assert "[[EMAIL:" in result["description"]

    def test_email_in_psk_name_field_tokenized(self, tokenizer: Tokenizer) -> None:
        # v2.3.1.2 universal email scan: emails in arbitrary field names
        # (not just `email` and not just free-text fields) get tokenized.
        # Mist's MPSK pattern uses the user's email as the PSK display
        # name — which would have leaked pre-v2.3.1.2.
        result = tokenize_response(
            {"name": "taylor.morgan@example.com", "ssid": "MPSK", "vlan_id": 1},
            tokenizer,
        )
        assert "taylor.morgan@example.com" not in str(result)
        assert "[[EMAIL:" in result["name"]
        assert result["ssid"] == "MPSK"  # SSID still passes through
        assert result["vlan_id"] == 1

    def test_email_in_unknown_field_tokenized(self, tokenizer: Tokenizer) -> None:
        # Field name we've never seen before, value is an email.
        result = tokenize_response({"some_random_field": "user@example.org"}, tokenizer)
        assert "user@example.org" not in str(result)
        assert "[[EMAIL:" in result["some_random_field"]

    def test_aws_signed_url_tokenized(self, tokenizer: Tokenizer) -> None:
        # v2.3.1.2: any value containing AWS Signature v4 credential
        # markers is treated as a temporary AWS credential and
        # tokenized whole as APITOKEN. Placeholders below intentionally
        # don't match the real AWS access-key shape (would trip gitleaks).
        signed_url = (
            "https://example.s3.us-east-1.amazonaws.com/portal_template/"
            "abc.json?X-Amz-Algorithm=AWS4-HMAC-SHA256"
            "&X-Amz-Credential=EXAMPLE_ACCESS_KEY%2F20260429%2Fus-east-1"
            "&X-Amz-Date=20260429T000000Z&X-Amz-Expires=3600"
            "&X-Amz-SignedHeaders=host"
            "&X-Amz-Security-Token=EXAMPLE_SESSION_TOKEN_PLACEHOLDER"
            "&X-Amz-Signature=EXAMPLE_SIGNATURE_HEX_PLACEHOLDER"
        )
        result = tokenize_response({"portal_template_url": signed_url}, tokenizer)
        # Whole URL replaced (partial substitution would still leak the access key)
        assert "X-Amz-Security-Token" not in str(result)
        assert "X-Amz-Credential" not in str(result)
        assert "X-Amz-Signature" not in str(result)
        assert "EXAMPLE_ACCESS_KEY" not in str(result)
        assert TOKEN_RE.fullmatch(result["portal_template_url"]).group(1) == "APITOKEN"

    def test_plain_url_passes_through(self, tokenizer: Tokenizer) -> None:
        # A normal URL without credentials should not match the AWS pattern.
        result = tokenize_response({"portal_url": "https://example.com/path"}, tokenizer)
        assert result["portal_url"] == "https://example.com/path"

    def test_idempotent_walk(self, tokenizer: Tokenizer) -> None:
        once = tokenize_response({"psk": "TwicePassed!"}, tokenizer)
        twice = tokenize_response(once, tokenizer)
        assert once == twice

    def test_mac_normalization_works_without_tokenizer(self) -> None:
        # tokenizer=None means tokenization off but MAC normalization on
        result = tokenize_response({"mac": "AABB.CCDD.EEFF"}, None)
        assert result["mac"] == "aa:bb:cc:dd:ee:ff"

    def test_unknown_fields_pass_through(self, tokenizer: Tokenizer) -> None:
        data = {"channel": 36, "rssi": -55, "ssid_string": "Corp"}
        result = tokenize_response(data, tokenizer)
        # `ssid_string` is NOT in the ruleset (only `ssid`), should pass through
        assert result == data


class TestDetokenizeArguments:
    def test_substitutes_token_in_args(self, tokenizer: Tokenizer) -> None:
        token = tokenizer.tokenize(TokenKind.PSK, "RoundTripMe!")
        args = {"psk": token, "ssid": "static"}
        new_args, unknown = detokenize_arguments(args, tokenizer)
        assert new_args["psk"] == "RoundTripMe!"
        assert new_args["ssid"] == "static"
        assert unknown == []

    def test_unknown_token_returns_in_list(self, tokenizer: Tokenizer) -> None:
        bogus = "[[PSK:00000000-0000-0000-0000-000000000000]]"
        new_args, unknown = detokenize_arguments({"psk": bogus}, tokenizer)
        assert unknown == [bogus]

    def test_token_inside_substring(self, tokenizer: Tokenizer) -> None:
        token = tokenizer.tokenize(TokenKind.PSK, "MyPsk1234!")
        args = {"description": f"WLAN uses {token} for auth"}
        new_args, _ = detokenize_arguments(args, tokenizer)
        assert "MyPsk1234!" in new_args["description"]
        assert "[[PSK:" not in new_args["description"]

    def test_nested_args(self, tokenizer: Tokenizer) -> None:
        # Use HOSTNAME as the kind — SITE was retired in v2.3.1.1 since
        # site IDs are already opaque UUIDs. Hostnames stay tokenized.
        token = tokenizer.tokenize(TokenKind.HOSTNAME, "production-db-01")
        args = {"filters": {"hostname": token}}
        new_args, unknown = detokenize_arguments(args, tokenizer)
        assert new_args["filters"]["hostname"] == "production-db-01"
        assert unknown == []


# ---------------------------------------------------------------------------
# End-to-end fixture: a Mist-shaped WLAN response
# ---------------------------------------------------------------------------


class TestRealisticMistFixture:
    """Walk a redacted-but-realistic Mist WLAN config through the pipeline."""

    @pytest.fixture
    def mist_wlan_response(self) -> dict:
        return {
            "id": "00000000-0000-0000-0000-aaaaaaaaaaaa",
            "site_id": "11111111-1111-1111-1111-bbbbbbbbbbbb",
            "ssid": "Corp-Wifi",
            "auth": {
                "type": "psk",
                "psk": "OurOfficeWifi2024!",
                "wpa3_psk": "OurOfficeWifi2024!",  # same value — should get same token
            },
            "radius_servers": [
                {
                    "host": "10.50.10.10",
                    "port": 1812,
                    "shared_secret": "RadiusSecret123!",
                },
                {
                    "host": "10.50.10.11",
                    "port": 1812,
                    "shared_secret": "RadiusSecret456!",
                },
            ],
            "description": "Tested with admin@corp.com on AP aa-bb-cc-dd-ee-ff at 10.50.10.1",
            "schedule": {"enabled": True, "hours": []},
            "device_name": "AP-Floor3-Conf",
            "client_mac": "AABB.CCDD.EEFF",
            "channel": 36,
            "rssi": -55,
            # MPSK record — Mist uses the user's email as the PSK display name
            "psks": [
                {
                    "id": "abc-123",
                    "name": "user@corp.com",
                    "ssid": "MPSK",
                    "vlan_id": 10,
                },
            ],
            # Mist sometimes returns AWS-signed URLs for portal-template previews.
            # Placeholders below intentionally don't match the real AWS access-key
            # shape (would trip gitleaks).
            "portal_template_url": (
                "https://example.s3.us-east-1.amazonaws.com/portal_template/"
                "abc.json?X-Amz-Algorithm=AWS4-HMAC-SHA256"
                "&X-Amz-Credential=EXAMPLE_ACCESS_KEY%2F20260429%2Fus-east-1"
                "&X-Amz-Security-Token=EXAMPLE_SESSION_TOKEN_PLACEHOLDER"
                "&X-Amz-Signature=EXAMPLE_SIGNATURE_HEX_PLACEHOLDER"
            ),
        }

    def test_full_walk(self, tokenizer: Tokenizer, mist_wlan_response: dict) -> None:
        result = tokenize_response(mist_wlan_response, tokenizer)

        # Tier 1 secrets — tokenized
        assert "OurOfficeWifi2024!" not in str(result)
        assert "RadiusSecret123!" not in str(result)
        assert "RadiusSecret456!" not in str(result)
        # Same value -> same token
        assert result["auth"]["psk"] == result["auth"]["wpa3_psk"]
        # Different secrets -> different tokens
        assert result["radius_servers"][0]["shared_secret"] != result["radius_servers"][1]["shared_secret"]

        # Platform UUIDs — pass through (already opaque, refined in v2.3.1.1)
        assert result["site_id"] == "11111111-1111-1111-1111-bbbbbbbbbbbb"
        assert result["id"] == "00000000-0000-0000-0000-aaaaaaaaaaaa"

        # SSID — passes through (broadcast, refined in v2.3.1.1)
        assert result["ssid"] == "Corp-Wifi"

        # IPs in arbitrary fields — pass through (refined in v2.3.1.2)
        assert "10.50.10.1" in result["description"]  # internal IP in free text

        # ...except `host` in a RADIUS-server context, which IS tokenized
        # (issue #235 carve-out: AAA infrastructure is auth-fabric-critical).
        assert TOKEN_RE.fullmatch(result["radius_servers"][0]["host"]).group(1) == "HOSTNAME"
        assert TOKEN_RE.fullmatch(result["radius_servers"][1]["host"]).group(1) == "HOSTNAME"
        # Different IPs get different tokens (deterministic per session).
        assert result["radius_servers"][0]["host"] != result["radius_servers"][1]["host"]

        # Hostnames — still tokenized (real customer naming pattern)
        assert result["device_name"] != "AP-Floor3-Conf"
        assert TOKEN_RE.fullmatch(result["device_name"]).group(1) == "HOSTNAME"

        # MAC — normalized, NOT tokenized
        assert result["client_mac"] == "aa:bb:cc:dd:ee:ff"
        assert "[[" not in result["client_mac"]

        # Free-text scan — embedded email + MAC handled in description
        assert "admin@corp.com" not in result["description"]
        assert "[[EMAIL:" in result["description"]
        assert "aa:bb:cc:dd:ee:ff" in result["description"]  # MAC normalized in place
        assert "aa-bb-cc-dd-ee-ff" not in result["description"]

        # Universal email scan — PSK with email-as-name (v2.3.1.2)
        assert "user@corp.com" not in str(result)
        assert "[[EMAIL:" in result["psks"][0]["name"]

        # Universal AWS-signed URL scan — whole URL tokenized as APITOKEN (v2.3.1.2)
        assert "X-Amz-Security-Token" not in str(result)
        assert "X-Amz-Credential" not in str(result)
        assert "EXAMPLE_ACCESS_KEY" not in str(result)
        assert TOKEN_RE.fullmatch(result["portal_template_url"]).group(1) == "APITOKEN"

        # Pass-through values preserved
        assert result["channel"] == 36
        assert result["rssi"] == -55
        assert result["schedule"] == {"enabled": True, "hours": []}

    def test_round_trip_secrets(self, tokenizer: Tokenizer, mist_wlan_response: dict) -> None:
        tokenized = tokenize_response(mist_wlan_response, tokenizer)
        psk_token = tokenized["auth"]["psk"]
        # Now imagine the AI passes that token back to a write tool.
        # site_id is now passed through verbatim (no detokenization needed).
        outbound_args = {"site_id": tokenized["site_id"], "psk": psk_token}
        detokenized, unknown = detokenize_arguments(outbound_args, tokenizer)
        assert detokenized["psk"] == "OurOfficeWifi2024!"
        assert detokenized["site_id"] == "11111111-1111-1111-1111-bbbbbbbbbbbb"
        assert unknown == []


# ---------------------------------------------------------------------------
# End-to-end fixture: Central-shaped responses (v2.3.1.3)
# ---------------------------------------------------------------------------


class TestRealisticCentralFixture:
    """Walk Central-shaped tool responses through the pipeline."""

    @pytest.fixture
    def central_wlan_profile_response(self) -> dict:
        # Shape mirrors central_get_wlan_profiles — raw API payload with
        # Central's hyphenated camelCase-derived field names. The
        # personal-security/wpa-passphrase nesting is the leak the
        # v2.3.1.3 hyphen-normalization fixes.
        return {
            "scope_id": "22222222-2222-2222-2222-cccccccccccc",
            "scope_name": "Indianapolis Office",
            "device_group_name": "Indiana Stores",
            "profile_data": {
                "wlan_name": "Corp-Wifi",
                "essid": "Corp-Wifi",
                "personal-security": {
                    "wpa-passphrase": "OurCentralWifi2024!",
                    "wpa-passphrase-mode": "wpa3-personal",
                },
                "auth-server-group": "RadiusGroup-1",
                "vlan_name": "Corporate",
            },
        }

    @pytest.fixture
    def central_audit_log_entry(self) -> dict:
        # Shape mirrors central_get_audit_log_detail
        return {
            "id": "33333333-3333-3333-3333-dddddddddddd",
            "scope_id": "22222222-2222-2222-2222-cccccccccccc",
            "scope_name": "Global",
            "device_group_name": "All Sites",
            "action": "config_update",
            "target_resource": "wlan-profile/Corp-Wifi",
            "user_name": "alice.smith",
            "updated_by": "alice.smith@corp.com",
            "created_by": "automation-bot",
            "created_at": "2026-04-30T10:00:00Z",
            "updated_at": "2026-04-30T10:05:00Z",
        }

    @pytest.fixture
    def central_server_group_response(self) -> dict:
        # Shape mirrors central_get_server_groups — RADIUS server config
        return {
            "name": "RadiusGroup-1",
            "scope_id": "22222222-2222-2222-2222-cccccccccccc",
            "radius_servers": [
                {
                    "host": "10.50.10.10",
                    "port": 1812,
                    "shared-secret": "CentralRadiusSecret123!",
                },
                {
                    "host": "10.50.10.11",
                    "port": 1812,
                    "shared-secret": "CentralRadiusSecret456!",
                },
            ],
        }

    def test_wlan_profile_walk(self, tokenizer: Tokenizer, central_wlan_profile_response: dict) -> None:
        result = tokenize_response(central_wlan_profile_response, tokenizer)

        # Hyphenated PSK field — caught by v2.3.1.3 hyphen normalization
        assert "OurCentralWifi2024!" not in str(result)
        psk_token = result["profile_data"]["personal-security"]["wpa-passphrase"]
        assert TOKEN_RE.fullmatch(psk_token).group(1) == "PSK"

        # Platform UUIDs — pass through (refined v2.3.1.1)
        assert result["scope_id"] == "22222222-2222-2222-2222-cccccccccccc"

        # Central organizational structure — pass through (per v2.3.1.3 design)
        assert result["scope_name"] == "Indianapolis Office"
        assert result["device_group_name"] == "Indiana Stores"

        # SSID family — pass through (broadcast)
        assert result["profile_data"]["wlan_name"] == "Corp-Wifi"
        assert result["profile_data"]["essid"] == "Corp-Wifi"

        # vlan_name — passes through cleartext (v3.0.1.12 privacy-model
        # refinement: schema labels describing network architecture are
        # not personally-identifying and audit utility benefits from
        # cleartext, matching scope_name / device_group_name policy).
        assert result["profile_data"]["vlan_name"] == "Corporate"

    def test_audit_log_user_fields_tokenized(self, tokenizer: Tokenizer, central_audit_log_entry: dict) -> None:
        result = tokenize_response(central_audit_log_entry, tokenizer)

        # New v2.3.1.3 user-identifying fields
        assert result["user_name"] != "alice.smith"
        assert TOKEN_RE.fullmatch(result["user_name"]).group(1) == "USER"
        # updated_by has an email — universal email scan substring-tokenizes
        assert "alice.smith@corp.com" not in str(result)
        assert "[[USER:" in result["updated_by"] or "[[EMAIL:" in result["updated_by"]
        assert result["created_by"] != "automation-bot"
        assert TOKEN_RE.fullmatch(result["created_by"]).group(1) == "USER"

        # Central organizational structure — pass through
        assert result["scope_name"] == "Global"
        assert result["device_group_name"] == "All Sites"

        # Action / target resource / timestamps — pass through (operational metadata)
        assert result["action"] == "config_update"
        assert result["target_resource"] == "wlan-profile/Corp-Wifi"

    def test_server_group_radius_secrets_tokenized(
        self, tokenizer: Tokenizer, central_server_group_response: dict
    ) -> None:
        result = tokenize_response(central_server_group_response, tokenizer)

        # Hyphenated shared-secret — caught by v2.3.1.3 hyphen normalization
        assert "CentralRadiusSecret123!" not in str(result)
        assert "CentralRadiusSecret456!" not in str(result)
        for server in result["radius_servers"]:
            secret_token = server["shared-secret"]
            assert TOKEN_RE.fullmatch(secret_token).group(1) == "RAD"

        # `host` in a RADIUS-server context IS tokenized (issue #235 carve-out:
        # AAA infrastructure is auth-fabric-critical, even though general IPs
        # pass through per v2.3.1.2).
        assert TOKEN_RE.fullmatch(result["radius_servers"][0]["host"]).group(1) == "HOSTNAME"
        assert TOKEN_RE.fullmatch(result["radius_servers"][1]["host"]).group(1) == "HOSTNAME"

        # Different secrets get different tokens
        assert result["radius_servers"][0]["shared-secret"] != result["radius_servers"][1]["shared-secret"]

    def test_round_trip_central_psk(self, tokenizer: Tokenizer, central_wlan_profile_response: dict) -> None:
        # Verify the AI can take a tokenized PSK from a hyphenated-field
        # response and pass it back into a write tool with the same
        # field name.
        tokenized = tokenize_response(central_wlan_profile_response, tokenizer)
        psk_token = tokenized["profile_data"]["personal-security"]["wpa-passphrase"]

        outbound_args = {"profile_data": {"personal-security": {"wpa-passphrase": psk_token}}}
        detokenized, unknown = detokenize_arguments(outbound_args, tokenizer)
        assert detokenized["profile_data"]["personal-security"]["wpa-passphrase"] == "OurCentralWifi2024!"
        assert unknown == []


@pytest.mark.unit
class TestShowCommandOutputSweep:
    """Issue #411 — raw device CLI output returned by show-command tools is
    held as a free-text blob under ``results[].output``. Before the fix that
    field classified ``SKIP`` and only the universal scan (emails / AWS-signed
    URLs) ran over it, so PEM cert/key blocks and MACs embedded in CLI text
    passed through unswept. Classifying ``output`` as a free-text field runs
    the full ``_scan_free_text`` sweep (PEM → email → MAC normalize)."""

    def _tokenizer(self, label: str) -> Tokenizer:
        return Tokenizer(SessionKeymap(), session_id=f"test-session-411-{label}", max_entries=100)

    def test_output_field_classifies_scan_free_text(self) -> None:
        cls, kind = classify_field("output", "some show command text")
        assert cls == FieldClassification.SCAN_FREE_TEXT
        assert kind is None

    def test_pem_block_in_show_output_is_tokenized(self) -> None:
        tokenizer = self._tokenizer("pem")
        pem = "-----BEGIN CERTIFICATE-----\nMIIBfakecertdata1234567890ABCDEF\n-----END CERTIFICATE-----"
        response = {"results": [{"command": "show crypto pki certificate", "output": f"Certificate:\n{pem}\n"}]}
        out = tokenize_response(response, tokenizer)
        swept = out["results"][0]["output"]
        # The PEM block is tokenized as CERT and no raw markers remain.
        assert "BEGIN CERTIFICATE" not in swept
        assert TOKEN_RE.search(swept).group(1) == "CERT"

    def test_email_in_show_output_is_tokenized(self) -> None:
        tokenizer = self._tokenizer("email")
        response = {"results": [{"command": "show run", "output": "snmp-server contact admin@example.com"}]}
        out = tokenize_response(response, tokenizer)
        swept = out["results"][0]["output"]
        assert "admin@example.com" not in swept
        assert TOKEN_RE.search(swept).group(1) == "EMAIL"

    def test_mac_in_show_output_is_normalized(self) -> None:
        tokenizer = self._tokenizer("mac")
        # Uppercase / dotted MAC in a CLI blob is normalized to canonical form
        # (MACs are normalize-only, never tokenized — per the v2.3.0.10 design).
        response = {"results": [{"command": "show mac-address", "output": "port 1/1/1  AABB.CCDD.EEFF  vlan 10"}]}
        out = tokenize_response(response, tokenizer)
        swept = out["results"][0]["output"]
        assert "aa:bb:cc:dd:ee:ff" in swept
        assert "AABB.CCDD.EEFF" not in swept
