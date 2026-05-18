"""Unit tests for the ClearPass policy-visualizer what-if simulator.

The simulator's correctness contract is UNCERTAINTY-FIRST: any predicate
whose attribute isn't provided in the context must evaluate to ``None``,
and ``None`` must propagate through ``And`` / ``Or`` / ``Not`` correctly.
The end-to-end ``SimulationOutcome`` must surface ``status="uncertain"``
and the missing attribute paths rather than producing a confident wrong
answer.

The operator was previously burned by a fake-simulator that confidently
reported wrong outcomes; these tests guard against any regression.
"""

from __future__ import annotations

import pytest

from hpe_networking_mcp.platforms.clearpass.policy_visualizer.conditions import (
    And,
    Not,
    Op,
    Or,
    Predicate,
    evaluate,
)
from hpe_networking_mcp.platforms.clearpass.policy_visualizer.flow_graph import compile_service
from hpe_networking_mcp.platforms.clearpass.policy_visualizer.policy_model import build

pytestmark = pytest.mark.unit


# ---------------------------------------------------------------------------
# evaluate() — per-Op coverage
# ---------------------------------------------------------------------------


def _p(ns: str, attr: str, op: Op, value: str, display: str = "") -> Predicate:
    return Predicate(namespace=ns, attribute=attr, op=op, rhs_raw=value, rhs_display=display)


class TestEvaluateBasicOps:
    def test_equals_true(self):
        assert evaluate(_p("Tips", "Role", Op.equals, "IoT Device"), {"Tips:Role": "IoT Device"}) is True

    def test_equals_false(self):
        assert evaluate(_p("Tips", "Role", Op.equals, "IoT Device"), {"Tips:Role": "Kid"}) is False

    def test_not_equals(self):
        assert evaluate(_p("Tips", "Role", Op.not_equals, "Kid"), {"Tips:Role": "IoT Device"}) is True
        assert evaluate(_p("Tips", "Role", Op.not_equals, "Kid"), {"Tips:Role": "Kid"}) is False

    def test_contains(self):
        assert evaluate(_p("X", "Name", Op.contains, "vis"), {"X:Name": "visitor-1"}) is True
        assert evaluate(_p("X", "Name", Op.contains, "vis"), {"X:Name": "other"}) is False

    def test_starts_with(self):
        assert evaluate(_p("X", "n", Op.starts_with, "Inspire"), {"X:n": "Inspire 3D"}) is True
        assert evaluate(_p("X", "n", Op.starts_with, "Inspire"), {"X:n": "3D Inspire"}) is False

    def test_regex(self):
        assert (
            evaluate(
                _p("X", "host", Op.regex, r"(hayley|rylee)-atv"),
                {"X:host": "hayley-atv"},
            )
            is True
        )
        assert (
            evaluate(
                _p("X", "host", Op.regex, r"(hayley|rylee)-atv"),
                {"X:host": "guest-laptop"},
            )
            is False
        )

    def test_in_(self):
        assert evaluate(_p("X", "v", Op.in_, "a,b,c"), {"X:v": "b"}) is True
        assert evaluate(_p("X", "v", Op.in_, "a,b,c"), {"X:v": "d"}) is False

    def test_exists_with_value_present(self):
        assert evaluate(_p("X", "v", Op.exists, ""), {"X:v": "anything"}) is True

    def test_exists_with_value_absent(self):
        assert evaluate(_p("X", "v", Op.exists, ""), {}) is False

    def test_not_exists(self):
        assert evaluate(_p("X", "v", Op.not_exists, ""), {}) is True
        assert evaluate(_p("X", "v", Op.not_exists, ""), {"X:v": "x"}) is False

    def test_numeric_comparison(self):
        assert evaluate(_p("X", "n", Op.less_than, "10"), {"X:n": "5"}) is True
        assert evaluate(_p("X", "n", Op.greater_than_or_equals, "10"), {"X:n": "10"}) is True
        assert evaluate(_p("X", "n", Op.greater_than, "10"), {"X:n": "10"}) is False


class TestEvaluateUnknown:
    """The critical uncertainty contract — missing attributes return None, never False."""

    def test_missing_attribute_returns_none_not_false(self):
        # This is the load-bearing case: operator didn't provide GuestUser:visitor
        # but a rule's condition references it. Result must be uncertain, never
        # a confident False that would mask a possible match.
        result = evaluate(_p("GuestUser", "visitor", Op.equals, "Inspire 3D"), {})
        assert result is None, "Missing attribute MUST return None (uncertain), never False"

    def test_missing_attribute_with_negative_op_still_returns_none(self):
        result = evaluate(_p("GuestUser", "visitor", Op.not_equals, "Inspire 3D"), {})
        assert result is None

    def test_present_attribute_returns_boolean(self):
        assert evaluate(_p("X", "v", Op.equals, "a"), {"X:v": "a"}) is True
        assert evaluate(_p("X", "v", Op.equals, "a"), {"X:v": "b"}) is False


