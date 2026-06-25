"""AOS 8 → canonical readers (one module per config kind).

Each ``aos8_read_<kind>`` builds the canonical model for one config object from
its AOS 8 source record(s), absorbing the per-kind preprocessing logic (netmask →
CIDR, policy reverse-index, aaa-profile normalization) the old JSON engine kept
in ``translations/preprocessing/``.
"""

from __future__ import annotations

from hpe_networking_mcp.translations.readers.aos8.auth import (
    aos8_read_aaa_profile,
    aos8_read_auth_server,
    aos8_read_captive_portal,
    aos8_read_dot1x_auth,
    aos8_read_mac_auth,
    aos8_read_server_group,
)
from hpe_networking_mcp.translations.readers.aos8.gateway_cluster import aos8_read_gateway_cluster
from hpe_networking_mcp.translations.readers.aos8.net_group import aos8_read_net_group
from hpe_networking_mcp.translations.readers.aos8.policy import aos8_read_policy
from hpe_networking_mcp.translations.readers.aos8.role import aos8_read_role
from hpe_networking_mcp.translations.readers.aos8.vlan import aos8_read_named_vlan, aos8_read_vlan_id
from hpe_networking_mcp.translations.readers.aos8.wlan import aos8_read_wlan

__all__ = [
    "aos8_read_aaa_profile",
    "aos8_read_auth_server",
    "aos8_read_captive_portal",
    "aos8_read_dot1x_auth",
    "aos8_read_gateway_cluster",
    "aos8_read_mac_auth",
    "aos8_read_named_vlan",
    "aos8_read_net_group",
    "aos8_read_policy",
    "aos8_read_role",
    "aos8_read_server_group",
    "aos8_read_vlan_id",
    "aos8_read_wlan",
]
