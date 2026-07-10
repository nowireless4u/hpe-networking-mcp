"""Tests for the GreenLake bulk-add hardening batch (#591–#594)."""

from __future__ import annotations

import pathlib
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastmcp.exceptions import ToolError

from hpe_networking_mcp.platforms.greenlake.tools.bulk_add import (
    _poll_async_operation,
    greenlake_bulk_add_devices,
)
from hpe_networking_mcp.platforms.greenlake.utils.csv_parser import parse_csv

pytestmark = pytest.mark.unit

_BULK = "hpe_networking_mcp.platforms.greenlake.tools.bulk_add"


def _ctx() -> MagicMock:
    ctx = MagicMock()
    ctx.report_progress = AsyncMock()
    ctx.info = AsyncMock()
    ctx.session_id = "test-session"
    ctx.lifespan_context = {"greenlake_token_manager": MagicMock(), "config": MagicMock(), "token_store": None}
    ctx.lifespan_context["config"].greenlake.api_base_url = "https://api.test.hpe.com"
    return ctx


def _limiter() -> MagicMock:
    m = MagicMock()
    m.__aenter__ = AsyncMock(return_value=None)
    m.__aexit__ = AsyncMock(return_value=False)
    return m


def _accepted_response() -> MagicMock:
    r = MagicMock()
    r.status_code = 202
    r.headers = {"location": "/devices/v1/async-operations/op-1"}
    return r


async def _run_tool_with_poll(ctx, csv_file, poll_result):
    """Drive greenlake_bulk_add_devices with a mocked client + crafted poll result."""
    client = MagicMock()
    client.post_raw = AsyncMock(return_value=_accepted_response())
    # device-id lookup GET for any SUCCEEDED row (assignment/enrichment path)
    client.get = AsyncMock(return_value={"items": [{"id": "uuid-x"}]})
    client.close = AsyncMock()
    limiter = _limiter()
    with (
        patch(f"{_BULK}.get_greenlake_client", return_value=client),
        patch(f"{_BULK}._poll_async_operation", new=AsyncMock(return_value=poll_result)),
        patch(f"{_BULK}.AsyncLimiter", return_value=limiter),
        patch(f"{_BULK}.make_patch_limiter", return_value=limiter),
    ):
        return await greenlake_bulk_add_devices(ctx, csv_path=str(csv_file))


def _one_row_csv(tmp_path: pathlib.Path, serial: str = "SN001") -> pathlib.Path:
    f = tmp_path / "d.csv"
    f.write_text(f"serialNumber,macAddress\n{serial},11:22:33:44:55:66\n", encoding="utf-8")
    return f


# ---------------------------------------------------------------------------
# #591 — poll transport containment
# ---------------------------------------------------------------------------


class TestPollContainment:
    async def test_retries_transient_transport_error(self) -> None:
        client = MagicMock()
        client.get = AsyncMock(side_effect=[RuntimeError("boom"), RuntimeError("boom"), {"status": "SUCCEEDED"}])
        with patch(f"{_BULK}.POLL_INTERVAL_SECONDS", 0):
            result = await _poll_async_operation(client, "op-x")
        assert result is not None and result["status"] == "SUCCEEDED"
        assert client.get.call_count == 3

    async def test_persistent_transport_error_returns_none_not_raise(self) -> None:
        client = MagicMock()
        client.get = AsyncMock(side_effect=RuntimeError("down"))
        with (
            patch(f"{_BULK}.MAX_POLL_ATTEMPTS", 3),
            patch(f"{_BULK}.POLL_INTERVAL_SECONDS", 0),
        ):
            result = await _poll_async_operation(client, "op-x")
        assert result is None  # contained → caller marks timed_out, never raises
        assert client.get.call_count == 3


class TestPostContainment:
    async def test_post_transport_error_marks_unconfirmed_not_definite_failure(self, tmp_path: pathlib.Path) -> None:
        # Casey #609: a POST timeout/reset after send may have been accepted
        # server-side, so it must be recorded as unknown (timed_out), not a
        # definite failure claiming the devices were never accepted.
        csv_file = _one_row_csv(tmp_path)
        client = MagicMock()
        client.post_raw = AsyncMock(side_effect=RuntimeError("connection reset"))
        client.get = AsyncMock(return_value={"items": []})
        client.close = AsyncMock()
        limiter = _limiter()
        with (
            patch(f"{_BULK}.get_greenlake_client", return_value=client),
            patch(f"{_BULK}.AsyncLimiter", return_value=limiter),
            patch(f"{_BULK}.make_patch_limiter", return_value=limiter),
        ):
            result = await greenlake_bulk_add_devices(_ctx(), csv_path=str(csv_file))
        # Run continued (no raw exception) and the batch counts as not-succeeded.
        assert result["succeeded"] == 0
        assert result["failed"] == 1  # timed_out rolls into the failed total
        assert result["failures"]
        reason = result["failures"][0]["reason"].lower()
        assert "unknown" in reason or "transport" in reason


