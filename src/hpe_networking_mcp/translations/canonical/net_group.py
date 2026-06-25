"""Canonical net-group model (AOS 8 ``netdst`` / ``netdst6`` → Central net-group).

``items`` are pre-built in the Central ``items[]`` shape by the reader (the
discriminator switch + netmask→CIDR conversion the old engine kept in
``preprocessing/aos8_net_group.py``); the writer substitutes them verbatim.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class CanonicalNetGroup(BaseModel):
    """A network-destination alias bound to a single address family."""

    model_config = ConfigDict(extra="forbid")
    name: str
    address_family: str  # IPV4_ONLY | IPV6_ONLY
    items: list[dict[str, Any]] = Field(default_factory=list)  # Central items[] (type/address/prefix/fqdn/index)
    invert: bool = False
