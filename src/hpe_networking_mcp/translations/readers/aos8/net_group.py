"""AOS 8 → canonical net-group reader (absorbs the old net_group preprocessing).

Maps an AOS 8 ``netdst`` (IPv4) / ``netdst6`` (IPv6) record to a
``CanonicalNetGroup``: address family from which ``__entry`` key is present, and
one Central ``items[]`` element per entry via the ``_objname`` discriminator
(``host`` → HOST, ``network`` → NETWORK with computed CIDR prefix, ``name`` →
FQDN). Record-level inherited/system filtering stays the migration skill's job;
this reader only filters per-entry ``_flags``.
"""

from __future__ import annotations

import ipaddress
from typing import Any

from hpe_networking_mcp.translations.canonical.net_group import CanonicalNetGroup


def _netmask_to_prefix(netmask: str) -> int:
    """Dotted-quad IPv4 netmask → CIDR prefix length; raises on non-contiguous masks."""
    try:
        return ipaddress.IPv4Network(f"0.0.0.0/{netmask}", strict=False).prefixlen
    except ValueError as exc:
        raise ValueError(
            f"net_group: non-contiguous IPv4 netmask {netmask!r} cannot be expressed as a CIDR prefix"
        ) from exc


def _ipv6_prefix_length(entry: dict[str, Any]) -> int | None:
    """Best-effort IPv6 prefix length from a netdst6 network entry, or None."""
    for field in ("prefix_len", "prefixlen", "prefix-length", "prefix", "netmask"):
        value = entry.get(field)
        if value is None or value == "":
            continue
        try:
            length = int(str(value))
        except (TypeError, ValueError):
            continue
        if 0 <= length <= 128:
            return length
    return None


def _build_item(entry: dict[str, Any], family: str) -> dict[str, Any] | None:
    """Map one AOS 8 ``__entry`` element to one Central ``items[]`` element."""
    objname = entry.get("_objname")
    if objname in ("netdst__host", "netdst6__host"):
        address = entry.get("address")
        return {"type": "HOST", "address": str(address)} if address else None

    if objname in ("netdst__network", "netdst6__network"):
        address = entry.get("address")
        if not address:
            return None
        if family == "IPV6_ONLY":
            if "/" in str(address):
                return {"type": "NETWORK", "prefix": str(address)}
            v6_prefix = _ipv6_prefix_length(entry)
            if v6_prefix is None:
                return {"type": "NETWORK", "prefix": str(address)}
            return {"type": "NETWORK", "prefix": f"{address}/{v6_prefix}"}
        netmask = entry.get("netmask")
        if not netmask:
            return None
        return {"type": "NETWORK", "prefix": f"{address}/{_netmask_to_prefix(str(netmask))}"}

    if objname in ("netdst__name", "netdst6__name"):
        host_name = entry.get("host_name")
        return {"type": "FQDN", "fqdn": str(host_name)} if host_name else None

    return None


def aos8_read_net_group(net_group: dict[str, Any]) -> CanonicalNetGroup:
    """Build a ``CanonicalNetGroup`` from one AOS 8 ``netdst`` / ``netdst6`` record.

    Raises:
        ValueError: when the record carries neither ``netdst__entry`` nor
            ``netdst6__entry`` (cannot determine address family).
    """
    if "netdst__entry" in net_group:
        family = "IPV4_ONLY"
        entries = net_group.get("netdst__entry") or []
    elif "netdst6__entry" in net_group:
        family = "IPV6_ONLY"
        entries = net_group.get("netdst6__entry") or []
    else:
        raise ValueError("net_group: record carries neither 'netdst__entry' nor 'netdst6__entry'")

    items: list[dict[str, Any]] = []
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        flags = entry.get("_flags") or {}
        if flags.get("default") is True or flags.get("system") is True:
            continue
        built = _build_item(entry, family)
        if built is not None:
            built["index"] = len(items) + 1
            items.append(built)

    return CanonicalNetGroup(
        name=str(net_group.get("dstname") or ""),
        address_family=family,
        items=items,
        invert=bool(net_group.get("invert")),
    )
