"""Unit tests for ``translations/preprocessing/aos8_dot1x_auth.py``.

Covers the dot1x_auth_profile normalizer: scalar unwrapping, presence-flag
flattening, ``_flags.default`` skipping, and the all-default record producing a
name-only shape. Generic placeholder data only.
"""

from __future__ import annotations

import pytest

from hpe_networking_mcp.translations.preprocessing.aos8_dot1x_auth import (
    preprocess_dot1x_auth,
)

pytestmark = pytest.mark.unit


def test_name_and_scalars_unwrapped() -> None:
    src = {
        "profile-name": "corp-dot1x",
        "reauth_period": {"ra-period": 3600},
        "max_requests": {"mx-requests": 2},
        "server_cert": {"server-cert-name": "corp-cert"},
        "framed_mtu": {"fmtu": 1400},
    }
    out = preprocess_dot1x_auth(src, {})
    assert out["_name"] == "corp-dot1x"
    assert out["_reauth_period"] == 3600
    assert out["_eapol_max_requests"] == 2
    assert out["_server_cert"] == "corp-cert"
    assert out["_framed_mtu"] == 1400


def test_presence_flags() -> None:
    src = {
        "profile-name": "p",
        "reauthentication": {},
        "validate_pmkid": {"_present": True},
        "dot1x_cert_cn_lookup": {},
    }
    out = preprocess_dot1x_auth(src, {})
    assert out["_reauth_enable"] is True
    assert out["_validate_pmkid"] is True
    assert out["_cert_cn_lookup"] is True


def test_default_flagged_fields_skipped() -> None:
    """Every-field-default record (the maintainer's live shape) -> name only."""
    src = {
        "profile-name": "MJG-Dot1x-80",
        "_flags": {"inherited": True},
        "reauth_period": {"_flags": {"default": True, "inherited": True}, "ra-period": 86400},
        "server_cert": {
            "_flags": {"default": True, "inherited": True},
            "server-cert-name": "default",
        },
        "validate_pmkid": {"_present": True, "_flags": {"default": True, "inherited": True}},
    }
    out = preprocess_dot1x_auth(src, {})
    # Only the name survives; every default-flagged field is dropped.
    underscore_keys = {k for k in out if k.startswith("_") and not k.startswith("_flags")}
    assert underscore_keys == {"_name"}
    assert out["_name"] == "MJG-Dot1x-80"


def test_source_data_preserved() -> None:
    """Original keys pass through; only ``_<field>`` keys are added."""
    src = {"profile-name": "p", "reauth_period": {"ra-period": 3600}}
    out = preprocess_dot1x_auth(src, {})
    assert out["profile-name"] == "p"
    assert out["reauth_period"] == {"ra-period": 3600}
