"""Unit tests for the ClearPass policy-visualizer model + flow compiler.

Builds a minimal ``raw`` dict directly (bypassing the adapter), runs
:func:`build` then :func:`compile_service`, and verifies the resulting
FlowGraph shape for the cases that exercise the interesting semantics:
first-applicable termination, evaluate-all chaining, implicit deny,
missing enforcement policy, RADIUS_PROXY skip-auth, and warnings for
unresolved references.
"""

from __future__ import annotations

import pytest

from hpe_networking_mcp.platforms.clearpass.policy_visualizer.flow_graph import (
    compile_service,
)
from hpe_networking_mcp.platforms.clearpass.policy_visualizer.policy_details import build_details
from hpe_networking_mcp.platforms.clearpass.policy_visualizer.policy_model import build

pytestmark = pytest.mark.unit


def _single_predicate(value: str = "x") -> dict:
    return {
        "operator": "and",
        "displayOperator": "MATCHES_ALL",
        "attributes": [{"type": "Tips", "name": "Role", "operator": "EQUALS", "value": value}],
    }


def _minimal_raw(
    *,
    rm_rules: list[dict] | None = None,
    rm_default: str = "",
    rm_combine: str = "first-applicable",
    enf_rules: list[dict] | None = None,
    enf_default: str = "",
    enf_combine: str = "first-applicable",
    service_type: str = "RADIUS",
) -> dict:
    """Construct a small raw dict suitable for build()."""
    return {
        "roles": [
            {"name": "[Employee]", "description": ""},
            {"name": "[Contractor]", "description": ""},
        ],
        "authMethods": [],
        "authSources": [],
        "radiusEnfProfiles": [
            {"name": "[Allow Access Profile]", "action": "Accept", "description": ""},
            {"name": "[Deny Access Profile]", "action": "Reject", "description": ""},
        ],
        "tacacsEnfProfiles": [],
        "radiusCoaEnfProfiles": [],
        "postAuthEnfProfiles": [],
        "genericEnfProfiles": [],
        "roleMappings": [
            {
                "name": "RM-Test",
                "ruleCombineAlgo": rm_combine,
                "defaultRole": rm_default,
                "rules": rm_rules or [],
            }
        ],
        "enforcementPolicies": [
            {
                "name": "EP-Test",
                "policyType": "RADIUS",
                "ruleCombineAlgo": enf_combine,
                "defaultProfile": enf_default,
                "rules": enf_rules or [],
            }
        ],
        "services": [
            {
                "name": "SVC-Test",
                "description": "",
                "serviceType": service_type,
                "matchExpression": _single_predicate("AirGroup"),
                "authMethods": [],
                "authSources": [],
                "roleMappings": ["RM-Test"],
                "enfPolicies": ["EP-Test"],
            }
        ],
    }


# ---------------------------------------------------------------------------
# build() — model construction + cross-references
# ---------------------------------------------------------------------------


class TestBuild:
    def test_minimal_build_populates_all_collections(self):
        model = build(_minimal_raw())
        assert len(model.roles) == 2
        assert len(model.enforcement_profiles) == 2
        assert len(model.role_mapping_policies) == 1
        assert len(model.enforcement_policies) == 1
        assert len(model.services) == 1
        svc = next(iter(model.services.values()))
        assert svc.name == "SVC-Test"
        assert svc.role_mapping_policy_name == "RM-Test"
        assert svc.enforcement_policy_name == "EP-Test"

    def test_unresolved_profile_creates_placeholder_and_warning(self):
        raw = _minimal_raw(
            enf_rules=[
                {
                    "index": 0,
                    "expression": _single_predicate(),
                    "results": [{"name": "Enforcement-Profile", "displayValue": "[Missing Profile]"}],
                }
            ],
        )
        model = build(raw)
        assert any("Missing Profile" in w for w in model.warnings)
        # Placeholder profile gets added so cross-refs still resolve
        assert any(p.name == "[Missing Profile]" for p in model.enforcement_profiles.values())

    def test_unresolved_role_creates_placeholder_and_warning(self):
        raw = _minimal_raw(
            rm_rules=[
                {
                    "index": 0,
                    "expression": _single_predicate(),
                    "results": [{"name": "Role", "displayValue": "[Phantom Role]"}],
                }
            ],
        )
        model = build(raw)
        assert any("Phantom Role" in w for w in model.warnings)


# ---------------------------------------------------------------------------
# compile_service() — flow graph shapes for each semantic case
# ---------------------------------------------------------------------------


