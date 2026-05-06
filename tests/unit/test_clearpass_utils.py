"""Unit tests for the shared ClearPass utility helpers.

Pins the contract for ``build_query_string`` (consolidated from 10 file-local
copies in issue #125) and ``clearpass_get`` (the centralized wrapper around
pyclearpass's private ``_send_request`` method, issue #126).
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from hpe_networking_mcp.platforms.clearpass.utils import (
    build_query_string,
    clearpass_get,
)

pytestmark = pytest.mark.unit


class TestClearPassGet:
    def test_delegates_to_send_request_with_get_method(self):
        client = MagicMock()
        client._send_request.return_value = {"items": []}
        result = clearpass_get(client, "/network-device?offset=0&limit=25")
        client._send_request.assert_called_once_with("/network-device?offset=0&limit=25", "get")
        assert result == {"items": []}

    def test_passes_path_through_unchanged(self):
        client = MagicMock()
        clearpass_get(client, "/cert-trust-list/42")
        # Single-item lookups (no query string) work the same way.
        client._send_request.assert_called_once_with("/cert-trust-list/42", "get")

    def test_returns_whatever_the_sdk_returns(self):
        client = MagicMock()
        sentinel = object()
        client._send_request.return_value = sentinel
        assert clearpass_get(client, "/anything") is sentinel


class TestBuildQueryString:
    def test_defaults_emit_offset_limit_and_calculate_count(self):
        assert build_query_string() == "?offset=0&limit=25&calculate_count=false"

    def test_filter_included_when_provided(self):
        result = build_query_string(filter='{"name":"foo"}')
        assert 'filter={"name":"foo"}' in result
        assert result.startswith("?filter=")

    def test_filter_omitted_when_none(self):
        assert "filter=" not in build_query_string()

    def test_sort_included_when_provided(self):
        result = build_query_string(sort="+name")
        assert "sort=+name" in result

    def test_calculate_count_true_lowercases_to_true(self):
        assert "calculate_count=true" in build_query_string(calculate_count=True)

    def test_calculate_count_false_lowercases_to_false(self):
        assert "calculate_count=false" in build_query_string(calculate_count=False)

    def test_offset_and_limit_respect_provided_values(self):
        result = build_query_string(offset=50, limit=100)
        assert "offset=50" in result
        assert "limit=100" in result

    def test_full_query_string_orders_filter_sort_offset_limit_count(self):
        result = build_query_string(filter='{"x":1}', sort="-id", offset=10, limit=5, calculate_count=True)
        assert result == '?filter={"x":1}&sort=-id&offset=10&limit=5&calculate_count=true'
