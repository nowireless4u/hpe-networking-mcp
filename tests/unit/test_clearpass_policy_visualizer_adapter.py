"""Unit tests for the ClearPass policy-visualizer adapter + conditions.

Covers the REST → ``raw`` dict transformation and the canonical operator
mapping. Engine internals only — no I/O.
"""

from __future__ import annotations

import pytest

from hpe_networking_mcp.platforms.clearpass.policy_visualizer.api_adapter import adapt
from hpe_networking_mcp.platforms.clearpass.policy_visualizer.conditions import (
    And,
    Op,
    Or,
    Predicate,
    expr_to_label,
    expr_to_node_label,
    normalize,
)

pytestmark = pytest.mark.unit


# ---------------------------------------------------------------------------
# Op mapping
# ---------------------------------------------------------------------------


class TestOpFromRaw:
    @pytest.mark.parametrize(
        ("raw", "expected"),
        [
            ("EQUALS", Op.equals),
            ("NOT_EQUALS", Op.not_equals),
            ("CONTAINS", Op.contains),
            ("MATCHES_REGEX", Op.regex),
            ("NOT_MATCHES_REGEX", Op.not_regex),
            ("MATCHES_ANY", Op.in_),  # per-predicate MATCHES_ANY means "in set"
            ("MATCHES_ALL", Op.matches_all),
            ("BELONGS_TO", Op.belongs_to_group),
            ("BEGINS_WITH", Op.starts_with),  # alias of STARTS_WITH
        ],
    )
    def test_known_operators(self, raw, expected):
        assert Op.from_raw(raw) is expected

    def test_unknown_operator_raises(self):
        with pytest.raises(ValueError, match="Unknown ClearPass operator"):
            Op.from_raw("DOES_NOT_EXIST")


# ---------------------------------------------------------------------------
# normalize() — Boolean AST construction
# ---------------------------------------------------------------------------


class TestNormalize:
    def test_none_input_returns_none(self):
        assert normalize(None) is None

    def test_single_predicate_unwraps_to_bare_predicate(self):
        raw = {
            "operator": "and",
            "attributes": [{"type": "Tips", "name": "Role", "operator": "EQUALS", "value": "X"}],
        }
        expr = normalize(raw)
        assert isinstance(expr, Predicate)
        assert expr.namespace == "Tips"
        assert expr.attribute == "Role"
        assert expr.op is Op.equals
        assert expr.rhs_raw == "X"

    def test_and_wrapper_with_multiple_predicates(self):
        raw = {
            "operator": "and",
            "attributes": [
                {"type": "T1", "name": "n1", "operator": "EQUALS", "value": "v1"},
                {"type": "T2", "name": "n2", "operator": "EQUALS", "value": "v2"},
            ],
        }
        expr = normalize(raw)
        assert isinstance(expr, And)
        assert len(expr.operands) == 2

    def test_or_via_display_operator(self):
        raw = {
            "displayOperator": "MATCHES_ANY",
            "attributes": [
                {"type": "T1", "name": "n1", "operator": "EQUALS", "value": "v1"},
                {"type": "T2", "name": "n2", "operator": "EQUALS", "value": "v2"},
            ],
        }
        expr = normalize(raw)
        assert isinstance(expr, Or)

    def test_empty_attributes_returns_sentinel_and(self):
        expr = normalize({"operator": "and", "attributes": []})
        assert isinstance(expr, And)
        assert expr.operands == []


# ---------------------------------------------------------------------------
# Label helpers
# ---------------------------------------------------------------------------


class TestLabels:
    def test_expr_to_label_none(self):
        assert expr_to_label(None) == "(no condition)"

    def test_expr_to_label_predicate(self):
        p = Predicate(namespace="Tips", attribute="Role", op=Op.equals, rhs_raw="", rhs_display="Helpdesk")
        label = expr_to_label(p)
        assert "Role" in label
        assert "Helpdesk" in label

    def test_expr_to_node_label_multiline(self):
        p = Predicate(
            namespace="Tips", attribute="Role", op=Op.equals, rhs_raw="X", rhs_display="", raw_operator="EQUALS"
        )
        label = expr_to_node_label(p)
        # three lines: namespace:attr / op / rhs
        assert label.count("\n") == 2
        assert "Tips:Role" in label
        assert "EQUALS" in label

    def test_expr_to_node_label_picks_display_over_numeric_raw(self):
        # When raw is a bare numeric ID, prefer the display value
        p = Predicate(
            namespace="GuestUser",
            attribute="Role ID",
            op=Op.equals,
            rhs_raw="1",
            rhs_display="Employee",
            raw_operator="EQUALS",
        )
        label = expr_to_node_label(p)
        assert "Employee" in label
        assert "\n1" not in label  # raw "1" should be replaced