class TestCompileServiceFirstApplicable:
    def test_two_rules_first_applicable_terminates_on_yes(self):
        rm_rules = [
            {
                "index": 0,
                "expression": _single_predicate("v1"),
                "results": [{"name": "Role", "displayValue": "[Contractor]"}],
            },
        ]
        enf_rules = [
            {
                "index": 0,
                "expression": _single_predicate("X"),
                "results": [{"name": "Enforcement-Profile", "displayValue": "[Allow Access Profile]"}],
            },
            {
                "index": 1,
                "expression": _single_predicate("Y"),
                "results": [{"name": "Enforcement-Profile", "displayValue": "[Deny Access Profile]"}],
            },
        ]
        model = build(_minimal_raw(rm_rules=rm_rules, enf_rules=enf_rules))
        flow = compile_service(next(iter(model.services.values())), model)
        end_nodes = [n for n in flow.nodes if n.type == "end"]
        # Expected ends (no rm_default, no enf_default — both produce extra
        # implicit-deny terminations):
        #   no_match + auth_fail + 2 enf rule ends + enf_implicit_deny + no_role
        assert len(end_nodes) == 6
        allow_ends = [n for n in end_nodes if "ALLOW" in n.label]
        deny_ends = [n for n in end_nodes if "DENY" in n.label]
        assert len(allow_ends) >= 1
        assert len(deny_ends) >= 1


class TestCompileServiceEvaluateAll:
    def test_evaluate_all_chains_continue_edges(self):
        enf_rules = [
            {
                "index": 0,
                "expression": _single_predicate("X"),
                "results": [{"name": "Enforcement-Profile", "displayValue": "[Allow Access Profile]"}],
            },
            {
                "index": 1,
                "expression": _single_predicate("Y"),
                "results": [{"name": "Enforcement-Profile", "displayValue": "[Allow Access Profile]"}],
            },
        ]
        model = build(_minimal_raw(enf_rules=enf_rules, enf_combine="evaluate-all"))
        flow = compile_service(next(iter(model.services.values())), model)
        continue_edges = [e for e in flow.edges if e.label == "CONTINUE"]
        # evaluate-all with 2 rules → 1 CONTINUE edge (action_0 → rule_1)
        assert len(continue_edges) == 1


class TestCompileServiceImplicitDeny:
    def test_implicit_deny_when_no_default(self):
        enf_rules = [
            {
                "index": 0,
                "expression": _single_predicate("X"),
                "results": [{"name": "Enforcement-Profile", "displayValue": "[Allow Access Profile]"}],
            }
        ]
        # No enf_default + no rm_default
        model = build(_minimal_raw(enf_rules=enf_rules))
        flow = compile_service(next(iter(model.services.values())), model)
        labels = [n.label for n in flow.nodes if n.type == "end"]
        assert any("implicit" in label.lower() for label in labels)


class TestCompileServiceNoEnforcementPolicy:
    def test_missing_enforcement_policy_yields_no_policy_deny(self):
        raw = _minimal_raw()
        # Strip out the enforcement policy entirely
        raw["enforcementPolicies"] = []
        raw["services"][0]["enfPolicies"] = []
        model = build(raw)
        flow = compile_service(next(iter(model.services.values())), model)
        labels = [n.label for n in flow.nodes if n.type == "end"]
        assert any("no enforcement policy" in label.lower() for label in labels)


class TestCompileServiceRadiusProxy:
    def test_radius_proxy_skips_auth_and_role_mapping(self):
        enf_rules = [
            {
                "index": 0,
                "expression": _single_predicate("X"),
                "results": [{"name": "Enforcement-Profile", "displayValue": "[Allow Access Profile]"}],
            }
        ]
        model = build(_minimal_raw(service_type="RADIUS_PROXY", enf_rules=enf_rules))
        flow = compile_service(next(iter(model.services.values())), model)
        node_ids = {n.id for n in flow.nodes}
        # No auth or rm nodes for RADIUS_PROXY
        assert not any("__auth" in nid for nid in node_ids)
        assert not any("__rm_" in nid for nid in node_ids)


# ---------------------------------------------------------------------------
# build_details() — inspector serializer
# ---------------------------------------------------------------------------


class TestBuildDetails:
    def test_details_contains_service_context_and_rules(self):
        rm_rules = [
            {
                "index": 0,
                "expression": _single_predicate("v1"),
                "results": [{"name": "Role", "displayValue": "[Contractor]"}],
            }
        ]
        enf_rules = [
            {
                "index": 0,
                "expression": _single_predicate("X"),
                "results": [{"name": "Enforcement-Profile", "displayValue": "[Allow Access Profile]"}],
            }
        ]
        model = build(_minimal_raw(rm_rules=rm_rules, enf_rules=enf_rules))
        svc = next(iter(model.services.values()))
        details = build_details(svc, model)
        assert details["service_context"]["service_name"] == "SVC-Test"
        assert len(details["role_mapping_rules"]) == 1
        assert len(details["enforcement_rules"]) == 1
        assert details["role_mapping_rules"][0]["action_text"].startswith("Set Role:")
        assert "[Allow Access Profile]" in details["enforcement_rules"][0]["action_text"]
        # Service-match key is always synthesized into rule_index
        assert any(k.endswith("__match") for k in details["rule_index"])
