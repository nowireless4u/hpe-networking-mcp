"""Named transforms referenced by mapping ``key_mappings.transform`` fields.

Each transform takes a source value and returns a target value. Some transforms
return tuples — e.g. ``split_csv_to_string_array`` for VLAN-ID lists returns
both the expanded discrete IDs (for layer2-vlan iteration) and the array form
that preserves range syntax (for alias overrides). The engine picks which
output it needs based on the emit step's iteration rule.

Most transforms have signature ``(value) -> result``. A few — primarily the
``central:policy`` translation's ``aos8_acl_sess_to_central_policy_rules`` —
declare a 2-arg signature ``(value, ctx) -> result`` to receive the engine's
context dict (``source_data`` + ``runtime_values``). The engine inspects
each transform's signature and dispatches accordingly.

Transforms must stay pure (no I/O) so they can be unit-tested in isolation.
"""

from __future__ import annotations

import ipaddress
import re
from collections.abc import Callable
from typing import Any

from hpe_networking_mcp.translations.policy_enum_tables import (
    AOS8_APP_CATEGORY_TO_CENTRAL,
    AOS8_APP_TO_CENTRAL,
    AOS8_WEB_CATEGORY_TO_CENTRAL,
    AOS8_WEB_REPUTATION_TO_CENTRAL,
)

# --------------------------------------------------------------------------- #
# Public registry
# --------------------------------------------------------------------------- #


#: Transform function signature. Most transforms are ``(value) -> result`` (1-arg),
#: but a few (notably ``aos8_acl_sess_to_central_policy_rules``) declare a 2-arg
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


# ============================================================================
# central:policy — AOS 8 acl_sess -> Central policies translation transforms
# ============================================================================
#
# AOS 8 stores access-list session ACLs under ``acl_sess`` with two parallel
# rule arrays per ACL: ``acl_sess__v4policy`` (IPv4) and ``acl_sess__v6policy``
# (IPv6). Each rule has source / destination discriminators, service mode
# (named svc-* / proto+port / app / web-cc / icmp), and an action with optional
# sub-shapes (dst-nat port, redirect target, dual-nat pool, etc.).
#
# Central /policies POST body wraps everything in ``security-policy.policy-rule[]``
# with each rule having ``condition`` (rule-type + source + destination + services
# + ip-header + transport-fields + time-range-name) and ``action`` (type +
# secondary-actions + redirect/source-nat/destination-nat/etc. sub-configs).
#
# The role inversion: AOS 8 binds ACLs to roles via ``role.role__acl[]``;
# Central back-fills ``role.policies[]`` from policy-side ``source.role-list``
# references. The translation receives ``role_attribution: list[str]`` (roles
# that reference this ACL) via ``runtime_values`` — the consumer pre-computes
# this by scanning ``role.role__acl`` across all roles. The translation uses
# ``role_attribution`` to populate ADDRESS_ROLE source/destination role-lists
# for AOS 8 ``suser`` / ``duser`` rules.


# ---------------------------------------------------------------------------- #
# AOS 8 named-service -> Central net-service reference
# ---------------------------------------------------------------------------- #
#
# Central /policies has a built-in ``net-services`` catalog that already
# mirrors AOS 8's svc-* convention (verified live: 73 net-services in the
# operator's tenant including svc-http, svc-https, svc-dns, svc-dhcp,
# svc-icmp, svc-v6-icmp, svc-v6-dhcp, svc-ssh, svc-ftp, svc-telnet,
# svc-smtp, svc-pop3, svc-snmp, svc-snmp-trap, svc-ntp, svc-tftp,
# svc-syslog, svc-radius, svc-tacacs is absent (TACACS uses TCP/49 raw),
# svc-ldap-ssl absent, svc-l2tp, svc-pptp, svc-ike, svc-natt, svc-gre,
# svc-esp, svc-rtsp, etc.).
#
# Translation strategy: pass the AOS 8 svc-name verbatim into Central's
# ``services.net-service`` field. Central will reject unknown names with
# a clear error rather than silently mistranslating, which surfaces real
# catalog mismatches as findings rather than baking in stale port maps.
# Known structural mismatches between AOS 8 and Central naming conventions
# (if any surface) live in ``_AOS8_TO_CENTRAL_SVC_NAME_ALIASES`` near
# ``_build_net_service_block``.