# ---------------------------------------------------------------------------
# adapt() — REST → raw
# ---------------------------------------------------------------------------


class TestAdapterEnforcementProfileBucketing:
    def test_radius_accept_lands_in_radius_bucket(self):
        raw = adapt(
            services=[],
            role_mappings=[],
            enforcement_policies=[],
            enforcement_profiles=[{"name": "P1", "type": "RADIUS", "action": "Accept"}],
            roles=[],
            auth_methods=[],
            auth_sources=[],
        )
        assert len(raw["radiusEnfProfiles"]) == 1
        assert raw["radiusEnfProfiles"][0]["name"] == "P1"
        assert raw["radiusEnfProfiles"][0]["action"] == "Accept"
        assert len(raw["tacacsEnfProfiles"]) == 0

    def test_tacacs_lands_in_tacacs_bucket(self):
        raw = adapt(
            services=[],
            role_mappings=[],
            enforcement_policies=[],
            enforcement_profiles=[{"name": "T1", "type": "TACACS", "action": "Accept"}],
            roles=[],
            auth_methods=[],
            auth_sources=[],
        )
        assert len(raw["tacacsEnfProfiles"]) == 1
        assert len(raw["radiusEnfProfiles"]) == 0

    def test_unknown_type_lands_in_generic_bucket(self):
        raw = adapt(
            services=[],
            role_mappings=[],
            enforcement_policies=[],
            enforcement_profiles=[{"name": "X", "type": "WeirdNewType", "action": "Accept"}],
            roles=[],
            auth_methods=[],
            auth_sources=[],
        )
        assert len(raw["genericEnfProfiles"]) == 1


class TestAdapterRules:
    def test_role_mapping_rule_with_single_condition(self):
        raw = adapt(
            services=[],
            role_mappings=[
                {
                    "name": "RM1",
                    "rule_combine_algo": "first-applicable",
                    "default_role_name": "[Employee]",
                    "rules": [
                        {
                            "match_type": "OR",
                            "role_name": "[Contractor]",
                            "condition": [{"type": "GuestUser", "name": "Role ID", "oper": "EQUALS", "value": "1"}],
                        }
                    ],
                }
            ],
            enforcement_policies=[],
            enforcement_profiles=[],
            roles=[],
            auth_methods=[],
            auth_sources=[],
        )
        rm = raw["roleMappings"][0]
        assert rm["ruleCombineAlgo"] == "first-applicable"
        assert rm["defaultRole"] == "[Employee]"
        rule = rm["rules"][0]
        assert rule["index"] == 0
        assert rule["results"] == [{"name": "Role", "displayValue": "[Contractor]"}]
        expr = rule["expression"]
        # single condition → still wrapped (normalize() unwraps later)
        assert len(expr["attributes"]) == 1
        assert expr["attributes"][0]["operator"] == "EQUALS"  # normalized from `oper`

    def test_enforcement_rule_with_multiple_conditions(self):
        raw = adapt(
            services=[],
            role_mappings=[],
            enforcement_policies=[
                {
                    "name": "EP1",
                    "enforcement_type": "RADIUS",
                    "rule_eval_algo": "evaluate-all",
                    "default_enforcement_profile": "[AirGroup Response]",
                    "rules": [
                        {
                            "enforcement_profile_names": ["[Profile A]", "[Profile B]"],
                            "condition": [
                                {"type": "Tips", "name": "Role", "oper": "MATCHES_ANY", "value": "X"},
                                {"type": "GuestUser", "name": "enabled", "oper": "EQUALS", "value": "1"},
                            ],
                        }
                    ],
                }
            ],
            enforcement_profiles=[],
            roles=[],
            auth_methods=[],
            auth_sources=[],
        )
        ep = raw["enforcementPolicies"][0]
        assert ep["ruleCombineAlgo"] == "evaluate-all"
        assert ep["policyType"] == "RADIUS"
        assert ep["defaultProfile"] == "[AirGroup Response]"
        rule = ep["rules"][0]
        assert rule["results"] == [{"name": "Enforcement-Profile", "displayValue": "[Profile A], [Profile B]"}]
        expr = rule["expression"]
        # 2 conditions, no match_type → default AND
        assert expr["operator"] == "and"
        assert expr["displayOperator"] == "MATCHES_ALL"
        assert len(expr["attributes"]) == 2


