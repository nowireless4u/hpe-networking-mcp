# (c) Copyright 2025 Hewlett Packard Enterprise Development LP
"""Unit tests for hpe_networking_mcp.platforms.greenlake.tools._bulk_assignment."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from hpe_networking_mcp.platforms.greenlake.tools._bulk_assignment import (
    _patch_assign_application,
    _patch_assign_subscription,
    _resolve_application_id,
    _resolve_subscription_id,
    _sanitize_reason,
    make_patch_limiter,
)

pytestmark = pytest.mark.unit


# ---------------------------------------------------------------------------
# TestSanitizeReason
# ---------------------------------------------------------------------------


class TestSanitizeReason:
    def test_strips_control_characters(self) -> None:
        """Control bytes (0x00-0x1f) must be replaced with spaces."""
        result = _sanitize_reason("hi\x00\x01there")
        assert "\x00" not in result
        assert "\x01" not in result
        assert "hi" in result
        assert "there" in result

    def test_truncates_to_200_chars(self) -> None:
        """Output must not exceed 200 characters."""
        long_input = "a" * 500
        result = _sanitize_reason(long_input)
        assert len(result) == 200

    def test_returns_empty_string_for_none(self) -> None:
        """None input must return empty string, not raise TypeError."""
        result = _sanitize_reason(None)  # type: ignore[arg-type]
        assert result == ""

    def test_preserves_printable_ascii(self) -> None:
        """Normal ASCII text must pass through unchanged."""
        text = "PATCH application 422: bad request"
        result = _sanitize_reason(text)
        assert result == text

    def test_replaces_high_bytes(self) -> None:
        """Characters above 0x7e must be replaced with space."""
        result = _sanitize_reason("hel\x7flo\x80world")
        assert "\x7f" not in result
        assert "\x80" not in result


# ---------------------------------------------------------------------------
# TestResolveSubscriptionId
# ---------------------------------------------------------------------------


class TestResolveSubscriptionId:
    async def test_caches_lookup_result(self) -> None:
        """Second call for same key must not call client.get again."""
        mock_client = MagicMock()
        mock_client.get = AsyncMock(return_value={"items": [{"id": "sub-uuid-1", "key": "KEY001"}]})
        cache: dict = {}
        result1 = await _resolve_subscription_id(mock_client, "KEY001", cache)
        result2 = await _resolve_subscription_id(mock_client, "KEY001", cache)
        assert result1 == "sub-uuid-1"
        assert result2 == "sub-uuid-1"
        assert mock_client.get.call_count == 1  # cached after first call

    async def test_returns_none_for_missing_key(self) -> None:
        """Empty items list must return None and cache the miss."""
        mock_client = MagicMock()
        mock_client.get = AsyncMock(return_value={"items": []})
        cache: dict = {}
        result = await _resolve_subscription_id(mock_client, "MISSING", cache)
        assert result is None
        assert "MISSING" in cache  # miss is also cached
        assert cache["MISSING"] is None

    async def test_returns_none_on_get_exception(self) -> None:
        """client.get exception must return None silently; cache key is None."""
        mock_client = MagicMock()
        mock_client.get = AsyncMock(side_effect=Exception("network error"))
        cache: dict = {}
        result = await _resolve_subscription_id(mock_client, "KEY001", cache)
        assert result is None
        assert cache.get("KEY001") is None

    async def test_passes_odata_filter_with_quoted_key(self) -> None:
        """OData filter must wrap the key in single quotes."""
        mock_client = MagicMock()
        mock_client.get = AsyncMock(return_value={"items": [{"id": "sub-uuid-2"}]})
        cache: dict = {}
        await _resolve_subscription_id(mock_client, "KEY001", cache)
        call_kwargs = mock_client.get.call_args
        params = call_kwargs.kwargs.get("params") or call_kwargs[1].get("params", {})
        assert params is not None
        filter_val = params.get("filter", "")
        assert "key eq 'KEY001'" in filter_val

    async def test_odata_injection_quote_escaped(self) -> None:
        """Single quote in subscription key must be doubled to prevent OData injection."""
        mock_client = MagicMock()
        mock_client.get = AsyncMock(return_value={"items": [{"id": "sub-1"}]})
        cache: dict = {}
        await _resolve_subscription_id(mock_client, "KEY'INJECT", cache)
        call_kwargs = mock_client.get.call_args
        params = call_kwargs.kwargs.get("params") or call_kwargs[1].get("params", {})
        assert params is not None
        filter_val = params.get("filter", "")
        # Single quote must be doubled (OData escaping), not left raw
        assert "KEY''INJECT" in filter_val, f"Expected escaped quote in filter; got: {filter_val!r}"
        # Must NOT contain the raw unescaped injection pattern
        assert "KEY'INJECT" not in filter_val.replace("KEY''INJECT", "")


# ---------------------------------------------------------------------------
# TestResolveApplicationId
# ---------------------------------------------------------------------------


class TestResolveApplicationId:
    async def test_fetches_catalog_once(self) -> None:
        """Catalog GET is called at most once regardless of row count."""
        mock_client = MagicMock()
        mock_client.get = AsyncMock(
            return_value={"items": [{"id": "app-uuid-1", "name": "Aruba Central", "region": "us-west"}]}
        )
        cache: dict = {}
        r1 = await _resolve_application_id(mock_client, "Aruba Central", cache)
        r2 = await _resolve_application_id(mock_client, "central", cache)  # case-insensitive
        assert r1 == ("app-uuid-1", "us-west")
        assert r2 == ("app-uuid-1", "us-west")
        assert mock_client.get.call_count == 1

    async def test_substring_case_insensitive_match(self) -> None:
        """'central' must match catalog item named 'Aruba Central'."""
        mock_client = MagicMock()
        mock_client.get = AsyncMock(
            return_value={"items": [{"id": "app-uuid-1", "name": "Aruba Central", "region": "us-east"}]}
        )
        cache: dict = {}
        app_id, region = await _resolve_application_id(mock_client, "central", cache)
        assert app_id == "app-uuid-1"
        assert region == "us-east"

    async def test_returns_none_tuple_when_not_found(self) -> None:
        """Empty catalog must return (None, None)."""
        mock_client = MagicMock()
        mock_client.get = AsyncMock(return_value={"items": []})
        cache: dict = {}
        result = await _resolve_application_id(mock_client, "Unknown Service", cache)
        assert result == (None, None)

    async def test_returns_region_none_when_field_absent(self) -> None:
        """Catalog item without region key must return (id, None)."""
        mock_client = MagicMock()
        mock_client.get = AsyncMock(return_value={"items": [{"id": "app-uuid-2", "name": "Aruba Central"}]})
        cache: dict = {}
        app_id, region = await _resolve_application_id(mock_client, "aruba central", cache)
        assert app_id == "app-uuid-2"
        assert region is None

    async def test_returns_none_tuple_on_exception(self) -> None:
        """client.get exception must return (None, None) and cache empty list."""
        mock_client = MagicMock()
        mock_client.get = AsyncMock(side_effect=Exception("timeout"))
        cache: dict = {}
        result = await _resolve_application_id(mock_client, "Central", cache)
        assert result == (None, None)
        assert cache.get("_catalog") == []  # avoids re-fetch on subsequent calls


# ---------------------------------------------------------------------------
# TestPatchAssignApplication
# ---------------------------------------------------------------------------


class TestPatchAssignApplication:
    async def test_returns_succeeded_on_successful_poll(self) -> None:
        """202 + Location + SUCCEEDED poll → ('succeeded', None)."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 202
        mock_response.headers = {"location": "/devices/v2beta1/async-operations/op-app-1"}
        mock_client.patch_raw = AsyncMock(return_value=mock_response)
        # _poll_async_operation is imported lazily from bulk_add — patch at the source
        with patch(
            "hpe_networking_mcp.platforms.greenlake.tools.bulk_add._poll_async_operation",
            new=AsyncMock(return_value={"status": "SUCCEEDED"}),
        ):
            status, reason = await _patch_assign_application(mock_client, "dev-uuid-1", "app-uuid-1", "us-west")
        assert status == "succeeded"
        assert reason is None

    async def test_returns_failed_on_non_202(self) -> None:
        """Non-202 status → ('failed', reason containing status code)."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 422
        mock_response.text = "bad request"
        mock_client.patch_raw = AsyncMock(return_value=mock_response)
        status, reason = await _patch_assign_application(mock_client, "dev-uuid-1", "app-uuid-1", "us-west")
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
            await _patch_assign_application(mock_client, "dev-1", "app-1", "us-west")
        call_kwargs = mock_client.patch_raw.call_args
        headers = call_kwargs.kwargs.get("additional_headers") or {}
        assert headers.get("Content-Type") == "application/merge-patch+json"

    async def test_body_includes_region_when_region_not_none(self) -> None:
        """When region is not None the PATCH body must include the 'region' key."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 202
        mock_response.headers = {"location": "/devices/v2beta1/async-operations/op-1"}
        mock_client.patch_raw = AsyncMock(return_value=mock_response)
        with patch(
            "hpe_networking_mcp.platforms.greenlake.tools.bulk_add._poll_async_operation",
            new=AsyncMock(return_value={"status": "SUCCEEDED"}),
        ):
            await _patch_assign_application(mock_client, "dev-1", "app-1", "us-west")
        call_kwargs = mock_client.patch_raw.call_args
        body = call_kwargs.kwargs.get("data") or {}
        assert "region" in body
        assert body["region"] == "us-west"

    async def test_body_omits_region_when_region_is_none(self) -> None:
        """When region is None the PATCH body must NOT include 'region' (per CONFIRMED A2)."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 202
        mock_response.headers = {"location": "/devices/v2beta1/async-operations/op-1"}
        mock_client.patch_raw = AsyncMock(return_value=mock_response)
        with patch(
            "hpe_networking_mcp.platforms.greenlake.tools.bulk_add._poll_async_operation",
            new=AsyncMock(return_value={"status": "SUCCEEDED"}),
        ):
            await _patch_assign_application(mock_client, "dev-1", "app-1", None)
        call_kwargs = mock_client.patch_raw.call_args
        body = call_kwargs.kwargs.get("data") or {}
        assert "region" not in body

    async def test_endpoint_uses_v2beta1_with_device_uuid_query_param(self) -> None:
        """Endpoint must be /devices/v2beta1/devices?id=<uuid> (per CONFIRMED A3)."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 202
        mock_response.headers = {"location": "/devices/v2beta1/async-operations/op-1"}
        mock_client.patch_raw = AsyncMock(return_value=mock_response)
        with patch(
            "hpe_networking_mcp.platforms.greenlake.tools.bulk_add._poll_async_operation",
            new=AsyncMock(return_value={"status": "SUCCEEDED"}),
        ):
            await _patch_assign_application(mock_client, "test-uuid-123", "app-1", "us-west")
        call_kwargs = mock_client.patch_raw.call_args
        endpoint = call_kwargs.args[0] if call_kwargs.args else call_kwargs.kwargs.get("endpoint", "")
        assert "/devices/v2beta1/devices" in endpoint
        assert "test-uuid-123" in endpoint
        assert "/v1/devices" not in endpoint

    async def test_never_raises_on_patch_raw_exception(self) -> None:
        """patch_raw exception must return ('failed', reason); must never propagate."""
        mock_client = MagicMock()
        mock_client.patch_raw = AsyncMock(side_effect=Exception("network down"))
        status, reason = await _patch_assign_application(mock_client, "dev-1", "app-1", "us-west")
        assert status == "failed"
        assert reason is not None

    async def test_returns_failed_on_no_location_header(self) -> None:
        """202 with empty Location header → ('failed', reason mentioning Location)."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 202
        mock_response.headers = {}
        mock_client.patch_raw = AsyncMock(return_value=mock_response)
        status, reason = await _patch_assign_application(mock_client, "dev-1", "app-1", "us-west")
        assert status == "failed"
        assert reason is not None
        assert "Location" in reason or "location" in reason.lower()

    async def test_returns_failed_on_poll_timeout(self) -> None:
        """_poll_async_operation returning None → ('failed', reason mentioning timeout)."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 202
        mock_response.headers = {"location": "/devices/v2beta1/async-operations/op-1"}
        mock_client.patch_raw = AsyncMock(return_value=mock_response)
        with patch(
            "hpe_networking_mcp.platforms.greenlake.tools.bulk_add._poll_async_operation",
            new=AsyncMock(return_value=None),
        ):
            status, reason = await _patch_assign_application(mock_client, "dev-1", "app-1", "us-west")
        assert status == "failed"
        assert reason is not None
        assert "timeout" in reason.lower()

    async def test_string_error_field_does_not_raise(self) -> None:
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
            status, reason = await _patch_assign_application(mock_client, "dev-1", "app-1", "us-west")
        assert status == "failed"
        assert reason is not None
        assert "plain string error" in reason


