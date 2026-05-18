"""REST → ``raw`` dict adapter.

Converts the JSON returned by the ``clearpass_get_*`` tools into the
``raw`` dict shape that :func:`policy_model.build` expects. The upstream
visualizer fed that shape from an XML parser — this module replaces it
for live API input.

Per-object key mapping (REST → raw):

- ``clearpass_get_roles`` (``name``, ``description``) → ``roles[]``.
- ``clearpass_get_auth_methods`` (``name``, ``method_type``, ``details``,
  ``inner_methods``) → ``authMethods[]``.
- ``clearpass_get_auth_sources`` (``name``, ``type``, ``description``)
  → ``authSources[]``.
- ``clearpass_get_enforcement_profiles`` bucketed by ``type`` field:
  RADIUS → ``radiusEnfProfiles[]``, TACACS → ``tacacsEnfProfiles[]``,
  RADIUS_CoA → ``radiusCoaEnfProfiles[]``, Post-Auth →
  ``postAuthEnfProfiles[]``, anything else → ``genericEnfProfiles[]``.
- ``clearpass_get_role_mappings``: ``rules[].condition`` +
  ``rules[].match_type`` → ``rules[].expression``;
  ``rules[].role_name`` → ``rules[].results``;
  ``rule_combine_algo``, ``default_role_name`` →
  ``ruleCombineAlgo``, ``defaultRole``.
- ``clearpass_get_enforcement_policies``: ``rules[].condition`` +
  ``rules[].match_type`` → ``rules[].expression``;
  ``rules[].enforcement_profile_names`` → ``rules[].results``;
  ``rule_eval_algo``, ``default_enforcement_profile`` →
  ``ruleCombineAlgo``, ``defaultProfile``; ``enforcement_type`` →
  ``policyType``.
- ``clearpass_get_services``: ``rules_conditions`` +
  ``rules_match_type`` → ``matchExpression``; ``type`` →
  ``serviceType`` (via ``_SERVICE_TYPE_MAP``); ``role_mapping_policy``,
  ``enf_policy`` → ``roleMappings[0]``, ``enfPolicies[0]``.

Operators are passed through as-is — :meth:`Op.from_raw` handles the
uppercase mapping.
"""

from __future__ import annotations

from typing import Any

# Service type strings ClearPass returns vs. what the upstream IR (and flow
# compiler) expects. RADIUS_PROXY in particular short-circuits auth + role
# mapping in flow_graph.compile_service.
_SERVICE_TYPE_MAP = {
    "RADIUS": "RADIUS",
    "TACACS": "TACACS",
    "RADIUS_PROXY": "RADIUS_PROXY",
    "Aruba Application Authentication": "RADIUS",
    "Aruba Application Authorization": "RADIUS",
    "Web-based Authentication": "RADIUS",
    "Web-based Open Network Authentication": "RADIUS",
}


def _adapt_condition(cond: dict) -> dict:
    """Normalize one REST condition into a predicate attribute dict.

    REST role-mapping / enforcement rules use ``oper``; services use
    ``operator``. We standardize on ``operator`` so :func:`conditions._normalize_predicate`
    reads it directly. ``value_disp_name`` is renamed to ``displayValue``.
    """
    return {
        "type": cond.get("type", ""),
        "name": cond.get("name", ""),
        "operator": cond.get("oper") or cond.get("operator") or "EQUALS",
        "value": cond.get("value", ""),
        "displayValue": cond.get("value_disp_name") or cond.get("displayValue", ""),
    }


def _adapt_expression(conditions: list[dict], match_type: str | None) -> dict | None:
    """Wrap a flat REST condition list into the ``raw_expression`` dict shape.

    Returns ``None`` if the condition list is empty (compatible with
    :func:`conditions.normalize`, which also returns ``None`` for absent input).
    """
    if not conditions:
        return None
    attributes = [_adapt_condition(c) for c in conditions]
    # match_type maps to displayOperator (MATCHES_ALL / MATCHES_ANY). Default to
    # MATCHES_ALL (AND) when absent — multi-condition rules without an explicit
    # match_type are implicitly conjunctive in CPPM.
    mt = (match_type or "AND").upper()
    display_op = "MATCHES_ANY" if mt in ("OR", "MATCHES_ANY") else "MATCHES_ALL"
    op_lower = "or" if display_op == "MATCHES_ANY" else "and"
    return {
        "operator": op_lower,
        "displayOperator": display_op,
        "attributes": attributes,
    }


def _adapt_rm_rule(rest_rule: dict, index: int) -> dict:
    """Convert one REST role-mapping rule to the raw rule dict shape."""
    expression = _adapt_expression(rest_rule.get("condition", []), rest_rule.get("match_type"))
    role_name = rest_rule.get("role_name", "")
    return {
        "index": index,
        "expression": expression,
        "results": [{"name": "Role", "displayValue": role_name}],
    }


