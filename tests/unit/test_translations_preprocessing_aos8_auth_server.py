"""Unit tests for ``translations/preprocessing/aos8_auth_server.py``.

Covers the rad_server / tacacs_server normalizer directly:
* RADIUS vs TACACS detection + field flattening (one-level value unwrap).
* ``_flags.default`` sub-values dropped (operator-undefined → Central default).
* None-valued keys omitted so optional typed transforms never run on None.
* CoA (RFC 3576) co-location correlation via ``runtime_values['coa_servers']``.

Generic placeholder data only (RAD-1 / TAC-1 / 10.0.0.x / <secret>).
"""

from __future__ import annotations

import pytest

from hpe_networking_mcp.translations.preprocessing.aos8_auth_server import (
    preprocess_auth_server,
)

pytestmark = pytest.mark.unit


def _radius(host: str = "10.0.0.10") -> dict:
    return {
        "rad_server_name": "RAD-1",
        "rad_host": {"host": host},
        "rad_key": {"key": "<secret>"},
        "rad_authport": {"authport": 1812},
        "rad_acctport": {"acctport": 1813},
        # operator-default sub-object — must be dropped:
        "rad_timeout": {"timeout": 5, "_flags": {"default": True}},
    }


def test_radius_normalizes_core_fields() -> None:
    out = preprocess_auth_server(_radius(), {})
    assert out["_type"] == "RADIUS"
    assert out["_name"] == "RAD-1"
    assert out["_host"] == "10.0.0.10"
    assert out["_secret"] == "<secret>"
    assert out["_auth_port"] == 1812
    assert out["_acct_port"] == 1813


def test_default_flagged_subvalue_is_dropped() -> None:
    """A sub-object flagged _flags.default is treated as operator-unset → omitted."""
    out = preprocess_auth_server(_radius(), {})
    assert "_timeout" not in out  # rad_timeout was _flags.default


def test_radius_without_coa_has_no_dynamic_auth() -> None:
    out = preprocess_auth_server(_radius(), {})
    assert "_radius_server_mode" not in out  # omitted → Central defaults to AUTH
    assert "_dynamic_auth" not in out


def test_tacacs_normalizes_and_maps_tcp_port_to_auth_port() -> None:
    src = {
        "tacacs_server_name": "TAC-1",
        "tacacs_host": {"host": "10.0.0.20"},
        "tacacs_key": {"key": "<secret>"},
        "tacacs_tcpport": {"tcp-port": 49},
    }
    out = preprocess_auth_server(src, {})
    assert out["_type"] == "TACACS"
    assert out["_name"] == "TAC-1"
    assert out["_host"] == "10.0.0.20"
    assert out["_auth_port"] == 49  # TACACS tcp-port folded into the shared slot
    assert "_acct_port" not in out  # RADIUS-only, omitted for TACACS


def test_coa_peer_correlation_sets_auth_and_coa() -> None:
    """A co-located RFC 3576 server (matching IP) flips RADIUS → AUTH_AND_COA."""
    coa = [{"rfc3576_server": "10.0.0.10", "rfc3576_secret": {"key": "<coa-secret>"}}]
    out = preprocess_auth_server(_radius("10.0.0.10"), {"coa_servers": coa})
    assert out["_radius_server_mode"] == "AUTH_AND_COA"
    assert out["_dynamic_auth"] is True


def test_coa_peer_non_matching_ip_does_not_correlate() -> None:
    coa = [{"rfc3576_server": "10.9.9.9"}]
    out = preprocess_auth_server(_radius("10.0.0.10"), {"coa_servers": coa})
    assert "_radius_server_mode" not in out


def test_coa_correlation_also_matches_server_ip_key() -> None:
    """CoA entries may use 'server_ip' (rfc3576_client_prof) instead of 'rfc3576_server'."""
    coa = [{"server_ip": "10.0.0.10"}]
    out = preprocess_auth_server(_radius("10.0.0.10"), {"coa_servers": coa})
    assert out["_radius_server_mode"] == "AUTH_AND_COA"


def test_tacacs_never_gets_coa() -> None:
    src = {"tacacs_server_name": "TAC-1", "tacacs_host": {"host": "10.0.0.10"}, "tacacs_key": {"key": "x"}}
    out = preprocess_auth_server(src, {"coa_servers": [{"rfc3576_server": "10.0.0.10"}]})
    assert "_radius_server_mode" not in out
