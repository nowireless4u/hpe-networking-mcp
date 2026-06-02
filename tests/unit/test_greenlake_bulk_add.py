# (c) Copyright 2025 Hewlett Packard Enterprise Development LP
"""Unit tests for hpe_networking_mcp.platforms.greenlake.tools.bulk_add."""

from __future__ import annotations

import json
import pathlib
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from hpe_networking_mcp.platforms.greenlake.tools.bulk_add import (
    _build_post_payload,
    _extract_device_id,
    _load_cache,
    _poll_async_operation,
    _write_cache_atomic,
    greenlake_bulk_add_devices,
)

pytestmark = pytest.mark.unit


# ---------------------------------------------------------------------------
# TestBuildPostPayload
# ---------------------------------------------------------------------------


class TestBuildPostPayload:
    def test_network_devices_grouped_correctly(self) -> None:
        rows = [
            {"serialNumber": "SN001", "macAddress": "11:22:33:44:55:66"},
            {"serialNumber": "SN002", "macAddress": "AA:BB:CC:DD:EE:FF"},
        ]
        payload = _build_post_payload(rows)
        assert "network" in payload
        assert len(payload["network"]) == 2
        for item in payload["network"]:
            assert "serialNumber" in item
            assert "macAddress" in item

    def test_partNumber_included_when_present(self) -> None:
        rows = [{"serialNumber": "SN001", "macAddress": "11:22:33:44:55:66", "partNumber": "JL123A"}]
        payload = _build_post_payload(rows)
        assert payload["network"][0]["partNumber"] == "JL123A"

    def test_partNumber_omitted_when_absent(self) -> None:
        rows = [{"serialNumber": "SN001", "macAddress": "11:22:33:44:55:66"}]
        payload = _build_post_payload(rows)
        assert "partNumber" not in payload["network"][0]

    def test_empty_rows_returns_empty_network(self) -> None:
        payload = _build_post_payload([])
        assert payload == {"network": [], "compute": [], "storage": []}


# ---------------------------------------------------------------------------
# TestExtractDeviceId
# ---------------------------------------------------------------------------


class TestExtractDeviceId:
    def test_extracts_id_field(self) -> None:
        item = {"id": "uuid-123", "status": "SUCCEEDED"}
        assert _extract_device_id(item) == "uuid-123"

    def test_extracts_from_resourceUri(self) -> None:
        item = {"resourceUri": "/devices/v1/devices/uuid-456"}
        assert _extract_device_id(item) == "uuid-456"

    def test_extracts_deviceId_field(self) -> None:
        item = {"deviceId": "uuid-789"}
        assert _extract_device_id(item) == "uuid-789"

    def test_returns_none_when_no_id(self) -> None:
        item: dict = {}
        assert _extract_device_id(item) is None

    def test_id_takes_precedence_over_resourceUri(self) -> None:
        item = {"id": "uuid-from-id", "resourceUri": "/devices/v1/devices/uuid-from-uri"}
        assert _extract_device_id(item) == "uuid-from-id"


# ---------------------------------------------------------------------------
# TestWriteCacheAtomic
# ---------------------------------------------------------------------------


class TestWriteCacheAtomic:
    def test_writes_valid_json(self, tmp_path: pathlib.Path) -> None:
        cache_path = tmp_path / "test.cache.json"
        data = {
            "SN1234": {
                "status": "succeeded",
                "device_id": "uuid-1",
                "row_index": 0,
                "reason": None,
            }
        }
        _write_cache_atomic(cache_path, data)
        assert cache_path.exists()
        loaded = json.loads(cache_path.read_text())
        assert loaded == data

    def test_tmp_file_cleaned_up(self, tmp_path: pathlib.Path) -> None:
        cache_path = tmp_path / "test.cache.json"
        _write_cache_atomic(cache_path, {})
        tmp_file = cache_path.with_suffix(".tmp")
        assert not tmp_file.exists()

    def test_overwrites_existing(self, tmp_path: pathlib.Path) -> None:
        cache_path = tmp_path / "test.cache.json"
        _write_cache_atomic(cache_path, {"first": {"status": "succeeded"}})
        second_data = {"second": {"status": "failed"}}
        _write_cache_atomic(cache_path, second_data)
        loaded = json.loads(cache_path.read_text())
        assert loaded == second_data
        assert "first" not in loaded


# ---------------------------------------------------------------------------
# TestLoadCache
# ---------------------------------------------------------------------------


class TestLoadCache:
    def test_returns_empty_dict_for_missing_file(self, tmp_path: pathlib.Path) -> None:
        path = tmp_path / "nonexistent.cache.json"
        assert _load_cache(path) == {}

    def test_returns_empty_dict_for_invalid_json(self, tmp_path: pathlib.Path) -> None:
        path = tmp_path / "bad.cache.json"
        path.write_text("not json", encoding="utf-8")
        assert _load_cache(path) == {}

    def test_returns_empty_dict_for_empty_file(self, tmp_path: pathlib.Path) -> None:
        path = tmp_path / "empty.cache.json"
        path.write_text("", encoding="utf-8")
        assert _load_cache(path) == {}

    def test_returns_cache_data(self, tmp_path: pathlib.Path) -> None:
        path = tmp_path / "valid.cache.json"
        data = {"SN001": {"status": "succeeded", "device_id": "uuid-1", "row_index": 0, "reason": None}}
        path.write_text(json.dumps(data), encoding="utf-8")
        loaded = _load_cache(path)
        assert loaded == data


# ---------------------------------------------------------------------------
# Shared fixture
# ---------------------------------------------------------------------------


@pytest.fixture
def mock_ctx() -> MagicMock:
    ctx = MagicMock()
    ctx.report_progress = AsyncMock()
    ctx.info = AsyncMock()
    ctx.session_id = "test-session-id"
    ctx.lifespan_context = {
        "greenlake_token_manager": MagicMock(),
        "config": MagicMock(),
        "token_store": None,
    }
    ctx.lifespan_context["config"].greenlake.api_base_url = "https://api.test.hpe.com"
    return ctx


# ---------------------------------------------------------------------------
# TestPollAsyncOperation
# ---------------------------------------------------------------------------


