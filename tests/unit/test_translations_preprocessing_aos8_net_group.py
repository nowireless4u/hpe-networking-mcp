"""Unit tests for ``translations/preprocessing/aos8_net_group.py``.

Covers the preprocessing function directly:
* Address-family detection from `netdst__entry` vs `netdst6__entry`.
* Per-entry discriminator mapping (`netdst__host` / `netdst__network` /
  `netdst__name`) into Central items[] elements.
* IPv4 netmask → CIDR prefix conversion (including non-contiguous mask
  failure).
* Per-entry `_flags.default` / `_flags.system` filtering.

Engine-level integration of these results lives in
``test_translations_engine.py`` under the ``central:net_group`` section.
"""

from __future__ import annotations

import pytest

from hpe_networking_mcp.translations.preprocessing.aos8_net_group import (
    _netmask_to_prefix,
    preprocess_net_group,
)

pytestmark = pytest.mark.unit


# --------------------------------------------------------------------------- #
# Address-family detection
# --------------------------------------------------------------------------- #


def test_netdst_record_is_ipv4_only() -> None:
    source = {"dstname": "x", "netdst__entry": []}
    out = preprocess_net_group(source, {})
    assert out["_address_family"] == "IPV4_ONLY"
    assert out["_central_items"] == []


def test_netdst6_record_is_ipv6_only() -> None:
    source = {"dstname": "x", "netdst6__entry": []}
    out = preprocess_net_group(source, {})
    assert out["_address_family"] == "IPV6_ONLY"
    assert out["_central_items"] == []


def test_record_without_entry_key_raises() -> None:
    with pytest.raises(ValueError, match="neither 'netdst__entry' nor 'netdst6__entry'"):
        preprocess_net_group({"dstname": "x"}, {})


def test_input_dict_not_mutated() -> None:
    source = {"dstname": "x", "netdst__entry": [{"_objname": "netdst__host", "address": "10.0.0.1"}]}
    snapshot = dict(source)
    snapshot_entries = list(source["netdst__entry"])
    preprocess_net_group(source, {})
    assert source == snapshot
    assert source["netdst__entry"] == snapshot_entries


# --------------------------------------------------------------------------- #
# Per-entry discriminator → Central items[] element
# --------------------------------------------------------------------------- #


def test_netdst_host_entry_maps_to_host_type() -> None:
    source = {
        "dstname": "x",
        "netdst__entry": [
            {"_objname": "netdst__host", "address": "192.168.20.70", "hosttag": "address"},
        ],
    }
    out = preprocess_net_group(source, {})
    assert out["_central_items"] == [{"type": "HOST", "address": "192.168.20.70", "index": 1}]


def test_netdst_network_entry_maps_to_network_with_cidr_prefix() -> None:
    source = {
        "dstname": "x",
        "netdst__entry": [
            {"_objname": "netdst__network", "address": "10.0.0.0", "netmask": "255.0.0.0"},
            {"_objname": "netdst__network", "address": "192.168.1.0", "netmask": "255.255.255.0"},
        ],
    }
    out = preprocess_net_group(source, {})
    assert out["_central_items"] == [
        {"type": "NETWORK", "prefix": "10.0.0.0/8", "index": 1},
        {"type": "NETWORK", "prefix": "192.168.1.0/24", "index": 2},
    ]


def test_netdst_name_entry_maps_to_fqdn() -> None:
    source = {
        "dstname": "x",
        "netdst__entry": [{"_objname": "netdst__name", "host_name": "cppm.example.com"}],
    }
    out = preprocess_net_group(source, {})
    assert out["_central_items"] == [{"type": "FQDN", "fqdn": "cppm.example.com", "index": 1}]