class TestAdapterServices:
    def test_service_with_match_conditions_and_refs(self):
        raw = adapt(
            services=[
                {
                    "name": "[AirGroup Authorization Service]",
                    "description": "Authz for AirGroup",
                    "type": "RADIUS",
                    "rules_match_type": "MATCHES_ALL",
                    "rules_conditions": [
                        {
                            "type": "Radius:IETF",
                            "name": "Called-Station-Id",
                            "operator": "EQUALS",
                            "value": "AirGroup",
                        }
                    ],
                    "auth_methods": ["[Allow All MAC AUTH]"],
                    "auth_sources": ["[Guest Device Repository]"],
                    "role_mapping_policy": "[AirGroup Version Match]",
                    "enf_policy": "[AirGroup Enforcement Policy]",
                }
            ],
            role_mappings=[],
            enforcement_policies=[],
            enforcement_profiles=[],
            roles=[],
            auth_methods=[],
            auth_sources=[],
        )
        svc = raw["services"][0]
        assert svc["name"] == "[AirGroup Authorization Service]"
        assert svc["serviceType"] == "RADIUS"
        assert svc["authMethods"] == ["[Allow All MAC AUTH]"]
        assert svc["authSources"] == ["[Guest Device Repository]"]
        assert svc["roleMappings"] == ["[AirGroup Version Match]"]
        assert svc["enfPolicies"] == ["[AirGroup Enforcement Policy]"]
        assert svc["matchExpression"]["attributes"][0]["operator"] == "EQUALS"

    def test_service_type_mapped(self):
        raw = adapt(
            services=[
                {"name": "S1", "type": "Aruba Application Authentication"},
            ],
            role_mappings=[],
            enforcement_policies=[],
            enforcement_profiles=[],
            roles=[],
            auth_methods=[],
            auth_sources=[],
        )
        # mapped to RADIUS via _SERVICE_TYPE_MAP
        assert raw["services"][0]["serviceType"] == "RADIUS"

    def test_service_without_role_mapping_emits_empty_list(self):
        raw = adapt(
            services=[{"name": "S2", "type": "RADIUS_PROXY"}],
            role_mappings=[],
            enforcement_policies=[],
            enforcement_profiles=[],
            roles=[],
            auth_methods=[],
            auth_sources=[],
        )
        # RADIUS_PROXY services skip auth + role mapping in flow compilation
        svc = raw["services"][0]
        assert svc["serviceType"] == "RADIUS_PROXY"
        assert svc["roleMappings"] == []
        assert svc["enfPolicies"] == []


class TestAdapterAuthMethodsAndSources:
    def test_auth_method_field_mapping(self):
        raw = adapt(
            services=[],
            role_mappings=[],
            enforcement_policies=[],
            enforcement_profiles=[],
            roles=[],
            auth_methods=[
                {
                    "name": "[PAP]",
                    "method_type": "PAP",
                    "details": {"encryption_scheme": "auto"},
                    "inner_methods": [],
                }
            ],
            auth_sources=[],
        )
        am = raw["authMethods"][0]
        assert am["name"] == "[PAP]"
        assert am["methodType"] == "PAP"
        assert am["params"] == {"encryption_scheme": "auto"}
        assert am["innerMethods"] == []

    def test_auth_source_coerces_authz_to_string(self):
        raw = adapt(
            services=[],
            role_mappings=[],
            enforcement_policies=[],
            enforcement_profiles=[],
            roles=[],
            auth_methods=[],
            auth_sources=[
                {"name": "src1", "type": "LDAP", "isAuthorizationSource": True},
                {"name": "src2", "type": "Local", "isAuthorizationSource": "false"},
            ],
        )
        # Boolean values get string-coerced so the upstream comparison works
        assert raw["authSources"][0]["isAuthorizationSource"] == "True"
        assert raw["authSources"][1]["isAuthorizationSource"] == "false"
