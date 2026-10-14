"""Unit tests for the central WIDS tool.

Regression coverage for the API-version fix: the live route is
``network-services/v1/wids-monitored-aps`` — the tool previously called the
``v1alpha1`` variant, which gateway-404s. Same defect, same family, as the
audit-trail routes already covered in ``test_central_audit_logs.py``.

Probed read-only on the lab tenant (US-1) 2026-09-02:
``network-services/v1alpha1/wids-monitored-aps`` -> 404,
``network-services/v1/wids-monitored-aps``       -> 200.

Mocks ``retry_central_command`` at the import site, matching the audit-logs
tests.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

pytestmark = pytest.mark.unit


def _ctx() -> MagicMock:
    ctx = MagicMock()
    ctx.lifespan_context = {"central_conn": MagicMock()}
    return ctx


class TestCentralGetWidsMonitoredAps:
    @patch("hpe_networking_mcp.platforms.central.tools.wids.retry_central_command")
    async def test_uses_v1_path(self, mock_cmd):
        from hpe_networking_mcp.platforms.central.tools.wids import central_get_wids_monitored_aps

        mock_cmd.return_value = {"code": 200, "msg": {"items": [], "total": 0, "count": 0, "offset": 0}}
        result = await central_get_wids_monitored_aps(_ctx())

        kwargs = mock_cmd.call_args.kwargs
        assert kwargs["api_method"] == "GET"
        # The bug was v1alpha1; the live route is v1.
        assert kwargs["api_path"] == "network-services/v1/wids-monitored-aps"
        assert kwargs["api_params"] == {"limit": 100, "offset": 0}
        assert result == {"items": [], "total": 0, "count": 0, "offset": 0}

    @patch("hpe_networking_mcp.platforms.central.tools.wids.retry_central_command")
    async def test_structured_args_compose_odata_filter(self, mock_cmd):
        from hpe_networking_mcp.platforms.central.tools.wids import central_get_wids_monitored_aps

        mock_cmd.return_value = {"code": 200, "msg": {"items": []}}
        await central_get_wids_monitored_aps(_ctx(), classification="ROGUE", contained_only=True, site_id="s1")

        params = mock_cmd.call_args.kwargs["api_params"]
        assert params["filter"] == ("classification eq 'ROGUE' and containmentStatus eq 'CONTAINED' and siteId eq 's1'")

    @patch("hpe_networking_mcp.platforms.central.tools.wids.retry_central_command")
    async def test_mixing_raw_and_structured_filters_is_refused(self, mock_cmd):
        from hpe_networking_mcp.platforms.central.tools.wids import central_get_wids_monitored_aps

        result = await central_get_wids_monitored_aps(_ctx(), classification="ROGUE", odata_filter="signal gt -70")
        assert isinstance(result, str) and result.startswith("Error:")
        mock_cmd.assert_not_called()

    @patch("hpe_networking_mcp.platforms.central.tools.wids.retry_central_command")
    async def test_non_2xx_returns_error_envelope(self, mock_cmd):
        from hpe_networking_mcp.platforms.central.tools.wids import central_get_wids_monitored_aps

        mock_cmd.return_value = {"code": 404, "msg": {"message": "404 Route Not Found"}}
        result = await central_get_wids_monitored_aps(_ctx())
        assert result["status"] == "error"
        assert result["code"] == 404