# ---------------------------------------------------------------------------- #
# AOS 8 action -> Central action.type
# ---------------------------------------------------------------------------- #


_AOS8_ACTION_TO_CENTRAL: dict[str, str] = {
    "permit": "ACTION_ALLOW",
    "deny_opt": "ACTION_DENY",
    "deny": "ACTION_DENY",
    "apppermit": "ACTION_ALLOW",
    "appdeny_opt": "ACTION_DENY",
    "appdeny": "ACTION_DENY",
    "src-nat": "ACTION_SOURCE_NAT",
    "dst-nat": "ACTION_DESTINATION_NAT",
    "dual-nat": "ACTION_DUAL_NAT",
    "redir_opt": "ACTION_REDIRECT",
    "redirect": "ACTION_REDIRECT",
    "route": "ACTION_ROUTE",
}


# ---------------------------------------------------------------------------- #
# Helpers: address shape builders (source / destination)
# ---------------------------------------------------------------------------- #


def _netmask_to_prefix(netmask: str) -> int | None:
    """Convert an IPv4 dotted netmask to a CIDR prefix length, or None on bad input."""
    try:
        return ipaddress.IPv4Network(f"0.0.0.0/{netmask}", strict=False).prefixlen
    except (ValueError, ipaddress.NetmaskValueError):
        return None


def _build_address(rule: dict, side: str, address_family: str, role_attribution: list[str]) -> dict[str, Any] | None:
    """Build a Central source/destination dict from one AOS 8 rule's fields.

    ``side``: ``"src"`` or ``"dst"`` — drives which AOS 8 field names to read.
    ``address_family``: ``"IPV4"`` or ``"IPV6"`` — controls IPv4 vs IPv6 sub-fields.
    ``role_attribution``: list of role names that reference this ACL — used to
        populate ADDRESS_ROLE.role-list when AOS 8 source is ``suser`` (the
        implicit "user-of-this-role" semantic).

    Returns the address dict shape per ``ArubaPolicyCondition_SourceConfig`` /
    ``DestinationConfig``, or ``None`` if the rule's discriminator is missing.
    """
    discriminator = rule.get(side)
    if discriminator is None:
        return None
    is_ipv6 = address_family == "IPV6"

    # --- ADDRESS_ANY ---
    # Note: AOS 8 "any any" rules (src=sany AND dst=dany on a role-bound
    # ACL) are bidirectional and Central represents them via TWO rules
    # (role->any AND any->role). That fan-out is handled at the higher
    # _build_central_rules level — _build_address always returns the
    # literal address per the discriminator. The orchestrator decides
    # when to expand.
    if discriminator in ("sany", "dany"):
        return {"type": "ADDRESS_ANY"}

    # --- ADDRESS_LOCAL (slocalip / dlocalip) ---
    if discriminator in ("slocalip", "dlocalip"):
        return {"type": "ADDRESS_LOCAL"}

    # --- ADDRESS_HOST (shost / dhost with sipaddr / dipaddr) ---
    if discriminator in ("shost", "dhost"):
        ip_field = "sipaddr" if side == "src" else "dipaddr"
        ip = rule.get(ip_field)
        if ip is None:
            return None
        host_key = "host-ipv6-address" if is_ipv6 else "host-ipv4-address"
        return {"type": "ADDRESS_HOST", "host-address": {host_key: str(ip)}}

    # --- ADDRESS_NETWORK (snetwork / dnetwork with snetaddr+snetmask / dnetaddr+dnetmask) ---
    if discriminator in ("snetwork", "dnetwork"):
        addr_field = "snetaddr" if side == "src" else "dnetaddr"
        mask_field = "snetmask" if side == "src" else "dnetmask"
        addr = rule.get(addr_field)
        mask = rule.get(mask_field)
        if addr is None or mask is None:
            return None
        if is_ipv6:
            # IPv6 mask is already in prefix form (integer); coerce if string-typed.
            v6_prefix: int = mask if isinstance(mask, int) else int(str(mask))
            return {
                "type": "ADDRESS_NETWORK",
                "network-address": {"network-ipv6-address": f"{addr}/{v6_prefix}"},
            }
        v4_prefix = _netmask_to_prefix(str(mask))
        if v4_prefix is None:
            return None
        return {
            "type": "ADDRESS_NETWORK",
            "network-address": {"network-ipv4-address": f"{addr}/{v4_prefix}"},
        }

    # --- ADDRESS_ALIAS (salias / dalias with srcalias / dstalias) ---
    if discriminator in ("salias", "dalias"):
        alias_field = "srcalias" if side == "src" else "dstalias"
        alias = rule.get(alias_field)
        if alias is None:
            return None
        return {"type": "ADDRESS_ALIAS", "host-address": {"host-address-alias": str(alias)}}

    # --- ADDRESS_ROLE — explicit (suserrole/duserrole + surname/durname) ---
    if discriminator in ("suserrole", "duserrole"):
        name_field = "surname" if side == "src" else "durname"
        role_name = rule.get(name_field)
        if role_name is None:
            return None
        return {"type": "ADDRESS_ROLE", "role": str(role_name)}

    # --- ADDRESS_ROLE — implicit (suser/duser → role_attribution from runtime) ---
    if discriminator in ("suser", "duser"):
        if not role_attribution:
            # No roles reference this ACL — the user-implicit semantic has no
            # equivalent on the Central side; treat as ADDRESS_ANY rather than
            # producing an invalid empty role-list.
            return {"type": "ADDRESS_ANY"}
        return {"type": "ADDRESS_ROLE", "role-list": list(role_attribution)}

    # --- ADDRESS_USER (synonym? AOS 8 uses suser/duser; if a tenant carries
    # an explicit ADDRESS_USER discriminator, map directly) ---
    if discriminator in ("suser_addr", "duser_addr"):
        return {"type": "ADDRESS_USER"}

    # Unknown discriminator — surface as None; consumer / tests will catch
    return None


