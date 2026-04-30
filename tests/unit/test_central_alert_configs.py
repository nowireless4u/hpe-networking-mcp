"""Catalog tests for the v2.3.1.6 Central alert-config tools.

Static-only checks against ``TOOLS`` to avoid the ``importlib.reload``
clash with ``configuration.py``'s ``ActionType`` enum identity that we
hit in v2.3.1.5 alert-action tests. Actual tool registration is
exercised by ``test_central_dynamic_mode.py``'s fixture.
"""

from __future__ import annotations

import pytest

from hpe_networking_mcp.platforms.central import TOOLS


@pytest.mark.unit
class TestAlertConfigToolCatalog:
    """All four v2.3.1.6 alert-config tools are listed under TOOLS['alert_configs']."""

    EXPECTED_TOOLS = (
        "central_get_alert_configs",
        "central_create_alert_config",
        "central_update_alert_config",
        "central_reset_alert_config",
    )

    def test_all_four_tools_in_catalog(self) -> None:
        listed = set(TOOLS["alert_configs"])
        for name in self.EXPECTED_TOOLS:
            assert name in listed, f"{name} missing from TOOLS['alert_configs']"

    def test_alerts_category_unchanged_by_split(self) -> None:
        # Sanity: the v2.3.1.5 alert-action tools still live under
        # TOOLS['alerts'] — splitting alert configs into a new module
        # didn't accidentally move them.
        listed = set(TOOLS["alerts"])
        assert "central_get_alerts" in listed
        assert "central_clear_alerts" in listed
        assert "central_get_alert_classification" in listed
        # And confirm none of the alert-config tools landed in the wrong bucket
        for name in self.EXPECTED_TOOLS:
            assert name not in listed, f"{name} should be under alert_configs, not alerts"