class TestEvaluateBooleanPropagation:
    """And/Or/Not three-valued logic."""

    def test_and_with_one_unknown_returns_none(self):
        # True AND None → None  (we can't claim the AND is True because we don't know the second)
        expr = And(
            operands=[
                _p("X", "a", Op.equals, "1"),
                _p("Y", "b", Op.equals, "2"),
            ]
        )
        assert evaluate(expr, {"X:a": "1"}) is None  # Y:b unknown

    def test_and_with_one_false_returns_false_even_if_other_unknown(self):
        # False AND None → False (short-circuit — AND is contradicted regardless of unknown)
        expr = And(
            operands=[
                _p("X", "a", Op.equals, "1"),
                _p("Y", "b", Op.equals, "2"),
            ]
        )
        assert evaluate(expr, {"X:a": "WRONG"}) is False  # X:a contradicts, Y:b unknown

    def test_or_with_one_true_returns_true_even_if_other_unknown(self):
        # True OR None → True (short-circuit — OR is satisfied)
        expr = Or(
            operands=[
                _p("X", "a", Op.equals, "1"),
                _p("Y", "b", Op.equals, "2"),
            ]
        )
        assert evaluate(expr, {"X:a": "1"}) is True

    def test_or_with_one_false_and_one_unknown_returns_none(self):
        # False OR None → None (we can't conclude OR is False without knowing the second)
        expr = Or(
            operands=[
                _p("X", "a", Op.equals, "1"),
                _p("Y", "b", Op.equals, "2"),
            ]
        )
        assert evaluate(expr, {"X:a": "WRONG"}) is None

    def test_not_propagates_none(self):
        expr = Not(operand=_p("X", "a", Op.equals, "1"))
        assert evaluate(expr, {}) is None
        assert evaluate(expr, {"X:a": "1"}) is False
        assert evaluate(expr, {"X:a": "2"}) is True


class TestEvaluateMultiValued:
    """Tips:Role and similar multi-valued attributes — list context, any-match for positive ops."""

    def test_role_list_any_match_for_equals(self):
        # Device has multiple roles assigned (evaluate-all RM); rule checks for one
        result = evaluate(
            _p("Tips", "Role", Op.equals, "Night Night"),
            {"Tips:Role": ["Kid", "Night Night"]},
        )
        assert result is True

    def test_role_list_no_match_returns_false(self):
        result = evaluate(
            _p("Tips", "Role", Op.equals, "IoT Device"),
            {"Tips:Role": ["Kid", "Night Night"]},
        )
        assert result is False

    def test_role_list_in_operator(self):
        # Tips:Role MATCHES_ANY ['Kid', 'Apple TV'] → True if any device role is in the set
        result = evaluate(
            _p("Tips", "Role", Op.in_, "Kid,Apple TV"),
            {"Tips:Role": ["Kid"]},
        )
        assert result is True

    def test_role_list_negative_op_requires_all_to_satisfy(self):
        # NOT_EQUALS with a role list: True only if NONE of the roles equals the rhs
        result = evaluate(
            _p("Tips", "Role", Op.not_equals, "Banned"),
            {"Tips:Role": ["Kid", "Night Night"]},
        )
        assert result is True

        result = evaluate(
            _p("Tips", "Role", Op.not_equals, "Kid"),
            {"Tips:Role": ["Kid", "Night Night"]},
        )
        assert result is False  # one of the roles matches "Kid" so NOT_EQUALS fails


# ---------------------------------------------------------------------------
# End-to-end: compile_service with simulated_attributes
# ---------------------------------------------------------------------------


def _single_predicate_expr(ns: str, attr: str, value: str) -> dict:
    return {
        "operator": "and",
        "attributes": [{"type": ns, "name": attr, "operator": "EQUALS", "value": value}],
    }


def _build_simulation_test_raw() -> dict:
    """A minimal but realistic policy: 2 RM rules (assign Kid or IoT) + 3 EP rules
    (one for Kid, one for IoT, one default-ish). Used to verify end-to-end
    simulation correctness against known contexts.
    """
    return {
        "roles": [{"name": "Kid", "description": ""}, {"name": "IoT Device", "description": ""}],
        "authMethods": [],
        "authSources": [],
        "radiusEnfProfiles": [
            {"name": "[Allow Access Profile]", "action": "Accept", "description": ""},
            {"name": "WLAN-KID", "action": "Accept", "description": ""},
            {"name": "WLAN-IoT", "action": "Accept", "description": ""},
            {"name": "VLAN-USER", "action": "Accept", "description": ""},
        ],
        "tacacsEnfProfiles": [],
        "radiusCoaEnfProfiles": [],
        "postAuthEnfProfiles": [],
        "genericEnfProfiles": [],
        "roleMappings": [
            {
                "name": "RM",
                "ruleCombineAlgo": "first-applicable",
                "defaultRole": "",
                "rules": [
                    {
                        "index": 0,
                        "expression": _single_predicate_expr("GuestUser", "Role ID", "11"),
                        "results": [{"name": "Role", "displayValue": "Kid"}],
                    },
                    {
                        "index": 1,
                        "expression": _single_predicate_expr("GuestUser", "Role ID", "26"),
                        "results": [{"name": "Role", "displayValue": "IoT Device"}],
                    },
                ],
            }
        ],
        "enforcementPolicies": [
            {
                "name": "EP",
                "policyType": "RADIUS",
                "ruleCombineAlgo": "first-applicable",
                "defaultProfile": "[Allow Access Profile]",
                "rules": [
                    {
                        "index": 0,
                        "expression": _single_predicate_expr("Tips", "Role", "Kid"),
                        "results": [{"name": "Enforcement-Profile", "displayValue": "WLAN-KID, VLAN-USER"}],
                    },
                    {
                        "index": 1,
                        "expression": _single_predicate_expr("Tips", "Role", "IoT Device"),
                        "results": [{"name": "Enforcement-Profile", "displayValue": "WLAN-IoT, VLAN-USER"}],
                    },
                ],
            }
        ],
        "services": [
            {
                "name": "Test-Service",
                "description": "",
                "serviceType": "RADIUS",
                "matchExpression": _single_predicate_expr("Connection", "SSID", "TestSSID"),
                "authMethods": [],
                "authSources": [],
                "roleMappings": ["RM"],
                "enfPolicies": ["EP"],
            }
        ],
    }


