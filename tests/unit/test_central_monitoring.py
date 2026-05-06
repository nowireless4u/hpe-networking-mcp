"""Unit tests for central_get_aps empty-list contract.

Pin the contract for issue #244: when ``MonitoringAPs.get_all_aps()`` returns
an empty result (None or []), ``central_get_aps`` must return ``[]`` so callers
can iterate without ``None``-guards. Earlier behavior returned the human-string
``"No access points found matching the specified criteria."``, which broke
``len(result)`` and ``for ap in result`` patterns.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

pytestmark = pytest.mark.unit


def _ctx() -> MagicMock:
    ctx = MagicMock()
    ctx.lifespan_context = {"central_conn": MagicMock()}
    ctx.get_state = AsyncMock(return_value="prompt")
    return ctx


class TestCentralGetApsEmptyContract:
    @patch("hpe_networking_mcp.platforms.central.tools.monitoring.MonitoringAPs.get_all_aps")
    async def test_none_normalizes_to_empty_list(self, mock_get_all):
        from hpe_networking_mcp.platforms.central.tools.monitoring import central_get_aps

        mock_get_all.return_value = None
        assert await central_get_aps(_ctx()) == []

    @patch("hpe_networking_mcp.platforms.central.tools.monitoring.MonitoringAPs.get_all_aps")
    async def test_empty_list_passes_through_as_empty_list(self, mock_get_all):
        from hpe_networking_mcp.platforms.central.tools.monitoring import central_get_aps

        mock_get_all.return_value = []
        assert await central_get_aps(_ctx()) == []

    @patch("hpe_networking_mcp.platforms.central.tools.monitoring.MonitoringAPs.get_all_aps")
    async def test_populated_list_passes_through(self, mock_get_all):
        from hpe_networking_mcp.platforms.central.tools.monitoring import central_get_aps

        sample = [{"name": "AP-1", "serial": "ABC123"}, {"name": "AP-2", "serial": "DEF456"}]
        mock_get_all.return_value = sample
        assert await central_get_aps(_ctx()) == sample

    @patch("hpe_networking_mcp.platforms.central.tools.monitoring.MonitoringAPs.get_all_aps")
    async def test_sdk_exception_returns_error_string(self, mock_get_all):
        from hpe_networking_mcp.platforms.central.tools.monitoring import central_get_aps

        mock_get_all.side_effect = RuntimeError("auth failed")
        result = await central_get_aps(_ctx())
        assert isinstance(result, str)
        assert "auth failed" in result
