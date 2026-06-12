"""Unit tests for the config-assignment device-function allowlist.

Covers the EdgeConnect device-function additions (EC_VPNC, EC_BRANCH_GW)
from assignments.json's device-function enum (issue #419).
"""

from __future__ import annotations

import pytest

from hpe_networking_mcp.platforms.central.tools.config_assignments import (
    VALID_DEVICE_FUNCTIONS,
)

pytestmark = pytest.mark.unit


def test_edgeconnect_device_functions_present() -> None:
    """EC_VPNC and EC_BRANCH_GW (EdgeConnect) are valid device functions."""
    assert "EC_VPNC" in VALID_DEVICE_FUNCTIONS
    assert "EC_BRANCH_GW" in VALID_DEVICE_FUNCTIONS


def test_existing_device_functions_unchanged() -> None:
    """The EdgeConnect additions don't disturb the existing core functions."""
    for df in ("CAMPUS_AP", "MOBILITY_GW", "BRANCH_GW", "VPNC", "ALL"):
        assert df in VALID_DEVICE_FUNCTIONS
