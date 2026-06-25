"""AOS 8 → canonical VLAN readers — ``vlan_id`` and ``named_vlan``.

``vlan_id`` is a bare numeric VLAN registration (with optional GW-only
sub-properties). ``named_vlan`` is the composite ``vlan_name`` ⨝ ``vlan_name_id``
form the migration skill pre-merges by name before passing one record per name.
"""

from __future__ import annotations

from typing import Any

from hpe_networking_mcp.translations.canonical.vlan import CanonicalNamedVlan, CanonicalVlanId
from hpe_networking_mcp.translations.readers.aos8._common import leaf


def _split_csv(value: Any) -> list[str]:
    """AOS 8 ``vlan-ids`` CSV → list of range-preserving id strings.

    Each element survives verbatim — discrete ids (``"107"``) AND ranges
    (``"108-110"``) — matching the validated ``split_csv_to_string_array``.
    """
    if value is None or value == "":
        return []
    return [chunk.strip() for chunk in str(value).split(",") if chunk.strip()]


def aos8_read_vlan_id(vlan_id: dict[str, Any]) -> CanonicalVlanId:
    """Build a ``CanonicalVlanId`` from one AOS 8 ``vlan_id`` record.

    Bare records carry only an integer ``id``. Richer records add the inline
    GW-only sub-properties ``option-82`` (top-level bool), ``vlan_id__descr.descr``
    and ``vlan_id__aaa.profile-name``.
    """
    raw_id = vlan_id.get("id")
    description = leaf(vlan_id.get("vlan_id__descr"), "descr")
    wired_aaa = leaf(vlan_id.get("vlan_id__aaa"), "profile-name")
    opt82_raw = vlan_id.get("option-82")
    option_82 = bool(opt82_raw) if opt82_raw is not None else None
    return CanonicalVlanId(
        vlan_id=str(raw_id),
        description=str(description) if description is not None else None,
        option_82=option_82,
        wired_aaa_profile=str(wired_aaa) if wired_aaa is not None else None,
    )


def aos8_read_named_vlan(named_vlan: dict[str, Any], *, alias_name: str | None = None) -> CanonicalNamedVlan:
    """Build a ``CanonicalNamedVlan`` from a pre-merged ``vlan_name`` ⨝ ``vlan_name_id`` record.

    Args:
        named_vlan: the merged record — ``{"name": ..., "vlan-ids": "<csv>"}``.
        alias_name: operator override for the alias name; defaults to the
            lower-case of the VLAN name (the validated convention).
    """
    name = str(named_vlan.get("name") or "")
    return CanonicalNamedVlan(
        vlan_name=name,
        alias_name=alias_name or name.lower(),
        vlan_ids=_split_csv(named_vlan.get("vlan-ids")),
    )