def test_mixed_entry_types_preserve_source_order() -> None:
    """Host, network, FQDN entries on one alias all map and preserve order."""
    source = {
        "dstname": "cppm",
        "netdst__entry": [
            {"_objname": "netdst__host", "address": "192.168.20.70"},
            {"_objname": "netdst__network", "address": "10.10.0.0", "netmask": "255.255.0.0"},
            {"_objname": "netdst__name", "host_name": "cppm.example.com"},
        ],
    }
    out = preprocess_net_group(source, {})
    assert out["_central_items"] == [
        {"type": "HOST", "address": "192.168.20.70", "index": 1},
        {"type": "NETWORK", "prefix": "10.10.0.0/16", "index": 2},
        {"type": "FQDN", "fqdn": "cppm.example.com", "index": 3},
    ]


def test_unknown_objname_silently_skipped() -> None:
    """Per the JSON's unmapped_fields: unknown _objname discriminators are dropped."""
    source = {
        "dstname": "x",
        "netdst__entry": [
            {"_objname": "netdst__host", "address": "10.0.0.1"},
            {"_objname": "netdst__future_type", "weird_field": "..."},
        ],
    }
    out = preprocess_net_group(source, {})
    assert out["_central_items"] == [{"type": "HOST", "address": "10.0.0.1", "index": 1}]


def test_entry_missing_required_field_is_dropped() -> None:
    """Defensive: host entry without 'address' is skipped, not an error."""
    source = {
        "dstname": "x",
        "netdst__entry": [
            {"_objname": "netdst__host"},  # no address
            {"_objname": "netdst__network", "address": "10.0.0.0"},  # no netmask
            {"_objname": "netdst__name"},  # no host_name
            {"_objname": "netdst__host", "address": "10.0.0.1"},
        ],
    }
    out = preprocess_net_group(source, {})
    assert out["_central_items"] == [{"type": "HOST", "address": "10.0.0.1", "index": 1}]


def test_non_dict_entry_silently_skipped() -> None:
    source = {
        "dstname": "x",
        "netdst__entry": [
            "not-a-dict",
            None,
            {"_objname": "netdst__host", "address": "10.0.0.1"},
        ],
    }
    out = preprocess_net_group(source, {})
    assert out["_central_items"] == [{"type": "HOST", "address": "10.0.0.1", "index": 1}]


# --------------------------------------------------------------------------- #
# Per-entry _flags filtering
# --------------------------------------------------------------------------- #


def test_entry_with_default_flag_filtered() -> None:
    """Per-entry _flags.default=true skips the entry."""
    source = {
        "dstname": "x",
        "netdst__entry": [
            {"_objname": "netdst__host", "address": "10.0.0.1", "_flags": {"default": True}},
            {"_objname": "netdst__host", "address": "10.0.0.2"},
        ],
    }
    out = preprocess_net_group(source, {})
    assert out["_central_items"] == [{"type": "HOST", "address": "10.0.0.2", "index": 1}]


def test_entry_with_system_flag_filtered() -> None:
    source = {
        "dstname": "x",
        "netdst__entry": [
            {"_objname": "netdst__host", "address": "10.0.0.1", "_flags": {"system": True}},
            {"_objname": "netdst__host", "address": "10.0.0.2"},
        ],
    }
    out = preprocess_net_group(source, {})
    assert out["_central_items"] == [{"type": "HOST", "address": "10.0.0.2", "index": 1}]


def test_entry_with_inherited_flag_passes_through() -> None:
    """_flags.inherited is consumer-filtered at the record level, not entry level —
    inherited per-entry markers should NOT cause preprocessing to drop entries
    (the consumer already decided to translate this record).
    """
    source = {
        "dstname": "x",
        "netdst__entry": [
            {"_objname": "netdst__host", "address": "10.0.0.1", "_flags": {"inherited": True}},
        ],
    }
    out = preprocess_net_group(source, {})
    assert out["_central_items"] == [{"type": "HOST", "address": "10.0.0.1", "index": 1}]


# --------------------------------------------------------------------------- #
# IPv6 path (assumed shape; structural symmetry with v4)
# --------------------------------------------------------------------------- #


