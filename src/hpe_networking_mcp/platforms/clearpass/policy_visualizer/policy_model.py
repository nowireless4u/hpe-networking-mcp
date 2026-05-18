"""Typed model of a ClearPass policy graph.

:func:`build` takes a ``raw`` dict (produced by :mod:`api_adapter` from
live ``clearpass_get_*`` responses) and returns a :class:`PolicyModel`
holding every service, role-mapping policy, enforcement policy /
profile, role, auth method, and auth source, with cross-references
resolved by name.

References to objects that aren't present in the input get **placeholder
records** + a human-readable line appended to ``model.warnings`` —
compilation never fails on a partial dataset.

Object IDs inside the model are deterministic slug + sha256[:6] hashes
of the upstream name. They're stable across re-builds (good for tests
and diffing) but are NOT the ClearPass numeric IDs — those live in the
original REST response and should be used directly when calling back
into ``clearpass_get_*`` tools.
"""

from __future__ import annotations

import hashlib
import logging
import re
from dataclasses import dataclass, field
from typing import Any

from .conditions import BooleanExpr, normalize

logger = logging.getLogger(__name__)


def _stable_id(name: str) -> str:
    """Generate a stable slug-style internal ID from an object name."""
    slug = re.sub(r"[^a-zA-Z0-9]+", "_", name).strip("_").lower()
    suffix = hashlib.sha256(name.encode()).hexdigest()[:6]
    return f"{slug}_{suffix}" if slug else f"id_{suffix}"


# ---------------------------------------------------------------------------
# Typed records
# ---------------------------------------------------------------------------


@dataclass
class AuthMethod:
    id: str
    name: str
    method_type: str
    params: dict[str, str] = field(default_factory=dict)
    inner_methods: list[str] = field(default_factory=list)


@dataclass
class AuthSource:
    id: str
    name: str
    source_type: str
    description: str = ""
    is_authz_source: bool = False


@dataclass
class Role:
    id: str
    name: str
    description: str = ""


@dataclass
class RuleThen:
    pass


@dataclass
class SetRole(RuleThen):
    role_id: str
    role_name: str


@dataclass
class ApplyProfiles(RuleThen):
    profile_ids: list[str] = field(default_factory=list)
    profile_names: list[str] = field(default_factory=list)


@dataclass
class RuleFlow:
    on_match: str = "stop"  # "stop" | "continue"


@dataclass
class PolicyRule:
    id: str
    index: int
    when: BooleanExpr | None
    then: RuleThen
    flow: RuleFlow = field(default_factory=RuleFlow)


@dataclass
class RoleMappingPolicy:
    id: str
    name: str
    rule_combine_algo: str
    rules: list[PolicyRule] = field(default_factory=list)
    default: SetRole | None = None


@dataclass
class ServiceAuthentication:
    method_ids: list[str] = field(default_factory=list)
    method_names: list[str] = field(default_factory=list)
    source_ids: list[str] = field(default_factory=list)
    source_names: list[str] = field(default_factory=list)


@dataclass
class EnforcementPolicy:
    id: str
    name: str
    policy_type: str
    rule_combine_algo: str = "first-applicable"
    rules: list[PolicyRule] = field(default_factory=list)
    default: ApplyProfiles | None = None


@dataclass
class EnforcementProfile:
    id: str
    name: str
    # profile_type is one of: radius_accept, radius_reject, tacacs_accept,
    # tacacs_other, radius_coa, generic_accept, generic_reject, post_auth,
    # builtin (last one is used for placeholder objects).
    profile_type: str
    action: str = ""
    description: str = ""


@dataclass
class Service:
    id: str
    name: str
    description: str
    service_type: str
    match: BooleanExpr | None
    authentication: ServiceAuthentication
    role_mapping_policy_id: str
    role_mapping_policy_name: str
    enforcement_policy_id: str
    enforcement_policy_name: str


@dataclass
class PolicyModel:
    services: dict[str, Service] = field(default_factory=dict)
    role_mapping_policies: dict[str, RoleMappingPolicy] = field(default_factory=dict)
    enforcement_policies: dict[str, EnforcementPolicy] = field(default_factory=dict)
    enforcement_profiles: dict[str, EnforcementProfile] = field(default_factory=dict)
    roles: dict[str, Role] = field(default_factory=dict)
    auth_methods: dict[str, AuthMethod] = field(default_factory=dict)
    auth_sources: dict[str, AuthSource] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Builder
