"""Unit tests for the PII tokenization + MAC normalization layer."""

from __future__ import annotations

import re

import pytest

from hpe_networking_mcp.redaction.mac_normalizer import (
    canonicalize_mac,
    is_mac_address,
    normalize_macs_in_value,
)
from hpe_networking_mcp.redaction.rules import (
    TOKEN_RE,
    FieldClassification,
    TokenKind,
    classify_field,
    is_known_enum_value,
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
        a, _ = classify_field("IP Address", "172.23.4.21")
        b, _ = classify_field("ip-address", "172.23.4.21")
        c, _ = classify_field("ip_address", "172.23.4.21")
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
        identifier is just ``"Name"``, with siblings ``"Model"`` and
        (effectively) ``"firmware"`` via ``"Version"``. The bare-``name``
        heuristic must accept space-separated sibling keys after
        normalization (issue #235)."""
        cls, kind = classify_field(
            "Name",
            "MM-01",
            parent_keys=frozenset(
                {
                    "Config ID",
                    "IP Address",
                    "Model",
                    "Name",
                    "Status",
                    "Type",
                    "firmware",
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
        assert kind == TokenKind.RADSEC

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
        assert kind == TokenKind.RADSEC


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

    def test_different_kinds_different_tokens_for_same_value(self) -> None:
        tk = self._make()
        psk = tk.tokenize(TokenKind.PSK, "shared-value-12345")
        api = tk.tokenize(TokenKind.API_TOKEN, "shared-value-12345")
        assert psk != api
        assert TOKEN_RE.fullmatch(psk).group(1) == "PSK"
        assert TOKEN_RE.fullmatch(api).group(1) == "APITOKEN"

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
        """End-to-end regression for issue #235.

        This is the exact shape live ``aos8_get_controllers`` returns:
        space-separated keys, ``"Name"`` as the controller identifier,
        ``"Model"`` as a device-context sibling, ``"Version"`` (which
        normalizes alongside but isn't a context hint by itself). With
        the fix, ``"Name"`` tokenizes as HOSTNAME because ``Model``
        + ``firmware``-equivalent siblings are now matched after the
        space normalization.
        """
        data = {
            "All Switches": [
                {
                    "Config ID": "1728",
                    "Configuration State": "UPDATE SUCCESSFUL",
                    "IP Address": "172.23.4.21",
                    "Location": "Building1.floor1",
                    "Model": "ArubaMM-VA",
                    "Name": "MM-01",
                    "Status": "up",
                    "Type": "conductor",
                    "firmware": "8.12.0.5",
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
        assert record["IP Address"] == "172.23.4.21"
        # Geographic / model / status fields remain cleartext.
        assert record["Model"] == "ArubaMM-VA"
        assert record["Location"] == "Building1.floor1"

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
            {"name": "travis.knapp@burninlab.com", "ssid": "MPSK", "vlan_id": 1},
            tokenizer,
        )
        assert "travis.knapp@burninlab.com" not in str(result)
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

        # IPs — pass through everywhere (refined in v2.3.1.2)
        assert result["radius_servers"][0]["host"] == "10.50.10.10"
        assert result["radius_servers"][1]["host"] == "10.50.10.11"
        assert "10.50.10.1" in result["description"]  # internal IP in free text

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

        # vlan_name — still tokenized as NAME
        assert result["profile_data"]["vlan_name"] != "Corporate"
        assert TOKEN_RE.fullmatch(result["profile_data"]["vlan_name"]).group(1) == "NAME"

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
            assert TOKEN_RE.fullmatch(secret_token).group(1) == "RADSEC"

        # IPs — pass through everywhere (v2.3.1.2)
        assert result["radius_servers"][0]["host"] == "10.50.10.10"
        assert result["radius_servers"][1]["host"] == "10.50.10.11"

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
