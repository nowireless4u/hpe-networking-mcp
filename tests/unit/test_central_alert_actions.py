"""Schema + registration tests for the v2.3.1.5 Central alert-action tools.

The actual API roundtrip is integration-tested out of band against a live
Central org; this file just verifies the model/cleaner pickup the new
``key`` field correctly and that all six tools are listed in the platform's
TOOLS catalog.

Avoids the ``importlib.reload`` fixture pattern (which clashes with enum
identity in ``configuration.py``) — relies on the existing
``test_central_dynamic_mode.py`` fixture to prove tool registration; this
file only checks the static TOOLS dict and the cleaner logic.
"""

from __future__ import annotations

import pytest

from hpe_networking_mcp.platforms.central import TOOLS
from hpe_networking_mcp.platforms.central.models import Alert
from hpe_networking_mcp.platforms.central.utils import clean_alert_data


@pytest.mark.unit
class TestAlertModelKey:
    def test_key_field_present_with_default_none(self) -> None:
        # Pre-v2.3.1.5 alerts had no ``key`` field. After this release the
        # field exists with a None default so old fixtures don't break.
        a = Alert(
            summary="x",
            cleared_reason=None,
            created_at="t",
            priority="High",
            updated_at=None,
            device_type=None,
            updated_by=None,
            name=None,
            status=None,
            category=None,
            severity=None,
        )
        assert a.key is None

    def test_clean_alert_data_picks_up_key(self) -> None:
        cleaned = clean_alert_data([{"key": "alert-001", "summary": "x", "createdAt": "t", "priority": "High"}])
        assert cleaned[0].key == "alert-001"

    def test_clean_alert_data_falls_back_to_id(self) -> None:
        cleaned = clean_alert_data([{"id": "alert-002", "summary": "x", "createdAt": "t", "priority": "High"}])
        assert cleaned[0].key == "alert-002"

    def test_clean_alert_data_falls_back_to_alert_id(self) -> None:
        # API field name ``alertId`` is camelCase; the test name uses
        # snake_case per project style.
        cleaned = clean_alert_data([{"alertId": "alert-003", "summary": "x", "createdAt": "t", "priority": "High"}])
        assert cleaned[0].key == "alert-003"

    def test_clean_alert_data_no_key_field_yields_none(self) -> None:
        cleaned = clean_alert_data([{"summary": "x", "createdAt": "t", "priority": "High"}])
        assert cleaned[0].key is None


@pytest.mark.unit
class TestAlertActionToolCatalog:
    """All six v2.3.1.5 alert tools must be listed under TOOLS['alerts'].
    Actual registration is exercised by ``test_central_dynamic_mode.py``.
    """

    EXPECTED_NEW_TOOLS = (
        "central_get_alert_classification",
        "central_get_alert_action_status",
        "central_clear_alerts",
        "central_defer_alerts",
        "central_reactivate_alerts",
        "central_set_alert_priority",
    )

    def test_all_six_tools_in_catalog(self) -> None:
        listed = set(TOOLS["alerts"])
        for name in self.EXPECTED_NEW_TOOLS:
            assert name in listed, f"{name} missing from TOOLS['alerts']"

    def test_existing_central_get_alerts_still_listed(self) -> None:
        # Sanity: the original alerts tool is still listed (we didn't
        # accidentally replace it with the new ones).
        assert "central_get_alerts" in TOOLS["alerts"]
