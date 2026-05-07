"""Named transforms referenced by mapping ``key_mappings.transform`` fields.

Each transform takes a source value and returns a target value. Some transforms
return tuples — e.g. ``split_csv_to_string_array`` for VLAN-ID lists returns
both the expanded discrete IDs (for layer2-vlan iteration) and the array form
that preserves range syntax (for alias overrides). The engine picks which
output it needs based on the emit step's iteration rule.

Transforms must stay pure (no I/O) so they can be unit-tested in isolation.
"""

from __future__ import annotations

import re
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


_VLAN_NUMERIC_RE = re.compile(r"^\d+$")


def aos8_role_acl_to_central_policies(value: Any) -> list[dict[str, str]] | None:
    """Convert AOS 8 ``role__acl`` array to Central role ``policies`` array.

    Source shape (per live AOS 8 capture)::

        [
          {"acl_type": "session", "pname": "global-sacl",
           "_flags": {"default": true, "readonly": true, "system": true}},
          {"acl_type": "session", "pname": "camera_role_ubt"}  # user-customized
        ]

    Target shape (Central role schema, ``policies[]``)::

        [{"name": "camera_role_ubt"}]

    Filtering: drop entries flagged ``system``, ``default``, or ``readonly`` —
    those are AOS 8 defaults the operator did not customize, and migrating
    them would overwrite Central's own defaults at the role profile.

    Returns ``None`` for empty input (so the engine drops the body key); a
    non-empty filtered list otherwise.
    """
    if not value:
        return None
    out: list[dict[str, str]] = []
    for entry in value:
        if not isinstance(entry, dict):
            continue
        flags = entry.get("_flags", {})
        if isinstance(flags, dict) and (flags.get("system") or flags.get("default") or flags.get("readonly")):
            continue
        pname = entry.get("pname")
        if pname:
            out.append({"name": str(pname)})
    return out if out else None


def vlanstr_to_id_if_numeric(value: Any) -> int | None:
    """Return int VLAN ID if ``value`` is a numeric string, else ``None``.

    AOS 8 stores both VLAN IDs and VLAN names as a single string in
    ``role__vlan.vlanstr``. Central splits these into ``access-vlan-id``
    (int) and ``access-vlan-name`` (string) with a ``vlan-type``
    discriminator. This transform extracts the ID variant; pair with
    ``vlanstr_to_name_if_nonnumeric`` and ``vlanstr_to_vlan_type``.
    """
    if value is None:
        return None
    s = str(value).strip()
    if _VLAN_NUMERIC_RE.fullmatch(s):
        return int(s)
    return None


def vlanstr_to_name_if_nonnumeric(value: Any) -> str | None:
    """Return string VLAN name if ``value`` is a non-numeric string, else ``None``."""
    if value is None:
        return None
    s = str(value).strip()
    if _VLAN_NUMERIC_RE.fullmatch(s) or not s:
        return None
    return s


def vlanstr_to_vlan_type(value: Any) -> str | None:
    """Return ``"VLAN_ID"`` or ``"VLAN_NAME"`` based on whether ``value`` is numeric.

    Central's role schema uses ``vlan-type`` as a discriminator alongside
    ``access-vlan-id`` / ``access-vlan-name``. This transform sources from
    the same AOS 8 ``role__vlan.vlanstr`` field as the two ID/name transforms.
    """
    if value is None:
        return None
    s = str(value).strip()
    if not s:
        return None
    return "VLAN_ID" if _VLAN_NUMERIC_RE.fullmatch(s) else "VLAN_NAME"


def aos8_present_flag_to_bool(value: Any) -> bool | None:
    """Map AOS 8 ``{_present: true}`` style sub-objects to a Python bool.

    AOS 8 surfaces several boolean role sub-properties (e.g. ``role__cp_acc``,
    ``role__openflow``, ``role__enforce_dhcp``) as small objects with a
    ``_present`` discriminator. The engine's ``_path_lookup`` reaches the
    inner ``_present`` value directly, so this transform is mostly a thin
    wrapper that tolerates both bool inputs and missing values.

    Returns ``None`` for missing input so the engine's optional-field path
    drops the corresponding body key; otherwise returns the boolean.
    """
    if value is None:
        return None
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in ("true", "yes", "1", "enabled")
    return bool(value)


_REGISTRY: dict[str, TransformFn] = {
    "direct": direct,
    "direct_str": direct_str,
    "direct_int": direct_int,
    "flag_to_bool": flag_to_bool,
    "split_csv_to_string_array": split_csv_to_string_array,
    "expand_vlan_id_csv": expand_vlan_id_csv,
    "aos8_role_acl_to_central_policies": aos8_role_acl_to_central_policies,
    "vlanstr_to_id_if_numeric": vlanstr_to_id_if_numeric,
    "vlanstr_to_name_if_nonnumeric": vlanstr_to_name_if_nonnumeric,
    "vlanstr_to_vlan_type": vlanstr_to_vlan_type,
    "aos8_present_flag_to_bool": aos8_present_flag_to_bool,
}