# ---------------------------------------------------------------------------


def build(raw: dict[str, Any]) -> PolicyModel:
    """Assemble a :class:`PolicyModel` from the adapter's ``raw`` dict.

    Expected top-level keys: ``roles``, ``authMethods``, ``authSources``,
    ``radiusEnfProfiles``, ``postAuthEnfProfiles``, ``tacacsEnfProfiles``,
    ``radiusCoaEnfProfiles``, ``genericEnfProfiles``, ``roleMappings``,
    ``enforcementPolicies``, ``services``. Each key holds a list of
    object dicts matching the shape the original XML pipeline produced —
    see :mod:`api_adapter` for the REST → raw transformation.
    """
    model = PolicyModel()

    # Roles
    for r in raw.get("roles", []):
        rid = _stable_id(r["name"])
        model.roles[rid] = Role(id=rid, name=r["name"], description=r.get("description", ""))
    role_by_name = {v.name: v for v in model.roles.values()}

    # Auth methods
    for am in raw.get("authMethods", []):
        mid = _stable_id(am["name"])
        model.auth_methods[mid] = AuthMethod(
            id=mid,
            name=am["name"],
            method_type=am.get("methodType", ""),
            params=am.get("params", {}),
            inner_methods=am.get("innerMethods", []),
        )
    method_by_name = {v.name: v for v in model.auth_methods.values()}

    # Auth sources
    for src in raw.get("authSources", []):
        sid = _stable_id(src["name"])
        model.auth_sources[sid] = AuthSource(
            id=sid,
            name=src["name"],
            source_type=src.get("type", ""),
            description=src.get("description", ""),
            is_authz_source=str(src.get("isAuthorizationSource", "false")).lower() == "true",
        )
    source_by_name = {v.name: v for v in model.auth_sources.values()}

    # Enforcement profiles (RADIUS + PostAuth + TACACS + CoA + Generic)
    for rp in raw.get("radiusEnfProfiles", []):
        pid = _stable_id(rp["name"])
        action = rp.get("action", "").lower()
        profile_type = "radius_accept" if action == "accept" else "radius_reject"
        model.enforcement_profiles[pid] = EnforcementProfile(
            id=pid,
            name=rp["name"],
            profile_type=profile_type,
            action=action,
            description=rp.get("description", ""),
        )
    for pp in raw.get("postAuthEnfProfiles", []):
        pid = _stable_id(pp["name"])
        model.enforcement_profiles[pid] = EnforcementProfile(
            id=pid,
            name=pp["name"],
            profile_type="post_auth",
            description=pp.get("description", ""),
        )
    for tp in raw.get("tacacsEnfProfiles", []):
        pid = _stable_id(tp["name"])
        action = tp.get("action", "").lower()
        model.enforcement_profiles[pid] = EnforcementProfile(
            id=pid,
            name=tp["name"],
            profile_type="tacacs_accept" if action == "accept" else "tacacs_other",
            action=action,
            description=tp.get("description", ""),
        )
    for cp in raw.get("radiusCoaEnfProfiles", []):
        pid = _stable_id(cp["name"])
        model.enforcement_profiles[pid] = EnforcementProfile(
            id=pid,
            name=cp["name"],
            profile_type="radius_coa",
            action=cp.get("action", "").lower(),
            description=cp.get("description", ""),
        )
    for gp in raw.get("genericEnfProfiles", []):
        pid = _stable_id(gp["name"])
        action = gp.get("action", "").lower()
        model.enforcement_profiles[pid] = EnforcementProfile(
            id=pid,
            name=gp["name"],
            profile_type="generic_accept" if action == "accept" else "generic_reject",
            action=action,
            description=gp.get("description", ""),
        )
    profile_by_name = {v.name: v for v in model.enforcement_profiles.values()}

    def _resolve_profiles(display_value: str, context: str = "") -> tuple[list[str], list[str]]:
        """Parse a comma-separated displayValue of profile names into (ids, names)."""
        names = [n.strip() for n in display_value.split(",") if n.strip()]
        ids = []
        for n in names:
            if n in profile_by_name:
                ids.append(profile_by_name[n].id)
            else:
                ctx = f" ({context})" if context else ""
                msg = f"EnforcementProfile '{n}' not found{ctx} — using placeholder"
                logger.warning("Unresolved reference: %s", msg)
                model.warnings.append(msg)
                pid = _stable_id(n)
                placeholder = EnforcementProfile(
                    id=pid,
                    name=n,
                    profile_type="builtin",
                    description="Built-in profile (not in API response)",
                )
                model.enforcement_profiles[pid] = placeholder
                profile_by_name[n] = placeholder
                ids.append(pid)
        return ids, names

    # Role mapping policies
    for rm in raw.get("roleMappings", []):
        rmid = _stable_id(rm["name"])
        rules = []
        for raw_rule in rm.get("rules", []):
            expr = normalize(raw_rule.get("expression"))
            results = raw_rule.get("results", [])
            then: RuleThen
            role_result = next((r for r in results if r.get("name") == "Role"), None)
            if role_result:
                role_name = role_result.get("displayValue", "")
                role = role_by_name.get(role_name)
                if role is None and role_name:
                    msg = f"Role '{role_name}' not found (rule in RoleMappingPolicy '{rm['name']}') — using placeholder"
                    logger.warning("Unresolved reference: %s", msg)
                    model.warnings.append(msg)
                    rid = _stable_id(role_name)
                    role = Role(id=rid, name=role_name, description="Built-in role (not in API response)")
                    model.roles[rid] = role
                    role_by_name[role_name] = role
                then = SetRole(
                    role_id=role.id if role else _stable_id(role_name),
                    role_name=role_name,
                )
            else:
                then = SetRole(role_id="unknown", role_name="Unknown")
            rule_id = f"{rmid}_rule_{raw_rule['index']}"
            rules.append(PolicyRule(id=rule_id, index=raw_rule["index"], when=expr, then=then))

        default_role_name = rm.get("defaultRole", "")
        default_role = role_by_name.get(default_role_name)
        if default_role_name and default_role is None:
            msg = (
                f"Role '{default_role_name}' not found "
                f"(default in RoleMappingPolicy '{rm['name']}') — using placeholder"
            )
            logger.warning("Unresolved reference: %s", msg)
            model.warnings.append(msg)
            rid = _stable_id(default_role_name)
            default_role = Role(id=rid, name=default_role_name, description="Built-in role (not in API response)")
            model.roles[rid] = default_role
            role_by_name[default_role_name] = default_role
        rm_default: SetRole | None = (
            SetRole(
                role_id=default_role.id if default_role else _stable_id(default_role_name),
                role_name=default_role_name,
            )
            if default_role_name
            else None
        )

        model.role_mapping_policies[rmid] = RoleMappingPolicy(
            id=rmid,
            name=rm["name"],
            rule_combine_algo=rm.get("ruleCombineAlgo", "first-applicable"),
            rules=rules,
            default=rm_default,
        )
    rm_by_name = {v.name: v for v in model.role_mapping_policies.values()}

    # Enforcement policies
    for ep in raw.get("enforcementPolicies", []):
        epid = _stable_id(ep["name"])
        rules = []
        for raw_rule in ep.get("rules", []):
            expr = normalize(raw_rule.get("expression"))
            results = raw_rule.get("results", [])
            enf_result = next((r for r in results if r.get("name") == "Enforcement-Profile"), None)
            profile_ids: list[str] = []
            profile_names: list[str] = []
            if enf_result:
                ctx = f"rule in EnforcementPolicy '{ep['name']}'"
                profile_ids, profile_names = _resolve_profiles(enf_result.get("displayValue", ""), ctx)
            then = ApplyProfiles(profile_ids=profile_ids, profile_names=profile_names)
            rule_id = f"{epid}_rule_{raw_rule['index']}"
            rules.append(PolicyRule(id=rule_id, index=raw_rule["index"], when=expr, then=then))

        default_profile_name = ep.get("defaultProfile", "")
        default_profile = profile_by_name.get(default_profile_name)
        if default_profile_name and default_profile is None:
            msg = (
                f"EnforcementProfile '{default_profile_name}' not found "
                f"(default in EnforcementPolicy '{ep['name']}') — using placeholder"
            )
            logger.warning("Unresolved reference: %s", msg)
            model.warnings.append(msg)
            pid = _stable_id(default_profile_name)
            placeholder = EnforcementProfile(
                id=pid,
                name=default_profile_name,
                profile_type="builtin",
                description="Built-in profile (not in API response)",
            )
            model.enforcement_profiles[pid] = placeholder
            profile_by_name[default_profile_name] = placeholder
            default_profile = placeholder
        ep_default: ApplyProfiles | None = (
            ApplyProfiles(
                profile_ids=[default_profile.id] if default_profile else [],
                profile_names=[default_profile_name] if default_profile_name else [],
            )
            if default_profile_name
            else None
        )

        model.enforcement_policies[epid] = EnforcementPolicy(
            id=epid,
            name=ep["name"],
            policy_type=ep.get("policyType", ""),
            rule_combine_algo=ep.get("ruleCombineAlgo", "first-applicable"),
            rules=rules,
            default=ep_default,
        )
    ep_by_name = {v.name: v for v in model.enforcement_policies.values()}

    # Services
    for svc in raw.get("services", []):
        svid = _stable_id(svc["name"])
        match_expr = normalize(svc.get("matchExpression"))

        method_ids = []
        method_names = svc.get("authMethods", [])
        for mn in method_names:
            m = method_by_name.get(mn)
            if m is None and mn:
                msg = f"AuthMethod '{mn}' not found (referenced in Service '{svc['name']}') — using placeholder"
                logger.warning("Unresolved reference: %s", msg)
                model.warnings.append(msg)
                mid = _stable_id(mn)
                m = AuthMethod(id=mid, name=mn, method_type="builtin")
                model.auth_methods[mid] = m
                method_by_name[mn] = m
            method_ids.append(m.id if m else _stable_id(mn))

        source_ids = []
        source_names = svc.get("authSources", [])
        for sn in source_names:
            s = source_by_name.get(sn)
            if s is None and sn:
                msg = f"AuthSource '{sn}' not found (referenced in Service '{svc['name']}') — using placeholder"
                logger.warning("Unresolved reference: %s", msg)
                model.warnings.append(msg)
                sid = _stable_id(sn)
                s = AuthSource(
                    id=sid, name=sn, source_type="builtin", description="Built-in source (not in API response)"
                )
                model.auth_sources[sid] = s
                source_by_name[sn] = s
            source_ids.append(s.id if s else _stable_id(sn))

        rm_names = svc.get("roleMappings", [])
        rm_name = rm_names[0] if rm_names else ""
        rm = rm_by_name.get(rm_name)
        if rm_name and rm is None:
            msg = f"RoleMappingPolicy '{rm_name}' not found (referenced in Service '{svc['name']}') — using placeholder"
            logger.warning("Unresolved reference: %s", msg)
            model.warnings.append(msg)
        rm_id = rm.id if rm else _stable_id(rm_name)

        ep_names = svc.get("enfPolicies", [])
        ep_name = ep_names[0] if ep_names else ""
        ep = ep_by_name.get(ep_name)
        if ep_name and ep is None:
            msg = f"EnforcementPolicy '{ep_name}' not found (referenced in Service '{svc['name']}') — using placeholder"
            logger.warning("Unresolved reference: %s", msg)
            model.warnings.append(msg)
        ep_id = ep.id if ep else _stable_id(ep_name)

        model.services[svid] = Service(
            id=svid,
            name=svc["name"],
            description=svc.get("description", ""),
            service_type=svc.get("serviceType", "RADIUS"),
            match=match_expr,
            authentication=ServiceAuthentication(
                method_ids=method_ids,
                method_names=method_names,
                source_ids=source_ids,
                source_names=source_names,
            ),
            role_mapping_policy_id=rm_id,
            role_mapping_policy_name=rm_name,
            enforcement_policy_id=ep_id,
            enforcement_policy_name=ep_name,
        )

    return model
