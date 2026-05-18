"""Flowchart compiler for a single ClearPass policy service.

:func:`compile_service` walks a :class:`~.policy_model.Service` (with
its cross-referenced role-mapping and enforcement policies) and emits a
:class:`FlowGraph` of nodes + edges ready for a frontend to render
(Mermaid, Graphviz, React, etc.).

Semantics preserved:

- **First-applicable**: role-mapping or enforcement chain stops at the
  first matching rule.
- **Evaluate-all**: every matching action runs; subsequent decisions
  are wired with a ``CONTINUE`` edge from the prior action.
- **Implicit deny**: if no rule matches and no default exists, a
  terminating "Access: DENY (implicit)" node is added.
- **RADIUS_PROXY services**: skip authentication + role-mapping;
  service-match YES wires directly into the enforcement chain.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

from .conditions import evaluate, expr_to_compact_label, expr_to_node_label
from .policy_model import (
    ApplyProfiles,
    EnforcementProfile,
    PolicyModel,
    Service,
    SetRole,
)

NodeType = Literal["start", "process", "decision", "action", "end"]
EdgeLabel = Literal["", "YES", "NO", "FAIL", "PASS", "CONTINUE"]


@dataclass
class FlowNode:
    id: str
    type: NodeType
    label: str
    # short_label is a compact single-line summary of the same content as
    # ``label`` — diagram renderers (Mermaid, Graphviz) should prefer this
    # for the visual node text to keep dense policies legible, and fall
    # back to ``label`` for inspector/tooltip text where verbosity is fine.
    # Populated by compile_service() for decision nodes; for non-decision
    # nodes it's left equal to ``label``.
    short_label: str = ""
    trace_rule_id: str = ""
    sub_label: str = ""
    rank_group: str = ""
    # Populated when compile_service is called with simulated_attributes.
    # ``True``  → the rule fires under the simulated context
    # ``False`` → the rule's condition is contradicted
    # ``None``  → cannot evaluate (at least one referenced attribute missing
    #             from the context — caller MUST NOT present this as a
    #             confident outcome)
    # Absent (when no simulation was requested) — left as None.
    simulation_match: bool | None = None

    def __post_init__(self) -> None:
        if not self.short_label:
            self.short_label = self.label


@dataclass
class SimulationOutcome:
    """Result of a what-if simulation against a chosen ``simulated_attributes`` context.

    Populated only when :func:`compile_service` is called with a
    non-empty ``simulated_attributes`` arg. Distinct from a per-node
    ``simulation_match`` because it summarizes the END-TO-END outcome:
    which role-mapping rules matched (and so what roles were assigned),
    which enforcement rule was the first-applicable winner, what
    profiles got applied, and what the resulting access decision was.

    The ``status`` field is the most important — three values:

    - ``"resolved"`` — every consulted predicate could be evaluated;
      ``matching_enforcement_rule`` / ``access_decision`` are authoritative.
    - ``"uncertain"`` — at least one predicate in the consulted chain
      returned None (unknown attribute). The simulator cannot make a
      confident claim; callers MUST present this as
      "need attribute X, Y, Z to resolve" rather than naming an outcome.
    - ``"no_match"`` — every rule's condition resolved to False; the
      access decision is the policy's default branch.
    """

    requested_attributes: dict[str, str | list[str]]
    status: str  # "resolved" | "uncertain" | "no_match"
    matching_role_mapping_rules: list[str]
    resulting_roles: list[str]
    matching_enforcement_rule: str | None
    applied_profiles: list[str]
    access_decision: str  # "ALLOW" | "DENY" | "UNKNOWN"
    unknown_attributes: list[str]
    notes: list[str]


@dataclass
class FlowEdge:
    from_id: str
    to_id: str
    label: EdgeLabel = ""
    reason: str = ""  # human-readable cause for conditional edges (e.g. "usernotfound")


@dataclass
class FlowGraph:
    service_id: str
    service_name: str
    service_type: str = "RADIUS"
    nodes: list[FlowNode] = field(default_factory=list)
    edges: list[FlowEdge] = field(default_factory=list)
    simulation: SimulationOutcome | None = None

    def add_node(self, node: FlowNode) -> FlowNode:
        self.nodes.append(node)
        return node

    def add_edge(self, from_id: str, to_id: str, label: EdgeLabel = "", reason: str = "") -> None:
        self.edges.append(FlowEdge(from_id=from_id, to_id=to_id, label=label, reason=reason))


_DENY_PROFILE_TYPES = {"radius_reject", "tacacs_other", "generic_reject"}
_DENY_ACTIONS = {"deny", "reject", "drop"}
_POST_AUTH_PROFILE_TYPE = "post_auth"
# Real MAC-auth + MPSK enforcement rules combine ONE RADIUS Accept (the
# access decision) with several Post_Authentication side-effects
# (endpoint updates, SDWAN role pushes, etc.). The side-effects must
# never contribute to the rule's ALLOW/DENY label — they happen
# regardless of whether access was granted.


def _is_deny(
    profile_ids: list[str],
    profile_names: list[str],
    profiles: dict[str, EnforcementProfile],
) -> bool:
    """Return True if any profile in the list represents an explicit deny.

    Post-authentication profiles are skipped — they're side-effects, not
    access decisions. Unknown / missing action is NOT treated as deny —
    we require an explicit signal. Falling back to a name heuristic
    requires a strong substring match.

    Resolution order (per profile):
    1. ``profile_type == "post_auth"`` → skip (side-effect, not an
       access decision).
    2. ``profile_type`` in ``{radius_reject, tacacs_other,
       generic_reject}`` → explicit deny.
    3. ``action`` in ``{deny, reject, drop}`` → explicit deny.
    4. Profile not present in the model (placeholder): only count as
       deny if the profile NAME starts with ``[Deny`` or equals/contains
       a strong deny token. ClearPass's built-in deny profile is named
       ``[Deny Access Profile]``.
    """
    for pid, name in zip(profile_ids, profile_names, strict=False):
        profile = profiles.get(pid)
        if profile is not None:
            if profile.profile_type == _POST_AUTH_PROFILE_TYPE:
                continue
            if profile.profile_type in _DENY_PROFILE_TYPES:
                return True
            if profile.action and profile.action.lower() in _DENY_ACTIONS:
                return True
            continue
        lowered = name.lower()
        if "deny access profile" in lowered or lowered.startswith("[deny"):
            return True
    return False


def _profiles_label(profile_names: list[str]) -> str:
    return ", ".join(profile_names) if profile_names else "Apply profiles"


def compile_service(
    service: Service,
    model: PolicyModel,
    simulated_attributes: dict[str, str | list[str]] | None = None,
) -> FlowGraph:
    """Compile one service into a :class:`FlowGraph`.

    When ``simulated_attributes`` is provided, the resulting graph also
    carries per-decision-node ``simulation_match`` flags and a
    top-level :class:`SimulationOutcome` describing the end-to-end
    what-if result. See :class:`SimulationOutcome` for the
    uncertainty-first contract.
    """
    flow = FlowGraph(service_id=service.id, service_name=service.name, service_type=service.service_type)
    sid = service.id

    # -----------------------------------------------------------------------
    # Start
    # -----------------------------------------------------------------------
    start = flow.add_node(FlowNode(id=f"{sid}__start", type="start", label=service.name))

    # -----------------------------------------------------------------------
    # Service match decision
    # -----------------------------------------------------------------------
    match_label = expr_to_node_label(service.match)
    match_short = expr_to_compact_label(service.match)
    svc_match = flow.add_node(
        FlowNode(
            id=f"{sid}__match",
            type="decision",
            label=f"Service Match?\n{match_label}",
            short_label=f"Service Match? {match_short}",
            trace_rule_id=f"{sid}__match",
        )
    )
    flow.add_edge(start.id, svc_match.id)

    no_match_end = flow.add_node(
        FlowNode(
            id=f"{sid}__no_match",
            type="end",
            label="Skip\n(no match)",
        )
    )
    flow.add_edge(svc_match.id, no_match_end.id, "NO")

    # -----------------------------------------------------------------------
    # Build enforcement chain (shared by all role paths)
    # -----------------------------------------------------------------------
    ep = model.enforcement_policies.get(service.enforcement_policy_id)
    if ep is None:
        ep = next(
            (v for v in model.enforcement_policies.values() if v.name == service.enforcement_policy_name),
            None,
        )

    # First node of the enforcement chain (all role paths will point here)
    enf_entry_id: str

    if ep is None or not ep.rules:
        deny_end = flow.add_node(
            FlowNode(
                id=f"{sid}__enf_no_policy",
                type="end",
                label="Access: DENY\n(no enforcement policy)",
            )
        )
        enf_entry_id = deny_end.id
    else:
        evaluate_all_enf = ep.rule_combine_algo == "evaluate-all"
        first_enf_id = f"{sid}__enf_rule_0"
        enf_entry_id = first_enf_id

        prev_enf_id: str | None = None
        prev_enf_action_id: str | None = None
        enf_rules = list(ep.rules)
        for i, rule in enumerate(enf_rules):
            is_last_enf = i == len(enf_rules) - 1
            cond_label = expr_to_node_label(rule.when)
            cond_short = expr_to_compact_label(rule.when)
            dec = flow.add_node(
                FlowNode(
                    id=f"{sid}__enf_rule_{rule.index}",
                    type="decision",
                    label=cond_label,
                    short_label=cond_short,
                    trace_rule_id=rule.id,
                    rank_group="enf_chain",
                )
            )
            if prev_enf_id is not None:
                flow.add_edge(prev_enf_id, dec.id, "NO")
            # evaluate-all: wire previous action → this decision via CONTINUE
            if evaluate_all_enf and prev_enf_action_id is not None:
                flow.add_edge(prev_enf_action_id, dec.id, "CONTINUE")
            prev_enf_action_id = None

            # YES → action
            if isinstance(rule.then, ApplyProfiles):
                names = rule.then.profile_names
                deny = _is_deny(rule.then.profile_ids, names, model.enforcement_profiles)
                action = flow.add_node(
                    FlowNode(
                        id=f"{sid}__enf_action_{rule.index}",
                        type="action",
                        label=_profiles_label(names),
                        trace_rule_id=rule.id,
                    )
                )
                flow.add_edge(dec.id, action.id, "YES")
                if not evaluate_all_enf or is_last_enf:
                    # first-applicable, or last rule in evaluate-all: terminate
                    access = "DENY" if deny else "ALLOW"
                    end_node = flow.add_node(
                        FlowNode(
                            id=f"{sid}__enf_end_{rule.index}",
                            type="end",
                            label=f"Access: {access}",
                        )
                    )
                    flow.add_edge(action.id, end_node.id)
                else:
                    # evaluate-all non-last: stash for CONTINUE edge on next iteration
                    prev_enf_action_id = action.id

            prev_enf_id = dec.id

        # Enforcement default (last NO path)
        if ep.default is not None and isinstance(ep.default, ApplyProfiles):
            def_names = ep.default.profile_names
            deny = _is_deny(ep.default.profile_ids, def_names, model.enforcement_profiles)
            def_action = flow.add_node(
                FlowNode(
                    id=f"{sid}__enf_default_action",
                    type="action",
                    label=f"Default:\n{_profiles_label(def_names)}",
                )
            )
            flow.add_edge(prev_enf_id, def_action.id, "NO")  # type: ignore[arg-type]
            access = "DENY" if deny else "ALLOW"
            def_end = flow.add_node(
                FlowNode(
                    id=f"{sid}__enf_default_end",
                    type="end",
                    label=f"Access: {access}\n(default)",
                )
            )
            flow.add_edge(def_action.id, def_end.id)
        elif prev_enf_id:
            implicit_deny = flow.add_node(
                FlowNode(
                    id=f"{sid}__enf_implicit_deny",
                    type="end",
                    label="Access: DENY\n(implicit)",
                )
            )
            flow.add_edge(prev_enf_id, implicit_deny.id, "NO")

    # -----------------------------------------------------------------------
    # Auth + role-mapping chains (skipped for RADIUS_PROXY)
    # -----------------------------------------------------------------------
    if service.service_type == "RADIUS_PROXY":
        flow.add_edge(svc_match.id, enf_entry_id, "YES")
    else:
        # --- Authentication process ---
        method_names = service.authentication.method_names
        source_names = service.authentication.source_names
        auth_label = "Authenticate"
        if method_names:
            auth_label += "\nMethods: " + ", ".join(method_names)
        if source_names:
            auth_label += "\nSources: " + ", ".join(source_names)

        auth_node = flow.add_node(FlowNode(id=f"{sid}__auth", type="process", label=auth_label))
        flow.add_edge(svc_match.id, auth_node.id, "YES")

        auth_fail = flow.add_node(
            FlowNode(
                id=f"{sid}__auth_fail",
                type="end",
                label="Auth Failed",
                sub_label="Access: DENY",
            )
        )
        flow.add_edge(auth_node.id, auth_fail.id, "FAIL")

        # --- Role mapping decision chain → all YES branches converge to enf_entry_id ---
        rm = model.role_mapping_policies.get(service.role_mapping_policy_id)
        if rm is None:
            rm = next(
                (v for v in model.role_mapping_policies.values() if v.name == service.role_mapping_policy_name),
                None,
            )

        current_tail = auth_node.id
        current_label: EdgeLabel = "PASS"

        if rm is not None:
            evaluate_all_rm = rm.rule_combine_algo == "evaluate-all"
            prev_rm_action_id: str | None = None
            rm_rules = list(rm.rules)
            for i, rule in enumerate(rm_rules):
                is_last_rm = i == len(rm_rules) - 1
                cond_label = expr_to_node_label(rule.when)
                cond_short = expr_to_compact_label(rule.when)
                dec = flow.add_node(
                    FlowNode(
                        id=f"{sid}__rm_rule_{rule.index}",
                        type="decision",
                        label=cond_label,
                        short_label=cond_short,
                        trace_rule_id=rule.id,
                        rank_group="rm_chain",
                    )
                )
                flow.add_edge(current_tail, dec.id, current_label)
                if evaluate_all_rm and prev_rm_action_id is not None:
                    flow.add_edge(prev_rm_action_id, dec.id, "CONTINUE")
                prev_rm_action_id = None

                if isinstance(rule.then, SetRole):
                    role_action = flow.add_node(
                        FlowNode(
                            id=f"{sid}__rm_action_{rule.index}",
                            type="action",
                            label=f"Set Role:\n{rule.then.role_name}",
                            trace_rule_id=rule.id,
                        )
                    )
                    flow.add_edge(dec.id, role_action.id, "YES")
                    if not evaluate_all_rm or is_last_rm:
                        flow.add_edge(role_action.id, enf_entry_id)
                    else:
                        prev_rm_action_id = role_action.id

                current_tail = dec.id
                current_label = "NO"

            # Default role → enforcement
            if rm.default is not None:
                def_role = flow.add_node(
                    FlowNode(
                        id=f"{sid}__rm_default",
                        type="action",
                        label=f"Default Role:\n{rm.default.role_name}",
                    )
                )
                flow.add_edge(current_tail, def_role.id, current_label)
                flow.add_edge(def_role.id, enf_entry_id)
            else:
                no_role_end = flow.add_node(
                    FlowNode(
                        id=f"{sid}__no_role",
                        type="end",
                        label="Access: DENY\n(no role matched)",
                    )
                )
                flow.add_edge(current_tail, no_role_end.id, current_label)
        else:
            # No role mapping — go straight to enforcement
            flow.add_edge(current_tail, enf_entry_id, current_label)

    # Run what-if simulation against the supplied context, if any.
    if simulated_attributes is not None:
        _apply_simulation(service, model, flow, simulated_attributes)

    return flow


# ---------------------------------------------------------------------------
# What-if simulation
# ---------------------------------------------------------------------------


def _collect_unknown_attrs(expr, context: dict[str, str | list[str]]) -> set[str]:
    """Walk a BooleanExpr and return the set of attribute paths referenced
    that aren't present in ``context`` — these are what the caller needs
    to provide to resolve an "uncertain" simulation outcome.
    """
    from .conditions import And, Not, Or, Predicate, _attribute_path

    out: set[str] = set()
    if expr is None:
        return out
    if isinstance(expr, Predicate):
        path = _attribute_path(expr)
        if path and path not in context:
            out.add(path)
        return out
    if isinstance(expr, (And, Or)):
        for operand in expr.operands:
            out |= _collect_unknown_attrs(operand, context)
        return out
    if isinstance(expr, Not):
        return _collect_unknown_attrs(expr.operand, context)
    return out


def _set_node_match(flow: FlowGraph, node_id: str, result: bool | None) -> None:
    """Set ``simulation_match`` on the decision node with the given ID."""
    for node in flow.nodes:
        if node.id == node_id:
            node.simulation_match = result
            return


def _apply_simulation(
    service: Service,
    model: PolicyModel,
    flow: FlowGraph,
    context: dict[str, str | list[str]],
) -> None:
    """Run the what-if simulation and attach :class:`SimulationOutcome` to the flow.

    Strict uncertainty contract: if any consulted predicate evaluates
    to ``None``, the outcome status is ``"uncertain"`` and the access
    decision is ``"UNKNOWN"``. Never produce a confident outcome from a
    partial evaluation.
    """
    sid = service.id
    unknown_attrs: set[str] = set()
    notes: list[str] = []

    # ---- Service match
    svc_match_result = evaluate(service.match, context)
    _set_node_match(flow, f"{sid}__match", svc_match_result)
    if svc_match_result is None:
        unknown_attrs |= _collect_unknown_attrs(service.match, context)
        flow.simulation = SimulationOutcome(
            requested_attributes=dict(context),
            status="uncertain",
            matching_role_mapping_rules=[],
            resulting_roles=[],
            matching_enforcement_rule=None,
            applied_profiles=[],
            access_decision="UNKNOWN",
            unknown_attributes=sorted(unknown_attrs),
            notes=["Service match condition is uncertain — provide the missing attribute(s) and re-simulate."],
        )
        return
    if svc_match_result is False:
        flow.simulation = SimulationOutcome(
            requested_attributes=dict(context),
            status="no_match",
            matching_role_mapping_rules=[],
            resulting_roles=[],
            matching_enforcement_rule=None,
            applied_profiles=[],
            access_decision="UNKNOWN",
            unknown_attributes=[],
            notes=["Service match returned False — this service does not apply to the simulated request."],
        )
        return

    # ---- Role mapping (skipped for RADIUS_PROXY)
    matching_rm_rules: list[str] = []
    resulting_roles: list[str] = []
    if service.service_type != "RADIUS_PROXY":
        rm = model.role_mapping_policies.get(service.role_mapping_policy_id)
        if rm is None:
            rm = next(
                (v for v in model.role_mapping_policies.values() if v.name == service.role_mapping_policy_name),
                None,
            )
        if rm is not None:
            evaluate_all_rm = rm.rule_combine_algo == "evaluate-all"
            rm_uncertain = False
            for rule in rm.rules:
                result = evaluate(rule.when, context)
                _set_node_match(flow, f"{sid}__rm_rule_{rule.index}", result)
                if result is True:
                    matching_rm_rules.append(rule.id)
                    if (
                        isinstance(rule.then, SetRole)
                        and rule.then.role_name
                        and rule.then.role_name not in resulting_roles
                    ):
                        resulting_roles.append(rule.then.role_name)
                    if not evaluate_all_rm:
                        break
                elif result is None:
                    rm_uncertain = True
                    unknown_attrs |= _collect_unknown_attrs(rule.when, context)
                    if not evaluate_all_rm:
                        break
            # Apply the default role only when no rule matched AND the
            # chain was deterministic — never silently apply a default
            # when uncertainty exists earlier in the chain.
            if not matching_rm_rules and not rm_uncertain and rm.default is not None and rm.default.role_name:
                resulting_roles.append(rm.default.role_name)
            if rm_uncertain:
                notes.append("Role mapping chain has uncertain rule(s); resulting role set may be incomplete.")

    # ---- Build the enforcement-context by merging resolved roles into Tips:Role.
    # If the operator also passed Tips:Role explicitly, union both sets.
    ep_context: dict[str, str | list[str]] = dict(context)
    if resulting_roles:
        explicit = ep_context.get("Tips:Role")
        if isinstance(explicit, list):
            ep_context["Tips:Role"] = list({*explicit, *resulting_roles})
        elif isinstance(explicit, str):
            ep_context["Tips:Role"] = list({explicit, *resulting_roles})
        else:
            ep_context["Tips:Role"] = list(resulting_roles)

    # ---- Enforcement
    matching_ep_rule: str | None = None
    applied_profiles: list[str] = []
    ep = model.enforcement_policies.get(service.enforcement_policy_id)
    if ep is None:
        ep = next(
            (v for v in model.enforcement_policies.values() if v.name == service.enforcement_policy_name),
            None,
        )

    ep_uncertain = False
    if ep is None or not ep.rules:
        flow.simulation = SimulationOutcome(
            requested_attributes=dict(context),
            status="no_match",
            matching_role_mapping_rules=matching_rm_rules,
            resulting_roles=resulting_roles,
            matching_enforcement_rule=None,
            applied_profiles=[],
            access_decision="DENY",
            unknown_attributes=sorted(unknown_attrs),
            notes=notes + ["No enforcement policy attached — service implicitly denies."],
        )
        return

    evaluate_all_ep = ep.rule_combine_algo == "evaluate-all"
    for rule in ep.rules:
        result = evaluate(rule.when, ep_context)
        _set_node_match(flow, f"{sid}__enf_rule_{rule.index}", result)
        if result is True:
            if not evaluate_all_ep:
                matching_ep_rule = rule.id
                if isinstance(rule.then, ApplyProfiles):
                    applied_profiles = list(rule.then.profile_names)
                break
            # evaluate-all: collect all matching rules' profiles, no break
            if matching_ep_rule is None:
                matching_ep_rule = rule.id  # report the first matched as the "primary" winner
            if isinstance(rule.then, ApplyProfiles):
                applied_profiles.extend(p for p in rule.then.profile_names if p not in applied_profiles)
        elif result is None:
            ep_uncertain = True
            unknown_attrs |= _collect_unknown_attrs(rule.when, ep_context)
            if not evaluate_all_ep:
                # In first-applicable mode, hitting an uncertain rule
                # before any True means we can't determine the winner.
                notes.append(
                    f"Enforcement rule {rule.index} is uncertain — cannot determine the first-applicable "
                    "winner without resolving it."
                )
                break

    # Default branch only when chain was deterministic + no rule matched
    if (
        matching_ep_rule is None
        and not ep_uncertain
        and ep.default is not None
        and isinstance(ep.default, ApplyProfiles)
        and ep.default.profile_names
    ):
        applied_profiles = list(ep.default.profile_names)
        matching_ep_rule = f"{ep.id}__default"

    # ---- Determine outcome
    if ep_uncertain or matching_ep_rule is None and unknown_attrs:
        status = "uncertain"
        access = "UNKNOWN"
    elif matching_ep_rule is None:
        status = "no_match"
        access = "DENY"  # implicit deny when nothing matched and no default
        notes.append("No enforcement rule matched and no default profile — implicit deny.")
    else:
        status = "resolved"
        # Resolve profile names → ids to apply _is_deny semantics
        profile_ids: list[str] = []
        for pname in applied_profiles:
            match = next((p for p in model.enforcement_profiles.values() if p.name == pname), None)
            profile_ids.append(match.id if match else "")
        access = "DENY" if _is_deny(profile_ids, applied_profiles, model.enforcement_profiles) else "ALLOW"

    if unknown_attrs and status == "uncertain":
        notes.append(
            f"Resolve {len(unknown_attrs)} missing attribute(s) and re-simulate: {', '.join(sorted(unknown_attrs))}"
        )

    flow.simulation = SimulationOutcome(
        requested_attributes=dict(context),
        status=status,
        matching_role_mapping_rules=matching_rm_rules,
        resulting_roles=resulting_roles,
        matching_enforcement_rule=matching_ep_rule,
        applied_profiles=applied_profiles,
        access_decision=access,
        unknown_attributes=sorted(unknown_attrs),
        notes=notes,
    )
