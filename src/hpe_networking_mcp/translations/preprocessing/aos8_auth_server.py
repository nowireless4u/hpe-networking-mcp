"""AOS 8 ``rad_server`` / ``tacacs_server`` → normalized auth-server source shape.

``central:auth_server`` accepts BOTH AOS 8 source objects in one translation —
their REST field names diverge (``rad_*`` vs ``tacacs_*``) and every value is
wrapped one level deep (e.g. ``rad_host: {"host": ...}``, ``rad_timeout:
{"timeout": ...}``), neither of which fits a shared per-field ``key_mapping``.
This preprocessing function detects the object type and flattens it into a single
``_<field>`` shape the key_mappings consume. Mirrors how ``central:net_group``
handles ``netdst`` + ``netdst6`` in one translation.

Field-name correspondence is locked against the vendored AOS 8 OAS
(``vendor/aos8/`` — ``/object/rad_server`` 28 fields, ``/object/tacacs_server``
10 fields) and the Central ``auth-servers`` body observed live.
"""

from __future__ import annotations

from typing import Any


def _leaf(wrapped: Any, subkey: str) -> Any:
    """Unwrap an AOS 8 single-key field (``{subkey: value, _flags: {...}}``).

    Returns ``None`` when the field is absent or operator-undefined
    (``_flags.default`` is set), so the optional-field drop leaves the Central
    body key unset — Central then applies its own default rather than us pinning
    AOS 8's resolved default value.
    """
    if not isinstance(wrapped, dict):
        return None
    if (wrapped.get("_flags") or {}).get("default"):
        return None
    return wrapped.get(subkey)


def _present_flag(source: dict, key: str) -> bool | None:
    """AOS 8 empty-object flag field (``{}`` present = enabled) → ``True`` / ``None``."""
    obj = source.get(key)
    if not isinstance(obj, dict):
        return None
    if (obj.get("_flags") or {}).get("default"):
        return None
    return True


def _coa_peer(host: Any, coa_servers: Any) -> dict | None:
    """Find a co-located CoA (RFC 3576) server whose IP matches the RADIUS host.

    ``coa_servers`` is the operator-supplied ``aaa_prof.rfc3576_client[]`` list
    (passed via runtime_values). AOS 8 keeps CoA as a server reference nested in
    the aaa-profile; Central folds it onto the co-located RADIUS auth-server as
    ``radius-server-mode: AUTH_AND_COA`` + ``dynamic-authorization-enable``
    (issue #322 — co-location-aware correlation). Matches on the entry's
    ``rfc3576_server`` / ``server_ip``.
    """
    if not host or not isinstance(coa_servers, list):
        return None
    for entry in coa_servers:
        if not isinstance(entry, dict):
            continue
        ip = entry.get("rfc3576_server") or entry.get("server_ip")
        if ip and ip == host:
            return entry
    return None


def preprocess_auth_server(source_data: dict, runtime_values: dict) -> dict:
    """Flatten a ``rad_server`` or ``tacacs_server`` record into ``_<field>`` keys."""
    sd = source_data
    is_tacacs = "tacacs_server_name" in sd or "tacacs_host" in sd

    if is_tacacs:
        norm: dict[str, Any] = {
            "_type": "TACACS",
            "_name": sd.get("tacacs_server_name"),
            "_host": _leaf(sd.get("tacacs_host"), "host"),
            "_secret": _leaf(sd.get("tacacs_key"), "key"),
            # TACACS has a single TCP port; map it into the shared port slot.
            "_auth_port": _leaf(sd.get("tacacs_tcpport"), "tcp-port"),
            "_timeout": _leaf(sd.get("tacacs_timeout"), "timeout"),
            "_retransmit": _leaf(sd.get("tacacs_retransmit"), "retransmit"),
            # RADIUS-only fields stay None for a TACACS source (optional-drop).
            "_acct_port": None,
            "_nas_id": None,
            "_nas_ip": None,
            "_nas_ip6": None,
            "_enable_radsec": None,
            "_radsec_port": None,
            "_radius_server_mode": None,
            "_dynamic_auth": None,
        }
    else:
        norm = {
            "_type": "RADIUS",
            "_name": sd.get("rad_server_name"),
            "_host": _leaf(sd.get("rad_host"), "host"),
            "_secret": _leaf(sd.get("rad_key"), "key"),
            "_auth_port": _leaf(sd.get("rad_authport"), "authport"),
            "_acct_port": _leaf(sd.get("rad_acctport"), "acctport"),
            "_timeout": _leaf(sd.get("rad_timeout"), "timeout"),
            "_retransmit": _leaf(sd.get("rad_retransmit"), "retransmit"),
            "_nas_id": _leaf(sd.get("rad_nasid"), "nas-identifier"),
            "_nas_ip": _leaf(sd.get("rad_nasip"), "nas-ip"),
            "_nas_ip6": _leaf(sd.get("rad_nasip6"), "nas-ip6"),
            "_enable_radsec": _present_flag(sd, "radsec_enable"),
            "_radsec_port": _leaf(sd.get("radsec_port"), "radsec-port"),
            # CoA correlation (issue #322): set below if a co-located RFC 3576
            # server exists; left as plain AUTH (Central default) otherwise.
            "_radius_server_mode": None,
            "_dynamic_auth": None,
        }
        coa = _coa_peer(norm["_host"], (runtime_values or {}).get("coa_servers"))
        if coa is not None:
            norm["_radius_server_mode"] = "AUTH_AND_COA"
            norm["_dynamic_auth"] = True

    # Omit None-valued keys so the engine skips absent optional fields (their
    # ``from`` path resolves to "missing", which the optional key_mapping drops)
    # rather than running a typed transform like direct_int on None. Required
    # fields (name/type/host/secret) carry real values; a genuinely-missing
    # required field stays absent and fails loud on its non-optional mapping.
    return {**source_data, **{k: v for k, v in norm.items() if v is not None}}