def test_netdst6_host_entry_maps_to_host() -> None:
    source = {
        "dstname": "x6",
        "netdst6__entry": [{"_objname": "netdst6__host", "address": "2001:db8::1"}],
    }
    out = preprocess_net_group(source, {})
    assert out["_central_items"] == [{"type": "HOST", "address": "2001:db8::1", "index": 1}]


def test_netdst6_network_with_cidr_already_in_address() -> None:
    """v6 networks carry the prefix length in the address string; pass through."""
    source = {
        "dstname": "x6",
        "netdst6__entry": [{"_objname": "netdst6__network", "address": "2001:db8::/32"}],
    }
    out = preprocess_net_group(source, {})
    assert out["_central_items"] == [{"type": "NETWORK", "prefix": "2001:db8::/32", "index": 1}]


def test_netdst6_network_prefix_from_prefix_length_field() -> None:
    """v6 NETWORK entry with a separate prefix-length field builds the CIDR from
    that length — real supernets are preserved, NOT collapsed to /128 (issue #419).
    """
    source = {
        "dstname": "ula",
        "netdst6__entry": [{"_objname": "netdst6__network", "address": "fc00::", "prefix_len": 7}],
    }
    out = preprocess_net_group(source, {})
    assert out["_central_items"] == [{"type": "NETWORK", "prefix": "fc00::/7", "index": 1}]


def test_netdst6_network_without_prefix_length_passes_address_through() -> None:
    """v6 NETWORK entry with no '/' and no prefix-length field passes the address
    through UNCHANGED rather than inventing a /128 host route (issue #419).
    """
    source = {
        "dstname": "x6",
        "netdst6__entry": [{"_objname": "netdst6__network", "address": "2001:db8::1"}],
    }
    out = preprocess_net_group(source, {})
    assert out["_central_items"] == [{"type": "NETWORK", "prefix": "2001:db8::1", "index": 1}]


# --------------------------------------------------------------------------- #
# invert clause
# --------------------------------------------------------------------------- #


def test_invert_truthy_surfaces_invert_flag() -> None:
    source = {
        "dstname": "x",
        "invert": True,
        "netdst__entry": [{"_objname": "netdst__host", "address": "10.0.0.1"}],
    }
    out = preprocess_net_group(source, {})
    assert out["_invert"] is True


def test_invert_falsy_omits_invert_flag() -> None:
    """Absent / false invert → no _invert key (Central absent == false shape)."""
    source = {
        "dstname": "x",
        "netdst__entry": [{"_objname": "netdst__host", "address": "10.0.0.1"}],
    }
    out = preprocess_net_group(source, {})
    assert "_invert" not in out


# --------------------------------------------------------------------------- #
# Netmask → CIDR prefix helper
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize(
    "netmask,expected_prefix",
    [
        ("255.255.255.255", 32),
        ("255.255.255.128", 25),
        ("255.255.255.0", 24),
        ("255.255.0.0", 16),
        ("255.0.0.0", 8),
        ("0.0.0.0", 0),
    ],
)
def test_netmask_to_prefix_contiguous(netmask: str, expected_prefix: int) -> None:
    assert _netmask_to_prefix(netmask) == expected_prefix


@pytest.mark.parametrize(
    "netmask",
    [
        "255.0.255.0",  # non-contiguous (gap in middle)
        "255.255.0.255",
        "not-a-mask",
        "256.0.0.0",
    ],
)
def test_netmask_to_prefix_invalid_raises(netmask: str) -> None:
    with pytest.raises(ValueError, match="non-contiguous|net_group"):
        _netmask_to_prefix(netmask)


def test_network_entry_with_non_contiguous_mask_raises_in_preprocessing() -> None:
    """Non-contiguous netmask surfaces from preprocessing, not silently corrupted."""
    source = {
        "dstname": "x",
        "netdst__entry": [
            {"_objname": "netdst__network", "address": "10.0.0.0", "netmask": "255.0.255.0"},
        ],
    }
    with pytest.raises(ValueError, match="non-contiguous"):
        preprocess_net_group(source, {})
