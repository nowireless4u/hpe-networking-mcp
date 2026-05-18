"""Unit tests for the ClearPass policy-visualizer Mermaid renderer.

The renderer's whole purpose is to be defensive against AI assembly
errors: every node declaration on its own line, every edge on its own
line, every label safely quoted. These tests pin the structural
invariants that protect against #356 / #358 recurring.
"""

from __future__ import annotations

import pytest

from hpe_networking_mcp.platforms.clearpass.policy_visualizer.flow_graph import compile_service
from hpe_networking_mcp.platforms.clearpass.policy_visualizer.mermaid_render import (
    _escape_label,
    format_mermaid,
)
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
    return {
        "roles": [{"name": "[Employee]", "description": ""}],
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


def _compile_minimal(simulate: dict | None = None):
    rm_rules = [
        {
            "index": 0,
            "expression": _single_predicate("UserA"),
            "results": [{"name": "Set Role", "displayValue": "Kid"}],
        },
        {
            "index": 1,
            "expression": _single_predicate("UserB"),
            "results": [{"name": "Set Role", "displayValue": "Nest Dweller"}],
        },
    ]
    enf_rules = [
        {
            "index": 0,
            "expression": _single_predicate("Kid"),
            "results": [{"name": "Enforcement-Profile", "displayValue": "[Allow Access Profile]"}],
        },
    ]
    model = build(_minimal_raw(rm_rules=rm_rules, rm_default="Guest", enf_rules=enf_rules))
    service = next(iter(model.services.values()))
    return compile_service(service, model, simulated_attributes=simulate)


class TestEscapeLabel:
    def test_demotes_double_quotes_to_single(self):
        assert _escape_label('Role = "Admin"') == "Role = 'Admin'"

    def test_html_escapes_angle_brackets(self):
        # `<` would otherwise be interpreted as the start of an HTML tag
        assert _escape_label("Score >= 5") == "Score &gt;= 5"
        assert _escape_label("a<b") == "a&lt;b"

    def test_leaves_other_punctuation_alone(self):
        # `&`, `|`, `=`, `:`, `+`, `(`, `)`, `'` all stay inside double-quoted Mermaid labels
        assert _escape_label("Role = 'Kid' & Status = 'Known'") == "Role = 'Kid' & Status = 'Known'"


class TestStructuralInvariants:
    def test_returns_three_sections_in_order(self):
        flow = _compile_minimal()
        result = format_mermaid(flow)
        titles = [s["title"] for s in result["sections"]]
        assert titles == [
            "Block A — Service intake (start → match → auth)",
            "Block B — Role mapping",
            "Block C — Enforcement (decision → access)",
        ]
        assert result["simulated"] is False

    def test_each_node_declaration_on_its_own_line(self):
        """Pin the cardinal rule from #356 / #358: at most one node
        declaration per source line. Detect a declaration as an
        identifier immediately followed by a shape opener.
        """
        import re

        # Identifier followed by a Mermaid shape opener (parens/brackets/braces).
        # Use longest-first alternation so `[/` wins over `[`.
        decl_re = re.compile(r"[A-Za-z_][\w]*(\[/|\(\(\(|\(\[|\{|\[|\()")
        flow = _compile_minimal()
        result = format_mermaid(flow)
        for section in result["sections"]:
            for line in section["code"].split("\n"):
                stripped = line.lstrip()
                if not stripped or stripped.startswith(("%%", "flowchart", "classDef")):
                    continue
                if "-->" in stripped or "-.->" in stripped:
                    continue  # edges are allowed to reference multiple node ids
                matches = decl_re.findall(stripped)
                assert len(matches) <= 1, f"Two node decls on one line: {line!r}"

    def test_every_label_wrapped_in_double_quotes(self):
        flow = _compile_minimal()
        result = format_mermaid(flow)
        # Every node line opens a shape and has `"..."` inside
        for section in result["sections"]:
            for line in section["code"].split("\n"):
                stripped = line.lstrip()
                if "{" not in stripped and "[/" not in stripped and "[" not in stripped and "([" not in stripped:
                    continue
                if stripped.startswith("%%") or stripped.startswith("classDef"):
                    continue
                if "-->" in stripped or "-.->" in stripped:
                    continue
                # Node lines: must have a quoted label region
                assert '"' in stripped, f"Node line without quoted label: {line!r}"

    def test_no_literal_newlines_inside_shapes(self):
        """The cardinal rule from #356: no `\\n` between a shape's opener and closer."""
        flow = _compile_minimal()
        result = format_mermaid(flow)
        # Whole-document property: no shape opener is followed by `\n` before its closer
        for section in result["sections"]:
            code = section["code"]
            # Walk every `{`, `[`, `(` and check the matching close is on the same line
            for line in code.split("\n"):
                # If a shape opens on this line, it must close on this line
                if any(o in line for o in ("{", "[", "(")):
                    pass  # presence checked above; here we just confirm no orphaned shape openers
                # A line ending in an unclosed `{`, `[/`, or `((` would mean the next line
                # is the close. Assert that doesn't happen.
                for opener, closer in [("{", "}"), ("[/", "/]"), ("(((", ")))"), ("([", "])"), ("[", "]")]:
                    if opener in line and closer not in line:
                        pytest.fail(f"Unclosed shape on line: {line!r}")

    def test_radius_proxy_omits_role_mapping_block(self):
        enf_rules = [
            {
                "index": 0,
                "expression": _single_predicate("X"),
                "results": [{"name": "Enforcement-Profile", "displayValue": "[Allow Access Profile]"}],
            }
        ]
        model = build(_minimal_raw(enf_rules=enf_rules, service_type="RADIUS_PROXY"))
        service = next(iter(model.services.values()))
        flow = compile_service(service, model)
        result = format_mermaid(flow)
        titles = [s["title"] for s in result["sections"]]
        assert "Block B — Role mapping" not in titles


class TestSimulationStyling:
    def test_simulated_flag_set_when_simulation_present(self):
        flow = _compile_minimal(simulate={"Tips:Role": ["UserA", "Kid"]})
        result = format_mermaid(flow)
        assert result["simulated"] is True

    def test_sim_classdefs_injected_when_simulated(self):
        flow = _compile_minimal(simulate={"Tips:Role": ["UserA", "Kid"]})
        result = format_mermaid(flow)
        combined = "\n".join(s["code"] for s in result["sections"])
        assert "classDef sim_match" in combined
        assert "classDef sim_skip" in combined
        assert "classDef sim_unknown" in combined

    def test_sim_classdefs_omitted_when_not_simulated(self):
        flow = _compile_minimal()
        result = format_mermaid(flow)
        combined = "\n".join(s["code"] for s in result["sections"])
        assert "classDef sim_match" not in combined
        assert "classDef sim_skip" not in combined

    def test_matching_decision_node_gets_sim_match_class(self):
        # Pass both roles so service-match (Tips:Role=AirGroup) AND
        # rule 0 (Tips:Role=UserA) both evaluate True. Multi-valued
        # Tips:Role: positive ops match if ANY value satisfies.
        flow = _compile_minimal(simulate={"Tips:Role": ["AirGroup", "UserA"]})
        result = format_mermaid(flow)
        # Block B holds the role-mapping decision lines
        block_b = next(s for s in result["sections"] if "Role mapping" in s["title"])
        assert ":::sim_match" in block_b["code"]