def _adapt_enf_rule(rest_rule: dict, index: int) -> dict:
    """Convert one REST enforcement-policy rule to the raw rule dict shape."""
    expression = _adapt_expression(rest_rule.get("condition", []), rest_rule.get("match_type"))
    profile_names = rest_rule.get("enforcement_profile_names", []) or []
    return {
        "index": index,
        "expression": expression,
        "results": [{"name": "Enforcement-Profile", "displayValue": ", ".join(profile_names)}],
    }


def _bucket_for_profile(profile: dict) -> str:
    """Return the raw bucket name for an enforcement profile based on its type."""
    ptype = profile.get("type", "")
    # ClearPass UI labels: "RADIUS" / "TACACS" / "RADIUS_CoA" / "Post-Auth" / ...
    if ptype == "TACACS":
        return "tacacsEnfProfiles"
    if ptype in ("RADIUS_CoA", "RADIUS CoA"):
        return "radiusCoaEnfProfiles"
    if ptype in ("Post-Auth", "PostAuth"):
        return "postAuthEnfProfiles"
    if ptype == "RADIUS":
        return "radiusEnfProfiles"
    return "genericEnfProfiles"


def _normalize_profile(profile: dict) -> dict:
    """Slim a REST enforcement profile to the keys the builder reads."""
    return {
        "name": profile.get("name", ""),
        "action": profile.get("action", ""),
        "description": profile.get("description", ""),
    }


def adapt(
    *,
    services: list[dict],
    role_mappings: list[dict],
    enforcement_policies: list[dict],
    enforcement_profiles: list[dict],
    roles: list[dict],
    auth_methods: list[dict],
    auth_sources: list[dict],
) -> dict[str, Any]:
    """Convert REST responses into the ``raw`` dict shape :func:`policy_model.build` expects."""
    raw: dict[str, Any] = {
        "roles": [{"name": r.get("name", ""), "description": r.get("description", "")} for r in roles],
        "authMethods": [
            {
                "name": am.get("name", ""),
                "methodType": am.get("method_type", ""),
                "params": am.get("details") or am.get("params") or {},
                "innerMethods": am.get("inner_methods", []),
            }
            for am in auth_methods
        ],
        "authSources": [
            {
                "name": s.get("name", ""),
                "type": s.get("type", ""),
                "description": s.get("description", ""),
                "isAuthorizationSource": str(s.get("isAuthorizationSource", "false")),
            }
            for s in auth_sources
        ],
        "radiusEnfProfiles": [],
        "tacacsEnfProfiles": [],
        "radiusCoaEnfProfiles": [],
        "postAuthEnfProfiles": [],
        "genericEnfProfiles": [],
        "roleMappings": [],
        "enforcementPolicies": [],
        "services": [],
    }

    for p in enforcement_profiles:
        bucket = _bucket_for_profile(p)
        raw[bucket].append(_normalize_profile(p))

    for rm in role_mappings:
        raw["roleMappings"].append(
            {
                "name": rm.get("name", ""),
                "description": rm.get("description", ""),
                "ruleCombineAlgo": rm.get("rule_combine_algo", "first-applicable"),
                "defaultRole": rm.get("default_role_name", ""),
                "rules": [_adapt_rm_rule(r, i) for i, r in enumerate(rm.get("rules", []))],
            }
        )

    for ep in enforcement_policies:
        raw["enforcementPolicies"].append(
            {
                "name": ep.get("name", ""),
                "description": ep.get("description", ""),
                "policyType": ep.get("enforcement_type", ""),
                "ruleCombineAlgo": ep.get("rule_eval_algo") or ep.get("rule_combine_algo") or "first-applicable",
                "defaultProfile": ep.get("default_enforcement_profile", ""),
                "rules": [_adapt_enf_rule(r, i) for i, r in enumerate(ep.get("rules", []))],
            }
        )

    for svc in services:
        match_expr = _adapt_expression(svc.get("rules_conditions", []), svc.get("rules_match_type"))
        service_type_raw = svc.get("type", "RADIUS")
        service_type = _SERVICE_TYPE_MAP.get(service_type_raw, service_type_raw)
        rm_name = svc.get("role_mapping_policy", "")
        ep_name = svc.get("enf_policy", "")
        raw["services"].append(
            {
                "name": svc.get("name", ""),
                "description": svc.get("description", ""),
                "serviceType": service_type,
                "matchExpression": match_expr,
                "authMethods": svc.get("auth_methods", []),
                "authSources": svc.get("auth_sources", []),
                "roleMappings": [rm_name] if rm_name else [],
                "enfPolicies": [ep_name] if ep_name else [],
            }
        )

    return raw
