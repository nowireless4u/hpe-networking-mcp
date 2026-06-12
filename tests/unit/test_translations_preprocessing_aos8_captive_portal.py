"""Unit tests for ``translations/preprocessing/aos8_captive_portal.py``.

Covers the cp_auth_profile normalizer: one-level scalar unwrap, empty-object
presence flags, the inverted protocol-http -> use-https, the auth-protocol
enum map, black/white-list arrays, and ``_flags.default`` skipping.
Generic placeholder data only.
"""

from __future__ import annotations

import pytest

from hpe_networking_mcp.translations.preprocessing.aos8_captive_portal import (
    preprocess_captive_portal,
)

pytestmark = pytest.mark.unit


def test_scalars_and_name() -> None:
    src = {
        "profile-name": "guest-cp",
        "cp_default_role": {"default-role": "guest"},
        "cp_server_group": {"server-group": "guest-radius"},
        "cp_redirect_pause": {"redirect-pause": 3},
    }
    out = preprocess_captive_portal(src, {})
    assert out["_name"] == "guest-cp"
    assert out["_default_role"] == "guest"
    assert out["_server_group"] == "guest-radius"
    assert out["_redirect_pause"] == 3


def test_presence_flag_set_vs_default() -> None:
    src = {
        "profile-name": "cp",
        "apple_cna_bypass": {},  # operator-set
        "logout_popup": {"_flags": {"default": True}},  # default -> dropped
    }
    out = preprocess_captive_portal(src, {})
    assert out["_apple_cna"] is True
    assert "_logout_popup" not in out


def test_protocol_http_inverts_to_use_https_false() -> None:
    out = preprocess_captive_portal({"profile-name": "cp", "cp_proto_http": {}}, {})
    assert out["_use_https"] is False


def test_no_protocol_http_omits_use_https() -> None:
    """Absent protocol-http -> use-https omitted (Central default True applies)."""
    out = preprocess_captive_portal({"profile-name": "cp"}, {})
    assert "_use_https" not in out


def test_auth_protocol_enum_map() -> None:
    for aos_val, central_val in [("PAP", "PAP"), ("MSCHAPv2", "MSCHAPv2"), ("chap", "CHAP")]:
        out = preprocess_captive_portal(
            {"profile-name": "cp", "authentication_method": {"captive_auth_t": aos_val}}, {}
        )
        assert out["_auth_protocol"] == central_val


def test_black_white_list_arrays() -> None:
    src = {
        "profile-name": "cp",
        "cp_black_list": [{"black-list": "bad-sites"}, {"black-list": "more-bad"}],
        "cp_white_list": [{"white-list": "ok-sites"}],
    }
    out = preprocess_captive_portal(src, {})
    assert out["_deny_list"] == ["bad-sites", "more-bad"]
    assert out["_allow_list"] == ["ok-sites"]


def test_default_flagged_scalar_dropped() -> None:
    out = preprocess_captive_portal(
        {"profile-name": "cp", "cp_redirect_pause": {"redirect-pause": 10, "_flags": {"default": True}}}, {}
    )
    assert "_redirect_pause" not in out
