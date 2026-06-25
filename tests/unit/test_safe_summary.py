"""Unit tests for the shared secret-safe summarizer (#523/#534)."""

from __future__ import annotations

import pytest

from hpe_networking_mcp.redaction.safe_summary import (
    REDACTED,
    is_sensitive_key,
    safe_value_summary,
    summarize_validation_errors,
)

pytestmark = pytest.mark.unit


class TestIsSensitiveKey:
    @pytest.mark.parametrize(
        "key",
        ["password", "secret", "api_key", "apiKey", "api-key", "clientSecret", "radiusSharedSecret", "psk", "token"],
    )
    def test_sensitive(self, key: str) -> None:
        assert is_sensitive_key(key) is True

    @pytest.mark.parametrize("key", ["org_id", "site_name", "ssid", "vlan", "hostname", "limit"])
    def test_not_sensitive(self, key: str) -> None:
        assert is_sensitive_key(key) is False


class TestSafeValueSummary:
    def test_sensitive_field_redacts_value(self) -> None:
        assert safe_value_summary("hunter2", field_name="password") == REDACTED

    def test_dict_summarized_by_shape(self) -> None:
        assert safe_value_summary({"a": 1, "b": 2}, field_name="payload") == "<dict: 2 field(s)>"

    def test_list_summarized_by_shape(self) -> None:
        assert safe_value_summary([1, 2, 3], field_name="items") == "<list: 3 item(s)>"

    def test_long_scalar_capped(self) -> None:
        out = safe_value_summary("x" * 500, field_name="note", max_len=50)
        assert len(out) <= 50
        assert out.endswith("…")

    def test_short_scalar_passes_through(self) -> None:
        assert safe_value_summary(42, field_name="count") == "42"


class TestSummarizeValidationErrors:
    def test_redacts_sensitive_field_value(self) -> None:
        errors = [{"loc": ("password",), "msg": "Input should be valid", "input": "supersecret-value"}]
        out = summarize_validation_errors("central_invoke_tool", errors)
        assert "supersecret-value" not in out
        assert REDACTED in out
        assert "central_invoke_tool" in out

    def test_summarizes_complex_input(self) -> None:
        errors = [{"loc": ("payload",), "msg": "x", "input": {"a": 1, "b": 2, "c": 3}}]
        out = summarize_validation_errors("t", errors)
        assert "<dict: 3 field(s)>" in out

    def test_no_input_key_omits_got(self) -> None:
        errors = [{"loc": ("org_id",), "msg": "Field required"}]
        out = summarize_validation_errors("t", errors)
        assert "got:" not in out
        assert "org_id: Field required" in out
