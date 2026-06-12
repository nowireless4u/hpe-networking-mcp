"""Named transforms referenced by mapping ``key_mappings.transform`` fields.

Each transform takes a source value and returns a target value. Some transforms
return tuples — e.g. ``split_csv_to_string_array`` for VLAN-ID lists returns
both the expanded discrete IDs (for layer2-vlan iteration) and the array form
that preserves range syntax (for alias overrides). The engine picks which
output it needs based on the emit step's iteration rule.

Most transforms have signature ``(value) -> result``. A few — primarily the
declare a 2-arg signature ``(value, ctx) -> result`` to receive the engine's
context dict (``source_data`` + ``runtime_values``). The engine inspects
each transform's signature and dispatches accordingly.

Transforms must stay pure (no I/O) so they can be unit-tested in isolation.
"""

from __future__ import annotations

import re
from collections.abc import Callable
from typing import Any

# --------------------------------------------------------------------------- #
# Public registry
# --------------------------------------------------------------------------- #


#: Transform function signature. Most transforms are ``(value) -> result`` (1-arg),
#: signature ``(value, ctx) -> result`` to receive the engine's context dict.
#: ``Callable[..., Any]`` accepts both forms; the engine inspects the actual
#: signature at dispatch time and passes ctx accordingly.
TransformFn = Callable[..., Any]


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


def aos8_field_present_to_true(value: Any) -> bool | None:
    """Map AOS 8 "field is present in payload" semantics to a Python ``True``.

    AOS 8 surfaces several boolean role sub-properties as empty dicts when
    configured (e.g. ``role__enforce_dhcp: {}``, ``role__reg_role: {}``,
    ``role__dpi_disable: {}``). The presence of the parent path means the
    operator enabled the feature; absence means they did not. Reaching this
    transform implies the engine's ``_path_lookup`` already succeeded — so
    the value is "configured" regardless of payload contents (empty dict,
    ``{_present: true}``, or any other shape).

    Returns ``True`` for any non-``None`` input; ``None`` for ``None``
    (so the engine's optional-field path drops the body key).
    """
    if value is None:
        return None
    return True


def aos8_reauth_minutes_value(value: Any) -> int | None:
    """Extract ``reauthperiod`` from ``role__reauth`` only when it's the minutes form.

    Source shape::

        {"reauthperiod": <int>}                       # minutes (default form)
        {"seconds": true, "reauthperiod": <int>}      # seconds form

    Returns ``reauthperiod`` only when ``seconds`` is absent / falsy;
    returns ``None`` for the seconds form so the seconds companion mapping
    can claim the value instead. ``None`` propagates to drop the body key.
    """
    if not isinstance(value, dict):
        return None
    if value.get("seconds"):
        return None
    period = value.get("reauthperiod")
    return int(period) if period is not None else None


def aos8_reauth_seconds_value(value: Any) -> int | None:
    """Extract ``reauthperiod`` from ``role__reauth`` only when it's the seconds form.

    Companion to ``aos8_reauth_minutes_value``. Returns the value only when
    ``seconds`` is truthy on the source dict.
    """
    if not isinstance(value, dict):
        return None
    if not value.get("seconds"):
        return None
    period = value.get("reauthperiod")
    return int(period) if period is not None else None


# --------------------------------------------------------------------------- #
# Bandwidth-contract transforms
# --------------------------------------------------------------------------- #
#
# AOS 8 carries role bandwidth-contract bindings in three source arrays that
# Central CNX splits into FIVE distinct schemas (plus two exclude variants):
#
#   role__bwc            -> aaa-bw-contract.bw-contract[]
#   role__bwc_app        -> app-aaa-contract.app[]                  (app_type="app")
#                        -> app-category-aaa-contract.app-category[] (app_type="appcategory")
#   role__bwc_web        -> web-category-aaa-contract.web-category[] (web_opt="web-cc-category")
#                        -> web-reputation-aaa-contract.web-reputation[] (web_opt="web-cc-reputation")
#
# Each transform filters the relevant source variant, normalises the casing
# (Central enums use UPPERCASE direction / reputation / category-name),
# renames the source fields to their Central equivalents, and returns
# ``None`` for empty-after-filter so the engine drops the body key.
#
# Live samples used to author these came from two roles in the operator's
# tenant: ``blacklisted`` (basic per-role) and ``parent`` at /md/Campus/West
# (per-app + per-appcategory + per-web-cc-category + per-web-cc-reputation).


def _norm_direction(value: Any) -> str:
    """AOS 8 lowercase 'downstream'/'upstream' -> Central UPPERCASE enum."""
    return str(value).strip().upper()


