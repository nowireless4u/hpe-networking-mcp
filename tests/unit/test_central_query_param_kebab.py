"""Regression tests for kebab-case query-param names on Central monitoring/
notification tools.

Unlike the ``network-config`` API (which silently *ignores* unknown query
params), the ``network-monitoring`` and ``network-notifications`` APIs **reject**
them with HTTP 400 "Unknown query parameter". These tools previously sent the
wrong names — ``start`` / ``end`` instead of the documented ``start-at`` /
``end-at``, and camelCase ``scopeId`` / ``scopeType`` instead of ``scope-id`` /
``scope-type`` — so scoped/time-windowed reads 400'd. Confirmed against the live
API and the vendored New Central OAS.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

pytestmark = pytest.mark.unit


def _ctx() -> MagicMock:
    ctx = MagicMock()
    ctx.lifespan_context = {"central_conn": MagicMock()}
    return ctx


@patch("hpe_networking_mcp.platforms.central.tools.mrt_clients.retry_central_command")
async def test_mobility_trail_sends_start_at_end_at(mock_cmd):
    from hpe_networking_mcp.platforms.central.tools.mrt_clients import central_get_client_mobility_trail

    mock_cmd.return_value = {"code": 200, "msg": {}}
    await central_get_client_mobility_trail(_ctx(), mac_address="d8:eb:46:0f:12:fb", start="T0", end="T1")

    params = mock_cmd.call_args.kwargs["api_params"]
    assert params == {"start-at": "T0", "end-at": "T1"}
    assert "start" not in params and "end" not in params


@patch("hpe_networking_mcp.platforms.central.tools.mrt_services.retry_central_command")
async def test_location_analytics_trends_sends_start_at_end_at(mock_cmd):
    from hpe_networking_mcp.platforms.central.tools.mrt_services import central_get_location_analytics_trends

    mock_cmd.return_value = {"code": 200, "msg": {}}
    await central_get_location_analytics_trends(_ctx(), start="T0", end="T1")

    params = mock_cmd.call_args.kwargs["api_params"]
    assert params.get("start-at") == "T0" and params.get("end-at") == "T1"
    assert "start" not in params and "end" not in params


@patch("hpe_networking_mcp.platforms.central.tools.alert_configs.retry_central_command")
async def test_get_alert_configs_sends_kebab_scope_params(mock_cmd):
    from hpe_networking_mcp.platforms.central.tools.alert_configs import central_get_alert_configs

    mock_cmd.return_value = {"code": 200, "msg": {}}
    await central_get_alert_configs(_ctx(), scope_id="site-123", scope_type="SITE")

    params = mock_cmd.call_args.kwargs["api_params"]
    assert params == {"scope-id": "site-123", "scope-type": "SITE"}
    assert "scopeId" not in params and "scopeType" not in params