# ---------------------------------------------------------------------------- #
# Helpers: services / protocol / port / icmp builders
# ---------------------------------------------------------------------------- #


def _build_services_block(rule: dict) -> dict[str, Any] | None:
    """Build Central ``condition.services`` block for app / web-cc rules.

    Triggered by AOS 8 ``service_app == "app_opt"`` rules. The ``app_web_type``
    discriminator (``app`` / ``app_cat`` / ``web_cc_cat`` / ``web_cc_rep``)
    selects which Central services field to populate.
    """
    if rule.get("service_app") != "app_opt":
        return None
    awt = rule.get("app_web_type")
    if awt == "app":
        appname = rule.get("appname")
        if not appname:
            return None
        # Look up Central enum value; fall back to source value verbatim if
        # not in the table (lets unknown-but-valid Central enum names pass through).
        central_val = AOS8_APP_TO_CENTRAL.get(str(appname), str(appname))
        return {"services": {"application": central_val}}
    if awt == "app_cat":
        cat = rule.get("appname")
        if not cat:
            return None
        central_val = AOS8_APP_CATEGORY_TO_CENTRAL.get(str(cat), str(cat).upper())
        return {"services": {"app-category": central_val}}
    if awt in ("web_cc_cat",):
        cat = rule.get("webcccatgname")
        if not cat:
            return None
        central_val = AOS8_WEB_CATEGORY_TO_CENTRAL.get(str(cat), str(cat).replace("/", "-").upper())
        return {"services": {"web-category": central_val}}
    if awt in ("web_cc_rep",):
        rep = rule.get("web_rep2") or rule.get("web_rep")
        if not rep:
            return None
        # web_rep2 may carry suffix like "high-risk2"; strip trailing digit.
        rep_norm = re.sub(r"\d+$", "", str(rep)) or str(rep)
        central_val = AOS8_WEB_REPUTATION_TO_CENTRAL.get(rep_norm, rep_norm.replace("-", "_").upper())
        return {"services": {"web-reputation": central_val}}
    return None