# ---------------------------------------------------------------------------
# TestPatchAssignSubscription
# ---------------------------------------------------------------------------


class TestPatchAssignSubscription:
    async def test_endpoint_uses_v2beta1(self) -> None:
        """Endpoint must be /devices/v2beta1/devices?id=<uuid>."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 202
        mock_response.headers = {"location": "/devices/v2beta1/async-operations/op-sub-1"}
        mock_client.patch_raw = AsyncMock(return_value=mock_response)
        with patch(
            "hpe_networking_mcp.platforms.greenlake.tools.bulk_add._poll_async_operation",
            new=AsyncMock(return_value={"status": "SUCCEEDED"}),
        ):
            await _patch_assign_subscription(mock_client, "dev-uuid-1", "sub-uuid-abc")
        call_kwargs = mock_client.patch_raw.call_args
        endpoint = call_kwargs.args[0] if call_kwargs.args else call_kwargs.kwargs.get("endpoint", "")
        assert "/devices/v2beta1/devices" in endpoint
        assert "dev-uuid-1" in endpoint

    async def test_body_uses_uuid_not_key_string(self) -> None:
        """Subscription body must use UUID, not the user-facing key string."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 202
        mock_response.headers = {"location": "/devices/v2beta1/async-operations/op-sub-1"}
        mock_client.patch_raw = AsyncMock(return_value=mock_response)
        with patch(
            "hpe_networking_mcp.platforms.greenlake.tools.bulk_add._poll_async_operation",
            new=AsyncMock(return_value={"status": "SUCCEEDED"}),
        ):
            await _patch_assign_subscription(mock_client, "dev-uuid-1", "sub-uuid-abc")
        call_kwargs = mock_client.patch_raw.call_args
        body = call_kwargs.kwargs.get("data") or {}
        assert body == {"subscription": [{"id": "sub-uuid-abc"}]}

    async def test_body_has_no_region_field(self) -> None:
        """Subscription PATCH body must NOT include 'region'."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 202
        mock_response.headers = {"location": "/devices/v2beta1/async-operations/op-sub-2"}
        mock_client.patch_raw = AsyncMock(return_value=mock_response)
        with patch(
            "hpe_networking_mcp.platforms.greenlake.tools.bulk_add._poll_async_operation",
            new=AsyncMock(return_value={"status": "SUCCEEDED"}),
        ):
            await _patch_assign_subscription(mock_client, "dev-uuid-1", "sub-uuid-abc")
        call_kwargs = mock_client.patch_raw.call_args
        body = call_kwargs.kwargs.get("data") or {}
        assert "region" not in body

    async def test_uses_merge_patch_content_type(self) -> None:
        """PATCH must include Content-Type: application/merge-patch+json."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 202
        mock_response.headers = {"location": "/devices/v2beta1/async-operations/op-sub-3"}
        mock_client.patch_raw = AsyncMock(return_value=mock_response)
        with patch(
            "hpe_networking_mcp.platforms.greenlake.tools.bulk_add._poll_async_operation",
            new=AsyncMock(return_value={"status": "SUCCEEDED"}),
        ):
            await _patch_assign_subscription(mock_client, "dev-1", "sub-1")
        call_kwargs = mock_client.patch_raw.call_args
        headers = call_kwargs.kwargs.get("additional_headers") or {}
        assert headers.get("Content-Type") == "application/merge-patch+json"

    async def test_never_raises_on_patch_raw_exception(self) -> None:
        """patch_raw exception must return ('failed', reason); must never propagate."""
        mock_client = MagicMock()
        mock_client.patch_raw = AsyncMock(side_effect=Exception("connection refused"))
        status, reason = await _patch_assign_subscription(mock_client, "dev-1", "sub-1")
        assert status == "failed"
        assert reason is not None

    async def test_string_error_field_does_not_raise(self) -> None:
        """poll_result with 'error' as a plain string must not raise AttributeError."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 202
        mock_response.headers = {"location": "/devices/v2beta1/async-operations/op-str-err-sub"}
        mock_client.patch_raw = AsyncMock(return_value=mock_response)
        with patch(
            "hpe_networking_mcp.platforms.greenlake.tools.bulk_add._poll_async_operation",
            new=AsyncMock(return_value={"status": "FAILED", "error": "plain string error"}),
        ):
            status, reason = await _patch_assign_subscription(mock_client, "dev-1", "sub-1")
        assert status == "failed"
        assert reason is not None
        assert "plain string error" in reason


# ---------------------------------------------------------------------------
# TestSubscriptionPatchLimiter
# ---------------------------------------------------------------------------


class TestMakePatchLimiter:
    def test_max_rate_is_20(self) -> None:
        """Rate must be 20 req/min (conservative margin vs documented 25/min)."""
        limiter = make_patch_limiter()
        assert limiter.max_rate == 20

    def test_time_period_is_60(self) -> None:
        """Time period must be 60 seconds (per minute)."""
        limiter = make_patch_limiter()
        assert limiter.time_period == 60

    def test_returns_distinct_instances(self) -> None:
        """Each call must return a new instance (per-invocation, not a singleton)."""
        a = make_patch_limiter()
        b = make_patch_limiter()
        assert a is not b
