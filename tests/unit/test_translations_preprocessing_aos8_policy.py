"""Unit tests for ``translations/preprocessing/aos8_policy.py``.

Regression coverage for the WebCC-category rule bug: AOS 8 REST emits
``app_web_type == "web_cat"`` for ``web-cc-category`` session-ACL rules
(live-verified on an 8.13 Mobility Conductor — ``/md/Campus``
``block-high-risk_web``). The preprocessing only recognised the
``"web_cc_cat"`` spelling, so real category rules fell through
``_build_services_block`` (returning ``None``) and ``_determine_rule_type``
classified them as ``RULE_ANY`` — silently turning a category-specific deny
into a deny-everything rule. These tests pin both spellings.

Engine-level integration lives in ``test_translations_engine.py``.
"""

from __future__ import annotations

import pytest

from hpe_networking_mcp.translations.preprocessing.aos8_policy import (
    _build_services_block,
    _determine_rule_type,
    preprocess_acl_for_policy,
)

pytestmark = pytest.mark.unit


def _web_cat_rule(catg: str = "malware-sites") -> dict:
    """A real-shape WebCC-category session-ACL rule as AOS 8 REST returns it."""
    return {
        "suser": True,
        "src": "suser",
        "dst": "dany",
        "webcccatgname": catg,
        "app_web_type": "web_cat",  # the spelling the live API actually emits
        "service_app": "app_opt",
        "appdeny": True,
        "appaction": "appdeny_opt",
    }


def test_web_cat_builds_web_category_services() -> None:
    """``web_cat`` (real API spelling) must produce a web-category services block."""
    out = _build_services_block(_web_cat_rule("malware-sites"))
    assert out == {"services": {"web-category": "MALWARE-SITES"}}


def test_web_cat_enum_table_mapping() -> None:
    """Category names route through the enum table, not the naive fallback."""
    out = _build_services_block(_web_cat_rule("keyloggers/monitoring"))
    assert out == {"services": {"web-category": "KEYLOGGERS-AND-MONITORING"}}


def test_web_cc_cat_legacy_spelling_still_handled() -> None:
    """The older ``web_cc_cat`` spelling must keep working (backward compatible)."""
    rule = _web_cat_rule()
    rule["app_web_type"] = "web_cc_cat"
    out = _build_services_block(rule)
    assert out == {"services": {"web-category": "MALWARE-SITES"}}


def test_web_cat_rule_type_is_web_category_not_any() -> None:
    """Regression: the category rule must classify as RULE_WEB_CATEGORY, not RULE_ANY."""
    rule = _web_cat_rule()
    services = _build_services_block(rule)
    assert services is not None  # the bug returned None here
    rule_type = _determine_rule_type(rule, services, None)
    assert rule_type == "RULE_WEB_CATEGORY"
    assert rule_type != "RULE_ANY"


def test_web_reputation_unaffected() -> None:
    """The reputation path (already correct) must remain intact."""
    rule = {
        "src": "sany",
        "dst": "dany",
        "web_rep2": "high-risk2",
        "app_web_type": "web_cc_rep",
        "service_app": "app_opt",
        "appdeny": True,
        "appaction": "appdeny_opt",
    }
    out = _build_services_block(rule)
    assert out == {"services": {"web-reputation": "HIGH_RISK"}}


# --------------------------------------------------------------------------- #
# Inherited-rule regression: a real AOS 8 effective-config ACL inherited to a
# descendant scope carries _flags.inherited on EVERY rule. The preprocessing
# used to skip inherited rules, which emptied policy-rule[] for any ACL
# previewed below its definition scope (the normal migration case). Fixed to
# skip only genuinely `system` rules. Mirrors the server_group member-inherited
# fix. Real captured shape from /md/Campus/East `deny-all` / `camera_policy`.
# --------------------------------------------------------------------------- #


def _inherited_acl() -> dict:
    """A real-shape acl_sess record as effective-config returns it at a child
    scope: the record AND every rule carry ``_flags.inherited``."""
    return {
        "accname": "deny-all",
        "_flags": {"inherited": True},
        "acl_sess__v4policy": [
            {
                "sany": True,
                "src": "sany",
                "dany": True,
                "dst": "dany",
                "service-any": True,
                "svc": "service-any",
                "service_app": "service",
                "deny": True,
                "action": "deny_opt",
                "_flags": {"inherited": True},
            }
        ],
    }


def test_inherited_rules_are_translated_not_dropped() -> None:
    """Regression: inherited rules must translate — the bug produced []."""
    out = preprocess_acl_for_policy(_inherited_acl(), {"role_records": []})
    assert len(out["_central_rules"]) >= 1, "inherited rules were dropped"
    assert out["_central_rules"][0]["action"]["type"] == "ACTION_DENY"


def test_system_rules_still_skipped() -> None:
    """A genuinely system-flagged rule is still skipped (built-in, not operator)."""
    acl = _inherited_acl()
    acl["acl_sess__v4policy"][0]["_flags"] = {"inherited": True, "system": True}
    out = preprocess_acl_for_policy(acl, {"role_records": []})
    assert out["_central_rules"] == []