def _build_net_service_block(rule: dict) -> dict[str, Any] | None:
    """Build Central ``services.net-service`` reference for AOS 8 named svc-* rules.

    Central ships 60+ pre-configured net-services whose names mirror AOS 8's
    svc-* convention (svc-http, svc-https, svc-dns, svc-dhcp, svc-icmp,
    svc-ssh, svc-ftp, svc-snmp, svc-ntp, svc-tftp, svc-syslog, svc-radius,
    svc-tacacs, svc-ldap, svc-pptp, svc-l2tp, svc-ike, svc-natt, svc-gre,
    svc-esp, svc-rtsp, svc-pop3, svc-smtp, svc-telnet, etc.). Operators can
    also define custom net-services. The translation passes the AOS 8 svc
    name through verbatim — Central rejects unknown names with a clear
    error rather than silently mistranslating.

    Known structural mismatches (AOS 8 form vs Central form) get aliased
    via ``_AOS8_TO_CENTRAL_SVC_NAME_ALIASES`` below; the alias table starts
    empty and grows as live mismatches are observed.

    Returns ``{"services": {"net-service": "<name>"}}`` or ``None`` for
    non-service-name rules.
    """
    if rule.get("svc") != "service-name" or rule.get("service_app") != "service":
        return None
    name = rule.get("service-name") or rule.get("service_name")
    if not name:
        return None
    central_name = _AOS8_TO_CENTRAL_SVC_NAME_ALIASES.get(str(name), str(name))
    return {"services": {"net-service": central_name}}


# Alias table for AOS 8 svc-* names that don't match Central's catalog
# verbatim. Empty by default — Central's catalog (verified 2026-05-07,
# 73 net-services in the operator's tenant) closely mirrors AOS 8's
# naming. Add entries when live mismatches surface (e.g. AOS 8
# 'svc-icmpv6' would alias to Central 'svc-v6-icmp' if/when observed).
_AOS8_TO_CENTRAL_SVC_NAME_ALIASES: dict[str, str] = {}


def _build_protocol_port_block(rule: dict) -> dict[str, Any] | None:
    """Build Central ``ip-header`` + ``transport-fields`` for ICMP / proto+port rules.

    Handles two AOS 8 service modes:

    * ``svc: "icmp"`` (with optional ``icmp_type``) — emits
      ``ip-header.protocol: IP_ICMP`` plus ``ip-header.icmp.icmp-type``.
    * ``svc: "tcp_udp"`` (raw protocol + port spec) — emits
      ``ip-header.protocol: IP_TCP|IP_UDP`` plus ``transport-fields.
      destination-port: {min, max}``.

    Named svc-* services (``svc: "service-name"``) are handled separately
    by ``_build_net_service_block`` — those reference Central's pre-existing
    net-service catalog rather than expanding to raw protocol+port.
    """
    svc_mode = rule.get("svc")
    service_app = rule.get("service_app")

    if service_app != "service":
        return None

    # ICMP (svc: "icmp" with optional icmp_type)
    if svc_mode == "icmp":
        ip_header: dict[str, Any] = {"protocol": "IP_ICMP"}
        icmp_type = rule.get("icmp_type")
        if icmp_type:
            ip_header["icmp"] = {"icmp-type": str(icmp_type)}
        return {"ip-header": ip_header}

    # Raw proto + port (svc: "tcp_udp" with proto + port + port1/port2)
    if svc_mode in ("tcp_udp", "tcp", "udp"):
        proto = rule.get("proto")
        proto_enum = {"tcp": "IP_TCP", "udp": "IP_UDP"}.get(str(proto).lower())
        if proto_enum is None:
            return None
        out: dict[str, Any] = {"ip-header": {"protocol": proto_enum}}
        # AOS 8 'port' field carries the mode ("eq", "range", "lt", "gt");
        # values are in port1 (and port2 for ranges). Normalise to a
        # min/max pair — the mode discriminator isn't needed once we have
        # both endpoints.
        port1 = rule.get("port1")
        port2 = rule.get("port2")
        if port1 is not None:
            min_port = int(port1)
            max_port = int(port2) if port2 is not None else min_port
            out["transport-fields"] = {"destination-port": {"min": min_port, "max": max_port}}
        return out

    # service-any / service-name handled elsewhere
    return None


