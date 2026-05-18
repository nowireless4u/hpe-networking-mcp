"""Inspector-style details serializer for a compiled service.

:func:`build_details` returns a plain dict that mirrors the FlowGraph
rule layout but carries human-readable per-rule action / linked-names
data — used to populate "click a node for full text" inspectors in
frontends, or to build a textual appendix alongside a rendered diagram.

The output dict shape::

    {
        "service_context": {service_name, service_type, description,
                            auth_method_names, auth_source_names, condition_text},
        "authen_rules": [],          # always empty for ClearPass — authentication
                                     # is a single step, not a chain
        "role_mapping_rules": [<rule detail>, ...],
        "enforcement_rules": [<rule detail>, ...],
        "warnings": [str, ...],
        "rule_index": {<trace_id>: <rule detail>, ...},
    }
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from .conditions import BooleanExpr, expr_to_node_label

if TYPE_CHECKING:
    from .policy_model import PolicyModel, Service


def condition_to_text(expr: BooleanExpr | None) -> str:
    """Render a canonical BooleanExpr as a human-readable multiline string."""
    return expr_to_node_label(expr)


def _rule_detail(
    rule_id: str,
    node_trace_id: str,
    index: int,
    name: str,
    condition_text: str,
    action_text: str,
    on_match: str,
    linked_names: list[str],
) -> dict:
    return {
        "rule_id": rule_id,
        "node_trace_id": node_trace_id,
        "index": index,
        "name": name,
        "condition_text": condition_text,
        "action_text": action_text,
        "on_match": on_match,
        "linked_names": linked_names,
    }


def _build_rule_index(role_mapping_rules: list[dict], enforcement_rules: list[dict]) -> dict[str, dict]:
    """Build a trace_rule_id → RuleDetail lookup dict from all rule lists."""
    index: dict[str, dict] = {}
    for rule in role_mapping_rules + enforcement_rules:
        tid = rule["node_trace_id"]
        if tid:
            index[tid] = rule
    return index


def build_details(service: Service, model: PolicyModel) -> dict:
    """Serialize a service + its referenced policies into an inspector dict."""
    from .policy_model import ApplyProfiles, SetRole

    service_context = {
        "service_name": service.name,
        "service_type": service.service_type,
        "description": service.description,
        "auth_method_names": list(service.authentication.method_names),
        "auth_source_names": list(service.authentication.source_names),
        "condition_text": condition_to_text(service.match),
    }

    role_mapping_rules: list[dict] = []
    rm_policy = model.role_mapping_policies.get(service.role_mapping_policy_id)
    if rm_policy:
        for rule in sorted(rm_policy.rules, key=lambda r: r.index):
            then = rule.then
            if isinstance(then, SetRole):
                action_text = f"Set Role: {then.role_name}" if then.role_name else f"Set Role: {then.role_id}"
                linked = [then.role_name] if then.role_name else [then.role_id]
            else:
                names = getattr(then, "profile_names", []) or getattr(then, "profile_ids", [])
                action_text = ", ".join(names)
                linked = list(names)
            role_mapping_rules.append(
                _rule_detail(
                    rule_id=rule.id,
                    node_trace_id=rule.id,
                    index=rule.index,
                    name=rm_policy.name,
                    condition_text=condition_to_text(rule.when),
                    action_text=action_text,
                    on_match=rule.flow.on_match,
                    linked_names=linked,
                )
            )

    enforcement_rules: list[dict] = []
    enf_policy = model.enforcement_policies.get(service.enforcement_policy_id)
    if enf_policy:
        for rule in sorted(enf_policy.rules, key=lambda r: r.index):
            then = rule.then
            if isinstance(then, ApplyProfiles):
                names = then.profile_names if then.profile_names else then.profile_ids
                action_text = ", ".join(names)
                linked = list(names)
            else:
                action_text = str(then)
                linked = []
            enforcement_rules.append(
                _rule_detail(
                    rule_id=rule.id,
                    node_trace_id=rule.id,
                    index=rule.index,
                    name=enf_policy.name,
                    condition_text=condition_to_text(rule.when),
                    action_text=action_text,
                    on_match=rule.flow.on_match,
                    linked_names=linked,
                )
            )

    rule_index = _build_rule_index(role_mapping_rules, enforcement_rules)

    svc_match_key = f"{service.id}__match"
    rule_index[svc_match_key] = _rule_detail(
        rule_id=svc_match_key,
        node_trace_id=svc_match_key,
        index=0,
        name="Service Match",
        condition_text=condition_to_text(service.match),
        action_text="Proceed to authentication",
        on_match="stop",
        linked_names=[],
    )

    return {
        "service_context": service_context,
        "authen_rules": [],
        "role_mapping_rules": role_mapping_rules,
        "enforcement_rules": enforcement_rules,
        "warnings": list(model.warnings),
        "rule_index": rule_index,
    }
