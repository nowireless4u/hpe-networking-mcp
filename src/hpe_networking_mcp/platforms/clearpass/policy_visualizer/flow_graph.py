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

from .conditions import expr_to_compact_label, expr_to_node_label
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

    def __post_init__(self) -> None:
        if not self.short_label:
            self.short_label = self.label


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


def compile_service(service: Service, model: PolicyModel) -> FlowGraph:
    """Compile one service into a :class:`FlowGraph`."""
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

    return flow