def _determine_rule_type(rule: dict, services_block: dict | None, proto_port_block: dict | None) -> str:
    """Pick the appropriate Central ``condition.rule-type`` enum value."""
    if services_block is not None:
        services = services_block.get("services", {})
        # Named-service reference (svc-http, svc-dns, etc.)
        if "net-service" in services:
            return "RULE_NET_SERVICE"
        # App / web rules
        if "application" in services:
            return "RULE_APPLICATION"
        if "app-category" in services:
            return "RULE_APP_CATEGORY"
        if "web-category" in services:
            return "RULE_WEB_CATEGORY"
        if "web-reputation" in services:
            return "RULE_WEB_REPUTATION"
    # Protocol/port rules
    if proto_port_block is not None:
        protocol = proto_port_block.get("ip-header", {}).get("protocol")
        if protocol == "IP_TCP":
            return "RULE_TCP"
        if protocol == "IP_UDP":
            return "RULE_UDP"
        # ICMP, ESP, GRE, etc. → generic RULE_PROTOCOL (live-verified shape)
        return "RULE_PROTOCOL"
    # Default
    return "RULE_ANY"


# ---------------------------------------------------------------------------- #
# Helpers: action builder
# ---------------------------------------------------------------------------- #


def _build_action(rule: dict) -> dict[str, Any]:
    """Build Central ``action`` dict from one AOS 8 rule's action + sub-fields."""
    aos8_action = rule.get("action") or rule.get("appaction")
    central_type = _AOS8_ACTION_TO_CENTRAL.get(str(aos8_action), "ACTION_ALLOW")
    action: dict[str, Any] = {"type": central_type}

    # Secondary actions: log
    if rule.get("log"):
        action.setdefault("secondary-actions", {})["log"] = True

    # send-deny-response (app deny rules)
    if rule.get("app-send-deny-response"):
        action["send-deny-response"] = True

    # destination-nat sub-config
    if central_type == "ACTION_DESTINATION_NAT":
        dst_nat: dict[str, Any] = {}
        if rule.get("dnatport") is not None:
            dst_nat["dest-port"] = int(rule["dnatport"])
        if rule.get("dnataddr") is not None:
            dst_nat["dest-address"] = str(rule["dnataddr"])
        if dst_nat:
            action["destination-nat"] = dst_nat

    # source-nat sub-config (no specific AOS 8 sub-fields seen in samples; placeholder)
    # dual-nat sub-config
    if central_type == "ACTION_DUAL_NAT":
        dual_nat: dict[str, Any] = {}
        if rule.get("dualnatport") is not None:
            dual_nat["dest-port"] = int(rule["dualnatport"])
        if rule.get("dualnatpool") is not None:
            dual_nat["pool"] = str(rule["dualnatpool"])
        if dual_nat:
            action["dual-nat"] = dual_nat

    # redirect sub-config (live-verified: re_dir + tunid / tungrpname)
    if central_type == "ACTION_REDIRECT":
        re_dir = rule.get("re_dir")
        redirect: dict[str, Any] = {}
        if re_dir == "tunnel" and rule.get("tunid") is not None:
            redirect["tunnel-id"] = int(rule["tunid"])
        elif re_dir == "tunnel-group" and rule.get("tungrpname") is not None:
            redirect["tunnel-group"] = str(rule["tungrpname"])
        # esi-group / datapath variants intentionally not handled (operator
        # scope-out — see translation's draft_notes)
        if redirect:
            action["redirect"] = redirect

    return action


# ---------------------------------------------------------------------------- #
# Per-rule orchestration: build one Central rule from one AOS 8 rule
# ---------------------------------------------------------------------------- #


