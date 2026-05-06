"""Unit tests for the shared ClearPass utility helpers.

Pins the contract for ``build_query_string`` after consolidating ten
file-local copies into ``platforms/clearpass/utils.py`` (issue #125).
"""

from __future__ import annotations

import pytest

from hpe_networking_mcp.platforms.clearpass.utils import build_query_string

pytestmark = pytest.mark.unit


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
