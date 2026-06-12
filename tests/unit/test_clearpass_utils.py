"""Unit tests for the shared ClearPass utility helpers.

Pins the contract for ``build_query_string`` (consolidated from 10 file-local
copies in issue #125) and ``clearpass_get`` (the centralized GET wrapper —
formerly around pyclearpass's ``_send_request``, now around
``ClearPassClient.request``; the isolation from issue #126 made the SDK
removal a one-function change).
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from hpe_networking_mcp.platforms.clearpass.utils import (
    build_query_string,
    clearpass_get,
)

pytestmark = pytest.mark.unit


class TestClearPassGet:
    async def test_delegates_to_client_request_with_get_method(self):
        client = MagicMock()
        client.request = AsyncMock(return_value={"items": []})
        result = await clearpass_get(client, "/network-device?offset=0&limit=25")
        client.request.assert_awaited_once_with("get", "/network-device?offset=0&limit=25")
        assert result == {"items": []}

    async def test_passes_path_through_unchanged(self):
        client = MagicMock()
        client.request = AsyncMock(return_value={})
        await clearpass_get(client, "/cert-trust-list/42")
        # Single-item lookups (no query string) work the same way.
        client.request.assert_awaited_once_with("get", "/cert-trust-list/42")

    async def test_returns_whatever_the_client_returns(self):
        client = MagicMock()
        sentinel = object()
        client.request = AsyncMock(return_value=sentinel)
        assert await clearpass_get(client, "/anything") is sentinel


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
