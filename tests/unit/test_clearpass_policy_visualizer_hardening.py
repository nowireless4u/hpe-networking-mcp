"""Tests for the ClearPass policy-visualizer hardening batch (data-model fixes).

Covers the localized model/classification/adapter findings from Casey Jones's
full-project review: #596 (action-less side-effect profiles), #599 (per-rule
evaluate-all flow), #600 (unknown-operator containment), #601 (comma-safe
profile names).
"""

from __future__ import annotations

import pytest

from hpe_networking_mcp.platforms.clearpass.policy_visualizer.conditions import Op, evaluate, normalize
from hpe_networking_mcp.platforms.clearpass.policy_visualizer.flow_graph import _is_deny
from hpe_networking_mcp.platforms.clearpass.policy_visualizer.policy_model import build

pytestmark = pytest.mark.unit


def _raw(*, generic=None, tacacs=None, radius=None, rms=None, eps=None) -> dict:
    return {
        "roles": [{"name": "[Employee]", "description": ""}],
        "authMethods": [],
        "authSources": [],
        "radiusEnfProfiles": radius or [],
        "tacacsEnfProfiles": tacacs or [],
        "radiusCoaEnfProfiles": [],
        "postAuthEnfProfiles": [],
        "genericEnfProfiles": generic or [],
        "roleMappings": rms or [],
        "enforcementPolicies": eps or [],
        "services": [],
    }


def _profile_by_name(model, name):
    return next(p for p in model.enforcement_profiles.values() if p.name == name)


# ---------------------------------------------------------------------------
# #596 — action-less side-effect profiles are not deny
# ---------------------------------------------------------------------------


class TestSideEffectNotDeny:
    def test_actionless_generic_is_neutral_not_deny(self) -> None:
        model = build(_raw(generic=[{"name": "Log Session", "action": "", "description": ""}]))
        p = _profile_by_name(model, "Log Session")
        assert p.profile_type == "generic_sideeffect"
        assert not _is_deny([p.id], [p.name], model.enforcement_profiles)

    def test_actionless_tacacs_is_neutral_not_deny(self) -> None:
        model = build(_raw(tacacs=[{"name": "Shell Profile", "action": "", "description": ""}]))
        p = _profile_by_name(model, "Shell Profile")
        assert p.profile_type == "tacacs_sideeffect"
        assert not _is_deny([p.id], [p.name], model.enforcement_profiles)

    def test_explicit_reject_generic_still_deny(self) -> None:
        model = build(_raw(generic=[{"name": "Block", "action": "Reject", "description": ""}]))
        p = _profile_by_name(model, "Block")
        assert p.profile_type == "generic_reject"
        assert _is_deny([p.id], [p.name], model.enforcement_profiles)

    def test_accept_generic_is_allow(self) -> None:
        model = build(_raw(generic=[{"name": "Grant", "action": "Accept", "description": ""}]))
        p = _profile_by_name(model, "Grant")
        assert p.profile_type == "generic_accept"
        assert not _is_deny([p.id], [p.name], model.enforcement_profiles)


# ---------------------------------------------------------------------------
# #599 — per-rule flow reflects evaluate-all
# ---------------------------------------------------------------------------


def _enf_policy(name, algo, rules):
    return {"name": name, "policyType": "RADIUS", "ruleCombineAlgo": algo, "defaultProfile": "", "rules": rules}


def _rm_policy(name, algo, rules):
    return {"name": name, "ruleCombineAlgo": algo, "defaultRole": "", "rules": rules}


_ENF_RULE = {
    "index": 0,
    "expression": {
        "operator": "and",
        "attributes": [{"type": "Tips", "name": "Role", "operator": "EQUALS", "value": "x"}],
    },
    "results": [{"name": "Enforcement-Profile", "values": ["Grant"]}],
}
_RM_RULE = {
    "index": 0,
    "expression": {
        "operator": "and",
        "attributes": [{"type": "Tips", "name": "Role", "operator": "EQUALS", "value": "x"}],
    },
    "results": [{"name": "Role", "displayValue": "[Employee]"}],
}


class TestEvaluateAllFlow:
    def test_enforcement_evaluate_all_rule_is_continue(self) -> None:
        model = build(
            _raw(generic=[{"name": "Grant", "action": "Accept"}], eps=[_enf_policy("EP", "evaluate-all", [_ENF_RULE])])
        )
        ep = next(iter(model.enforcement_policies.values()))
        assert ep.rules[0].flow.on_match == "continue"

    def test_enforcement_first_applicable_rule_is_stop(self) -> None:
        model = build(
            _raw(
                generic=[{"name": "Grant", "action": "Accept"}],
                eps=[_enf_policy("EP", "first-applicable", [_ENF_RULE])],
            )
        )
        ep = next(iter(model.enforcement_policies.values()))
        assert ep.rules[0].flow.on_match == "stop"

    def test_role_mapping_evaluate_all_rule_is_continue(self) -> None:
        model = build(_raw(rms=[_rm_policy("RM", "evaluate-all", [_RM_RULE])]))
        rm = next(iter(model.role_mapping_policies.values()))
        assert rm.rules[0].flow.on_match == "continue"


# ---------------------------------------------------------------------------
# #600 — unknown operators are contained
# ---------------------------------------------------------------------------


class TestUnknownOperatorContained:
    def test_from_raw_returns_sentinel(self) -> None:
        assert Op.from_raw("SOME_EXOTIC_OP") is Op.unknown

    def test_build_does_not_raise_on_unknown_operator(self) -> None:
        rule = {
            "index": 0,
            "expression": {
                "operator": "and",
                "attributes": [{"type": "Tips", "name": "Role", "operator": "SOME_EXOTIC_OP", "value": "x"}],
            },
            "results": [{"name": "Enforcement-Profile", "values": ["Grant"]}],
        }
        # Must not raise — the exotic operator can't fail the whole compile (#600).
        model = build(
            _raw(generic=[{"name": "Grant", "action": "Accept"}], eps=[_enf_policy("EP", "first-applicable", [rule])])
        )
        assert model.enforcement_policies

    def test_unknown_operator_evaluates_uncertain(self) -> None:
        expr = normalize(
            {"operator": "and", "attributes": [{"type": "Tips", "name": "Role", "operator": "WAT", "value": "x"}]}
        )
        # Even with the attribute present, an unknown operator is uncertain (None).
        assert evaluate(expr, {"Tips:Role": "x"}) is None


# ---------------------------------------------------------------------------
# #601 — comma-containing profile names survive
# ---------------------------------------------------------------------------


class TestCommaSafeProfileNames:
    def test_profile_name_with_comma_not_split(self) -> None:
        rule = {
            "index": 0,
            "expression": {
                "operator": "and",
                "attributes": [{"type": "Tips", "name": "Role", "operator": "EQUALS", "value": "x"}],
            },
            "results": [{"name": "Enforcement-Profile", "values": ["Allow, Log Session"]}],
        }
        model = build(
            _raw(
                generic=[{"name": "Allow, Log Session", "action": "Accept"}],
                eps=[_enf_policy("EP", "first-applicable", [rule])],
            )
        )
        ep = next(iter(model.enforcement_policies.values()))
        then = ep.rules[0].then
        # One profile, name preserved verbatim — not split into two placeholders.
        assert then.profile_names == ["Allow, Log Session"]
        assert len(then.profile_ids) == 1
        assert not model.warnings  # the real profile resolved; no placeholder warning
