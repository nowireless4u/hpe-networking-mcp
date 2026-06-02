# (c) Copyright 2025 Hewlett Packard Enterprise Development LP
"""Unit tests for hpe_networking_mcp.platforms.greenlake.tools._bulk_enrichment."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from hpe_networking_mcp.platforms.greenlake.tools._bulk_enrichment import (
    _enrich_for_row,
    _parse_tags_to_dict,
    _patch_enrich_location,
    _patch_enrich_tags,
)

pytestmark = pytest.mark.unit


# ---------------------------------------------------------------------------
# TestParseTags
# ---------------------------------------------------------------------------


class TestParseTags:
    def test_splits_on_comma(self) -> None:
        """Comma-separated tags must be split into a dict with empty-string values."""
        result = _parse_tags_to_dict("wlan, floor3, us-west")
        assert result == {"wlan": "", "floor3": "", "us-west": ""}

    def test_drops_empty_elements(self) -> None:
        """Double commas must not produce empty-string keys."""
        result = _parse_tags_to_dict("wlan,,floor3")
        assert len(result) == 2
        assert "wlan" in result
        assert "floor3" in result

    def test_strips_whitespace(self) -> None:
        """Leading/trailing whitespace around tag names must be stripped."""
        result = _parse_tags_to_dict("  tag1  ,  tag2  ")
        assert "tag1" in result
        assert "tag2" in result

    def test_returns_empty_dict_for_blank(self) -> None:
        """Whitespace-only input must return an empty dict."""
        result = _parse_tags_to_dict("   ")
        assert result == {}

    def test_values_are_empty_strings(self) -> None:
        """Each tag name must map to an empty string value (not None or bool)."""
        result = _parse_tags_to_dict("wlan")
        assert result == {"wlan": ""}


# ---------------------------------------------------------------------------
# TestPatchEnrichLocation
# ---------------------------------------------------------------------------


class TestPatchEnrichLocation:
    async def test_returns_succeeded_on_successful_poll(self) -> None:
        """202 + Location header + SUCCEEDED poll → ('succeeded', None)."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 202
        mock_response.headers = {"location": "/devices/v2beta1/async-operations/op-1"}
        mock_client.patch_raw = AsyncMock(return_value=mock_response)
        with patch(
            "hpe_networking_mcp.platforms.greenlake.tools.bulk_add._poll_async_operation",
            new=AsyncMock(return_value={"status": "SUCCEEDED"}),
        ):
            status, reason = await _patch_enrich_location(mock_client, "dev-uuid-1", "loc-uuid-1")
        assert status == "succeeded"
        assert reason is None

    async def test_returns_failed_on_non_202(self) -> None:
        """Non-202 status → ('failed', reason containing status code)."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 422
        mock_response.text = "bad request"
        mock_client.patch_raw = AsyncMock(return_value=mock_response)
        status, reason = await _patch_enrich_location(mock_client, "dev-uuid-1", "loc-uuid-1")
        assert status == "failed"
        assert reason is not None
        assert "422" in reason

    async def test_uses_merge_patch_content_type(self) -> None:
        """PATCH must include Content-Type: application/merge-patch+json."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 202
        mock_response.headers = {"location": "/devices/v2beta1/async-operations/op-1"}
        mock_client.patch_raw = AsyncMock(return_value=mock_response)
        with patch(
            "hpe_networking_mcp.platforms.greenlake.tools.bulk_add._poll_async_operation",
            new=AsyncMock(return_value={"status": "SUCCEEDED"}),
        ):
            await _patch_enrich_location(mock_client, "dev-uuid-1", "loc-uuid-1")
        call_kwargs = mock_client.patch_raw.call_args
        headers = call_kwargs.kwargs.get("additional_headers") or {}
        assert headers.get("Content-Type") == "application/merge-patch+json"

    async def test_body_format(self) -> None:
        """PATCH body must be {'location': {'id': location_uuid}}."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 202
        mock_response.headers = {"location": "/devices/v2beta1/async-operations/op-1"}
        mock_client.patch_raw = AsyncMock(return_value=mock_response)
        with patch(
            "hpe_networking_mcp.platforms.greenlake.tools.bulk_add._poll_async_operation",
            new=AsyncMock(return_value={"status": "SUCCEEDED"}),
        ):
            await _patch_enrich_location(mock_client, "dev-uuid-1", "loc-uuid-1")
        call_kwargs = mock_client.patch_raw.call_args
        body = call_kwargs.kwargs.get("data") or {}
        assert body == {"location": {"id": "loc-uuid-1"}}

    async def test_endpoint_uses_v2beta1_with_uuid_query_param(self) -> None:
        """Endpoint must be /devices/v2beta1/devices with id passed as params dict."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 202
        mock_response.headers = {"location": "/devices/v2beta1/async-operations/op-1"}
        mock_client.patch_raw = AsyncMock(return_value=mock_response)
        with patch(
            "hpe_networking_mcp.platforms.greenlake.tools.bulk_add._poll_async_operation",
            new=AsyncMock(return_value={"status": "SUCCEEDED"}),
        ):
            await _patch_enrich_location(mock_client, "dev-uuid-1", "loc-uuid-1")
        call_kwargs = mock_client.patch_raw.call_args
        endpoint = call_kwargs.args[0] if call_kwargs.args else call_kwargs.kwargs.get("endpoint", "")
        params = call_kwargs.kwargs.get("params") or {}
        assert "/devices/v2beta1/devices" in endpoint
        assert "?" not in endpoint
        assert params.get("id") == "dev-uuid-1"

    async def test_never_raises_on_patch_raw_exception(self) -> None:
        """patch_raw exception must return ('failed', reason); must never propagate."""
        mock_client = MagicMock()
        mock_client.patch_raw = AsyncMock(side_effect=Exception("network down"))
        status, reason = await _patch_enrich_location(mock_client, "dev-1", "loc-1")
        assert status == "failed"
        assert reason is not None

    async def test_returns_failed_on_no_location_header(self) -> None:
        """202 with empty Location header → ('failed', reason mentioning Location)."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 202
        mock_response.headers = {}
        mock_client.patch_raw = AsyncMock(return_value=mock_response)
        status, reason = await _patch_enrich_location(mock_client, "dev-1", "loc-1")
        assert status == "failed"
        assert reason is not None
        assert "Location" in reason or "location" in reason.lower()

    async def test_returns_failed_on_poll_timeout(self) -> None:
        """_poll_async_operation returning None → ('failed', reason containing 'timeout')."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 202
        mock_response.headers = {"location": "/devices/v2beta1/async-operations/op-1"}
        mock_client.patch_raw = AsyncMock(return_value=mock_response)
        with patch(
            "hpe_networking_mcp.platforms.greenlake.tools.bulk_add._poll_async_operation",
            new=AsyncMock(return_value=None),
        ):
            status, reason = await _patch_enrich_location(mock_client, "dev-1", "loc-1")
        assert status == "failed"
        assert reason is not None
        assert "timeout" in reason.lower()

    async def test_failed_poll_with_string_error_does_not_raise(self) -> None:
        """poll_result with 'error' as a plain string must not raise AttributeError."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 202
        mock_response.headers = {"location": "/devices/v2beta1/async-operations/op-str-err"}
        mock_client.patch_raw = AsyncMock(return_value=mock_response)
        with patch(
            "hpe_networking_mcp.platforms.greenlake.tools.bulk_add._poll_async_operation",
            new=AsyncMock(return_value={"status": "FAILED", "error": "plain string error"}),
        ):
            status, reason = await _patch_enrich_location(mock_client, "dev-1", "loc-1")
        assert status == "failed"
        assert reason is not None
        assert "plain string error" in reason


# ---------------------------------------------------------------------------
# TestPatchEnrichTags
# ---------------------------------------------------------------------------


class TestPatchEnrichTags:
    async def test_returns_succeeded_on_successful_poll(self) -> None:
        """202 + Location header + SUCCEEDED poll → ('succeeded', None)."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 202
        mock_response.headers = {"location": "/devices/v2beta1/async-operations/op-tags-1"}
        mock_client.patch_raw = AsyncMock(return_value=mock_response)
        with patch(
            "hpe_networking_mcp.platforms.greenlake.tools.bulk_add._poll_async_operation",
            new=AsyncMock(return_value={"status": "SUCCEEDED"}),
        ):
            status, reason = await _patch_enrich_tags(mock_client, "dev-uuid-1", {"wlan": "", "floor3": ""})
        assert status == "succeeded"
        assert reason is None

    async def test_returns_failed_on_non_202(self) -> None:
        """Non-202 status → ('failed', reason containing status code)."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 422
        mock_response.text = "invalid tag format"
        mock_client.patch_raw = AsyncMock(return_value=mock_response)
        status, reason = await _patch_enrich_tags(mock_client, "dev-uuid-1", {"wlan": ""})
        assert status == "failed"
        assert reason is not None
        assert "422" in reason

    async def test_uses_merge_patch_content_type(self) -> None:
        """PATCH must include Content-Type: application/merge-patch+json."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 202
        mock_response.headers = {"location": "/devices/v2beta1/async-operations/op-tags-2"}
        mock_client.patch_raw = AsyncMock(return_value=mock_response)
        with patch(
            "hpe_networking_mcp.platforms.greenlake.tools.bulk_add._poll_async_operation",
            new=AsyncMock(return_value={"status": "SUCCEEDED"}),
        ):
            await _patch_enrich_tags(mock_client, "dev-1", {"wlan": ""})
        call_kwargs = mock_client.patch_raw.call_args
        headers = call_kwargs.kwargs.get("additional_headers") or {}
        assert headers.get("Content-Type") == "application/merge-patch+json"

    async def test_body_format_is_dict_not_array(self) -> None:
        """PATCH body must be {'tags': dict} NOT {'tags': ['wlan', 'floor3']}."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 202
        mock_response.headers = {"location": "/devices/v2beta1/async-operations/op-tags-3"}
        mock_client.patch_raw = AsyncMock(return_value=mock_response)
        with patch(
            "hpe_networking_mcp.platforms.greenlake.tools.bulk_add._poll_async_operation",
            new=AsyncMock(return_value={"status": "SUCCEEDED"}),
        ):
            await _patch_enrich_tags(mock_client, "dev-uuid-1", {"wlan": "", "floor3": ""})
        call_kwargs = mock_client.patch_raw.call_args
        body = call_kwargs.kwargs.get("data") or {}
        assert "tags" in body
        assert isinstance(body["tags"], dict)  # dict, not list
        assert not isinstance(body["tags"], list)  # explicitly not array
        assert body["tags"] == {"wlan": "", "floor3": ""}

    async def test_endpoint_uses_v2beta1(self) -> None:
        """Endpoint must be /devices/v2beta1/devices with id passed as params dict."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 202
        mock_response.headers = {"location": "/devices/v2beta1/async-operations/op-tags-4"}
        mock_client.patch_raw = AsyncMock(return_value=mock_response)
        with patch(
            "hpe_networking_mcp.platforms.greenlake.tools.bulk_add._poll_async_operation",
            new=AsyncMock(return_value={"status": "SUCCEEDED"}),
        ):
            await _patch_enrich_tags(mock_client, "dev-uuid-1", {"wlan": ""})
        call_kwargs = mock_client.patch_raw.call_args
        endpoint = call_kwargs.args[0] if call_kwargs.args else call_kwargs.kwargs.get("endpoint", "")
        params = call_kwargs.kwargs.get("params") or {}
        assert "/devices/v2beta1/devices" in endpoint
        assert "?" not in endpoint
        assert params.get("id") == "dev-uuid-1"

    async def test_never_raises_on_patch_raw_exception(self) -> None:
        """patch_raw exception must return ('failed', reason); must never propagate."""
        mock_client = MagicMock()
        mock_client.patch_raw = AsyncMock(side_effect=Exception("connection refused"))
        status, reason = await _patch_enrich_tags(mock_client, "dev-1", {"wlan": ""})
        assert status == "failed"
        assert reason is not None

    async def test_returns_failed_on_no_location_header(self) -> None:
        """202 with empty Location header → ('failed', reason mentioning Location)."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 202
        mock_response.headers = {}
        mock_client.patch_raw = AsyncMock(return_value=mock_response)
        status, reason = await _patch_enrich_tags(mock_client, "dev-1", {"wlan": ""})
        assert status == "failed"
        assert reason is not None
        assert "Location" in reason or "location" in reason.lower()

    async def test_string_error_field_does_not_raise(self) -> None:
        """poll_result with 'error' as a plain string must not raise AttributeError."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 202
        mock_response.headers = {"location": "/devices/v2beta1/async-operations/op-str-err-tags"}
        mock_client.patch_raw = AsyncMock(return_value=mock_response)
        with patch(
            "hpe_networking_mcp.platforms.greenlake.tools.bulk_add._poll_async_operation",
            new=AsyncMock(return_value={"status": "FAILED", "error": "plain string error"}),
        ):
            status, reason = await _patch_enrich_tags(mock_client, "dev-1", {"wlan": ""})
        assert status == "failed"
        assert reason is not None
        assert "plain string error" in reason


