"""Unit tests for ``translations/preprocessing/aos8_mac_auth.py``.

Covers the mac_auth_profile normalizer: scalar unwrapping, the MAC-formatting
enums, presence flags, and ``_flags.default`` skipping. Generic placeholder
data only.
"""

from __future__ import annotations

import pytest

from hpe_networking_mcp.translations.preprocessing.aos8_mac_auth import (
    preprocess_mac_auth,
)

pytestmark = pytest.mark.unit


def test_scalars_and_enums() -> None:
    src = {
        "profile-name": "corp-mac",
        "mac_reauth_period": {"ra-period": 7200},
        "mba_maxf": {"max-authentication-failures": 4},
        "mba_case": {"mba_case_t": "lower"},
        "mba_fmt": {"mba_delimiter_t": "colon"},
    }
    out = preprocess_mac_auth(src, {})
    assert out["_name"] == "corp-mac"
    assert out["_reauth_period"] == 7200
    assert out["_max_retries"] == 4
    assert out["_case_type"] == "lower"
    assert out["_address_format"] == "colon"


def test_presence_flags() -> None:
    src = {
        "profile-name": "p",
        "mac_reauthentication": {},
        "mac_use_server_reauth_period": {"_present": True},
    }
    out = preprocess_mac_auth(src, {})
    assert out["_reauth_enable"] is True
    assert out["_use_server_reauth"] is True


def test_default_flagged_fields_skipped() -> None:
    src = {
        "profile-name": "default",
        "mac_reauth_period": {"_flags": {"default": True}, "ra-period": 86400},
        "mac_reauthentication": {"_flags": {"default": True}},
    }
    out = preprocess_mac_auth(src, {})
    assert "_reauth_period" not in out
    assert "_reauth_enable" not in out
    assert out["_name"] == "default"
