"""Unit tests for the central_get_aps collection contract.

Pins the uniform collection shape (#491): ``central_get_aps`` returns
``{"items": [...]}`` so a model always reaches the rows via ``data["items"]``,
even when empty (``{"items": []}``) — never a bare list, name-keyed dict, or
human-string. (Supersedes the #244 bare-``[]`` contract.)
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
    @patch("hpe_networking_mcp.platforms.central.tools.monitoring.monitoring_api.get_all_aps", new_callable=AsyncMock)
    async def test_none_normalizes_to_empty_list(self, mock_get_all):
        from hpe_networking_mcp.platforms.central.tools.monitoring import central_get_aps

        mock_get_all.return_value = None
        assert await central_get_aps(_ctx()) == {"items": []}

    @patch("hpe_networking_mcp.platforms.central.tools.monitoring.monitoring_api.get_all_aps", new_callable=AsyncMock)
    async def test_empty_list_passes_through_as_empty_list(self, mock_get_all):
        from hpe_networking_mcp.platforms.central.tools.monitoring import central_get_aps

        mock_get_all.return_value = []
        assert await central_get_aps(_ctx()) == {"items": []}

    @patch("hpe_networking_mcp.platforms.central.tools.monitoring.monitoring_api.get_all_aps", new_callable=AsyncMock)
    async def test_populated_list_passes_through(self, mock_get_all):
        from hpe_networking_mcp.platforms.central.tools.monitoring import central_get_aps

        sample = [{"name": "AP-1", "serial": "ABC123"}, {"name": "AP-2", "serial": "DEF456"}]
        mock_get_all.return_value = sample
        assert await central_get_aps(_ctx()) == {"items": sample}

    @patch("hpe_networking_mcp.platforms.central.tools.monitoring.monitoring_api.get_all_aps", new_callable=AsyncMock)
    async def test_sdk_exception_raises_tool_error(self, mock_get_all):
        """v3.2.1.0: SDK exceptions now raise ToolError(502) instead of
        returning an error string."""
        from fastmcp.exceptions import ToolError

        from hpe_networking_mcp.platforms.central.tools.monitoring import central_get_aps

        mock_get_all.side_effect = RuntimeError("auth failed")
        with pytest.raises(ToolError) as exc_info:
            await central_get_aps(_ctx())
        assert exc_info.value.args[0]["status_code"] == 502
        assert "auth failed" in exc_info.value.args[0]["message"]