# ---------------------------------------------------------------------------
# TestEnrichForRow
# ---------------------------------------------------------------------------


class TestEnrichForRow:
    async def test_not_applicable_when_device_not_succeeded(self) -> None:
        """cache[sn]['status'] != 'succeeded' → all 4 fields set to 'not_applicable', returns (0,0,0,0)."""
        mock_client = MagicMock()
        cache = {"SN001": {"status": "failed", "device_id": None, "row_index": 0, "reason": "POST failed"}}
        row = {"serialNumber": "SN001", "location": "loc-uuid-1", "tags": "wlan,floor3"}
        result = await _enrich_for_row(mock_client, row, cache, "SN001")
        assert result == (0, 0, 0, 0)
        assert cache["SN001"]["location_status"] == "not_applicable"
        assert cache["SN001"]["tags_status"] == "not_applicable"
        assert cache["SN001"]["location_reason"] is None
        assert cache["SN001"]["tags_reason"] is None
        mock_client.patch_raw.assert_not_called() if hasattr(mock_client, "patch_raw") else None

    async def test_location_skipped_when_blank(self) -> None:
        """Blank location cell → location_status='skipped', no PATCH call, returns (0,0,...)."""
        mock_client = MagicMock()
        mock_client.patch_raw = AsyncMock()
        cache = {"SN001": {"status": "succeeded", "device_id": "dev-uuid-1", "row_index": 0, "reason": None}}
        row = {"serialNumber": "SN001", "location": "", "tags": ""}
        result = await _enrich_for_row(mock_client, row, cache, "SN001")
        assert result[0] == 0  # loc_attempted
        assert cache["SN001"]["location_status"] == "skipped"
        assert cache["SN001"]["location_reason"] is None
        mock_client.patch_raw.assert_not_called()

    async def test_tags_skipped_when_blank(self) -> None:
        """Blank tags cell → tags_status='skipped', no PATCH call."""
        mock_client = MagicMock()
        mock_client.patch_raw = AsyncMock()
        cache = {"SN001": {"status": "succeeded", "device_id": "dev-uuid-1", "row_index": 0, "reason": None}}
        row = {"serialNumber": "SN001", "location": "", "tags": ""}
        result = await _enrich_for_row(mock_client, row, cache, "SN001")
        assert result[2] == 0  # tags_attempted
        assert cache["SN001"]["tags_status"] == "skipped"
        assert cache["SN001"]["tags_reason"] is None

    async def test_location_failed_when_no_device_uuid(self) -> None:
        """status='succeeded' but device_id=None → loc_attempted=1, location_status='failed'."""
        mock_client = MagicMock()
        cache = {"SN001": {"status": "succeeded", "device_id": None, "row_index": 0, "reason": None}}
        row = {"serialNumber": "SN001", "location": "loc-uuid-1", "tags": ""}
        result = await _enrich_for_row(mock_client, row, cache, "SN001")
        assert result[0] == 1  # loc_attempted — operator intended enrichment, counted even when UUID missing
        assert cache["SN001"]["location_status"] == "failed"
        assert cache["SN001"]["location_reason"] is not None
        assert "no device_uuid" in cache["SN001"]["location_reason"]

    async def test_tags_attempted_when_no_device_uuid(self) -> None:
        """status='succeeded' but device_id=None with tags → tags_attempted=1, tags_status='failed'."""
        mock_client = MagicMock()
        cache = {"SN001": {"status": "succeeded", "device_id": None, "row_index": 0, "reason": None}}
        row = {"serialNumber": "SN001", "location": "", "tags": "wlan,floor3"}
        result = await _enrich_for_row(mock_client, row, cache, "SN001")
        assert result[2] == 1  # tags_attempted — operator intended enrichment, counted even when UUID missing
        assert cache["SN001"]["tags_status"] == "failed"
        assert cache["SN001"]["tags_reason"] is not None
        assert "no device_uuid" in cache["SN001"]["tags_reason"]

    async def test_location_patch_called_with_stripped_uuid(self) -> None:
        """Location value with whitespace must be stripped before passing to _patch_enrich_location."""
        mock_client = MagicMock()
        cache = {"SN001": {"status": "succeeded", "device_id": "dev-uuid-1", "row_index": 0, "reason": None}}
        row = {"serialNumber": "SN001", "location": "  loc-uuid  ", "tags": ""}
        with patch(
            "hpe_networking_mcp.platforms.greenlake.tools._bulk_enrichment._patch_enrich_location",
            new=AsyncMock(return_value=("succeeded", None)),
        ) as mock_patch_loc:
            result = await _enrich_for_row(mock_client, row, cache, "SN001")
        assert result[0] == 1  # loc_attempted
        assert result[1] == 1  # loc_succeeded
        call_args = mock_patch_loc.call_args
        # Third positional arg (or location_id kwarg) must be stripped
        location_id_arg = call_args.args[2] if len(call_args.args) >= 3 else call_args.kwargs.get("location_id", "")
        assert location_id_arg == "loc-uuid"

    async def test_tags_assembled_as_dict(self) -> None:
        """tags='wlan, floor3' → _patch_enrich_tags called with {'wlan': '', 'floor3': ''}, not a list."""
        mock_client = MagicMock()
        cache = {"SN001": {"status": "succeeded", "device_id": "dev-uuid-1", "row_index": 0, "reason": None}}
        row = {"serialNumber": "SN001", "location": "", "tags": "wlan, floor3"}
        with patch(
            "hpe_networking_mcp.platforms.greenlake.tools._bulk_enrichment._patch_enrich_tags",
            new=AsyncMock(return_value=("succeeded", None)),
        ) as mock_patch_tags:
            result = await _enrich_for_row(mock_client, row, cache, "SN001")
        assert result[2] == 1  # tags_attempted
        assert result[3] == 1  # tags_succeeded
        call_args = mock_patch_tags.call_args
        tags_dict_arg = call_args.args[2] if len(call_args.args) >= 3 else call_args.kwargs.get("tags_dict", {})
        assert isinstance(tags_dict_arg, dict)
        assert not isinstance(tags_dict_arg, list)
        assert tags_dict_arg == {"wlan": "", "floor3": ""}
