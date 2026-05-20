"""Unit tests for central config_health tools (v3.1.0.1).

Tests the two new diagnostic tools that wrap the New Central Configuration
API config-health surface (``/network-config/v1alpha1/config-health/*``).
Mocks ``retry_central_command`` at the import site — it's the only thing
the wrappers call besides ``ctx.lifespan_context["central_conn"]``.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

pytestmark = pytest.mark.unit


def _ctx() -> MagicMock:
    ctx = MagicMock()
    ctx.lifespan_context = {"central_conn": MagicMock()}
    return ctx


class TestCentralGetDeviceConfigIssues:
    @patch("hpe_networking_mcp.platforms.central.tools.config_health.retry_central_command")
    async def test_passes_serial_to_correct_endpoint(self, mock_cmd):
        from hpe_networking_mcp.platforms.central.tools.config_health import (
            central_get_device_config_issues,
        )

        mock_cmd.return_value = {"code": 200, "msg": {"issues": [{"id": "x"}]}}
        result = await central_get_device_config_issues(_ctx(), serial="ABC123")

        mock_cmd.assert_called_once()
        kwargs = mock_cmd.call_args.kwargs
        assert kwargs["api_method"] == "GET"
        assert kwargs["api_path"] == "network-config/v1alpha1/config-health/active-issue"
        assert kwargs["api_params"] == {"serial": "ABC123"}
        assert result == {"issues": [{"id": "x"}]}

    @patch("hpe_networking_mcp.platforms.central.tools.config_health.retry_central_command")
    async def test_missing_msg_returns_empty_dict(self, mock_cmd):
        """If the response omits 'msg' for any reason, return {} rather than raising."""
        from hpe_networking_mcp.platforms.central.tools.config_health import (
            central_get_device_config_issues,
        )

        mock_cmd.return_value = {"code": 200}
        assert await central_get_device_config_issues(_ctx(), serial="X") == {}


class TestCentralGetDevicesConfigHealth:
    @patch("hpe_networking_mcp.platforms.central.tools.config_health.retry_central_command")
    async def test_defaults_pass_limit_and_offset(self, mock_cmd):
        from hpe_networking_mcp.platforms.central.tools.config_health import (
            central_get_devices_config_health,
        )

        mock_cmd.return_value = {"code": 200, "msg": {"items": [], "total": 0}}
        await central_get_devices_config_health(_ctx())

        kwargs = mock_cmd.call_args.kwargs
        assert kwargs["api_method"] == "GET"
        assert kwargs["api_path"] == "network-config/v1alpha1/config-health/devices"
        assert kwargs["api_params"] == {"limit": 100, "offset": 0}

    @patch("hpe_networking_mcp.platforms.central.tools.config_health.retry_central_command")
    async def test_all_optional_params_pass_through(self, mock_cmd):
        from hpe_networking_mcp.platforms.central.tools.config_health import (
            central_get_devices_config_health,
        )

        mock_cmd.return_value = {"code": 200, "msg": {}}
        await central_get_devices_config_health(
            _ctx(),
            limit=50,
            offset=10,
            sort="activeIssues desc",
            filter="configStatus eq 'OUT_OF_SYNC'",
            search="switch",
        )

        kwargs = mock_cmd.call_args.kwargs
        assert kwargs["api_params"] == {
            "limit": 50,
            "offset": 10,
            "sort": "activeIssues desc",
            "filter": "configStatus eq 'OUT_OF_SYNC'",
            "search": "switch",
        }

    @patch("hpe_networking_mcp.platforms.central.tools.config_health.retry_central_command")
    async def test_omits_none_optionals_from_query_params(self, mock_cmd):
        """sort/filter/search must NOT appear in api_params when None — keeps the query
        URL clean and avoids upstream rejecting unrecognized empty strings."""
        from hpe_networking_mcp.platforms.central.tools.config_health import (
            central_get_devices_config_health,
        )

        mock_cmd.return_value = {"code": 200, "msg": {}}
        await central_get_devices_config_health(_ctx(), limit=25, offset=0)

        kwargs = mock_cmd.call_args.kwargs
        assert kwargs["api_params"] == {"limit": 25, "offset": 0}

    @pytest.mark.parametrize("bad_search", ["", "ab", "x" * 129, "x" * 500])
    async def test_search_length_rejected(self, bad_search):
        """Search must be 3-128 chars per upstream OpenAPI. v3.2.1.0:
        validation failures raise ToolError(400) instead of returning a
        string."""
        from fastmcp.exceptions import ToolError

        from hpe_networking_mcp.platforms.central.tools.config_health import (
            central_get_devices_config_health,
        )

        with pytest.raises(ToolError) as exc_info:
            await central_get_devices_config_health(_ctx(), search=bad_search)
        assert exc_info.value.args[0]["status_code"] == 400
        assert "search must be 3-128 chars" in exc_info.value.args[0]["message"]

    @pytest.mark.parametrize("good_search", ["foo", "x" * 3, "x" * 128, "abc switch"])
    @patch("hpe_networking_mcp.platforms.central.tools.config_health.retry_central_command")
    async def test_search_length_accepted(self, mock_cmd, good_search):
        from hpe_networking_mcp.platforms.central.tools.config_health import (
            central_get_devices_config_health,
        )

        mock_cmd.return_value = {"code": 200, "msg": {"ok": True}}
        result = await central_get_devices_config_health(_ctx(), search=good_search)
        # Not a rejection string.
        assert not (isinstance(result, str) and "search must be" in result)
        # Search arg made it to the request.
        assert mock_cmd.call_args.kwargs["api_params"]["search"] == good_search