def _build_central_rules(
    aos8_rule: dict,
    address_family: str,
    starting_position: int,
    role_attribution: list[str],
) -> list[dict[str, Any]]:
    """Build the Central ``policy-rule[]`` entries for one AOS 8 v4/v6policy rule.

    Returns a list of 0, 1, or 2 Central rule dicts:

    * 0 — the source rule is malformed (missing discriminators / unknown
      address types we can't translate). Caller skips it.
    * 1 — the typical case: one AOS 8 rule maps to one Central rule.
    * 2 — the AOS 8 "any any" pattern (src=sany AND dst=dany) on a role-
      bound ACL expands to TWO Central rules (role->any AND any->role)
      because Central can't represent "any any" for a role-bound policy
      — and AOS 8's any-any semantic is bidirectional, so a single
      role->any rule would lose the return-traffic match.

    Position numbers are assigned sequentially starting from
    ``starting_position`` so the caller can compute the next starting
    position via ``starting_position + len(returned)``.
    """
    # Build the shared condition pieces (services, proto/port, time-range)
    # and the action — these are identical across both rules of an
    # any-any expansion.
    net_service_block = _build_net_service_block(aos8_rule)
    services_block = net_service_block or _build_services_block(aos8_rule)
    proto_port_block = _build_protocol_port_block(aos8_rule)
    rule_type = _determine_rule_type(aos8_rule, services_block, proto_port_block)
    action = _build_action(aos8_rule)
    time_range = aos8_rule.get("trname")

    def _make_rule(pos: int, source: dict, destination: dict) -> dict[str, Any]:
        condition: dict[str, Any] = {
            "rule-type": rule_type,
            "address-family": address_family,
            "source": source,
            "destination": destination,
        }
        if services_block:
            condition.update(services_block)
        if proto_port_block:
            condition.update(proto_port_block)
        if time_range:
            condition["time-range-name"] = str(time_range)
        return {"position": pos, "condition": condition, "action": action}

    # Detect the bidirectional any-any case (operator-confirmed rule):
    # AOS 8 "any any" on a role-bound ACL is bidirectional; Central
    # represents this as two unidirectional rules role->any AND any->role.
    is_any_any = aos8_rule.get("src") == "sany" and aos8_rule.get("dst") == "dany"
    if is_any_any and role_attribution:
        role_addr = {"type": "ADDRESS_ROLE", "role-list": list(role_attribution)}
        any_addr = {"type": "ADDRESS_ANY"}
        return [
            _make_rule(starting_position, role_addr, any_addr),
            _make_rule(starting_position + 1, any_addr, role_addr),
        ]

    # Normal single-rule path
    src = _build_address(aos8_rule, "src", address_family, role_attribution)
    dst = _build_address(aos8_rule, "dst", address_family, role_attribution)
    if src is None or dst is None:
        return []
    return [_make_rule(starting_position, src, dst)]


# ---------------------------------------------------------------------------- #
# Top-level transform: full ACL -> Central policy-rule[] array
# ---------------------------------------------------------------------------- #


def aos8_acl_sess_to_central_policy_rules(value: Any, ctx: dict[str, Any]) -> list[dict[str, Any]] | None:
    """Build Central ``security-policy.policy-rule[]`` from an AOS 8 acl_sess record.

    2-arg transform (signature dispatch by the engine). ``value`` is whatever
    the key_mapping's ``from`` path resolves to — we ignore it in favor of the
    full source record at ``ctx["source_data"]``, since the policy rules need
    BOTH ``acl_sess__v4policy`` and ``acl_sess__v6policy`` simultaneously.

    Reads ``ctx["runtime_values"]["role_attribution"]`` (list of role names that
    reference this ACL — pre-computed by the consumer) to populate
    ADDRESS_ROLE.role-list for AOS 8 ``suser`` / ``duser`` rules.

    Returns the rule array, or ``None`` if the source has no rules at all (per
    the LLD's "empty ACL not migrated" rule — engine drops the body key).
    """
    source_data = ctx.get("source_data") or {}
    runtime_values = ctx.get("runtime_values") or {}
    role_attribution = list(runtime_values.get("role_attribution") or [])

    out: list[dict[str, Any]] = []
    position = 1
    for variant_field, address_family in (
        ("acl_sess__v4policy", "IPV4"),
        ("acl_sess__v6policy", "IPV6"),
    ):
        for aos8_rule in source_data.get(variant_field, []) or []:
            if not isinstance(aos8_rule, dict):
                continue
            # Defensive: skip system / inherited rules. Consumer should
            # pre-filter, but a stray inherited entry shouldn't break the build.
            flags = aos8_rule.get("_flags") or {}
            if flags.get("inherited") or flags.get("system"):
                continue
            built = _build_central_rules(aos8_rule, address_family, position, role_attribution)
            if not built:
                continue
            out.extend(built)
            position += len(built)
    return out or None


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
    "aos8_acl_sess_to_central_policy_rules": aos8_acl_sess_to_central_policy_rules,
}
