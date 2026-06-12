"""Unit tests for ``translations/preprocessing/aos8_aaa_profile.py``.

Covers the aaa_prof normalizer: top-level scalar/flag flattening, the nested
authentication{} / authorization{} sub-dict assembly, the CoA server list, and
``_flags.default`` skipping. Generic placeholder data only.
"""

from __future__ import annotations

import pytest

from hpe_networking_mcp.translations.preprocessing.aos8_aaa_profile import (
    preprocess_aaa_profile,
)

pytestmark = pytest.mark.unit


def _aaa() -> dict:
    return {
        "profile-name": "corp-aaa",
        "rad_acct_sg": {"server_group_name": "corp-radius"},
        "max_ipv4_for_wireless": {"max_ipv4_users": 3},
        "enforce_dhcp": {},  # presence flag
        "default_user_role": {"role": "deny-all"},
        "dot1x_auth_profile": {"profile-name": "corp-dot1x"},
        "dot1x_default_role": {"default-role": "corp-employee"},
        "dot1x_server_group": {"srv-group": "corp-radius"},
        "mba_server_group": {"srv-group": "corp-mac"},
        "rfc3576_client": [{"rfc3576_server": "10.0.0.70"}],
    }


def test_top_level_fields_and_flags() -> None:
    out = preprocess_aaa_profile(_aaa(), {})
    assert out["_name"] == "corp-aaa"
    assert out["_acct_sg"] == "corp-radius"
    assert out["_max_ipv4"] == 3
    assert out["_enforce_dhcp"] is True


def test_authentication_block_assembled() -> None:
    out = preprocess_aaa_profile(_aaa(), {})
    assert out["_authentication"] == {
        "dot1x-auth": "corp-dot1x",
        "dot1x-default-role": "corp-employee",
        "dot1xauth-server-group": "corp-radius",
        "macauth-server-group": "corp-mac",
    }


def test_authorization_block_from_default_role() -> None:
    out = preprocess_aaa_profile(_aaa(), {})
    assert out["_authorization"] == {"pre-auth-role": "deny-all"}


def test_coa_server_list() -> None:
    out = preprocess_aaa_profile(_aaa(), {})
    assert out["_coa_list"] == ["10.0.0.70"]


def test_empty_blocks_omitted() -> None:
    """A bare profile (no dot1x/mac/role) omits the nested blocks entirely."""
    out = preprocess_aaa_profile({"profile-name": "bare"}, {})
    assert "_authentication" not in out
    assert "_authorization" not in out
    assert "_coa_list" not in out


def test_default_flagged_fields_skipped() -> None:
    src = {
        "profile-name": "p",
        "rad_acct_sg": {"server_group_name": "x", "_flags": {"default": True}},
        "enforce_dhcp": {"_flags": {"default": True}},
    }
    out = preprocess_aaa_profile(src, {})
    assert "_acct_sg" not in out
    assert "_enforce_dhcp" not in out
