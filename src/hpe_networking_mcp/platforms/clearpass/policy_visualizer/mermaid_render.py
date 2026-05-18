"""Mermaid renderer for :class:`FlowGraph` objects.

The compiled :class:`~.flow_graph.FlowGraph` is platform-neutral (nodes
+ edges + optional simulation result). This module converts it into
ready-to-paste Mermaid source so the AI client doesn't have to assemble
declarations on its own — historically the AI inlines multiple node
declarations on a single source line, which Mermaid's per-line shape
parser refuses to parse. By emitting the source server-side we eliminate
that whole class of bug (issue #356).

Output shape:

    {
        "sections": [
            {"title": "Block A — Service intake", "code": "flowchart LR\\n..."},
            {"title": "Block B — Role mapping (...)", "code": "flowchart LR\\n..."},
            {"title": "Block C — Enforcement (...)", "code": "flowchart LR\\n..."},
        ],
        "simulated": bool,
    }

Each ``code`` is a complete Mermaid block ready to embed in a
`````mermaid ... ````` fence. Every node is on its own line,
every edge is on its own line, every label is wrapped in double quotes,
internal double quotes in labels are demoted to single quotes.

Sections are always three (A / B / C) for consistency. Blocks are
omitted only when they contain no nodes (e.g. RADIUS_PROXY skips
role-mapping entirely).
"""

from __future__ import annotations

from .flow_graph import FlowEdge, FlowGraph, FlowNode

# Each node type maps to (open, close) Mermaid shape delimiters. Labels
# always go inside double quotes inside the shape — Mermaid's bare-label
# parser stumbles on ":" "=" "+" "&" "|" "'" "(" ")" which are common in
# ClearPass condition predicates.
_NODE_SHAPE: dict[str, tuple[str, str]] = {
    "start": ("([", "])"),
    "process": ("[", "]"),
    "decision": ("{", "}"),
    "action": ("[/", "/]"),
    "end": ("(((", ")))"),
}

# Edge label → Mermaid arrow syntax. CONTINUE uses a dotted line to
# visually distinguish evaluate-all chaining from first-applicable
# fall-through. The "PASS" key is the auth → role-mapping edge label
# (authentication passed) — bandit B105 misreads it as a hardcoded
# credential, suppress on the offending line.
_EDGE_FORMAT: dict[str, str] = {
    "": "{f} --> {t}",
    "YES": "{f} -->|YES| {t}",
    "NO": "{f} -->|NO| {t}",
    "FAIL": "{f} -->|FAIL| {t}",
    "PASS": "{f} -->|PASS| {t}",  # nosec B105 — Mermaid edge label, not a credential
    "CONTINUE": "{f} -. CONTINUE .-> {t}",
}

# classDefs emitted in every block. The first three are the styling for
# end-node ALLOW/DENY/skip; the second three are for simulation
# highlighting (only emitted when flow.simulation is non-None).
_BASE_CLASSDEFS = (
    "classDef deny fill:#fee,stroke:#c33,stroke-width:2px;",
    "classDef skip fill:#eee,stroke:#999,stroke-width:1px;",
)
_SIM_CLASSDEFS = (
    "classDef sim_match fill:#dfd,stroke:#3a3,stroke-width:3px;",
    "classDef sim_skip fill:#222,color:#555,stroke:#444;",
    "classDef sim_unknown fill:#ffd,stroke:#aa6,stroke-width:2px;",
)


def _escape_label(text: str) -> str:
    """Sanitize a label for safe embedding in a Mermaid double-quoted label.

    Demotes internal double-quotes to single quotes (Mermaid's label
    quote syntax is `"..."` — embedded `"` would close the quote early)
    and HTML-escapes the `<` `>` chars that Mermaid would otherwise
    interpret as HTML tags.
    """
    return text.replace('"', "'").replace("<", "&lt;").replace(">", "&gt;")


def _node_classes(node: FlowNode, simulated: bool) -> list[str]:
    """Pick the visual classes that apply to a given node.

    Order of priority for end nodes (only one class wins): the
    simulation class if a simulation context was supplied, else the
    deny/skip class. Non-end / non-decision nodes get no class.
    Simulation classes only apply to decision nodes.
    """
    classes: list[str] = []
    if simulated and node.type == "decision":
        if node.simulation_match is True:
            classes.append("sim_match")
        elif node.simulation_match is False:
            classes.append("sim_skip")
        elif node.simulation_match is None:
            # Only mark unknown if the simulator actually consulted this
            # node — `None` is also the initial value before simulation.
            # We can't tell from a single node, so we leave it default
            # rather than yellow-flag every node in a non-simulated graph.
            pass
    if node.type == "end":
        s = node.short_label
        if "DENY" in s or "Auth Failed" in s:
            classes.append("deny")
        elif s.startswith("Skip"):
            classes.append("skip")
    return classes


