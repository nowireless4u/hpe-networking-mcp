"""Regression tests for cleartext that escaped the tokenizer by hiding inside
a larger string, and for over-masking that destroyed legible data.

All three behaviors below were found during testing against a live tenant. They
share one root cause: the keymap replay matched a value only when the value was
a known plaintext *in its entirety*, so anything concatenated around it (a path
prefix, or serialization into a blob) slipped through — while the exact-match
secret path in the other direction masked whatever sat under a certificate-ish
key regardless of shape.

The leaks matter more than they look: the same identifier is tokenized when it
appears under its own key, so leaving it cleartext elsewhere in the *same*
response lets a reader undo the masking by correlation.
"""

from __future__ import annotations

import json

import pytest

from hpe_networking_mcp.redaction.rules import TokenKind, looks_like_certificate
from hpe_networking_mcp.redaction.token_store import SessionKeymap
from hpe_networking_mcp.redaction.tokenizer import Tokenizer
from hpe_networking_mcp.redaction.walker import tokenize_response

pytestmark = pytest.mark.unit


def _tokenizer() -> Tokenizer:
    return Tokenizer(SessionKeymap(), session_id="test-session", max_entries=1000)


class TestEmbeddedCleartextReplay:
    def test_prefixed_value_is_masked(self):
        """``management-users/<user>`` kept the username cleartext because the
        whole-string match failed on the prefix."""
        tok = _tokenizer()
        token = tok.tokenize(TokenKind.USER, "ArubaAdmin")

        out = tok.replace_known_cleartext("management-users/ArubaAdmin")

        assert out == f"management-users/{token}"
        assert "ArubaAdmin" not in out

    def test_value_inside_stringified_blob_is_masked(self):
        tok = _tokenizer()
        token = tok.tokenize(TokenKind.SERIAL, "AB12345678")

        blob = "[{'scope_type': 'DEVICE', 'scope_name': 'AB12345678'}]"
        out = tok.replace_known_cleartext(blob)

        assert token in out
        assert "AB12345678" not in out

    def test_does_not_fire_inside_a_longer_word(self):
        """Word-bounded: a known plaintext must not corrupt a longer identifier
        that merely contains it."""
        tok = _tokenizer()
        tok.tokenize(TokenKind.USER, "admin1")

        out = tok.replace_known_cleartext("admin1234 and admin1x")

        assert out == "admin1234 and admin1x"

    def test_separators_still_count_as_boundaries(self):
        tok = _tokenizer()
        token = tok.tokenize(TokenKind.SERIAL, "AB12345678")

        for wrapped in (
            "'AB12345678'",
            '"AB12345678"',
            "AB12345678 / MOBILITY_GW",
            "path/AB12345678,next",
        ):
            assert token in tok.replace_known_cleartext(wrapped), wrapped

    def test_short_plaintexts_are_not_replayed_into_text(self):
        """Below the length floor, substituting inside arbitrary text does more
        damage than the leak it prevents."""
        tok = _tokenizer()
        tok.tokenize(TokenKind.USER, "bob")

        out = tok.replace_known_cleartext("bob logged in")

        assert out == "bob logged in"

    def test_unknown_value_is_untouched(self):
        tok = _tokenizer()
        tok.tokenize(TokenKind.SERIAL, "AB12345678")

        assert tok.replace_known_cleartext("nothing to see here") == "nothing to see here"

    def test_existing_token_is_not_double_tokenized(self):
        tok = _tokenizer()
        token = tok.tokenize(TokenKind.SERIAL, "AB12345678")

        assert tok.replace_known_cleartext(token) == token

    def test_longest_match_wins(self):
        """When one plaintext contains another, the more specific one must win."""
        tok = _tokenizer()
        tok.tokenize(TokenKind.USER, "service")
        long_token = tok.tokenize(TokenKind.USER, "service-account")

        out = tok.replace_known_cleartext("user=service-account")

        assert out == f"user={long_token}"

    def test_pattern_cache_refreshes_as_keymap_grows(self):
        tok = _tokenizer()
        tok.tokenize(TokenKind.USER, "firstuser")
        assert "firstuser" not in tok.replace_known_cleartext("id=firstuser")

        second = tok.tokenize(TokenKind.USER, "seconduser")
        out = tok.replace_known_cleartext("id=seconduser")
        assert out == f"id={second}", "pattern must be rebuilt when the keymap grows"


