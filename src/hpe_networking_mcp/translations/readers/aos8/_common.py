"""Shared AOS 8 source-record helpers for the canonical readers.

AOS 8 ``effective_config`` wraps most leaf values as ``{<subkey>: value, _flags:
{...}}`` and surfaces system defaults / inherited copies via ``_flags``. These
helpers unwrap those shapes and index referenced profiles by name — the joins
every per-kind reader shares.
"""

from __future__ import annotations

from typing import Any


def leaf(wrapped: Any, subkey: str) -> Any:
    """Unwrap a one-level AOS 8 field; ``None`` if absent or operator-default.

    AOS 8 surfaces a leaf as ``{<subkey>: value, _flags: {default: bool, ...}}``.
    A ``_flags.default`` value is the system default the operator never set, so it
    is treated as absent (drops the resulting Central body key).
    """
    if not isinstance(wrapped, dict):
        return None
    if (wrapped.get("_flags") or {}).get("default"):
        return None
    return wrapped.get(subkey)


def is_system_default(record: Any) -> bool:
    """True when a top-level AOS 8 record is a system default (``_flags.default``).

    System-default records (e.g. ``localip`` / ``controller`` netdestinations,
    built-in roles) are not migrated. Record-level *inherited* filtering stays the
    consumer's job (per the migration skill) — this only flags ``default``.
    """
    return bool(isinstance(record, dict) and (record.get("_flags") or {}).get("default"))


def flag_unless_default(source: dict, key: str) -> bool | None:
    """AOS 8 empty-object presence flag → ``True`` when operator-set, else ``None``.

    Used by the AAA-chain readers: an empty ``{}`` (or ``{_present: ...}``) under
    ``key`` means the operator enabled the feature; a ``_flags.default`` marker or
    an absent key means they did not (so the Central body key drops). This differs
    from the role reader's presence check, which keeps ``_flags.default`` values
    because the role consumer filters defaults at the record level.
    """
    obj = source.get(key)
    if not isinstance(obj, dict):
        return None
    if (obj.get("_flags") or {}).get("default"):
        return None
    return True


def opmode_key(opmode_obj: Any) -> str | None:
    """AOS 8 opmode is ``{<mode>: true, _flags: {...}}`` — return the mode key."""
    if not isinstance(opmode_obj, dict):
        return None
    for k, v in opmode_obj.items():
        if k == "_flags":
            continue
        if v is True or v == "true":
            return k
    return None


def index(records: list[dict] | None, *name_keys: str) -> dict[str, dict]:
    """Index records by their profile/server name (first matching key wins)."""
    out: dict[str, dict] = {}
    for r in records or []:
        if not isinstance(r, dict):
            continue
        for k in name_keys:
            if r.get(k):
                out[r[k]] = r
                break
    return out


def members(group: dict | None) -> list[str]:
    """Member auth-server names listed on an AOS 8 server_group (``auth_server[].name``)."""
    names: list[str] = []
    for m in (group or {}).get("auth_server") or []:
        if isinstance(m, dict) and m.get("name"):
            names.append(m["name"])
    return names
