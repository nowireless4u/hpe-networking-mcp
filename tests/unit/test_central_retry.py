"""Unit tests for retry_central_command's transient-failure backoff.

Without backoff, all retries fire in <1s and a brief upstream flap (e.g. the
degrading audit endpoint near its sunset) defeats every attempt. These tests
pin the exponential backoff and the eventual-success behaviour, with
``time.sleep`` patched so the suite stays fast.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from fastmcp.exceptions import ToolError

from hpe_networking_mcp.platforms.central.utils import (
    _retry_backoff_secs,
    retry_central_command,
)

pytestmark = pytest.mark.unit


def _conn(responses: list[dict]) -> MagicMock:
    """A fake pycentral conn whose .command returns the given responses in order."""
    conn = MagicMock()
    conn.command.side_effect = responses
    conn.logger = MagicMock()
    return conn


class TestRetryBackoff:
    def test_backoff_schedule_is_capped_exponential(self):
        assert _retry_backoff_secs(1) == 0.5
        assert _retry_backoff_secs(2) == 1.0
        assert _retry_backoff_secs(3) == 2.0
        assert _retry_backoff_secs(4) == 4.0
        # capped at 5.0
        assert _retry_backoff_secs(5) == 5.0
        assert _retry_backoff_secs(10) == 5.0

    @patch("hpe_networking_mcp.platforms.central.utils.time.sleep")
    def test_transient_500_then_success(self, mock_sleep):
        conn = _conn(
            [
                {"code": 500, "msg": {"message": "flap"}},
                {"code": 500, "msg": {"message": "flap"}},
                {"code": 200, "msg": {"audits": [{"id": "x"}]}},
            ]
        )
        resp = retry_central_command(conn, "GET", "network-services/v1/audits")
        assert resp["code"] == 200
        # rode out two flaps -> slept after attempts 1 and 2
        assert [c.args[0] for c in mock_sleep.call_args_list] == [0.5, 1.0]

    @patch("hpe_networking_mcp.platforms.central.utils.time.sleep")
    def test_429_is_retried_with_backoff(self, mock_sleep):
        conn = _conn([{"code": 429, "msg": {}}, {"code": 200, "msg": {"ok": True}}])
        resp = retry_central_command(conn, "GET", "network-monitoring/v1/devices/X")
        assert resp["code"] == 200
        assert [c.args[0] for c in mock_sleep.call_args_list] == [0.5]

    @patch("hpe_networking_mcp.platforms.central.utils.time.sleep")
    def test_exhausts_retries_then_raises_toolerror_without_sleeping_after_last(self, mock_sleep):
        conn = _conn([{"code": 503, "msg": {"message": "down"}}] * 5)
        with pytest.raises(ToolError) as exc:
            retry_central_command(conn, "GET", "network-services/v1/audits")
        # exhaustion preserves the last transient code, not a generic 500
        assert exc.value.args[0]["status_code"] == 503
        assert "after 5 attempts" in exc.value.args[0]["message"]
        # 5 attempts -> sleeps after attempts 1..4 only (no sleep after the last)
        assert [c.args[0] for c in mock_sleep.call_args_list] == [0.5, 1.0, 2.0, 4.0]

    @patch("hpe_networking_mcp.platforms.central.utils.time.sleep")
    def test_4xx_raises_toolerror_immediately_no_sleep(self, mock_sleep):
        conn = _conn([{"code": 400, "msg": {"message": "bad"}}])
        with pytest.raises(ToolError) as exc:
            retry_central_command(conn, "GET", "network-services/v1/audits")
        # real 4xx code is preserved (not masked, not relabelled 502)
        assert exc.value.args[0]["status_code"] == 400
        assert "bad" in exc.value.args[0]["message"]
        mock_sleep.assert_not_called()
