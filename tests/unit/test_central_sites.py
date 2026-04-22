"""Unit tests for central sites tool helpers.

Covers the ``normalize_site_name_filter`` helper introduced for issue #146:
the ``central_get_site_health`` tool accepts either a single string or a list
of strings so LLMs pattern-matching against peer Central tools (which all use
singular ``site_name``) don't get tripped up.
"""

from __future__ import annotations

import pytest

from hpe_networking_mcp.platforms.central.utils import normalize_site_name_filter


@pytest.mark.unit
class TestNormalizeSiteNameFilter:
    def test_none_stays_none(self):
        assert normalize_site_name_filter(None) is None

    def test_single_string_wraps_in_list(self):
        assert normalize_site_name_filter("Owls Nest") == ["Owls Nest"]

    def test_single_string_with_special_chars_preserved(self):
        assert normalize_site_name_filter("Owls Nest New Central") == ["Owls Nest New Central"]

    def test_list_passes_through_as_list(self):
        assert normalize_site_name_filter(["A", "B"]) == ["A", "B"]

    def test_single_element_list_stays_list(self):
        assert normalize_site_name_filter(["Solo"]) == ["Solo"]

    def test_empty_list_returns_empty_list(self):
        # An empty list is not None — caller decides whether to return all sites
        # or no sites. The helper preserves that distinction.
        assert normalize_site_name_filter([]) == []

    def test_tuple_coerced_to_list(self):
        assert normalize_site_name_filter(("A", "B")) == ["A", "B"]