def aos8_role_bwc_basic_to_central(value: Any) -> list[dict[str, str]] | None:
    """Map ``role__bwc[]`` to Central's ``aaa-bw-contract.bw-contract[]``.

    Source items: ``{"dir_type": "downstream"|"upstream", "name": "<contract>"}``.
    Target items: ``{"bwc-name", "direction": "DOWNSTREAM"|"UPSTREAM"}``.

    AOS 8 doesn't carry the ``association`` field (per-user vs per-apgroup);
    Central will apply its default. Returns ``None`` for empty input so the
    engine drops the body key.
    """
    if not isinstance(value, list) or not value:
        return None
    out: list[dict[str, str]] = []
    for entry in value:
        if not isinstance(entry, dict):
            continue
        name = entry.get("name")
        dir_type = entry.get("dir_type")
        if name and dir_type:
            out.append({"bwc-name": str(name), "direction": _norm_direction(dir_type)})
    return out or None


def aos8_role_bwc_app_filter_app(value: Any) -> list[dict[str, str]] | None:
    """Filter ``role__bwc_app[]`` to ``app_type == "app"``; rename for Central.

    Source items (filtered): ``{"app_type": "app", "dir": "...", "appname": "<dpi-app>", "name": "<contract>"}``.
    Target items: ``{"appname", "bwc-name", "direction"}``.

    NOTE: Central's ``appname`` is an enum of ~3953 DPI app identifiers. AOS 8
    source values pass through as-is; if AOS 8 and Central's DPI catalog drift
    apart, the operator may need to remap unrecognized app names manually.
    """
    if not isinstance(value, list):
        return None
    out: list[dict[str, str]] = []
    for entry in value:
        if not isinstance(entry, dict) or entry.get("app_type") != "app":
            continue
        appname = entry.get("appname")
        name = entry.get("name")
        direction = entry.get("dir")
        if appname and name and direction:
            out.append(
                {
                    "appname": str(appname),
                    "bwc-name": str(name),
                    "direction": _norm_direction(direction),
                }
            )
    return out or None


def aos8_role_bwc_app_filter_appcategory(value: Any) -> list[dict[str, str]] | None:
    """Filter ``role__bwc_app[]`` to ``app_type == "appcategory"``; rename + uppercase.

    Source (filtered): ``{"app_type": "appcategory", "dir": "...",
    "appname": "streaming", "name": "<contract>"}``.
    Target: ``{"category-name": "STREAMING", "bwc-name", "direction"}``.

    Central's ``category-name`` is an enum of 24 UPPERCASE-DASHED app category
    identifiers; this transform uppercases the AOS 8 source value (``streaming``
    -> ``STREAMING``) and otherwise passes through verbatim.
    """
    if not isinstance(value, list):
        return None
    out: list[dict[str, str]] = []
    for entry in value:
        if not isinstance(entry, dict) or entry.get("app_type") != "appcategory":
            continue
        cat = entry.get("appname")
        name = entry.get("name")
        direction = entry.get("dir")
        if cat and name and direction:
            out.append(
                {
                    "category-name": str(cat).upper(),
                    "bwc-name": str(name),
                    "direction": _norm_direction(direction),
                }
            )
    return out or None


def aos8_role_bwc_web_filter_category(value: Any) -> list[dict[str, str]] | None:
    """Filter ``role__bwc_web[]`` to ``web_opt == "web-cc-category"``; rename + normalise.

    Source (filtered): ``{"web_opt": "web-cc-category", "dir": "...",
    "webcccatgname": "streaming/media", "name": "<contract>"}``.
    Target: ``{"webcategory-name": "STREAMING-MEDIA", "bwc-name", "direction"}``.

    Central's ``webcategory-name`` is an enum of 85 UPPERCASE-DASHED Web Content
    Classification category names. The transform uppercases and replaces ``/``
    with ``-`` to match Central's casing convention. Live example: AOS 8
    ``streaming/media`` -> Central ``STREAMING-MEDIA`` (slash to dash + uppercase).

    Caveat: only the simplest ``a/b -> A-B`` mapping is performed. Some Central
    category names include connective words AOS 8 omits (e.g. AOS 8 may store
    ``entertainment/arts`` while Central wants ``ENTERTAINMENT-AND-ARTS``).
    Operators should spot-check categories with multi-word Central forms after
    migration.
    """
    if not isinstance(value, list):
        return None
    out: list[dict[str, str]] = []
    for entry in value:
        if not isinstance(entry, dict) or entry.get("web_opt") != "web-cc-category":
            continue
        cat = entry.get("webcccatgname")
        name = entry.get("name")
        direction = entry.get("dir")
        if cat and name and direction:
            out.append(
                {
                    "webcategory-name": str(cat).replace("/", "-").upper(),
                    "bwc-name": str(name),
                    "direction": _norm_direction(direction),
                }
            )
    return out or None