def _format_node_line(node: FlowNode, simulated: bool) -> str:
    """Format one node declaration on its own source line."""
    open_, close = _NODE_SHAPE.get(node.type, ("[", "]"))
    label = _escape_label(node.short_label)
    line = f'    {node.id}{open_}"{label}"{close}'
    classes = _node_classes(node, simulated)
    if classes:
        # Mermaid only supports one ::: class per node; pick the
        # highest-priority one — sim styles win over deny/skip.
        line += ":::" + classes[0]
    return line


def _format_edge_line(edge: FlowEdge) -> str:
    tmpl = _EDGE_FORMAT.get(edge.label, "{f} --> {t}")
    return "    " + tmpl.format(f=edge.from_id, t=edge.to_id)


def _section_for_id(node_id: str, sid: str) -> str:
    """Bucket a node ID into section A (intake), B (role mapping), or C (enforcement)."""
    suffix = node_id[len(sid) + 2 :] if node_id.startswith(f"{sid}__") else node_id
    if suffix in ("start", "match", "no_match", "auth", "auth_fail"):
        return "A"
    if suffix.startswith("rm_") or suffix == "no_role":
        return "B"
    if suffix.startswith("enf_"):
        return "C"
    return "A"


def _render_block(
    title: str,
    nodes: list[FlowNode],
    edges: list[FlowEdge],
    simulated: bool,
    cross_section_targets: dict[str, str] | None = None,
) -> str:
    """Render one section as a complete Mermaid block.

    ``cross_section_targets`` maps node IDs that live in other sections
    to a stub label like "→ Block C" — these get rendered as plain
    rectangle stubs at the destination of cross-section edges so the
    reader sees where the flow continues.
    """
    lines: list[str] = ["flowchart LR"]
    lines.append("    %%{init: {'flowchart': {'nodeSpacing': 30, 'rankSpacing': 50, 'curve': 'basis'}}}%%")
    lines.append("")
    lines.append("    %% --- nodes ---")
    for node in nodes:
        lines.append(_format_node_line(node, simulated))

    # Emit any cross-section stub nodes (one per target ID)
    cross_section_targets = cross_section_targets or {}
    for stub_id, stub_label in cross_section_targets.items():
        safe = _escape_label(stub_label)
        lines.append(f'    {stub_id}["{safe}"]')

    lines.append("")
    lines.append("    %% --- edges ---")
    for edge in edges:
        lines.append(_format_edge_line(edge))

    lines.append("")
    for cd in _BASE_CLASSDEFS:
        lines.append(f"    {cd}")
    if simulated:
        for cd in _SIM_CLASSDEFS:
            lines.append(f"    {cd}")

    return "\n".join(lines)


def format_mermaid(flow: FlowGraph) -> dict:
    """Render a :class:`FlowGraph` as three Mermaid section blocks.

    Returns the dict shape documented at the top of this module. Every
    declaration is emitted on its own source line and every label is
    wrapped in double quotes so Mermaid's per-line parser can't trip on
    AI assembly errors.

    Empty sections are omitted from the result — RADIUS_PROXY services
    skip role mapping entirely, for instance, and policies without an
    attached EP skip enforcement.
    """
    simulated = flow.simulation is not None
    sid = flow.service_id

    # Bucket nodes by section
    nodes_by_section: dict[str, list[FlowNode]] = {"A": [], "B": [], "C": []}
    section_of: dict[str, str] = {}
    for node in flow.nodes:
        sect = _section_for_id(node.id, sid)
        nodes_by_section[sect].append(node)
        section_of[node.id] = sect

    # Bucket edges by their FROM section; cross-section edges produce a stub
    edges_by_section: dict[str, list[FlowEdge]] = {"A": [], "B": [], "C": []}
    stubs_by_section: dict[str, dict[str, str]] = {"A": {}, "B": {}, "C": {}}
    for edge in flow.edges:
        src_sect = section_of.get(edge.from_id, "A")
        dst_sect = section_of.get(edge.to_id, "A")
        if src_sect == dst_sect:
            edges_by_section[src_sect].append(edge)
            continue
        # Cross-section: rewrite the destination to a stub at the source section
        stub_id = f"__stub_to_{dst_sect}_{edge.to_id}"
        stubs_by_section[src_sect][stub_id] = f"→ Block {dst_sect}"
        edges_by_section[src_sect].append(
            FlowEdge(from_id=edge.from_id, to_id=stub_id, label=edge.label, reason=edge.reason)
        )

    section_titles = {
        "A": "Block A — Service intake (start → match → auth)",
        "B": "Block B — Role mapping",
        "C": "Block C — Enforcement (decision → access)",
    }

    sections: list[dict[str, str]] = []
    for key in ("A", "B", "C"):
        if not nodes_by_section[key]:
            continue
        code = _render_block(
            section_titles[key],
            nodes_by_section[key],
            edges_by_section[key],
            simulated,
            cross_section_targets=stubs_by_section[key],
        )
        sections.append({"title": section_titles[key], "code": code})

    return {"sections": sections, "simulated": simulated}
