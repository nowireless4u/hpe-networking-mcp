"""Preprocessing for ``central:net_group`` (AOS 8 netdst / netdst6 → Central net-group).

The translation JSON declares this module's ``preprocess_net_group`` function
in its top-level ``preprocessing`` field. The engine invokes the function
before ``key_mappings`` run, and the function returns an augmented
``source_data`` dict with two new fields:

* ``_address_family`` — ``"IPV4_ONLY"`` or ``"IPV6_ONLY"`` based on which
  ``__entry`` key the source record carries (``netdst__entry`` →
  ``IPV4_ONLY``; ``netdst6__entry`` → ``IPV6_ONLY``).
* ``_central_items`` — the Central ``items[]`` array, with each AOS 8
  ``netdst__entry`` mapped to a Central item via the ``_objname``
  discriminator (``netdst__host`` → ``HOST``; ``netdst__network`` →
  ``NETWORK`` with computed CIDR prefix; ``netdst__name`` → ``FQDN``).

Per the translations authoring guide (``AUTHORING.md``), preprocessing lives
in this module because the per-entry build needs a discriminator switch +
the netmask → CIDR-prefix helper, which doesn't fit a per-field
1-arg transform.
"""

from __future__ import annotations

import ipaddress
from typing import Any


def preprocess_net_group(source_data: dict[str, Any], runtime_values: dict[str, Any]) -> dict[str, Any]:
    """Augment a single netdst / netdst6 record with ``_address_family`` + ``_central_items``.

    Args:
        source_data: One AOS 8 ``netdst`` or ``netdst6`` record. Must carry
            either ``netdst__entry`` or ``netdst6__entry`` as a list of
            per-entry dicts. ``dstname`` is read by the JSON's regular
            ``key_mappings``; this function only augments the items
            and address-family fields.
        runtime_values: Engine-supplied; unused for net-group preprocessing
            (no cross-record lookups, no caller-supplied context needed).

    Returns:
        A NEW dict ``{**source_data, "_address_family": ..., "_central_items": [...]}``.
        Input is not mutated.

    Raises:
        ValueError: If the record carries neither ``netdst__entry`` nor
            ``netdst6__entry``, or if a NETWORK entry's netmask is
            non-contiguous (rare AOS 8 syntax; explicit failure preferred
            over silent corruption of the CIDR prefix).
    """
    del runtime_values  # unused

    if "netdst__entry" in source_data:
        family = "IPV4_ONLY"
        entries = source_data.get("netdst__entry") or []
    elif "netdst6__entry" in source_data:
        family = "IPV6_ONLY"
        entries = source_data.get("netdst6__entry") or []
    else:
        raise ValueError(
            "net_group preprocessing: source record carries neither 'netdst__entry' nor "
            "'netdst6__entry' — cannot determine address family"
        )

    items: list[dict[str, Any]] = []
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        # Skip per-entry inherited/system markers — consumer should filter at
        # the record level, but defend against partial-inheritance shapes.
        flags = entry.get("_flags") or {}
        if flags.get("default") is True or flags.get("system") is True:
            continue
        built = _build_item(entry, family)
        if built is not None:
            # Central items[] carry a 1-based `index` (the schema x-key); every
            # live built-in item has it. Number in source order after filtering.
            built["index"] = len(items) + 1
            items.append(built)

    augmented: dict[str, Any] = {
        **source_data,
        "_address_family": family,
        "_central_items": items,
    }
    # AOS 8 netdestinations carry an `invert` clause. Central's built-in shape
    # omits the key when false (absent == false), so only surface it when truthy.
    if source_data.get("invert"):
        augmented["_invert"] = True
    return augmented


def _build_item(entry: dict[str, Any], family: str) -> dict[str, Any] | None:
    """Map one AOS 8 ``__entry`` element to one Central ``items[]`` element.

    Returns ``None`` for unknown discriminators (silently dropped per
    the JSON's ``unmapped_fields`` policy — surface as a non_empty_regression
    finding at the consumer level if needed).
    """
    objname = entry.get("_objname")
    if objname in ("netdst__host", "netdst6__host"):
        address = entry.get("address")
        if not address:
            return None
        return {"type": "HOST", "address": str(address)}

    if objname in ("netdst__network", "netdst6__network"):
        address = entry.get("address")
        if not address:
            return None
        if family == "IPV6_ONLY":
            # IPv6 networks carry the prefix length separately (mirror of the IPv4
            # dotted-quad path). If the address already embeds '/', pass through.
            # Otherwise build the prefix from the entry's prefix-length field. A
            # hardcoded /128 fallback would collapse real supernets (e.g. fc00::/7
            # → /128), so when no prefix-length is present, pass the address through
            # UNCHANGED rather than inventing a host route.
            if "/" in str(address):
                return {"type": "NETWORK", "prefix": str(address)}
            v6_prefix = _ipv6_prefix_length(entry)
            if v6_prefix is None:
                return {"type": "NETWORK", "prefix": str(address)}
            return {"type": "NETWORK", "prefix": f"{address}/{v6_prefix}"}
        # IPv4: netmask is dotted-quad; convert to CIDR prefix length.
        netmask = entry.get("netmask")
        if not netmask:
            return None
        cidr_len = _netmask_to_prefix(str(netmask))
        return {"type": "NETWORK", "prefix": f"{address}/{cidr_len}"}

    if objname in ("netdst__name", "netdst6__name"):
        host_name = entry.get("host_name")
        if not host_name:
            return None
        return {"type": "FQDN", "fqdn": str(host_name)}

    return None


def _ipv6_prefix_length(entry: dict[str, Any]) -> int | None:
    """Extract an IPv6 prefix length from a netdst6 network entry, or None.

    The netdst6 entry shape isn't live-verified (zero records in the maintainer's
    tenant), so probe the candidate AOS 8 field names. ``netmask`` carries the
    prefix length for IPv6 entries in some schema variants (an integer rather
    than a dotted-quad). Returns None when no prefix-length field is present so
    the caller can pass the address through unchanged.
    """
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


def _netmask_to_prefix(netmask: str) -> int:
    """Convert a dotted-quad IPv4 netmask to a CIDR prefix length.

    Raises ValueError on non-contiguous masks (e.g. ``'255.0.255.0'``) —
    AOS 8 syntactically allows them but Central CIDR notation cannot
    represent them. Explicit failure preferred over silent corruption.
    """
    try:
        return ipaddress.IPv4Network(f"0.0.0.0/{netmask}", strict=False).prefixlen
    except ValueError as exc:
        raise ValueError(
            f"net_group preprocessing: non-contiguous IPv4 netmask {netmask!r} cannot be "
            f"expressed as a CIDR prefix; Central NETWORK entries require a prefix length"
        ) from exc
