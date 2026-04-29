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
    PUBLIC_IP_ALLOWLIST,
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

    def test_macs_normalized_not_tokenized(self, tokenizer: Tokenizer) -> None:
        data = {"mac": "AA-BB-CC-DD-EE-FF", "client_mac": "aabb.ccdd.eeff"}
        result = tokenize_response(data, tokenizer)
        assert result["mac"] == "aa:bb:cc:dd:ee:ff"
        assert result["client_mac"] == "aa:bb:cc:dd:ee:ff"
        # No token brackets
        assert "[[" not in result["mac"]
        assert "[[" not in result["client_mac"]

    def test_public_dns_ip_preserved(self, tokenizer: Tokenizer) -> None:
        data = {"dns_servers": ["8.8.8.8", "1.1.1.1"]}
        # IP isn't in a tokenized field name (`dns_servers` isn't in the
        # ruleset) so it passes through. But also test that even *if* the
        # field name caused tokenization, the public allowlist would skip:
        result = tokenize_response({"ip": "8.8.8.8"}, tokenizer)
        assert result == {"ip": "8.8.8.8"}
        # And confirm the public allowlist entry is intact
        assert "8.8.8.8" in PUBLIC_IP_ALLOWLIST
        assert data["dns_servers"] == ["8.8.8.8", "1.1.1.1"]

    def test_internal_ip_tokenized_in_known_field(self, tokenizer: Tokenizer) -> None:
        # `ip` in PUBLIC_IP_ALLOWLIST is preserved, but a corporate IP isn't.
        # We use a field that maps to TokenKind.IP via the rules. Right now
        # `ip` is not in the identifier ruleset directly — IPs are tokenized
        # via free-text scan. So test in that path:
        data = {"description": "Gateway is 10.50.10.1 inside the LAN"}
        result = tokenize_response(data, tokenizer)
        assert "10.50.10.1" not in result["description"]
        # Public IPs in free text are preserved
        data2 = {"description": "Tested with DNS 8.8.8.8 and 1.1.1.1"}
        result2 = tokenize_response(data2, tokenizer)
        assert "8.8.8.8" in result2["description"]
        assert "1.1.1.1" in result2["description"]

    def test_email_in_free_text_tokenized(self, tokenizer: Tokenizer) -> None:
        result = tokenize_response(
            {"description": "contact admin@example.com for help"},
            tokenizer,
        )
        assert "admin@example.com" not in result["description"]
        assert "[[EMAIL:" in result["description"]

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
            "description": "Tested with admin@corp.com on AP aa-bb-cc-dd-ee-ff",
            "schedule": {"enabled": True, "hours": []},
            "device_name": "AP-Floor3-Conf",
            "client_mac": "AABB.CCDD.EEFF",
            "channel": 36,
            "rssi": -55,
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