def aos8_role_bwc_web_filter_reputation(value: Any) -> list[dict[str, str]] | None:
    """Filter ``role__bwc_web[]`` to ``web_opt == "web-cc-reputation"``; rename + uppercase.

    Source (filtered): ``{"web_opt": "web-cc-reputation", "dir": "...",
    "web_rep": "trustworthy", "name": "<contract>"}``.
    Target: ``{"webrepname": "TRUSTWORTHY", "bwc-name", "direction"}``.

    Central's ``webrepname`` is a 5-value enum (TRUSTWORTHY / LOW_RISK /
    MODERATE_RISK / SUSPICIOUS / HIGH_RISK). AOS 8 stores the lowercase form;
    this transform uppercases. Underscores in the multi-word forms (``low-risk``
    vs ``LOW_RISK``) are handled by replacing ``-`` with ``_``.
    """
    if not isinstance(value, list):
        return None
    out: list[dict[str, str]] = []
    for entry in value:
        if not isinstance(entry, dict) or entry.get("web_opt") != "web-cc-reputation":
            continue
        rep = entry.get("web_rep")
        name = entry.get("name")
        direction = entry.get("dir")
        if rep and name and direction:
            out.append(
                {
                    "webrepname": str(rep).replace("-", "_").upper(),
                    "bwc-name": str(name),
                    "direction": _norm_direction(direction),
                }
            )
    return out or None


def aos8_role_bwc_excl_filter_app(value: Any) -> list[dict[str, str]] | None:
    """Filter ``role__bwc_ex[]`` to ``app_type == "app"``; rename for Central.

    Source (filtered): ``{"app_type": "app", "appname": "<dpi-app>"}``.
    Target: ``{"exclude-app-name": "<dpi-app>"}``.

    The exclude variant carries no traffic direction and no contract
    reference — listed apps simply bypass bandwidth-contract enforcement.
    """
    if not isinstance(value, list):
        return None
    out: list[dict[str, str]] = []
    for entry in value:
        if not isinstance(entry, dict) or entry.get("app_type") != "app":
            continue
        appname = entry.get("appname")
        if appname:
            out.append({"exclude-app-name": str(appname)})
    return out or None


def aos8_role_bwc_excl_filter_appcategory(value: Any) -> list[dict[str, str]] | None:
    """Filter ``role__bwc_ex[]`` to ``app_type == "appcategory"``; rename + uppercase.

    Source (filtered): ``{"app_type": "appcategory", "appname": "collaboration"}``.
    Target: ``{"exclude-app-category-name": "COLLABORATION"}``.

    Companion to ``aos8_role_bwc_excl_filter_app`` — sources from the same
    ``role__bwc_ex`` array but filters to the appcategory variant. The
    AOS 8 ``appname`` field carries the category name (a quirk of the
    source schema reusing the field for both variants).
    """
    if not isinstance(value, list):
        return None
    out: list[dict[str, str]] = []
    for entry in value:
        if not isinstance(entry, dict) or entry.get("app_type") != "appcategory":
            continue
        cat = entry.get("appname")
        if cat:
            out.append({"exclude-app-category-name": str(cat).upper()})
    return out or None


def aos8_server_group_members(value: Any) -> list[dict[str, Any]]:
    """AOS 8 ``server_group_prof.auth_server[]`` → Central ``servers[]``.

    Each member maps to ``{"server-name": <name>, "position": <1-based>}``,
    preserving the AOS 8 ordering (auth precedence); entries without a name are
    dropped. The referenced auth-servers must already exist in Central
    (central:auth_server runs first).

    NOTE: member ``_flags.inherited`` is NOT a drop signal — it merely reflects
    that the whole group was authored at an ancestor scope (every member then
    shows ``inherited`` at descendant scopes). Record-level inheritance
    filtering is the consumer's job (skip inherited *groups* before emit), the
    same convention as central:net_group / central:role.
    """
    if not isinstance(value, list):
        return []
    servers: list[dict[str, Any]] = []
    position = 1
    for member in value:
        if not isinstance(member, dict):
            continue
        name = member.get("name")
        if not name:
            continue
        servers.append({"server-name": str(name), "position": position})
        position += 1
    return servers


_REGISTRY: dict[str, TransformFn] = {
    "direct": direct,
    "direct_str": direct_str,
    "direct_int": direct_int,
    "flag_to_bool": flag_to_bool,
    "split_csv_to_string_array": split_csv_to_string_array,
    "expand_vlan_id_csv": expand_vlan_id_csv,
    "vlanstr_to_id_if_numeric": vlanstr_to_id_if_numeric,
    "vlanstr_to_name_if_nonnumeric": vlanstr_to_name_if_nonnumeric,
    "vlanstr_to_vlan_type": vlanstr_to_vlan_type,
    "aos8_field_present_to_true": aos8_field_present_to_true,
    "aos8_reauth_minutes_value": aos8_reauth_minutes_value,
    "aos8_reauth_seconds_value": aos8_reauth_seconds_value,
    "aos8_role_bwc_basic_to_central": aos8_role_bwc_basic_to_central,
    "aos8_role_bwc_app_filter_app": aos8_role_bwc_app_filter_app,
    "aos8_role_bwc_app_filter_appcategory": aos8_role_bwc_app_filter_appcategory,
    "aos8_role_bwc_web_filter_category": aos8_role_bwc_web_filter_category,
    "aos8_role_bwc_web_filter_reputation": aos8_role_bwc_web_filter_reputation,
    "aos8_role_bwc_excl_filter_app": aos8_role_bwc_excl_filter_app,
    "aos8_role_bwc_excl_filter_appcategory": aos8_role_bwc_excl_filter_appcategory,
    "aos8_server_group_members": aos8_server_group_members,
}
