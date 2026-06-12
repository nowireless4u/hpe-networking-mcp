"""Unit tests for ``translations/preprocessing/aos8_gateway_cluster.py``.

Covers the cluster_prof normalizer: strategy validation + flags, member mapping
(ip / coa-vrrp-ip / priority), inherited-member preservation, and multicast /
heartbeat handling. Generic placeholder data only.
"""

from __future__ import annotations

import pytest

from hpe_networking_mcp.translations.preprocessing.aos8_gateway_cluster import (
    preprocess_gateway_cluster,
)

pytestmark = pytest.mark.unit


def _cluster() -> dict:
    return {
        "profile-name": "East",
        "cluster_controller": [
            {"ip": "10.0.0.1", "vrrp_ip": "10.0.0.10", "prio": 128, "mcast_vlan": 0},
            {"ip": "10.0.0.2", "vrrp_ip": "10.0.0.11", "prio": 128, "mcast_vlan": 0},
        ],
        "heartbeat_threshold": {"_flags": {"default": True}, "heartbeat-threshold": 0},
    }


def test_members_mapped() -> None:
    out = preprocess_gateway_cluster(_cluster(), {"cluster_strategy": "ha_only"})
    assert out["_name"] == "East"
    assert out["_ipv4_gateways"] == [
        {"ip": "10.0.0.1", "coa-vrrp-ip": "10.0.0.10", "priority": 128},
        {"ip": "10.0.0.2", "coa-vrrp-ip": "10.0.0.11", "priority": 128},
    ]


def test_strategy_flags() -> None:
    ha = preprocess_gateway_cluster(_cluster(), {"cluster_strategy": "ha_only"})
    assert "_emit_intent" not in ha and "_cluster_mode" not in ha

    site = preprocess_gateway_cluster(_cluster(), {"cluster_strategy": "intent_site"})
    assert site["_emit_intent"] is True and site["_cluster_mode"] == "CM_SITE"

    man = preprocess_gateway_cluster(_cluster(), {"cluster_strategy": "intent_manual"})
    assert man["_emit_intent"] is True and man["_cluster_mode"] == "CM_MANUAL"


def test_invalid_strategy_raises() -> None:
    with pytest.raises(ValueError, match="cluster_strategy"):
        preprocess_gateway_cluster(_cluster(), {})
    with pytest.raises(ValueError, match="cluster_strategy"):
        preprocess_gateway_cluster(_cluster(), {"cluster_strategy": "bogus"})


def test_inherited_members_not_dropped() -> None:
    """Member _flags.inherited must NOT cause the controller to be skipped."""
    src = _cluster()
    for c in src["cluster_controller"]:
        c["_flags"] = {"inherited": True}
    out = preprocess_gateway_cluster(src, {"cluster_strategy": "ha_only"})
    assert len(out["_ipv4_gateways"]) == 2


def test_system_members_skipped() -> None:
    src = _cluster()
    src["cluster_controller"][0]["_flags"] = {"system": True}
    out = preprocess_gateway_cluster(src, {"cluster_strategy": "ha_only"})
    assert len(out["_ipv4_gateways"]) == 1
    assert out["_ipv4_gateways"][0]["ip"] == "10.0.0.2"


def test_multicast_vlan_first_nonzero() -> None:
    src = _cluster()
    src["cluster_controller"][1]["mcast_vlan"] = 150
    out = preprocess_gateway_cluster(src, {"cluster_strategy": "ha_only"})
    assert out["_multicast_vlan"] == 150


def test_default_heartbeat_omitted() -> None:
    out = preprocess_gateway_cluster(_cluster(), {"cluster_strategy": "ha_only"})
    assert "_heartbeat_threshold" not in out
