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


class TestCompileServiceMacAuthMpskShape:
    """The shape that actually broke in the field — every rule mixes one
    RADIUS Accept profile (the access decision) with multiple
    Post_Authentication side-effect profiles. Pre-fix bug: every rule was
    labeled "Access: DENY" because the post-auth profiles fell into the
    generic bucket and got `generic_reject` via the missing-action default,
    which `_is_deny` then matched. Verifies the access decision now ignores
    post-auth and resolves correctly to ALLOW.
    """

    def _build_mpsk_raw(self) -> dict:
        return {
            "roles": [{"name": "IoT Device", "description": ""}],
            "authMethods": [],
            "authSources": [],
            "radiusEnfProfiles": [
                {"name": "WLAN-IoT-DEVICE", "action": "Accept", "description": ""},
                {"name": "VLAN-IoT", "action": "Accept", "description": ""},
                {"name": "[Registered Device MPSK]", "action": "Accept", "description": ""},
                {"name": "No Wireless For You Default PSK", "action": "Accept", "description": ""},
            ],
            "postAuthEnfProfiles": [
                # These are the profiles that previously broke the classifier.
                # `EnforcementProfile.action` defaults to "" for post-auth (REST
                # returns action=None); the fix ensures we skip them in _is_deny.
                {"name": "Update PDC-FW (Device Name)", "description": ""},
                {"name": "Update EdgeConnect Orchestrator Roles", "description": ""},
                {"name": "SDWAN Role Update IoT Device", "description": ""},
                {"name": "[Update Endpoint Known]", "description": ""},
            ],
            "tacacsEnfProfiles": [],
            "radiusCoaEnfProfiles": [],
            "genericEnfProfiles": [],
            "roleMappings": [],
            "enforcementPolicies": [
                {
                    "name": "MPSK-Enforcement",
                    "policyType": "RADIUS",
                    "ruleCombineAlgo": "first-applicable",
                    "defaultProfile": "No Wireless For You Default PSK",
                    "rules": [
                        {
                            "index": 0,
                            "expression": _single_predicate("IoT Device"),
                            "results": [
                                {
                                    "name": "Enforcement-Profile",
                                    "displayValue": (
                                        "WLAN-IoT-DEVICE, VLAN-IoT, [Registered Device MPSK], "
                                        "Update PDC-FW (Device Name), Update EdgeConnect Orchestrator Roles, "
                                        "SDWAN Role Update IoT Device, [Update Endpoint Known]"
                                    ),
                                }
                            ],
                        }
                    ],
                }
            ],
            "services": [
                {
                    "name": "MPSK-Service",
                    "description": "",
                    "serviceType": "RADIUS_PROXY",  # short-circuit auth + role mapping for the test
                    "matchExpression": _single_predicate("anything"),
                    "authMethods": [],
                    "authSources": [],
                    "roleMappings": [],
                    "enfPolicies": ["MPSK-Enforcement"],
                }
            ],
        }

    def test_rule_mixing_radius_accept_with_post_auth_is_allow_not_deny(self):
        model = build(self._build_mpsk_raw())
        flow = compile_service(next(iter(model.services.values())), model)
        # The single enforcement rule should produce an Access: ALLOW end node,
        # NOT Access: DENY (the prior bug).
        end_labels = [n.label for n in flow.nodes if n.type == "end"]
        rule_ends = [label for label in end_labels if label.startswith("Access:")]
        assert any("ALLOW" in label for label in rule_ends), (
            f"Expected at least one ALLOW end node, got: {rule_ends}. "
            "Mixing RADIUS Accept with Post_Authentication profiles "
            "should resolve to ALLOW — the post-auth profiles are "
            "side-effects, not access decisions."
        )
        assert not any("DENY" in label and "(default)" not in label for label in rule_ends), (
            f"Rule end labels include DENY for an Accept-with-side-effects rule: {rule_ends}"
        )

    def test_default_radius_accept_resolves_to_allow(self):
        model = build(self._build_mpsk_raw())
        flow = compile_service(next(iter(model.services.values())), model)
        default_ends = [n.label for n in flow.nodes if n.type == "end" and "default" in n.label]
        assert any("ALLOW" in label for label in default_ends), (
            f"Default profile is RADIUS Accept — expected ALLOW (default), got: {default_ends}"
        )