class TestSimulationEndToEnd:
    def test_resolved_outcome_when_full_context_provided(self):
        model = build(_build_simulation_test_raw())
        svc = next(iter(model.services.values()))
        context = {
            "Connection:SSID": "TestSSID",
            "GuestUser:Role ID": "11",  # → Kid
        }
        flow = compile_service(svc, model, simulated_attributes=context)
        assert flow.simulation is not None
        assert flow.simulation.status == "resolved"
        assert flow.simulation.resulting_roles == ["Kid"]
        assert flow.simulation.access_decision == "ALLOW"
        assert "WLAN-KID" in flow.simulation.applied_profiles
        assert "VLAN-USER" in flow.simulation.applied_profiles
        # Did NOT apply the IoT profile or the default
        assert "WLAN-IoT" not in flow.simulation.applied_profiles

    def test_uncertain_outcome_when_role_id_missing(self):
        """The case the operator was burned by: partial context → simulator must
        return uncertain, NOT a confident wrong answer."""
        model = build(_build_simulation_test_raw())
        svc = next(iter(model.services.values()))
        context = {"Connection:SSID": "TestSSID"}  # GuestUser:Role ID intentionally missing
        flow = compile_service(svc, model, simulated_attributes=context)
        assert flow.simulation is not None
        assert flow.simulation.status == "uncertain"
        assert flow.simulation.access_decision == "UNKNOWN"
        assert "GuestUser:Role ID" in flow.simulation.unknown_attributes
        # MUST NOT have invented a matching rule or profile
        assert flow.simulation.matching_enforcement_rule is None
        assert flow.simulation.applied_profiles == []
        # MUST surface the unknown in notes
        assert any("GuestUser:Role ID" in n for n in flow.simulation.notes)

    def test_no_match_when_service_match_false(self):
        model = build(_build_simulation_test_raw())
        svc = next(iter(model.services.values()))
        # Service match condition is SSID=TestSSID; simulate a different SSID
        context = {"Connection:SSID": "OtherSSID"}
        flow = compile_service(svc, model, simulated_attributes=context)
        assert flow.simulation is not None
        assert flow.simulation.status == "no_match"
        # No rule-mapping or enforcement rules should have been consulted
        assert flow.simulation.matching_role_mapping_rules == []
        assert flow.simulation.matching_enforcement_rule is None

    def test_decision_node_simulation_match_populated(self):
        model = build(_build_simulation_test_raw())
        svc = next(iter(model.services.values()))
        context = {
            "Connection:SSID": "TestSSID",
            "GuestUser:Role ID": "11",
        }
        flow = compile_service(svc, model, simulated_attributes=context)
        # The matched RM rule node has simulation_match=True
        rm_rule_0 = next(n for n in flow.nodes if n.id.endswith("__rm_rule_0"))
        assert rm_rule_0.simulation_match is True
        # RM is first-applicable; rule 0 matched, so rule 1 was never
        # consulted. Its simulation_match stays None (not False) — that
        # correctly conveys "we didn't need to look at this rule" vs.
        # "this rule's condition is contradicted".
        rm_rule_1 = next(n for n in flow.nodes if n.id.endswith("__rm_rule_1"))
        assert rm_rule_1.simulation_match is None
        # The first EP rule (Tips:Role = Kid) is True because the resolved
        # Kid role got merged into the EP context
        enf_rule_0 = next(n for n in flow.nodes if n.id.endswith("__enf_rule_0"))
        assert enf_rule_0.simulation_match is True
        # EP is also first-applicable; rule 0 matched so rule 1 wasn't consulted
        enf_rule_1 = next(n for n in flow.nodes if n.id.endswith("__enf_rule_1"))
        assert enf_rule_1.simulation_match is None

    def test_no_simulation_when_no_context_provided(self):
        model = build(_build_simulation_test_raw())
        svc = next(iter(model.services.values()))
        flow = compile_service(svc, model)  # no simulated_attributes
        assert flow.simulation is None
        # And no node should have simulation_match set
        for node in flow.nodes:
            assert node.simulation_match is None
