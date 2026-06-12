"""Unit tests for ``central_cable_test`` poll-budget parameters.

Regression coverage for issue #382: the tool is fire-and-poll (the ported
``cable_test`` polls up to ``max_attempts * poll_interval`` seconds), which
can breach the code-mode sandbox wall-clock budget. The tool now exposes
``max_attempts`` / ``poll_interval`` (validated, 1-10) and forwards them to
the async monitoring_api port.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastmcp.exceptions import ToolError

from hpe_networking_mcp.platforms.central.tools.troubleshooting import central_cable_test

pytestmark = pytest.mark.unit

_CABLE = "hpe_networking_mcp.platforms.central.tools.troubleshooting.monitoring_api.cable_test"
_RESOLVE = "hpe_networking_mcp.platforms.central.tools.troubleshooting._resolve_if_switch"


def _ctx() -> MagicMock:
    ctx = MagicMock()
    ctx.lifespan_context = {"central_conn": MagicMock()}
    return ctx


class TestCableTestPolling:
    @patch(_RESOLVE, new_callable=AsyncMock, return_value="SW1")
    @patch(_CABLE, new_callable=AsyncMock)
    async def test_defaults_forward_5_by_5(self, mock_cable, _mock_resolve):
        mock_cable.return_value = {"ports": []}
        await central_cable_test(_ctx(), serial_number="SW1", device_type="cx", ports="1/1/1")
        kw = mock_cable.call_args.kwargs
        assert kw["max_attempts"] == 5
        assert kw["poll_interval"] == 5

    @patch(_RESOLVE, new_callable=AsyncMock, return_value="SW1")
    @patch(_CABLE, new_callable=AsyncMock)
    async def test_custom_poll_params_forwarded(self, mock_cable, _mock_resolve):
        mock_cable.return_value = {"ports": []}
        await central_cable_test(
            _ctx(), serial_number="SW1", device_type="cx", ports="1/1/1", max_attempts=2, poll_interval=1
        )
        kw = mock_cable.call_args.kwargs
        assert kw["max_attempts"] == 2
        assert kw["poll_interval"] == 1

    @pytest.mark.parametrize("max_attempts", [0, 11, -1])
    async def test_invalid_max_attempts_raises_400(self, max_attempts):
        with pytest.raises(ToolError) as exc:
            await central_cable_test(
                _ctx(), serial_number="SW1", device_type="cx", ports="1/1/1", max_attempts=max_attempts
            )
        assert exc.value.args[0]["status_code"] == 400

    @pytest.mark.parametrize("poll_interval", [0, 11, -1])
    async def test_invalid_poll_interval_raises_400(self, poll_interval):
        with pytest.raises(ToolError) as exc:
            await central_cable_test(
                _ctx(), serial_number="SW1", device_type="cx", ports="1/1/1", poll_interval=poll_interval
            )
        assert exc.value.args[0]["status_code"] == 400

    @patch(_RESOLVE, new_callable=AsyncMock, return_value="SW1")
    @patch(_CABLE, new_callable=AsyncMock)
    async def test_empty_result_returns_info_string(self, mock_cable, _mock_resolve):
        mock_cable.return_value = None
        result = await central_cable_test(_ctx(), serial_number="SW1", device_type="cx", ports="1/1/1")
        assert result == "Cable test returned no results."