class TestScopeAnnotationBlob:
    """Central returns scope_device_function as a *string* of records, so the
    walker sees one opaque value and never reaches the identifiers inside."""

    _JSON_BLOB = json.dumps(
        [
            {"device_function": "MOBILITY_GW", "scope_type": "DEVICE", "scope_name": "AB12345678"},
            {"device_function": "MOBILITY_GW", "scope_type": "SITE", "scope_name": "Branch-1"},
        ]
    )
    _REPR_BLOB = "[{'scope_type': 'DEVICE', 'scope_name': 'AB12345678', 'device_function': 'MOBILITY_GW'}]"

    def test_device_scope_name_is_tokenized(self):
        """A DEVICE scope is named by its serial, which is masked elsewhere."""
        tok = _tokenizer()
        payload = {"@": {"aruba-annotation:scope_device_function": self._JSON_BLOB}}

        out = tokenize_response(payload, tok)

        blob = out["@"]["aruba-annotation:scope_device_function"]
        assert "AB12345678" not in blob
        assert "[[SERIAL:" in blob

    def test_python_repr_serialization_is_handled(self):
        """Central emits this annotation as a Python repr as well as JSON."""
        tok = _tokenizer()
        payload = {"@": {"aruba-annotation:scope_device_function": self._REPR_BLOB}}

        out = tokenize_response(payload, tok)

        blob = out["@"]["aruba-annotation:scope_device_function"]
        assert "AB12345678" not in blob
        assert "[[SERIAL:" in blob

    def test_site_and_group_names_stay_cleartext(self):
        """The privacy model deliberately passes architecture labels through;
        this fix must not widen masking beyond the device identifier."""
        tok = _tokenizer()
        payload = {"@": {"aruba-annotation:scope_device_function": self._JSON_BLOB}}

        out = tokenize_response(payload, tok)

        assert "Branch-1" in out["@"]["aruba-annotation:scope_device_function"]

    def test_serial_dedupes_with_the_same_serial_elsewhere(self):
        """The whole point: one device, one token, however it is reached."""
        tok = _tokenizer()
        payload = {
            "device": {"serial": "AB12345678", "model": "AP-635"},
            "@": {"aruba-annotation:scope_device_function": self._JSON_BLOB},
        }

        out = tokenize_response(payload, tok)

        assert out["device"]["serial"] == "[[SERIAL:" + out["device"]["serial"].split(":", 1)[1]
        assert out["device"]["serial"] in out["@"]["aruba-annotation:scope_device_function"]

    def test_unparseable_blob_is_left_alone(self):
        tok = _tokenizer()
        payload = {"@": {"aruba-annotation:scope_device_function": "[not valid at all"}}

        out = tokenize_response(payload, tok)

        assert out["@"]["aruba-annotation:scope_device_function"] == "[not valid at all"

    def test_blob_without_device_scope_is_byte_identical(self):
        """No masking needed → keep the upstream serialization untouched."""
        tok = _tokenizer()
        blob = json.dumps([{"scope_type": "SITE", "scope_name": "Branch-1"}])
        payload = {"@": {"aruba-annotation:scope_device_function": blob}}

        out = tokenize_response(payload, tok)

        assert out["@"]["aruba-annotation:scope_device_function"] == blob


class TestCertificateOverMasking:
    """TokenKind.CERT exists for PEM blocks, but its field names are ordinary
    words, so short scalars that merely reused the key were masked."""

    def test_short_scalar_under_cert_key_is_not_masked(self):
        tok = _tokenizer()

        out = tokenize_response({"certificate": "list"}, tok)

        assert out["certificate"] == "list"

    def test_certificate_name_stays_legible(self):
        tok = _tokenizer()

        out = tokenize_response({"certificate": "Guest-Portal-Cert"}, tok)

        assert out["certificate"] == "Guest-Portal-Cert"

    def test_pem_material_is_still_masked(self):
        tok = _tokenizer()
        pem = "-----BEGIN CERTIFICATE-----\nMIIBIjANBgkqhki\n-----END CERTIFICATE-----"

        out = tokenize_response({"certificate": pem}, tok)

        assert out["certificate"].startswith("[[CERT:")

    def test_long_opaque_blob_is_still_masked(self):
        """Bias toward masking: an unarmored long blob under a cert key is far
        more likely payload than label."""
        tok = _tokenizer()
        blob = "MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA1234567890abcdefXYZ"

        out = tokenize_response({"certificate": blob}, tok)

        assert out["certificate"].startswith("[[CERT:")

    def test_other_secret_kinds_keep_firing_unconditionally(self):
        """The shape gate is CERT-only — a short PSK must still be masked."""
        tok = _tokenizer()

        out = tokenize_response({"wpa-passphrase": "short1"}, tok)

        assert out["wpa-passphrase"].startswith("[[PSK:")

    @pytest.mark.parametrize(
        ("value", "expected"),
        [
            ("list", False),
            ("", False),
            ("Guest-Portal-Cert", False),
            ("-----BEGIN CERTIFICATE-----\nabc\n-----END CERTIFICATE-----", True),
            ("ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQ", True),
            ("A" * 40, True),
        ],
    )
    def test_looks_like_certificate(self, value, expected):
        assert looks_like_certificate(value) is expected
