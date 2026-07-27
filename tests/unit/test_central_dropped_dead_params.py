"""Regression tests: dead query-param arguments were removed from Central tools.

Live testing confirmed these params cause HTTP 400 "Unknown query parameter" on
the New Central API:
  * the AP/gateway/switch/cluster *trend* endpoints accept no time-window param —
    both ``start``/``end`` AND ``start-at``/``end-at`` 400, and no-params returns
    200 — so ``start``/``end`` were removed from the 13 trend tools;
  * ``filter`` is rejected on the 9 tools below (400), so it was removed.

These tests pin those params as *gone* from the tool signatures, so a future
edit can't silently re-introduce a param that only ever produces a 400.
"""

from __future__ import annotations

import importlib
import inspect

import pytest

pytestmark = pytest.mark.unit

_MOD = "hpe_networking_mcp.platforms.central.tools."

# (module, tool) -> the dead param that must NOT be in the signature
_TREND_TOOLS = [
    ("mrt_ap", "central_get_ap_trend"),
    ("mrt_ap", "central_get_ap_radio_trend"),
    ("mrt_ap", "central_get_ap_port_trend"),
    ("mrt_ap", "central_get_ap_tunnel_trend"),
    ("mrt_ap", "central_get_ap_wlan_throughput"),
    ("mrt_gateway", "central_get_gateway_trend"),
    ("mrt_gateway", "central_get_gateway_port_trend"),
    ("mrt_gateway", "central_get_gateway_tunnel_trend"),
    ("mrt_gateway", "central_get_gateway_uplink_trend"),
    ("mrt_gateway", "central_get_gateway_uplink_probe_performance"),
    ("mrt_gateway", "central_get_gateway_uplink_vpn_availability"),
    ("mrt_gateway", "central_get_cluster_capacity_trends"),
    ("mrt_switch", "central_get_switch_interface_trends"),
]
_FILTER_TOOLS = [
    ("mrt_clients", "central_get_client_onboarding_score"),
    ("mrt_clients", "central_get_client_onboarding_stage_count"),
    ("mrt_clients", "central_get_client_onboarding_stage_export"),
    ("mrt_clients", "central_get_client_onboarding_stage_reasons"),
    ("mrt_health", "central_get_tenant_client_health"),
    ("mrt_health", "central_get_tenant_device_health"),
    ("mrt_insights", "central_get_insights"),
    ("mrt_troubleshooting", "central_get_event_extra_attributes"),
    ("mrt_services", "central_get_location_analytics_site_insights"),
]


def _params(module: str, tool: str) -> set[str]:
    fn = getattr(importlib.import_module(_MOD + module), tool)
    return set(inspect.signature(fn).parameters)


@pytest.mark.parametrize(("module", "tool"), _TREND_TOOLS)
def test_trend_tools_have_no_time_window_params(module, tool):
    params = _params(module, tool)
    assert "start" not in params, f"{tool} still exposes a dead 'start' param"
    assert "end" not in params, f"{tool} still exposes a dead 'end' param"


@pytest.mark.parametrize(("module", "tool"), _FILTER_TOOLS)
def test_filter_rejecting_tools_have_no_filter_param(module, tool):
    assert "filter" not in _params(module, tool), f"{tool} still exposes a dead 'filter' param"


def test_time_params_helper_is_gone():
    # The shared helper that built the dead start/end params was removed.
    for module in ("mrt_ap", "mrt_gateway"):
        mod = importlib.import_module(_MOD + module)
        assert not hasattr(mod, "_time_params"), f"{module}._time_params should be removed"