# ---------------------------------------------------------------------------
# #592 — fail closed on FAILED / empty result
# ---------------------------------------------------------------------------


class TestFailClosed:
    async def test_failed_no_result_does_not_synthesize_success(self, tmp_path: pathlib.Path) -> None:
        csv_file = _one_row_csv(tmp_path)
        result = await _run_tool_with_poll(_ctx(), csv_file, {"status": "FAILED"})
        assert result["succeeded"] == 0
        assert result["failed"] == 1

    async def test_failed_empty_dict_result_does_not_synthesize_success(self, tmp_path: pathlib.Path) -> None:
        csv_file = _one_row_csv(tmp_path)
        result = await _run_tool_with_poll(_ctx(), csv_file, {"status": "FAILED", "result": {}})
        assert result["succeeded"] == 0
        assert result["failed"] == 1

    async def test_shape_c_partial_success_preserved(self, tmp_path: pathlib.Path) -> None:
        # Explicit failedDevicesSerial breakdown → listed fails, the rest onboard.
        f = tmp_path / "two.csv"
        f.write_text(
            "serialNumber,macAddress\nSN001,11:22:33:44:55:66\nSN002,11:22:33:44:55:67\n",
            encoding="utf-8",
        )
        poll = {"status": "FAILED", "result": {"failedDevicesSerial": ["SN001"]}}
        result = await _run_tool_with_poll(_ctx(), f, poll)
        assert result["succeeded"] == 1  # SN002
        assert result["failed"] == 1  # SN001


# ---------------------------------------------------------------------------
# #593 — CSV hygiene
# ---------------------------------------------------------------------------


class TestCsvHygiene:
    def test_short_row_reported_not_crashed(self) -> None:
        # Second data row is short (missing macAddress column) → None value.
        text = "serialNumber,macAddress\nSN001,11:22:33:44:55:66\nSN002\n"
        result = parse_csv(None, text)
        assert result.error is None
        assert len(result.valid_rows) == 1  # SN001 only
        assert any(r.get("serial") == "SN002" or "missing macAddress" in r["error"] for r in result.invalid_rows)

    def test_bom_in_csv_text_stripped(self) -> None:
        text = "\ufeffserialNumber,macAddress\nSN001,11:22:33:44:55:66\n"
        result = parse_csv(None, text)
        assert result.error is None  # BOM no longer breaks schema validation
        assert len(result.valid_rows) == 1

    def test_duplicate_serials_rejected(self) -> None:
        text = "serialNumber,macAddress\nSN001,11:22:33:44:55:66\nSN001,11:22:33:44:55:67\n"
        result = parse_csv(None, text)
        assert len(result.valid_rows) == 1  # first SN001
        assert any("duplicate" in r["error"].lower() for r in result.invalid_rows)

    def test_duplicate_serials_case_insensitive(self) -> None:
        # validate_row uppercases, so sn001 and SN001 collide.
        text = "serialNumber,macAddress\nsn001,11:22:33:44:55:66\nSN001,11:22:33:44:55:67\n"
        result = parse_csv(None, text)
        assert len(result.valid_rows) == 1
        assert any("duplicate" in r["error"].lower() for r in result.invalid_rows)


# ---------------------------------------------------------------------------
# #594 — guarded client
# ---------------------------------------------------------------------------


class TestGuardedClient:
    async def test_none_token_manager_raises_503(self, tmp_path: pathlib.Path) -> None:
        ctx = _ctx()
        ctx.lifespan_context["greenlake_token_manager"] = None  # startup failed / not configured
        csv_file = _one_row_csv(tmp_path)
        with pytest.raises(ToolError) as ei:
            await greenlake_bulk_add_devices(ctx, csv_path=str(csv_file))
        assert ei.value.args[0]["status_code"] == 503
