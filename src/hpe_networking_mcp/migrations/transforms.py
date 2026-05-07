"""Named transforms referenced by mapping ``key_mappings.transform`` fields.

Each transform takes a source value and returns a target value. Some transforms
return tuples — e.g. ``split_csv_to_string_array`` for VLAN-ID lists returns
both the expanded discrete IDs (for layer2-vlan iteration) and the array form
that preserves range syntax (for alias overrides). The engine picks which
output it needs based on the emit step's iteration rule.

Transforms must stay pure (no I/O) so they can be unit-tested in isolation.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

# --------------------------------------------------------------------------- #
# Public registry
# --------------------------------------------------------------------------- #


TransformFn = Callable[[Any], Any]


def get_transform(name: str) -> TransformFn:
    """Resolve a named transform; raises KeyError on unknown names."""
    try:
        return _REGISTRY[name]
    except KeyError as exc:
        known = ", ".join(sorted(_REGISTRY.keys()))
        raise KeyError(f"Unknown transform {name!r}. Known: {known}") from exc


# --------------------------------------------------------------------------- #
# Transforms
# --------------------------------------------------------------------------- #


def direct(value: Any) -> Any:
    """Pass the value through unchanged."""
    return value


def direct_str(value: Any) -> str:
    """Coerce to str and pass through."""
    return str(value)


def direct_int(value: Any) -> int:
    """Coerce to int. Raises ValueError on non-numeric input."""
    return int(value)


def flag_to_bool(value: Any) -> bool:
    """Source presence (truthy value, ``True``, ``"true"``, ``"yes"``) → True."""
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in ("true", "yes", "1", "enabled")
    return bool(value)


def split_csv_to_string_array(value: Any) -> list[str]:
    """Split a CSV string into an array of element strings.

    Each element is preserved verbatim — discrete IDs (``"107"``) AND ranges
    (``"108-110"``) survive intact. The engine's per-vlan-id iteration logic
    handles range expansion separately when needed (see expand_vlan_id_csv).

    Examples:
        ``"107"`` → ``["107"]``
        ``"104,160"`` → ``["104", "160"]``
        ``"108-110"`` → ``["108-110"]``
        ``"100,108-110,200"`` → ``["100", "108-110", "200"]``
    """
    if value is None or value == "":
        return []
    return [chunk.strip() for chunk in str(value).split(",") if chunk.strip()]


def expand_vlan_id_csv(value: Any) -> list[int]:
    """Expand a CSV-of-IDs-and-ranges into discrete integer VLAN IDs.

    Used by engine call-iteration when a step needs one call per VLAN ID
    (e.g. ``per_vlan_id_in_binding`` on ``layer2-vlan`` creation).

    Examples:
        ``"107"`` → ``[107]``
        ``"104,160"`` → ``[104, 160]``
        ``"108-110"`` → ``[108, 109, 110]``
        ``"100,108-110,200"`` → ``[100, 108, 109, 110, 200]``

    Raises:
        ValueError: On malformed elements (non-numeric, inverted ranges,
            VLANs outside 1..4094).
    """
    out: list[int] = []
    for chunk in split_csv_to_string_array(value):
        if "-" in chunk:
            low_s, high_s = chunk.split("-", 1)
            low, high = int(low_s), int(high_s)
            if low > high:
                raise ValueError(f"Inverted VLAN range {chunk!r} (low > high)")
            if not (1 <= low <= 4094) or not (1 <= high <= 4094):
                raise ValueError(f"VLAN range {chunk!r} contains IDs outside 1..4094")
            out.extend(range(low, high + 1))
        else:
            vid = int(chunk)
            if not (1 <= vid <= 4094):
                raise ValueError(f"VLAN ID {vid} outside 1..4094")
            out.append(vid)
    return out


_REGISTRY: dict[str, TransformFn] = {
    "direct": direct,
    "direct_str": direct_str,
    "direct_int": direct_int,
    "flag_to_bool": flag_to_bool,
    "split_csv_to_string_array": split_csv_to_string_array,
    "expand_vlan_id_csv": expand_vlan_id_csv,
}