class TestPollAsyncOperation:
    async def test_returns_result_on_succeeded(self) -> None:
        mock_client = MagicMock()
        mock_client.get = AsyncMock(return_value={"status": "SUCCEEDED", "items": []})
        with patch("hpe_networking_mcp.platforms.greenlake.tools.bulk_add.POLL_INTERVAL_SECONDS", 0):
            result = await _poll_async_operation(mock_client, "op-id-123")
        assert result is not None
        assert result["status"] == "SUCCEEDED"

    async def test_returns_result_on_failed(self) -> None:
        mock_client = MagicMock()
        mock_client.get = AsyncMock(return_value={"status": "FAILED", "items": []})
        with patch("hpe_networking_mcp.platforms.greenlake.tools.bulk_add.POLL_INTERVAL_SECONDS", 0):
            result = await _poll_async_operation(mock_client, "op-id-fail")
        assert result is not None
        assert result["status"] == "FAILED"

    async def test_returns_result_on_timeout_status(self) -> None:
        mock_client = MagicMock()
        mock_client.get = AsyncMock(return_value={"status": "TIMEOUT", "items": []})
        with patch("hpe_networking_mcp.platforms.greenlake.tools.bulk_add.POLL_INTERVAL_SECONDS", 0):
            result = await _poll_async_operation(mock_client, "op-id-timeout")
        assert result is not None
        assert result["status"] == "TIMEOUT"

    async def test_returns_none_after_max_attempts(self) -> None:
        mock_client = MagicMock()
        mock_client.get = AsyncMock(return_value={"status": "RUNNING"})
        with (
            patch("hpe_networking_mcp.platforms.greenlake.tools.bulk_add.MAX_POLL_ATTEMPTS", 2),
            patch("hpe_networking_mcp.platforms.greenlake.tools.bulk_add.POLL_INTERVAL_SECONDS", 0),
        ):
            result = await _poll_async_operation(mock_client, "op-1")
        assert result is None

    async def test_normalizes_split_arrays(self) -> None:
        """Items missing 'items' key but with split succeeded/failed arrays are normalized."""
        mock_client = MagicMock()
        mock_client.get = AsyncMock(
            return_value={
                "status": "SUCCEEDED",
                "succeeded": [{"serialNumber": "SN1", "id": "uuid-1"}],
                "failed": [],
            }
        )
        with patch("hpe_networking_mcp.platforms.greenlake.tools.bulk_add.POLL_INTERVAL_SECONDS", 0):
            result = await _poll_async_operation(mock_client, "op-split")
        assert result is not None
        assert result.get("items") is not None
        assert len(result["items"]) == 1

    async def test_calls_get_with_correct_endpoint(self) -> None:
        mock_client = MagicMock()
        mock_client.get = AsyncMock(return_value={"status": "SUCCEEDED", "items": []})
        with patch("hpe_networking_mcp.platforms.greenlake.tools.bulk_add.POLL_INTERVAL_SECONDS", 0):
            await _poll_async_operation(mock_client, "op-id-test")
        mock_client.get.assert_called_with("/devices/v1/async-operations/op-id-test")


# ---------------------------------------------------------------------------
# TestGreenlakeBulkAddDevices
# ---------------------------------------------------------------------------


