"""Unit tests for hpe_networking_mcp.platforms.mist.client — response formatting."""

from unittest.mock import MagicMock

import pytest

from hpe_networking_mcp.platforms.mist.client import _get_total, format_response_data


# ---------------------------------------------------------------------------
# Helper — mock APIResponse
# ---------------------------------------------------------------------------


class MockAPIResponse:
    """Lightweight stand-in for mistapi.__api_response.APIResponse."""

    def __init__(
        self,
        data=None,
        headers=None,
        next_page=None,
        status_code=200,
    ):
        self.data = data
        self.headers = headers or {}
        self.next = next_page
        self.status_code = status_code


# ---------------------------------------------------------------------------
# _get_total
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestGetTotal:
    def test_extracts_from_x_page_total_header(self):
        resp = MockAPIResponse(data=[], headers={"X-Page-Total": "42"})
        assert _get_total(resp) == 42

    def test_extracts_from_response_data_total(self):
        resp = MockAPIResponse(data={"total": 99, "results": []})
        assert _get_total(resp) == 99

    def test_returns_none_when_no_total_available(self):
        resp = MockAPIResponse(data=[{"id": "abc"}])
        assert _get_total(resp) is None

    def test_header_takes_precedence_over_data_total(self):
        resp = MockAPIResponse(
            data={"total": 10, "results": []},
            headers={"X-Page-Total": "20"},
        )
        assert _get_total(resp) == 20

    def test_returns_none_for_invalid_header_value(self):
        resp = MockAPIResponse(data=[], headers={"X-Page-Total": "not-a-number"})
        assert _get_total(resp) is None

    def test_returns_none_for_empty_headers(self):
        resp = MockAPIResponse(data={"items": []}, headers={})
        assert _get_total(resp) is None

    def test_returns_none_for_none_headers(self):
        resp = MockAPIResponse(data=[], headers=None)
        assert _get_total(resp) is None


# ---------------------------------------------------------------------------
# format_response_data
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestFormatResponseData:
    def test_list_data_with_next_page(self):
        resp = MockAPIResponse(
            data=[{"id": "1"}, {"id": "2"}],
            next_page="/api/v1/things?page=2",
            headers={"X-Page-Total": "10"},
        )
        result = format_response_data(resp)
        assert result["results"] == [{"id": "1"}, {"id": "2"}]
        assert result["next"] == "/api/v1/things?page=2"
        assert result["has_more"] is True
        assert result["total"] == 10

    def test_dict_data_with_next_page(self):
        resp = MockAPIResponse(
            data={"results": [{"id": "1"}], "extra": "value"},
            next_page="/api/v1/things?page=2",
        )
        result = format_response_data(resp)
        assert result["next"] == "/api/v1/things?page=2"
        assert result["has_more"] is True
        assert result["results"] == [{"id": "1"}]
        assert result["extra"] == "value"

    def test_dict_data_without_next_page(self):
        resp = MockAPIResponse(data={"results": [{"id": "1"}]})
        result = format_response_data(resp)
        assert result["has_more"] is False
        assert "next" not in result

    def test_list_data_without_next_page(self):
        """List data with no next page is returned as-is (no wrapping)."""
        resp = MockAPIResponse(data=[{"id": "1"}])
        result = format_response_data(resp)
        # No next page and data is a list -- returned unchanged
        assert result == [{"id": "1"}]

    def test_dict_data_preserves_existing_total(self):
        """When data dict already has 'total', format_response_data does not overwrite it."""
        resp = MockAPIResponse(
            data={"results": [], "total": 50},
            next_page="/next",
            headers={"X-Page-Total": "100"},
        )
        result = format_response_data(resp)
        # The code only sets total if "total" not in data
        assert result["total"] == 50

    def test_list_data_with_next_page_no_total(self):
        resp = MockAPIResponse(
            data=[{"id": "1"}],
            next_page="/next",
        )
        result = format_response_data(resp)
        assert result["has_more"] is True
        assert "total" not in result
