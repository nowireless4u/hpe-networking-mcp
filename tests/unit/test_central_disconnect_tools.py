"""Unit tests for the Central MRT disconnect tools.

Regression coverage for the payload-contract bug: the AP/gateway disconnect
actions take specific body fields (``userMacAddress`` / ``networkName`` /
``clientMacAddress``), but the tools previously exposed a free-form ``payload``
dict with a misleading "{mac_address}" hint, so callers guessed wrong field
names and got HTTP 400. These tests pin the exact body each tool sends, plus
the ``_call`` ToolError behaviour (so upstream errors aren't masked to a
generic "Error calling tool" in code mode).
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from fastmcp.exceptions import ToolError

pytestmark = pytest.mark.unit

_CMD = "hpe_networking_mcp.platforms.central.tools.mrt_troubleshooting.retry_central_command"


def _ctx() -> MagicMock:
    ctx = MagicMock()
    ctx.lifespan_context = {"central_conn": MagicMock()}
    return ctx


class TestDisconnectBodies:
    @patch(_CMD)
    async def test_by_mac_on_ap_uses_user_mac_address(self, mock_cmd):
        from hpe_networking_mcp.platforms.central.tools.mrt_troubleshooting import (
            central_disconnect_user_by_mac_on_ap,
        )

        mock_cmd.return_value = {"code": 202, "msg": {"status": "INITIATED"}}
        await central_disconnect_user_by_mac_on_ap(_ctx(), serial_number="CNT123", user_mac_address="00:BD:3E:E4:8C:5D")
        kw = mock_cmd.call_args.kwargs
        assert kw["api_method"] == "POST"
        assert kw["api_path"] == "network-troubleshooting/v1/aps/CNT123/disconnectUserByMacAddress"
        assert kw["api_data"] == {"userMacAddress": "00:BD:3E:E4:8C:5D"}

    @patch(_CMD)
    async def test_by_network_uses_network_name(self, mock_cmd):
        from hpe_networking_mcp.platforms.central.tools.mrt_troubleshooting import (
            central_disconnect_user_by_network,
        )

        mock_cmd.return_value = {"code": 202, "msg": {}}
        await central_disconnect_user_by_network(_ctx(), serial_number="CNT123", network_name="CORP-WIFI")
        kw = mock_cmd.call_args.kwargs
        assert kw["api_path"] == "network-troubleshooting/v1/aps/CNT123/disconnectUserByNetwork"
        assert kw["api_data"] == {"networkName": "CORP-WIFI"}

    @patch(_CMD)
    async def test_by_mac_on_gateway_uses_client_mac_address(self, mock_cmd):
        from hpe_networking_mcp.platforms.central.tools.mrt_troubleshooting import (
            central_disconnect_client_by_mac_on_gateway,
        )

        mock_cmd.return_value = {"code": 202, "msg": {}}
        await central_disconnect_client_by_mac_on_gateway(
            _ctx(), serial_number="GW9", client_mac_address="aa:bb:cc:dd:ee:ff"
        )
        kw = mock_cmd.call_args.kwargs
        assert kw["api_path"] == "network-troubleshooting/v1/gateways/GW9/disconnectClientByMacAddress"
        assert kw["api_data"] == {"clientMacAddress": "aa:bb:cc:dd:ee:ff"}

    @patch(_CMD)
    async def test_all_on_ap_sends_empty_body(self, mock_cmd):
        from hpe_networking_mcp.platforms.central.tools.mrt_troubleshooting import (
            central_disconnect_user_all_on_ap,
        )

        mock_cmd.return_value = {"code": 202, "msg": {}}
        await central_disconnect_user_all_on_ap(_ctx(), serial_number="CNT123")
        kw = mock_cmd.call_args.kwargs
        assert kw["api_path"] == "network-troubleshooting/v1/aps/CNT123/disconnectUserAll"
        assert kw["api_data"] == {}

    @patch(_CMD)
    async def test_all_on_gateway_sends_empty_body(self, mock_cmd):
        from hpe_networking_mcp.platforms.central.tools.mrt_troubleshooting import (
            central_disconnect_client_all_on_gateway,
        )

        mock_cmd.return_value = {"code": 202, "msg": {}}
        await central_disconnect_client_all_on_gateway(_ctx(), serial_number="GW9")
        kw = mock_cmd.call_args.kwargs
        assert kw["api_path"] == "network-troubleshooting/v1/gateways/GW9/disconnectClientAll"
        assert kw["api_data"] == {}


class TestCallErrorSurfacing:
    @patch(_CMD)
    async def test_non_2xx_raises_tool_error_with_detail(self, mock_cmd):
        """A 4xx body must surface as a ToolError carrying the real message —
        not be masked to a generic 'Error calling tool' in code mode."""
        from hpe_networking_mcp.platforms.central.tools.mrt_troubleshooting import (
            central_disconnect_user_by_mac_on_ap,
        )

        mock_cmd.return_value = {
            "code": 400,
            "msg": {"message": "Bad Request", "errorCode": "HPE_GL_NETWORKING_ERROR_BAD_REQUEST"},
        }
        with pytest.raises(ToolError) as exc:
            await central_disconnect_user_by_mac_on_ap(_ctx(), serial_number="CNT123", user_mac_address="x")
        assert exc.value.args[0]["status_code"] == 400
        assert "Bad Request" in exc.value.args[0]["message"]

    @patch(_CMD)
    async def test_upstream_exception_wrapped_as_tool_error(self, mock_cmd):
        from hpe_networking_mcp.platforms.central.tools.mrt_troubleshooting import (
            central_disconnect_user_by_mac_on_ap,
        )

        mock_cmd.side_effect = Exception("Client error from central: {'code': 400}")
        with pytest.raises(ToolError) as exc:
            await central_disconnect_user_by_mac_on_ap(_ctx(), serial_number="CNT123", user_mac_address="x")
        assert exc.value.args[0]["status_code"] == 502
        assert "Client error from central" in exc.value.args[0]["message"]


class TestSwitchRename:
    def test_switch_tool_exists_and_old_name_gone(self):
        import hpe_networking_mcp.platforms.central.tools.actions as actions

        assert hasattr(actions, "central_disconnect_client_switch")
        assert not hasattr(actions, "central_disconnect_client_ap")