class TestGreenlakeBulkAddDevices:
    # --- Batch-loop integration tests ---

    def _make_limiter_mock(self) -> MagicMock:
        """Return an async context manager mock that skips rate limiting."""
        m = MagicMock()
        m.__aenter__ = AsyncMock(return_value=None)
        m.__aexit__ = AsyncMock(return_value=False)
        return m

    async def test_batch_failure_continues(self, mock_ctx: MagicMock, tmp_path: pathlib.Path) -> None:
        """D-03: POST error on batch 1 does not prevent batch 2 from running.

        Uses 6 rows so batches are [5 rows] and [1 row] — two separate POSTs.
        """
        # 6 rows → 2 batches (batch size = 5)
        lines = ["serialNumber,macAddress"] + [f"SN{i:03d},11:22:33:44:55:{i:02x}" for i in range(1, 7)]
        csv_content = "\n".join(lines) + "\n"
        csv_file = tmp_path / "devices.csv"
        csv_file.write_text(csv_content, encoding="utf-8")

        # Batch 1 fails (422), batch 2 succeeds (202)
        fail_response = MagicMock()
        fail_response.status_code = 422
        fail_response.text = "duplicate device"
        fail_response.headers = {}

        success_response = MagicMock()
        success_response.status_code = 202
        success_response.headers = {"location": "/devices/v1/async-operations/op-abc"}

        mock_client_instance = MagicMock()
        mock_client_instance.post_raw = AsyncMock(side_effect=[fail_response, success_response])
        mock_client_instance.close = AsyncMock()

        # Batch 2 has SN006 only
        poll_result = {
            "status": "SUCCEEDED",
            "items": [{"serialNumber": "SN006", "id": "uuid-006", "status": "SUCCEEDED"}],
        }

        mock_limiter = self._make_limiter_mock()
        with (
            patch(
                "hpe_networking_mcp.platforms.greenlake.tools.bulk_add.GreenLakeHttpClient",
                return_value=mock_client_instance,
            ),
            patch(
                "hpe_networking_mcp.platforms.greenlake.tools.bulk_add._poll_async_operation",
                new=AsyncMock(return_value=poll_result),
            ),
            patch("hpe_networking_mcp.platforms.greenlake.tools.bulk_add.AsyncLimiter", return_value=mock_limiter),
            patch(
                "hpe_networking_mcp.platforms.greenlake.tools.bulk_add.make_patch_limiter",
                return_value=mock_limiter,
            ),
        ):
            result = await greenlake_bulk_add_devices(
                mock_ctx,
                csv_path=str(csv_file),
            )

        assert isinstance(result, dict)
        # Batch 1 (SN001–SN005) failed (422), Batch 2 (SN006) succeeded
        assert result["failed"] >= 1
        assert result["succeeded"] >= 1

    async def test_report_progress_called_per_batch(self, mock_ctx: MagicMock, tmp_path: pathlib.Path) -> None:
        """D-05: ctx.report_progress is called twice per batch (submitted + completed)."""
        csv_content = "serialNumber,macAddress\nSN001,11:22:33:44:55:66\n"
        csv_file = tmp_path / "devices.csv"
        csv_file.write_text(csv_content, encoding="utf-8")

        success_response = MagicMock()
        success_response.status_code = 202
        success_response.headers = {"location": "/devices/v1/async-operations/op-xyz"}

        mock_client_instance = MagicMock()
        mock_client_instance.post_raw = AsyncMock(return_value=success_response)
        mock_client_instance.close = AsyncMock()

        poll_result = {
            "status": "SUCCEEDED",
            "items": [{"serialNumber": "SN001", "id": "uuid-001", "status": "SUCCEEDED"}],
        }

        mock_limiter = self._make_limiter_mock()
        with (
            patch(
                "hpe_networking_mcp.platforms.greenlake.tools.bulk_add.GreenLakeHttpClient",
                return_value=mock_client_instance,
            ),
            patch(
                "hpe_networking_mcp.platforms.greenlake.tools.bulk_add._poll_async_operation",
                new=AsyncMock(return_value=poll_result),
            ),
            patch("hpe_networking_mcp.platforms.greenlake.tools.bulk_add.AsyncLimiter", return_value=mock_limiter),
            patch(
                "hpe_networking_mcp.platforms.greenlake.tools.bulk_add.make_patch_limiter",
                return_value=mock_limiter,
            ),
            patch("hpe_networking_mcp.platforms.greenlake.tools.bulk_add._write_cache_atomic"),
        ):
            await greenlake_bulk_add_devices(
                mock_ctx,
                csv_path=str(csv_file),
            )

        assert mock_ctx.report_progress.call_count == 2
        calls = mock_ctx.report_progress.call_args_list
        first_msg = calls[0].kwargs.get("message", "") or str(calls[0])
        second_msg = calls[1].kwargs.get("message", "") or str(calls[1])
        assert "submitted" in first_msg
        assert "succeeded" in second_msg or "failed" in second_msg

    async def test_cache_deleted_on_full_success(self, mock_ctx: MagicMock, tmp_path: pathlib.Path) -> None:
        """RESUME-03: cache file is removed after fully successful run."""
        csv_content = "serialNumber,macAddress\nSN001,11:22:33:44:55:66\n"
        csv_file = tmp_path / "devices.csv"
        csv_file.write_text(csv_content, encoding="utf-8")
        cache_path = tmp_path / "devices.cache.json"

        success_response = MagicMock()
        success_response.status_code = 202
        success_response.headers = {"location": "/devices/v1/async-operations/op-del"}

        mock_client_instance = MagicMock()
        mock_client_instance.post_raw = AsyncMock(return_value=success_response)
        mock_client_instance.close = AsyncMock()

        poll_result = {
            "status": "SUCCEEDED",
            "items": [{"serialNumber": "SN001", "id": "uuid-001", "status": "SUCCEEDED"}],
        }

        mock_limiter = self._make_limiter_mock()
        with (
            patch(
                "hpe_networking_mcp.platforms.greenlake.tools.bulk_add.GreenLakeHttpClient",
                return_value=mock_client_instance,
            ),
            patch(
                "hpe_networking_mcp.platforms.greenlake.tools.bulk_add._poll_async_operation",
                new=AsyncMock(return_value=poll_result),
            ),
            patch("hpe_networking_mcp.platforms.greenlake.tools.bulk_add.AsyncLimiter", return_value=mock_limiter),
            patch(
                "hpe_networking_mcp.platforms.greenlake.tools.bulk_add.make_patch_limiter",
                return_value=mock_limiter,
            ),
        ):
            result = await greenlake_bulk_add_devices(
                mock_ctx,
                csv_path=str(csv_file),
            )

        # Cache should be deleted on full success (RESUME-03)
        assert not cache_path.exists()
        assert isinstance(result, dict)
        assert result["succeeded"] == 1
        assert result["cache_path"] is None

    async def test_resume_skips_succeeded(self, mock_ctx: MagicMock, tmp_path: pathlib.Path) -> None:
        """RESUME-02: rows with status==succeeded in existing cache are skipped."""
        csv_content = "serialNumber,macAddress\nSN1234,11:22:33:44:55:66\n"
        csv_file = tmp_path / "devices.csv"
        csv_file.write_text(csv_content, encoding="utf-8")

        # Pre-populate cache with SN1234 as succeeded
        cache_path = tmp_path / "devices.cache.json"
        cache_data = {
            "SN1234": {
                "status": "succeeded",
                "device_id": "uuid-pre",
                "row_index": 0,
                "reason": None,
            }
        }
        cache_path.write_text(json.dumps(cache_data), encoding="utf-8")

        mock_client_instance = MagicMock()
        mock_client_instance.post_raw = AsyncMock()
        mock_client_instance.close = AsyncMock()

        with (
            patch(
                "hpe_networking_mcp.platforms.greenlake.tools.bulk_add.GreenLakeHttpClient",
                return_value=mock_client_instance,
            ),
            patch(
                "hpe_networking_mcp.platforms.greenlake.tools.bulk_add.parse_csv",
                wraps=__import__(
                    "hpe_networking_mcp.platforms.greenlake.utils.csv_parser",
                    fromlist=["parse_csv"],
                ).parse_csv,
            ) as mock_parse,
        ):
            result = await greenlake_bulk_add_devices(
                mock_ctx,
                csv_path=str(csv_file),
            )

        # parse_csv is called (we read the file), but no POST is made
        mock_parse.assert_called_once()
        mock_client_instance.post_raw.assert_not_called()
        assert isinstance(result, dict)
        assert result["skipped"] == 1

    async def test_summary_includes_failure_reasons(self, mock_ctx: MagicMock, tmp_path: pathlib.Path) -> None:
        """D-06: final response dict has 'failures' list with 'serial' and 'reason' keys; capped at 10."""
        csv_content = "serialNumber,macAddress\nSN001,11:22:33:44:55:01\nSN002,11:22:33:44:55:02\n"
        csv_file = tmp_path / "devices.csv"
        csv_file.write_text(csv_content, encoding="utf-8")

        # Both batches fail (status 422)
        fail_response = MagicMock()
        fail_response.status_code = 422
        fail_response.text = "device already exists"
        fail_response.headers = {}

        mock_client_instance = MagicMock()
        mock_client_instance.post_raw = AsyncMock(return_value=fail_response)
        mock_client_instance.close = AsyncMock()

        mock_limiter = self._make_limiter_mock()
        with (
            patch(
                "hpe_networking_mcp.platforms.greenlake.tools.bulk_add.GreenLakeHttpClient",
                return_value=mock_client_instance,
            ),
            patch("hpe_networking_mcp.platforms.greenlake.tools.bulk_add.AsyncLimiter", return_value=mock_limiter),
            patch(
                "hpe_networking_mcp.platforms.greenlake.tools.bulk_add.make_patch_limiter",
                return_value=mock_limiter,
            ),
            patch("hpe_networking_mcp.platforms.greenlake.tools.bulk_add._write_cache_atomic"),
        ):
            result = await greenlake_bulk_add_devices(
                mock_ctx,
                csv_path=str(csv_file),
            )

        assert isinstance(result, dict)
        assert "failures" in result
        assert isinstance(result["failures"], list)
        for entry in result["failures"]:
            assert "serial" in entry
            assert "reason" in entry
        assert len(result["failures"]) <= 10


# ---------------------------------------------------------------------------
# TestBulkAddPhase20Integration
# ---------------------------------------------------------------------------
#
# Each test runs greenlake_bulk_add_devices against a real CSV (written to
# tmp_path) with the following mocks in place:
#   - GreenLakeHttpClient patched to return mock_client_instance
#   - mock_client_instance.post_raw, .patch_raw, .get, .close all AsyncMocks
#   - _device_add_limiter mocked as AsyncContextManager (skips rate limiting)
#   - _subscription_patch_limiter mocked at SOURCE in _bulk_assignment module
#   - _poll_async_operation mocked in bulk_add module namespace
#
# All tests verify cache JSON written to disk and/or the return envelope.
# Tests are in RED state until Task 2 wires Section 6f.5 into bulk_add.py.


def _make_success_post_response(op_id: str = "op-001") -> MagicMock:
    """Return a fake 202 POST response with a Location header."""
    r = MagicMock()
    r.status_code = 202
    r.headers = {"location": f"/devices/v1/async-operations/{op_id}"}
    r.text = ""
    return r


