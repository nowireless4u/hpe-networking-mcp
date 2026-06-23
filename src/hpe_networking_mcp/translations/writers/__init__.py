"""Canonical → platform writers."""

from hpe_networking_mcp.translations.writers.central import central_write_wlan, server_group_name
from hpe_networking_mcp.translations.writers.central_radius import (
    central_write_server_group,
    member_name,
)

__all__ = [
    "central_write_server_group",
    "central_write_wlan",
    "member_name",
    "server_group_name",
]