class TestIsDenySemantics:
    """Direct tests of _is_deny's revised semantics (post-fix)."""

    def test_explicit_radius_reject_is_deny(self):
        from hpe_networking_mcp.platforms.clearpass.policy_visualizer.flow_graph import _is_deny
        from hpe_networking_mcp.platforms.clearpass.policy_visualizer.policy_model import EnforcementProfile

        profiles = {
            "p1": EnforcementProfile(
                id="p1",
                name="[Deny Access Profile]",
                profile_type="radius_reject",
                action="reject",
            ),
        }
        assert _is_deny(["p1"], ["[Deny Access Profile]"], profiles) is True

    def test_explicit_drop_action_is_deny(self):
        from hpe_networking_mcp.platforms.clearpass.policy_visualizer.flow_graph import _is_deny
        from hpe_networking_mcp.platforms.clearpass.policy_visualizer.policy_model import EnforcementProfile

        profiles = {
            "p1": EnforcementProfile(
                id="p1",
                name="[Drop Access Profile]",
                profile_type="radius_reject",
                action="drop",
            ),
        }
        assert _is_deny(["p1"], ["[Drop Access Profile]"], profiles) is True

    def test_post_auth_alone_is_not_deny(self):
        from hpe_networking_mcp.platforms.clearpass.policy_visualizer.flow_graph import _is_deny
        from hpe_networking_mcp.platforms.clearpass.policy_visualizer.policy_model import EnforcementProfile

        # Post-auth profiles in isolation have no access decision — must not deny
        profiles = {
            "p1": EnforcementProfile(id="p1", name="[Update Endpoint Known]", profile_type="post_auth", action=""),
        }
        assert _is_deny(["p1"], ["[Update Endpoint Known]"], profiles) is False

    def test_radius_accept_plus_post_auth_is_not_deny(self):
        from hpe_networking_mcp.platforms.clearpass.policy_visualizer.flow_graph import _is_deny
        from hpe_networking_mcp.platforms.clearpass.policy_visualizer.policy_model import EnforcementProfile

        profiles = {
            "p1": EnforcementProfile(id="p1", name="WLAN-IoT-DEVICE", profile_type="radius_accept", action="accept"),
            "p2": EnforcementProfile(id="p2", name="[Update Endpoint Known]", profile_type="post_auth", action=""),
        }
        assert _is_deny(["p1", "p2"], ["WLAN-IoT-DEVICE", "[Update Endpoint Known]"], profiles) is False

    def test_missing_action_is_not_deny(self):
        """Pre-fix bug: missing/empty action defaulted to generic_reject which was treated as deny."""
        from hpe_networking_mcp.platforms.clearpass.policy_visualizer.flow_graph import _is_deny
        from hpe_networking_mcp.platforms.clearpass.policy_visualizer.policy_model import EnforcementProfile

        profiles = {
            "p1": EnforcementProfile(id="p1", name="some-profile", profile_type="radius_accept", action=""),
        }
        assert _is_deny(["p1"], ["some-profile"], profiles) is False

    def test_placeholder_with_bracketed_deny_name_is_deny(self):
        # Placeholder = profile not found in the model dict. Old code matched
        # any name containing "deny" (e.g. "Update Deny List" would falsely
        # trigger). New code requires the canonical [Deny Access Profile]
        # spelling or a [Deny... bracketed name.
        from hpe_networking_mcp.platforms.clearpass.policy_visualizer.flow_graph import _is_deny

        # Placeholder (not in profiles dict) — heuristic only
        assert _is_deny(["unknown_pid"], ["[Deny Access Profile]"], {}) is True
        # False positive guard: a name containing the word "deny" in some
        # non-deny context should NOT trigger
        assert _is_deny(["unknown_pid"], ["Update DenyList Audit"], {}) is False


class TestShortLabelPropagation:
    """Decision nodes must populate short_label with the compact summary so
    diagram renderers can produce legible Mermaid for large policies.
    """

    def test_service_match_decision_has_short_label(self):
        model = build(_minimal_raw())
        flow = compile_service(next(iter(model.services.values())), model)
        match_node = next(n for n in flow.nodes if n.id.endswith("__match"))
        assert match_node.short_label
        # short_label must be substantially shorter than label for compound conditions
        # (label includes 3 lines per predicate; short_label is single line)
        assert "\n" not in match_node.short_label.replace("\n", " ")[: len(match_node.short_label)]
        assert match_node.short_label.startswith("Service Match?")

    def test_enforcement_decision_short_label_is_single_line(self):
        enf_rules = [
            {
                "index": 0,
                "expression": {
                    "operator": "and",
                    "displayOperator": "MATCHES_ALL",
                    "attributes": [
                        {"type": "Tips", "name": "Role", "operator": "EQUALS", "value": "X"},
                        {"type": "Endpoint", "name": "Status", "operator": "EQUALS", "value": "Active"},
                    ],
                },
                "results": [{"name": "Enforcement-Profile", "displayValue": "[Allow Access Profile]"}],
            }
        ]
        model = build(_minimal_raw(enf_rules=enf_rules))
        flow = compile_service(next(iter(model.services.values())), model)
        enf_dec = next(n for n in flow.nodes if "__enf_rule_" in n.id)
        # short_label is one line — no embedded newlines
        assert "\n" not in enf_dec.short_label
        # label is the verbose multi-line form
        assert "\n" in enf_dec.label
        # short_label still encodes both conditions joined with &
        assert "&" in enf_dec.short_label

    def test_non_decision_nodes_default_short_label_to_label(self):
        """For start/process/action/end nodes, short_label defaults to label."""
        model = build(_minimal_raw())
        flow = compile_service(next(iter(model.services.values())), model)
        for node in flow.nodes:
            if node.type != "decision":
                # These nodes don't get a compact override — default == label
                assert node.short_label == node.label, (
                    f"Non-decision node {node.id} ({node.type}) has short_label != label"
                )


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