def _make_fail_post_response(code: int = 422, text: str = "conflict") -> MagicMock:
    """Return a fake non-202 POST response."""
    r = MagicMock()
    r.status_code = code
    r.headers = {}
    r.text = text
    return r


def _make_success_patch_response(op_id: str = "patch-op-001") -> MagicMock:
    """Return a fake 202 PATCH response with a Location header."""
    r = MagicMock()
    r.status_code = 202
    r.headers = {"location": f"/devices/v1/async-operations/{op_id}"}
    r.text = ""
    return r


def _make_fail_patch_response(code: int = 422, text: str = "assignment failed") -> MagicMock:
    """Return a fake non-202 PATCH response."""
    r = MagicMock()
    r.status_code = code
    r.headers = {}
    r.text = text
    return r


def _make_poll_result(status: str = "SUCCEEDED", items: list | None = None) -> dict:
    """Build a minimal async-operations poll response."""
    return {"status": status, "items": items or []}


def _write_csv(tmp_path: pathlib.Path, rows: list[dict], filename: str = "devices.csv") -> pathlib.Path:
    """Write a CSV file with header derived from first row's keys."""
    csv_file = tmp_path / filename
    if not rows:
        csv_file.write_text("serialNumber,macAddress\n", encoding="utf-8")
        return csv_file
    header = ",".join(rows[0])
    lines = [header] + [",".join(str(r.get(k, "")) for k in rows[0]) for r in rows]
    csv_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return csv_file


def _load_cache_from_disk(csv_file: pathlib.Path) -> dict:
    """Load the .cache.json file adjacent to the CSV.

    Note: fully-successful runs delete the cache file in SECTION 8.
    Use ``_capture_final_cache`` in tests that need to inspect per-row
    cache fields after a fully-successful run.
    """
    cache_path = csv_file.with_suffix(".cache.json")
    if not cache_path.exists():
        return {}
    return json.loads(cache_path.read_text(encoding="utf-8"))


def _capture_final_cache() -> tuple[MagicMock, list[dict]]:
    """Return a (mock, captured_list) pair that captures _write_cache_atomic calls.

    Usage::

        mock_write, captures = _capture_final_cache()
        with patch("hpe_networking_mcp.platforms.greenlake.tools.bulk_add._write_cache_atomic",
                   mock_write):
            await run_tool(...)
        last_cache = captures[-1]  # final write for the last batch
    """
    from unittest.mock import MagicMock  # local to avoid namespace pollution

    captured: list[dict] = []

    def _side_effect(path: pathlib.Path, data: dict) -> None:
        # Also write the real file so SECTION 8 cleanup logic can run
        tmp = path.with_suffix(".tmp")
        import json as _json
        import os as _os

        tmp.write_text(_json.dumps(data, indent=2), encoding="utf-8")
        _os.replace(tmp, path)
        captured.append(dict(data))

    mock = MagicMock(side_effect=_side_effect)
    return mock, captured


