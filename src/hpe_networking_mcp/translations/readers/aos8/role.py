"""AOS 8 → canonical user-role reader.

Mirrors the validated ``central:role`` key-mappings + transforms exactly (no
``_flags`` filtering — record/sub-object inheritance + default filtering stays the
migration skill's job, matching the old engine's consumer contract). AOS 8
surfaces booleans as *field presence* (empty ``{}`` or ``{_present: ...}``), so
those map to ``True`` when the key exists and ``None`` otherwise.
"""

from __future__ import annotations

import re
from typing import Any

from hpe_networking_mcp.translations.canonical.role import CanonicalRole

_VLAN_NUMERIC_RE = re.compile(r"^\d+$")


def _path(record: dict[str, Any], *keys: str) -> Any:
    """Nested lookup; ``None`` on any missing key or non-dict hop."""
    cur: Any = record
    for k in keys:
        if not isinstance(cur, dict) or k not in cur:
            return None
        cur = cur[k]
    return cur


def _present(record: dict[str, Any], key: str) -> bool | None:
    """AOS 8 presence-to-True: ``True`` when ``key`` carries a non-None value, else ``None``."""
    return True if record.get(key) is not None else None


def _vlanstr_id(value: Any) -> int | None:
    if value is None:
        return None
    s = str(value).strip()
    return int(s) if _VLAN_NUMERIC_RE.fullmatch(s) else None


def _vlanstr_name(value: Any) -> str | None:
    if value is None:
        return None
    s = str(value).strip()
    return None if (not s or _VLAN_NUMERIC_RE.fullmatch(s)) else s


def _vlanstr_type(value: Any) -> str | None:
    if value is None:
        return None
    s = str(value).strip()
    if not s:
        return None
    return "VLAN_ID" if _VLAN_NUMERIC_RE.fullmatch(s) else "VLAN_NAME"


def _reauth_minutes(value: Any) -> int | None:
    if not isinstance(value, dict) or value.get("seconds"):
        return None
    period = value.get("reauthperiod")
    return int(period) if period is not None else None


def _reauth_seconds(value: Any) -> int | None:
    if not isinstance(value, dict) or not value.get("seconds"):
        return None
    period = value.get("reauthperiod")
    return int(period) if period is not None else None


def _norm_dir(value: Any) -> str:
    return str(value).strip().upper()


def _bwc_basic(value: Any) -> list[dict[str, str]] | None:
    if not isinstance(value, list):
        return None
    out = [
        {"bwc-name": str(e["name"]), "direction": _norm_dir(e["dir_type"])}
        for e in value
        if isinstance(e, dict) and e.get("name") and e.get("dir_type")
    ]
    return out or None


def _bwc_app(value: Any, app_type: str) -> list[dict[str, str]] | None:
    """``role__bwc_app`` filtered to app vs appcategory; renamed for Central."""
    if not isinstance(value, list):
        return None
    out: list[dict[str, str]] = []
    for e in value:
        if not isinstance(e, dict) or e.get("app_type") != app_type:
            continue
        name, direction = e.get("name"), e.get("dir")
        appname = e.get("appname")
        if not (appname and name and direction):
            continue
        if app_type == "app":
            out.append({"appname": str(appname), "bwc-name": str(name), "direction": _norm_dir(direction)})
        else:
            out.append(
                {"category-name": str(appname).upper(), "bwc-name": str(name), "direction": _norm_dir(direction)}
            )
    return out or None


def _bwc_web(value: Any, web_opt: str) -> list[dict[str, str]] | None:
    """``role__bwc_web`` filtered to category vs reputation; renamed + normalised."""
    if not isinstance(value, list):
        return None
    out: list[dict[str, str]] = []
    for e in value:
        if not isinstance(e, dict) or e.get("web_opt") != web_opt:
            continue
        name, direction = e.get("name"), e.get("dir")
        if web_opt == "web-cc-category":
            cat = e.get("webcccatgname")
            if cat and name and direction:
                out.append(
                    {
                        "webcategory-name": str(cat).replace("/", "-").upper(),
                        "bwc-name": str(name),
                        "direction": _norm_dir(direction),
                    }
                )
        else:
            rep = e.get("web_rep")
            if rep and name and direction:
                out.append(
                    {
                        "webrepname": str(rep).replace("-", "_").upper(),
                        "bwc-name": str(name),
                        "direction": _norm_dir(direction),
                    }
                )
    return out or None


def _bwc_exclude(value: Any, app_type: str) -> list[dict[str, str]] | None:
    """``role__bwc_ex`` filtered to app vs appcategory; renamed for Central."""
    if not isinstance(value, list):
        return None
    out: list[dict[str, str]] = []
    for e in value:
        if not isinstance(e, dict) or e.get("app_type") != app_type:
            continue
        appname = e.get("appname")
        if not appname:
            continue
        if app_type == "app":
            out.append({"exclude-app-name": str(appname)})
        else:
            out.append({"exclude-app-category-name": str(appname).upper()})
    return out or None


def aos8_read_role(role: dict[str, Any]) -> CanonicalRole:
    """Build a ``CanonicalRole`` from one AOS 8 ``role`` record (Gateway-targeted)."""
    vlanstr = _path(role, "role__vlan", "vlanstr")
    max_sess = _path(role, "role__max_sess", "max_sess")
    reauth = role.get("role__reauth")

    return CanonicalRole(
        name=str(role.get("rname") or ""),
        access_vlan_id=_vlanstr_id(vlanstr),
        access_vlan_name=_vlanstr_name(vlanstr),
        vlan_type=_vlanstr_type(vlanstr),
        captive_portal=(lambda v: str(v) if v is not None else None)(_path(role, "role__cp", "cp_profile_name")),
        check_for_accounting=_present(role, "role__cp_acc"),
        max_sessions=int(max_sess) if max_sess is not None else None,
        reauth_interval=_reauth_minutes(reauth),
        reauth_interval_seconds=_reauth_seconds(reauth),
        enforce_dhcp=_present(role, "role__enforce_dhcp"),
        robust_age_out=_present(role, "role__robust_age_out"),
        registration_role=_present(role, "role__reg_role"),
        openflow_enable=_present(role, "role__openflow"),
        ip_classification=_present(role, "role_disable_ipclassify"),
        dpi_classification=_present(role, "role__dpi_disable"),
        dpi_youtube_education=_present(role, "role_enable_youtubeedu"),
        web_cc=_present(role, "role__disable_webcc"),
        bwc_basic=_bwc_basic(role.get("role__bwc")),
        bwc_app=_bwc_app(role.get("role__bwc_app"), "app"),
        bwc_appcategory=_bwc_app(role.get("role__bwc_app"), "appcategory"),
        bwc_web_category=_bwc_web(role.get("role__bwc_web"), "web-cc-category"),
        bwc_web_reputation=_bwc_web(role.get("role__bwc_web"), "web-cc-reputation"),
        bwc_exclude_app=_bwc_exclude(role.get("role__bwc_ex"), "app"),
        bwc_exclude_appcategory=_bwc_exclude(role.get("role__bwc_ex"), "appcategory"),
    )