class TestBulkAddPhase20Integration:
    """Integration tests verifying Section 6f.5 subscription & service assignment."""

    def _make_client(
        self,
        post_side_effect=None,
        patch_side_effect=None,
        get_side_effect=None,
    ) -> MagicMock:
        """Build a mock GreenLakeHttpClient with configurable side_effects."""
        client = MagicMock()
        client.close = AsyncMock()
        if post_side_effect is not None:
            client.post_raw = AsyncMock(side_effect=post_side_effect)
        else:
            client.post_raw = AsyncMock(return_value=_make_success_post_response())
        if patch_side_effect is not None:
            client.patch_raw = AsyncMock(side_effect=patch_side_effect)
        else:
            client.patch_raw = AsyncMock(return_value=_make_success_patch_response())
        if get_side_effect is not None:
            client.get = AsyncMock(side_effect=get_side_effect)
        else:
            client.get = AsyncMock(return_value={"items": []})
        return client

    def _make_poll_side_effect(
        self,
        sn: str,
        device_id: str = "dev-uuid-001",
    ) -> list[dict]:
        """Build the poll return value for a batch of one row."""
        return [_make_poll_result("SUCCEEDED", [{"serialNumber": sn, "id": device_id, "status": "SUCCEEDED"}])]

    async def _run_tool(
        self,
        mock_ctx: MagicMock,
        csv_file: pathlib.Path,
        mock_client: MagicMock,
        poll_return_values: list[dict] | None = None,
        mock_sub_limiter: MagicMock | None = None,
    ) -> tuple[dict, dict]:
        """Run greenlake_bulk_add_devices with standard Phase 20 mocks.

        Returns:
            (result_envelope, final_cache) where final_cache is the last
            cache dict written during the run (captured before SECTION 8
            cleanup, so it has all Phase 20 fields even on full success).
        """
        if poll_return_values is None:
            poll_return_values = []

        if mock_sub_limiter is None:
            mock_sub_limiter = MagicMock()
            mock_sub_limiter.__aenter__ = AsyncMock(return_value=None)
            mock_sub_limiter.__aexit__ = AsyncMock(return_value=False)

        # Capture the last _write_cache_atomic call to inspect per-row Phase 20 fields.
        # The real write still happens so SECTION 8 cleanup logic can delete the file.
        captured_caches: list[dict] = []
        original_write = __import__(
            "hpe_networking_mcp.platforms.greenlake.tools.bulk_add",
            fromlist=["_write_cache_atomic"],
        )._write_cache_atomic

        def capturing_write(path: pathlib.Path, data: dict) -> None:
            captured_caches.append(dict(data))
            original_write(path, data)

        with (
            patch(
                "hpe_networking_mcp.platforms.greenlake.tools.bulk_add.GreenLakeHttpClient",
                return_value=mock_client,
            ),
            patch(
                "hpe_networking_mcp.platforms.greenlake.tools.bulk_add._poll_async_operation",
                new=AsyncMock(side_effect=poll_return_values),
            ),
            patch(
                "hpe_networking_mcp.platforms.greenlake.tools.bulk_add.AsyncLimiter",
                return_value=mock_sub_limiter,
            ),
            patch(
                "hpe_networking_mcp.platforms.greenlake.tools.bulk_add.make_patch_limiter",
                return_value=mock_sub_limiter,
            ),
            patch(
                "hpe_networking_mcp.platforms.greenlake.tools.bulk_add._write_cache_atomic",
                side_effect=capturing_write,
            ),
        ):
            result = await greenlake_bulk_add_devices(
                mock_ctx,
                csv_path=str(csv_file),
            )

        assert isinstance(result, dict), f"Expected dict, got: {result!r}"
        assert captured_caches, "No _write_cache_atomic calls captured — implementation did not write cache"
        final_cache = captured_caches[-1]
        return result, final_cache

    async def test_service_patch_called_before_subscription_patch(
        self, mock_ctx: MagicMock, tmp_path: pathlib.Path
    ) -> None:
        """SVC-01: service PATCH is always sent before subscription PATCH per row."""
        sn = "SN001"
        csv_file = _write_csv(
            tmp_path,
            [
                {
                    "serialNumber": sn,
                    "macAddress": "11:22:33:44:55:01",
                    "service": "Aruba Central",
                    "subscriptionKey": "KEY001",
                }
            ],
        )
        mock_client = self._make_client()
        mock_client.get = AsyncMock(
            side_effect=[
                # service catalog lookup (first GET in _assign_for_row)
                {"items": [{"id": "app-uuid-001", "name": "Aruba Central", "region": "us-west"}]},
                # subscription lookup (second GET in _assign_for_row)
                {"items": [{"id": "sub-uuid-001"}]},
            ]
        )
        mock_client.patch_raw = AsyncMock(
            side_effect=[
                _make_success_patch_response("patch-svc-op"),
                _make_success_patch_response("patch-sub-op"),
            ]
        )

        poll_values = [
            # POST poll — Phase 19 device-add
            _make_poll_result("SUCCEEDED", [{"serialNumber": sn, "id": "dev-uuid-001", "status": "SUCCEEDED"}]),
            # service PATCH poll
            _make_poll_result("SUCCEEDED"),
            # subscription PATCH poll
            _make_poll_result("SUCCEEDED"),
        ]
        _result, _cache = await self._run_tool(mock_ctx, csv_file, mock_client, poll_values)

        # Inspect call order from call_args_list — first call should have "application" in body,
        # second call should have "subscription" in body.
        calls = mock_client.patch_raw.call_args_list
        assert len(calls) == 2, f"Expected 2 PATCH calls, got {len(calls)}"
        first_body = calls[0].kwargs.get("data") or (calls[0].args[1] if len(calls[0].args) > 1 else {})
        second_body = calls[1].kwargs.get("data") or (calls[1].args[1] if len(calls[1].args) > 1 else {})
        assert "application" in first_body, (
            f"First PATCH should be service (application), got keys: {list(first_body.keys())}"
        )
        assert "subscription" in second_body, (
            f"Second PATCH should be subscription, got keys: {list(second_body.keys())}"
        )

    async def test_assignment_skipped_when_columns_missing(self, mock_ctx: MagicMock, tmp_path: pathlib.Path) -> None:
        """D-09: no service/subscriptionKey columns → both statuses are 'skipped'."""
        sn = "SN001"
        csv_file = _write_csv(
            tmp_path,
            [{"serialNumber": sn, "macAddress": "11:22:33:44:55:01"}],
        )
        mock_client = self._make_client()
        poll_values = [
            _make_poll_result("SUCCEEDED", [{"serialNumber": sn, "id": "dev-uuid-001", "status": "SUCCEEDED"}]),
        ]
        _result, _cache = await self._run_tool(mock_ctx, csv_file, mock_client, poll_values)

        cache = _cache
        assert sn in cache
        assert cache[sn]["service_status"] == "skipped", f"Expected skipped, got: {cache[sn].get('service_status')}"
        assert cache[sn]["subscription_status"] == "skipped"

    async def test_subscription_skipped_but_service_assigned_when_only_service_column(
        self, mock_ctx: MagicMock, tmp_path: pathlib.Path
    ) -> None:
        """service column present but no subscriptionKey → service succeeded, subscription skipped."""
        sn = "SN001"
        csv_file = _write_csv(
            tmp_path,
            [{"serialNumber": sn, "macAddress": "11:22:33:44:55:01", "service": "Aruba Central"}],
        )
        mock_client = self._make_client()
        mock_client.get = AsyncMock(
            side_effect=[
                # service catalog
                {"items": [{"id": "app-uuid-001", "name": "Aruba Central", "region": "us-west"}]},
            ]
        )
        mock_client.patch_raw = AsyncMock(return_value=_make_success_patch_response("patch-svc"))

        poll_values = [
            # POST poll
            _make_poll_result("SUCCEEDED", [{"serialNumber": sn, "id": "dev-uuid-001", "status": "SUCCEEDED"}]),
            # service PATCH poll
            _make_poll_result("SUCCEEDED"),
        ]
        _result, _cache = await self._run_tool(mock_ctx, csv_file, mock_client, poll_values)

        cache = _cache
        assert cache[sn]["service_status"] == "succeeded"
        assert cache[sn]["subscription_status"] == "skipped"

    async def test_service_skipped_but_subscription_assigned_when_only_sub_column(
        self, mock_ctx: MagicMock, tmp_path: pathlib.Path
    ) -> None:
        """subscriptionKey column present but no service → service skipped, subscription succeeded."""
        sn = "SN001"
        csv_file = _write_csv(
            tmp_path,
            [{"serialNumber": sn, "macAddress": "11:22:33:44:55:01", "subscriptionKey": "KEY001"}],
        )
        mock_client = self._make_client()
        mock_client.get = AsyncMock(
            side_effect=[
                # subscription lookup
                {"items": [{"id": "sub-uuid-001"}]},
            ]
        )
        mock_client.patch_raw = AsyncMock(return_value=_make_success_patch_response("patch-sub"))

        poll_values = [
            # POST poll
            _make_poll_result("SUCCEEDED", [{"serialNumber": sn, "id": "dev-uuid-001", "status": "SUCCEEDED"}]),
            # subscription PATCH poll
            _make_poll_result("SUCCEEDED"),
        ]
        _result, _cache = await self._run_tool(mock_ctx, csv_file, mock_client, poll_values)

        cache = _cache
        assert cache[sn]["service_status"] == "skipped"
        assert cache[sn]["subscription_status"] == "succeeded"

    async def test_subscription_failure_does_not_abort_remaining_rows(
        self, mock_ctx: MagicMock, tmp_path: pathlib.Path
    ) -> None:
        """SUB-03: row N subscription failure does not abort rows N+1..end."""
        rows = [
            {"serialNumber": "SN001", "macAddress": "11:22:33:44:55:01", "subscriptionKey": "KEY001"},
            {"serialNumber": "SN002", "macAddress": "11:22:33:44:55:02", "subscriptionKey": "KEY001"},
            {"serialNumber": "SN003", "macAddress": "11:22:33:44:55:03", "subscriptionKey": "KEY001"},
        ]
        csv_file = _write_csv(tmp_path, rows)
        mock_client = self._make_client()
        mock_client.get = AsyncMock(
            side_effect=[
                # subscription lookup (same key for all 3; cached after 1st call)
                {"items": [{"id": "sub-uuid-001"}]},
            ]
        )

        # SN001 subscription PATCH fails (422), SN002 and SN003 succeed
        mock_client.patch_raw = AsyncMock(
            side_effect=[
                _make_fail_patch_response(422, "throttled"),  # SN001 sub PATCH fails
                _make_success_patch_response("patch-sub-002"),  # SN002 sub PATCH ok
                _make_success_patch_response("patch-sub-003"),  # SN003 sub PATCH ok
            ]
        )

        # All 3 rows succeed in Phase 19 (batch of 3)
        poll_values = [
            _make_poll_result(
                "SUCCEEDED",
                [
                    {"serialNumber": "SN001", "id": "dev-uuid-001", "status": "SUCCEEDED"},
                    {"serialNumber": "SN002", "id": "dev-uuid-002", "status": "SUCCEEDED"},
                    {"serialNumber": "SN003", "id": "dev-uuid-003", "status": "SUCCEEDED"},
                ],
            ),
            # SN001 subscription PATCH: 422 → no poll
            # SN002 subscription PATCH poll (202)
            _make_poll_result("SUCCEEDED"),
            # SN003 subscription PATCH poll (202)
            _make_poll_result("SUCCEEDED"),
        ]
        _result, _cache = await self._run_tool(mock_ctx, csv_file, mock_client, poll_values)

        cache = _cache
        assert cache["SN001"]["subscription_status"] == "failed"
        assert cache["SN002"]["subscription_status"] == "succeeded"
        assert cache["SN003"]["subscription_status"] == "succeeded"

    async def test_service_failure_does_not_abort_subscription_for_same_row(
        self, mock_ctx: MagicMock, tmp_path: pathlib.Path
    ) -> None:
        """SVC-02: service PATCH failure does NOT skip subscription PATCH for the same row."""
        sn = "SN001"
        csv_file = _write_csv(
            tmp_path,
            [
                {
                    "serialNumber": sn,
                    "macAddress": "11:22:33:44:55:01",
                    "service": "Aruba Central",
                    "subscriptionKey": "KEY001",
                }
            ],
        )
        mock_client = self._make_client()
        mock_client.get = AsyncMock(
            side_effect=[
                # service catalog
                {"items": [{"id": "app-uuid-001", "name": "Aruba Central", "region": "us-west"}]},
                # subscription lookup
                {"items": [{"id": "sub-uuid-001"}]},
            ]
        )
        # Service PATCH fails (422), subscription PATCH succeeds
        mock_client.patch_raw = AsyncMock(
            side_effect=[
                _make_fail_patch_response(422, "service error"),  # service PATCH
                _make_success_patch_response("patch-sub"),  # subscription PATCH
            ]
        )

        poll_values = [
            # POST poll
            _make_poll_result("SUCCEEDED", [{"serialNumber": sn, "id": "dev-uuid-001", "status": "SUCCEEDED"}]),
            # subscription PATCH poll (no service poll because service was non-202)
            _make_poll_result("SUCCEEDED"),
        ]
        _result, _cache = await self._run_tool(mock_ctx, csv_file, mock_client, poll_values)

        cache = _cache
        assert cache[sn]["service_status"] == "failed"
        assert cache[sn]["subscription_status"] == "succeeded"

    async def test_not_applicable_when_phase19_failed(self, mock_ctx: MagicMock, tmp_path: pathlib.Path) -> None:
        """Phase 19 item-level failure → service_status and subscription_status both 'not_applicable'.

        Uses a per-item FAILED result (poll returns FAILED status for the item) rather than
        a batch-level 422 POST failure, because the 6f.5 block runs only for rows that
        entered the per-item extraction path in Section 6f.
        """
        sn = "SN001"
        csv_file = _write_csv(
            tmp_path,
            [
                {
                    "serialNumber": sn,
                    "macAddress": "11:22:33:44:55:01",
                    "service": "Aruba Central",
                    "subscriptionKey": "KEY001",
                }
            ],
        )
        mock_client = self._make_client()
        mock_client.patch_raw = AsyncMock()  # should NOT be called

        # Phase 19 poll returns FAILED for the item
        poll_values = [
            _make_poll_result(
                "SUCCEEDED",
                [{"serialNumber": sn, "id": None, "status": "FAILED", "reason": "device error"}],
            ),
        ]

        _result, _cache = await self._run_tool(mock_ctx, csv_file, mock_client, poll_values)

        cache = _cache
        assert cache[sn]["service_status"] == "not_applicable"
        assert cache[sn]["subscription_status"] == "not_applicable"
        assert mock_client.patch_raw.call_count == 0

    async def test_cache_extended_with_new_fields(self, mock_ctx: MagicMock, tmp_path: pathlib.Path) -> None:
        """D-03: successful run extends cache with four new Phase 20 fields."""
        sn = "SN001"
        csv_file = _write_csv(
            tmp_path,
            [
                {
                    "serialNumber": sn,
                    "macAddress": "11:22:33:44:55:01",
                    "service": "Aruba Central",
                    "subscriptionKey": "KEY001",
                }
            ],
        )
        mock_client = self._make_client()
        mock_client.get = AsyncMock(
            side_effect=[
                {"items": [{"id": "app-uuid-001", "name": "Aruba Central", "region": "us-west"}]},
                {"items": [{"id": "sub-uuid-001"}]},
            ]
        )
        mock_client.patch_raw = AsyncMock(
            side_effect=[
                _make_success_patch_response("patch-svc"),
                _make_success_patch_response("patch-sub"),
            ]
        )
        poll_values = [
            _make_poll_result("SUCCEEDED", [{"serialNumber": sn, "id": "dev-uuid-001", "status": "SUCCEEDED"}]),
            _make_poll_result("SUCCEEDED"),
            _make_poll_result("SUCCEEDED"),
        ]
        _result, _cache = await self._run_tool(mock_ctx, csv_file, mock_client, poll_values)

        cache = _cache
        row = cache[sn]
        # Phase 19 keys must still be present
        assert "status" in row
        assert "device_id" in row
        # Phase 20 new keys
        assert "service_status" in row, f"Missing service_status in {list(row.keys())}"
        assert "service_reason" in row
        assert "subscription_status" in row
        assert "subscription_reason" in row

    async def test_subscription_patch_limiter_acquired_for_each_patch(
        self, mock_ctx: MagicMock, tmp_path: pathlib.Path
    ) -> None:
        """SUB-02: patch limiter is acquired for EVERY assignment PATCH."""
        sn = "SN001"
        csv_file = _write_csv(
            tmp_path,
            [
                {
                    "serialNumber": sn,
                    "macAddress": "11:22:33:44:55:01",
                    "service": "Aruba Central",
                    "subscriptionKey": "KEY001",
                }
            ],
        )
        mock_client = self._make_client()
        mock_client.get = AsyncMock(
            side_effect=[
                {"items": [{"id": "app-uuid-001", "name": "Aruba Central", "region": "us-west"}]},
                {"items": [{"id": "sub-uuid-001"}]},
            ]
        )
        mock_client.patch_raw = AsyncMock(
            side_effect=[
                _make_success_patch_response("patch-svc"),
                _make_success_patch_response("patch-sub"),
            ]
        )
        poll_values = [
            _make_poll_result("SUCCEEDED", [{"serialNumber": sn, "id": "dev-uuid-001", "status": "SUCCEEDED"}]),
            _make_poll_result("SUCCEEDED"),
            _make_poll_result("SUCCEEDED"),
        ]

        mock_sub_limiter = MagicMock()
        mock_sub_limiter.__aenter__ = AsyncMock(return_value=None)
        mock_sub_limiter.__aexit__ = AsyncMock(return_value=False)

        _result, _cache = await self._run_tool(mock_ctx, csv_file, mock_client, poll_values, mock_sub_limiter)

        # 1 device_add limiter + 2 PATCH limiters (service + subscription) = 3 total acquisitions
        assert mock_sub_limiter.__aenter__.call_count == 3, (
            f"Expected 3 limiter acquisitions (1 device + 2 PATCH), got {mock_sub_limiter.__aenter__.call_count}"
        )

    async def test_subscription_uuid_lookup_cached_across_rows(
        self, mock_ctx: MagicMock, tmp_path: pathlib.Path
    ) -> None:
        """SUB-01: subscription lookup is made only ONCE for the same key across all rows."""
        rows = [
            {"serialNumber": f"SN{i:03d}", "macAddress": f"11:22:33:44:55:{i:02x}", "subscriptionKey": "KEY001"}
            for i in range(1, 4)
        ]
        csv_file = _write_csv(tmp_path, rows)
        mock_client = self._make_client()

        subscription_get_calls = 0

        async def tracking_get(endpoint, params=None, **kwargs):  # type: ignore[no-untyped-def]
            nonlocal subscription_get_calls
            if "/subscriptions/v1/subscriptions" in endpoint:
                subscription_get_calls += 1
                return {"items": [{"id": "sub-uuid-001"}]}
            return {"items": []}

        mock_client.get = AsyncMock(side_effect=tracking_get)
        mock_client.patch_raw = AsyncMock(return_value=_make_success_patch_response())

        poll_values = [
            _make_poll_result(
                "SUCCEEDED",
                [{"serialNumber": f"SN{i:03d}", "id": f"dev-uuid-{i:03d}", "status": "SUCCEEDED"} for i in range(1, 4)],
            ),
            # PATCH polls: 3 sub patches
            _make_poll_result("SUCCEEDED"),
            _make_poll_result("SUCCEEDED"),
            _make_poll_result("SUCCEEDED"),
        ]
        _result, _cache = await self._run_tool(mock_ctx, csv_file, mock_client, poll_values)

        assert subscription_get_calls == 1, f"Expected 1 subscription lookup, got {subscription_get_calls}"

    async def test_service_catalog_fetched_once(self, mock_ctx: MagicMock, tmp_path: pathlib.Path) -> None:
        """Service catalog is fetched exactly once even across 5 rows with the same service."""
        rows = [
            {"serialNumber": f"SN{i:03d}", "macAddress": f"11:22:33:44:55:{i:02x}", "service": "Aruba Central"}
            for i in range(1, 6)
        ]
        csv_file = _write_csv(tmp_path, rows)
        mock_client = self._make_client()

        catalog_get_calls = 0

        async def tracking_get(endpoint, params=None, **kwargs):  # type: ignore[no-untyped-def]
            nonlocal catalog_get_calls
            if "/service-catalog/v1/service-managers" in endpoint:
                catalog_get_calls += 1
                return {"items": [{"id": "app-uuid-001", "name": "Aruba Central", "region": "us-west"}]}
            return {"items": []}

        mock_client.get = AsyncMock(side_effect=tracking_get)
        mock_client.patch_raw = AsyncMock(return_value=_make_success_patch_response())

        poll_values = [
            _make_poll_result(
                "SUCCEEDED",
                [{"serialNumber": f"SN{i:03d}", "id": f"dev-uuid-{i:03d}", "status": "SUCCEEDED"} for i in range(1, 6)],
            ),
            # 5 service PATCH polls
            _make_poll_result("SUCCEEDED"),
            _make_poll_result("SUCCEEDED"),
            _make_poll_result("SUCCEEDED"),
            _make_poll_result("SUCCEEDED"),
            _make_poll_result("SUCCEEDED"),
        ]
        _result, _cache = await self._run_tool(mock_ctx, csv_file, mock_client, poll_values)

        assert catalog_get_calls == 1, f"Expected 1 catalog fetch, got {catalog_get_calls}"

    async def test_return_envelope_includes_assignment_counts(
        self, mock_ctx: MagicMock, tmp_path: pathlib.Path
    ) -> None:
        """Return envelope must include six new assignment count fields."""
        rows = [
            {
                "serialNumber": "SN001",
                "macAddress": "11:22:33:44:55:01",
                "service": "Aruba Central",
                "subscriptionKey": "KEY001",
            },
            {"serialNumber": "SN002", "macAddress": "11:22:33:44:55:02"},  # no assignment columns
        ]
        csv_file = _write_csv(tmp_path, rows)
        mock_client = self._make_client()
        mock_client.get = AsyncMock(
            side_effect=[
                {"items": [{"id": "app-uuid-001", "name": "Aruba Central", "region": "us-west"}]},
                {"items": [{"id": "sub-uuid-001"}]},
            ]
        )
        mock_client.patch_raw = AsyncMock(
            side_effect=[
                _make_success_patch_response("patch-svc"),
                _make_success_patch_response("patch-sub"),
            ]
        )

        poll_values = [
            _make_poll_result(
                "SUCCEEDED",
                [
                    {"serialNumber": "SN001", "id": "dev-uuid-001", "status": "SUCCEEDED"},
                    {"serialNumber": "SN002", "id": "dev-uuid-002", "status": "SUCCEEDED"},
                ],
            ),
            _make_poll_result("SUCCEEDED"),
            _make_poll_result("SUCCEEDED"),
        ]
        result, _cache = await self._run_tool(mock_ctx, csv_file, mock_client, poll_values)

        for field in (
            "service_succeeded",
            "service_failed",
            "service_skipped",
            "subscription_succeeded",
            "subscription_failed",
            "subscription_skipped",
        ):
            assert field in result, f"Missing field '{field}' in return envelope"
            assert isinstance(result[field], int), f"Field '{field}' must be int, got {type(result[field])}"

        # SN001: service succeeded, subscription succeeded
        # SN002: no columns → skipped
        assert result["service_succeeded"] == 1
        assert result["service_skipped"] == 1
        assert result["subscription_succeeded"] == 1
        assert result["subscription_skipped"] == 1

    async def test_subscription_status_recorded_with_sanitized_reason(
        self, mock_ctx: MagicMock, tmp_path: pathlib.Path
    ) -> None:
        """T-20-02: control characters in response.text must be stripped from cache reason."""
        sn = "SN001"
        csv_file = _write_csv(
            tmp_path,
            [{"serialNumber": sn, "macAddress": "11:22:33:44:55:01", "subscriptionKey": "KEY001"}],
        )
        mock_client = self._make_client()
        mock_client.get = AsyncMock(
            side_effect=[
                {"items": [{"id": "sub-uuid-001"}]},
            ]
        )

        bad_response = _make_fail_patch_response(422, "ERROR: \x00\x01attacker text")
        mock_client.patch_raw = AsyncMock(return_value=bad_response)

        poll_values = [
            _make_poll_result("SUCCEEDED", [{"serialNumber": sn, "id": "dev-uuid-001", "status": "SUCCEEDED"}]),
        ]
        _result, _cache = await self._run_tool(mock_ctx, csv_file, mock_client, poll_values)

        cache = _cache
        reason = cache[sn].get("subscription_reason", "")
        assert "\x00" not in (reason or ""), "Control char \\x00 found in reason"
        assert "\x01" not in (reason or ""), "Control char \\x01 found in reason"

    async def test_patch_endpoints_use_v2beta1(self, mock_ctx: MagicMock, tmp_path: pathlib.Path) -> None:
        """A3: all assignment PATCHes must target /devices/v2beta1/devices?id=..."""
        sn = "SN001"
        csv_file = _write_csv(
            tmp_path,
            [
                {
                    "serialNumber": sn,
                    "macAddress": "11:22:33:44:55:01",
                    "service": "Aruba Central",
                    "subscriptionKey": "KEY001",
                }
            ],
        )
        mock_client = self._make_client()
        mock_client.get = AsyncMock(
            side_effect=[
                {"items": [{"id": "app-uuid-001", "name": "Aruba Central", "region": "us-west"}]},
                {"items": [{"id": "sub-uuid-001"}]},
            ]
        )
        mock_client.patch_raw = AsyncMock(
            side_effect=[
                _make_success_patch_response("patch-svc"),
                _make_success_patch_response("patch-sub"),
            ]
        )
        poll_values = [
            _make_poll_result("SUCCEEDED", [{"serialNumber": sn, "id": "dev-uuid-001", "status": "SUCCEEDED"}]),
            _make_poll_result("SUCCEEDED"),
            _make_poll_result("SUCCEEDED"),
        ]
        _result, _cache = await self._run_tool(mock_ctx, csv_file, mock_client, poll_values)

        calls = mock_client.patch_raw.call_args_list
        assert len(calls) >= 2, "Expected at least 2 PATCH calls"
        for call in calls:
            endpoint = call.args[0] if call.args else call.kwargs.get("endpoint", "")
            assert endpoint == "/devices/v2beta1/devices", f"Unexpected endpoint: {endpoint!r}"
            params = call.kwargs.get("params", {})
            assert "id" in params, f"Missing 'id' query param in PATCH call params: {params!r}"
            assert "/devices/v1/devices" not in endpoint, f"v1 endpoint used: {endpoint!r}"

    async def test_succeeded_status_preserved_through_phase20(
        self, mock_ctx: MagicMock, tmp_path: pathlib.Path
    ) -> None:
        """D-04: Phase 19 'status' field must NOT be overwritten by Phase 20 assignment."""
        sn = "SN001"
        csv_file = _write_csv(
            tmp_path,
            [
                {
                    "serialNumber": sn,
                    "macAddress": "11:22:33:44:55:01",
                    "service": "Aruba Central",
                    "subscriptionKey": "KEY001",
                }
            ],
        )
        mock_client = self._make_client()
        mock_client.get = AsyncMock(
            side_effect=[
                {"items": [{"id": "app-uuid-001", "name": "Aruba Central", "region": "us-west"}]},
                {"items": [{"id": "sub-uuid-001"}]},
            ]
        )
        mock_client.patch_raw = AsyncMock(
            side_effect=[
                _make_success_patch_response("patch-svc"),
                _make_success_patch_response("patch-sub"),
            ]
        )
        poll_values = [
            _make_poll_result("SUCCEEDED", [{"serialNumber": sn, "id": "dev-uuid-001", "status": "SUCCEEDED"}]),
            _make_poll_result("SUCCEEDED"),
            _make_poll_result("SUCCEEDED"),
        ]
        _result, _cache = await self._run_tool(mock_ctx, csv_file, mock_client, poll_values)

        cache = _cache
        # Phase 19 status field must be exactly "succeeded" — Phase 20 must not overwrite it
        assert cache[sn]["status"] == "succeeded", f"Phase 19 status was overwritten: {cache[sn].get('status')!r}"

    async def test_batch_422_leaves_phase20_fields_absent(self, mock_ctx: MagicMock, tmp_path: pathlib.Path) -> None:
        """Batch-level 422 POST failure → cache row has no Phase 20 fields at all.

        Distinguishes from the per-item failure path (test_not_applicable_when_phase19_failed)
        where the batch POST succeeds but a per-item status is FAILED — that path runs
        _assign_for_row and writes 'not_applicable' to service_status.  A batch-level 422
        never reaches Section 6f.5, so service_status/subscription_status are absent entirely.
        Section 10 reads these with defensive .get(), so callers must not assume their presence.
        """
        sn = "SN-422"
        csv_file = _write_csv(
            tmp_path,
            [
                {
                    "serialNumber": sn,
                    "macAddress": "AA:BB:CC:DD:EE:FF",
                    "service": "Aruba Central",
                    "subscriptionKey": "KEY1",
                }
            ],
        )
        # POST returns 422 → batch-level failure, Section 6f.5 is never reached
        mock_client = self._make_client(post_side_effect=_make_fail_post_response(422, "conflict"))
        _result, final_cache = await self._run_tool(mock_ctx, csv_file, mock_client, poll_return_values=[])

        # The cache entry must exist (batch-level failure still writes a "failed" row)
        assert sn in final_cache, f"Expected {sn!r} in cache; keys={list(final_cache)}"
        # Phase 20 assignment fields must be ABSENT — not "not_applicable", not present at all
        assert "service_status" not in final_cache[sn], (
            f"service_status should be absent for batch-422 failure, got {final_cache[sn].get('service_status')!r}"
        )
        assert "subscription_status" not in final_cache[sn], (
            f"subscription_status should be absent for batch-422 failure, got "
            f"{final_cache[sn].get('subscription_status')!r}"
        )


# ---------------------------------------------------------------------------
# Regression test — TIMEDOUT terminal state (20-01-02)
# ---------------------------------------------------------------------------


async def test_poll_timedout_terminal() -> None:
    """TIMEDOUT must be recognized as a terminal state — poll exits on first observation.

    Regression for Phase 19 bug: TIMEOUT was the only timeout spelling in the terminal
    tuple; the GreenLake OpenAPI AsyncOperationResource.status enum uses TIMEDOUT (one word).
    Without this fix the poll loop spins MAX_POLL_ATTEMPTS times before returning None.
    """
    mock_client = MagicMock()
    mock_client.get = AsyncMock(return_value={"status": "TIMEDOUT", "id": "op-123"})

    result = await _poll_async_operation(mock_client, "op-123")

    assert result is not None
    assert result["status"] == "TIMEDOUT"
    assert mock_client.get.call_count == 1
