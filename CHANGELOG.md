# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [3.1.7.0] - 2026-05-19

**Minor — Central scope visualizer skill + symmetric `central_get_committed_config` tool.** Operator's first try at `central_get_scope_diagram` produced a sprawling unreadable wall — devices and device-groups all enumerated as separate circle nodes. The structured `central_get_scope_tree` output already has everything needed for the screenshot-quality visualizations operators want (per-scope resource counts, persona breakdowns, device-type rollups) — there was just no discoverable runbook telling the AI to use that path instead of the raw Mermaid string.

### New skill: `central-scope-visualizer`

RF-check-style runbook for Central scope hierarchy visualization. Surfaces from `skills_list` in code mode so the AI has a discoverable entry point. Gives as much data as possible (whole tree + per-scope committed/effective config + device inventory) and lets the AI build whatever diagram fits the request — top-level overview, drilled-in site, per-scope inspector, committed-vs-effective diff.

Operator-output rules pinned: aggregate by default (don't enumerate 17 devices as 17 boxes — group by type with counts), resource counts on every node, never expose raw numeric scope IDs, color-code by node type, legend at the top. Doesn't blindly call `central_get_scope_diagram` — that tool is now noted as deprecated for visualization, kept only as text-mode fallback.

### New tool: `central_get_committed_config(scope_id, persona?, include_details=True)`

Symmetric sibling of `central_get_effective_config`. Returns what's COMMITTED at a scope (no parent-scope inheritance rollup) with the same per-resource shape as `effective_resources` so the two views diff cleanly side-by-side. Useful when the operator asks "what did the parent contribute vs what was added at this scope?" — call both and compare. The legacy `central_get_scope_resources` does the same job functionally but the asymmetric naming made the relationship non-obvious to operators (and to AIs reading the catalog).

Live-verified shape against HOME scope (52 committed resources across ACCESS_SWITCH / CAMPUS_AP personas). Returns empty `committed_resources` list — not an error — when an organizational-container scope has nothing directly assigned.

## [3.1.6.0] - 2026-05-19

**Minor — ClearPass policy visualizer fix combine-algorithm mislabeling + add cross-platform Aruba role resolution (#360); response envelope no longer drops bare-string returns from invoke_tool dispatch (#362).**

### Envelope bug — bare-string returns silently lost via `<platform>_invoke_tool` (#362)

Operator dispatched `central_get_scope_diagram` via `central_invoke_tool` and got `{ok: True, data: None}` — the Mermaid source was silently lost. Root cause: `_payload_from_content` in the response envelope only recovered JSON-parseable text blocks (`json.loads(block.text)` raises on a Mermaid string → loop `continue`s → returns None). Affected EVERY string-returning tool dispatched through the meta-tool path, including the very common `-> dict | list | str` error-fallback case where the AI silently lost `"Error: ..."` messages.

Fixed in `middleware/response_envelope.py:_payload_from_content`: two-pass recovery — first pass finds a JSON-parseable block (existing behaviour, preserves dict/list payloads), fallback returns the first non-empty text block as a raw string. Bare-string returns now survive. Unit tests pin the contract.

### Operator's original v3.1.5.0 visualizer feedback (#360)

Custom widget on v3.1.5.0 hardcoded "stop on match" on every role-mapping rule row even though the policy is evaluate-all (rules continue, devices accumulate multiple roles). Also: there was no way to drill into what an Aruba role actually does — `WLAN-NIGHT-NIGHT` was just a name. Both fixed.

### Combine algorithm surfaced as structured response fields

`clearpass_compile_policy_flow` returns two new top-level fields:

- `role_mapping_combine` — `"first-applicable"` / `"evaluate-all"` / `None`
- `enforcement_combine` — same domain

Mermaid section titles now include the combine algorithm: *"Block B — Role mapping (evaluate-all — rules continue, multiple actions accumulate)"* / *"Block C — Enforcement (first-applicable — first matching rule wins)"*. AI clients building custom widgets must label rule rows from these fields, not hardcode.

### Enforcement profile attributes surfaced

`EnforcementProfile` model + adapter extended to carry the raw `attributes` list (RADIUS / TACACS attribute pushes — e.g. `Aruba-User-Role: night-night`, `Aruba-Named-User-Vlan: iot`, `Session-Timeout: 28800`). Available in `details.profile_attributes[<profile name>].attributes` when `include_details=True`. Operators (and the new Central role resolver) can now see what each profile actually pushes — names like `WLAN-NIGHT-NIGHT` are no longer opaque.

### New Central tool: `central_get_role_with_policy`

Bundles two endpoints in one call:

- `GET /network-config/v1alpha1/roles/{name}` — role config (VLAN, session params, classification settings)
- `GET /network-config/v1alpha1/policies/{name}` — security policy named after the role (firewall rules with per-rule `condition` + `action`)

Response shape: `{name, role: {...}|None, policy: {...}|None, not_found: [...], errors: [...]}`. Either resource being absent is reported in `not_found` (informational — many shared roles are skeletal, many roles have no separately-named policy). Per-endpoint exceptions go in `errors` and don't abort the other fetch.

Use case: when ClearPass enforcement profile pushes `Aruba-User-Role: night-night`, the AI calls `central_get_role_with_policy(name="night-night")` to surface what that role actually grants/denies (e.g. deny SOCIAL-NETWORKING, deny netflix, deny hulu, etc.).

### Skill template updated

`clearpass-policy-walker.md` gets:

- Step 4b-2 — honor the combine algorithms; never hardcode "stop on match" on evaluate-all role-mapping.
- Step 4d — call `central_get_role_with_policy` when operator asks about role detail. Cheap (~2 GETs per role) but call only for roles the operator actually asks about.

## [3.1.5.0] - 2026-05-18

**Minor — ClearPass policy visualizer now pre-renders Mermaid server-side (#358).** `clearpass_compile_policy_flow` adds a `mermaid` field to the response with three ready-to-paste sectioned blocks. The skill embeds them verbatim — no more AI-side diagram assembly.

### Why now

v3.1.4.1's engine fix guaranteed `short_label` is single-line, but the operator's next test still hit `Parse error … got NODE_STRING` on Block B + Block C — the AI was inlining two node declarations on the same source line in its own assembly pass (`N{"…21"} RA0[/"Set Role…/]` with no edge between them). The skill template's "one declaration per line" rule wasn't enough — AI clients reliably miscompose multi-line Mermaid source. Pre-rendering server-side eliminates the entire failure mode.

### New `format_mermaid()` helper

`policy_visualizer/mermaid_render.py` converts a compiled `FlowGraph` into the structured output:

```json
{
  "mermaid": {
    "sections": [
      {"title": "Block A — Service intake (start → match → auth)", "code": "flowchart LR\n…"},
      {"title": "Block B — Role mapping", "code": "flowchart LR\n…"},
      {"title": "Block C — Enforcement (decision → access)", "code": "flowchart LR\n…"}
    ],
    "simulated": false
  }
}
```

Each `code` is a complete `flowchart LR` block. Every node declaration on its own line. Every label wrapped in double quotes. Internal double quotes demoted to single quotes; `<` `>` HTML-escaped. classDefs (`deny` / `skip` — and `sim_match` / `sim_skip` / `sim_unknown` when a simulation was requested) injected per block. Cross-section edges rendered as labeled stub nodes ("→ Block C") so each block stays self-contained.

Sections with no nodes are omitted (RADIUS_PROXY services skip Block B entirely, for instance).

### Skill template rewritten

`clearpass-policy-walker.md` Step 3 + Step 5b now say "embed `result['mermaid']['sections']` verbatim — do NOT re-assemble." The old per-shape syntax cheat-sheet is gone; AI clients don't need it anymore.

### Backwards-compat

`nodes` / `edges` arrays remain in the response for inspector tooling that needs the raw structure. The `mermaid` field is purely additive.

## [3.1.4.1] - 2026-05-18

**Patch — fix ClearPass policy visualizer Mermaid render failures on large policies (#356).** Operator hit `Parse error … got NODE_STRING` rendering the sectioned Block B / Block C output from v3.1.3.3+. Action / process / end nodes set `label` with literal `\n` (e.g. `"Set Role:\nNest Dweller"`, `"Access: DENY\n(implicit)"`, `"Default:\n..."`) and never set `short_label` explicitly, so `FlowNode.__post_init__` defaulted `short_label = label` — newlines and all. When the AI substituted that into a Mermaid `[/.../]` shape, the literal newline broke Mermaid's per-line shape parser.

### Engine fix

`FlowNode.__post_init__` now collapses any embedded whitespace runs (newlines + tabs + multi-spaces) in `short_label` to single spaces. The single-line invariant is now guaranteed for every node, regardless of node type or which compile_service branch emitted it. `label` keeps its multi-line form for inspector tooltips — only the diagram-facing `short_label` is normalized.

Added a hard unit invariant test: every node returned by `compile_service` across a fixture exercising all node-emitter branches (start, decision, action, process, end variants, defaults, implicit deny) must have a single-line `short_label`.

### Skill template hardened

`clearpass-policy-walker.md` Step 3 readability rules now make two previously-implicit requirements explicit:

- **One node per source line. One edge per source line.** Mermaid's parser doesn't span lines for shapes — `A[/x/] B(((y)))` on one line throws the parse error. Even with edges, declare nodes on their own lines first.
- **Always wrap node label text in double quotes.** ClearPass conditions contain `:`, `=`, `+`, `&`, `|`, `'` etc. that Mermaid's bare-label parser treats as syntax; the compact-label engine emits `&` between AND predicates which MUST stay inside quotes or Mermaid reads it as its own node-list separator.

The template Mermaid example shows the quoted form: `<id>{"<short_label>"}` instead of `<id>{<short_label>}`.

## [3.1.4.0] - 2026-05-18

**Minor — ClearPass policy visualizer gains a what-if simulator. Pass a `simulated_attributes` context (roles, endpoint status, time, visitor name, etc.) and the tool evaluates every rule's predicates against it, returning per-decision-node `simulation_match` flags + a top-level `SimulationOutcome` describing the matched rules, resulting roles, applied profiles, and access decision.**

### Why now

Operator's prior session showed an earlier (pre-v3.1.3.2) simulator-like rendering producing confidently wrong outcomes — the post-auth bucketing bug had every MPSK rule mis-classified as DENY and the visualization presented that as "this is what fires." The whole point of the new simulator is to be **uncertainty-first**: when it can't evaluate a predicate, it returns `None` and the skill MUST surface that as "need more info" rather than guessing.

### Three-valued evaluator

New `conditions.evaluate(expr, context)` — full `Op` coverage with strict three-valued logic:

- `True` — condition is satisfied by the supplied context.
- `False` — condition is contradicted.
- `None` — at least one referenced attribute is missing from the context → genuinely unknown.

`And` / `Or` / `Not` propagate `None` correctly:

| Logic | Result |
|---|---|
| `True AND None` | `None` (can't claim AND is True without knowing the other) |
| `False AND None` | `False` (short-circuit — AND already contradicted) |
| `True OR None` | `True` (short-circuit — OR already satisfied) |
| `False OR None` | `None` (can't claim OR is False without knowing the other) |
| `NOT None` | `None` |

### Multi-valued attribute support

`Tips:Role` and similar attributes accept a `list[str]` context value (for evaluate-all role mapping where a device ends up with multiple roles). Semantics:

- Positive ops (`equals`, `contains`, `regex`, `in_`, ...) → match if ANY value satisfies.
- Negative ops (`not_equals`, `not_contains`, ...) → match only if ALL values satisfy ("none of the roles is X").

### End-to-end simulation outcome

The tool's response now carries a `simulation` block when `simulated_attributes` is supplied:

```json
{
  "simulation": {
    "requested_attributes": {"Connection:SSID": "TestSSID", "GuestUser:Role ID": "11"},
    "status": "resolved",            // "resolved" | "uncertain" | "no_match"
    "matching_role_mapping_rules": ["RM_rule_0"],
    "resulting_roles": ["Kid"],
    "matching_enforcement_rule": "EP_rule_0",
    "applied_profiles": ["WLAN-KID", "VLAN-USER"],
    "access_decision": "ALLOW",       // "ALLOW" | "DENY" | "UNKNOWN"
    "unknown_attributes": [],
    "notes": []
  }
}
```

The simulator merges resolved roles into the enforcement-evaluation context as `Tips:Role` so enforcement rules that match on role correctly resolve.

### Skill workflow (Step 5)

`clearpass-policy-walker` adds Step 5 — a REQUIRED post-render prompt offering the simulation, plus Step 5a defining the strict output contract:

| `simulation.status` | What the AI says to the operator |
|---|---|
| `"resolved"` | Confidently name the matching rule + access decision |
| `"uncertain"` | DO NOT name an outcome. List all `unknown_attributes` and ask for them. |
| `"no_match"` | "No rule matched — implicit deny." |

Step 5b adds re-render guidance with classDefs for green-match / dim-skip / yellow-unknown highlighting. Step 5c gives attribute prompting hints (common keys: `Tips:Role`, `GuestUser:visitor`, `Endpoint:Status`, `Connection:NAD-IP-Address`, etc.).

### Files changed

- `src/.../clearpass/policy_visualizer/conditions.py` — `evaluate()` + per-Op evaluators + multi-valued attribute support + `_attribute_path()` + `_collect_unknown_attrs()` exposed for the simulator.
- `src/.../clearpass/policy_visualizer/flow_graph.py` — `SimulationOutcome` dataclass + `FlowNode.simulation_match` field + `FlowGraph.simulation` field + `_apply_simulation()` walking service-match → RM chain → EP chain with strict uncertainty propagation.
- `src/.../clearpass/tools/policy_visualizer.py` — `simulated_attributes` parameter; `simulation` block in the response when supplied.
- `src/.../skills/clearpass-policy-walker.md` — Step 5 / 5a / 5b / 5c covering the simulation workflow + uncertainty-first output contract + classDef highlighting + attribute prompting hints.
- `tests/unit/test_clearpass_policy_visualizer_simulator.py` — comprehensive new test file: per-Op coverage, three-valued boolean propagation, multi-valued attribute semantics, the previously-burned partial-context case, and end-to-end simulation correctness.

### Counts

- ClearPass tools: still 142 (existing tool gained a parameter — no new tool)
- pytest: 1337 → **1370 passed** (33 new tests in the simulator file)

### Verified

- `ruff check .` ✓
- `ruff format --check .` ✓
- `mypy src/ --ignore-missing-imports` ✓
- `pytest tests/ -q` ✓

## [3.1.3.3] - 2026-05-18

**Patch — make the rendered ClearPass policy flow readable for large policies. Operator's screenshot showed the diagram correctly produced but rendered as one tall narrow column with tiny text, because Mermaid's default `flowchart TD` + the verbose multi-line decision labels collapsed under the conversation's width constraint.**

### Three coordinated fixes

1. **`expr_to_compact_label()` — single-line condition summaries.** New helper in `conditions.py` that produces a compact rendering: drops the namespace prefix (`Authorization:[Guest Device Repository]:Device Role ID` → `Device Role ID`), uses short operator glyphs (`=` `≠` `~=` `∈` `&` `|`), prefers `displayValue` over numeric IDs, and truncates long values with an ellipsis. Caps at 80 chars by default.

   Compare:

   ```
   # expr_to_node_label (verbose — 3 lines per predicate, for inspector tooltips):
   Authorization:[Guest Device Repository]:Device Role ID
   EQUALS
   21

   # expr_to_compact_label (compact single-line, for diagram nodes):
   Device Role ID = 21
   ```

2. **`FlowNode.short_label` field** populated by `compile_service()` for every decision node. Diagram renderers (Mermaid, Graphviz) should prefer this for the visible node text; `label` stays around for inspector / tooltip / details-block content where verbosity is fine. For non-decision nodes (`start`, `process`, `action`, `end`), `short_label` defaults to `label` via `__post_init__` so existing rendering paths still work unchanged.

3. **Skill template rewritten for legibility.**
   - Default direction switched to `flowchart LR` (left-right). Long chains lay out horizontally instead of stacking vertically.
   - Added Mermaid `%%{init: ...}%%` directive prescribing reasonable `nodeSpacing` / `rankSpacing`.
   - Template now uses `short_label` for every node, NOT `label`.
   - New **Step 3b — Sectioned rendering** REQUIRED for policies with ≥ 8 decision nodes: render service-intake / role-mapping / enforcement as three separate Mermaid blocks instead of one giant diagram. Each block fits on screen, operators zoom each independently.

### Why this matters

A real ClearPass MAC-auth + MPSK enforcement policy on the operator's tenant has ~30 decision diamonds across role-mapping + enforcement chains. With the prior template (`TD` + verbose `label`), the rendered Mermaid was unreadable in the chat client — the whole graph got scaled to fit the conversation width while being many screens tall, making every label tiny. After the fix the chains lay out horizontally with one-line condition labels, or split across three readable blocks.

### Files changed

- `src/.../platforms/clearpass/policy_visualizer/conditions.py` — `expr_to_compact_label()` + `_OP_SHORT` glyph map + extracted `_pick_rhs_for_display()`.
- `src/.../platforms/clearpass/policy_visualizer/flow_graph.py` — `FlowNode.short_label` field with `__post_init__` default; every decision-node construction populates it via `expr_to_compact_label`.
- `src/.../skills/clearpass-policy-walker.md` — Step 3 rewritten with `LR` default + `short_label` requirement + Mermaid init directive; new Step 3b on sectioned rendering for large policies.
- `tests/unit/test_clearpass_policy_visualizer_adapter.py` — `TestCompactLabel` (6 cases).
- `tests/unit/test_clearpass_policy_visualizer_flow.py` — `TestShortLabelPropagation` (3 cases) verifying decision nodes get `short_label` and non-decision nodes default.

### Counts

- ClearPass tools: still 142
- pytest: 1328 → **1337 passed** (9 new tests)

### Verified

- `ruff check .` ✓
- `ruff format --check .` ✓
- `mypy src/ --ignore-missing-imports` ✓
- `pytest tests/ -q` ✓

## [3.1.3.2] - 2026-05-18

**Patch — fix four operator-reported bugs in the ClearPass policy visualizer: strict name matching, internal IDs leaking to the user, every enforcement rule mis-labeled "Access: DENY" on real MPSK policies, and the visualization not explaining roles that come from auth-source attributes rather than role-mapping rules.**

### Fix 3 — Every enforcement rule mis-labeled "Access: DENY" on MAC auth + MPSK policies

The most visible bug from a live operator session. On a real MPSK enforcement policy where every rule applies ~10 profiles (one RADIUS Accept + one VLAN + one MPSK + several Post_Authentication side-effect updates), the visualizer labeled every rule "Access: DENY" while the default (single RADIUS Accept) correctly showed "Access: ALLOW."

Two compounding tool bugs:

1. **`_bucket_for_profile()` missed `Post_Authentication`** — the underscore-long-form variant ClearPass REST returns. It recognized `Post-Auth` and `PostAuth` only. Post-auth profiles fell through to `genericEnfProfiles`.
2. **`build()` for `genericEnfProfiles` defaulted missing actions to `generic_reject`** — and Post_Authentication profiles have no `action` field (`null` in the REST response). So they got `profile_type="generic_reject"`. Then `_is_deny()` matched on that type and flagged the rule as deny.

Fixes:

- **`_bucket_for_profile()` normalizes type via lowercase + strip separators**: `Post_Authentication`, `PostAuthentication`, `post-auth`, `PostAuth` all bucket to `postAuthEnfProfiles`.
- **`_is_deny()` semantically tightened**:
  - Skips `post_auth` profiles entirely (side-effects, not access decisions).
  - Requires an explicit deny signal: `profile_type` in `{radius_reject, tacacs_other, generic_reject}` OR `action` in `{deny, reject, drop}`. Missing/empty action no longer counts.
  - Placeholder name heuristic tightened: requires `[Deny Access Profile]` substring or `[Deny`-bracketed prefix. Bare word "deny" in an unrelated context (e.g. `"Update DenyList Audit"`) no longer triggers.

### Fix 4 — Visualization gives no clue when enforcement rules match on auth-source attributes

ClearPass enforcement rules can match on roles or attributes the role-mapping policy never sets — e.g. `Authorization:[Guest Device Repository]:Device Role ID EQUALS 24` maps a guest-device-repository field directly to a per-device classification. The flow rendering is technically correct (it includes the full condition), but operators looking at the visualization couldn't easily tell which roles came from the role-mapping policy vs which came from authorization-source attributes.

Added skill guidance (Step 4b in `clearpass-policy-walker.md`): when a role/attribute referenced in an enforcement rule doesn't appear as a `Set Role` action in the role-mapping section, call it out explicitly in the walkthrough with its source repository.

Also added Step 4c covering the multi-profile MAC-auth + MPSK shape: explains why a rule with 10 profiles still ends in `Access: ALLOW` (RADIUS-layer decision) and that the side-effect profiles in the action node ride alongside the access decision.

### Fix 1 — Fuzzy service-name matching

### Fix 1 — Fuzzy service-name matching

The compile tool previously did only exact-string match on `service_name`. Operator-natural phrasing like *"ClearPass No Wireless For You Auth Service"* (prepends "ClearPass") didn't exact-match the real `"No Wireless For You Auth Service"` → returned `service_not_found` → AI had to fall back to listing all services to find the real name. Wasted round-trip + a misleading "not found" the AI then had to explain.

New tiered resolver (`_resolve_service_name`):

1. `service_id` exact match (unchanged).
2. `service_name` exact case-sensitive match (unchanged behavior — preserved for current callers).
3. **NEW** — case-insensitive exact match.
4. **NEW** — case-insensitive substring match. One result → use it. Multiple results → return `{"status": "ambiguous", "candidates": [<name>, ...]}` so the caller can present a disambiguation prompt by name.

Now *"ClearPass No Wireless For You"* resolves correctly to *"No Wireless For You Auth Service"* in one call.

### Fix 2 — Never expose internal service IDs in user-facing output

The skill runbook didn't explicitly tell the AI to suppress numeric service IDs in its reply. AI output included text like "id 3010" and "id 3044" — internal API identifiers operators don't recognize and don't want to see. Added a top-of-skill **Operator-output rules** section with three explicit rules:

1. NEVER expose numeric ClearPass service IDs (`3010`, `id 1`, `service_id=2`) in user-facing text.
2. Don't expose engine-internal slug IDs either (the `service_id` slug in FlowGraph output).
3. Refer to services by their full ClearPass name in quotes.

The skill's disambiguation example now shows the right output: list candidate names, no IDs.

### Files changed

- `src/hpe_networking_mcp/platforms/clearpass/tools/policy_visualizer.py` — extracted `_resolve_service_name()` helper with 4-tier match; added `ambiguous` response shape; renamed `service_name` arg docstring to call out fuzzy matching; called out `service_id` as internal.
- `src/hpe_networking_mcp/skills/clearpass-policy-walker.md` — restructured procedure around fuzzy match; added Operator-output rules section; replaced worked example with the No-Wireless-For-You ambiguous-resolution case.
- `tests/unit/test_clearpass_policy_visualizer_tools.py` — added `TestResolveServiceName` (7 cases covering all 4 match tiers + id match) + `TestCompilePolicyFlowAmbiguousResponse` (end-to-end ambiguous response).

### Files changed (this patch)

- `src/hpe_networking_mcp/platforms/clearpass/policy_visualizer/api_adapter.py` — `_bucket_for_profile()` normalizes type via lowercase + strip separators, recognizing `Post_Authentication` and its spelling variants.
- `src/hpe_networking_mcp/platforms/clearpass/policy_visualizer/flow_graph.py` — `_is_deny()` skips post-auth profiles, requires explicit deny, stricter placeholder name heuristic; `_DENY_ACTIONS` adds `drop`.
- `src/hpe_networking_mcp/platforms/clearpass/tools/policy_visualizer.py` — `_resolve_service_name()` 4-tier fuzzy match + `ambiguous` response shape.
- `src/hpe_networking_mcp/skills/clearpass-policy-walker.md` — Operator-output rules section (no IDs in user-visible text); Step 4b on auth-source role attribution; Step 4c on the multi-profile MAC-auth + MPSK shape.
- `tests/unit/test_clearpass_policy_visualizer_tools.py` — `TestResolveServiceName` + `TestCompilePolicyFlowAmbiguousResponse`.
- `tests/unit/test_clearpass_policy_visualizer_flow.py` — `TestCompileServiceMacAuthMpskShape` (realistic 10-profile rule shape); `TestIsDenySemantics` (post-auth-skipping + explicit-deny + drop + placeholder-name-strictness).

### Verified

- `ruff check .` ✓
- `ruff format --check .` ✓
- `mypy src/ --ignore-missing-imports` ✓
- `pytest tests/ -q` ✓ (1312 → 1328 passed)

## [3.1.3.1] - 2026-05-18

**Patch — version-aligns the trigger-coverage fix that landed in #351.**

PR #351 hardened the `clearpass-policy-walker` skill triggering (see commit `add2747`) but was merged as "docs-only" with no version bump. That was a misclassification — `src/hpe_networking_mcp/INSTRUCTIONS.md` and the skill `.md` files under `src/hpe_networking_mcp/skills/` are **shipped runtime artifacts**: the server reads INSTRUCTIONS.md at startup (see `server.py:12`, `server.py:255`) and surfaces it as the MCP `serverInstructions` field. Skill files are read by `skills_list` / `skills_load` at runtime. Operators who consume the Docker image have no way to receive trigger fixes without a tagged release.

This patch bumps `pyproject.toml` so the v3.1.3.1 git tag aligns with the package version + triggers the `Docker Publish` workflow against a release event, making the fix actually reachable for image consumers.

### Versioning rule clarification

Going forward: a version bump is required for any change to a file the server loads at runtime — including INSTRUCTIONS.md, every skill markdown under `src/.../skills/`, and any other content shipped inside `src/`. Pure documentation files (`README.md`, `CHANGELOG.md`, `docs/TOOLS.md`, source comments) that don't affect runtime behavior still don't need a version bump.

### What changed in #351 (re-summarized for the release notes)

- Extended the `clearpass-policy-walker` skill's `description` frontmatter (what `skills_list` returns) to cover ClearPass-native phrasings — *"auth service"*, *"authentication service"*, *"policy service"*, *"ClearPass service"* — and casual-name handling (e.g. *"No Wireless For You"*).
- Added *visualize*, *render*, *diagram*, *flowchart*, *draw*, *walk the flow*, *show me how X decides* to the universal-trigger-words list in INSTRUCTIONS.md so any pairing with a ClearPass service name forces a `skills_list()` call before the model answers.
- Added an explicit CRITICAL clause in the skill description: never guess at a named service; always call the tools first.

## [3.1.3.0] - 2026-05-18

**Minor — ClearPass policy visualizer: render a service's full decision flow (service match → authentication → role mapping → enforcement) as a Mermaid flowchart. Ships as 2 new tools + 1 new skill, backed by an internal compilation engine ported (and adapted for REST) from an existing standalone project. Closes #349.**

### What got added

| Layer | Component | Purpose |
|---|---|---|
| Tool | `clearpass_list_policy_services` | Slim picker-ready service list (id / name / type / template / enabled / role_mapping_policy / enf_policy / hit_count / monitor_mode) |
| Tool | `clearpass_compile_policy_flow` | Compile one service into a FlowGraph (nodes + edges + warnings) ready for an AI client to render as Mermaid. Supports `service_id` OR `service_name`; optional `include_details` for per-rule inspector data. |
| Skill | `clearpass-policy-walker` | Multi-step runbook: pick service → compile → render as Mermaid + per-service summary + walkthrough |
| Engine | `clearpass/policy_visualizer/` (5 modules, ~1,400 LOC) | `conditions.py` (Boolean AST + Op enum), `policy_model.py` (typed PolicyModel + cross-reference resolver), `flow_graph.py` (FlowGraph compiler), `policy_details.py` (inspector serializer), `api_adapter.py` (REST JSON → raw dict bridge) |

### Semantics baked into the compiler

- **First-applicable**: role-mapping or enforcement chain stops at the first matching rule.
- **Evaluate-all**: every matching action runs; subsequent decisions wired with `CONTINUE` edges from prior actions.
- **Implicit deny**: terminating "Access: DENY (implicit)" node when no rule matches and no default exists.
- **RADIUS_PROXY**: service-match YES wires directly into enforcement, skipping authentication + role mapping entirely.
- **Unresolved references**: never fail-fast — surface a placeholder object and append a human-readable warning to `model.warnings`.

### REST data sources

Every call to `clearpass_compile_policy_flow` fans out to 7 endpoints (`/config/service`, `/role-mapping`, `/enforcement-policy`, `/enforcement-profile`, `/role`, `/auth-method`, `/auth-source`) to resolve cross-references — typical tenant returns in well under a second.

### Counts

- ClearPass: 140 → **142**
- Server-wide underlying tools: 1891 → **1893**
- Bundled skills: 10 → **11**

### Verified

- `ruff check .` ✓
- `ruff format --check .` ✓
- `mypy src/ --ignore-missing-imports` ✓
- `pytest tests/ -q` ✓ (1266 → 1300+ passed; 3 new test files: `test_clearpass_policy_visualizer_adapter.py` covers operator mapping + adapter shape, `test_clearpass_policy_visualizer_flow.py` covers model build + flow semantics including evaluate-all, implicit-deny, RADIUS_PROXY, and `test_clearpass_policy_visualizer_tools.py` covers the 2 MCP tools with mocked HTTP layer)

### Not yet shipped (future work)

- Cisco ISE policy visualization (the upstream supports it; not built here)
- XML import (REST is the source of truth)
- Server-side SVG/PNG rendering (AI client renders Mermaid in-conversation)
- Orphan / unused-object detection across the whole tenant (would reuse `policy_model.build()`)
- Live per-rule hit-count data (ClearPass exposes it at a different endpoint; not wired in yet)

## [3.1.2.1] - 2026-05-16

**Patch — correct the feature-comparison matrix in README.md (12-row audit) + fix the `central_get_asset_tags` / `central_get_asset_tag` / `central_manage_asset_tag_metadata` docstrings to describe what they actually wrap.**

### README feature-matrix audit

Full audit of the README feature-comparison table against actual tool inventory across all 7 platforms. **7 rows corrected, 5 new rows added.**

| Row | Change | Why |
|---|---|---|
| **Rogue AP Detection** | Central — → ✅ | `central_get_wids_monitored_aps` shipped v3.1.1.1 |
| **Endpoint Profiling** | Central — → ✅ | `central_get_devicefingerprinting*` + `central_get_client_insight` (config) + fingerprinted attrs on `central_get_clients` (data) — shipped v3.1.1.0 |
| **Application Visibility** | Mist — → ✅ | `orgs_applications` + `orgs_linked_applications` |
| **Subscriptions / Licensing** | Mist — → ✅ | `orgs_licenses` / `msps_licenses` / `sites_licenses` |
| **User Management** | Mist + Central — → ✅ | Mist: `orgs_admins` / `orgs_sso*` / `msps_admins` / `msps_sso*`. Central: `central_get_management_user` / `_management_user_group` from v3.1.1.0 |
| **Guest Management** | Mist + Central — → ✅ | Mist: `orgs_guests` / `sites_guests`. Central: `central_get_aaa_captive_portal` + `central_get_cda_portal_*` |
| **Certificates** | Mist + Central — → ✅ | Mist: `orgs_cert` / `orgs_crl` / `orgs_scep` / `orgs_nac_crl`. Central: `central_get_certificate*` family from v3.1.1.0 |

New rows added (5):

- **Webhooks** — Mist + Central
- **Reports / Scheduled Reports** — Mist + Central + ClearPass
- **Floor Plans / Sitemaps** — Mist + Central
- **BLE Asset Tracking / IoT Beacons** — Mist + Central (see asset-tag docstring fix below)
- **Marvis / AI Assistant** — Mist only

### Asset-tag docstring fix (the row that nearly went wrong)

The v3.1.2.0 import described Central's `network-services/v1/asset-tags` endpoints as "user-defined metadata you attach to devices for grouping / filtering" — which was wrong. The Postman example response confirmed: each record carries a BLE `macAddress`, `deviceClassifications` like `"ArubaAssetTag"` / `"Blyott"` (Blyott is a BLE beacon vendor), `firstSeen` timestamps from AP detection, and "last known location." These ARE BLE asset tags — physical beacons attached to tracked assets (laptops, medical equipment, inventory) that APs detect and locate. The `/metadata` sub-resource is the inventory annotation layer (name, owner, asset class, etc.) you attach to each detected tag.

Docstrings on `central_get_asset_tags` / `central_get_asset_tag` / `central_manage_asset_tag_metadata` rewritten to reflect that. The `BLE Asset Tracking / IoT Beacons` matrix row gained Central ✅ as part of the audit.

### Deliberate non-changes

- **Radio Resource Management — Central**: stayed —. Central has `central_get_radio` (config-model radio profile) but the actual auto-tuning RRM engine is AirMatch, which lives under `airmatch/v1/` and is out-of-policy per the 2026-05-15 build rule.
- **Workspaces — Central**: stayed —. Workspaces are a GreenLake-specific construct.

### Verified

- `ruff check .` ✓
- `ruff format --check .` ✓
- `mypy src/ --ignore-missing-imports` ✓
- `pytest tests/ -q` ✓ (1266 passed, 1 skipped)

## [3.1.2.0] - 2026-05-15

**Minor — bulk-import the Aruba Central MRT API surface (Monitoring / Reporting / Troubleshooting / Notifications / Services / MSP / Sitemaps) as 133 net-new typed tools across 13 new modules. Central: 480 → 613; server-wide: 1758 → 1891.**

Closes the long-standing gap between Central's published config-model surface (the `network-config/v1alpha1/*` tools we shipped in v3.1.1.0) and its live observability + operations surface. After this release the platform is reachable for the full read-write loop: configure → monitor → troubleshoot → react, all from the AI.

### What got added (by section)

| Module | Tools | Covers |
|---|---|---|
| `mrt_msp.py` | 1 | MSP tenant listing |
| `mrt_insights.py` | 1 | `network-notifications/v1/insights` (recommendation-style observations distinct from `central_get_alerts`) |
| `mrt_reporting.py` | 3 | Reports list / update / report-runs |
| `mrt_webhooks.py` | 4 | Webhooks CRUD + HMAC key rotation |
| `mrt_services.py` | 14 | FCO response info, asset tags, AP ranging scans, device locations, WiFi-client locations, location analytics |
| `mrt_sitemaps.py` | 17 | Floors, buildings, walls, zones, device placement (deploy/assign/plan), wall-types, sitemap import, scale + image |
| `mrt_health.py` | 4 | Per-site / tenant-wide device + client health rollups beyond the existing `central_get_site_health` dashboard view |
| `mrt_clients.py` | 9 | Clients trend, top-N by usage, mobility trail, per-client detail, onboarding-stage diagnostics (score / export / reasons / count), firewall sessions (3 perspectives) |
| `mrt_topology.py` | 7 | Topology graph, LLDP/CDP neighbours, unmanaged-device detection, isolated-devices, device inventory, device PATCH + DELETE |
| `mrt_switch.py` | 8 | Switches list, LAG, runtime VLANs, hardware categories, per-interface trends, top-N interface trends, VSX, stack members |
| `mrt_ap.py` | 17 | AP top-level trends (cpu/memory/power/throughput), per-radio trends, per-port trends, per-tunnel trends, per-WLAN throughput, tenant-wide radios/BSSIDs/WLANs/swarms lists, top-N APs by usage |
| `mrt_gateway.py` | 18 | Gateway list + top-level trends, ports, tunnels, runtime VLANs, uplinks + probes + probe performance, DHCP pools/clients, cluster members + summaries + capacity trends |
| `mrt_troubleshooting.py` | 25 | pingSweep, getArpTable, nslookup, AAA test, iperf, HTTP/HTTPS/TCP probes, speedtest, locate, reboot, halt, rebootSwarm, list-tasks, list supported show commands, event-extra-attributes, gateway / AP disconnect-extras, shared async-status poller |

### Conventions

- **Hand-curated style** — matches the existing 480-tool Central surface (Annotated + Field descriptions, `retry_central_command` for transport, `READ_ONLY` / `WRITE_DELETE` / `OPERATIONAL` annotations gating elicitation + write-tool toggle).
- **Trend endpoints consolidated** — per-entity time-series endpoints fold into one tool per sub-resource taking a `dimension` Literal (e.g. `central_get_ap_radio_trend(serial, radio_number, dimension)` covers throughput / channel-utilization / channel-quality / noise-floor / frames). Matches the existing `central_get_switch_hardware_trends` pattern.
- **Async-pollers shared** — every troubleshooting POST returns a `task_id`; one `central_get_troubleshooting_task_status(device_family, serial, action, task_id)` polls them all.
- **Device-family routing** — actions offered on multiple device families (`aos-s` / `aps` / `cx` / `gateways`) take a `device_family` Literal arg and route internally, matching the existing `central_ping(device_type=...)` pattern.
- **Operational vs write** — destructive operations (reboot, halt, locate, disconnect) use `OPERATIONAL` annotation (fires elicitation, no toggle); config-write operations (manage_webhook, update_report, update_device, manage_sitemap_devices, manage_floor, manage_floor_walls, etc.) use `WRITE_DELETE` + `central_write_delete` tag (toggle-gated AND elicitation).

### Tool surface delta

- **Mist**: 1037 (unchanged)
- **Central**: 480 → **613** (+133)
- **GreenLake**: 10 (unchanged)
- **ClearPass**: 140 (unchanged)
- **Apstra**: 19 (unchanged)
- **Axis**: 25 (unchanged)
- **AOS8**: 47 (unchanged)
- **Server-wide total**: 1758 → **1891**

### Known limitations / follow-ups

- **PII tokenization**: webhook HMAC keys, AAA-test credentials, asset-tag metadata, mobility-trail records, location analytics, and firewall sessions carry sensitive data. Existing rules cover MACs + WLAN/RADIUS surfaces but not these new shapes. File a follow-up tokenization extension PR before turning on `ENABLE_CENTRAL_WRITE_TOOLS=true` on tenants with untrusted AI clients (same caveat as v3.1.1.0).
- **Overlap with pycentral library wrappers**: a small number of MRT endpoints have existing hand-curated tools that route through `pycentral.new_monitoring.*` library calls (e.g. `central_get_aps`, `central_get_clients`, `central_get_gateway_details`). Those are left untouched; the new MRT tools cover everything *not* already wrapped via pycentral. No collisions.
- **Async polling is operator-driven** — `central_get_troubleshooting_task_status` is a separate call; the POST tools don't auto-poll. Matches the existing async-status pattern.

### Verified

- `ruff check .` ✓
- `ruff format --check .` ✓
- `mypy src/ --ignore-missing-imports` ✓ (430 source files, no issues)
- `pytest tests/ -q` ✓ (1266 passed, 1 skipped)
- Live registration smoke test: `register_tools(mcp, ...)` returns 613 underlying Central tools

## [3.1.1.1] - 2026-05-15

**Patch — add `central_get_wids_monitored_aps`, wrapping the `network-services/v1alpha1/wids-monitored-aps` undocumented-but-in-policy endpoint. Surfaces neighbor / rogue / suspect / interfering APs detected by the caller's APs, plus the fabric's containment status for each.**

The endpoint is undocumented in Central's public API reference but lives under the in-policy `network-*/v1alpha1` path family (per the 2026-05-15 build-rule), is tenant-scoped (no cross-tenant exposure), and was already live-probed during the undocumented-endpoint catalog work. No secrets in the response — BSSIDs ride existing MAC normalization rules; everything else is normal tenant data.

### Tool surface

- **`central_get_wids_monitored_aps(classification=..., contained_only=False, site_id=..., odata_filter=..., limit=100, offset=0)`** — GET wrapper with structured args that compose into an OData filter, plus an `odata_filter` raw pass-through escape hatch. Validates that the two paths are mutually exclusive (raw filter OR structured args, not both) and returns a clear error string if mixed.

Each record carries: `id`, `bssid`, `ssid`, `classification` (`ROGUE` / `SUSPECT_ROGUE` / `INTERFERING` / `VALID`), `classificationMethod`, `classificationRule`, `containmentStatus` (e.g. `CONTAINED`), `encryption`, `signal`, `macVendor`, `type`, `portData`, `firstSeen` / `lastSeen` timestamps, the detecting-device names + serials (first / most-recent), plus `siteId` / `siteName` of the detecting AP.

### Tool surface delta

- **Mist**: 1037 (unchanged)
- **Central**: 479 → **480** (+1)
- **GreenLake**: 10 (unchanged)
- **ClearPass**: 140 (unchanged)
- **Apstra**: 19 (unchanged)
- **Axis**: 25 (unchanged)
- **AOS8**: 47 (unchanged)
- **Server-wide total**: 1757 → **1758**

### Verified

- `ruff check .` ✓
- `ruff format --check .` ✓
- `mypy src/ --ignore-missing-imports` ✓
- Live registration smoke test: `register_tools(mcp, ...)` returns 480 underlying Central tools
- Endpoint was already live-probed during the undocumented-endpoint catalog work — shape is stable; PII review pre-done

## [3.1.1.0] - 2026-05-15

**Minor — bulk-import the Aruba Central config-model OpenAPI surface as 197 new typed config-object types (389 net-new tools across 19 new modules). Unlocks AAA, AOS-CX interface/routing/services/system, certificates, AirGroup, NAC (CDA), telemetry, and the wider device-level config-model so design work no longer blocks on per-type tool authoring.**

Central went from 90 underlying tools → **479**. Server-wide tool count: **1368 → 1757**.

### Why this PR

Previous workflow was hand-curating one Central config-model tool at a time as design work required it. The 212 OpenAPI specs under the local-only `api-endpoints/central/config/` directory captured the full configurable surface; only 15 had hand-curated tool pairs. Multi-step design conversations (AAA, RF, security policy modelling) kept stalling on "this type doesn't have tools yet — let me add them first." Bulk-importing the remaining 197 types into the codebase removes that bottleneck so design conversations can focus on mappings instead of tool authoring.

Per the project's no-partial-implementations guidance, the import covers every spec we can map cleanly — three OpenAPI path shapes are handled:

1. Collection + item (the common case): emits `central_get_<type>(ctx, <id>=None)` + `central_manage_<type>(ctx, <id>, action_type, payload, ...)`.
2. Singleton (no item path — e.g. `system-info`, `firmware-compliance`): emits the same pair without an identifier parameter.
3. Item-only with parameterised path (e.g. `persona-assignment/{device-function}`): emits the pair with the path param as the identifier.

### Approach — one-shot import, hand-curated going forward

This is **not** a maintained spec-driven generator. The bigger "should Central be spec-driven like Mist" decision is deferred. What we shipped instead:

- A one-shot import script at `scripts/import_central_config_tools.py` that reads `api-endpoints/central/config/` (gitignored — your local-only snapshot) and emits hand-curated-style wrappers under `src/hpe_networking_mcp/platforms/central/tools/`.
- Each generated file leads with `Initial import emitted by ... — safe to edit afterward` and refers operators to the import script for regeneration. Re-running overwrites local edits, so treat the output as ordinary hand-curated Python from here on.
- 15 types already covered by tuned hand-curated wrappers (`alias`, `auth-server-group`, `config-assignment`, `gw-cluster`, `gw-cluster-intent`, `named-vlan`, `net-group`, `net-service`, `object-group`, `policy`, `policy-group`, `role`, `role-acl`, `role-gpid`, `wlan`) are on an explicit skip list so their rich docstrings, edge-case handling, and LOCAL filters stay intact.

### What got generated (19 new modules)

| Module | Objects | x-tag-group |
|---|---|---|
| `application_experience.py` | 2 | Application Experience |
| `central_nac.py` | 11 | Central NAC (full CDA surface) |
| `config_management.py` | 3 | Config Management |
| `extensions.py` | 3 | Extensions |
| `firmware_policy.py` | 1 | Firmware Policy |
| `high_availability.py` | 3 | High Availability |
| `interfaces.py` | 22 | Interfaces |
| `iot.py` | 1 | IoT |
| `named_object.py` | 1 | Named Object |
| `network_services.py` | 22 | Network Services |
| `routing_overlays.py` | 22 | Routing & Overlays |
| `security.py` | 30 | Security (AAA, auth servers, certificates, firewall, MAC-sec, port-security, …) |
| `services.py` | 5 | Services (AirGroup, location, …) |
| `system.py` | 36 | System (system-info, snmp, ntp, logging, management users, …) |
| `telemetry.py` | 9 | Telemetry |
| `tunnels.py` | 2 | Tunnels |
| `uncategorized.py` | 7 | Uncategorized (overlay-wlan, vxlan, vsx-pair, …) |
| `vlans_networks.py` | 11 | VLANs & Networks |
| `wireless.py` | 6 | Wireless |

Each module emits `central_get_<title>` + `central_manage_<title>` per type (with asymmetric specs emitting only what's supported — five types are GET-only or POST-only, hence 389 net-new tools rather than the 197×2 = 394 ceiling).

### Naming conventions

- **Function names use OpenAPI `info.title` directly (singular)**: `central_get_aaa_profile` / `central_manage_aaa_profile`. Discoverable as a pair; no irregular-plural edge cases. Hand-curated tools (skip-list) keep their existing plural-GET / singular-MANAGE convention; the two conventions coexist by name without collision.
- **Path-param identifiers snake-cased, original spelling preserved in docstring**: e.g. the spec's `{mac-address}` becomes Python `mac_address`, with the docstring noting `OpenAPI path param: mac-address` for traceability.
- **Reserved-name collision avoidance**: when an OpenAPI path param snake-cases to a name reserved by the manage-tool signature (`ctx`, `action_type`, `payload`, `scope_id`, `device_function`, `confirmed`), the emitter prefixes the path param with `target_` (real-world offender: `persona-assignment/{device-function}` → `target_device_function`).

### Shared helper extension

`_manage_resource` in `src/.../central/tools/security_policy.py` learnt to handle the singleton URL shape: when `name` is `None`/empty the URL omits the trailing `/{name}` segment. Existing callers always pass a real string, so behaviour is unchanged for the 15 hand-curated types.

### Tool surface delta

- **Mist**: 1037 (unchanged)
- **Central**: 90 → **479** (+389)
- **GreenLake**: 10 (unchanged)
- **ClearPass**: 140 (unchanged)
- **Apstra**: 19 (unchanged)
- **Axis**: 25 (unchanged)
- **AOS8**: 47 (unchanged)
- **Server-wide total**: 1368 → **1757**

### Known limitations / follow-ups

- **PII tokenization**: several net-new types carry sensitive payloads (RADIUS shared secrets in `auth-server`, passwords in `internal-user`, certificate/key material in `certificate*`, MPSK PSKs in `mpsk-local`, etc.). The existing tokenization rules in `redaction/rules.py` cover Mist + Central WLAN/RADIUS but not the wider AOS-CX surface. This PR ships the tools without extending tokenization rules — file an issue and extend rules before turning on `ENABLE_CENTRAL_WRITE_TOOLS=true` on a tenant where AI clients are untrusted.
- **Payload schemas remain `dict`**: matches the existing hand-curated pattern. Per-type Pydantic models could be added by hand-editing the generated files (the headers explicitly invite this).
- **9 specs needed singleton / item-only support** that the original parser rejected; the import script grew the two shapes to cover them. Future genuinely-non-standard specs may need further parser work.

### Verified

- `ruff check .` ✓
- `ruff format --check .` ✓
- `mypy src/ --ignore-missing-imports` ✓ (416 source files, no issues)
- `pytest tests/ -q` ✓ (1266 passed, 1 skipped — same baseline as v3.1.0.15)
- Live registration smoke test: `register_tools(mcp, ...)` returns 479 underlying Central tools

## [3.1.0.15] - 2026-05-15

**Patch — relocate the Mist tool generator out of `src/` into `scripts/` so it no longer ships dead in the runtime Docker image.**

The Mist generator (`_generator.py`) and its CLI (`regenerate.py`) lived inside the runtime package but were never invoked at server startup — they only run at release time, manually by the maintainer. Shipping ~640 LOC of dead code in every Docker image was a quirk from when Mist was first ported to spec-driven generation (v3.1.0.0), never reconsidered. Moving them outside `src/` keeps the regen workflow functionally identical while removing the dead bytes from production builds. Sets up the same `scripts/`-based home for the next PR's Central one-shot import script.

### What moved

- `src/hpe_networking_mcp/platforms/mist/_generator.py` → `scripts/_mist_generator.py`
- `src/hpe_networking_mcp/platforms/mist/regenerate.py` → `scripts/regenerate_mist_tools.py`

The CLI imports its sibling generator via a `sys.path.insert(0, ...)` at the top so `scripts/` doesn't need to be a Python package.

### What stayed (intentionally)

- Generator logic itself — verbatim port, no behavior change.
- Vendored spec at `vendor/mist_openapi.json`.
- Daily sync workflow at `.github/workflows/sync-mist-openapi.yml` (still runs, still commits to `main`).
- Auto-emitted Mist tool files at `src/.../mist/tools/` — only their docstring headers (the `emitted by` and `Regenerate via:` lines) were mechanically updated to point at the new path. Function bodies untouched.

### Workflow change

The release-time regen command changes from:

```bash
uv run python -m hpe_networking_mcp.platforms.mist.regenerate
```

to:

```bash
uv run python scripts/regenerate_mist_tools.py
```

`docker-compose.dev.yml` now mounts `./scripts:/app/scripts` so the regen runs in Python 3.12 with the project's deps, same as before. The production `docker-compose.yml` is unaffected; the production `Dockerfile` already copies only `src/` (plus `pyproject.toml` and `README.md`), so excluding the generator from the image is structurally enforced by the Dockerfile, not just by `.dockerignore`.

### Reference updates

- `.github/workflows/sync-mist-openapi.yml` — the commit-message hint now quotes the new path.
- `vendor/mist_openapi.SOURCE.md` — the "Regeneration runs at release time" block now quotes the new path.
- `.gitleaks.toml` — the comment over the `mist/tools/` allow-path now names `scripts/_mist_generator.py`.
- `src/.../mist/__init__.py` — module docstring's regen instruction quotes the new path.

### Verified

- AST parse of both relocated `scripts/*.py` files.
- Container import: `_mist_generator` loads cleanly under Python 3.12 inside the dev image with the sibling `sys.path` tweak; `generate_tool_files` symbol is exposed as before.

### Follow-up

Next PR brings in the 197 net-new Central config tools as hand-curated-style wrappers via a new one-shot import script at `scripts/import_central_config_tools.py`. The bigger "should Central also be spec-driven via a maintained generator" decision is deferred and tracked separately.

## [3.1.0.14] - 2026-05-15

**Patch — harden `cross-platform-rf-check` against three operator-transcript failure modes. Closes #340 and #342.**

Operator ran *"Do an RF check at HOME in Central"* on GitHub Copilot (Sonnet 4.6); the skill loaded but the in-sandbox AI hit two crashes AND ignored the user's platform scope:

1. (#340) `Sandbox error: Exception: Unknown tool: mist_get_self` — the AI dispatched the Mist tool by bare name through `call_tool("mist_get_self", {})`. That's the #328 footgun: the ~1000 spec-driven Mist tools are registered but not in the sandbox's resolvable catalog by bare name; they must go through `mist_invoke_tool`. The skill had Step 2 worded as a direct call (`mist_list_org_sites(org_id=...)`) with no dispatch warning — and said `org_id` "comes from `health` or the Mist session context" without a concrete tool, so the AI extrapolated `mist_get_self` and used the wrong dispatch pattern.
2. (#340) `AttributeError: 'list' object has no attribute 'get'` — the AI called `radio["radioStats"].get("channelUtilization")`. Central's `central_get_ap_details` returns `radioStats` as a single-element **list** (`[{"channelUtilization": ..., "noiseFloor": ...}]`), not a dict. The skill's Step 6 wording (*"`radioStats` **with** `channelUtilization` and `noiseFloor`"*) implied a dict.
3. (#342) The AI ignored the user's *"in Central"* scope. It said to itself: *"Since the user said 'in Central', I'll still check both platforms per the runbook but will focus on Central"* — then ran Mist steps anyway (which is where the dispatch crash above surfaced). The skill's `## Procedure` defaulted to full cross-platform fan-out, the Decision matrix had no row for *user-stated* scope (only *config-enabled* scope), and nothing in the body said user constraints override runbook defaults. Per the project's MCP-memory architectural finding, INSTRUCTIONS.md is treated as untrusted by AI clients — only the loaded skill body can reliably shape behavior — so the load-bearing fix lives in the runbook itself.

### What changed

- **Mist dispatch — CRITICAL** subsection right before *Response shapes*: shows the WRONG (`call_tool("mist_get_self", {})`) and RIGHT (`call_tool("mist_invoke_tool", {"name": ..., "params": ...})`) patterns side-by-side, and names every Mist tool in the runbook (`mist_get_self`, `mist_list_org_sites`, `mist_list_site_devices_stats`, `mist_get_site_current_channel_planning`). Step 2 rewritten with a concrete two-call snippet: `mist_invoke_tool(name="mist_get_self", params={})` → pick `privileges[i]["scope"] == "org"` for `org_id` → `mist_invoke_tool(name="mist_list_org_sites", params={"org_id": ...})`. Steps 4 and 5 updated to the same dispatch shape.
- **Response shapes table** gains a `mist_get_self` row; **Step 6 + a follow-up callout** spell out that `radioStats` is a list and show `radio["radioStats"][0]["channelUtilization"]` — including the exact `'list' object has no attribute 'get'` error string so the AI can recognize the symptom.
- **New Step 0 — Determine platform scope from the user's request** at the very top of the Procedure. Parses common language (*"in Mist"*, *"in Central / Aruba"*, *"across both / everywhere"*) into a `user_scope` list and states explicitly that user scope is authoritative and overrides the runbook default. Also quotes the *"still check both per the runbook"* anti-pattern from the transcript so the AI recognizes the trap.
- **Per-step `user_scope` gates** on Step 2 (Mist entry) and Step 3 (Central entry). Steps 4/5 cascade off Step 2 and Step 6 cascades off Step 3, so they inherit the skip naturally.
- **Decision matrix** gains two top rows: *"User scoped to Mist only"* and *"User scoped to Central only"* — making single-platform-by-user-request a first-class shape, not a deviation.
- **Step 8 Output formatting** — the report headline now echoes `(scope: user-requested <platform>)` when `user_scope` covered one platform, so the operator can see the run honored their constraint.
- **Examples section** gains scoped examples (*"Do an RF check at HQ in Central" → `user_scope=["central"]`*) so the keyword/scope mapping is concrete.
- **Frontmatter `tools:` allowlist** now includes `mist_invoke_tool` and `mist_get_self`.
- **INSTRUCTIONS.md** gains item #9 — a defensive (best-effort) note that AIs should honor user-stated platform scope inside loaded multi-platform skills. Annotated as defensive because MCP-server-supplied content is untrusted in AI-client views per the project's architectural finding; the load-bearing fix is in the skill body.

### Verified

- New `tests/unit/test_skill_cross_platform_rf_check.py` (10 tests, all green) asserts: the Mist-dispatch warning carries both `mist_invoke_tool` and the `Unknown tool` error string; Step 2 names `mist_get_self` and dispatches via `mist_invoke_tool`; Steps 4/5 dispatch via `mist_invoke_tool`; `radioStats` is documented as a list with the `[0]` indexing pattern and the exact `AttributeError` quoted; frontmatter includes the new tool names; Step 0 exists and precedes Step 1; Step 0 captures `user_scope` with the *"in Mist"* / *"in Central"* keywords and the override directive plus the *"still check both per the runbook"* anti-pattern quote; Steps 2/3 carry `"<platform>" not in user_scope` gates; Decision matrix has both user-scoped rows; Output formatting instructs the headline to echo `(scope: user-requested ...)`.
- `test_skill_tool_references.py` still clean — verified the new Python snippet doesn't introduce variable names that look like tool refs to the regex (`mist_site` → `site_match`).

## [3.1.0.13] - 2026-05-14

**Patch — enforce "skills first" at the tool layer instead of just implying it. Closes #338.**

Operator: *"Do an RF check for HOME in Central"* → the AI went straight to `search` / `execute` and improvised; it never called `skills_list`, so it never found `cross-platform-rf-check`. Its own diagnosis: the `skills_list` description was a soft, conditional trigger ("Use this when the user asks to run an audit, migration…") that an RF check "didn't feel like," and `search` / `execute` — the tools it actually used — had **no gate** pointing back to skills. "The root issue is that 'check skills first' is *implied* rather than *enforced* at the tool layer."

v3.1.0.12 (#336) fixed the `skills_list` *output* to push toward `skills_load` — but that only helps once `skills_list` is called. This release makes sure it gets called.

### What changed

- **`skills/_engine.py` — `_SKILLS_LIST_DESC`** reframed from conditional ("List available skills… Use this when…") to unconditional: "ALWAYS call this FIRST — before `search` / `tags` / `get_schema` / `execute` / any platform tool — on ANY networking request." Now also names "RF / channel-planning checks" explicitly in the covered-procedures list.
- **`server.py`** — new shared `_SKILLS_FIRST_GATE` prepended to `_SEARCH_DESCRIPTION`, `_TAGS_DESCRIPTION`, and `_GET_SCHEMA_DESCRIPTION`: "Call `skills_list` FIRST… only fall through to this tool when `skills_list` returns no applicable skill."
- **`server.py` — `execute_description`** gains a hard `PREREQUISITE` line near the top: call `skills_list` at the outer surface before using `execute`.
- **`INSTRUCTIONS.md`** — universal skill-trigger word list gains `rf check`, `rf`, `check the rf`, `channel planning`, `spectrum`, `co-channel` (a known gap — "RF check" matched none of the MUST-fire triggers).

### Verified

- New `test_server_code_mode.py` tests assert the skills-first gate leads `_SEARCH_/_TAGS_/_GET_SCHEMA_DESCRIPTION` and that `execute_description` carries the `PREREQUISITE`; new `test_skills.py` test asserts `_SKILLS_LIST_DESC` opens with the unconditional "ALWAYS … FIRST" directive.
- All unit tests + ruff + format + mypy clean.

## [3.1.0.12] - 2026-05-14

**Patch — `skills_list` output now pushes the AI to `skills_load`. Closes #336.**

An AI client recognized a skill trigger, called `skills_list()` three times, saw the metadata (description + tool list), and **never called `skills_load(name=...)`** to fetch the actual runbook body — it improvised the procedure (and the visualization) from the metadata hint instead. Its own post-mortem: *"the metadata gives enough of a hint that a visualization is involved, but not how — that detail only exists in the body."*

Root cause: `skills_list` returned `{"count", "skills"}` with nothing in the **response** telling the AI this is metadata-only and `skills_load` is the required next step. The tool *description* says so, but the AI reads the description once and the output every call — the output is the high-signal surface and carried no directive.

### Fix

`_engine.py::_make_skills_list_fn` — the `skills_list` response now carries:
- a top-level **`next_step`** directive — when there are matches: "this is metadata only, NOT the runbook; you MUST `skills_load(name=...)` and follow every step including its output format; do NOT improvise." When there are no matches: "no skills matched — proceed with per-platform tools."
- a per-entry **`load_with`** field — the literal `skills_load(name='<skill>')` call, so the AI has the exact next call in front of it for each matched skill.

One change covers both the code-mode discovery-tool path and the dynamic-mode `@mcp.tool` path (shared body).

### Verified

- 2 updated/new tests in `test_skills.py::TestDiscoveryToolFactories` — the matched-result `next_step` + `load_with` fields, and the empty-result fallback directive.
- All unit tests + ruff + format + mypy clean.

## [3.1.0.11] - 2026-05-14

**Patch — rewrite the `cross-platform-rf-check` skill's Step 9 to a precise RF-planner widget layout.**

The v3.1.0.8 / v3.1.0.9 Step 9 described the *ingredients* of the visualization (floor plan, coverage rings, band toggle) but not the *layout*, so AI clients produced inconsistent, sub-par results. Operator feedback supplied a target screenshot of an excellent RF-planner widget; Step 9 now specs that layout prescriptively, top to bottom:

1. **Header** — `SITE <id> · <N> APs · <model>` eyebrow, `<site> · RF planner` title, band-toggle button group (EM-spectrum accent ramp: amber 2.4 / teal 5 / purple 6).
2. **Stats strip** — four cards (Active band · Avg utilization · Avg noise floor · Connected clients), active-band-only.
3. **Floor-plan canvas** — when no Mist map coordinates exist, **synthesize labelled room rectangles from AP names** (group indoor rooms in a "Main level" box, outbuildings as separate rectangles) rather than scattering dots on a blank canvas. Faint grid, AP markers with channel pills, concentric power-scaled coverage contours.
4. **AP cards sidebar** — per-AP `Ch · BW · dBm`, "Channel busy %" bar, noise/clients footer.
5. **Channel-plan strip** — active-band pills, co-channel collisions flagged.

Hard rule reinforced: **one band at a time** — the header toggle is the only switch; stats, canvas, cards, and channel strip all reflect just the active band. All names in the spec are generic format placeholders, with an explicit instruction to render the operator's real site/AP/room names from live data. The ASCII spectrum diagram remains the non-artifact fallback.

Skill-only + version + CHANGELOG; no Python touched. `test_skill_tool_references.py` still green (no tool changes).

## [3.1.0.10] - 2026-05-14

**Patch — a tool's `ToolError` no longer crashes the entire code-mode `execute()` block. Closes #333.**

When a platform tool dispatched via `<platform>_invoke_tool` raised `ToolError` — which `mist_request` does for **every** Mist 4xx/5xx — the exception propagated through the code-mode sandbox's `call_tool` and aborted the whole `execute()` block, taking every successful call in that block down with it. The AI saw `Sandbox error: Exception: {'status_code': 400, ...}` instead of an inspectable error.

Surfaced in an operator transcript: a code-mode RF-check session lost a successful `mist_get_site_current_channel_planning` result because a *later* `mist_get_site_channel_scores` call in the same block returned a 400.

### Fix

`platforms/_common/meta_tools.py::_invoke_tool` now catches `ToolError` and returns it as a structured error dict — matching its existing `not_found` / `forbidden` / `invalid_params` convention:

```python
except ToolError as exc:
    payload = exc.args[0] if exc.args else str(exc)
    if isinstance(payload, dict):
        return {"status": "tool_error", **payload}   # preserves status_code + message
    return {"status": "tool_error", "message": str(payload)}
```

`_invoke_tool` is the universal dispatch path `build_meta_tools` installs for all 7 platforms, so the one fix covers every platform. A Mist 400 now comes back as `{"status": "tool_error", "status_code": 400, "message": ...}` — the AI can inspect it and continue the block, or self-correct (e.g. the `mist_list_site_rrm_events` "valid band is required" 400 becomes a retryable error rather than a fatal crash).

### Verified

- 2 new tests in `test_meta_tools.py::TestInvokeTool` — dict-payload and string-payload `ToolError` both return `{"status": "tool_error", ...}` with no exception.
- All unit tests + ruff + format + mypy clean.

## [3.1.0.9] - 2026-05-14

**Patch — harden `cross-platform-rf-check` skill: response-shape guidance + RF-planner-style coverage-map visualization. Two fixes from operator transcripts.**

### Response-shapes table (crash fix)

An operator transcript showed a code-mode session crash with `AttributeError: 'list' object has no attribute 'get'` — the AI called `.get("items", ...)` on `mist_list_org_sites`'s `data`, which is a bare JSON array (post-#327 it correctly carries the payload). The skill never told the AI what shape `data` is per tool, so it guessed wrong.

Added a **Response shapes** section: a table mapping each of the skill's six tools to its `data` shape (bare array / plain dict / inner-`result`-wrapped) with the correct iteration pattern, plus the snake_case-vs-camelCase note (Mist `radio_stat` / `serial` vs Central `radioStats` / `serialNumber`). All shapes verified live against the maintainer's tenant.

### Step 9 — RF-planner-style coverage map (visualization rework)

The v3.1.0.8 Step 9 produced a channel-spectrum bar chart. Operator feedback: "ok for a first attempt but didn't come out how I'd like" — the target is what a real RF planner shows. Reworked the preferred HTML artifact spec to a **coverage map**: SVG floor-plan canvas with APs placed by Mist map coordinates (`x`/`y`/`map_id`) when present or a logical name-derived layout otherwise; concentric signal-strength coverage rings scaled by band + transmit power; 2.4/5/6 GHz band selector with an EM-spectrum colour ramp (amber/teal/purple); click-an-AP detail panel; per-band site-stats strip; co-channel flagging. No gradients/glows — solid fills with opacity. The ASCII spectrum diagram remains the fallback for non-artifact clients.

Skill-only + version + CHANGELOG; no Python touched. `test_skill_tool_references.py` still green (no new tools).

## [3.1.0.8] - 2026-05-14

**Patch — `cross-platform-rf-check` skill gains an interactive RF visualization step.**

The skill previously ended with the ASCII text report. It now has a **Step 9** that produces a channel-spectrum visualization the operator can explore, after the text report (never instead of it):

- **Preferred — self-contained HTML artifact** (when the client renders HTML artifacts, e.g. Claude.ai / Claude Desktop): inline CSS + vanilla JS, no external assets. One panel per band; each radio drawn as a block on its primary channel with width proportional to bandwidth (so channel overlaps are visible); fill color mapped to utilization; hover/click reveals per-AP detail; co-channel clusters flagged; Mist allowed-but-unused channels marked on the axis.
- **Fallback — rich ASCII spectrum diagram** (when the client can't render artifacts): the same information laid out spatially in monospace text, documented under *Interactive RF visualization* in the skill's output-formatting section.

No new tools referenced — the visualization renders from data the skill already collects in Steps 4–7. `test_skill_tool_references.py` still green.

## [3.1.0.7] - 2026-05-14

**Patch — fix code-mode payload loss + correct sandbox dispatch guidance. Closes #327 + #328.**

Both bugs surfaced from one operator transcript: a code-mode Claude session testing the `cross-platform-rf-check` skill reported `mist_list_site_devices_stats` "consistently returns null data."

### #327 — response envelope dropped bare-JSON-array payloads

Any tool whose endpoint returns a **bare top-level JSON array** came back as `{"ok": true, "data": null, ...}` — the payload silently discarded before the AI ever saw it.

**Root cause** (verified live in the dev container): FastMCP populates `structured_content` for a `-> Any` tool only when it returns a **dict**. A bare-list return under `-> Any` leaves `structured_content` as `None`, with the payload stranded in the `content` blocks as JSON text. The response envelope read only `structured_content`, so it wrapped `None` → `data: null`. Both the ~1000 generated Mist tools and every `<platform>_invoke_tool` meta-tool are `-> Any`, so this hit every `mist_list_*` call and every meta-tool dispatch to one. Confirmed live: `mist_list_org_sites` and `mist_list_site_devices_stats` both returned `data: null` against an org/site with real data.

**Fix** — `middleware/response_envelope.py`: new `_payload_from_content()` helper recovers the payload from the `content` TextContent JSON block when `structured_content` is `None`. Middleware-layer fix, so it covers every bare-array-returning tool on every platform, present and future. Dict-returning tools, already-enveloped responses, and non-JSON content are all unaffected (no regression). 13 new tests in `TestPayloadFromContent` + `TestContentFallbackRecovery`.

### #328 — `execute` description over-promised direct platform-tool dispatch

The `execute` tool description and INSTRUCTIONS.md told the AI that `call_tool` dispatches to platform tools "by names starting with `mist_`, `central_`, ...". True for hand-curated platforms, **false for Mist**: `call_tool("mist_get_self", {})` inside the sandbox raises `Unknown tool`. The ~1000 spec-driven Mist tools are registered with FastMCP but deliberately **not listed** in the catalog (keeps the surface small); CodeMode's sandbox `call_tool` resolves names against the *listed* catalog, so Mist tools are unreachable by bare name — only via `mist_invoke_tool`.

**Fix** — doc/guidance only:
- `server.py` — rewrote the `execute` description to steer the AI to `<platform>_invoke_tool(name=..., params=...)` as the universal dispatch path, explicitly noting the Mist tools are reachable *only* that way.
- `INSTRUCTIONS.md` — same correction in the code-mode discovery section: dispatch via `<platform>_invoke_tool`, not by bare tool name.

### Verified

- All 1249 unit tests + 1 skip pass; ruff + format + mypy clean.
- FastMCP `-> Any` vs `-> list` structured-content behaviour confirmed by direct dev-container probe before writing the fix.

## [3.1.0.6] - 2026-05-14

**Patch — new `cross-platform-rf-check` skill: a code-mode runbook equivalent of the `site_rf_check` tool.**

`site_rf_check` (and `site_health_check`, `manage_wlan_profile`, the WLAN sync tools) are registered **only in dynamic mode** — code mode deliberately omits the cross-platform aggregators on the premise that the AI composes per-platform tools itself. But operators on the default code-mode deployment hit "the AI can't find `site_rf_check`" with no guidance on what to do instead. This release closes that gap.

### New skill — `cross-platform-rf-check`

A bundled markdown runbook that walks the AI through the same RF / channel-planning check `site_rf_check` performs, but via individual per-platform tools so it works in code mode:

- **Mist** — `mist_list_org_sites` (resolve site), `mist_list_site_devices_stats` (per-AP `radio_stat`), `mist_get_site_current_channel_planning` (RF-template allowed channels)
- **Central** — `central_get_site_name_id_mapping` (resolve site), `central_get_aps` (list APs), `central_get_ap_details` (per-AP `radios` array)
- Aggregates per-band channel distribution + util + noise; flags co-channel clusters (3+ APs same channel on 5/6 GHz), airtime pressure (peak util ≥ 70%), elevated noise (> −70 dBm).
- Output structure matches `site_rf_check`'s ASCII RF dashboard for consistency.

Brings the bundled-skill count to **10**.

### Documentation fix

`INSTRUCTIONS.md` previously described all four cross-platform tools (`health`, `site_health_check`, `site_rf_check`, `manage_wlan_profile`) as if always available. It now explicitly flags that only `health` is registered in code mode, and points to the new skill for RF checks. The skill-mapping table gains a `cross-platform-rf-check` row.

### Verified

- `tests/unit/test_skill_tool_references.py` — all six per-platform tool names referenced by the new skill resolve to real registered tools.
- All unit tests + ruff + format + mypy clean.

## [3.1.0.5] - 2026-05-14

**Patch — rewrite source-masked secrets to `REPLACE_ME` during migration reads. Closes #276.**

Source platforms like AOS 8 mask shared secrets server-side: `show aaa rfc-3576-server <ip>` and `show aaa authentication-server radius <name>` both return `Key: "********"` rather than the cleartext value — the real secret never leaves the controller, even in a full flash backup.

Until now the redaction walker *skipped* masked placeholders — `********` flowed through unchanged. `********` reads as "redacted/hidden", which is ambiguous: an AI orchestrator can't tell whether there's a recoverable value behind it. This release rewrites the masked value to the literal directive `REPLACE_ME` — an unambiguous "operator must set this" marker. During an AOS 8 → Central migration the operator gets a clear to-do marker in the output instead of a vague mask.

### What changed

- **`redaction/rules.py`**:
  - New `FieldClassification.MASKED_SECRET` — `classify_field` returns this (instead of the bare `SKIP`) when `is_masked_placeholder(value)` is true.
  - New `MASKED_SECRET_PLACEHOLDER = "REPLACE_ME"` constant + `is_known_placeholder(value)` helper.
  - `classify_field` now checks `is_known_placeholder` first → `SKIP`. Critical guard: `REPLACE_ME` landing in an exact-match secret field like `coa_secret` / `shared_secret` would otherwise be tokenized, burying the operator signal behind an opaque token. This guard also keeps the walk idempotent.
- **`redaction/walker.py`** — `_walk_pair` handles the `MASKED_SECRET` classification by returning the literal `REPLACE_ME`.

### Scope

The descope from the originally-filed #276 is deliberate and confirmed with the maintainer: **no secrets vault, no synthesis, no ClearPass propagation.** The entire mechanism is the single `********` → `REPLACE_ME` walker rewrite. The operator sets the real value in Central themselves.

Gated on `ENABLE_PII_TOKENIZATION` — the rewrite happens via `classify_field`, which only runs when the tokenizer is active. Deployments with PII tokenization off still see `********` (unchanged behavior).

### Verified

- `TestMaskedSecretRewrite` (8 new tests): the rewrite, the `is_known_placeholder` guard, idempotency, `REPLACE_ME` not tokenized in an exact-match secret field, real secrets still tokenizing alongside masked ones, `detokenize_arguments` leaving `REPLACE_ME` untouched.
- Existing `TestIsMaskedPlaceholder` + `test_aos8_aaa_radius_detail_after_flatten_tokenizes_host` updated for the new `MASKED_SECRET` classification and `REPLACE_ME` output.
- All 1236 unit tests + 1 skip pass; ruff + format + mypy clean.

### Unblocks

- **#322** — the combined CoA + RADIUS migration tool. Its masked secrets become `REPLACE_ME` automatically via the walker; the tool needs no secret-handling logic of its own.

## [3.1.0.4] - 2026-05-13

**Patch — plug AOS 8 rfc-3576 detail-form wrapper-key IP leak + align CoA secrets to the RAD token family. Closes #319 + #321.**

### CoA secret realignment (#321)

CoA secrets joined the RAD token family because RFC-3576 ("Dynamic Authorization Extensions to RADIUS") is a RADIUS extension and the shared secret is reused on the same physical server. Operator decision: TACACS+ stays its own kind (different service); CoA endpoint identifiers (IPs / server names) stay `[[COA:uuid]]` (identifiers stay distinct per kind).

| Field | Before | After |
|---|---|---|
| `coa_servers[].secret` (Mist) | `[[COA:uuid]]` | `[[RAD:uuid]]` |
| `coa_secret` flat field (combined-tool output) | (no rule — cleartext) | `[[RAD:uuid]]` |
| `coa_servers[].ip` | `[[COA:uuid]]` | unchanged |
| `rfc_3576_server_list[].name` | `[[COA:uuid]]` | unchanged |

The realignment lets the forthcoming combined CoA + RADIUS migration tool (#322) emit the same plaintext in both `radius_secret` and `coa_secret` fields and have the keymap return a single `[[RAD:uuid]]` token across the entire structure — no walker-side cross-kind dedup or association map required.

---

### AOS 8 rfc-3576 wrapper-key IP leak (#319)

Live audit of the AOS 8 `show aaa rfc-3576-server <ip>` response shape surfaced a leak the structural-context rules didn't catch:

```json
{"RFC 3576 Server 192.168.20.70": [
    {"Parameter": "Key", "Value": "********"},
    ...
]}
```

The walker classifies fields by their *normalized* names — `rfc_3576_server_192.168.20.70` doesn't match any rule, so the IP-bearing wrapper key passed through to the AI cleartext. The list-form companion shape (`{"RFC 3576 Server List": [{"Name": "192.168.20.70", ...}]}`) was already covered by the v3.0.1.12 structural rule (#296); the detail-form wrapper was the remaining gap.

### What changed

- **`redaction/rules.py`** — added `WRAPPER_KEY_PATTERNS`, a list of `(regex, TokenKind)` pairs. The walker rewrites any matching dict key by tokenizing the captured substring in place. First entry: `re.compile(r"^RFC 3576 Server (?!List$)(\S+)$")` → `TokenKind.COA`. The negative lookahead excludes the list-form wrapper (`"RFC 3576 Server List"`), which is handled by the existing `rfc_3576_server_list[].name` structural rule on the list elements.
- **`redaction/walker.py`** — `_walk_dict` now calls `_rewrite_wrapper_key()` on each key before placing it in the output dict. Same token kind as the list-form rule (`COA`), so the same IP appearing in both the list and detail forms within one session resolves to a single `[[COA:uuid]]` token via the keymap — required for migration tooling that fans out across shapes.
- **`redaction/walker.py::_detokenize_walk`** — extended to detokenize dict KEYS, not just values. If the AI ever passes the rewritten wrapper-key dict back as an argument, the inbound walker restores the cleartext IP before the call hits the platform.

### Verified

- New test class `TestWrapperKeyRewrite` in `tests/unit/test_pii_redaction.py` covers four cases:
  - Rewrite: the IP-bearing wrapper key is replaced with the tokenized form
  - Same-token correlation: list-form and detail-form responses tokenizing the same IP share the same `[[COA:uuid]]` token within a session
  - Round-trip: `detokenize_arguments` on a dict carrying the rewritten key restores the cleartext IP
  - No-op: dicts whose keys don't match any wrapper pattern pass through unchanged
- All 1225 unit tests + 1 skip pass; ruff + format + mypy clean.

### Operator-facing detail

The AOS 8 single-server detail also returns the shared secret under `Parameter: "Key"` / `Value: "********"`. The `is_masked_placeholder` check skips tokenization on that placeholder — the real secret never leaves the controller, so there's nothing useful to tokenize. (Per the verified-live note in `feedback_aos8_secret_visibility.md`: AOS 8 server-side masks RADIUS / TACACS / RFC-3576 shared secrets but ships PSKs cleartext.)

## [3.1.0.3] - 2026-05-13

**Patch — rewires skills + INSTRUCTIONS.md to the v3.1.0.0 spec-driven Mist tool names. Closes #305.**

The v3.1.0.0 Mist refactor deleted 30+ hand-curated composite tools and replaced them with ~1000 spec-driven tools. The bundled skills and INSTRUCTIONS.md still referenced the deleted names, which made AI orchestrators hit "Unknown tool" errors at runtime when they followed skill guidance — observed organically during a 2026-05-13 test session where Claude walked into `mist_get_self`, `mist_get_configuration_objects`, `mist_list_upgrades` failures one after another.

This release rewires every active reference to its current spec-driven equivalent. The CHANGELOG entry for v3.1.0.0 had called this out as a known gap; #305 closes it.

### What changed

Per-skill rewires (8 files, ~20 distinct deleted-tool references):

- **`skills/mist-scope-audit.md`** — heaviest hit. `mist_get_configuration_objects(object_type=X)` composite calls fanned out to per-resource list/get tools: `mist_list_org_templates` (WLAN templates — the API endpoint is `/templates/` so the tool name lacks the "wlan" qualifier), `mist_list_org_rf_templates`, `mist_list_org_network_templates`, `mist_list_org_site_templates`, `mist_list_org_site_groups`, `mist_list_org_device_profiles`, `mist_list_org_psks`, `mist_list_org_device_upgrades`. `mist_get_org_or_site_info(info_type="setting")` → `mist_get_site_setting` / `mist_get_org_settings`. The step describing port profiles now points at `mist_list_org_network_templates` and the `port_usages` field nested within (port profiles aren't a standalone resource in the spec).
- **`skills/morning-coffee-report.md`** — `mist_search_audit_logs` → `mist_list_org_audit_logs`. `mist_search_alarms` → `mist_search_org_alarms`. `mist_search_client` → `mist_search_org_wireless_clients`. `mist_search_device(device_type=X)` → `mist_search_org_devices(type=X)` (parameter renamed). `mist_get_site_sle` → `mist_get_site_sle_summary`. `mist_get_insight_metrics` → `mist_get_site_insight_metrics`.
- **`skills/change-pre-check.md`** — `mist_search_alarms(org_id, site_id)` → `mist_search_site_alarms(site_id)`. `mist_search_audit_logs` → `mist_list_org_audit_logs`. `mist_get_configuration_objects(object_type="wlans", object_id=...)` → `mist_get_org_wlan` / `mist_get_site_wlan`. `mist_get_switch_details` and `mist_get_ap_details` both consolidate into `mist_get_site_device(site_id, device_id)` (resolve `site_id` first via `mist_search_org_devices`). `mist_search_device(device_type)` → `mist_search_org_devices(type)`. `mist_get_site_health` → `mist_get_site_sle_summary`.
- **`skills/change-post-check.md`** — `mist_search_alarms` and `mist_search_audit_logs` migrated to `mist_search_site_alarms` / `mist_list_org_audit_logs`.
- **`skills/infrastructure-health-check.md`** — `mist_search_alarms` → `mist_search_org_alarms`.
- **`skills/wlan-sync-validation.md`** — `mist_get_wlans()` (which used to accept either org or site scope) split into `mist_list_org_wlans` / `mist_list_site_wlans`; the prose now picks per scope.
- **`INSTRUCTIONS.md`** — `ID Resolution` table rewritten end-to-end. `mist_get_self` no longer takes `action_type=`. `mist_search_device` → `mist_search_org_devices`. `mist_search_client` split into `mist_search_org_wireless_clients` + `mist_search_org_wired_clients`. The `Port Bounce and PoE Bounce Safety Rules` device-lookup section now points at `mist_search_org_devices` → `mist_get_site_device` for the per-port detail. The v3.1.0.0 migration note text updated to reflect "rewire completed by #305 in v3.1.0.3" so future readers don't think the gap is still open.

### Test allowlist pruning

- `tests/unit/test_skill_tool_references.py` — dropped 28 of the 34 v3.1.0.0 Mist allowlist entries (no longer referenced anywhere after the rewire). The 6 names that remain (`mist_change_org_configuration_objects`, `mist_get_configuration_objects`, `mist_get_site_health`, `mist_get_wlans`, `mist_search_alarms`) appear only in historical-mention prose ("the v3.1.0.0-deleted `mist_get_site_health` composite now lives behind …"). The allowlist comment block updated to record this.

### Verified

- 10/10 `test_skill_tool_references.py` parametrized cases pass after rewire. The regex enforcer is now satisfied without the bulk allowlist.
- No skill or INSTRUCTIONS.md reference resolves to a deleted Mist tool name in active prose.

### Files

- **Modified**: `INSTRUCTIONS.md`, `skills/{mist-scope-audit,morning-coffee-report,change-pre-check,change-post-check,infrastructure-health-check,wlan-sync-validation}.md`, `tests/unit/test_skill_tool_references.py`, `pyproject.toml`

### Notes

- A handful of composite-tool semantics changed: e.g., `mist_search_device(device_type="ap")` becomes `mist_search_org_devices(type="ap")` — same intent, renamed parameter. Operators following the skill body get the right call shape; those who memorized the old names need to re-discover via `mist_list_tools(filter="<keyword>")`.
- Port profiles no longer exist as a standalone Mist resource per the spec — they live inside network template `port_usages`. The audit step now describes how to inspect them inline rather than calling a separate list tool.

## [3.1.0.2] - 2026-05-13

**Patch — `ValidationCatchMiddleware` now returns a properly-shaped envelope on Pydantic validation rejections. Closes #309.**

Before this fix, the middleware returned `ToolResult(content=error_text)` — text content only, no `structured_content`. Code-mode callers using `await call_tool(...)` received a bare string instead of the universal `{ok, status, data, message, tool, platform}` envelope, and any attempt to branch on `response.get("ok")` failed with `AttributeError: 'str' object has no attribute 'get'`.

Surfaced during a GPT troubleshooting session that called `central_get_clients(status="ACTIVE")` and `("CONNECTED")` against the Pydantic `Literal["Connected", "Failed"]` enum. Each rejection crashed the sandbox before the AI could recover with the correctly-cased value.

### What changed

- **`middleware/validation_catch.py`** — when catching `pydantic.ValidationError`, the middleware now builds an envelope via the same helpers `ResponseEnvelopeMiddleware` uses (`_build_envelope`, `_infer_platform` from `middleware/response_envelope.py`) and returns `ToolResult(content=error_text, structured_content=envelope)`. The envelope carries `ok=False, status=422, data=None, message=<readable error>, tool=<name>, platform=<inferred>`.
- **Idempotency preserved**: `ResponseEnvelopeMiddleware._is_envelope_shape` recognizes the structured payload by `{ok, data, tool}` key presence and passes it through unchanged. No double-wrap.
- **Existing behavior preserved**: text content is still set so clients that read the text channel see the same readable error.

### Test changes

- **New: `tests/unit/test_validation_catch.py`** — 6 unit tests covering: envelope shape contract (`ok=False`, `status=422`, `data=None`), readable message content, content / message parity, platform inference across all 7 platform prefixes + cross-platform tools (`health`, `execute`), pass-through for non-`ValidationError` exceptions, pass-through for normal results.

### Files

- **Modified**: `src/hpe_networking_mcp/middleware/validation_catch.py`, `pyproject.toml` (version)
- **New**: `tests/unit/test_validation_catch.py`

### Notes

- AI client code that does the standard `response = await call_tool(...); if response.get("ok"): ...` now branches cleanly through validation rejections — same code path as any other tool's error case.

## [3.1.0.1] - 2026-05-13

**Patch — adds two Central config-health diagnostic tools for the "device not achieving config sync" troubleshooting flow.**

These wrap the New Central Configuration API at `/network-config/v1alpha1/config-health/*` — endpoints we hadn't surfaced before. Operator-reported gap: an AI client troubleshooting a stuck-out-of-sync device couldn't query the config-health surface because the tools didn't exist.

### What's new

- **`central_get_device_config_issues(serial)`** — returns active configuration issues blocking config sync for a single device, plus recommended actions. Read-only.
- **`central_get_devices_config_health(limit, offset, sort, filter, search)`** — fleet-wide summary of configuration health. Pageable, sortable on every meaningful field (`activeIssues desc` for worst-offenders-first), OData-filterable, and free-text-searchable. Read-only.

### Files

- **New**: `src/hpe_networking_mcp/platforms/central/tools/config_health.py`, `tests/unit/test_central_config_health.py`
- **Modified**: `src/hpe_networking_mcp/platforms/central/__init__.py` (adds `config_health` category), `pyproject.toml` (version bump), `docs/TOOLS.md` (new tool entries).

### Notes

- README aggregate tool counts remain stale post-v3.1.0.0 (tracked in #307). The follow-up docs sync after the MemPalace experimentation period will refresh them.

## [3.1.0.0] - 2026-05-12

**Minor release (substantial new subsystem) — Mist platform rewritten as spec-driven tool generation. Drops the `mistapi` SDK dependency. Closes #304.**

Versioning note: this turns over the Mist tool surface wholesale, but the other six platforms (Central, ClearPass, Apstra, Axis, GreenLake, AOS 8) are unchanged. Consumers who don't use Mist see zero difference. Consumers who hardcoded specific old Mist tool names break — but most code-mode AI flows that discover via `mist_list_tools` don't.

The 35 hand-curated Mist tools that shipped through v3.0.1.15 carried recurring friction: non-conventional names (the `mist_get_configuration_objects(object_type="org_sites")` composite pattern wasn't guessable), narrow API coverage (35 of Mist's ~1000 endpoints), a three-way version coupling (Mist API → `mistapi` → our wrappers), and Mist-specific testing on every cross-cutting feature (PII, envelope, MAC normalization).

v3.1.0.0 replaces all of this. The vendored Mist OpenAPI spec at `vendor/mist_openapi.json` drives a generator that emits one tool per REST endpoint. The `mistapi` SDK is gone; a thin httpx client takes its place.

### What's new

- **`vendor/mist_openapi.json`** — vendored from upstream `mistsys/mist_openapi` (commit-pinned in `vendor/mist_openapi.SOURCE.md`). MIT-licensed. The upstream README disclaims the spec for code-generation use; risk mitigated by the spec driving Mist's own UI (catastrophic spec bugs would break the UI itself).
- **`platforms/mist/_generator.py`** — OpenAPI 3.x → Python tool functions. Parses paths × methods, resolves `$ref` parameters, maps OpenAPI types to Python type hints (string / int / bool / enum → `Literal[...]` / list / dict). Stable ordering across regenerations for clean PR diffs.
- **`platforms/mist/_client.py`** — direct httpx client. Replaces `mistapi.APISession` with ~270 lines. Auth header injection, org_id validation, pagination-header detection (`X-Next-Page` / `X-Page-Total`), structured error mapping.
- **`platforms/mist/regenerate.py`** — release-time CLI: `uv run python -m hpe_networking_mcp.platforms.mist.regenerate`. Cleans `tools/`, regenerates from spec, runs ruff format on output. Maintainer reviews the diff before tagging.
- **`platforms/mist/tools/` (regenerated)** — 210 per-tag modules, ~1000 generated tools following `mist_<snake_case_operationId>` convention (`mist_list_org_sites`, `mist_get_self`, `mist_create_org_wlan`, `mist_search_org_devices`, `mist_bounce_device_port`, etc.).
- **`.github/workflows/sync-mist-openapi.yml`** — daily auto-sync. Fetches upstream `mistsys/mist_openapi:master`, validates it parses cleanly as OpenAPI 3.x, auto-commits the updated spec + SOURCE.md to `main` (no PR, no tool regeneration). Tool regeneration stays a deliberate release-time step; this workflow only keeps the vendored spec current. If validation fails, files a tracking issue.

### Removed

- **`mistapi>=0.60.4`** dependency. Drops the SDK, its 45K-line `schemas_data.py` enum dump, and the three-way version coupling. The 10 lines of work `mistapi` did for us (auth header, `getSelf` helper) are reimplemented in `_client.py`.
- **`src/hpe_networking_mcp/platforms/mist/tools/*.py`** (the 35 hand-curated files) — replaced by the regenerated 210 per-tag modules.
- **`src/hpe_networking_mcp/platforms/mist/client.py`** (old SDK wrapper).
- **`src/hpe_networking_mcp/platforms/mist/tools/guardrails.py`** — the write-tool anti-pattern warnings (no place to inject them with auto-generated tools; revisit if specific anti-patterns become essential).
- **Lint exemptions** in `pyproject.toml`: `mist/tools/*.py = ["N801"]` and `mist/tools/schemas_data.py = ["E501", "E711"]` are gone. Generated tools follow our conventions cleanly (replaced with a single `["E501"]` carve-out for long auto-emitted parameter descriptions).
- **`tests/unit/test_mist_client.py`**, **`tests/unit/test_mist_dynamic_mode.py`**, **`tests/unit/test_guardrails.py`** — tested the removed surface.

### Cross-platform tools updated

- **`platforms/health.py`** — Mist probe rewritten to httpx (`client.get("/api/v1/self")`)
- **`platforms/manage_wlan.py`** — `_find_mist_wlan` rewritten to httpx
- **`platforms/site_health_check.py`** — `_collect_mist` + `_extract_mist_device_ips` rewritten to httpx (the latter became async)
- **`platforms/site_rf_check.py`** — `_collect_mist` + `_summarize_mist_sites` rewritten to httpx
- **`server.py:lifespan`** — replaces `mistapi.APISession` construction with `build_mist_client` + `resolve_org_id_from_self`. Cleanup-on-shutdown closes the httpx client.

### Known gaps shipping with v3.1.0.0

- **Skills + INSTRUCTIONS.md still reference old Mist tool names.** Tracked in #305. The v3.1.0.0-historical names are explicitly allowlisted in `tests/unit/test_skill_tool_references.py` so CI passes, but AI orchestrators following the old names will get "Unknown tool" errors at runtime. A follow-up PR rewires each call site to the new spec-driven name. Until then, the AI's path is: invoke `mist_list_tools(filter="<keyword>")` from inside `execute()` to discover the current tool name, then dispatch.
- **`mist_get_constants`** (the AOS-specific reference / enum catalog) has no spec-driven equivalent — Mist's constants endpoints are split per-category in the spec. Tools like `mist_list_const_alarm_defs`, `mist_list_const_applications` etc. cover the equivalent surface.

### Test changes

1202 passed (was 1258 in v3.0.1.15). The drop is from removing tests of the deleted surface (`test_mist_dynamic_mode.py`, `test_mist_client.py`, `test_guardrails.py`, two `test_code_mode.py` cases). The skill-references test still passes via the historical allowlist. Lint / format / mypy clean.

### Files

- **New**: `vendor/mist_openapi.json`, `vendor/mist_openapi.SOURCE.md`, `platforms/mist/_client.py`, `platforms/mist/_generator.py`, `platforms/mist/regenerate.py`, `.github/workflows/sync-mist-openapi.yml`
- **Regenerated**: `platforms/mist/tools/*.py` (210 files)
- **Modified**: `server.py`, `platforms/mist/__init__.py`, `platforms/mist/utils.py`, `platforms/health.py`, `platforms/manage_wlan.py`, `platforms/site_health_check.py`, `platforms/site_rf_check.py`, `utils/logging.py`, `INSTRUCTIONS.md`, `pyproject.toml`, `docker-compose.dev.yml` (vendor mount), `tests/unit/test_health.py`, `tests/unit/test_code_mode.py`, `tests/unit/test_skill_tool_references.py`
- **Removed**: `platforms/mist/client.py`, `platforms/mist/tools/*.py` (35 old hand-curated files), `tests/unit/test_mist_client.py`, `tests/unit/test_mist_dynamic_mode.py`, `tests/unit/test_guardrails.py`

### Notes

- **Backward-incompatibility**: Mist tool names changed wholesale. Operator-side scripts referencing specific old names will break.
- **Code mode AI experience**: `mist_list_tools` (in-sandbox meta-tool from v3.0.1.15) remains the canonical discovery path. The new generator produces ~30× more tools, so naive top-level catalog enumeration isn't useful; filtered queries are.
- **Live verification recommended after deploy**: from inside `execute()`, call `await call_tool("mist_get_self")` (should return privileges); call `await call_tool("mist_list_org_sites", {"org_id": "..."})` (should return the operator's sites).
- **Stale memory cleanup**: `project_mist_upstream_origin.md` (the "Mist tools ported from upstream mistmcp; conventions diverge" note) can be retired post-v3.1.0.0 — divergence ends with this release.

## [3.0.1.15] - 2026-05-12

**Tool-discovery hardening — three layered fixes targeting the "Mist intermittent" report from Mike Gallagher (2026-05-12, Sonnet 4.6). Closes #293 and #302.**

The reported symptom — *"Mist sometimes works, sometimes doesn't; Central works fine"* — turned out NOT to be a Mist platform bug. Live triage reproduced three layered tool-discovery failures that surface together. Central happens to work despite them because its tool names follow our `<platform>_<action>_<resource>` convention and the AI guesses correctly; Mist's names diverge (ported from Thomas Munzer's upstream mistmcp) so the AI can't guess and falls back on discovery, which was broken in three different ways.

### Layer A — Discovery tool descriptions rewritten

The top-level discovery tools (`tags`, `search`, `get_schema`, `skills_list`, `skills_load`) had generic descriptions like *"Search for available tools by query"* that lost client semantic ranking against more keyword-rich tools from other MCP servers attached to the same client (e.g. the Home Assistant MCP's tools ranked higher when the AI searched for "list mist sites"). Result: the client never surfaced our discovery tools, leaving the AI with only `execute` and no way to find platform tool names except by guessing.

`server.py` now subclasses FastMCP's `Search` / `GetTags` / `GetSchemas` with HPE-Networking-specific descriptions that name the seven platforms (`mist`, `central`, `aos8`, `clearpass`, `apstra`, `axis`, `greenlake`) and describe what they're for — listing sites, getting devices, searching events, managing config, checking health. The skill discovery descriptions in `skills/_engine.py` got the same keyword treatment.

### Layer B — Universal envelope no longer wraps discovery tools (closes #293)

The discovery tools ship with `x-fastmcp-wrap-result: true` output schemas that require a top-level `result` field (FastMCP convention: primitive returns get auto-wrapped as `{"result": <value>}`). When the universal envelope middleware (v3.0.0.0) wrapped them again as `{"ok": ..., "data": {"result": ...}, ...}`, output validation failed because the OUTER envelope has no top-level `result`. Result: when the AI *did* manage to call a discovery tool, it got `Output validation error: 'result' is a required property`.

`ResponseEnvelopeMiddleware` now passes through the five discovery tool names unchanged. They speak their own uniform shape that clients understand.

### Layer C1 — Per-platform meta-tools always registered

Each platform's `register_tools` had `if config.tool_mode == "dynamic":` gating the call to `build_meta_tools`. In code mode the meta-tools (`<platform>_list_tools`, `<platform>_get_tool_schema`, `<platform>_invoke_tool`) were NOT registered at all. Yet `INSTRUCTIONS.md:25` told the AI to call them inside `execute()` as the code-mode discovery path. Verified live 2026-05-12: `mist_list_tools` and `central_list_tools` both returned `Unknown tool` when invoked via `call_tool` inside `execute()`.

The gate is removed — meta-tools register unconditionally now. In dynamic mode they remain visible at the top level (current behavior unchanged); in code mode they're hidden by `CodeMode.transform_tools`'s catalog replacement but **remain callable via `call_tool` from inside `execute()`**. This gives the AI a foolproof in-sandbox discovery fallback that doesn't depend on the client surfacing the outer discovery tools.

Also: `execute_description` in `server.py` now teaches the in-sandbox discovery path explicitly, and `INSTRUCTIONS.md` describes both discovery paths (outer when the client surfaces them, in-sandbox as fallback).

### Files

- **`src/hpe_networking_mcp/middleware/response_envelope.py`** — added `_NO_ENVELOPE_TOOLS` skip set; early-return for the five discovery tool names.
- **`src/hpe_networking_mcp/server.py`** — added `_SEARCH_DESCRIPTION` / `_TAGS_DESCRIPTION` / `_GET_SCHEMA_DESCRIPTION` constants; subclassed `Search` / `GetTags` / `GetSchemas` to inject those descriptions; updated `execute_description` to teach the in-sandbox `<platform>_list_tools` discovery path.
- **`src/hpe_networking_mcp/skills/_engine.py`** — `_SKILLS_LIST_DESC` / `_SKILLS_LOAD_DESC` updated with platform keyword hooks.
- **`src/hpe_networking_mcp/platforms/<each>/__init__.py`** — removed the `if config.tool_mode == "dynamic":` gate on `build_meta_tools`. 7 platforms + 1 template.
- **`src/hpe_networking_mcp/INSTRUCTIONS.md`** — line 25 rewritten to describe both code-mode discovery paths accurately.
- **`tests/unit/test_response_envelope_middleware.py`** — added `TestDiscoveryToolBypass` with 5 parameterized passthrough tests + 1 non-discovery-sanity test.
- **`tests/unit/test_server_code_mode.py`** — added 3 tests: `test_execute_description_mentions_in_sandbox_discovery_path`, `test_discovery_tool_descriptions_carry_platform_keywords`, and `test_platform_init_registers_meta_tools_unconditionally` (parameterized across the 7 platform `__init__.py` files).
- **`pyproject.toml`** — bump 3.0.1.14 → 3.0.1.15.

### Test changes

1243 → 1258 passing (+15 net new). Lint + format + mypy clean.

### Notes

- **What this fix does NOT do.** It does not rename Mist tools to follow our `<platform>_<action>_<resource>` convention — that's a separate larger conversation with back-compat implications. The fix here gives the AI a reliable discovery path so the convention divergence doesn't matter.
- **Backwards-compatible.** No public tool removed. The 21 meta-tools that were code-mode-hidden now exist in code mode too, but as hidden registrations reachable only through `call_tool` inside `execute()` — they don't add to the visible surface count.
- **Live verification recommended after deploy.** From a Claude client with the MCP attached, ask *"list mist sites"* — the client should surface `hpe-networking:search` for semantic ranking (description hooks now help), and if it doesn't, the AI can fall back to `await call_tool("mist_list_tools", {"filter": "site"})` inside `execute()` and get a useful catalog.

## [3.0.1.14] - 2026-05-11

**Translations engine — `central:net_group` (AOS 8 `netdst` + `netdst6` → Central `/net-groups`).** Closes #300; references #279.

This is the fifth shipped translation and the **missing dependency for `central:policy`**. Before v3.0.1.14, `central:policy`'s rule bodies referenced `net-group` aliases by name (via `host-address-alias`) — but no current translation created those alias objects, so policy POSTs would fail at Central with an unknown-alias error unless the operator had pre-populated matching names in the target tenant. The Stage 8 disposition prose in v3.0.1.13 also misdescribed the architecture as if both `net_group` and `net_service` already shipped; corrected here.

### What ships

- **`translations/targets/central/net_group_v1.json`** — multi-source translation handling both `netdst` (IPv4) and `netdst6` (IPv6) AOS 8 source schemas. Two emits per source record: `POST /net-groups/{name}` + `POST /config-assignments`. The address-family discriminator (`netdestination-type` enum: `IPV4_ONLY` / `IPV6_ONLY` — Central explicitly doesn't support `IPV4_IPV6_MIXED`) is inferred by preprocessing from which `__entry` key the source record carries.
- **`translations/preprocessing/aos8_net_group.py`** — preprocessing module that:
  - Routes records to the right address family based on `netdst__entry` vs `netdst6__entry` presence.
  - Maps each per-entry `_objname` discriminator to a Central items[] element: `netdst__host` → `HOST` + `address`; `netdst__network` → `NETWORK` + computed `prefix` (CIDR); `netdst__name` → `FQDN` + `fqdn`.
  - Converts AOS 8 dotted-quad netmasks (e.g. `255.255.255.0`) to CIDR prefix lengths (`/24`) via `_netmask_to_prefix`. Non-contiguous masks (e.g. `255.0.255.0`) raise rather than silently corrupting the prefix.
  - Skips per-entry `_flags.default=true` / `_flags.system=true` markers. Record-level filtering (`inherited` / `default` / empty entries) is consumer responsibility, matching the convention in `central:role` and `central:policy`.

### Skill updates

- **`aos-migration.md` COLLECT-01** — `OBJECT_TYPES` extended with `netdst` and `netdst6` (CLI nouns `netdestination` / `netdestination6` differ from REST schema names — surfaced in the comment block).
- **`aos-migration.md` Stage 8 disposition matrix** —
  - `acl_sess` row corrected: describes the actual shipped architecture (`central:policy` references `net-group` aliases that ship via `central:net_group`; `net-service` aliases pending).
  - New row for `netdst` / `netdst6`: documents the `central:net_group` translation, the must-run-before-`central:policy` dependency, and per-entry mapping rules.
  - Source-type enumeration includes `netdst` and `netdst6`; clarifies CLI-vs-REST naming discrepancy and the `netsvc` deferral.
- **`aos-migration.md` Stage 9b** — adds preview block 2e for `central:net_group`. Block intentionally placed after policies in display order with a *"despite appearing last in the preview, this translation runs FIRST in execution"* call-out. Step 3 prose now says "five `result` dicts."

### Coverage scope

Live-verified against the maintainer's tenant: 8 operator-authored `netdst` aliases (mix of host, network, FQDN entries; one alias holds ~100 CIDR rows). `netdst6` schema is recognized but the tenant has zero records — first tenant with IPv6 aliases configured will validate the assumed sibling-naming shape; the preprocessing function detects v4 vs v6 by which `__entry` key is present so a `netdst6` record matching the documented shape works without code change.

### `central:net_service` deferred

Per the real-captured-fixtures-only convention (memory: `feedback_real_captured_fixtures.md`), the `central:net_service` translation is **not authored** in this release. The maintainer's tenant has zero `netsvc` records — the schema is recognized but unused. AOS 8 `acl_sess` rules in this tenant reference only Central's built-in `svc-*` catalog (which `central:policy` already passes through verbatim via `services.net-service` + `RULE_NET_SERVICE`). Will revisit once a tenant with custom `netsvc` records becomes available.

### Files

- **`src/hpe_networking_mcp/translations/targets/central/net_group_v1.json`** — new translation file.
- **`src/hpe_networking_mcp/translations/preprocessing/aos8_net_group.py`** — new preprocessing module.
- **`src/hpe_networking_mcp/skills/aos-migration.md`** — COLLECT-01, Stage 8 (disposition matrix + source-type enum), Stage 9b (preview block + counts).
- **`tests/unit/test_translations_preprocessing_aos8_net_group.py`** — new preprocessing unit tests (24 tests covering address-family detection, all three entry-type mappings, mixed-entry order preservation, per-entry flag filtering, IPv6 path including the `/128` fallback for prefix-less network entries, netmask → CIDR parametrized over 6 contiguous + 4 non-contiguous cases).
- **`tests/unit/test_translations_engine.py`** — appends 9 new engine-level tests covering the net_group translation end-to-end (host / network / FQDN / mixed / v6 / device-function override / missing-source / preprocessing error propagation).
- **`pyproject.toml`** — bump 3.0.1.13 → 3.0.1.14.

### Notes

- **Dependency order at execution time:** `central:net_group` must run BEFORE `central:policy` in any consumer-orchestrated migration. The Stage 9b preview reflects this in prose; Phase 3 execution (issue #240) will enforce it via the translation file's `dependencies` block.
- **Idempotency:** if a `net-group` profile with the same name already exists, the POST returns HTTP 409. Consumer must handle 409 idempotently.
- **Tests:** 1206 → 1243 passing (+37 net new). Lint + format + mypy clean.

## [3.0.1.13] - 2026-05-11

**Patch release — `aos-migration` skill drops `acl_eth` (Ethertype ACL) and `acl_mac` (MAC ACL) from Stage 1 collection. Closes #298.**

Live probe against the maintainer's tenant via `aos8_get_effective_config` returned:

- **`acl_eth`** — three records total: one platform default (`validuserethacl` with `_flags.default=true`) plus two operator-authored test ACLs (`test_ethertype` at `/md/Campus`, `deny_all_ethertype` at `/md/Campus/West`). None carried an auto-generated marker; none followed a role-pair naming pattern.
- **`acl_mac`** — zero records anywhere; the schema is recognized but unused.

The decision was operator-driven (no automated migration path even when present). The maintainer confirmed these are unique-use cases unlikely to be encountered in real migrations; the cost of carrying them through Stage 1 collection + Stage 2 normalization + Stage 7 per-scope inventory + Stage 8 disposition + Stage 9 translation gap handling exceeds the value.

### Files

- **`src/hpe_networking_mcp/skills/aos-migration.md`** —
  - COLLECT-01 `OBJECT_TYPES` list: removed `acl_eth`, `acl_mac` (replaced with a comment noting the issue-#298 scope decision).
  - Stage 2 normalization: removed the parenthetical about collecting Ethernet/MAC ACLs separately from `session_acls`.
  - Stage 7 per-scope inventory table header: removed `acl_eth` and `acl_mac` columns (and the corresponding `…` cells in the sample rows).
  - Stage 8 disposition matrix row for ACLs: narrowed to `acl_sess` only; updated the disposition prose to reflect the engine-driven `central:policy` translation that supersedes the obsolete `net_group + net_service + role_acl` framing. Added an explicit out-of-scope note pointing at issue #298.
  - Stage 8 source-type enumeration: removed `acl_eth`, `acl_mac` from the schema-name list; added a parenthetical Notes block.
  - Stage 9b "Ethertype ACL out of scope for central:policy" paragraph: replaced with a narrower note advising operators to leave the binding noted in the disposition row but NOT attempt to translate it, since Stage 1 no longer enumerates these ACL types.
  - Stage 9b "Findings produced" clause: removed the now-redundant Ethernet ACL OPERATOR-MAP clause.
- **`src/hpe_networking_mcp/INSTRUCTIONS.md`** — REST-schema-names example narrowed to `acl_sess` only (no longer cites `acl_eth` / `acl_mac`).
- **`pyproject.toml`** — bump 3.0.1.12 → 3.0.1.13.

### Notes

- **Translations engine checklist (issue #279):** the previously-listed `central:acl_eth` and `central:acl_mac` translations are now formally out of scope for v1. They were never authored.
- **Forward path:** if a future tenant configures non-trivial Ethernet ACLs that need migration, we'll revisit (re-add to COLLECT-01 and scope a `central:acl_eth` translation). The captured fixtures above demonstrate this is rare enough to defer indefinitely.
- 1206 tests pass; no test changes were required (existing skill-discovery tests verify shape, not content).

## [3.0.1.12] - 2026-05-11

**Patch release — PII privacy-model refinement. Two related changes: (a) drop tokenization of network-architecture schema labels that aren't personally-identifying (`vlan_name`, `subnet_name`, `org_name`, `site_name`), (b) add the missing CoA / RFC-3576 dynamic-authorization rules so dynamic-authorization endpoint IPs + shared secrets — which are auth-fabric-critical — actually get tokenized.**

The trigger was the live tenant work that produced v3.0.1.6–v3.0.1.10. Walking the live config surfaced two categories of mismatch between what the ruleset tokenized and what was actually sensitive:

1. **Over-coverage of schema labels.** `vlan_name`, `subnet_name`, `org_name`, `site_name` were all tokenizing to `[[NAME:uuid]]`. None of these are personally-identifying — `vlan_name` and `subnet_name` describe network architecture (and `scope_name` / `device_group_name` already pass through cleartext per the v2.3.1.3 design); `org_name` / `site_name` are typically findable on the company's public website or partner directory. Tokenizing them cost audit utility (operators couldn't refer to "the Corporate VLAN" by name in chat) without buying privacy.
2. **Under-coverage of critical-infrastructure CoA endpoints.** AOS 8's `show aaa rfc-3576-server` returns `{"RFC 3576 Server List": [{"Name": "192.168.20.70", ...}]}`. The bare `Name` child had no rule, and IPs aren't tokenized in general (v2.3.1.2 carve-out). Same story for Mist's `coa_servers` schema entries (`ip`, `secret`). Result: dynamic-authorization server IPs and shared secrets were leaking through cleartext. Per the operator's call-out: *"You left out radius server address, dynamic authorization server address, tacacs server address, and tacacs secret. I know we said IP addresses would be fine to display but these are critical infrastructure related items."*

### Privacy-model changes

| Field / wrapper shape | Before v3.0.1.12 | After v3.0.1.12 |
| --- | --- | --- |
| `vlan_name: "Corporate"` | `[[NAME:uuid]]` | cleartext (schema label) |
| `subnet_name: "Guest-Subnet"` | `[[NAME:uuid]]` | cleartext (schema label) |
| `org_name: "Acme Networks"` | `[[NAME:uuid]]` | cleartext (publicly findable) |
| `site_name: "HQ"` | `[[NAME:uuid]]` | cleartext (publicly findable) |
| AOS 8 `{"vlan_name": [{"name": "guest"}]}` | `[[NAME:uuid]]` (issue #289) | cleartext |
| AOS 8 `{"vlan_name_id": [{"name": "user", ...}]}` | `[[NAME:uuid]]` (issue #289) | cleartext |
| AOS 8 `{"RFC 3576 Server List": [{"Name": "192.168.20.70"}]}` | cleartext (leak) | `[[COA:uuid]]` |
| Mist `coa_servers[].ip` | cleartext (leak) | `[[COA:uuid]]` |
| Mist `coa_servers[].secret` | cleartext (leak) | `[[COA:uuid]]` |

`TokenKind.NAME` is removed from the enum; `TokenKind.COA` replaces it.

### Kind-agnostic plaintext dedup (Tokenizer.tokenize)

A CoA shared secret is conventionally the same string as the RADIUS shared secret on the same auth fabric. Per the operator: *"That server would use the same secret as the radius servers since they are typically the same."* Without dedup, the response payload `{"radius_servers": [{"shared_secret": "X"}], "coa_servers": [{"secret": "X"}]}` would emit two distinct tokens for the same plaintext, breaking round-trip reuse.

`Tokenizer.tokenize()` now consults the kind-agnostic `by_plaintext_value` reverse index *before* allocating a fresh token. If the plaintext was previously tokenized under any other kind in the same session, the existing token is returned (and stashed under the new `(kind, plaintext)` key so subsequent same-kind lookups hit the cache directly). Walker traversal order determines which kind label "wins" — the dict's natural insertion order, which for the typical RADIUS-then-CoA payload means RAD allocates first and CoA inherits.

### Files

- **`src/hpe_networking_mcp/redaction/rules.py`** —
  - Removed `TokenKind.NAME`.
  - Added `TokenKind.COA`.
  - Removed `site_name`, `org_name`, `vlan_name`, `subnet_name` from `TOKENIZED_IDENTIFIER_FIELDS` (replaced with a NOTE explaining the v3.0.1.12 design).
  - Removed `(vlan_name, name)` and `(vlan_name_id, name)` from `STRUCTURAL_IDENTIFIER_CONTEXTS`.
  - Added `(rfc_3576_server_list, name)` and `(coa_servers, ip)` to `STRUCTURAL_IDENTIFIER_CONTEXTS`.
  - Added `(coa_servers, secret)` to `STRUCTURAL_SECRET_CONTEXTS`.
- **`src/hpe_networking_mcp/redaction/tokenizer.py`** — `tokenize()` consults `by_plaintext_value` before allocation for kind-agnostic dedup. Comment block on the reverse index updated to reflect that the index is now single-writer per plaintext.
- **`src/hpe_networking_mcp/redaction/token_store.py`** — `SessionKeymap.by_plaintext_value` docstring updated to describe the dedup behavior.
- **`src/hpe_networking_mcp/INSTRUCTIONS.md`** — token-kinds list updated: removed `NAME`, added `COA`. Carve-out section now explicitly lists schema labels (`vlan_name`, `subnet_name`, `org_name`, `site_name`, `scope_name`, `device_group_name`) as cleartext.
- **`tests/unit/test_pii_redaction.py`** —
  - Replaced `TestStructuralIdentifierContexts` (vlan_name) with `TestSchemaLabelPassthrough` (parameterized cleartext assertion for all four removed fields + companion check for the removed `(vlan_name, name)` structural rule).
  - Replaced `TestStructuralIdentifierContextsEndToEnd` with `TestStructuralCoaContexts` + `TestStructuralCoaContextsEndToEnd` (AOS 8 + Mist response-shape coverage).
  - Rewrote `TestKeymapReplayOnSkipPath` to use the new CoA structural rule for setup (the old vlan_name rule is gone).
  - Added `TestKindAgnosticDedup` (4 unit + 1 walker e2e test).
  - Updated `test_wlan_profile_walk` to assert `vlan_name` passes through cleartext.
- **`pyproject.toml`** — bump 3.0.1.11 → 3.0.1.12.

### Notes

- **Coverage scope of this release.** AOS 8 CoA (verified live via `show aaa rfc-3576-server`) + Mist CoA (verified against `schemas_data.py`'s `coa_servers` entry). **Central CoA tokenization is deferred** — the modern `network-config/v1alpha1` Central tenant we probed against does not currently expose CoA / dynamic-authorization endpoint detail through any MCP-wrapped tool. `central_get_server_groups` returns name-only references (`server-name`, `position`), `central_get_wlan_profiles` doesn't expose CoA fields, and `central_get_effective_config` at the root scope didn't surface the detail. The Central `auth-servers` detail endpoint isn't wrapped today. A follow-up release will add a Central auth-servers read tool and the corresponding structural rule.
- **Round-trip behavior with shared RADIUS / CoA secrets.** Both the `shared_secret` (under `radius_servers`) and `secret` (under `coa_servers`) fields now produce the *same* `[[RAD:uuid]]` token within a session when the operator has configured them as the same value. Detokenization round-trips correctly to the original plaintext via either tool.
- **Backwards-compatible.** No removed-tool surface or breaking config changes. Operators do not need to re-cache anything; the keymap is per-session and lives in memory only.
- **Live verification recommended after deploy.** Walk an AOS 8 controller config that contains `aaa server-group authentication-server <name>` with a CoA server reference (or a Mist WLAN with a populated `coa_servers` list). Confirm `[[COA:uuid]]` appears for the endpoint + secret. Confirm `vlan_name` / `site_name` come back as cleartext.

## [3.0.1.11] - 2026-05-08

**Patch release — INSTRUCTIONS.md additions targeting the small-local-model orchestration issues from Zach's continued OpenClaw + Qwen3 4B test report. Two prose changes; no code, no skills, no tools.**

The continued report surfaced several model-side failure modes that don't have direct server-side fixes — they're mitigated by clearer prompt language. Two specific gaps the existing instructions didn't cover:

1. **Sandbox-stdlib reference.** The `execute_description` in `server.py` documents some blocked items (`asyncio.gather`, `datetime.now`, `time.time`, file I/O, `os.environ`, `subprocess`) but doesn't name `hashlib` (verified blocked by Zach's continued report) or `yield` / `yield from` (verified blocked in v3.0.1.9 regression testing). Operators authoring skill snippets had no single place to look up "what's allowed in `execute()`?". Added a Sandbox-stdlib reference section under the existing `Code-mode execute() patterns` section in INSTRUCTIONS.md with a known-working / known-blocked table and substitute guidance per blocked item. Note that the table will grow as more failures surface — and the corresponding `tests/unit/test_skill_snippet_sandbox_compat.py` lint (added v3.0.1.10) is the enforcement side of the same evidence.

2. **Tool-call-first idiom for identifier queries.** Existing `CRITICAL RULES` rule #3 (*"Only answer based on data returned by tools"*) is generic. The continued report showed Qwen reliably skipping tool calls and answering from training-data memory or earlier-session context — even when the user's question named a specific identifier (AP name, scope name, ACL name, etc.). Tightened rule #3 with an explicit "you MUST first call the matching read tool" obligation when a question names any specific identifier, plus a worked good/bad example showing the difference between calling `central_get_ap_details(ap_name="corp-ap-01")` first vs. answering from stale memory.

### Files

- **`src/hpe_networking_mcp/INSTRUCTIONS.md`** — new Sandbox-stdlib reference section under `Code-mode execute() patterns`; expanded `CRITICAL RULES` rule #3 with the tool-call-first idiom + worked example.
- **`pyproject.toml`** — bump 3.0.1.10 → 3.0.1.11.

### Notes

- 1196 tests pass (no test-count change — pure docs release).
- These are the two model-side issues from Zach's continued report that the existing instructions didn't already cover. Other model behaviors (`async def run()` wrapping, large-payload final-answer truncation, fabricated counts, bounded-output patterns) were already addressed by v3.0.1.5 / v3.0.1.7 INSTRUCTIONS.md additions and Stage 9b prose. The aos-migration skill carries explicit anti-fabrication language ("Use the engine's deterministic counts — never hand-fabricate").
- The new Sandbox-stdlib reference table is intentionally living documentation. Issue templates around skill-snippet bugs should reference it; `test_skill_snippet_sandbox_compat.py` enforces the blocklist mechanically.

## [3.0.1.10] - 2026-05-08

**Patch release — `central-scope-walker` skill snippet rewritten to stack-based iteration. The shipped recursive-generator form was rejected by the MCP code-mode sandbox (`NotImplementedError: The monty syntax parser does not yet support yield expressions`), making the skill non-functional. Reported by Zach via ChatGPT regression testing of v3.0.1.9.**

Plus a regression-prevention test that catches sandbox-incompatible Python in any shipped skill snippet at CI time.

### Bug

`central-scope-walker.md` (and the matching walker snippet in `aos-migration.md` Stage 9b's Step 1) used:

```python
def walk(node, path):
    here = path + [...]
    yield {...}
    for child in node.get("children") or []:
        yield from walk(child, here)
```

The MCP sandbox uses `pydantic-monty` for its Python parser, which currently rejects `yield` / `yield from`. The skill loaded fine via `skills_load`, but the moment the AI pasted the snippet into `execute()`, the sandbox returned `NotImplementedError: The monty syntax parser does not yet support yield expressions` — the operator's actual `central-scope-walker` query failed despite the skill being advertised as paste-and-go.

Verified by Zach's regression run: a stack-based rewrite of the same logic resolved the same scope query (`Owls Nest New Central` → scope_id `46237598667`, type `SITE`, path `<root>/Owls Nest Collection/Owls Nest New Central`, 7 devices, 38 scopes walked).

### Fix

1. **Rewrote both walker snippets to iterative depth-first traversal via an explicit stack.** Same data shape produced, no generators. The traversal is now pure list/loop ops — exactly the kind of idiom small models can paste reliably.

2. **Added `tests/unit/test_skill_snippet_sandbox_compat.py`** — a regression test that scans every shipped skill markdown for sandbox-incompatible Python in fenced `python` code blocks. Catches:
   - `yield` / `yield from` (this incident)
   - `async def` (the v3.0.1.5 `async def run()` rule — already in INSTRUCTIONS.md, now enforced for skills)
   - `import hashlib` (Zach's continued report — sandbox-blocked)
   - Internal-module imports (`import hpe_networking_mcp.*`)
   - Other documented sandbox limits: `datetime.now()`, `time.time()`, `os.environ`, `subprocess`, `asyncio.gather()`

   Comments are stripped before scanning so rationale-comments like `# sandbox parser rejects yield` don't false-positive. Per-rule violation messages reference the upstream sandbox limitation so future authors know what to substitute.

### Files

- **`src/hpe_networking_mcp/skills/central-scope-walker.md`** — walker snippet rewritten to stack-based iteration
- **`src/hpe_networking_mcp/skills/aos-migration.md`** — Stage 9b Step 1's walker snippet rewritten the same way
- **New: `tests/unit/test_skill_snippet_sandbox_compat.py`** — 10 tests (9 parameterized per-skill + 1 sanity check)
- **`pyproject.toml`** — bump 3.0.1.9 → 3.0.1.10

### Notes

- 1196 tests pass (was 1186; +10 new sandbox-compat tests).
- The sandbox-compat test runs on **every** shipped skill, not just the two with walker snippets. Caught nothing else this round but will catch the next instance of any author pasting Python that the sandbox rejects.
- A separate issue (#293) is filed for an unrelated sandbox-adjacent bug Zach reported: the `search` discovery tool returns `Output validation error: 'result' is a required property` for some queries. Investigation deferred — non-blocking; AI clients can fall back to `tags` or per-platform `<platform>_list_tools`.

## [3.0.1.9] - 2026-05-08

**Patch release — fixes #291: walker keymap-replay on outbound SKIP path. Closes the round-trip leak that v3.0.1.8 surfaced — values tokenized once in a session now stay tokenized across every tool's outbound, even when the output field name carries no rule.**

### Bug

After fixing #289 in v3.0.1.8, AOS 8 read responses correctly tokenize VLAN names via the new `(vlan_name, name)` structural rule. The AI receives tokens. **But** the round-trip through any downstream tool re-leaks them — verified live against tenant on v3.0.1.8 (image label confirmed v3.0.1.8).

Concretely, the `aos-migration` Stage 9b flow:

1. `aos8_get_effective_config(object_name="vlan_name")` → middleware tokenizes outbound → AI receives `[[NAME:1]]` ✓
2. AI calls `central_translation_preview(source_records=[{"name": "[[NAME:1]]"}, ...])`
3. Middleware **detokenizes inbound** so the tool sees cleartext `"guest"` (this is by design — tools always see cleartext)
4. Tool returns `{"results": [{"record_id": "guest", "sample_body": {"name": "guest"}, ...}]}`
5. Middleware outbound: walker checks rules. `record_id` has no rule. `name` under `sample_body` parent has no rule. **Both pass through cleartext.**
6. AI's summary uses cleartext.

The session keymap already mapped `"guest" → [[NAME:1]]` from step 1. The walker just didn't consult it on subsequent outbounds.

### Fix

**Walker keymap-replay on SKIP path.** When the walker classifies a string value as `FieldClassification.SKIP` (no field rule, no structural-context rule), it now asks the session tokenizer: "have you seen this exact cleartext before?" If yes, restore the existing token. Properties:

- **Keymap-driven, not heuristic.** Only values that have been tokenized via field rules (and recorded in the keymap) get restored. Cleartext values that were never tokenized in this session stay cleartext — no false positives.
- **Bounded.** O(1) keymap lookup per string value walked.
- **Fixes every tool automatically.** Not specific to `central_translation_preview`.
- **Round-trip-safe.** A token issued for `"guest"` in session N gets the SAME token restored anywhere `"guest"` appears in session N's outputs, regardless of which field it lands at.
- **Idempotent.** Existing `[[KIND:uuid]]` token-shaped strings pass through; we never tokenize a token.

### Implementation

1. **`SessionKeymap` gains a third index:** `by_plaintext_value: dict[str, TokenEntry]` alongside the existing `by_plaintext[(kind, plaintext)]` and `by_token[token]`. Kind-agnostic — last writer wins on the rare case where the same plaintext is allocated under multiple kinds in one session.
2. **Tokenizer.tokenize populates the new index** alongside the existing two.
3. **New `Tokenizer.token_for_existing_cleartext(value: str) -> str | None`** method does the reverse lookup. Returns None for empty strings, non-strings, and values that look like existing tokens.
4. **Walker `_walk_pair` SKIP path** consults the tokenizer's keymap-replay BEFORE running the universal scan. If a token is restored, return it; otherwise fall through to universal scan (which still handles embedded patterns like emails / AWS-signed URLs).

### Files

- **`src/hpe_networking_mcp/redaction/token_store.py`** — adds `by_plaintext_value` index to `SessionKeymap`
- **`src/hpe_networking_mcp/redaction/tokenizer.py`** — populates the new index in `tokenize`; adds `token_for_existing_cleartext` method
- **`src/hpe_networking_mcp/redaction/walker.py`** — wires keymap-replay into `_walk_pair`'s SKIP path
- **`tests/unit/test_pii_redaction.py`** — adds `TestKeymapReplayOnSkipPath` with 6 tests (round-trip, nested-structure round-trip, negative case, idempotency, direct API check, and the realistic `central_translation_preview` shape end-to-end)
- **`pyproject.toml`** — bump 3.0.1.8 → 3.0.1.9

### Notes

- 1186 tests pass (was 1180; +6 new).
- **Closes #291.**
- **Live verification recommended after the new image rolls.** Re-run Stage 9b against the tenant; the VLAN names that came through cleartext on v3.0.1.8 should now appear as `[[NAME:uuid]]` tokens — both in the summary table's `name`/`record_id` column AND in the sample TargetCall body fields.
- **The fix benefits every tool, not just `central_translation_preview`.** Any tool that emits a previously-tokenized value at a SKIP-classified field now restores the original token. Examples: `aos-migration` Stage 9b's `summary` dict; `change-pre-check` baseline snapshots that re-serialize names without their original wrappers; future translation-execute tools that emit POSTed-body confirmations.
- **No new tokenization happens via this path.** Replay only restores tokens that were already issued by the existing field-rule path. Untokenized cleartext stays cleartext.

### Out of scope

- Adding new field rules for role/ACL names (`rname`, `accname` aren't in any rule today). Separate scope decision; tracked elsewhere.
- Mist / Central site list audit. Different wrappers; same shape pattern; needs its own audit.

## [3.0.1.8] - 2026-05-08

**Patch release — fixes #289: walker structural-identifier rule for AOS 8 list-of-dicts identifier shapes. Production VLAN names that were leaking through cleartext now tokenize correctly.**

### Bug

The PII walker's field-name rule for `vlan_name → NAME` (in `redaction/rules.py:208`) only fires when a string value sits *directly* at a `vlan_name` key. AOS 8's actual response shape is:

```json
{"_data": {"vlan_name": [{"name": "guest"}, {"name": "local"}]}}
```

The walker walks the list with `parent_field_name="vlan_name"`, then walks each `{"name": "guest"}` dict — at this point the inner key is `"name"`, which isn't in the field-rule dict. No structural-context rule paired `(vlan_name, name)` either; the existing `STRUCTURAL_SECRET_CONTEXTS` only covered RADIUS/TACACS shared secrets per #277. Result: VLAN names slipped through cleartext on production data. Verified empirically against a live tenant during v3.0.1.6 Stage 9b runs (`guest`, `local`, `vlan20` all unredacted).

### Fix

1. **New `STRUCTURAL_IDENTIFIER_CONTEXTS` table in `redaction/rules.py`** — parallel to the existing `STRUCTURAL_SECRET_CONTEXTS`. Same `(parent_field_name, child_field_name) → TokenKind` shape; classifies as `TOKENIZE_IDENTIFIER` instead of `TOKENIZE_SECRET`.

2. **Wired into `classify_field()`** after the existing structural-secret check and before the field-name lookup. The masked-placeholder skip still runs first so AOS 8's `"********"` placeholders aren't tokenized into the dangerous-illusion shape (#275).

3. **Added the AOS 8 vlan_name patterns:**
   - `(vlan_name, name): TokenKind.NAME`
   - `(vlan_name_id, name): TokenKind.NAME`

4. **Six new tests** (parallel to `TestStructuralSecretContexts`):
   - 4 isolation tests: rule fires for `(vlan_name, name)` and `(vlan_name_id, name)`; bare `name` outside known wrappers still skipped; `name` under unrelated wrapper still skipped.
   - 2 end-to-end walker tests against the realistic AOS 8 response shape verifying the inner names get tokenized AND non-name fields (`vlan-ids`) survive cleartext.

### Files

- **`src/hpe_networking_mcp/redaction/rules.py`** — adds `STRUCTURAL_IDENTIFIER_CONTEXTS` + `(vlan_name, name)` + `(vlan_name_id, name)` rules; extends `classify_field` to consult the new table.
- **`tests/unit/test_pii_redaction.py`** — adds `TestStructuralIdentifierContexts` (4 isolation tests) + `TestStructuralIdentifierContextsEndToEnd` (2 walker e2e tests).
- **`pyproject.toml`** — bump 3.0.1.7 → 3.0.1.8.

### Notes

- 1180 tests pass (was 1174; +6 from the new structural-identifier tests).
- **Closes #289.**
- **Live verification recommended after deploying.** Re-run Stage 9b against the tenant; confirm VLAN names appear as `[[NAME:uuid]]` tokens in tool output. The unit tests prove the rule wires correctly against the documented AOS 8 shape; live verification confirms the actual production response matches.

### Out of scope (still open)

- Role / ACL name tokenization. AOS 8 uses `rname` (roles) and `accname` (ACLs), not `name`. Those fields aren't in any rule today. Separate scope decision; not this release.
- Mist / Central site list audit (`org_sites`, `sites`). Different wrapping field names; needs its own audit. File separately if needed.
- The diagnostic-dict over-fire (cosmetic) where a literal `"dict"` string at a `vlan_name` key gets tokenized — harmless and rare. Not addressed; would require redesigning the field-name rule to be shape-aware, which is a much bigger change.

## [3.0.1.7] - 2026-05-08

**Patch release — `aos-migration` Stage 9b prose tightening from a live-run review against Jon's tenant. Five skill-prose fixes; no Python / engine / tool changes.**

First real run of Stage 9b (added in v3.0.1.6) surfaced a handful of skill-prose issues. The bridge tool fired correctly and produced deterministic engine output for all four translations, but the AI's report missed things the skill should have explicitly directed:

1. **Walker is now optional with placeholder fallback.** Stage 9b previously read as if walker resolution was a hard prerequisite. In practice, the target Central hierarchy doesn't need to exist yet — Stage 9 builds it as the first cutover step; Stage 9b just previews what gets POSTed afterward. When walker returns no match for a Stage-7 Central scope name, the skill now substitutes `<TBD:<name>>` as the scope_id and continues. The engine accepts any string for `central_scope_id` (it just substitutes), so the resulting body's `scope-id` field reads `<TBD:USE/West>` — exactly the right "this scope must be created before execution" signal. Output report flags placeholder vs resolved scope status loudly. Stage 7 is also softened from required to recommended; if the operator skips Act I and runs straight to Stage 9b, Global is the documented fallback.

2. **Empty-rule-list filter for `central:policy`.** Five AppRF system-companion ACLs (`apprf-*-sacl`) plus two non-AppRF ACLs (`transition`, `blacklisted`) leaked through to the engine on the live run because the previous filter caught only `_flags.inherited == True` and `_flags.system == True`. The translation JSON's `ignored_variants` already declares "Empty ACL will NOT be migrated"; the skill now pre-filters records where both `acl_sess__v4policy` and `acl_sess__v6policy` are missing/empty AND surfaces them in a `Skipped per LLD` subsection so the operator sees what was excluded and why.

3. **Composite-source merge for `central:named_vlan` codified.** The AI on the live run correctly inferred to merge `vlan_name` ⨝ `vlan_name_id` on `name` before passing records to the engine, but that step wasn't spelled out in the skill prose anywhere. Now explicit: required pre-merge, drop `_flags.inherited` from both source arrays, surface "name registered without binding" as a `Skipped per LLD` finding (per the translation's `unmapped_fields` declaration that names without bindings are non-functional in Central).

4. **`acl_eth` (Ethertype ACL) out-of-scope note.** AOS 8 roles can bind both session ACLs (`role__acl[]` with `acl_type="session"`) and Ethernet ACLs (`acl_type="eth"`). The shipped `central:policy` translation only handles session ACLs. On the live run the `blacklisted` role bound an Ethertype ACL (`deny_all_ethertype`) which the AI surfaced correctly as OPERATOR-MAP, but the skill prose now spells it out: while iterating roles, collect any binding an `acl_eth` and surface as a Translation gap finding so future AIs don't have to figure this out from first principles.

5. **Output report now emits sample bodies + drill-down prose, not just summary tables.** Stage 9b previously instructed *"Do NOT dump full target_calls bodies in the consolidated output"* (a small-model defense). For capable models running the skill, this stripped exactly the data operators need — the actual JSON wire payload — and made the engine output indistinguishable from a narrative summary. The new Step 3 emits THREE parts: summary table, per-record detail tables, AND at least one representative `target_calls[0].body` JSON code block per translation. Drill-down prose explicitly invites *"show me the body for ACL X"* / *"dump all bodies for X"* follow-ups.

### Files

- **`src/hpe_networking_mcp/skills/aos-migration.md`** — Stage 9b prose: preconditions softened, Step 1 walker-optional with placeholder fallback, 2a/2b/2c/2d filters tightened (composite merge codified, empty-rule-list filter added, `acl_eth` collection added), Step 3 rewritten to emit sample bodies + drill-down. Net ~+90 lines of prose.
- **`.gitignore`** — adds `docs/engine_test.md` (private session log used to drive these fixes).
- **`pyproject.toml`** — bump 3.0.1.6 → 3.0.1.7.

### Notes

- 1174 tests pass (no test-count change — pure docs/skill release).
- **No engine, tool, or translation JSON changes.** All five fixes are in skill prose so the AI handles the workflow correctly without needing to re-derive logic per run.
- **The PII tokenization quirk surfaced during diagnosis (walker tokenized the literal string `"dict"` because it appeared as the value for a `vlan_name` key in an AI diagnostic dict) is a real bug but unrelated to Stage 9b's correctness.** Tracking separately; no action this release.
- **Real engine output validated against live data.** All four shipped translations (`central:vlan_id`, `central:named_vlan`, `central:role`, `central:policy`) ran cleanly against Jon's tenant on the first attempt. The fixes here are about how the *skill* presents the output, not about the engine producing wrong output.

## [3.0.1.6] - 2026-05-08

**Patch release — `central_translation_preview` tool + `aos-migration` Stage 9b engine-driven preview. Phase-3-lite read-only path so the translations engine sees daylight on real data before #240's actual writes land.**

The translations engine (4 shipped translations, validated lint, ~480-line preprocessing module for policy) has been infrastructure-only since v3.0.1.0 — no consumer skill actually invokes it; `aos-migration` Act II describes translation outcomes narratively but doesn't call `emit_calls`. Code-mode `execute()` blocks imports of internal modules (verified by Zach's report: `import hashlib` failed), so an AI client running the skill cannot reach the engine directly.

This release ships the bridge: a read-only tool that wraps `emit_calls`, plus an aos-migration skill stage that uses it. When an operator asks "what policies will be migrated and where will they land," the skill now produces deterministic engine output rather than the AI's interpretation.

### Three changes

1. **New `central_translation_preview` tool.** Accepts `translation_id` + `source_records` (list of source-platform dicts) + `runtime_values` and returns the deterministic per-record `TargetCall` list. Read-only by construction — the engine is pure data; the tool wraps it; no `central_*` API call is made. Per-record `EngineError` surfaces as `skip_reason` so a partial preview is still useful (empty ACLs, missing required runtime values, etc. don't crash the batch). Module-level cache loads translations once per process. Not gated by `ENABLE_CENTRAL_WRITE_TOOLS` because it cannot write.

2. **`aos-migration` Stage 9b — engine-driven translation preview.** New stage between Stage 9 (narrative AI-authored API call sequence) and Stage 10 (validation checklist). For each of the four shipped translations (`central:vlan_id`, `central:named_vlan`, `central:role`, `central:policy`), Stage 9b provides a paste-ready `execute()` block that:
   - Resolves Stage 7's operator-confirmed Central scope names to scope_ids via `central-scope-walker`.
   - Filters Stage 1's collected records (system / inherited entries dropped per the translation's consumer responsibilities).
   - Pre-merges composite sources (`central:named_vlan` joins `vlan_name` ⨝ `vlan_name_id`).
   - Calls `central_translation_preview` with the right runtime_values (including `role_records` for policy preprocessing).
   - Renders a bounded summary table (~30 rows max per translation; full bodies reachable on operator drill-down).

   Stage 9 stays — it's the high-level cutover plan. Stage 9b is the deterministic per-object engine output. Both compose; operators read Stage 9 for the order of operations and Stage 9b for "show me the actual JSON bodies and rule counts."

3. **INSTRUCTIONS.md** — adds `central_translation_preview` to the Aruba Central tool index with the per-translation `runtime_values` requirements (especially `role_records` for policy reverse-index lookup).

### Files

- **New: `src/hpe_networking_mcp/platforms/central/tools/translation_preview.py`** — the bridge tool (~210 lines)
- **`src/hpe_networking_mcp/platforms/central/__init__.py`** — registers the new `translation_preview` category
- **New: `tests/unit/test_central_translation_preview.py`** — 16 tests (per-translation happy paths, per-record EngineError surfacing, fatal-error contract, caching)
- **`src/hpe_networking_mcp/skills/aos-migration.md`** — Stage 9b section + adds `central_translation_preview` to `tools` frontmatter
- **`src/hpe_networking_mcp/INSTRUCTIONS.md`** — adds the tool to the Central section
- **`README.md`** — Central count 87 → 88, total underlying 367 → 368
- **`docs/TOOLS.md`** — Central count 87 → 88, total underlying 367 → 368
- **`pyproject.toml`** — bump 3.0.1.5 → 3.0.1.6

### Notes

- 1174 tests pass (was 1158; +16 from the new tool's tests).
- **Tool is read-only by construction.** The engine never calls `central_*` APIs; it only manipulates dicts. Returning `TargetCall` descriptors as JSON-serializable dicts cannot accidentally mutate Central state. Real execution lands as a separate `central_manage_*` tool with elicitation gating per #240.
- **Why a tool when the policy is "skill, not tool"?** The `central-scope-walker` skill works because `central_get_scope_tree` is already a tool — the data is fetchable, the skill just composes it. The translations engine isn't reachable from `execute()` (sandbox blocks internal imports), so no skill can invoke it. The "no tool when a skill works" rule applies when the data is fetchable; here it isn't.
- **Phase 3 boundary stays clean.** This tool is `_preview` (read-only). Future execution is a separate `central_manage_*` tool — different name, write-tool gating, elicitation. Operators inspecting the tool list can tell preview from execute at a glance.

## [3.0.1.5] - 2026-05-07

**Patch release — small-local-model code-mode hardening from Zach's continued OpenClaw + Qwen3 4B test report (2026-05-07).**

The continued report showed two repeating failure modes that are skill-and-docs-fixable rather than middleware-fixable:

1. **Tree-recursion authorship in the sandbox.** Qwen3 4B reliably mutates multiline code (inserts spurious leading spaces → `Unexpected indentation at byte range 57..58`), then returns `found:false` as if the traversal had completed. The recurring offender was `central_get_scope_tree` walking — every "find scope by name" path failed.
2. **Final-answer-space data manipulation.** The model truncates large JSON, fabricates counts, omits records, and wraps code in `async def run()` (returning a coroutine object then fabricating output) when asked to operate on tool results outside `execute()`.

Both fixes ship as docs / skill changes. No engine code changed — the v3 envelope, code-mode sandbox, and `isError:true` plumbing all worked correctly in the test report (Sections 6.x and 9.2 explicitly validate them).

### Three changes

1. **New `central-scope-walker` skill.** Tiny, paste-ready primitive that walks `central_get_scope_tree` output and resolves a name / path / `scope_id` / case-insensitive substring to its Central `scope_id` plus parent path, type, and metadata. Bounded output (caps to 10 matches) so it stays small-model-friendly. Designed deliberately to NOT require the AI to author tree-recursion — every recursion path failed in Zach's test for Qwen.

2. **See-also references in four downstream skills.** `central-scope-audit` (Prerequisites: resolve operator-named audit scope first), `change-pre-check` (Prerequisites: pin scope_id in the snapshot since names can be ambiguous across collections), `change-post-check` (Prerequisites: cross-check post-check name against baseline scope_id), `aos-migration` (Stage 7: resolve operator-confirmed Central names to scope_ids before Stage 9 emits config-assignments). The walker is the canonical resolution primitive; downstream skills don't author their own.

3. **INSTRUCTIONS.md `Code-mode execute() patterns` section.** Two rules with worked-example code for each:
   - **Don't wrap in `async def run()`.** `execute()` already runs in an async context. Wrapping creates an unawaited coroutine and the model fabricates a final answer because no real data came back.
   - **Filter / count / project large results inside `execute()`.** Final-answer space breaks on > ~30-item lists; do all reductions in the sandbox and return a small bounded dict.

### What was deliberately NOT done

- **No `central_find_scope_by_name` tool.** Per discussion with the maintainer: code mode is the default forward path, and a skill can do everything a tool would do here without inflating the underlying-tool count or violating the code-mode "compose primitives in `execute`" model. Skills encode workflow over read tools; tools encode policy or new endpoints. Scope-name lookup is the former.
- **No `hashlib` whitelist** in the sandbox stdlib surface. Qwen retrying with a fabricated hash after `import hashlib` failed is a model-trust issue, not a sandbox-completeness issue. If the operator wants hashing in `execute()`, they ask explicitly.

### Files

- **New: `src/hpe_networking_mcp/skills/central-scope-walker.md`** — 9th bundled skill
- **`src/hpe_networking_mcp/INSTRUCTIONS.md`** — adds Code-mode `execute()` patterns section after the response envelope section
- **`src/hpe_networking_mcp/skills/central-scope-audit.md`** — Prerequisites references the walker
- **`src/hpe_networking_mcp/skills/change-pre-check.md`** — Prerequisites references the walker (pin scope_id in baseline)
- **`src/hpe_networking_mcp/skills/change-post-check.md`** — Prerequisites references the walker (cross-check vs baseline)
- **`src/hpe_networking_mcp/skills/aos-migration.md`** — Stage 7 references the walker for resolving Central names to scope_ids
- **`docs/TOOLS.md`** — adds `central-scope-walker` row to the Bundled skills table
- **`.gitignore`** — adds the continued test report markdown file
- **`pyproject.toml`** — bump 3.0.1.4 → 3.0.1.5

### Notes

- 1158 tests pass (was 1157; +1 from skills-discovery tests auto-counting the new `central-scope-walker` skill — no functional change).
- The first OpenClaw + Qwen3 4B report drove v3.0.0.0 (universal envelope) and v2.5.2.1 (`isError:true` on sandbox failures). This continued report drives v3.0.1.5. Zach's continued report explicitly validates both prior changes — strict-wrapper prompts work because every tool ships the same envelope shape, and direct MCP `tools/call` correctly emits `isError:true` for sandbox indentation failures.
- The walker snippet uses the documented double-unwrap fallback (`response.get("data", response)` → optional inner `result` unwrap) so it's safe across the inner-wrapper inconsistency between platforms.

## [3.0.1.4] - 2026-05-07

**Patch release — translation authoring template standardization. Refactor `central:policy` to the standard Paradigm-B shape, add a `preprocessing` engine field for translations whose source needs restructuring, ship lint rules + CI enforcement so future translations follow the template.**

After shipping four translations following three different authoring paradigms (named_vlan: engine-driven iteration; vlan_id + role: per-field key_mappings; policy: single big 2-arg transform), this release converges on **one standard template** and adds CI lint to keep new translations from drifting. The user-facing engine API is unchanged; translation JSON authoring rules are now uniform.

### Three changes

1. **Engine: `preprocessing` field as a structured escape hatch.** Translations whose source shape doesn't fit per-field `key_mapping` (parallel arrays, cross-record lookups, fan-out expansion) declare a dotted import path to a preprocessing function:

   ```json
   {
     "preprocessing": "hpe_networking_mcp.translations.preprocessing.aos8_policy.preprocess_acl_for_policy",
     ...
   }
   ```

   The function signature is `(source_data, runtime_values) -> dict`. The engine invokes it before `key_mappings` (after the source-platform check + `required_runtime_values` validation), with the function returning an augmented `source_data` dict that the standard per-field key_mappings then operate on. Translations without `preprocessing` declared skip this step entirely — the simple pattern that fits most translations.

   The 2-arg transform support added in v3.0.1.3 stays in place (still useful for per-field transforms that need narrow context), but the preprocessing field is the preferred home for source-shape restructuring — it's declarative, the body in the JSON stays structurally complete, and reviewers can find all the complex logic in one named module rather than chasing it across `transforms.py`.

2. **`central:policy` refactored to the standard Paradigm-B template.** The 2-arg `aos8_acl_sess_to_central_policy_rules` transform (~515 lines) is removed from `transforms.py`; all its logic moved verbatim into `src/hpe_networking_mcp/translations/preprocessing/aos8_policy.py` as `preprocess_acl_for_policy`. The translation JSON now has thin `key_mappings` (just `name` ← `accname` via `direct_str` and `policy_rules` ← `_central_rules` via `direct`), with the body structurally complete and `policy-rule: "{policy_rules}"` as the only computed substitution. Wire output is identical (asserted by 30+ engine tests).

   Also: the preprocessing function now computes `role_attribution` internally from `runtime_values["role_records"]` (the full list of role records, supplied once per migration run) rather than relying on the consumer to pre-compute it. Cleaner consumer contract — the consumer pre-fetches roles once, and every ACL's preprocessing reverse-indexes them into per-ACL role_attribution. The translation's `required_runtime_values` changed from `["central_scope_id", "role_attribution"]` to `["central_scope_id", "role_records"]`.

3. **Lint module + CI enforcement.** New `src/hpe_networking_mcp/translations/lint.py` with four rules:
   - `check_no_fat_transforms` — every transform in the registry has < 50 source lines. Composite logic must live in `preprocessing/`.
   - `check_body_or_body_template` — each emit has exactly one of `body` / `body_template`; POST/PUT/PATCH emits must declare one.
   - `check_required_runtime_values_referenced` — every key in `required_runtime_values` is referenced somewhere (placeholder, preprocessing module source, narrative). Catches refactor leftover.
   - `check_preprocessing_path_resolves` — when `preprocessing` is set, the dotted path resolves to a callable with the right `(source_data, runtime_values)` signature.

   The rules are enforced both by `tests/unit/test_translations_lint.py` (auto-runs in CI via the existing `pytest tests/unit` step — fails CI on any violation against the shipped translations) and by a CLI entry point: `python -m hpe_networking_mcp.translations.lint`.

### Files

- **New: `src/hpe_networking_mcp/translations/AUTHORING.md`** — standard template + decision tree + per-translation examples + lint rules table
- **New: `src/hpe_networking_mcp/translations/preprocessing/__init__.py`** — module docs explaining when to use preprocessing (and when not to)
- **New: `src/hpe_networking_mcp/translations/preprocessing/aos8_policy.py`** — `preprocess_acl_for_policy` (the migrated central:policy logic, ~480 lines)
- **New: `src/hpe_networking_mcp/translations/lint.py`** — four lint rules + CLI entry point
- **New: `tests/unit/test_translations_lint.py`** — 16 tests (smoke + per-rule synthetic violations)
- **`src/hpe_networking_mcp/translations/loader.py`** — adds optional `preprocessing` field to `Translation`
- **`src/hpe_networking_mcp/translations/engine.py`** — preprocessing dispatch + `_run_preprocessing` helper
- **`src/hpe_networking_mcp/translations/targets/central/policy_v1.json`** — refactored to thin Paradigm-B + `preprocessing` field; `required_runtime_values` updated to `role_records`
- **`src/hpe_networking_mcp/translations/transforms.py`** — removes `aos8_acl_sess_to_central_policy_rules` + 9 helper functions (~515 lines) and unused imports
- **`tests/unit/test_translations_engine.py`** — adds 5 preprocessing engine tests; updates 14 policy tests for the `role_records` runtime shape
- **`tests/unit/test_translations_loader.py`** — updates policy schema-validation test for the new `preprocessing` field + `role_records` requirement
- **`pyproject.toml`** — bump 3.0.1.3 → 3.0.1.4

### Notes

- 1157 tests pass (was 1136; +21 from new lint tests + new preprocessing engine tests).
- **No behavior change visible to consumer skills.** `central:policy`'s wire output is identical pre/post refactor — the only consumer-visible API delta is `runtime_values["role_attribution"]` → `runtime_values["role_records"]` (cleaner: pre-fetch roles once, let preprocessing reverse-index per-ACL).
- **Adding a new translation now follows AUTHORING.md.** Decision tree: simple 1:1 source → per-field key_mappings only. Source needs restructuring (parallel arrays, cross-record lookups, fan-out) → author a preprocessing module under `translations/preprocessing/` and declare its dotted path in JSON. Run `python -m hpe_networking_mcp.translations.lint` locally before opening a PR.
- **CI integration** is automatic via the existing `pytest tests/unit` step — `test_shipped_translations_pass_all_rules` exercises every rule against every shipped translation. Drift surfaces immediately rather than at runtime.

## [3.0.1.3] - 2026-05-07

**Patch release — fourth translation (`central:policy`, AOS 8 acl_sess → Central /policies) + engine 2-arg transform support + ~120 KB of inline enum lookup tables.**

Adds `central:policy`, the fourth shipped translation, completing the role / policy migration story by handling the AOS 8 → Central inversion: AOS 8 binds ACLs to roles via `role.role__acl[]` (role-side reference), while Central inverts and references roles from policies via `policy-rule[].condition.source.role-list` (policy-side reference). Central back-fills `role.policies[]` automatically from those references — `central:role` was authored knowing this translation was coming and explicitly deferred `role__acl` to here.

The translation handles the rich AOS 8 acl_sess shape (parallel `acl_sess__v4policy` + `acl_sess__v6policy` rule arrays per ACL) and produces a single Central `policy-rule[]` with each rule tagged by `address-family`. Verified live across 88 user-customized ACLs in the operator's tenant plus a purpose-configured `missing-policies` ACL exercising the variants not present elsewhere (host destination, ICMP echo, time-range reference, standalone dst-nat, redirect-tunnel + redirect-tunnel-group, destination user-role, destination local-IP, app-deny). Central GW shape verified live for `RULE_PROTOCOL` + `ip-header.protocol` via the operator's `amazon-device` policy on a mobility gateway.

### Three changes

1. **New translation `central:policy`.** Two-step Central CNX flow (policy SHARED create + multi-DF config-assignments). Composite source declaring both `acl_sess` (the ACL definition) and `role` (for the role-attribution reverse-index lookup); consumer pre-computes `role_attribution: list[str]` per ACL and passes via `runtime_values`. The translation maps:
   - **Source/destination types** (7 of 14 Central enum values verified): `ADDRESS_ANY`, `ADDRESS_HOST` (with `host-ipv4-address`), `ADDRESS_NETWORK` (with netmask → CIDR conversion), `ADDRESS_ALIAS`, `ADDRESS_ROLE` (single via `suserrole`/`duserrole` + name; role-list via `suser`/`duser` + role_attribution from runtime), `ADDRESS_LOCAL`, `ADDRESS_USER`. The 7 less common types (DOMAIN_NAME, GROUP, AP_*, MASTER_IP, SUBNET_MASK) deferred.
   - **Rule types**: `RULE_ANY` (default), `RULE_PROTOCOL` (live-verified), `RULE_TCP` / `RULE_UDP` (inferred from schema parallel structure), `RULE_APPLICATION` / `RULE_APP_CATEGORY` / `RULE_WEB_CATEGORY` / `RULE_WEB_REPUTATION` for app/web rules.
   - **Service modes**: AOS 8 named svc-\* (svc-icmp, svc-dns, svc-dhcp, svc-http, svc-https, ...) via a hand-curated lookup to `(protocol, port-range)` tuples; raw `proto + port + port1/port2` rules; ICMP with optional `icmp_type`; app/web rules via the schema's `x-enumDescriptions`-derived enum tables.
   - **Actions**: `ACTION_ALLOW`, `ACTION_DENY`, `ACTION_DESTINATION_NAT` (with `destination-nat.dest-port`), `ACTION_SOURCE_NAT`, `ACTION_DUAL_NAT` (with `dual-nat.{dest-port, pool}`), `ACTION_REDIRECT` (tunnel + tunnel-group variants live-verified; esi-group + datapath operator-scoped-out), `ACTION_ROUTE`. Secondary actions: `log` + `send-deny-response` for app deny.
   - **Time-range** reference via `condition.time-range-name`.
   - **Empty-ACL handling**: per the LLD's "empty ACL not migrated" rule, the transform returns `None` when no rules are produced; engine drops the body key.

2. **Engine: 2-arg transform support.** Transforms can optionally declare a `(value, ctx) -> result` signature; the engine inspects the function via `inspect.signature` and dispatches accordingly. The 1-arg form `(value) -> result` continues to work unchanged (backward compatible — every prior transform keeps its signature). The 2-arg form's `ctx` is `{"source_data": ..., "runtime_values": ...}`. Used by `aos8_acl_sess_to_central_policy_rules` to read both `acl_sess__v4policy` and `acl_sess__v6policy` from `source_data` plus `role_attribution` from `runtime_values` — neither of which fits the engine's existing single-`from`-path key_mapping pattern.

3. **`policy_enum_tables.py` — ~120 KB of inline Central enum lookup tables.** Auto-generated at authoring time from `api-endpoints/central/policy.json`'s `x-enumDescriptions` annotations. Four tables: `AOS8_APP_TO_CENTRAL` (3952 DPI apps), `AOS8_APP_CATEGORY_TO_CENTRAL` (24), `AOS8_WEB_CATEGORY_TO_CENTRAL` (85), `AOS8_WEB_REPUTATION_TO_CENTRAL` (5). Inline-not-runtime-loaded for self-contained engine and reviewable mappings. **Critical**: 21 of 85 web-category entries insert connective words ("AND") between slash-separated AOS 8 forms (e.g. `entertainment/arts` → `ENTERTAINMENT-AND-ARTS`); a naive `.upper().replace("/", "-")` transform would silently produce wrong Central enum values for those. The lookup tables enforce correctness.

### Files

- **New: `src/hpe_networking_mcp/translations/targets/central/policy_v1.json`** — fourth shipped translation
- **New: `src/hpe_networking_mcp/translations/policy_enum_tables.py`** — 4 enum lookup tables (~120 KB)
- **`src/hpe_networking_mcp/translations/transforms.py`** — adds the `aos8_acl_sess_to_central_policy_rules` 2-arg transform plus 9 helper functions (~350 lines total) and the AOS 8 named-service → (protocol, port) lookup table
- **`src/hpe_networking_mcp/translations/engine.py`** — 2-arg transform dispatch via signature inspection
- **`tests/unit/test_translations_engine.py`** — 16 new tests (2 engine 2-arg + 14 policy)
- **`tests/unit/test_translations_loader.py`** — 1 new policy schema-validation test
- **`pyproject.toml`** — bump 3.0.1.2 → 3.0.1.3

### Notes

- 1136 tests pass (was 1114; +22 from new tests).
- **Any-any expansion (operator-confirmed):** Central can express `any → user/host/network` and `user → any` for a role-bound policy, but NOT `any → any`. AOS 8 `any any` semantics are bidirectional (allow both directions of traffic between role and anywhere). The translation expands one AOS 8 `any any` rule into **TWO** Central rules — `role → any` AND `any → role` — so return traffic is matched. This pattern matches the live `PD-allowall` policy in the operator's tenant. Rules where AOS 8 source is `any` but destination is specific (`any → host`, `any → network`, `any → role`) keep `source: ADDRESS_ANY` since Central does support those patterns; only the literal any-any pattern triggers expansion. When `role_attribution` is empty (an ACL with no role attribution should not reach the translation per the LLD, but the transform is defensive), no expansion happens — the single-rule form with both ANY addresses is emitted.
- **Named svc-* services use Central's authoritative net-service catalog.** Originally the translation hand-curated AOS 8 svc-* → (protocol, port-range) mappings. After verifying live that Central ships 73 net-services in the operator's tenant (`central_get_net_services`) — including 64 svc-* names that mirror AOS 8 conventions exactly — the translation now uses `condition.services.net-service: "<svc-name>"` with `rule-type: RULE_NET_SERVICE`. Cleaner, uses Central's authoritative source, and surfaces unknown svc-* names as clean Central errors rather than silently mistranslating to wrong port mappings. The hand-curated `_AOS8_NAMED_SERVICE_TO_CENTRAL` table was removed. A small `_AOS8_TO_CENTRAL_SVC_NAME_ALIASES` dict (currently empty) is kept for known-mismatch edge cases that surface live (e.g. AOS 8 `svc-icmpv6` vs Central `svc-v6-icmp` if/when observed).
- Central GW `RULE_PROTOCOL` + `ip-header.protocol` is live-verified (operator's `amazon-device` policy). `RULE_TCP` / `RULE_UDP` + `transport-fields.destination-port` follows the schema's parallel structure but should be verified against the operator's tenant before treating as authoritative for production migration. Schema annotations on policy.json are unreliable for Gateway support — many fields tagged Switch/AP-only are clearly used by GW-bound policies in live data. Per operator clarification, `x-supportedDeviceType` is field-honored, not body-gated; trust live data over annotations.
- Consumer responsibilities documented in `draft_notes`: pre-compute `role_attribution` per ACL by scanning role records (filter `_flags.system / .default / .readonly` entries on both sides); skip ACLs with empty rule lists or zero role attribution per the LLD migration rules.
- Deferred to v2 in `unmapped_fields`: QoS marking (apptosstr / appprio8021p / queue), src-nat / route action sub-configs, mirror / blacklist / captive action variants, less-common address types (DOMAIN_NAME / GROUP / AP_* / MASTER_IP / SUBNET_MASK), redirect esi-group + datapath variants (operator scope-out).
- AOS 8 doesn't generate composite role+address rules (single-token CLI source-spec grammar). Central's `role-options` sub-schema is therefore Central-native with no AOS 8 source path — flagged in draft_notes as a non-target.

## [3.0.1.2] - 2026-05-07

**Patch release — third translation (`central:role`, Gateway-targeted) + engine empty-dict drop + role-specific transforms (including all five bandwidth-contract sub-shapes).**

Adds `central:role`, the third shipped translation, covering AOS 8 user-role REST object → Central role profile for the Gateway device-function. This is the **second iteration** of the role translation: the first iteration (PR #282, never merged) was caught in operator-led review with several wire-incorrect fields (a `policies[]` body field that doesn't exist on Central's role schema, VLAN binding nested inside `vlan-parameters` when GW puts it at the root, and 5 LLD-INFERRED source field names that turned out wrong). The current version is fully cross-referenced against the live AOS 8 tenant **and** the Central role schema's `x-supportedDeviceType=Gateway` annotations. Bandwidth contracts (originally deferred to v2) shipped after the operator configured the missing variants on the test role.

### Three changes

1. **New translation `central:role`.** Two-step Central CNX flow (role SHARED create + multi-DF config-assignments). Body has the role at the root plus three nested groups (`session-parameters`, `miscellaneous-parameters`, `classification-parameters`). Every body field is Gateway-supported per the Central role schema. `target_meta.device_functions` is **`["MOBILITY_GW"]` only** — AP-targeted role definitions use a different schema (`vlan-parameters`, `named-vlan`, etc.) and would need a separate translation.

   Source-side field names verified live, including a purpose-configured `parent` role at `/md/Campus/West` with the full Tier 1 flag set + `reauthentication-interval 3600 seconds`. The single-underscore prefix gotcha (`role_disable_ipclassify`, `role_enable_youtubeedu`) is real and called out in the JSON. The reauth disambiguator (`role__reauth.seconds: true` flag distinguishes the seconds-form from the minutes-form) is handled by paired transforms. Bandwidth contracts (`role__bwc`) deferred to a future v2 — one variant captured live (basic per-role with `dir_type` discriminator) but the 4 other LLD sub-shapes still need samples. VIA + IP pool families excluded from v1 per operator's call (rarely used; alternative products handle that workflow).

   **Inversion call-out (the bug the review caught):** AOS 8 carries the role→ACL binding inside the role record (`role__acl[]`). Central inverts this — policies reference roles via `policy-rule[].condition.source.role`, and Central back-fills `role.policies[]` automatically from those references. This translation does **NOT** send `policies[]` in the role body; ACL/policy binding is owned by the future `central:policy` translation.

2. **Engine: `_drop_none_keys` now drops empty nested dicts.** When every member of a nested body group is an optional field whose source value was missing, the post-render pass now drops the now-empty parent key entirely. Top-level empty dicts pass through unchanged. Critical for the role translation since most roles configure only a small subset of the ~16 mappable fields (and all three nested groups are entirely optional).

3. **Thirteen new transforms in `translations/transforms.py`:**
   - `vlanstr_to_id_if_numeric` / `vlanstr_to_name_if_nonnumeric` / `vlanstr_to_vlan_type` — disambiguate AOS 8's combined `role__vlan.vlanstr` field (Central splits it into separate `access-vlan-id` int / `access-vlan-name` string + `vlan-type` enum).
   - `aos8_field_present_to_true` — handles both the older Pattern A flag shape (`{_present: true, _flags: {default: true}}` on `role__cp_acc` / `role__openflow`) and the newer Pattern B shape (empty `{}` when configured on `role__enforce_dhcp` / `role__reg_role` / `role__dpi_disable` / etc.). Returns `True` for any non-`None` input — reaching the transform implies the path resolved.
   - `aos8_reauth_minutes_value` / `aos8_reauth_seconds_value` — paired transforms reading the `role__reauth` dict; one returns the value when `seconds` is falsy/absent (minutes form), the other when `seconds: true` (seconds form). Live-verified on the `parent` role.
   - **`aos8_role_bwc_basic_to_central`** — basic per-role bandwidth contract: `role__bwc[]` → `aaa-bw-contract.bw-contract[]`. Live shape verified on `blacklisted` role.
   - **`aos8_role_bwc_app_filter_app`** / **`aos8_role_bwc_app_filter_appcategory`** — paired transforms that fan out the AOS 8 `role__bwc_app[]` array (which mixes per-app + per-appcategory entries discriminated by `app_type`) into Central's two distinct schemas (`app-aaa-contract.app[]` and `app-category-aaa-contract.app-category[]`). Live-verified on `parent` role with `youtube` (app) and `streaming` (appcategory).
   - **`aos8_role_bwc_web_filter_category`** / **`aos8_role_bwc_web_filter_reputation`** — same fan-out pattern for `role__bwc_web[]` (mixed per-web-cc-category + per-web-cc-reputation discriminated by `web_opt`) → `web-category-aaa-contract.web-category[]` / `web-reputation-aaa-contract.web-reputation[]`. Category names are uppercased + slash-replaced (e.g. `streaming/media` → `STREAMING-MEDIA`); reputations are uppercased + dash-to-underscore-replaced (e.g. `low-risk` → `LOW_RISK`).
   - **`aos8_role_bwc_excl_filter_app`** / **`aos8_role_bwc_excl_filter_appcategory`** — same pattern for the bw-contract exclude variants (`role__bwc_ex[]` discriminated by `app_type`) → `exclude-app-contract.exclude-app[]` / `exclude-app-cat-contract.exclude-app-category[]`. The exclude variant carries no traffic direction and no contract reference — listed apps/categories simply bypass bandwidth-contract enforcement.

### Files

- **New: `src/hpe_networking_mcp/translations/targets/central/role_v1.json`** — third shipped translation
- **`src/hpe_networking_mcp/translations/transforms.py`** — six new transforms + registry entries
- **`src/hpe_networking_mcp/translations/engine.py`** — `_drop_none_keys` enhanced to drop empty nested dicts
- **New: `tests/unit/test_translations_transforms.py`** — 36 tests covering the role-specific transforms + the registry
- **`tests/unit/test_translations_engine.py`** — 13 new role tests (minimum record, named-VLAN at root, numeric-VLAN at root, Pattern-A flags, Pattern-B flags, reauth-minutes routing, reauth-seconds routing, captive portal, max-sessions, full rich record, no-policies-emitted, MOBILITY_GW-only assignment, missing-rname error, empty-group drop)
- **`tests/unit/test_translations_loader.py`** — 1 new role schema-validation test (asserts the corrected source field names + that `policies` doesn't appear in the body template + that `role__bwc` and `role__acl` are explicitly captured as deferred)
- **`pyproject.toml`** — bump 3.0.1.1 → 3.0.1.2

### Notes

- 1114 tests pass (was 1037; +77 from new transforms + role tests including all 7 bw-contract sub-shapes).
- Cross-referenced the operator's live tenant (55 roles at `/md/Campus/West`, including the test `parent` role with all 7 bw-contract sub-shapes configured — basic + per-app + per-appcategory + per-web-cc-category + per-web-cc-reputation + exclude-app + exclude-appcategory) against `api-endpoints/central/role.json`'s `x-supportedDeviceType` annotations. The body shape is now the strict intersection of "AOS 8 carries it" + "Central role schema accepts it for Gateway".
- Consumer responsibility documented: pre-filter `_flags.default=true` sub-objects (and top-level `_flags.default=true` roles) from source records before passing to `emit_calls`. Otherwise every role POST will explicitly carry AOS 8 system defaults (`max-sessions=65535`, `check-for-accounting=true`, etc.) which may overwrite Central's own role-profile defaults.
- Remaining deferrals: `role__acl` (handled by future `central:policy` translation), VIA + pool fields (operator scoped them out as rarely used / better handled by alternative products), `disable-cp-gw-translation` (Gateway-only Central field; AOS 8 source name unknown).
- Earlier draft from PR #282 is gone — the rework is a clean replacement, not a patch.

## [3.0.1.1] - 2026-05-07

**Patch release — second translation (`central:vlan_id`) + engine optional-field support + iteration rename.**

Adds the second shipped translation, `central:vlan_id`, covering the AOS 8 bare-and-rich `vlan_id` REST object → Central layer2-vlan profile. Source field names were live-verified against the maintainer's tenant during authoring; the operator supplied a sample rich-record payload (with sub-properties nested under `vlan_id__aaa.profile-name` and `vlan_id__descr.descr`, plus top-level `option-82`) that drove the design. The earlier speculative split into separate `central:vlan_id` (bare) and `central:vlan` (rich) translations was abandoned once the live shape confirmed it's a single object — the same translation handles both cases via optional body fields.

### Three changes

1. **New translation `central:vlan_id`.** Two-step Central CNX flow (layer2-vlan SHARED create + multi-DF config-assignments), structurally a subset of `central:named_vlan` steps 1+4. Step 1 body is `{"vlan": "<id>"}` for bare records; for rich records the body grows to include `description`, `option-82`, and `wired-aaa-profile` only when the source carries them. Live-verified the rich-record source shape from the operator's tenant (top-level `option-82`, nested `vlan_id__aaa`/`vlan_id__descr` sub-objects).

2. **Engine optional-field support.** New `optional: bool` field on `KeyMapping`. When set and the source record lacks the field, the engine substitutes `None` into the body and a post-render pass drops `None`-valued keys from the rendered dict. Required (default) fields still raise `EngineError` on missing source data — unchanged behavior. Falsy non-`None` values (e.g. `option-82=false`) are preserved; only literal `None` triggers key drop.

3. **Iteration value rename: `once_per_named_vlan` → `once`.** The original name was specific to the named-VLAN translation and became misleading once a second translation needed a no-fan-out emit. Clean rename — engine only recognizes `"once"` now (no backwards-compat alias). `named_vlan_v1.json` and the test fixtures were updated accordingly.

### Files

- **New: `src/hpe_networking_mcp/translations/targets/central/vlan_id_v1.json`** — second shipped translation
- **`src/hpe_networking_mcp/translations/loader.py`** — `KeyMapping.optional` field added
- **`src/hpe_networking_mcp/translations/engine.py`** — `optional` flag wired through `_build_base_context`; new `_drop_none_keys` post-render pass; `once_per_named_vlan` → `once`
- **`src/hpe_networking_mcp/translations/targets/central/named_vlan_v1.json`** — iteration values renamed to `once`
- **`tests/unit/test_translations_engine.py`** — 8 new tests for `central:vlan_id` covering bare records, rich records, partial-rich (description-only, option-82-only), `option-82=false` preservation, runtime device-function override, and missing-required-id error
- **`tests/unit/test_translations_loader.py`** — 1 new test for `central:vlan_id` schema validation; existing fixtures renamed to `once`
- **`pyproject.toml`** — bump 3.0.1.0 → 3.0.1.1

### Notes

- 1037 tests pass (was 1028; +9 from the new `central:vlan_id` tests).
- The earlier session draft authored a separate `central:vlan_v1.json` for the rich form before live verification revealed there's only one AOS 8 object. That speculative file was deleted before the PR.
- Pattern for future translations with optional body fields: declare `optional: true` on `KeyMapping` entries; engine handles the rest. Tests should cover both presence and absence cases.

## [3.0.1.0] - 2026-05-07

**Minor release — translations engine (loader + runtime engine + first translation).**

Adds the data-driven foundation for **cross-platform configuration translations** in service of issue [#240](https://github.com/nowireless4u/hpe-networking-mcp/issues/240) (aos-migration Phase 3 — execute Central writes) and future use cases like Mist ↔ Central WLAN sync. Per the design in [#279](https://github.com/nowireless4u/hpe-networking-mcp/issues/279), three pieces ship together:

1. **Translation data files** under `src/hpe_networking_mcp/translations/targets/<platform>/` — JSON files describing per-target API call sequences with source-platform-specific extraction logic. v1 ships one translation: `targets/central/named_vlan_v1.json`, covering the AOS 8 named-VLAN → Central named-VLAN/alias/layer2-vlan chain. The format is **multi-source AND multi-target ready**: each translation has a `target_platform` field + `sources.<platform_id>` blocks. v1 authors AOS 8 → Central only.
2. **Loader** (`translations/loader.py`) — pydantic-validated `Translation` schema; reads every `*.json` under `targets/<platform>/` at lifespan startup; supports operator overrides via `TRANSLATIONS_PATH` env var (file-level replacement); fails fast at startup with aggregated error messages on malformed files; returns `dict[str, Translation]` keyed by `"<target_platform>:<target_id>"`.
3. **Runtime engine** (`translations/engine.py`) — `emit_calls(translation, source_data, source_platform_id, runtime_values, overrides)` returns ordered `TargetCall` descriptors ready for dispatch. The engine **does not** call any target platform — Phase 3 / #240 (or future skills) will be the dispatcher. Generic `runtime_values: dict[str, Any]` carries target-platform-specific runtime context (e.g. for Central: `central_scope_id`, `device_functions`); the translation's `required_runtime_values` declares which keys must be present.

The named-VLAN translation captures six empirical findings verified against the maintainer's live Central tenant during design (see #279 for details), notably: SHARED + LOCAL profile distinction, multi-device-function packing in `config-assignments` arrays, alias auto-pull behavior when a named-VLAN is assigned, and AOS 8's asymmetric range-syntax handling between `vlan_id` (expands) and `vlan_name_id` (preserves).

### Why "translations" and not "migrations"

Migration is one-time and end-state-oriented (AOS 8 → Central). The engine's actual job — translate source-shape to ordered target-API-calls — also covers ongoing operational sync (Mist ↔ Central WLAN reconciliation runs repeatedly, not once). Same primitive, different consumer modes. Naming the package "migrations" would have locked us into a one-time-use framing that becomes obsolete after AOS 8 → Central work completes.

### Why minor (3rd-digit) bump

Per the project's version-bump scope rule, "minor (3rd) for substantial new subsystems." This adds a complete new package, format spec, public API surface, and runtime engine — substantial enough to warrant the minor bump even though no user-visible behavior changes yet (no skill consumes the engine in this release; that's #240).

### Files

- **New: `src/hpe_networking_mcp/translations/__init__.py`** — package init, public API exports
- **New: `src/hpe_networking_mcp/translations/loader.py`** — pydantic schemas + `load_translations()` entry point
- **New: `src/hpe_networking_mcp/translations/engine.py`** — `emit_calls()` + `TargetCall` dataclass + iteration/template logic
- **New: `src/hpe_networking_mcp/translations/transforms.py`** — registry of named transforms (`split_csv_to_string_array`, `expand_vlan_id_csv`, `direct_int`, `flag_to_bool`, etc.)
- **New: `src/hpe_networking_mcp/translations/targets/central/named_vlan_v1.json`** — first shipped translation (AOS 8 named-VLAN → Central, 6-emit chain)
- **New: `tests/unit/test_translations_loader.py`** — 8 tests covering shipped-translation validation, composite-key isolation across platforms, override path, schema rejection, JSON parse errors
- **New: `tests/unit/test_translations_engine.py`** — 14 tests covering end-to-end call generation, per-step assertions, iteration patterns (per-VLAN-ID range expansion, multi-device-function array packing, runtime-values device-function override), error paths
- **`pyproject.toml`** — bump 3.0.0.6 → 3.0.1.0

### Notes

- 1028 tests pass (was 1006; +22 from the new translation tests).
- The loader is **not** wired into `server.py:lifespan()` in this release. The engine has no consumer yet (the aos-migration skill still emits a text plan; Phase 3 / #240 will integrate). Wiring + lifespan exposure will land in the same PR as the first consumer to avoid unused startup cost.
- The cross-platform `manage_wlan_profile` aggregator tool will eventually be deprecated in favor of a future Mist-targeted translation + a WLAN-sync skill that consumes the same engine. Tracked in #279.

## [3.0.0.6] - 2026-05-06

**Patch release — PII walker structural-context rules + `RADSEC` → `RAD` / `TACACS` token-kind split.**

The AOS 8 structured config endpoint `/v1/configuration/object/rad_server?type=user` returns RADIUS shared secrets in **cleartext** as `rad_key.key` (verified live with a direct httpx call inside the running MCP container, bypassing the PII tokenization middleware). The PII walker classified the inner `key` field via the `looks_like_credential()` shape heuristic — and short single-class secrets like `"protocol"` failed the shape check, leaking cleartext to the AI.

This was a **pre-existing privacy bug** affecting every operator who reads AOS 8 RADIUS server config through this MCP server, regardless of migration use case.

Closes [#277](https://github.com/nowireless4u/hpe-networking-mcp/issues/277).

### Three changes

1. **Walker plumbing extension.** `_walk_dict` / `_walk_pair` / `_walk_list` now thread a `parent_field_name` argument through recursion — the wrapping key under which the current dict was found. `classify_field` accepts it as a new keyword argument.

2. **Structural-context rules.** New `STRUCTURAL_SECRET_CONTEXTS: dict[(parent, child), TokenKind]` table fires unconditionally (no shape check) when a generic field name is nested under a wrapping key that strongly implies a credential. Shipped entries:
   - `("rad_key", "key")` → `RAD`
   - `("tacacs_key", "key")` → `TACACS`
   The placeholder-skip from v3.0.0.5 still runs first, so a `********` value under `rad_key` stays cleartext (preserves the dangerous-illusion safety net).

3. **`TokenKind.RADSEC` split into `RAD` and `TACACS`.** The old `RADSEC` was a category covering RADIUS / RadSec / TACACS+ shared secrets and EAP passwords — overloaded with the *RadSec* protocol (RADIUS over TLS). Split for clarity:
   - **`TokenKind.RAD`** — RADIUS / RadSec shared secrets, EAP-tunneled passwords
   - **`TokenKind.TACACS`** — TACACS+ shared secrets and TACACS+-tunneled passwords

   Existing `SECRET_FIELD_NAMES` entries (`shared_secret`, `radius_secret`, `radsec_secret`, `eap_password`, `inner_password`) and the generic-credential `secret` rule remap to `RAD`. Wire format changes from `[[RADSEC:uuid]]` to `[[RAD:uuid]]` (or `[[TACACS:uuid]]` when fired via the structural rule). Internal-only change; new sessions use the new labels.

4. **`vrrp_passphrase` rule** added to `SECRET_FIELD_NAMES` mapping to `PSK`. Live captures show AOS 8 returns `cluster_prof.vrrp_info.vrrp_passphrase` as the deterministic-encrypted form (~48 hex chars); we tokenize unconditionally rather than relying on the shape-check heuristic incidentally passing.

### Behavior change to flag

Callers / clients that previously hard-coded prefix-detection for `[[RADSEC:` will need to recognize `[[RAD:` and `[[TACACS:` instead. The detokenize round-trip works as before for any token allocated within the same session.

### Files

- `src/hpe_networking_mcp/redaction/rules.py` — `TokenKind.RADSEC` removed; `RAD` + `TACACS` added; existing field-rule entries remapped; `STRUCTURAL_SECRET_CONTEXTS` added; `classify_field` accepts `parent_field_name` and consults the structural rules; `vrrp_passphrase` added to `SECRET_FIELD_NAMES`.
- `src/hpe_networking_mcp/redaction/walker.py` — `_walk_dict` / `_walk_pair` / `_walk_list` thread `parent_field_name` through recursion.
- `src/hpe_networking_mcp/INSTRUCTIONS.md` — token-kind list updated for the rename.
- `tests/unit/test_pii_redaction.py` — existing `RADSEC` assertions updated to `RAD`; new test classes for `TestStructuralSecretContexts`, `TestVrrpPassphraseRule`, and `TestStructuralWalkerEndToEnd` (covers a realistic AOS 8 `rad_server` shape with both short single-class and multi-class secrets).
- `pyproject.toml` — bump 3.0.0.5 → 3.0.0.6.

### Notes

- 1006 tests pass (was 998; +8 from new structural / vrrp / end-to-end tests).
- Live evidence captured during issue #277 design discussion: the structured endpoint returns `rad_key.key` values like `"protocol"` and `"nowireless4u"` in cleartext. After this release, both tokenize correctly as `[[RAD:uuid]]` end-to-end.

## [3.0.0.5] - 2026-05-06

**Patch release — AOS 8 transposed-table tokenization fix.**

AOS 8 `show <thing> detail`-style commands (notably `show aaa authentication-server radius/tacacs/ldap/internal <name>`) return their content as a **transposed key/value table** — a list of two-column rows where every row is a dict with literal field names `"Parameter"` and `"Value"`. The PII tokenization walker classifies values by JSON field name, so it could never see the *semantic* field name (`Host`, `Key`, `NAS IP`, ...) hidden in the `Parameter` column. Identifier-field rules keyed on names like `host` could not fire — RADIUS/TACACS/LDAP server IPs and FQDNs leaked to the AI in cleartext.

Fix: added `flatten_param_value_lists()` to `aos8/tools/_helpers.py` that recursively detects `[{Parameter: k, Value: v}, ...]` and rewrites it into a regular dict (`{k: v, ...}`). Applied in `run_show()` so every AOS 8 show-command response gets the treatment automatically. The walker's existing space-→-underscore normalization (added in v2.4.0.5) makes `"Host"` resolve to `host`, so a new `host` rule in `TOKENIZED_IDENTIFIER_FIELDS` fires on the AAA-server IP/FQDN. Carve-out from the v2.3.1.2 "internal IPs not tokenized" decision — AAA infrastructure is auth-fabric-critical.

Live-verified the transposed shape against an AOS 8.13.1.2 LSR Mobility Conductor before designing the flattener (captured `show aaa authentication-server radius ClearPass70` → `RADIUS Server ClearPass70: [{Parameter: Host, Value: 192.168.20.70}, ...]`). Fixture saved to `tests/unit/fixtures/aos8/show_aaa_radius_server_detail.json`.

Closes [#235](https://github.com/nowireless4u/hpe-networking-mcp/issues/235).

### Files

- **`src/hpe_networking_mcp/platforms/aos8/tools/_helpers.py`** — added `flatten_param_value_lists()`. Conservative detection: only flattens lists where *every* element is a dict containing at minimum `Parameter` and `Value` keys. Non-matching shapes pass through unchanged. Applied in `run_show()` after `strip_meta()`.
- **`src/hpe_networking_mcp/redaction/rules.py`** — added `host: TokenKind.HOSTNAME` to `TOKENIZED_IDENTIFIER_FIELDS`. Carve-out from the v2.3.1.2 IP-passthrough rule, scoped to AAA server detail (where the field name `host` is the server's IP/FQDN). Comment cites issue #235.
- **`tests/unit/test_aos8_helpers.py`** — new unit-test file for the flattener (8 tests covering: transposed list flattens; nested transposed list flattens in place; non-transposed list passes through; empty list passes through; scalar passes through; mixed-shape list passes through; real fixture flattens; idempotent on already-flattened dict). Plus an integration-style test for `run_show()`.
- **`tests/unit/fixtures/aos8/show_aaa_radius_server_detail.json`** — captured fixture from a live AOS 8.13.1.2 MM, with the masked `Key: ********` value preserved as-returned by the controller.
- **`tests/unit/test_pii_redaction.py`** — updated two Mist/Central RADIUS-server fixture tests (`test_full_walk`, `test_server_group_radius_secrets_tokenized`) to reflect the new contract: `host` in a RADIUS-server context IS tokenized as HOSTNAME, where v2.3.1.2 had treated it as a generic IP. Added `test_aos8_aaa_radius_detail_after_flatten_tokenizes_host` end-to-end regression.
- **`pyproject.toml`** — bump 3.0.0.4 → 3.0.0.5.

### Behavior change to flag

The `host` rule applies fleet-wide, not just to AOS 8. Mist/Central tools that return RADIUS server records with a `host` field will now tokenize the IP/FQDN where they previously did not. This is consistent with the issue's stated threat model (AAA infrastructure is critical, regardless of platform).

### Subtlety: masked-placeholder skip (also added in this release)

AOS 8 returns shared secrets / passwords as runs of asterisks (`"********"`) — the real value never leaves the controller. After this release's transposed-table flattening, the walker would see `Key: "********"` as a `key` field with a credential-shaped value, and tokenize the placeholder as `[[APITOKEN:uuid]]`.

That sounds harmless, but it isn't: a tokenized placeholder creates the **dangerous illusion** that the AI has a real tokenized secret it can pass to a write tool. The detokenize round-trip restores `"********"` — which Central / AOS 10 would happily accept as a literal RADIUS shared secret, and RADIUS auth would then fail silently the next time a client tries to associate. Better to fail loudly: AI sees `"********"` directly and knows it has to ask the operator for the real secret.

Added `is_masked_placeholder(value)` to `redaction/rules.py` (recognizes all-asterisk strings of length 4+) and a short-circuit at the top of `classify_field` that skips tokenization for masked values regardless of which rule path the field name matches. Future placeholder patterns (`<hidden>`, `[REDACTED]`, etc.) can be added as they surface.

### Notes

- 998 tests pass (was 979; +19 total: +10 from the flattener + tokenization tests, +9 from the placeholder-skip tests).
- The flattener is conservative (requires *every* row to match the shape), so existing show commands that return regular records (e.g. `show ap database`, `show aaa authentication-server radius` listing) are untouched.

## [3.0.0.4] - 2026-05-06

**Patch release — ClearPass `_send_request` private-method dependency wrapped (refactor only).**

ClearPass GET reads have to use `pyclearpass.ClearPassAPILogin._send_request(path, "get")` because the SDK doesn't expose a public list method for most resource types. That direct dependency on a private SDK method (the leading underscore) was scattered across 69 call sites in 16 tool files — if a future pyclearpass release renames or removes `_send_request`, all 69 sites break.

Wrapped the dependency in a single `clearpass_get(client, path)` helper in `platforms/clearpass/utils.py`, alongside the `build_query_string` helper added in v3.0.0.3. Now there's exactly one place to update if pyclearpass changes its transport layer.

Pure refactor. No behavior change — every call site produces the same HTTP request as before.

Closes [#126](https://github.com/nowireless4u/hpe-networking-mcp/issues/126).

### Files

- **`src/hpe_networking_mcp/platforms/clearpass/utils.py`** — added `clearpass_get(client, path)` helper. Single line of meaningful code (`return client._send_request(path, "get")`); the rest is a docstring explaining why the wrapper exists.
- **16 ClearPass tool files** (`audit.py`, `auth.py`, `certificate_authority.py`, `certificates.py`, `endpoint_visibility.py`, `endpoints.py`, `enforcement.py`, `guest_config.py`, `guests.py`, `identities.py`, `integrations.py`, `network_devices.py`, `policy_elements.py`, `roles.py`, `server_config.py`, `sessions.py`) — replaced 69 \`client._send_request(path, "get")\` calls with `clearpass_get(client, path)`. 10 files extended their existing `build_query_string` import; 6 files added a fresh import.
- **`tests/unit/test_clearpass_utils.py`** — added 3 new tests covering `clearpass_get` (delegation contract, path passthrough, return-value passthrough). 11 tests total in the file.
- **`pyproject.toml`** — bump 3.0.0.3 → 3.0.0.4.

### Notes

- 979 tests pass (was 976; +3 from the new helper tests).
- Scope deliberately limited to GET reads (the issue's stated target). The 139 remaining `_send_request` write-method call sites (POST / PATCH / DELETE) are unchanged. If a future pyclearpass change breaks them too, a follow-up PR can extend the wrapper to method-agnostic.

## [3.0.0.3] - 2026-05-06

**Patch release — ClearPass `build_query_string` consolidation (refactor only).**

Ten ClearPass tool files each carried a private byte-identical copy of `_build_query_string()` (52 grep hits across the platform). Extracted to a single `platforms/clearpass/utils.py` shared helper, dropped the leading underscore (it's now a real shared module-public helper, not module-private), and updated all 42 call sites. Net **−245 lines** across the ClearPass tool layer with no behavior change.

The new helper follows the same pattern as `central/utils.py:normalize_site_name_filter` — a small platform-scoped utility module for cross-tool helpers.

Closes [#125](https://github.com/nowireless4u/hpe-networking-mcp/issues/125).

### Files

- **`src/hpe_networking_mcp/platforms/clearpass/utils.py`** — new module; defines `build_query_string(filter, sort, offset, limit, calculate_count)`. Same body as the previous file-local copies.
- **`src/hpe_networking_mcp/platforms/clearpass/tools/`** (10 files: `audit.py`, `certificate_authority.py`, `certificates.py`, `endpoint_visibility.py`, `guest_config.py`, `identities.py`, `integrations.py`, `network_devices.py`, `policy_elements.py`, `server_config.py`) — removed the local `_build_query_string` definition; added `from hpe_networking_mcp.platforms.clearpass.utils import build_query_string`; renamed all call sites.
- **`tests/unit/test_clearpass_utils.py`** — new file pinning the helper's contract (defaults, filter/sort omission when None, calculate_count true/false casing, full-string ordering).
- **`pyproject.toml`** — bump 3.0.0.2 → 3.0.0.3.

### Notes

- 976 tests pass (was 968; +8 from the new test file).
- Pure refactor — no runtime behavior change. Every existing call site produces the exact same query string as before.

## [3.0.0.2] - 2026-05-06

**Patch release — `central_get_aps` empty-list contract fix.**

`central_get_aps()` returned the human-string `"No access points found matching the specified criteria."` when the AP list was empty, which broke caller patterns like `len(result)` (returned 38, the string length) and `for ap in result` (iterates over characters). Fix: return `[]` instead so callers can iterate without `None`/`str` guards.

Live-verified the broken behavior against the maintainer's Central workspace before fixing (issue #244 also reported `None` as a possible value, but the actual current behavior was the string — both fixed by the same change).

Closes [#244](https://github.com/nowireless4u/hpe-networking-mcp/issues/244).

### Files

- **`src/hpe_networking_mcp/platforms/central/tools/monitoring.py`** — replaced the empty-result string fallback with `return aps or []`. Single-line change. Type signature `-> list[dict] | str` unchanged (str now reserved for actual error paths).
- **`tests/unit/test_central_monitoring.py`** — new unit-test file pinning the empty-list contract (covers `None` → `[]`, `[]` → `[]`, populated → passthrough, SDK exception → error string).
- **`pyproject.toml`** — bump 3.0.0.1 → 3.0.0.2.

### Side housekeeping (not in this release; closed during review)

- **#243** (GreenLake `state` field shows `?`) — closed; verified live the GreenLake API field is `subscriptionStatus`, not `state`. Tool wrapper passes the raw response through unchanged. The `?` rendering was the AI's own placeholder for a missing field name. No code change needed.
- **#165** (Phase 7 v2.0 cleanup) — closed as no-longer-applicable; verified GreenLake aliases gone, `greenlake_tool_mode` config alias gone, dynamic-mode benchmarking implicitly answered by v3.0.0.0's default flip to code mode.

## [3.0.0.1] - 2026-05-06

**Patch release — aos-migration skill robustness pass from operator transcript.**

Three fixes from a live AOS 8.13.1.2 LSR audit transcript shared by Jon:

1. **Sandbox `AttributeError: 'str' object has no attribute 'get'`** when the AI hand-rolled an unwrap helper that dropped the outer dict-guard. AOS 8 read tools are typed `dict | str` and the v3 envelope wraps the string at `data` — so the inner payload can be a string. The skill's documented pattern was correct but verbose enough that AIs paraphrased it into a one-liner that crashed. Fix: skill now defines a verbatim `_unwrap()` helper at the top of Stage 1 with a "USE UNMODIFIED" directive. All inline unwrap snippets in COLLECT-01 / COLLECT-04 collapsed to `_unwrap(response)` calls.
2. **Stage 7 cluster-mode derivation false-negative on adopted APs** — the AI consulted the wrong `cluster_prof` (an inherited `East` cluster surfaced at the AP's site) and concluded the AP wasn't adopted, downgrading `CM_SITE` → `CM_MANUAL`. Live evidence confirmed `cluster_prof.cluster_controller[].ip` is the correct field and matches AP `Switch IP` / `Standby IP` exactly when iterated against the right profile. Fix: Stage 2 normalization now explicitly filters `_flags.inherited == True` cluster_prof rows (AOS 8's `entry_type="user"` keeps user-config but does NOT strip inherited copies); Stage 7 Step 4 now emphatically says "iterate EVERY deduped cluster_prof, do not skip / dedupe-by-name / short-circuit on the first match"; field-name guidance clarifies `ip` (per-controller mgmt) vs `vrrp_ip` (VRRP virtual — never an AP adoption target).
3. **Stage 7 missing per-scope configuration inventory + `/md`-prefixed persona-scope notation** — the AI emitted a hierarchy mapping but no manifest of which configured objects (cluster_prof, ssid_prof, role, server_group, ap_sys_prof, etc.) live at each scope, so the operator had no bridge from Stage 7 placement to Stage 8 per-object disposition. Separately, the persona-scope example used `/md/Branch` notation when Central has no `/md/` prefix in its hierarchy. Fix: added a REQUIRED per-scope configuration inventory table to Stage 7 (counts + named-object follow-up bullets per scope, definition-only — inherited copies don't double-count); added a clarification that AOS 10 / Central scopes use the operator-confirmable target name (no `/md/` prefix); fixed the persona-scope example row to reference the AOS 10 target name (`Branch` Site Collection); added explicit guidance for `/md`-root-defined objects since AOS 10's root is implicit (operator decides target scope per object).
4. **"5 placement types" + persona-scope concept were factually wrong** — the skill claimed AOS 10 has five placements including a "device persona scope," but per the Aruba Central VSG *Configuration Model* the actual five scopes are `Global` (implicit root), `Site Collection`, `Site`, `Device`, and `Device Group`. Personas are NOT a scope — they're a separate dimension called **Device Functions** (Campus Access Point, Mobility Gateway, VPNC, etc.) that filters which device types receive a profile within a given scope. Fix: replaced the "5 placement types" definition with the correct enumeration; renamed every "Inferred persona" column header / "persona-scope" placement reference to use Device Function framing; updated the VPNC example to map to a Device Group with Device Function = VPNC instead of a non-existent persona-scope; added a *Central scope placement: precedence + additive rules* section to Stage 8 documenting the precedence order (`Device > Device Group > Site > Site Collection > Global`), additive-profile behaviour (WLAN / VLAN / role / security policy assignments at multiple scopes add together), and default placement strategy for translated objects.
5. **Rule F5 ("Static AP IPs") was overclassified as REGRESSION** — the skill treated any static-AP-IP as migration-blocking. Per Jon's correction (operator domain knowledge from AP-onboarding workflows): the DHCP requirement applies **only to APs during initial Central onboarding** (Aruba Activate + first call-home); after an AP is adopted, the operator can reapply a static IP. The constraint does NOT apply to gateways or switches at all — those can be brought into Central static and stay static. Fix: F5 reclassified DRIFT (operator must ensure DHCP is available during the AP onboarding window, not a permanent / fleet-wide rule); finding wording reframed to scope it to APs and call out the gateway/switch carve-out; F5 moved from the REGRESSION block of the Act I template to the DRIFT block.

Closes [#269](https://github.com/nowireless4u/hpe-networking-mcp/issues/269), [#270](https://github.com/nowireless4u/hpe-networking-mcp/issues/270).

### Files

- **`src/hpe_networking_mcp/skills/aos-migration.md`** — added `_unwrap()` helper block at start of Stage 1 with USE-UNMODIFIED directive; replaced inline COLLECT-01 / COLLECT-04 unwrap snippets with `_unwrap()` calls; corrected COLLECT-04 AP name field (`ap["Name"]`, not `ap["ap_name"]`, per live AOS 8 API shape); Stage 2 normalization now requires `_flags.inherited == True` filter on cluster_profiles; Stage 7 Step 4 hardened with "iterate EVERY deduped cluster_prof" directive + `ip` vs `vrrp_ip` field clarification + skip-conductor-IP guard; added a REQUIRED per-scope configuration inventory table (object counts per scope + named-object bullets); added Central-scope-notation guidance (no `/md/` prefix); fixed persona-scope example row to use AOS 10 target name; added handling guidance for `/md`-root-defined objects; replaced the "5 placement types" enumeration with the correct Central scopes (Global / Site Collection / Site / Device / Device Group) and reframed personas as Device Functions throughout Stages 7-9 + Output formatting; added Stage 8 *Central scope placement: precedence + additive rules* section.
- **`pyproject.toml`** — bump 3.0.0.0 → 3.0.0.1.
- **`.gitignore`** — added `docs/central_configuration_model.md` (vendor copyright; kept locally for skill authoring, not redistributed via the repo).

## [3.0.0.0] - 2026-05-06

**Major release.** Three breaking changes bundled into one:

1. **`MCP_TOOL_MODE=static` REMOVED** — at 367 tools / ~64K tokens of schema, static mode was no longer practical. Setting it now raises `ValueError` at startup with a migration message.
2. **Default tool mode flipped from `dynamic` → `code`** — code mode exposes only `execute` + 5 discovery tools (`tags`, `search`, `get_schema`, `skills_list`, `skills_load`); all 367 underlying tools are reachable via `await call_tool(name, params)` inside the sandboxed Python `execute()` block. Smallest initial token cost; best for orchestrators driving small / local LLMs.
3. **Response envelope universal** — every tool's response is wrapped in `{ok, status, data, message, tool, platform}`. v2.5.1.0 prototyped this on 4 cross-platform tools; v3.0.0.0 expanded to every tool after Zach's OpenClaw + Qwen3 4B test confirmed the envelope worked for the small-local-model use case (#246 reassessment). The actual API payload always lives at `result["data"]`.

Closes [#246](https://github.com/nowireless4u/hpe-networking-mcp/issues/246), [#267](https://github.com/nowireless4u/hpe-networking-mcp/issues/267).

### Why this is one release, not three

The three changes are tightly coupled:
- Removing static mode removes the breaking-change concern from the original [#246](https://github.com/nowireless4u/hpe-networking-mcp/issues/246) envelope expansion (which had cited static-mode consumers as the load-bearing reason it had to be a major bump).
- Flipping the default to code mode fully realizes the envelope's value (uniform shape across every `call_tool()` return inside `execute()`).
- Doing all three together gives operators ONE breaking-change story to learn instead of three separate releases close together.

The original effort estimate was ~3 days per [#246](https://github.com/nowireless4u/hpe-networking-mcp/issues/246); actual work was a fraction of that because the test rewrite was much smaller than expected (unit tests call tool functions directly and bypass middleware, so envelope expansion didn't break them).

### Migration paths

| If you were running... | After v3.0.0.0... | Action |
|---|---|---|
| `MCP_TOOL_MODE=static` (explicit) | Hard error at startup with migration message | Switch to `dynamic` (per-platform meta-tools, ~3,700 tokens) or `code` (sandboxed `execute`, ~minimal tokens) |
| `MCP_TOOL_MODE=dynamic` (explicit) | Continues to work as before | Nothing required |
| `MCP_TOOL_MODE=code` (explicit) | Continues to work as before | Nothing required |
| No `MCP_TOOL_MODE` set (implicit default) | Now defaults to `code` mode (was `dynamic` in v2.x); startup log warns once | Set `MCP_TOOL_MODE=dynamic` in your compose to keep prior behavior |
| AI client checking `result["foo"]` directly on tool calls | Now needs `result["data"]["foo"]` (envelope wraps everything) | Update client code to navigate through the envelope |
| Static-mode `tools/call` usage | No longer supported | Use code mode (`execute` + `call_tool`) or dynamic mode (`<platform>_invoke_tool`) |
| `pydantic_monty` was previously installed via `fastmcp[code-mode]` extra | Now a hard requirement (code mode is default) | The extra is still on the dependency line; nothing to do for fresh installs |

### What's new

- **`src/hpe_networking_mcp/config.py`** — drop `static` from valid `MCP_TOOL_MODE` values; raise `ValueError` with migration message. Flip application default from `dynamic` → `code`. Log a startup migration message when env var unset.
- **Per-platform `__init__.py`** (Mist, Central, GreenLake, ClearPass, Apstra, Axis, AOS 8, `_template`) — drop the static-mode log branch; only dynamic / code remain.
- **`src/hpe_networking_mcp/server.py`** — cleanup `dynamic / static modes` comment to just `dynamic mode`.
- **`src/hpe_networking_mcp/middleware/response_envelope.py`** — drop `PROTOTYPE_TOOLS` allowlist; envelope wraps every tool universally. Already-enveloped responses still pass through idempotently.
- **`pyproject.toml`** — bump 2.5.2.1 → 3.0.0.0; updated `fastmcp[code-mode]` dependency comment to reflect code-mode-as-default (the extra is still required as a hard dep).
- **`docker-compose.yml`** (committed template) — comment out `MCP_TOOL_MODE=${MCP_TOOL_MODE:-dynamic}` so the application default takes effect for fresh installs. Explanatory comment for opting back into dynamic.
- **`tests/unit/test_code_mode.py`** — test contract updates: default is `code`, unknown values fall back to `code`, `static` raises ValueError. Removed `test_static_mode_registers_all_aggregators` (premise no longer applies).
- **`tests/unit/test_response_envelope_middleware.py`** — drop `PROTOTYPE_TOOLS` import; flipped `test_passes_through_non_prototype_tool` → `test_wraps_platform_prefixed_tool` (asserts `central_get_sites` IS wrapped now); replaced `test_prototype_tools_set_membership` with `test_wraps_aos8_tool` (verifies AOS 8 tools added after v2.5.1.0 are also wrapped).
- **`src/hpe_networking_mcp/skills/aos-migration.md`** — `response.get("result")` envelope unwrap → `response.get("data", response)` for v3 envelope shape; same for ap_database access in COLLECT-04.
- **`src/hpe_networking_mcp/INSTRUCTIONS.md`** — rewrote tool-discovery preamble for code-default + dynamic-opt-in; expanded "Response envelope" section to universal scope; flagged static-mode removal.
- **`README.md`** — comparison table heading + default-tool-surface callout + startup-log examples + architecture-diagram ASCII art + env-var table + troubleshooting section all updated for v3.0.0.0 reality.
- **`docs/TOOLS.md`** — code mode documented first (as default); dynamic mode follows (opt-in); static mode removal documented.

### Notes

- 964 tests still pass throughout. The unit-test suite calls tool functions directly (bypassing middleware) so the envelope expansion didn't break them. AI clients / orchestrators that previously checked `result["foo"]` directly on the wire will need to navigate through `result["data"]["foo"]` post-v3.0.0.0.
- `pydantic_monty` was already pulled in via `fastmcp[code-mode]` — no new dependency.
- Code mode's premise (LLM composes per-platform tools via `call_tool` inside the sandbox) explicitly does NOT include the cross-platform aggregators (`site_health_check`, `site_rf_check`, `manage_wlan_profile`) — those are workarounds for dynamic mode's "AI picks one platform and stops" problem. They remain registered only in dynamic mode.

## [2.5.2.1] - 2026-05-05

**`SandboxErrorCatchMiddleware` now signals `isError: true` on the wire for code-mode sandbox failures.** Reported by Zach during OpenClaw MCP execute testing — sandbox parse/runtime errors were reaching MCP clients as `isError: false` tool results, making it impossible for orchestrators to distinguish failed execution from successful JSON output that happened to contain error-shaped strings.

### Why

`SandboxErrorCatchMiddleware` (added in v2.x as the fix for [#208](https://github.com/nowireless4u/hpe-networking-mcp/issues/208) so the LLM can read sandbox error messages and self-correct) was returning the unwrapped error text via `ToolResult(content=...)`. FastMCP's `ToolResult` doesn't expose `isError` — that flag is set on the wire only when a tool raises an exception. Returning a `ToolResult` always gets `isError: false`.

The trade-off had been: LLM gets readable error message ✓ / orchestrator sees error flag ✗. After Zach's bug report we have evidence both halves are needed: the agent self-corrected through 5+ retries (the message is reaching it correctly), but the orchestrator's trace recorded every failed iteration as a successful tool call.

### Fix

`SandboxErrorCatchMiddleware` now **re-raises a fresh `ToolError`** carrying the unwrapped sandbox error text, instead of returning a `ToolResult`. Verified empirically against FastMCP's masking logic (`server.py:1241-1243`): the `except FastMCPError` branch re-raises `ToolError` instances unchanged before the generic `except Exception` masking branch can wrap them. So a middleware-raised `ToolError` propagates to the wire with `isError: true` AND our enriched message intact.

Live verification in the dev container with intentionally bad indentation (` return 1` — the same shape as the model-generated code that triggered Zach's report):

```
Sandbox error: Unexpected indentation at byte range 1..2
```

The MCP client received the response wrapped in error-marker tags (proving `isError: true` on the wire) AND the readable cause text in the content. Successful execute calls continue to work unchanged.

### What's new

- **`src/hpe_networking_mcp/middleware/sandbox_error_catch.py`** — middleware now raises `ToolError(error_text) from cause` instead of returning `ToolResult(content=error_text)`. Module docstring updated with the call-chain reasoning (middleware sits outside the masking layer; `ToolError` from middleware bypasses `mask_error_details`). Removed the unused `ToolResult` import.
- **`tests/unit/test_middleware.py`** — `test_catches_monty_runtime_error_on_execute` renamed to `test_catches_monty_runtime_error_on_execute_and_re_raises`, asserts `pytest.raises(ToolError)` instead of `result.content`. New regression test `test_catches_monty_syntax_error_and_re_raises` pins the OpenClaw-reported syntax-error path specifically (built via real `MontySyntaxError` from ` return 1`). Both tests verify the original cause is preserved on `ToolError.__cause__` for telemetry.

### Validates / closes

- Closes the OpenClaw-reported isError signaling bug (no GitHub issue filed; reported via maintainer's session).
- Re-validates [#208](https://github.com/nowireless4u/hpe-networking-mcp/issues/208) — message readability is preserved (the LLM still sees the actual error cause, just now via the standard error-response path instead of via content of a successful response).

### Notes

- Patch (`x.x.x.X`) bump — bug fix, no API surface change. Behavior change: clients that previously checked `result.content` for error-shaped text on a successful response now need to check `isError` per the MCP spec. This matches what the spec says clients should do anyway.
- Docs-only files (README, INSTRUCTIONS, TOOLS.md) unchanged — no tool surface change, no operator-visible workflow change.

## [2.5.2.0] - 2026-05-05

**Central Gateway Cluster Intent (GCIS) tools + `aos-migration` Stage 7 cluster-mode derivation.** Closes [#261](https://github.com/nowireless4u/hpe-networking-mcp/issues/261). Adds 4 new Central tools for managing AOS 10's gateway cluster orchestration plane — the migration target for AOS 8 `cluster_prof` + `group_membership`.

### Why a minor (`x.x.X.x`) bump

Two changes that depend on each other:

1. **Skill change** (Stage 7 cluster-mode derivation) cites `central_manage_gateway_cluster_intent_profile` and `central_manage_gateway_cluster` as the migration targets. Without those tools, the disposition matrix would emit a `[Central API gap]` placeholder — operators reading the migration plan would see "use these tools" with no tools to use.
2. **Tool change** (4 new Central tools for GCIS + realized cluster profiles) is a new subsystem area on Central — gateway clustering wasn't covered before.

Bundling them so the skill and the tool surface ship together; an image with the skill update but missing the tools would be a half-shipped feature.

### What's new — Central tools

Two new tool files (4 tools total):

- **`src/hpe_networking_mcp/platforms/central/tools/gateway_cluster_intent.py`**:
  - `central_get_gateway_cluster_intent_profiles` — list or single GCIS intent profile (optional `name` and `scope_id` parameters). API path: `network-config/v1alpha1/gw-cluster-intent-config[/{name}]`.
  - `central_manage_gateway_cluster_intent_profile` — create / update / delete a GCIS intent profile. Supports `cluster-mode` (`CM_SITE` / `CM_MANUAL`), `device-type` (persona — defaults to `MOBILITY_GW`), `multicast-vlan`, `heartbeat-threshold`, `ipv6-enable`, `coa-enable`, `coa-vrrp`, `default-gateway-mode` (1:1 redundancy for BRANCH_GW), `uplink-tracking`, `uplink-sharing`, `description`. Scope-id + device-function for LOCAL profiles. Gated by `ENABLE_CENTRAL_WRITE_TOOLS=true` + elicitation on update / delete.
- **`src/hpe_networking_mcp/platforms/central/tools/gateway_clusters.py`**:
  - `central_get_gateway_clusters` — list or single realized gw-cluster profile. API path: `network-config/v1alpha1/gateway-clusters[/{name}]`.
  - `central_manage_gateway_cluster` — create / update / delete a realized cluster profile. Supports `ipv4-gateways[].mac` and `ipv6-gateways[].mac` member lists (up to 12 per profile, fewer on some platforms), `auto-cluster` (false for manual; reserved for GCIS-managed auto-clusters when true), `one-to-one-redundancy`, `multicast-vlan`, `heartbeat-threshold`, `uplink-tracking`, `coa-vrrp`, `description`. Manual cluster names cannot start with `auto_` (reserved prefix) or contain spaces. Scope-id + device-function for LOCAL profiles. Gated + elicitation as above.

Both tool files modeled on the existing `roles.py` / `server_groups.py` patterns: shared/local scoping via `scope_id` + `device_function` query params, elicitation on non-create operations, success/error response normalization.

### What's new — `aos-migration` skill

Completes the Stage 7 cluster-mode derivation work that v2.5.1.3 left as TBD. The algorithm was locked after live probing confirmed AOS 8 has no cluster-mode field — the mode is fully derivable from `ap_database.Switch IP`/`Standby IP` matching `cluster_prof.cluster_controller[].ip`, with `ap_multizone_prof.controller[].ip` providing enrichment for distinguishing tunnel anchors from DMZ/unused clusters.

8 places in the skill updated:

- Stage 7 Step 4 — pseudo-code for the derivation, conductor exclusion, multizone enrichment, external multizone target detection.
- Stage 7 output template (9-column shape) — example rows for AP-bearing site, multizone anchor, and unused/DMZ clusters.
- Stage 6 readiness template — Cluster mode column changes from `decide` to `CM_SITE` / `CM_MANUAL` (auto-derived).
- Act II Stage 7 report template — same column treatment.
- Stage 8 cluster_prof + group_membership disposition row — Notes column now references the GCIS target tool flow (no longer a `[Central API gap]` since the tools exist).
- Stage 9 API call sequence — new dependency rule: cluster intent profile → realized cluster (manual only) before any object scoped to cluster gateways.
- Stage 10 validation checklist — 2 new rows mapping the cluster manage tools to their read-back tools.
- New INFO finding type — *External multizone target* surfaces multizone IPs that are neither in any source `cluster_prof` nor managed by this conductor.
- Skill `tools:` allowlist — 4 new Central tool names added.
- Line 86 overview — adds AOS 10 cluster-mode to the auto-derived inputs list.

### Validated against live data

Lab probing on ArubaMM-VA at 172.23.4.21 (AOS 8.12.0.5):

| Cluster | Origin scope | APs adopted | AOS 10 mode (derived) | AOS 10 target tool flow |
|---|---|---|---|---|
| `site-cluster` | `/md/Campus/West` | 1 AP (Switch IP 10.104.23.219) | CM_SITE | `central_manage_gateway_cluster_intent_profile` (intent) → GCIS auto-creates realized profile |
| `East` | `/md/Campus` | 0 | CM_MANUAL | intent + `central_manage_gateway_cluster` (explicit member MACs) |
| `ACX-AOS8-CLUSTER` | `/md/ACX` | 0 | CM_MANUAL | intent + `central_manage_gateway_cluster` (explicit member MACs) |

Plus one INFO finding from the lab: *"AP-group 'Indoor' multizone-1 references 192.168.199.250 — not in any source cluster, not managed by this conductor. External standalone controller; migrates to a single Central gateway."*

### Tests

- **`tests/unit/test_central_gateway_clusters.py`** — new test file covering all 4 new tools: API-path pinning, query-param shape (object-type + scope-id + device-function for LOCAL), method-per-action (POST/PATCH/DELETE for create/update/delete), error-response normalization, invalid-action-type validation. 12 new tests.
- **`tests/unit/test_skill_tool_references.py`** — removed the temporary allowlist entries for `central_manage_gateway_cluster_intent_profile` and `central_manage_gateway_cluster` (added in v2.5.1.4 as forward references; now the tools exist).

### Notes

- Central tool count: 83 → 87 (+4 in the new gateway clustering subsystem).
- The skill's disposition row no longer flags this as a `[Central API gap]` — operators following the migration plan can now run the tools end-to-end.
- Did NOT ship as v2.5.1.4 (the original plan) because the tool addition is a new Central subsystem area, qualifying for a minor bump per the project's versioning rules.

## [2.5.1.3] - 2026-05-05

**`aos-migration` skill — full alignment with the v2.5.1.2 OBJECT_TYPES rewrite + new hierarchy mapping rules engine.** Closes [#255](https://github.com/nowireless4u/2hpe-networking-mcp/issues/255), [#256](https://github.com/nowireless4u/hpe-networking-mcp/issues/256), [#257](https://github.com/nowireless4u/hpe-networking-mcp/issues/257).

### Why

v2.5.1.2 fixed the COLLECT-01 `OBJECT_TYPES` list (correct REST schema names) but left the rest of the skill internally inconsistent. Stage 6 readiness templates, Stage 7 hierarchy rules, Stage 8 disposition matrix, and the Act II report templates all still embedded the OLD object names and an OLD 4-level structural hierarchy model that didn't match what the skill was actually collecting. Operators reading the audit output would have seen mismatched names and a hierarchy mapping that didn't reflect any of the design discussion (5 placement types, persona dimension, naming heuristics, cluster-mode-driven decisions).

This release closes that loop. Surfaced when Jon manually inspected the skill after v2.5.1.2 shipped — would have caused confusing test output otherwise.

### Hierarchy mapping rules engine (#255)

AOS 10 / Central has **5 placement types**, not 4: `Site Collection`, `Site`, `Device Group`, **`device persona scope`**, and the implicit `(global)` root. Persona is a first-class scope dimension — config can apply to "all VPNCs at scope X" without creating a Device Group. Stage 7 now produces a draft classification per `/md/<path>` Group node using:

- **Step 1 — Drop conductor / mobility-manager scope:** `/md` and `/mm`+descendants → `drop`.
- **Step 2 — Determine persona for each Device child** by cross-referencing the Stage 1 inventory. Personas in scope: `MOBILITY_GW` (default for AOS 8 MDs — = WLAN gateway), `VPNC` (never has APs), `BRANCH_GW` (SD-Branch CPE; never has APs; rare in 8.x), `MICROBRANCH_AP`, `CAMPUS_AP`. Out-of-scope (`ACCESS_SWITCH`, `AGG_SWITCH`, `CORE_SWITCH`, `BRIDGE`, `HYBRID_NAC`) are flagged and skipped.
- **Step 3 — Classify each Group node** by structure + naming + persona signal (priority-ordered):
  - Has child Group nodes → `Site Collection` (high)
  - Plural noun in name (`Branch_Sites`, `Stores`) → `Site Collection` (medium)
  - `_Static` suffix → `Device Group` (medium)
  - Children include APs → `Site` (auto-clustering re-enabled in AOS 10) (high)
  - Children uniformly VPNC or BRANCH_GW → persona-scope at parent **unless** `cluster_prof` present + manual mode → Device Group (medium)
  - Children uniformly MOBILITY_GW (no APs — DMZ pattern) AND `cluster_prof` present → operator confirms cluster mode (medium)
  - Geographic / cardinal noun (`East`, `Dallas`, three-letter region codes) → `Site` (high)
  - No matching signal → `Device Group` (low; operator review)
- **Step 4 — Cluster mode disambiguation:** auto-site cluster → Site; manual cluster → Device Group. **The auto-vs-manual mode field in `cluster_prof` has not yet been validated against a populated cluster** — until then, operator confirms the mode for every scope where `cluster_prof` is defined. The draft mapping marks those rows `decide`. Automated detection is a planned enhancement.

The Stage 7 output table is **promoted from 5 columns to 9** to capture: `Source AOS node`, `Source path`, `Disposition`, `Target type`, **`Inferred persona`**, **`Cluster mode signal`**, `Target name`, **`Confidence`**, `Notes`. The Stage 6 readiness template ("Suggested AOS 10 hierarchy mapping") and the Act II Stage 7 report template both adopt the same expanded shape. Operator confirmation is required for any `medium` or `low` confidence row, and for any row where `cluster_prof` is defined.

### Object-name corrections (#256)

13+ downstream references in the skill still used AOS 8 CLI nouns instead of REST schema names. v2.5.1.2 fixed COLLECT-01 but didn't propagate. Now all aligned:

| Old (CLI noun) | New (REST schema) |
|---|---|
| `aaa_server_group` | `server_group_prof` |
| `wlan_ssid_profile` | `ssid_prof` |
| `lc_cluster_profile` | `cluster_prof` (+ `group_membership` where MD-binding is referenced) |
| `reg_domain_profile` | `reg_domain_prof` |
| `arm_profile` | `arm_prof` |
| `user_role` | `role` |
| `ip_access_list` | split: `acl_sess` / `acl_eth` / `acl_mac` |
| `captive_portal_auth_profile` | `cp_auth_profile` |
| `dot1x_authentication_profile` | `dot1x_auth_profile` |
| `mac_authentication_profile` | `mac_auth_profile` |
| `dot11a_radio_prof` + `dot11g_radio_prof` | `ht_radio_prof` (combined since AOS 8.4) |

Stage 8 source-type enumeration rewritten with all corrected names plus `cluster_prof`, `group_membership`, and the 3-way ACL split. Disposition rules table updated to reflect the new names. Example disposition matrix rows in the Act II report template updated. F7 finding text updated to reference `arm_prof` / `ht_radio_prof` / `reg_domain_prof`. OPERATOR-MAP example findings updated with corrected object names and the new `entry_type='user'` argument.

### `internal_db_server` cleanup (#257)

Central replaces internal-DB auth entirely (per session discussion). The Stage 8 disposition row for `internal_db_server` has been removed — the F2 REGRESSION finding ("Internal Authentication Server in use with local users") stays and is sourced from `local-userdb` text dump, not from a missing REST-object lookup. Stage 8 source-type enumeration explicitly notes the absence to prevent future re-introduction. Inventory dict's `aaa_servers.internal_db` key removed.

### Files changed

- `src/hpe_networking_mcp/skills/aos-migration.md` — Stage 6 readiness template, Stage 7 rules + output template, Stage 8 disposition rules + source-type enumeration, Act II Stage 7 report template, F7 finding, OPERATOR-MAP examples, inventory dict structure. ~9 KB of skill content rewritten.
- `pyproject.toml` — v2.5.1.3.

### What this does NOT do

The cluster auto-vs-manual mode signal still requires operator confirmation. The exact `cluster_prof` schema field that distinguishes the two modes hasn't been validated against a populated cluster yet — when that's done, the rules engine can detect it automatically and the `decide` action can become `auto`. Marked as TBD in the skill.

### Notes

- This release was prompted by Jon's manual inspection catching that v2.5.1.2 only updated COLLECT-01 and not the rest of the skill. Saved as a feedback memory: when a discussion produces a new model, audit every place the old model is embedded — not just the immediate code path.
- Verified live against an ArubaMM-VA Conductor (AOS 8.12.0.5) for the v2.5.1.2 work; the v2.5.1.3 skill rewrite uses the same source-of-truth examples (ACX, Branch, Branch_VPNC, Branch_Sites_Static, Branch_Sites, Campus East/West).

## [2.5.1.2] - 2026-05-04

**Comprehensive AOS 8 audit fallout — restores 8 broken read tools, adds `entry_type` filter for ~93% smaller migration audits, fixes 11 wrong object names in `aos-migration` skill.** Surfaced by a live audit of all 35 aos8 tools against an ArubaMM-VA Conductor (AOS 8.12.0.5).

### Why

After v2.5.1.1 fixed `aos8_get_md_hierarchy` (#248) and improved decode-error diagnostics (#249), an audit of every aos8 tool against the live Conductor showed **9 more tools** were silently broken and **11 of 20** object names in the `aos-migration` skill's COLLECT-01 list were wrong. Three discoveries:

1. **`run_show()` crashed on valid commands with empty / text bodies.** Tools like `aos8_get_alarms`, `aos8_get_clients`, `aos8_get_events`, `aos8_get_audit_trail`, `aos8_get_logs`, etc. were all returning the cryptic *"Expecting value: line 1 column 1 (char 0)"* error — but the underlying commands were valid. The AOS 8 `showcommand` REST endpoint just returns an empty body when there's no data (no clients, no alarms) or a plain-text body for log/audit dumps. `run_show()` called `response.json()` and crashed. Issue [#252](https://github.com/nowireless4u/hpe-networking-mcp/issues/252).
2. **`/v1/configuration/object/<name>` accepts a `type=user` filter** that strips factory defaults and returns only customer-defined entries. Live A/B testing across 20 object types × 5 hierarchy scopes: response payload shrinks ~93% (~145 KB → ~10 KB per scope). For migration audits, defaults are pure noise — the AI should only see customer config. Issue [#253](https://github.com/nowireless4u/hpe-networking-mcp/issues/253).
3. **The `aos-migration` skill's hard-coded `OBJECT_TYPES` list was authored against AOS 8 CLI command nouns**, not REST schema names. 11 of 20 names silently returned `{"ERROR": "Invalid Object"}` — meaning critical config (RBAC roles, ACLs, ARM, auth profiles, cluster) was being dropped from every migration plan against every Conductor. Operator-facing translation was materially incomplete and the failure mode was invisible. Issue [#250](https://github.com/nowireless4u/hpe-networking-mcp/issues/250).

### What's new

- **`src/hpe_networking_mcp/platforms/aos8/tools/_helpers.py`**:
  - `run_show()` now mirrors `aos8_show_command`'s passthrough contract on non-JSON bodies: empty body → `{}` (success, no data); text body → `{"output": <text>}`. Restores 8 tools to working state without changing their tool surfaces.
  - `get_object()` adds an optional `entry_type` parameter that maps to AOS 8's `type` query filter (`"user"`, `"local"`, `"default"`, `"inherited"`). `get_object()` remains strict on JSON parsing — the object endpoint always returns JSON or an `Invalid Object` envelope, so non-JSON bodies there indicate a real protocol problem (AOS8DecodeError from v2.5.1.1).
- **`src/hpe_networking_mcp/platforms/aos8/tools/differentiators.py`** — `aos8_get_effective_config` exposes `entry_type` to AI callers with documentation pointing at migration audits as the primary use case.
- **`src/hpe_networking_mcp/skills/aos-migration.md`** — COLLECT-01 `OBJECT_TYPES` list rewritten with 11 corrected REST schema names: `aaa_server_group` → `server_group_prof`; `wlan_ssid_profile` dropped (duplicate of `ssid_prof`); `reg_domain_profile` → `reg_domain_prof`; `arm_profile` → `arm_prof`; `dot11a_radio_prof` + `dot11g_radio_prof` → `ht_radio_prof` (combined since AOS 8.4); `user_role` → `role`; `ip_access_list` → 3-way split into `acl_sess` / `acl_eth` / `acl_mac`; `captive_portal_auth_profile` → `cp_auth_profile`; `dot1x_authentication_profile` → `dot1x_auth_profile`; `mac_authentication_profile` → `mac_auth_profile`; `lc_cluster_profile` → `cluster_prof` + `group_membership` (paired); `internal_db_server` dropped (Central replaces internal-DB auth entirely). COLLECT-01 loop now defaults to `entry_type="user"` and surfaces `Invalid Object` responses as `_collection_error` so future schema drift fails loudly instead of silently dropping rows.
- **`tests/unit/test_aos8_read_differentiators.py`** — replaces the v2.5.1.1 strict-decode test on `aos8_get_md_hierarchy` (now graceful) with two new tests for the empty/text body shapes; adds a strict-decode test on `aos8_get_effective_config` to pin the `get_object()` contract; adds two tests for `entry_type` (passes through as `type` query param when set; omitted from query when `None`).

### What this does NOT do

Air-monitor coverage (`aos8_get_air_monitors` sends `show ap monitor active-laser-beams`, which is a WIDS feature, not the AM AP list) is **not fixed in this release**. Dropped from scope: the `aos-migration` skill doesn't use it, AP mode is already accessible from `aos8_get_ap_database`, and dedicated air-monitor APs are largely deprecated in AOS 10. Tool stays broken-but-harmless until a future skill needs it.

The hierarchy-mapping rules engine for the `aos-migration` skill (translating AOS 8 `/md/<path>` nodes to AOS 10 site collection / site / device group / device persona) is **deferred** — design discussion in progress; needs live cluster data before rules can be locked in.

### Notes

- This is the third instance ([#237](https://github.com/nowireless4u/hpe-networking-mcp/issues/237), [#248](https://github.com/nowireless4u/hpe-networking-mcp/issues/248), now [#250](https://github.com/nowireless4u/hpe-networking-mcp/issues/250)) of mistakes that would have been caught by live verification against a real device. Future schema-touching changes should be live-verified before merge — not just unit-tested against fixtures.
- Verified live against a `developer.arubanetworks.com/aos8/reference`-documented schema. The reference site is the authoritative source for REST object names; CLI nouns are not a reliable mapping.

## [2.5.1.1] - 2026-05-04

**`aos8_get_md_hierarchy` was sending an unrecognized CLI command — fixed; AOS 8 helpers now diagnose decode failures.** Two related bugs surfaced from an `aos-migration` operator transcript:

- The differentiator tool was issuing `show switch hierarchy` (singular), which is not a real AOS 8 CLI command. The Conductor's CLI parser silently rejected it and returned an empty body, which `run_show()` couldn't parse → bare `JSONDecodeError` → cryptic *"Expecting value: line 1 column 1 (char 0)"* error reaching the AI. The hand-built fixture invented both the command name and the response shape, so the unit test was passing against a fiction. Verified live against an ArubaMM-VA conductor (AOS 8.12.0.5): the correct command is `show configuration node-hierarchy`, returning a `Configuration node hierarchy` table with `Config Node` / `Name` / `Type` columns. Issue [#248](https://github.com/nowireless4u/hpe-networking-mcp/issues/248).
- More generally, every AOS 8 read tool that goes through `run_show()` or `get_object()` was leaking raw `json.JSONDecodeError` messages on any 2xx-with-non-JSON response (empty body, HTML login redirect, plaintext error). The bare error gave the AI no hint about *what* failed. Helpers now raise `AOS8DecodeError` with HTTP status, content-type, body length, and a body preview, which `format_aos8_error()` renders as an actionable diagnostic. Issue [#249](https://github.com/nowireless4u/hpe-networking-mcp/issues/249).

A follow-up issue [#250](https://github.com/nowireless4u/hpe-networking-mcp/issues/250) tracks the related `aos-migration` skill bug — 13 of 20 names in the COLLECT-01 `OBJECT_TYPES` list are not valid AOS 8 REST schema names; that fix lands separately.

### What's new

- **`src/hpe_networking_mcp/platforms/aos8/tools/differentiators.py`** — `aos8_get_md_hierarchy` now sends `show configuration node-hierarchy`. Docstring updated to reflect the real top-level response key.
- **`src/hpe_networking_mcp/platforms/aos8/tools/_helpers.py`** — new `AOS8DecodeError` class + `_decode_json_or_raise()` helper. `run_show()` and `get_object()` route their `response.json()` calls through it. `format_aos8_error()` gains a branch for `AOS8DecodeError` so the diagnostic surfaces verbatim instead of falling into the generic *"Unexpected error"* path.
- **`tests/unit/fixtures/aos8/show_configuration_node_hierarchy.json`** — replaces hand-built `show_switch_hierarchy.json` with a real-shape capture (16 rows: System / Group / Device entries spanning `/md/ACX`, `/md/Branch`, `/md/Campus/East`, `/md/Campus/West`, `/mm/mynode`).
- **`tests/unit/test_aos8_read_differentiators.py`** — `test_get_md_hierarchy` updated to the new command + shape; new `test_get_md_hierarchy_non_json_body_diagnoses_decode_error` regression test ensures decode failures surface a structured diagnostic with HTTP status, content-type, and body length, and that the bare json-module error never leaks to callers.

### Notes

- This is the second instance (after [#237](https://github.com/nowireless4u/hpe-networking-mcp/issues/237)) of a hand-fabricated fixture masking a real-world bug. Live-capture-only fixtures remain mandatory for new code paths.

## [2.5.1.0] - 2026-05-04

**Response envelope prototype (v3.0.0.0 candidate).** Wraps the four cross-platform tools (`health`, `site_health_check`, `site_rf_check`, `manage_wlan_profile`) in a uniform response envelope so AIs navigating their output learn one shape instead of four bespoke ones. Tracked in issue [#246](https://github.com/nowireless4u/hpe-networking-mcp/issues/246) for the full v3.0.0.0 expansion to every tool in the catalog.

### Why

Operator transcripts surfaced a code-mode AI hitting *"`central.message` / `http_status` were read from the wrong level"* — a class of error caused by every tool having its own response structure. A smart-dict wrapper (overridden `__missing__` for helpful KeyError messages) was prototyped and **empirically rejected**: the Monty sandbox runtime strips dict subclasses across the boundary, so subclass behavior doesn't reach the AI. The only structural fix that survives marshaling is changing the data **shape** itself.

This release ships the shape change scoped to four tools to validate the pattern before committing to the full v3 refactor (which would be a breaking change for static-mode consumers across all 312 tools).

### Envelope shape

```
{
  "ok":       bool,            # success indicator
  "status":   int | null,      # HTTP status (200 / 401 / 503) or null for non-HTTP
  "data":     <any>,           # the actual payload — list, dict, or null
  "message":  str | null,      # human-readable error / context message
  "tool":     str,             # tool name (e.g. "health")
  "platform": str | null       # platform-prefix-derived; null for cross-platform
}
```

For multi-platform tools like `health`, the inner `data` preserves each platform's natural shape rather than triple-nesting envelopes.

### What's new

- **`src/hpe_networking_mcp/middleware/response_envelope.py`** — new `ResponseEnvelopeMiddleware`. Allowlist-scoped to `PROTOTYPE_TOOLS = {health, site_health_check, site_rf_check, manage_wlan_profile}`. Other tools short-circuit and pass through unchanged. Idempotency check ensures already-enveloped responses (a tool returning the envelope explicitly) are not re-wrapped.
- **`src/hpe_networking_mcp/server.py`** — middleware wired into the chain as **innermost** (last in the list), so it wraps raw tool output before retry / PII / elicitation / etc. process the response. RetryMiddleware's status-code extraction works equally on the envelope's `status` field as on raw `status_code`/`code`/`http_status`.
- **`tests/unit/test_response_envelope_middleware.py`** — 27 new unit tests covering platform inference, status extraction, envelope-shape detection, success wrapping, prototype-tool short-circuit (non-allowlisted tools pass through), idempotency on already-enveloped responses, and `None`-structured-content handling.
- **`INSTRUCTIONS.md`** — new "Response envelope on cross-platform tools" section telling AIs how to navigate the new shape: payload is at `result["data"]` for these four tools; everything else returns native shape.

### What this does NOT do

- **Doesn't apply to the other 308 tools.** Their response shapes are unchanged. The full v3 refactor is tracked separately as [#246](https://github.com/nowireless4u/hpe-networking-mcp/issues/246).
- **Doesn't fix wrong-level access inside `data`.** The envelope makes the *outer* shape uniform; the inner `data` field still has tool-specific structure. Reduces the navigation surface from "every tool has a different shape" to "the four cross-platform tools all start at `data`," which is genuinely simpler but not a panacea.
- **Doesn't fix pure Python logic errors** like `same_scope_id = scope_a or scope_b` returning a string instead of a bool. Those are AI capability issues no platform change can paper over.
- **Doesn't update skill text** to reference the new envelope shape — skills describe data semantically and AIs adapt with one global note in `INSTRUCTIONS.md`. Skill-text updates are deferred to v3 to amortize across the full refactor.

### Decision criteria for promoting to v3

- Operator sessions on the four wrapped tools show no regressions from the existing shape.
- AI behavior is observably better on these tools (fewer wrong-level errors).
- Test/skill update pattern is mechanical enough to scale to 312 tools without surprises.
- PII tokenization continues to work correctly through the envelope (verified — PII walker descends into `data` recursively; envelope metadata fields like `tool` and `platform` aren't tracked field names).

### File touches

- `src/hpe_networking_mcp/middleware/response_envelope.py` — new (143 lines)
- `src/hpe_networking_mcp/server.py` — added 1 import + 1 line in middleware chain
- `tests/unit/test_response_envelope_middleware.py` — new (213 lines, 27 tests)
- `src/hpe_networking_mcp/INSTRUCTIONS.md` — new envelope-explanation section
- `pyproject.toml` — version 2.5.0.1 → 2.5.1.0
- `CHANGELOG.md` — this entry

No skill text changes; no breaking changes; no platform code changes.

## [2.5.0.1] - 2026-05-04

**Eight-item cleanup pass on the `aos-migration` skill driven by operator transcripts.** Drops AOS 6 and Instant AP support, deletes the Stage 0 operator interview, replaces controller-plumbing REGRESSION rules with inventory-only entries, adds applicability gates so empty environments don't generate spurious findings, introduces an `EMPTY-SOURCE` verdict, makes Stage 1 walk the full `/md` hierarchy in code-mode orchestration, and adds a `usage_state` column to the disposition matrix so unused/orphaned config still gets translated.

### Why

Three operator transcripts surfaced overlapping issues:

1. The skill was generating four pages of AI reasoning to converge on **BLOCKED** for an environment with **zero APs** — rule logic that made sense for a populated production migration produced false positives against empty/lab deployments.
2. The AI was getting hung up on `lms-ip: 192.168.120.1` when source clusters were offline. LMS-IP is controller plumbing that dissolves at migration (APs go to Central, not to controllers); flagging it as REGRESSION is technically correct under the old rule set but operationally meaningless.
3. The Stage 1 collection at `/md` root only — silently missing customer config defined at `/md/<region>` or below. The AI in one session discovered this organically by widening the scope manually; the skill should have done it by design.

The user's framing was sharp: *"It should never assume configuration shouldn't be migrated just because it isn't used."* That's now a design principle encoded in Stage 8.

### Eight changes

1. **Delete Stage 0 interview entirely.** No operator questions. The skill detects AOS 8 reachability via `health()` and derives every input from collected config (target SSID forwarding mode auto-recommended from `forward-mode` in `virtual_ap` rows; cluster topology from `lc_cluster_profile` + `aos8_get_cluster_state`; AirWave presence from config grep; L3 Mobility from effective-config). Operator overrides any auto-derived value when reviewing the report.
2. **Delete AOS 6 + Instant AP support.** Skill is AOS 8 → AOS 10 only. AOS 6 has a different migration path; IAP customers usually flow through classic Central. Operator-facing redirect message at Stage -1 if either is named.
3. **Stage 1 hierarchy walk in code-mode orchestration.** The skill now describes a Python pattern the AI executes inside `mcp__hpe-networking__execute`: walk every node in `aos8_get_md_hierarchy()`, query effective-config per object type per scope, aggregate. No new tools needed — this is pure orchestration in code mode. Closes the silent under-collection bug.
4. **Reframe rules: inventory vs feature-parity vs orchestration prerequisite.** Controller-plumbing rules (LMS-IP, Backup-LMS-IP, AP Fast Failover, cluster L2/L3 connectivity, VRRP VIP placement) are now **inventory rows** — they appear in the report's inventory section and inform Act II translation, but do NOT fire as REGRESSION/DRIFT. Real REGRESSION rules are limited to **feature-parity gaps** (Internal Auth Server, AAA FastConnect, L3 Mobility, VC-managed WLANs, static AP IPs, AirWave dependency, default Captive Portal cert) and **orchestration prerequisites** (controller firmware floor, Central reachable, GreenLake AP-license capacity).
5. **Applicability gates on every rule.** Each rule has a `requires:` clause. Rules don't fire on empty source surfaces (zero APs → no Static-AP-IP rule fires; zero local users → no Internal-Auth-Server REGRESSION; etc.). Eliminates the false-positive cascade against bare deployments.
6. **`EMPTY-SOURCE` verdict** for environments with zero customer-defined objects across all `/md` scopes. Skill stops emitting REGRESSION for hypothetical scenarios and acknowledges *"source has only AOS 8 system defaults — no migration work required."* Act II is still offered (translation plan for whatever defaults exist).
7. **`usage_state` column on the disposition matrix.** Every configured object gets a row regardless of whether it's `assigned-and-active` / `configured-but-unassigned` / `orphaned`. The customer's running config is the source of truth; whether something is in use today is metadata, not a basis for excluding it from migration.
8. **Cluster-offline tolerance.** When `aos8_get_cluster_state()` returns degraded data (clusters offline at audit time), prefer `lc_cluster_profile` config rows as the source of truth. Rules that need live state mark `inconclusive`. Audit always proceeds — never blocks on cluster-offline.

### Stage 4 trim

Translated the previous 13-row Central-side check table into:
- **Stage 4a — Migration orchestration prerequisites** (5 checks): Central reachable, GreenLake AP-license capacity ≥ source AP count, AP onboarding gap, NAD list coverage for new AP subnets (gated), NAD list coverage for cluster gateways/VRRP VIPs (gated).
- **Stage 4b — Translation enrichment for Act II** (5 enrichments): WLAN-profile name collisions, role-name collisions, named-VLAN ID collisions, server-group collisions, per-AP-model AOS 10 firmware recommendation. These don't gate the verdict — they tag rows in the disposition matrix.

Removed: ClearPass server-certificate validity check (out of scope; ClearPass cert health is its own ops concern, not a migration predictor); GreenLake subscription-by-subscription enumeration (replaced with single AP-license-vs-AP-count comparison); A11 ClearPass-vs-AOS8 local-user dual-source-of-truth check (folded into rule F2).

### Bugs filed alongside this patch

Two real platform-tool bugs surfaced by the operator transcripts; filed as separate issues with one-line tool-layer fixes:

- [#243](https://github.com/nowireless4u/hpe-networking-mcp/issues/243) — `greenlake_get_subscriptions` `state` field shows `?` instead of actual values
- [#244](https://github.com/nowireless4u/hpe-networking-mcp/issues/244) — `central_get_aps` returns `None` for empty AP list (should return `[]`)

### File touches

- `src/hpe_networking_mcp/skills/aos-migration.md` — skill rewrite (~400 lines changed, 968 lines total)
- `src/hpe_networking_mcp/INSTRUCTIONS.md` — line-88 trigger row drops AOS 6 / IAP triggers, adds AOS-8-only note
- `docs/TOOLS.md` — line-156 entry rewritten for v2.5.0.1 changes
- `pyproject.toml` — version 2.5.0.0 → 2.5.0.1
- `CHANGELOG.md` — this entry

No code/platform changes. Skill text + docs only.

## [2.5.0.0] - 2026-05-04

**Renames `aos-migration-readiness` skill → `aos-migration` and expands it from a readiness-only audit into a full migration workflow.** Closes [#239](https://github.com/nowireless4u/hpe-networking-mcp/issues/239). Substantial new subsystem → minor version bump per project policy.

### What's new

The skill now operates in two acts:

- **Act I (Stages -1 through 6) — readiness audit.** Unchanged from v2.4.0.7. Always runs. Ends with the verdict + combined readiness report.
- **Act I → Act II gate.** After the Act I report, the AI emits one of three literal prompts based on verdict (BLOCKED locks translation; GO/PARTIAL prompt for `yes / no / edit-context`) and stops. No Act II execution without operator `yes`.
- **Act II (Stages 7 through 10) — translation plan.** Conditional on a non-BLOCKED verdict and explicit operator confirmation:
  - **Stage 7 — Hierarchy translation.** AOS 8 `/md/<region>/<site>/<ap-group>` → AOS 10 Site Collection / Site / Device Group, anchored on VSG §1529-§1535.
  - **Stage 8 — Per-object translation matrix.** Disposition matrix (direct-translate / transform / drop / deprecated / operator-driven / inconclusive) for AAA / roles / ACLs / AP profiles / WLAN profiles / VAPs / 802.1X / captive portals / ARM / ClientMatch / AP overrides. Per-row anchor cells use real VSG section numbers when they exist; literal `none` when the VSG is silent (most non-WLAN-SSID-profile rows).
  - **Stage 9 — Central API call sequence.** Topologically ordered plan respecting dependencies (server-group → role-acl → role → WLAN profile → config-assignment). Three known Central API gaps (AAA servers, AAA server-groups, AP system profiles) emit `[Central API gap — manual UI: <area>]` placeholder steps that downstream API calls reference as prerequisites.
  - **Stage 10 — Validation checklist.** Maps each `central_manage_*` create-step to its corresponding `central_get_*` read-back call with expected attributes.

The skill emits the **plan**. It does NOT execute `central_manage_*` write tools. Phase 3 — actual execution — is deferred per [#240](https://github.com/nowireless4u/hpe-networking-mcp/issues/240).

### New finding type

`OPERATOR-MAP` joins the existing REGRESSION / DRIFT / INFO triple. One finding per `operator-driven` matrix row — flags object types the VSG doesn't auto-map (TACACS / LDAP servers, MAC-auth profiles, captive portals, MAC randomization, individual role/ACL attribute mappings). The Act II header narrative counts OPERATOR-MAP separately so operators can scan the manual-mapping work items independently.

### Honest scope language

The VSG itself stops short of per-object translation tables outside two worked SSID examples (CorpNet 802.1X §2127-§2219, OpsNet WPA3-Personal §2222-§2308). The skill does NOT fabricate VSG anchors where none exist; rows without real anchors carry the literal `vsg-anchor: none` cell and emit `OPERATOR-MAP` findings. The output-hygiene rules now explicitly forbid invented VSG anchors and invented Central tool names (the latter for the three documented Central API gaps).

### File touches

- **Renamed:** `src/hpe_networking_mcp/skills/aos-migration-readiness.md` → `src/hpe_networking_mcp/skills/aos-migration.md`. Frontmatter `name: aos-migration`. Tools array expanded with the Central write tools and read tools needed for Act II (`central_manage_site`, `central_manage_role`, `central_manage_role_acl`, `central_manage_net_group`, `central_manage_net_service`, `central_manage_wlan_profile`, `central_manage_config_assignment`, `central_get_role_acls`, `central_get_net_groups`, `central_get_net_services`, `central_get_aliases`).
- **`tests/unit/test_skill_aos8_live_detection.py`** — `SKILL_PATH` updated to new filename; docstring + assertion message references updated.
- **`src/hpe_networking_mcp/INSTRUCTIONS.md`** — line-88 trigger row expanded with translation-themed phrases (`"translate AOS 8 config to AOS 10"`, `"AOS 10 config mapping"`, `"build me an AOS 10 migration plan"`, `"generate Central API call sequence for migration"`).
- **`docs/TOOLS.md`** — line-156 entry renamed and rewritten to describe the two-act workflow.

### Why the rename

Three operator transcripts captured AI behaviors on the readiness-only skill that revealed a broader scope mismatch — operators expected the skill to also produce config translation, and AIs flip-flopped or freelanced when asked. v2.4.0.7 hardened the readiness scope language to make the boundary explicit; v2.5.0.0 closes the gap by absorbing translation into the same skill. Single workflow, single invocation, conditional second half. Drops "readiness" from the name because the skill is no longer readiness-only.

### Migration notes

No tool / API breaking changes. The frontmatter `name:` rename means the skill loads under its new name in `skills_list()` / `skills_load()`. Operator-facing trigger phrases work identically (and now include translation phrases too). Operators who want only the readiness portion can answer `no` at the gate and end the session with the unchanged Act I report.

## [2.4.0.7] - 2026-05-04

**Technical corrections + scope hardening for the `aos-migration-readiness` skill, surfaced by three operator transcripts where AI behavior on the skill went off-spec.** Closes the immediate issues; the broader skill expansion (rename + per-object config translation) is tracked as [#239](https://github.com/nowireless4u/hpe-networking-mcp/issues/239) and shipping next as v2.5.0.0.

### Fixed

- **Technical correction — ARM is replaced by RF Profiles, not AirMatch.** The skill had been claiming "ARM Profiles / Dot11a/g Radio Profiles / Regulatory Domain Profiles … replaced by **AirMatch** in Central" in five places. That conflates two different RF management features: AirMatch already exists in AOS 8 as a separate feature and continues into AOS 10 / Central — it is not the AOS 10 ARM replacement. The legacy ARM (Adaptive Radio Management) profile system is replaced by **RF Profiles** in AOS 10 / Central. ClientMatch tunable language stays correct. Affected lines: skill body §1855, §1163-§1166 rule body, C4 rule row, paste-mode A-row table, REGRESSION findings template. (Has been wrong since v2.3.0.6.)
- **VALID8 references removed.** VALID8 is HPE channel-partner-only; references in a public MCP project are inappropriate. Five mentions across the skill (objective intro, "data sources" block, "read-only" disclaimer, PoC caveats footer) replaced with neutral *"customer's standard change-management process and partner-tool guidance"* phrasing. Historical CHANGELOG entry for v2.3.0.6 also updated to remove the VALID8 callout.

### Added

- **`Scope boundaries (what this skill is and is NOT)` section** added directly under the Objective. Three IS bullets (readiness audit, hierarchy mapper, cutover sequencer) and three IS-NOT bullets (config translator, migration executor, per-object translation engine). The IS-NOT bullets reference issue [#239](https://github.com/nowireless4u/hpe-networking-mcp/issues/239) for the v2.5 expansion that will cover those gaps. Operators asking for any "is NOT" item now get an explicit boundary acknowledgement instead of AI flip-flopping or freelancing.
- **`Output format is mandatory — do NOT substitute alternatives` clause** added to the Output formatting section. Explicitly forbids: diagrams/charts/ASCII art in place of mandatory tables; prose paragraphs in place of finding lists; collapsed multi-finding rows; reframed verdicts. Closes the failure mode where an AI argued that "a side-by-side hierarchy diagram is genuinely more legible" and tried to substitute its preferred format for the spec'd hierarchy mapping table.
- **Promoted the trigger description from passive to imperative.** First line of the description is now `PRIMARY TRIGGER — invoke this skill whenever the operator mentions AOS 6, AOS 8, or Instant AP migration to AOS 10 or Aruba Central in any phrasing. Do NOT improvise or skip the skill: it carries the VSG-anchored rule set and the live AOS 8 collection sequence that free-form analysis cannot reproduce.` Previous wording read as suggestion; this reads as instruction.

### Why

Three operator transcripts captured AI behaviors that boil down to: (a) substituting output formats the AI judged "more legible" for the formats the skill specifies, (b) flip-flopping on what's in/out of scope when an operator asks a clarifying question, (c) treating the trigger phrase list as suggestive rather than authoritative ("the AI didn't want to use the skill at first"). The fix isn't "make the AI behave" — you can't — it's making the spec's boundaries explicit enough that going off-spec requires the AI to consciously override clear instructions, which is rarer.

## [2.4.0.6] - 2026-05-03

**v2.4.0.5 follow-up — adds `version` and `release_type` to `DEVICE_CONTEXT_HINTS`. Tracks issue [#237](https://github.com/nowireless4u/hpe-networking-mcp/issues/237).**

v2.4.0.5 shipped with a passing unit test for the AOS 8 controller-record tokenization, but live verification immediately after release showed `Name: MM-01` was *still* coming through cleartext on real `aos8_get_controllers` responses. Root cause: the test fixture had been seeded with a `firmware` sibling key (which IS in `DEVICE_CONTEXT_HINTS`), but live AOS 8 returns `Version` and `Release Type` instead. Without those in the hint set, the bare-`name` heuristic had only `Model` matching — one hint, below the ≥2 threshold introduced in v2.3.1.2 — so tokenization didn't fire.

### Fixed

- **`src/hpe_networking_mcp/redaction/rules.py`** — added `version` and `release_type` to `DEVICE_CONTEXT_HINTS`. Both are strong device-shape signals: `version` is universal across switch/AP/controller records; `release_type` is Aruba-specific (LSR / SSR / UNCLASSIFIED) and effectively unique to Aruba device records, so false-positive risk is negligible.
- **`tests/unit/test_pii_redaction.py`** — replaced the rigged `firmware` key in two AOS 8 fixtures (`test_aos8_controller_name_via_bare_name_with_device_siblings`, `test_aos8_controller_record_tokenizes_name`) with the actual live shape captured from a real Mobility Conductor: `Config ID`, `Configuration State`, `IP Address`, `Location`, `Model`, `Name`, `Release Type`, `Status`, `Type`, `Version`. The test now reflects production rather than a happy path.

### Why this got past unit tests once already

The v2.4.0.5 fixture seeded `"firmware": "8.12.0.5"` to "represent" the controller's `Version` field. That short-circuited the heuristic — `firmware` is a hint, so the test passed without proving that `Version` would also work. Lesson logged in memory: when adding regression tests for response-shape bugs, the fixture must come from real captured responses, not a hand-typed approximation that "looks similar."

### Live verification

After the v2.4.0.6 deploy, `aos8_get_controllers` now returns `"Name": "[[HOSTNAME:<uuid>]]"` instead of `"Name": "MM-01"`. The previously-cleartext fields (`IP Address`, `Location`, `Model`) remain cleartext per the design intent — IPs are intentionally not tokenized; geographic/model info is operational metadata.

## [2.4.0.5] - 2026-05-03

**PII tokenization improvement for AOS 8 — extend the field-name normalizer to treat spaces the same as hyphens, so AOS 8's space-separated `showcommand` headers (`"AP name"`, `"Host Name"`, `"Wired MAC Address"`) match the existing snake_case rules. Closes the *flat-record* tokenization gap on AOS 8 responses; the transposed key/value shape used by `show <foo> detail` commands (RADIUS / TACACS / LDAP server detail) is tracked separately as issue [#235](https://github.com/nowireless4u/hpe-networking-mcp/issues/235).** Mist and Central are not affected — their APIs use snake_case / camelCase exclusively, so the change is a no-op there.

### Why

When AOS 8 was added in v2.4.0.0 it inherited the Mist/Central PII rules unchanged. Live traffic against a real Mobility Conductor showed that AOS 8 responses use space-separated column headers, which our normalizer (lowercased + hyphen→underscore only) didn't reach. Result: AP names, host names, and `Mac Address`/`Wired MAC Address` columns were arriving cleartext to the AI even though Mist/Central rules already existed for those concepts.

Live verification against a real `show switches` response confirmed `"Name": "MM-01"` survived as cleartext because:
1. `"Name"` lowercased to `"name"` — bare, requires sibling-context to fire.
2. The sibling `"Model"` was a valid hint, but `"IP Address"`, `"Type"`, etc. weren't normalizing for the parent-key intersection check, so only one device-context hint matched (need ≥2).

### What changed

- **`src/hpe_networking_mcp/redaction/rules.py`** — extracted the field-name normalizer into a `_normalize_field_name()` helper that does `lower() + "-" → "_" + " " → "_"`. `classify_field()` uses it for the field name being classified, AND for the parent-keys set when checking the bare-`name` heuristic. Added three identifier-field aliases: `host_name` (AOS 8 client tables), `controller_name`, `switch_name` — all → HOSTNAME.
- **`src/hpe_networking_mcp/redaction/walker.py`** — MAC-field detection in `_walk_pair` now goes through the same normalizer. Added `mac_address` and `wired_mac_address` to `_MAC_FIELD_HINTS` to cover AOS 8's column-header form.
- **`tests/unit/test_pii_redaction.py`** — added 6 regression tests using the actual live `aos8_get_controllers` response shape so future changes can't silently regress: `test_aos8_ip_address_field_normalizes`, `test_aos8_ap_name_with_space_tokenizes_as_hostname`, `test_aos8_host_name_field_tokenizes_as_hostname`, `test_aos8_controller_name_via_bare_name_with_device_siblings`, `test_aos8_controller_record_tokenizes_name`, `test_aos8_mac_address_with_space_normalized`.

### Not addressed in this patch (tracked in #235)

The transposed key/value shape used by `show <foo> detail` commands — where the actual JSON field names are literally `"Parameter"` and `"Value"` — defeats field-name-based classification entirely. RADIUS/TACACS server hosts/IPs visible in those responses still come through cleartext. AOS 8 itself masks the shared secret server-side (`'********'`), so secrets aren't at risk; the residual gap is server identifiers. Issue #235 covers the response-flattening work and the new `host` / `rad_server_name` / `tacacs_server_name` rules needed to close it.

## [2.4.0.4] - 2026-05-03

**Security patch — AOS 8 UIDARUBA session token was being written to INFO-level logs on every API request. Fix scope: redact `UIDARUBA=` query values and `SESSION=` cookie values in the AOS 8 transport request/response logging hooks; close the test blind spot that let the leak ship undetected.** Tracks issue [#233](https://github.com/nowireless4u/hpe-networking-mcp/issues/233). Affects every release in the v2.4.0.x series before this one running with AOS 8 secrets configured. Operators without AOS 8 enabled are unaffected (the platform is gated off when `aos8_*` secrets are missing or empty, and the leaking code never executes).

### Fixed

- **`src/hpe_networking_mcp/platforms/aos8/client.py`** — added a `SESSION=<value>` cookie regex to complement the existing `UIDARUBA=<value>` regex, and applied both via a new unified `_sanitize_for_log()` helper to the `Cookie` request header, the request query string, and the `Set-Cookie` response header in `_log_request` / `_log_response`. The previous slicing-only "redaction" (`[:40]`, `[:60]`, `[:80]`) chopped the end off the secret but left the leading entropy fully exposed. The login line continues to use `mask_secret()` for the head-and-tail-with-ellipsis form so operators can correlate sessions in logs without exposing the token.
- **`tests/unit/test_aos8_client.py`** and **`tests/unit/test_aos8_security.py`** — fixed `_install_mock_transport` / `_install` to swap only the transport on the persistent `client._http` (`client._http._transport = MockTransport(...)`) instead of constructing a fresh `AsyncClient`. The fresh-client pattern silently dropped the request/response event hooks defined in `_make_http_client`, which is why the existing leak tests passed against vulnerable code — the leaking log statements never fired during the test. This change mirrors the production code path the round-1 PR #230 review fix B1 established (persistent `_http`).
- **Tightened the existing leak assertions and added a new one** — every log line that mentions `UIDARUBA=` OR `SESSION=` must now also contain `<redacted>` (positive assertion, complementing the prior negative-only "bait token not in log" check). New `test_set_cookie_session_value_redacted_in_response_log` directly drives a `Set-Cookie: SESSION=<token>` header through the response hook and asserts the response-log line contains `SESSION=<redacted>`.

### Mitigation if you've been running v2.4.0.0–v2.4.0.3 with AOS 8 enabled

See issue #233 for detection (`docker compose logs | grep 'AOS8 HTTP.*UIDARUBA='`) and pre-fix mitigation (`LOG_LEVEL=warning`). Operators who collected logs and want to invalidate already-leaked tokens can rotate `aos8_username` / `aos8_password` Docker secrets; UIDARUBA tokens issued under the old credentials become unusable once the new credentials are first used.

## [2.4.0.3] - 2026-05-03

**Final polish on the AOS 8 / Mobility Conductor platform module from PR #230 — the last 3 test failures, an `INSTRUCTIONS.md` doc gap, and a compose-default revert. Lands together with @dendyc's contribution rather than as a separate follow-up. No functional change to AOS8 itself.**

### Fixed

- **`docker-compose.yml`** — reverted Mist / Central / ClearPass / Apstra / Axis write-tool defaults from `:-true` back to `:-false`; AOS8 stays `:-false`. The `:-true` flips were an accidental capture of a local development compose during the PR rebase and would have changed every existing operator's security posture on upgrade.
- **`tests/integration/test_server.py`** — `test_no_visibility_transform_when_write_tools_enabled` now passes `enable_aos8_write_tools=True` so the AOS8 visibility transform doesn't fail the assertion.
- **`tests/unit/test_aos8_read_differentiators.py`** — aligned 2 test assertions to match implementation: `test_get_md_hierarchy` expects `"show switch hierarchy"` (was `"show configuration node-hierarchy"`), `test_get_cluster_state` expects `"show lc-cluster group-membership"` (was `"show switches"`). Implementation was correct; tests had stale strings from earlier iteration.

### Added

- **`src/hpe_networking_mcp/INSTRUCTIONS.md`** — added AOS 8 / Mobility Conductor as the 7th platform: top intro paragraph, `aos8_*` namespace row, MM vs MD context guidance, tool categories breakdown (health, WLAN, differentiators, clients, alerts, troubleshooting, writes), pending-changes workflow, write-tool safety notes. Also picked up the missing `axis_*` namespace row (pre-existing oversight from when AXIS shipped). Tool count at session start updated 24 → 27 (4 cross-platform + 7 × 3 meta-tools + 2 skills).

## [2.4.0.2] - 2026-05-01

**AOS8 PR #230 review fixes — squash-rebase onto upstream main + reviewer-requested code cleanups. No new functionality; addresses reviewer feedback B1, B2, B3, B4, C1, C2 from upstream PR review.**

### Fixed

- Fixed httpx client reuse so MockTransport-based tests pass (closes #230 review B1)
- Fixed ruff I001 import-order errors in aos8/client.py and tests/unit/test_aos8_write.py (B2)
- Reverted FASTMCP_STATELESS_HTTP=true addition in docker-compose.yml (B4)
- Changed ENABLE_AOS8_WRITE_TOOLS default to false to match other platforms (C1)
- Removed dead AOS8Client.reset_session() method (C2)
- Rebased onto upstream/main and bumped version to 2.4.0.2 (B3)

## [2.3.1.8] - 2026-05-01

**New skill: `morning-coffee-report`. Daily ops digest for the open-the-laptop-with-coffee read with two output modes — engineer-detailed (default) and executive-summary (business-language). Combines audit-log activity (who's been in Central / Mist over the last 24h and what they did), active alerts/alarms, top talkers (clients and APs by load), and Mist Marvis SLE insights. Phase 1 covers Mist + Central with last-24h scope. Day-over-day delta deferred to phase 2; ClearPass / Apstra / Axis coverage deferred to phase 3.**

Tracks GitHub issue [#231](https://github.com/nowireless4u/hpe-networking-mcp/issues/231). Requested by Seth and Bruno.

### What's new

- **`src/hpe_networking_mcp/skills/morning-coffee-report.md`** — new bundled skill (~250 lines). Five output sections: headline, activity, what's broken, top talkers, insights. Strict output template specified — same approach as `central-scope-audit` and `mist-scope-audit` to keep different runs comparable.

- **Trigger phrases in `INSTRUCTIONS.md` Section 8:** *"morning coffee report"*, *"morning coffee"*, *"morning digest"*, *"morning rundown"*, *"give me the rundown"*, *"what happened overnight"*, *"who's been in Central / Mist over the last day"*. Universal trigger words from v2.3.1.4 (audit, summary, overview, daily) help narrow to skills generally; these specific phrases route to `morning-coffee-report`.

- **Tools used (all existing — no new platform tools needed for phase 1):**
  - Mist: `health`, `mist_get_self`, `mist_search_audit_logs`, `mist_search_events`, `mist_search_alarms`, `mist_search_client`, `mist_search_device`, `mist_get_org_sle`, `mist_get_org_sites_sle`, `mist_get_site_sle`, `mist_get_insight_metrics`
  - Central: `central_get_audit_logs`, `central_get_audit_log_detail`, `central_get_alerts`, `central_get_alert_classification`, `central_get_clients`, `central_get_aps`, `central_get_sites`, `central_get_site_health`

### Output modes

Two output shapes share one data-gathering procedure. The mode is selected by the user's trigger phrasing — no parameter needed.

- **Engineer mode (default)** — full digest with five sections (headline, activity, what's broken, top talkers, insights). Includes tool names, platform names, raw counts, IPs/MACs/sites. Triggered by *"morning coffee report"*, *"morning digest"*, *"give me the rundown"*, *"what happened overnight"*, *"who's been in Central / Mist over the last day"*.
- **Executive mode (new)** — one-paragraph business-language summary, ≤100 words. No tool / platform / IP / MAC / port references. Same gas-gauge color but framed as plain-English impact and recommended decisions. Triggered by *"executive summary"*, *"exec briefing"*, *"summary for the boss / leadership"*, *"high-level summary"*, *"30-second summary"*, *"what do I tell my manager"*. Sections: gas gauge → bottom line → what matters today (0–2 bullets) → recommended action. On 🟢 GREEN status the report collapses to 3 lines.

Authoring rules for executive mode are enforced in the skill body — drop technical jargon, round counts, use business-impact framing ("a site has reduced wireless reliability"), no top-talker section, no audit-log per-user breakdown.

### What the report covers (engineer mode)

1. **Status indicator + headline** — leads with a 🟢 GREEN / 🟡 YELLOW / 🔴 RED gas-gauge color so the operator can decide in two seconds whether to read deeper. Green = skip, yellow = read headline, red = read everything. The rubric is computed from data the procedure already collected (no extra tool calls): RED on any Critical alert / SLE <75% / unavailable platform; YELLOW on any Major alert / SLE 75–85% / capacity warnings; GREEN otherwise. Then the 3–5 sentence headline.
2. **Activity** — audit-log digest: per-user event counts grouped by login / read / write actions. Highlights users who took config write actions; surfaces top 3 actions per user with target resource.
3. **What's broken right now** — active alerts/alarms severity-ordered (Central via `central_get_alert_classification`, Mist via `mist_search_alarms`). Top 5 per platform; collapses repeats; flags Critical with 🔴 prefix.
4. **Top talkers** — top 5–10 clients by traffic and top APs by client count or load, per platform. Callouts when a single client uses >40% of traffic or an AP has 50+ concurrent clients.
5. **Insights** — Mist SLE rollup (worst category, worst site). Central side surfaces alert-category trends from classification data.

### What's deferred (per issue #231)

- **Phase 2:** day-over-day delta — "what changed since yesterday" requires either re-querying with a yesterday time window and computing diffs in the runbook, or storing yesterday's snapshot. Approach decided in phase 2 design.
- **Phase 3:** ClearPass session/auth-failure summary, Apstra fabric anomalies, Axis connector status — extend coverage to platforms beyond Mist + Central.

### Tests

- 742 passing (unchanged) — `test_skill_tool_references.py` verifies every tool referenced in the new runbook resolves to a registered tool, plus the new entry in `INSTRUCTIONS.md` Section 8.

### Docs

- `docs/TOOLS.md` skills table gains a `morning-coffee-report` row.
- `INSTRUCTIONS.md` Section 8 gains the trigger row.

## [2.3.1.7] - 2026-04-30

**Documentation refresh — pulls stale tool counts and structural references in `README.md`, `docs/TOOLS.md`, `CLAUDE.md`, `INSTRUCTIONS.md`, and `docs/MIGRATING_TO_V2.md` up to v2.3.1.6 reality. No code changes; one bandit/ruff/mypy/pytest run confirms 742 still passing.**

### What changed

**README.md:**
- Comparison table: Aruba Central tool count `73 + 12 prompts` → `83 + 12 prompts`.
- Architecture diagram: Central `73 tools` → `83 tools`.
- "Verify" troubleshooting section: corrected the per-platform tool counts surfaced in `docker compose logs` output, and the dynamic-mode tool surface (`24` exposed, `312` underlying — was `22` / `300+`).
- "Tool Surface Looks Wrong" troubleshooting: explicit `24 tools / 312 underlying` framing including the 2 skills tools (was missing from the breakdown).
- Project structure: test count `639+` → `740+` unit tests.

**docs/TOOLS.md:**
- Dynamic-mode opener: `19 tools` → `24 tools` (added the 2 skills tools, expanded from 5 platforms to 6 to include Axis).
- Code-mode tag-list example: Mist `31 tools` → `35`, Central `73` → `83` to match reality.
- Overview table: Aruba Central row `60 / 13 / 12 / 85` → `63 / 20 / 12 / 95` (covers v2.3.1.5 alert-action + v2.3.1.6 alert-config tools).
- Section headers: `Aruba Central (73 tools + 12 prompts)` → `83 tools`, `Juniper Apstra (21 tools)` → `19 tools`, added missing `(10 tools)` to the GreenLake section.

**CLAUDE.md (substantial rewrite of three sections):**
- "Project Overview" now lists all 6 platforms (was 4 — missed Apstra and Axis).
- "Current State (as of 2026-03-28)" → "Current State (as of 2026-04-30, v2.3.1.6)". Replaced "49 tools registered: 29 Mist + 10 Central + 10 GreenLake" with the real `312 tools across 6 platforms` breakdown plus tool-mode summary, PII tokenization, and skills bullet points.
- "Project Structure" rewritten to reflect v2.3.1.x reality: middleware now lists all 7 modules (added `origin_validation`, `pii_tokenization`, `retry`, `sandbox_error_catch`, `validation_catch`); new `redaction/` package documented; `skills/` directory listed; platform sections updated to current tool counts; Apstra and Axis sections added.
- "Conventions" — corrected `ENABLE_WRITE_TOOLS=true` (singular) to the real per-platform env vars (`ENABLE_MIST_WRITE_TOOLS`, `ENABLE_CENTRAL_WRITE_TOOLS`, etc.); noted `OPERATIONAL` annotation tools aren't gated by these; added `ALLOWED_ORIGINS` reference.
- "Known Issues" replaced with current "Open Items / Known Quirks" — the v0.5-era issues (2 Mist tools failing to load, pycentral API surprises, GreenLake meta-tools deferred) are all resolved.
- "Testing (not yet implemented)" comment fixed; bandit added to commands.
- "Secrets File Reference" extended with `apstra_*` and `axis_api_token`.

**INSTRUCTIONS.md (AI-facing):**
- Tool-discovery opener: `18 tools` → `24 tools` (added skills tools and 6th platform).
- Central tool category: split single `Alerts: central_get_alerts` line into two well-described entries — `Alerts (instances)` covering the v2.3.1.5 list/classification/state-transition tools, and `Alert configurations (rules)` covering the v2.3.1.6 read/create/update/reset tools, with a clear note about which is which.

**docs/MIGRATING_TO_V2.md:**
- Added a "this document is a v1→v2.0 snapshot" note at the top so readers don't mistake the v2.0-era counts for current.

**Skipped (per scope agreement):**
- Skill markdown files — INSTRUCTIONS.md is the authoritative trigger source; per-skill descriptions are descriptive rather than load-bearing.
- `docs/PRD.md` and `docs/PRP.md` — internal planning artifacts, not user-facing.

### Tests

- 742 passing (unchanged) — no code touched. Pre-push checks confirm clean ruff/format/mypy/bandit/pytest.

## [2.3.1.6] - 2026-04-30

**Adds Aruba Central alert *configuration* management — the rules that determine when alerts fire — wrapping the four `/network-notifications/v1/alert-config` endpoints. Distinct from v2.3.1.5's alert *action* tools (clear / defer / reactivate / set-priority) which act on already-fired alert instances; these manage the alert system's threshold definitions. New module `tools/alert_configs.py`; the existing `tools/alerts.py` is left at its current size below the 500-line cap.**

### What's new

One read tool (`READ_ONLY` annotation):

- **`central_get_alert_configs(scope_id, scope_type?)`** — list the alert configurations defined at a scope. Each item carries `inherited: true/false` (whether this scope has its own override or is using a parent's config) and `ruleSource: SYSTEM | USER` (Central built-in vs. operator-customized). Hits `GET /alert-config`.

Three write tools (`WRITE_DELETE` annotation, tagged `central_write_delete`, gated behind `ENABLE_CENTRAL_WRITE_TOOLS`, fire elicitation):

- **`central_create_alert_config(type_id, scope_id, enabled, clear_timeout?, rules?, scope_type?)`** — create a custom alert configuration. Hits `POST /alert-config/create`.
- **`central_update_alert_config(type_id, scope_id, enabled?, clear_timeout?, rules?, scope_type?)`** — update existing. Despite using HTTP PUT, the API behaves like PATCH: fields you omit are preserved. Hits `PUT /alert-config/update`.
- **`central_reset_alert_config(type_id, scope_id, scope_type?)`** — remove the scope-level override and revert to inherited (parent-scope) configuration. The alert *type* is not deleted; only the override at this scope. Hits `DELETE /alert-config/delete`.

### Annotation choice

These tools are `WRITE_DELETE` (gated behind `ENABLE_CENTRAL_WRITE_TOOLS`) — different from v2.3.1.5's alert-action tools which were `OPERATIONAL`. Reasoning:

- v2.3.1.5 tools act on alert *instances* — operational state transitions, like rebooting a switch.
- v2.3.1.6 tools act on alert *definitions* — config writes that change what the system tracks. Same threat model as managing roles, policies, WLAN profiles. Belongs in the gated write surface.

### Rule shape

Both `create` and `update` accept a `rules: list[dict] | None` parameter with the API's literal camelCase shape:

```python
rules=[
    {
        "ruleNumber": 0,
        "duration": 300,                 # seconds metric must stay over threshold
        "conditions": [
            {"severity": "CRITICAL", "operator": "GT", "threshold": 90.0},
            {"severity": "MAJOR",    "operator": "GT", "threshold": 80.0},
        ],
        "additionalConditions": [],
    },
]
```

- Severity values: `CRITICAL`, `MAJOR`, `MINOR`, `INFO`.
- Operator values: `EQ`, `NEQ`, `GT`, `GTE`, `LT`, `LTE`, `IN`, `NIN`.
- `clearTimeout` format: `<number><unit>` where unit is `H`/`h` (hours), `D`/`d` (days), or `M`/`m` (minutes) — e.g. `1H`, `30D`, `15m`.

The tool docstrings include the full shape + enum reference inline so the AI can construct rules without consulting external docs.

### Scope semantics

The `scope_type` parameter on every tool accepts `GLOBAL` (tenant-wide, default), `SITE` (per-site), or `DEVICE` (per-device). `GLOBAL` is the default if omitted, matching the API.

### Tests

- 741 passing (was 739). Net +2: catalog assertions for the four new tools (no fixture — avoids the v2.3.1.5 `importlib.reload` clash with `configuration.py`'s `ActionType` enum identity); the existing `test_central_dynamic_mode.py` `test_write_tools_carry_write_delete_tag` test was extended to cover the three new write tools, plus a new `test_alert_config_read_has_no_write_tag` for the read tool.

## [2.3.1.5] - 2026-04-30

**Adds Aruba Central alert state-management tools — clear, defer, reactivate, set-priority — plus alert classification and async-task status. Six new tools, all in the existing `central_*` alerts surface. Requested feature; existing `central_get_alerts` tool gains a `key` field on each returned `Alert` so the AI can pass keys through to the new action tools.**

### What's new

Two read tools (`READ_ONLY` annotation):

- **`central_get_alert_classification(classify_by, filter, search)`** — group alerts by `severity` / `status` / `priority` / `category` / `device_type` / `impacted_devices` and return per-bucket counts. Cheaper than paging through `central_get_alerts` when you only need a summary. Hits `GET /network-notifications/v1/alerts/classification`.
- **`central_get_alert_action_status(task_id)`** — poll the result of any of the four action tools. The action endpoints are async and return a `task_id`; this tool checks completion. Hits `GET /network-notifications/v1/alerts/async-operations/{task_id}`.

Four operational tools (`OPERATIONAL` annotation — fires elicitation prompt for confirmation but NOT gated behind `ENABLE_CENTRAL_WRITE_TOOLS`; rides alongside reboot/AP-action tools):

- **`central_clear_alerts(keys, reason, notes?)`** — Active → Cleared. `reason` is required, enum: `Problem was resolved` / `False Positive` / `Insufficient information for troubleshooting` / `Alert is not important` / `Other`. Optional free-text `notes`. Hits `POST /alerts/clear`.
- **`central_defer_alerts(keys, defer_until)`** — Active → Deferred until the specified ISO 8601 datetime. Auto-reactivates if condition still applies after that time. Hits `POST /alerts/defer`.
- **`central_reactivate_alerts(keys)`** — Cleared/Deferred → Active. Use to undo a clear or pull a defer back early. Hits `POST /alerts/active`.
- **`central_set_alert_priority(keys, priority)`** — Operator-assigned priority (`Very High` / `High` / `Medium` / `Low` / `Very Low`), distinct from system-assigned `severity`. Hits `POST /alerts/priority`.

All four action tools accept a list of `keys` (batch) and return the async task descriptor — chain a `central_get_alert_action_status(task_id)` call to confirm completion.

### Model change

- `Alert.key: str | None` — new field. The list endpoint's raw alert key field is unconfirmed against production data; `clean_alert_data` defensively maps `key` → `id` → `alertId` (whichever exists). Pin to the actual field once observed in the wild.

### Tests

- 741 passing (was 732). Net +9: model-key handling (5 cases covering each fallback path), tool registration (3 cases), tag-gating (2 cases — operational tools NOT carrying `central_write_delete`).

### Behavior matrix

| State transition | Tool |
|---|---|
| Active → Cleared | `central_clear_alerts` |
| Active → Deferred | `central_defer_alerts` |
| Cleared → Active | `central_reactivate_alerts` |
| Deferred → Active | `central_reactivate_alerts` |
| Any priority change | `central_set_alert_priority` |

## [2.3.1.4] - 2026-04-30

**Broadens the Skills trigger guidance in `INSTRUCTIONS.md` so the AI more reliably loads `mist-scope-audit` / `central-scope-audit` (and the other bundled runbooks) on natural-language audit queries that don't include the literal word "scope". `INSTRUCTIONS.md`-only change; no Python code, no skill body changes — the skills themselves were already producing rich output when triggered.**

### Why

Two consecutive sessions on the same chat asked *"Do a config audit for this site."* — same query verbatim. Central's AI proactively asked itself *"is there a runbook for this?"* and used `central-scope-audit`, producing a comprehensive VSG-anchored report. Mist's AI freelanced and produced a custom audit instead. Same query, different model habit.

The diagnosis: the per-skill trigger phrases in `INSTRUCTIONS.md` Section 8 required platform-prefixed framings like *"audit Mist scope / config"*. Generic phrasings — *"do a config audit"*, *"check the configuration"*, *"does this site follow best practices"*, *"possible improvements"* — didn't match the table, so the AI fell back to manual tool sequencing.

### What changed

Three additions to Section 8 (*"Always check Skills FIRST..."*):

1. **Universal trigger words at the top of the section** — any of these MUST cause `skills_list()` first, regardless of whether a platform name appears in the query: *audit*, *health check*, *review*, *baseline*, *snapshot*, *drift*, *best practices*, *compliance*, *follow standards*, *check the configuration*, *check the config*, *check this site*, *possible improvements*, *what could be better*, *what should I change*, *is this configured correctly*, *is this OK*, *is this set up right*, *how does this look*. Platform context is taken from the conversation (the site/org being discussed, the platform already touched in-session).
2. **Per-skill row triggers expanded** for `mist-scope-audit` and `central-scope-audit` — added *"do a config audit"*, *"audit this site"*, *"check the config"*, *"check the Wi-Fi configuration"* (Mist), *"does this site follow best practices"*, *"is this configured correctly"*, *"possible improvements"*, *"review this site"*.
3. **Explicit "don't reinvent" rule** at the bottom of the section — if a skill matches the request and the platform context, the AI MUST `skills_load()` and follow the runbook rather than synthesizing a custom audit. The runbook output is what the user expects (consistent shape, severity ordering, anchored on vendor docs); a freelanced audit produces inconsistent results across sessions.

### What's NOT changing

- Skill bodies are unchanged. The `central-scope-audit` output the user shared is rich and well-shaped (active-alert correlation, VSG-section citations, scope-tree placement audit, persona-assignment gaps, naming-hygiene smells, severity-ordered next actions). `mist-scope-audit`'s 590-line runbook is comparably designed. The skills are good; the trigger reliability was the bug.
- No code changes, no test changes (test count unchanged at 732). `tests/unit/test_skill_tool_references.py` validates that every tool reference in `INSTRUCTIONS.md` resolves — the new wording introduces no new tool references, only narrative phrasing.

## [2.3.1.3] - 2026-04-30

**Extends the PII tokenization ruleset to cover Aruba Central response shapes. Three new identifier fields (`user_name`, `updated_by`, `created_by`), one one-line normalization fix that lets hyphen-cased keys (`wpa-passphrase`, `shared-secret`) match the same ruleset entries as their snake_case equivalents. No protocol or API change; existing Mist tokenization is unaffected.**

### What changed

1. **`user_name`, `updated_by`, `created_by` added to `TOKENIZED_IDENTIFIER_FIELDS`** as `USER`. Central exposes these in audit log entries (`updated_by` = the operator who modified config, `created_by` = the operator who created it) and uses `user_name` as the snake_case variant alongside Mist-style `username`.

2. **Hyphen normalization in `classify_field`** — field names are now lowercased AND have hyphens collapsed to underscores at lookup time (`field_name.lower().replace("-", "_")`). This makes the ruleset match Central's hyphenated keys without enumerating every variant. Concretely: `wpa-passphrase` now matches `wpa_passphrase` and tokenizes as `PSK`; `shared-secret` matches `shared_secret` and tokenizes as `RADSEC`.

### Deliberately NOT added

Per the v2.3.1.3 design discussion:

- **`device_group_name`** — Central's group hierarchy. Organizational structure, not customer-identifying.
- **`scope_name`** — Central's scope tree. Same reasoning.

Both pass through as cleartext. Audit utility benefits from operators being able to read which group / scope was affected.

### Tests

- 732 passing (was 721) — net +11: 7 new field-classification tests covering `user_name`, `updated_by`, `created_by`, `device_group_name` passthrough, `scope_name` passthrough, hyphenated `wpa-passphrase`, hyphenated `shared-secret`; 4 new Central-shaped fixture tests covering WLAN profile walk, audit-log user-field tokenization, server-group RADIUS-secret tokenization, and a round-trip through hyphenated PSK fields.

### What this unlocks

Running an audit on Central with `ENABLE_PII_TOKENIZATION=true` should now produce useful output:

- WLAN profile PSKs (`wpa-passphrase` inside `personal-security`) tokenize as `[[PSK:...]]`
- Server group RADIUS shared secrets (`shared-secret`) tokenize as `[[RADSEC:...]]`
- Audit log `updated_by` / `created_by` / `user_name` tokenize as `[[USER:...]]`
- Device names / AP names (via the device-context heuristic) tokenize as `[[HOSTNAME:...]]`
- Scope names, device group names, IPs, MACs, SSIDs, platform UUIDs all pass through cleartext

### Cross-platform note

GreenLake, ClearPass, Apstra, Axis still need their own ruleset extensions. Each likely follows the same shape (small set of platform-specific identifier fields + verify the existing secret rules cover their auth fields). One platform per follow-up patch.

## [2.3.1.2] - 2026-04-29

**Closes four leaks / false positives surfaced by the first real Mist audit run with v2.3.1.1. Email addresses now tokenize anywhere they appear (not just in `email` fields), AWS-signed URLs are tokenized whole as APITOKEN credentials, the wxtag → HOSTNAME false positive is fixed, and IP addresses pass through as cleartext everywhere. No protocol or API change; existing PSK / RADSEC / cert / hostname tokenization continues unchanged.**

### What changed

1. **Universal email scan.** The email regex is now applied to every string value the walker encounters (in addition to the existing free-text scan), not just to fields named `email` and not just to `description` / `notes` / etc. **Why:** Mist's MPSK pattern uses the user's email as the PSK display name (`name: "user@corp.com"`), which slipped through both the field-name path (the field was `name`, not `email`) and the free-text path (PSK objects don't have a `description` field). Substring substitution preserves surrounding text.

2. **AWS-signed URL credential detection.** Any string value containing `X-Amz-Security-Token`, `X-Amz-Credential`, or `X-Amz-Signature` (case-insensitive) is recognized as a temporary AWS credential and the **whole value** is tokenized as `APITOKEN`. **Why:** Mist embeds AWS Signature v4 pre-signed URLs in fields like `portal_template_url` so operators can preview captive-portal pages directly from S3. These URLs include short-lived credentials that the AI doesn't need; partial-redaction would leave the access key visible, so we tokenize the entire URL.

3. **Tightened bare-`name` HOSTNAME heuristic.** The "treat `name` as a hostname when the parent looks like a device" rule now requires **2+** matches against `DEVICE_CONTEXT_HINTS` (was 1). **Why:** wxtag objects have a single `mac` field for "match by client MAC" rules. The old "any single hint" check incorrectly treated wxtags as devices and tokenized their display names (`"DHCP/DNS Ports"`, `"Internet"`, etc.) as `[[HOSTNAME:...]]`, making the AI unable to read what each rule meant. Real device responses (mac + model + serial + type) still trigger HOSTNAME.

4. **IP addresses pass through everywhere.** Removed `TokenKind.IP`, the `PUBLIC_IP_ALLOWLIST` and `PUBLIC_IP_ALLOWLIST_RANGES` constants, the IPv4 / IPv6 regexes, and all IP-related helpers from the walker. Internal RFC1918 subnets, public WAN IPs, and CIDR ranges all pass through verbatim. **Why:** internal subnet topology is generally known to anyone on-network, and CIDR / route analysis is a core audit task. Tokenizing IPs broke cidr-sanity workflows (the audit AI couldn't check `172.168.0.0/12` vs the correct `172.16.0.0/12`). The privacy gain wasn't worth the audit-utility loss.

### What's still tokenized

Unchanged: PSKs, RADIUS / RadSec / SNMP / admin / VPN secrets, certificates, private keys, API tokens (now also catching AWS-signed URLs), hostnames, FQDNs, device names, AP names, site names, org names, VLAN / subnet names, usernames, **emails (now everywhere)**, real names, phone numbers, hardware serials, IMEI / IMSI / ICCID.

### What now passes through

In addition to v2.3.1.1's carve-outs (MACs, SSIDs, platform UUIDs, geographic data, public DNS), v2.3.1.2 adds:

- **All IPv4 / IPv6 addresses** — internal RFC1918, public WAN, link-local, multicast, anything.
- **CIDR ranges** — preserved for route / subnet analysis.

### Tests

- 721 passing (was 715) — net +6: removed two IP-tokenization tests, added eight covering email-in-arbitrary-fields, plain-URL passthrough, AWS-signed URL detection, wxtag-shape false-positive prevention, single-hint passthrough, two-hint trigger, all-IPs passthrough, and an updated Mist fixture exercising the email-as-PSK-name and portal_template_url cases together.

## [2.3.1.1] - 2026-04-29

**Refines the v2.3.1.0 PII tokenization ruleset based on first-audit feedback. Stops tokenizing values that were either (a) already opaque (platform UUIDs), (b) publicly observable (SSIDs, broadcast in beacons), or (c) typically findable on the company's website (street addresses, geographic data). The original v2.3.1.0 ruleset over-tokenized — making audit output noisier without adding meaningful privacy. No protocol or API change; existing PSK/RADSEC/cert/hostname/email tokenization continues unchanged.**

### What changed

Removed from `TOKENIZED_IDENTIFIER_FIELDS` in `redaction/rules.py`:

- **SSIDs / ESSIDs.** `ssid`, `essid`. Broadcast in beacon frames — observable to anyone in radio range. Same threat-model logic that already applied to BSSIDs and client MACs.
- **All platform UUID `*_id` fields.** `org_id`, `msp_id`, `site_id`, `siteid`, `device_id`, `ap_id`, `switch_id`, `gateway_id`, `mxedge_id`, `wlan_id`, `wxlan_id`, `wxtag_id`, `wxtunnel_id`, `wxrule_id`, `wxlan_tunnel_id`, `client_id`, `mobile_id`, `mac_id`, `template_id`, `assignment_id`, `policy_id`, `psk_id`, `tenant_id`, `workspace_id`, `subscription_id`. Mist's API uniformly returns these as random UUIDs which are already opaque; replacing them with our own UUIDs adds no privacy and makes AI audit narration harder to follow.
- **Geographic fields.** `address`, `street`, `city`, `state`, `zip`, `postal_code`, `country`, `room`, `floor`, `building`, `latitude`, `longitude`. Business addresses are typically public on the company's website. Removing `state` also closes a latent false-positive vector — the field name commonly means device/connection state in network APIs and was at risk of being tokenized in those contexts too.

Removed from `TokenKind` (dead code after the field-mapping changes):

- `SSID`, `ORG`, `SITE`, `DEVICE`, `AP`, `SWITCH`, `GATEWAY`, `WLAN`, `TEMPLATE`, `POLICY`, `TENANT`, `WORKSPACE`, `SUBSCRIPTION`, `CLIENT`, `GEO`

### Still tokenized (unchanged)

- **Tier 1 secrets** — every WPA/SAE/WEP key, RADIUS/RadSec/SNMP/admin/VPN/API token, certificate, private key, keytab.
- **Hostnames + operator-assigned names** — `device_name`, `ap_name`, `hostname`, `fqdn`, `site_name`, `org_name`, `vlan_name`, `subnet_name`. These reveal customer infrastructure naming patterns even though they may show up in DNS.
- **User-identifying** — `username`, `user`, `login`, `email`, `first_name`, `last_name`, `full_name`, `display_name`, `phone`, `phone_number`, `mobile`.
- **Hardware identifiers** — `serial`, `serial_number`, `sn`, `imei`, `imsi`, `iccid`. Tie back to purchase records.
- **Internal IPs** — RFC1918 and other non-public IPs in the free-text scan. Public DNS / loopback / RFC documentation IPs preserved by the existing allowlist.
- **MAC normalization** — always-on, all formats canonicalized to `aa:bb:cc:dd:ee:ff`.

### Why

The first real audit run (after v2.3.1.0 shipped) flagged two issues:

1. **AI confusion with opaque-on-opaque substitution.** When the AI ingests `org_id: "[[ORG:550e8400-...]]"` instead of `org_id: "eec497e7-f27a-..."`, it has the same information content (an opaque identifier) but pays the context-window cost twice and has to reason about a token shape it didn't see in training. Net negative.
2. **SSIDs are publicly broadcast.** The principle we agreed on for MACs ("don't tokenize what's observable in radio space") wasn't applied consistently — SSIDs slipped into the original ruleset. Same logic applies.

### Tests

- 715 passing (was 712) — net +3: removed two tests for retired enum behavior, added five new tests asserting passthrough for SSID, every platform `*_id` field, geographic fields, and confirming hostnames are still tokenized.

### Cross-platform note (deferred to next minor)

Mist's IDs are uniformly UUIDs, so dropping `*_id` mappings is correct for Mist. Central, GreenLake, ClearPass, and Apstra IDs may not all be UUIDs (GreenLake `subscription_id` shapes vary, Apstra has slug-style IDs in places, ClearPass uses integer IDs). When those rulesets are added in the next minor, we'll add either a UUID-shape check or per-platform mappings — to be decided then.

## [2.3.1.0] - 2026-04-29

**Adds session-stable PII tokenization for tool responses + always-on MAC normalization. Sensitive fields (PSKs, RADIUS secrets, certificates) and customer-identifying values (platform UUIDs, hostnames, emails, geographic data) get replaced with `[[KIND:uuid]]` tokens before reaching the AI; the AI can pass tokens back into write tools and the inbound side substitutes plaintext before the API call. The mapping is held in process memory keyed by `Mcp-Session-Id` and never persisted to disk. Mist ruleset only this release; Central / GreenLake / ClearPass / Apstra / Axis follow in the next minor.**

### What's new

- **`src/hpe_networking_mcp/redaction/` package** — five modules covering rules, MAC normalization, the per-session token store, the bidirectional tokenizer, and the recursive walker. ~700 LOC of pure logic, no platform dependencies.
- **`src/hpe_networking_mcp/middleware/pii_tokenization.py`** — bidirectional FastMCP middleware. Inbound: walks `arguments` for `[[KIND:uuid]]` tokens and substitutes plaintext from the session keymap before the call hits the platform. Unknown tokens (model referenced something from a stale session) cause the call to fail with a JSON-RPC error rather than passing literal bracket text downstream. Outbound: walks `ToolResult.structured_content` and JSON-shaped text content blocks, applying MAC normalization (always-on) and PII tokenization (when enabled).
- **MAC normalization is default-on regardless of the tokenization toggle** — every MAC address in tool responses gets rewritten to canonical `aa:bb:cc:dd:ee:ff` form (lowercase, colon-separated). Mist's API can return MACs in four different formats across different endpoints; normalizing to one consistent shape lets the AI correlate `aa:bb:cc:dd:ee:ff` to itself across an audit. Per the design discussion, MACs are NOT tokenized — they're observable in radio space (BSSID broadcast, client probes), so privacy tokenization adds cost without security gain.
- **PII tokenization is opt-in via `ENABLE_PII_TOKENIZATION=true`** for this minor; default flips to on in the next minor after the Mist ruleset has been validated against real audits.
- **Tier 1 secrets (always tokenized when enabled):** `psk`, `passphrase`, `wpa3_psk`, `sae_password`, `ppsk`, `wep_key`; `shared_secret`, `radius_secret`, `radsec_secret`, `eap_password`; `community`, `auth_password`, `priv_password` (SNMP); `admin_password`, `enable_secret`, `cli_password`; `pre_shared_key`, `ipsec_psk`, `vpn_psk`; `api_token`, `client_secret`, `bearer_token`, `access_token`, `refresh_token`, `webhook_secret`; `private_key`, `cert`, `certificate`, `client_cert`, `server_cert`, `ca_cert`, `chain`, `pkcs12`, `pem`, `kerberos_keytab`. Plus content-fingerprint detection on `-----BEGIN ` PEM blocks anywhere.
- **Tier 2 identifiers:** platform UUIDs (`org_id`, `site_id`, `device_id`, `wlan_id`, `client_id`, etc.); operator-assigned names (`device_name`, `ap_name`, `hostname`, `fqdn`, `ssid`, `vlan_name`); user-identifying fields (`username`, `email`, `first_name`, `last_name`, `phone`); hardware identifiers (`serial`, `imei`, `imsi`, `iccid`); geographic data (`latitude`, `longitude`, `address`, `street`, `city`, `state`, `zip`, `country`). IPs in `description`/`notes`/`comment`/`remarks`/`details` free-text fields are scanned and tokenized in place (substring substitution, surrounding text preserved). Public DNS / loopback / RFC documentation IPs are exempt from tokenization.
- **Token format: `[[KIND:550e8400-e29b-41d4-a716-446655440000]]`** — UUID4 with dashes, lowercase. 128 bits of entropy means collision probability is effectively zero across any session size. Same plaintext gets the same token within a session ("same value, same token" — enables sync, migration, and rotation workflows that depend on equality).
- **Storage:** in-memory `TokenStore` on the FastMCP instance. Per-session `SessionKeymap` keyed by `Mcp-Session-Id`; `get_or_create()` allocates lazily. Soft cap of 10K tokens per session (configurable via `PII_MAX_TOKENS_PER_SESSION`); cap-hit logs a warning and falls through with plaintext rather than erroring out the call. **No disk persistence** — keymap dies with the process. Saved chat references to `[[KIND:uuid]]` from a dead session become unresolvable on resurrection; the operator re-runs the workflow that produced them.
- **Audit logging:** every tokenization and detokenization event logs to stderr (`docker compose logs`) with tool name, parameter name, kind, token ID, truncated value-hash (SHA-256, first 16 hex), session prefix. **Plaintext is never logged.** The value-hash lets an operator confirm "the same value tokenized to the same token" without revealing the value.

### Why it matters

Pre-2.3.1.0: a Mist scope-audit response contains every WLAN's PSK, RADIUS shared secrets, admin passwords, and operator-assigned names in cleartext. The AI ingests all of it as conversation context and the AI provider sees it on every prompt. The `aos-migration-readiness` skill explicitly called this out as a known PoC limitation.

Post-2.3.1.0: with `ENABLE_PII_TOKENIZATION=true`, the AI sees `[[PSK:550e8400-...]]` instead of the literal PSK, can pass that token back into `mist_create_wlan` to clone the WLAN to another site, and the middleware substitutes the real PSK at the inbound boundary. WLAN sync, AOS 8 → AOS 10 migration, and mass PSK rotation all keep working because tokenization is round-trippable. The AI's conversation context window never holds a literal secret.

Compose well with code mode (`MCP_TOOL_MODE=code`): in the sandbox, the AI can call `secrets.token_urlsafe(20)` to generate a fresh PSK, pass it to `mist_create_wlan`, and only see the tokenized form in the `return` value — the literal PSK lives in the sandbox's local scope and never enters the AI's context window.

### Configuration

| Env var | Default | Description |
|---|---|---|
| `ENABLE_PII_TOKENIZATION` | `false` | Master toggle. Off this release; flips to `true` in the next minor after ruleset validation. |
| `PII_MAX_TOKENS_PER_SESSION` | `10000` | Soft cap on keymap size per session. Cap-hit returns plaintext rather than erroring. |

### Tests

- 712 passing (was 653) — 59 new tests covering MAC normalization, field classification, credential-shape heuristics, token-store lifecycle, tokenizer round-trip, walker recursion, free-text scan, public-IP allowlist, and a realistic Mist WLAN fixture.

### Known limitations

- **Mist ruleset only.** Central / GreenLake / ClearPass / Apstra / Axis tools work but their platform-specific field names (e.g. Central's `radius_servers[*].secret` shape, ClearPass's certificate model) aren't fully covered. Next minor.
- **Paste-into-chat is still exposed.** A user typing `psk=Welcome2024` into the AI prompt has the literal PSK in their context immediately — outside our threat model. We tokenize the API echo back when the response comes through, so subsequent references stop leaking, but the originating turn does. Documented behavior.
- **No reveal mechanism.** There is no tool to retrieve the plaintext for a token. Operators see the audit log if they need to confirm what a token references; the platform UI is the source of truth for the actual values.

## [2.3.0.9] - 2026-04-29

**Closes the MCP Streamable HTTP spec's Origin-validation requirement (DNS rebinding defense) and tightens the host port publish to loopback by default. Both changes are transport-layer hardening; no tools or APIs are affected.**

### Security

- **`Origin` header validation** — new ASGI middleware (`src/hpe_networking_mcp/middleware/origin_validation.py`) rejects HTTP requests whose `Origin` header is set to anything outside the allowlist with `403 Forbidden`. Browsers always send `Origin` and cannot lie about it (it is a forbidden header in the Fetch spec), so a server-side allowlist is sufficient defense against DNS rebinding attacks. Non-browser clients (supergateway, curl, native MCP clients) typically don't send `Origin` and are passed through unchanged. The MCP spec (2025-06-18 §Streamable HTTP) requires this check.
- **Host port publish now binds loopback by default** — `docker-compose.yml` changes `ports: "${MCP_PORT:-8000}:8000"` → `"127.0.0.1:${MCP_PORT:-8000}:8000"`. Previously the published port answered on every host interface (`0.0.0.0:8000`, `[::]:8000`), which meant any host on the same LAN could reach the unauthenticated MCP endpoint. Loopback-only publishing eliminates that exposure. The container's internal bind (`MCP_HOST=0.0.0.0`) is unchanged — that controls binding *inside* the container's network namespace, which is correct for Docker's port-forwarder to reach the app.

### What's new

- **New env var: `ALLOWED_ORIGINS`** (comma-separated). Defaults to `http://localhost:<MCP_PORT>,http://127.0.0.1:<MCP_PORT>` — covers Claude Desktop / supergateway / Claude Code / curl from the host. Set `ALLOWED_ORIGINS=*` to disable the check entirely (use only when fronted by an auth proxy that already validates origins).
- Origin allowlist is logged at startup so misconfiguration is visible. A `*` wildcard is logged as a `WARNING`.

### Why it matters

Before this release: a malicious page in any browser tab on the operator's machine could DNS-rebind its own domain to `127.0.0.1` and POST to `/mcp`, driving the entire fleet (Mist, Central, GreenLake, ClearPass, Apstra, Axis) without ever crossing the supergateway/Claude Desktop trust boundary. With `0.0.0.0:8000` exposure also active, the same attack worked from any host on the LAN.

After this release: the published port answers only on loopback (eliminates LAN exposure), and the Origin allowlist blocks browser-driven cross-origin POSTs (eliminates DNS rebinding from tabs on the same machine). Defense in depth — both controls are applied.

### How to verify after upgrade

```bash
docker compose up -d --force-recreate
docker ps --format '{{.Names}}\t{{.Ports}}' | grep hpe-networking
# Expect: 127.0.0.1:8000->8000/tcp   (no [::]:8000 line)

# Allowed (no Origin) → 200/SSE
curl -i -X POST http://127.0.0.1:8000/mcp \
  -H 'Accept: application/json, text/event-stream' \
  -H 'Content-Type: application/json' -d '{}'

# Disallowed Origin → 403
curl -i -X POST http://127.0.0.1:8000/mcp \
  -H 'Origin: http://evil.example' \
  -H 'Accept: application/json, text/event-stream' \
  -H 'Content-Type: application/json' -d '{}'
```

### Tests

- 653 passing — no test changes; behavior unit-testable end-to-end via curl above.

## [2.4.0.1] - 2026-04-29

### Fixed
- **AOS8 differentiator tools (DIFF-01..09) production response-contract bug.** `differentiators.py` `_show()` and `_object()` previously returned a raw `httpx.Response` object instead of parsed JSON, causing all 9 DIFF tools (`aos8_get_md_hierarchy`, `aos8_get_effective_config`, `aos8_get_pending_changes`, `aos8_get_rf_neighbors`, `aos8_get_cluster_state`, `aos8_get_air_monitors`, `aos8_get_ap_wired_ports`, `aos8_get_ipsec_tunnels`, `aos8_get_md_health_check`) to fail in production. Refactored to use canonical `_helpers.run_show()` / `get_object()`. Test mocks updated to match the real `AOS8Client.request()` contract.
- **Code-mode `execute_description`** now lists `aos8_` as a callable platform prefix. The sandboxed `execute()` LLM was previously told only 6 platform prefixes were dispatchable, causing `Unknown tool: aos8_*` failures despite the tools being registered. Added regression test `test_server_code_mode.py` that asserts every platform prefix appears in the literal.

### Documentation
- README.md, docs/TOOLS.md tool counts corrected from 38 → **47 AOS8 tools** (26 read + 12 write + 9 differentiators). The 9 differentiator tools were added in Phase 7 but the user-facing strings were not refreshed at the time. Note for [2.4.0.0]: tool count was incorrectly stated as 38; the actual shipped count was 47.
- docs/TOOLS.md: new `### Differentiators (9)` subsection lists all 9 AOS8-unique read tools with descriptions.
- `.planning/phases/04-differentiator-tools/04-VERIFICATION.md` added — formally documents that Phase 4 was administratively merged into Phase 7 (plans 07-01/07-02/07-03) and corrected by Phase 8 (plan 08-01).
- REQUIREMENTS.md DIFF-01..09 traceability now reads "Complete".

### Tests
- New `tests/unit/test_server_code_mode.py` (2 tests) — guards code-mode `execute_description` literal against future platform-prefix drift.
- Total unit tests: 766 (was 764).

## [2.4.0.0] - 2026-04-28

### Added
- **Aruba OS 8 / Mobility Conductor platform module** (seventh platform).
  - 38 tools across 6 categories: 8 health/inventory, 4 client, 3 alert/audit, 4 WLAN/config, 7 troubleshooting, 12 write
  - 9 guided prompts: aos8_triage_client, aos8_triage_ap, aos8_health_check, aos8_audit_change, aos8_rf_analysis, aos8_wlan_review, aos8_client_flood, aos8_compare_md_config, aos8_pre_change_check
  - Token-reusing UIDARUBA session client with single-flight 401 refresh, asyncio.Lock-serialized token rotation, lazy login (deferred to first tool call), and explicit aclose() that logs out on shutdown
  - Write tools gated behind `ENABLE_AOS8_WRITE_TOOLS` (default false); every write returns `requires_write_memory_for`
  - `aos8_write_memory` is the only path to persist staged config — never auto-called
  - SSL verification enabled by default; opt-out emits a startup WARNING
  - Five Docker secrets: `aos8_host`, `aos8_username`, `aos8_password`, `aos8_port` (default 4343), `aos8_verify_ssl`
- New repo-root **INSTRUCTIONS.md** — operator-facing documentation covering AOS8 config_path semantics, write_memory contract, show_command passthrough, Conductor-vs-standalone behavior, and the guided-prompt index. Distinct from the in-package AI-facing src/hpe_networking_mcp/INSTRUCTIONS.md.
- AOS8 tool reference section in **docs/TOOLS.md**.
- AOS8 row in README.md capability table; AOS8 secrets reference section; AOS8 added to platform auto-disable example.

### Changed
- README.md tool counts and architecture diagram updated to include AOS8 (38 + 9 prompts).
- Bumped version to 2.4.0.0 (minor — additive platform).

### Tests
- 11+ new unit tests in tests/unit/test_aos8_prompts.py covering prompt registration and non-empty return contract for all 9 PROMPT-01..09 prompts.
- Phase-5 baseline of 737 tests remains green; total now 767+ tests passing.

## [2.3.0.8] - 2026-04-28

**Fixes a content gap in `central-scope-audit`: when an alias has a placeholder default value (e.g. `1.1.1.1`, RFC-5737 documentation block) at Global, the audit was flagging it as REGRESSION without first checking whether the alias is *overridden* at consuming scopes (Site Collection / Site / Device Group / per-device via `Save as local profile`). In Aruba Central's two-layer alias model, a placeholder at the definition scope is the canonical pattern — what matters is whether each consumer (Static Routes, profiles, ACLs, etc.) has an override at scope-or-below. Caught in the wild when the audit flagged four `Default Gateway -*` aliases all defaulting to `1.1.1.1` at Global as REGRESSION without confirming whether the consuming static routes had per-site / per-device overrides.**

### What changed

Three updates to `skills/central-scope-audit.md`:

1. **Step 7 (Aliases)** — added a new *"Placeholder default values — MUST walk the hierarchy before flagging"* sub-section spelling out:
   - Common placeholder sentinels: `1.1.1.1`, `0.0.0.0`, `255.255.255.255`, RFC-5737 documentation blocks (`192.0.2.x`, `198.51.100.x`, `203.0.113.x`), and obvious tokens like names containing `placeholder` / `default` / `template`.
   - **Mandatory hierarchy lookup before assigning severity**: identify every consumer (Static Routes are the canonical case; also role ACLs, net-services, server-host fields, AP Uplink, any `*-Address` / `*-NextHop` field), then for each consuming scope use `central_get_scope_resources` + `central_get_effective_config(include_details=true)` walking Global → Collections → Sites → Device Groups → Devices to resolve the alias's effective value.
   - **Severity follows coverage, not the placeholder itself**: REGRESSION only when a consuming scope has *no* override at-or-below (the device installs the literal placeholder); DRIFT when the consumer is itself unused / disabled; INFO when every consumer is overridden (canonical pattern).
   - Reporting requirement: name the alias, the placeholder, the consuming profile + scope, and the override state for each consumer.
2. **Step 11 (Routing & Network Services)** — added a per-profile check telling the audit that any static route referencing a `Default Gateway -*` / `Next Hop` / `MGMT Default Gateway` alias MUST follow Step 7's hierarchy-lookup procedure before deciding severity, and added a corresponding REGRESSION entry that explicitly notes *"Do not flag REGRESSION on the placeholder alone — it's REGRESSION specifically because no consumer overrode the placeholder."*
3. **Output rollup** — added the new REGRESSION entry (placeholder unoverridden at consuming scope) with a structured one-finding template, and a paired INFO entry (placeholder with full override coverage) so the report can list canonical-pattern aliases without operator confusion.

### Why it mattered

The two-layer alias model exists *precisely* so a single alias name like `Default Gateway - SW` can resolve to a different next-hop on every site. A blanket *"alias defaults to 1.1.1.1 = REGRESSION"* finding either generates false positives (canonical pattern flagged as broken) or — if the auditor stops there — masks the actual question: *which consumers, if any, would push the literal placeholder to real devices*. The fix mandates the hierarchy walk before assigning severity, and gives the audit explicit language to use when a placeholder is fully covered (INFO) vs partially covered (DRIFT) vs uncovered at a real consumer (REGRESSION).

### Tests

- 653 passing, 0 failing — `test_skill_tool_references.py` still resolves every platform-prefixed tool reference (8/8 parametrized cases pass).

## [2.3.0.7] - 2026-04-28

**Fixes a content bug in `mist-scope-audit`: the skill conflated 802.1X reauthentication interval with RADIUS accounting interim-update interval. The Mist Wired guide §2660-§2663 recommendation of 6-12 hours (21600-43200s) applies to *reauthentication* (`reauth_interval` on dot1x-enabled port profiles), not to `acct_interim_interval` (RADIUS accounting interim updates) — but the audit was citing it against the latter. Caught in the wild when a user's audit flagged `acct_interim_interval: 60` with the §2662 reauth recommendation.**

### What changed

- **`mist-scope-audit.md`** — three locations corrected:
  - Per-port-profile structural-checks table: row renamed from "RADIUS interim-update" to "802.1X reauthentication interval (`reauth_interval` on dot1x-enabled port profiles)" with the full §2660-§2663 quote and an explicit *"Do NOT confuse this with `acct_interim_interval`"* warning.
  - Drift findings list: same correction with note that `acct_interim_interval` should be flagged as INFO (not DRIFT) without citing §2662 since the Mist Wired guide doesn't give a recommended value for it.
  - Output-formatting rollup: counter renamed to "802.1X `reauth_interval` outside 6-12 hour range".

### Why it mattered

Reauthentication interval (how often a 802.1X client must re-prove identity to RADIUS) and accounting interim interval (how often accounting status updates are sent to the accounting server) are two different fields with different purposes. The Mist Wired guide §1803 describes accounting interim updates as a frequency setting without prescribing a value; §2660-§2663 describes reauthentication with the 6-12 hour recommendation. Conflating them would either generate false-positive drift findings (flagging perfectly fine accounting intervals) or, worse, push operators to set accounting intervals to multi-hour values they shouldn't.

### Tests

- 653 passing, 0 failing — no test changes (skill body is content; reference test still validates every platform-prefixed tool name resolves).

## [2.3.0.6] - 2026-04-28

**Adds `aos-migration-readiness` skill — VSG-anchored AOS 6 / AOS 8 / Instant AP → AOS 10 migration readiness audit (PoC). Operator pastes a fixed bundle of CLI command outputs from the source platform into chat; the audit parses the bundle, runs Central-side API checks, applies ~50 granular VSG-anchored rules across source-platform × target-mode combinations, and emits a GO / BLOCKED / PARTIAL verdict with cutover sequencing and rollback validation.**

### What's new

- **`aos-migration-readiness` skill** (~44K chars) — covers all three legacy source platforms (AOS 6 Mobility Conductor, AOS 8 Mobility Conductor + Controller, Instant AP Virtual Controller cluster) and all three AOS 10 SSID-forwarding modes (Tunnel, Bridge, Mixed). Anchored on the **Aruba Campus Migrate VSG** with section-number citations on every finding.
- **6-stage audit pipeline:**
  - **Stage 0**: 7-question operator interview (source platform, AirWave state, target mode, scope, cluster type, L3 Mobility, target HA mode)
  - **Stage 1**: Paste-driven data collection — fixed CLI command tables per source platform (16 commands for AOS 8 per VSG §1671-§1873; adapted command sets for AOS 6 and IAP) collected as one all-at-once bundle
  - **Stage 2**: Per-artifact parse instructions per source platform
  - **Stage 3**: ~50 VSG-anchored readiness rules — Universal (U1-U11), AOS 6/8-specific (C1-C10), IAP-specific (I1-I10), per-target-mode rules (T1-T7 Tunnel, B1-B11 Bridge, M1-M5 Mixed)
  - **Stage 4**: Central API checks (A1-A13) — workspace state, scope-tree readiness, license inventory, firmware-recommendation delta, NAD/server-group/named-VLAN parity
  - **Stage 5**: Cutover sequencing + rollback per VSG §2352-§2576 (8-phase: AP redistribute → upgrade Controller 1 → AP convert test → upgrade remaining APs → upgrade Controller 2 → rollback validation)
- **GO / BLOCKED / PARTIAL verdict** with structured report: source-platform inventory, target-side state, AOS 10 hierarchy mapping suggestion, REGRESSION / DRIFT / INFO findings (each citing VSG section), cutover sequence, recommended next actions, PoC caveats
- **Decision matrix** maps ~30 conditions to verdicts so the AI doesn't have to invent ranking rules at runtime
- **PoC scope explicitly noted:** PII / customer-data tokenization is *not* implemented — paste-into-chat workflow has known PII exposure since the AI client ingests configs before relaying. Production migration cutovers should follow the customer's standard change-management process

### Documentation

- **`INSTRUCTIONS.md`** — added a new query→skill row to the rule #8 table covering migration-readiness query shapes (*"AOS 8 → AOS 10 migration readiness"*, *"AOS 6 → AOS 10 readiness"*, *"Instant AP → AOS 10 readiness"*, *"are we ready for AOS 10"*)

### Tests

- 653 passing (was 652) — `test_skill_tool_references.py` picks up the new skill via parametrization and validates every platform-prefixed tool reference in the body resolves to a real tool in the catalog

### Skill count

- **7 bundled skills** (was 6): `infrastructure-health-check`, `change-pre-check`, `change-post-check`, `wlan-sync-validation`, `central-scope-audit`, `mist-scope-audit`, **`aos-migration-readiness`** ← new

## [2.3.0.5] - 2026-04-28

**Adds two comprehensive scope-aware configuration-audit skills, one per platform — anchored on Aruba's Validated Solution Guides (Central) and Mist's best-practices documentation, covering ~25 / ~20 profile categories respectively with explicit "should be" judgments against vendor-recommended scope.**

### What's new

Two symmetric audit skills, both read-only:

- **`central-scope-audit`** — Walks Central's Configuration Manager hierarchy (Global → Site Collections → Sites → Device Groups → Devices) across **~25 profile categories** (Authentication Servers, Server Groups, AAA Authentication, Roles, Role ACLs, Role GPIDs, Policies, Policy Groups, Network Services, Network Groups, Object Groups, Aliases, WLAN profiles, Named VLANs, User Administration, System Administration, Switch System, Source Interface, Port Profile, Interface Profile, Device Identity, Static Routing, DHCP Snooping, AP Uplink, etc.). Each finding is judged against the **VSG-recommended scope** with explicit *"VSG recommends X, found at Y"* drift markers.
- **`mist-scope-audit`** — Walks Mist's org → site-group → site → device-profile → device hierarchy across **~20 categories** (WLAN templates, per-WLAN settings, bare site-level WLANs, RF templates, site templates, site groups, site-level overrides, device profiles, firmware auto-upgrade, PSK/MPSK strategy). Anchored on Mist best-practices: *"template everything, override nothing unless you have to."*

### VSG / best-practices anchoring

The Central audit cites VSG section + line numbers for each scope recommendation:

| Profile category | VSG-recommended scope | VSG anchor |
|---|---|---|
| Authentication Server | **Global** | Campus Deploy §10703 |
| Authentication Server Group | **Global** | Campus Deploy §10564 |
| Device Identity | **Global** | Campus Deploy §11753 |
| AAA Authentication | **Site** | Campus Deploy §11799 |
| Switch System / VLAN / Static Routing / DHCP Snooping | **Site** | Campus Deploy §11659, §11420, §12415, §11179 |
| Port Profile / Interface Profile | **Site** per device-function | Campus Deploy §11948-12061 |
| Roles / Policies | **Site** typically | Campus Deploy §9337, Policy Design §1184 |

Plus VSG-derived rules:
- *"A role is not pushed to a device unless referenced by a scoped policy"* (Policy Design)
- *"Keep the number of roles as small as possible"* (Policy Design)

The Mist audit anchors on the local best-practices doc with citations like *"per §2.4: assign templates to site groups whenever possible"* and *"per §4.5: enable auto-upgrade at the org level with maintenance window"*.

### What each audit checks (structured per skill)

**Central** (12 audit checks, ~25 profile categories):
0. Reachability + scope-tree snapshot (committed + effective view)
1. Authentication Servers — should be Global
2. Authentication Server Groups — should be Global
3. AAA Authentication profiles — typically Site
4. Roles + Role ACLs + Role GPIDs — orphan detection, role-count sanity, role→policy linkage
5. Policies + Policy Groups — orphan detection, broken role references
6. Network Services / Groups / Object Groups — orphan detection
7. Aliases — orphan / duplicate / hardcoded-instead detection
8. WLAN Profiles + Named VLANs — bare-local-scope WLANs (primary drift), VLAN naming consistency
9. System profiles (User Admin / System Admin / Switch System / Source Interface)
10. Interface profiles (Port / Interface / Device Identity / AP Uplink)
11. Routing & Network Services (Static Routing / DHCP Snooping / AP Uplink)
12. Cross-cutting — bare local configs, peer-collection diff, assignment-density heuristics

**Mist** (11 audit checks, ~20 categories):
0. Reachability + org_id
1. WLAN templates + assignment scope (org / site-group / site)
2. Per-WLAN settings (band steering, 11r, mDNS scope, ARP filter, broadcast limit, VLAN ≠ 1, PSK type, RADIUS via template variables)
3. Bare site-level WLANs (primary drift source)
4. Org-level WLAN reconciliation (every WLAN should have a template_id)
5. RF templates + assignment scope + per-band channel-width / TX-power rules
6. Site templates (consistent new-site baseline)
7. Site groups + site membership
8. Site-level overrides (only timezone / country / local gateway IP / unique VLANs are valid; everything else is drift)
9. Device profiles + device-level config (device-level = REGRESSION)
10. Firmware auto-upgrade policy (maintenance window, pilot site group, compliance tracking)
11. PSK / MPSK strategy (Cloud PSK preferred, expiration on guest PSKs)

### Output format — structured + repeatable

Both skills emit reports with the same `REGRESSION → DRIFT → INFO` severity order. Each section heading must be present even if "0 findings" — operators can eyeball today's audit against last week's. Profile-category summary table at the top gives a one-glance health view.

### INSTRUCTIONS.md rule #8 query→skill table extended

Two new rows mapping audit-shaped queries to the new skills:

| User query shape | Likely skill |
|---|---|
| *"audit Central scope / config"*, *"where are my Central WLAN profiles assigned"*, *"is my Central config drifting"* | `central-scope-audit` |
| *"audit Mist scope / config"*, *"where are my Mist WLAN templates assigned"*, *"find bare site-level WLANs"* | `mist-scope-audit` |

### Skill design — read-only audits, no fixes

Both skills are explicitly **read-only**. They identify issues; they don't correct them. Fixes still go through `mist_change_org_configuration_objects` / `central_manage_*` with elicitation gating. Keeping the audit pure-read means the operator can run it freely (no write-tool flag, no elicitation prompt, no chance of accidentally touching production) and decide which findings to act on.

### Tests (650 → 652)

Two new parametrized cases in `test_skill_tool_references.py::TestSkillToolReferences` (one per new skill) — automatic from the existing pytest parametrization. The regression test caught a regex artifact (`central_manage_*` in prose) which was added to `_GLOBAL_ALLOWLIST` alongside the existing meta-tool / historical mentions. Central audit references **23 distinct Central tools**; Mist audit references **8 Mist tools** (Mist gets fewer because `mist_get_configuration_objects` covers many object types via the `object_type` parameter — `wlantemplates`, `rftemplates`, `sitegroups`, `deviceprofiles`, `psks`, etc.).

### Live-tested

- Container restarts with **6 skills registered** (was 4)
- `skills_load("central-scope-audit")` returns **16,027-char body** at top level in code mode
- `skills_load("mist-scope-audit")` returns **16,049-char body** at top level in code mode
- Both new skills appear with correct platform tags in `skills_list(platform="central")` / `skills_list(platform="mist")` filters

### Reference material (kept locally, gitignored)

The Central audit is anchored on the four Aruba Validated Solution Guides
(Campus Design, Campus Deploy, Policy Design, Policy Deploy) — vendor-licensed
PDFs kept in `docs/central/vsg/` for skill authoring; **not redistributed via
the repo** (added to `.gitignore`). Same pattern for `docs/mist/vsg/` which
holds the Mist best-practices reference.

### Maximum-granularity rewrite (in-PR iteration)

After the def-vs-value correction, user requested *"the more granular we
are with Central and Mist config audit the better the results. Add as
much detail as possible to both."* Both skills were rewritten again
against all source material:

- **Central audit: 21K → 38K chars** (15 audit steps, 60 REGRESSION
  signals, 44 DRIFT signals). Now includes per-setting checks within
  each category (specific VSG-recommended values, not just scope).
  Examples: VLAN 1 as production = REGRESSION, MTU < 9198 on CX/AOS-10
  = REGRESSION (per VSG §970), Loop Protect Re-Enable Time = 0 =
  REGRESSION (per VSG §3298), DHCP snooping/ARP inspection not trust
  on LAG = REGRESSION (per VSG §3495), default captive-portal cert
  = REGRESSION (per VSG §364), server group with only 1 RADIUS server
  = REGRESSION (per VSG §5006), missing canonical roles (ARUBA-AP /
  BLACKHOLE / REJECT-AUTH / CRITICAL-AUTH) = REGRESSION when 802.1X
  / APs are deployed.
- **Mist audit: 18K → 33K chars** (15 audit steps, 44 REGRESSION
  signals, 63 DRIFT signals). Three NEW source documents incorporated:
  Mist Wired Assurance Configuration Guide, Mist Wireless Assurance
  Configuration Guide, Juniper AI-Driven Wired & Wireless Network
  Deployment Guide. New audit categories: switch configuration
  templates (org/site/device hierarchy), site variables (Mist's
  alias-equivalent — same definition-vs-value pattern), port profiles
  (static + dynamic + DPC rules), AP-port best practices, virtual
  chassis. New per-setting checks: 11r on non-Enterprise SSID =
  REGRESSION (won't function), WEP/WPA1 = REGRESSION, port security
  on AP ports = REGRESSION (Mist Wired §4016), MAC-based dynamic
  match on 802.1X port = REGRESSION (Mist Wired §3001), CLI-managed
  switches = REGRESSION (Mist Wired §3597-§3598), 2.4 GHz channel
  width > 20 MHz = REGRESSION, 2.4 GHz channels other than {1,6,11}
  = REGRESSION.

### Definition-vs-value pattern (Central) — corrected mid-PR after user catch

Initial draft of the audit conflated two distinct device-level patterns the
VSG documents in Campus Deploy §11220-§11377 and §10620-§10625:

1. **Auto-imported device-level profiles** (drift): when a switch is
   onboarded, Central auto-creates device-level profiles for STP / System
   Administration / etc. with naming convention `profile-<device serial>` and
   `Inherits From: Self`. These BLOCK inheritance from higher-scope profiles.
   **VSG explicitly directs operators to delete these.** The audit now
   detects them as REGRESSION findings.
2. **"Save as local profile" — intentional device-level overrides** (canonical):
   the operator's explicit override mechanism. Used for alias VALUES per
   device (the SC-SW-IP pattern — the alias DEFINITION lives at Site/Collection/Global,
   each switch's IP VALUE is assigned via `Save as local profile`), per-VLAN
   switch-param tweaks, etc. These are **VSG-canonical, not drift.** The
   audit lists them at INFO level for periodic review — never flags.

The audit's cross-cutting rule (Step 12) now uses three buckets at device
scope: REGRESSION (auto-imported `profile-<serial>` or bare local config) /
INFO (sanctioned `Save as local profile` overrides + per-device alias VALUE
assignments) / RESEARCH (effective vs committed inconsistencies).

Same softening applied to Mist Step 9: per-device hostname / IP / name are
inherent identification (NOT drift); only device-level config that *competes*
with template / site-group / org config (radio overrides without justification,
device-level WLAN, firmware pin diverging from auto-upgrade) is REGRESSION.

## [2.3.0.4] - 2026-04-28

**Fixes the AI generalizing Mist-only WLAN best practices onto Central, plus broadens the Mist WLAN-template assignment scope guidance.**

### What went wrong

In-the-wild signal: a user asked their AI for a Central config / scope audit and got back:

> *"WLANs should live in templates assigned to site groups (Global or Site-Collection scope), never at site or device level."*

That sentence is wrong on multiple counts:
- *"templates"* — Central does **not** have WLAN templates. That's Mist terminology. Central uses WLAN profiles.
- *"never at site or device level"* — too restrictive even for Mist (templates can target a single site) and Central (WLAN profiles can be assigned at site or device-group scope).
- *"Global or Site-Collection scope"* — Central terminology mashed onto Mist guidance.

Two compounding root causes:

1. **Mist guidance overreach.** INSTRUCTIONS.md `Mist Best Practices > WLANs` said *"assign templates to site groups"* — implying site groups were the *only* valid template-assignment target. The actual rule is **org-wide / site groups / specific sites — never device level**. The same too-narrow language was repeated in `platforms/mist/tools/guardrails.py:_check_site_wlan_creation`'s warning text.

2. **Missing Aruba Central Best Practices section.** When asked for a Central audit, the AI had no Central-specific guidance to anchor on. It generalized Mist's *"push config high, use templates"* rule onto Central, picked up Central terminology along the way (*"Site-Collection scope"*), and produced a hybrid that's wrong on both platforms.

### What's fixed

**Mist guidance broadened** (matches the actual platform model):

- `INSTRUCTIONS.md > Mist Best Practices > WLANs` — *"assign each template at the appropriate scope: org-wide, to a site group, or to specific sites. Never at the device level."* The rule against bare site-level WLANs (i.e. WLANs created without a template) stays — that's still correct shorthand for *"WLANs without a template should never be created"*.
- `INSTRUCTIONS.md > Site Groups` — site groups are now described as one of three valid assignment targets, not the only valid one. Site-level template assignment is explicitly endorsed for site-specific cases.
- `INSTRUCTIONS.md > Site Provisioning` — broadened the same way.
- `platforms/mist/tools/guardrails.py:_check_site_wlan_creation` — warning text now lists all three valid scopes (org / site group / specific sites) and explicitly notes "never at device level" instead of implying site groups are the only target.

**Aruba Central Best Practices section added** (mirrors Mist structure but uses correct Central terminology):

- Configuration Hierarchy: *Global → Site Collections → Sites → Device Groups → Devices*
- WLAN Profiles: assign at *Global*, *site collection*, *site*, or *device group* (Mist has no device-group equivalent — this scope is Central-only)
- **Local overrides — use local profiles, not direct configs**: explicitly explains that bare local-scope configs lead to drift and orphan when the parent profile changes. The correct override pattern is a **local profile** assigned at the lower scope, which falls back to inherited config cleanly when deleted.
- Naming: keep Mist site groups and Central site collections in sync by name so cross-platform sync workflows pair up.

**Mist ↔ Central terminology table** added under the Central section:

| Concept | Mist | Central |
|---|---|---|
| Reusable config bundle for SSIDs | WLAN **template** | WLAN **profile** |
| Top of the hierarchy | **Org** | **Global** |
| Group of sites | **Site group** | **Site collection** |
| Individual site | **Site** | **Site** |
| Group of devices | *(no equivalent)* | **Device group** |
| Override at lower scope | Bare site-level config (avoid) | Local profile (correct) / bare local config (avoid) |

The table is preceded by an explicit *"do NOT generalize a rule from one platform onto the other"* directive — meant to defang the exact AI behavior that produced the original bad answer.

### Tests (649 → 650)

One new guardrail-message-content test in `tests/unit/test_guardrails.py::TestSiteWlanCreation::test_site_wlan_create_warning_lists_all_valid_scopes`:

- Asserts the warning mentions org-wide assignment
- Asserts the warning mentions site-group assignment
- Asserts the warning mentions site-level assignment (not just site groups)
- Asserts the warning calls out "never at device level" explicitly

Catches a regression where someone narrows the scope guidance back to site-groups-only.

### Live-tested

Verified via direct probe of the running server's `instructions` field over the MCP `initialize` response that the new sections (`Aruba Central Best Practices`, `Local Overrides`, `Mist ↔ Central terminology`, `Device Groups`, `Configuration Manager`) are all loaded and reach the AI client at session start.

## [2.3.0.3] - 2026-04-28

**Fixes a top-level visibility bug that hid `skills_list` and `skills_load` in code mode since v2.3.0.0, and strengthens INSTRUCTIONS.md rule #8 to make the AI proactively check skills first.**

### What was broken

In **code mode**, the actual MCP-exposed surface was 4 tools (`tags`, `search`, `get_schema`, `execute`) — `skills_list` and `skills_load` were nowhere to be found in `tools/list`. The AI had no top-level signal that skills existed, so it never reached for them on questions like *"how's my infrastructure in Central?"*.

Confirmed via direct wire-protocol probe (`tools/list` over the streaming-HTTP MCP endpoint) — not just inferred. Verified the regression had been present since v2.3.0.0 by reading git history; nothing in server.py or skills/ ever passed skills as discovery tools.

### Why it happened

`skills_list` / `skills_load` were registered via `@mcp.tool` before `_register_code_mode(mcp)` ran. CodeMode's `transform_tools()` then *replaces* the visible catalog with `[*discovery_tools, execute]` — it doesn't merge with the existing catalog, it substitutes. So skills were callable from inside `execute()` via `await call_tool("skills_list", {})` (their `@mcp.tool` registration kept them in the backend catalog), but invisible to the AI at the top level. I tested skills via `execute()` during v2.3.0.0 development and didn't notice they weren't visible at the top.

### The fix

`skills/_engine.py` now exposes two discovery-tool factories matching `CodeMode.discovery_tools`'s signature (same shape as fastmcp's `GetTags` / `Search` / `GetSchemas`):

- `SkillsListDiscoveryTool(registry)` — produces a `skills_list` Tool
- `SkillsLoadDiscoveryTool(registry)` — produces a `skills_load` Tool

`server.py:_register_code_mode` builds a `SkillRegistry` once and hands the factories into `discovery_tools` alongside the standard `GetTags`/`Search`/`GetSchemas`. In code mode the exposed surface is now **6 tools**: `tags`, `search`, `get_schema`, `skills_list`, `skills_load`, `execute`.

`server.py:create_server` skips the `@mcp.tool` registration path (`_register_skills(mcp)`) when `tool_mode == "code"` to avoid registering them twice. Dynamic and static modes still use `register(mcp)` — `@mcp.tool` works correctly there because no transform replaces the catalog.

### Trade-off accepted

Skills are now **discovery-only** in code mode — same shape as `tags`/`search`/`get_schema`. They're callable at the top level but NOT from inside `execute()` (the sandbox's `call_tool` only resolves backend platform tools). That matches their semantic role: planning tools, not dispatch tools. The `execute_description` is updated to call this out explicitly, alongside the existing note about `tags`/`search`/`get_schema` not being callable inside `execute()`. If any LLM tries `await call_tool("skills_list", {})` from inside the sandbox, the existing `SandboxErrorCatchMiddleware` (v2.2.0.4) will surface `Sandbox error: Unknown tool: skills_list` as a string so the LLM can self-correct.

### INSTRUCTIONS.md rule #8 strengthened

The previous rule said *"call `skills_list` first when the user asks for a known runbook"* — too passive, required the AI to recognize the runbook shape. New rule:

> *"**Always check Skills FIRST for multi-step / cross-platform questions.** Even when the user names a specific platform (e.g. *"how's my infrastructure in Central?"*), call `skills_list()` BEFORE reaching for per-platform tools..."*

Plus a query→skill table giving concrete pattern → skill mappings:

| User query shape | Likely skill |
|---|---|
| *"how's my infrastructure?"*, *"is everything healthy?"*, *"how is health in &lt;platform&gt;?"* | `infrastructure-health-check` |
| *"about to push a change"*, *"give me a baseline"* | `change-pre-check` |
| *"the change is done — verify"*, *"post-change check"* | `change-post-check` |
| *"are WLANs in sync?"*, *"WLAN drift audit"* | `wlan-sync-validation` |

### Tests (644 → 649)

- `TestDiscoveryToolFactories` × 5 cases — factories produce Tools with the right name + working body, support filter args, accept custom names, return clean errors on no-match
- `TestCodeModeAggregatorGating` extended — asserts `skills.register` is called in dynamic/static and NOT called in code mode (with a comment pointing at this CHANGELOG entry so future contributors don't "fix" the assertion the wrong way)

Plus an end-to-end live verification via the wire-protocol `tools/list`:
- code mode → 6 top-level tools (`tags`, `search`, `get_schema`, `skills_list`, `skills_load`, `execute`)
- dynamic mode → 109 visible (per-platform meta-tools + cross-platform statics + skills_list + skills_load)

### Live-tested

- `tools/call` for `skills_list` at the top level in code mode → returns all 4 bundled skills
- `tools/call` for `skills_load` at the top level in code mode → returns infrastructure-health-check body
- Dynamic-mode wire probe confirms skills_list / skills_load still appear there

## [2.3.0.2] - 2026-04-27

**Fixes 12 wrong tool-name references in the bundled skills, tightens output templates so the AI doesn't improvise inconsistent formatting, and adds a regression test that catches this whole class of bug at CI time.**

### What went wrong

In-the-wild signal from running `infrastructure-health-check` and `change-pre-check`: skills were referencing tool names that don't exist (e.g. `clearpass_get_recent_audit_log`, `mist_get_org_wlans`, `apstra_get_blueprint_revisions`). The AI got "tool not found" errors via the discovery tools and worked around them — sometimes by skipping the step entirely (silent gap in output), sometimes by improvising a substitute. Output was incomplete and inconsistent across runs.

Root cause: the v2.3.0.0 skills were authored without verifying every referenced name against the actual tool catalog. The output formatting templates were also loose enough that the AI was filling in freeform sections.

### Skill fixes (12 wrong names corrected)

| Wrong name | Correct name | Files |
|---|---|---|
| `clearpass_get_recent_audit_log` | `clearpass_get_system_events` | infrastructure-health-check, change-pre-check, change-post-check |
| `clearpass_get_active_sessions` | `clearpass_get_sessions` | change-pre-check |
| `clearpass_get_enforcement_policy` | `clearpass_get_enforcement_policies(policy_id=...)` | change-pre-check |
| `mist_get_org_wlans` / `mist_get_site_wlans` | `mist_get_wlans()` (accepts `org_id` or `site_id`) | wlan-sync-validation |
| `mist_get_wlan` (singular) | `mist_get_configuration_objects(object_type="wlans", object_id=...)` | change-pre-check |
| `mist_get_device` | `mist_search_device` (org inventory) or `mist_get_ap_details` / `mist_get_switch_details` (specific device) | change-pre-check |
| `mist_get_device_port_config` | `mist_get_switch_details(device_id=...)` (port config is part of switch detail) | change-pre-check |
| `central_get_site_wlans` | `central_get_wlans(site_id=...)` | wlan-sync-validation |
| `central_get_wlan` (singular) | `central_get_wlans()` | change-pre-check |
| `central_get_switch_port` | `central_get_switch_details(serial=...)` | change-pre-check |
| `apstra_get_blueprint_revisions` | `apstra_get_blueprints(blueprint_id=...)` (record `version`) + `apstra_get_diff_status` (uncommitted changes) | change-pre-check |

### Tightened output templates

Each skill's "Output formatting" section now leads with a directive: *"Use the EXACT structure below. Every section heading must be present even if its content is..."* This stops the AI from skipping sections, adding freeform "Notable" sections that aren't in the template, or rewriting headings between runs. The output structure itself is unchanged — same headings, same fields — just enforced.

`infrastructure-health-check` also gained `apstra_get_anomalies`, `axis_get_connectors`, and `axis_get_status` to the `tools:` frontmatter (they were referenced in the body but missing from the metadata list) and clarified the Axis step to spell out the runtime-status field names (`cpuStatus`, `memoryStatus`, `networkStatus`, `diskSpaceStatus`).

### Regression test (`tests/unit/test_skill_tool_references.py`)

Builds a server in static mode (every tool registered) plus the dynamic-mode meta-tool name patterns. Walks each `skills/*.md` body and `INSTRUCTIONS.md`, extracts every platform-prefixed identifier via regex, asserts each appears in the canonical catalog or in a small `_GLOBAL_ALLOWLIST` for known historical mentions (e.g. *"`apstra_health` was removed in v2.0"*) and regex artifacts (e.g. incomplete patterns like `mist_change_org` inside *"`mist_change_org_*` family"* prose).

5 new test cases:
- Per-skill parametrized check: 4 skills × 1 test = 4 cases
- INSTRUCTIONS.md check: 1 case

Future skill authors get a CI failure if they reference a non-existent tool, with a clear remediation message ("either fix the name to match a real tool, or — if the reference is intentional — add it to `_GLOBAL_ALLOWLIST`").

### What we didn't change

- INSTRUCTIONS.md had **0 actual broken references**. The regex caught 12 hits but every single one was either historical prose ("X was removed in v2.0", surfaced for context) or a regex artifact (incomplete pattern like `mist_change_org` inside `mist_change_org_*` family-mention prose). All were added to the allowlist with comments rather than rewritten.
- `@mcp.prompt(...)` bodies and human-facing docs (README, docs/TOOLS.md) — same regex sweep but no real bugs found, so no changes there. The regression test currently covers skills + INSTRUCTIONS.md; expand if more authoring surfaces emerge.

### Tests (639 → 644)

5 new regression tests; existing 639 still pass.

## [2.3.0.1] - 2026-04-27

**Adds the `change-post-check` skill (partner to `change-pre-check`) and documents two pydantic-monty sandbox limits the LLM was discovering at runtime.**

### `change-post-check` skill

The `change-pre-check` skill captures a baseline before a planned change; this new skill re-pulls the same data afterward and diffs against the baseline to produce a verdict:

| Verdict | Trigger |
|---|---|
| `CLEAN` | Reachability unchanged + 0 new alarms + config diff matches plan + metric deltas <5% |
| `IMPACT-OBSERVED` | At least one IMPACT signal but no REGRESSION (new minor alarm, 5-15% client delta, etc.) |
| `REGRESSION` | Platform unreachable / planned change didn't land / unplanned config drift / >15% delta |

**Baseline-discovery design:** the skill checks conversation context first for the `## Pre-change baseline — ...` block and only asks the user to paste it back if it's not in scope. Operators working in the same chat as the pre-check don't need to copy-paste anything.

`change-pre-check.md` gains a "After the change — run the post-check" section so the AI tells the operator about the partner skill on its way out, with the in-context-vs-paste-back distinction called out explicitly.

### Documented sandbox limits

In-the-wild observation: the AI ran `change-pre-check` in code mode and tripped on two pydantic-monty sandbox limits, recovering each time via the `SandboxErrorCatchMiddleware` (v2.2.0.4) error string but burning a turn each:

1. **`asyncio.gather()`** fails with `TypeError: 'list' object is not an iterator` — the sandbox treats the awaitable list as a non-iterator.
2. **`datetime.now()`** is blocked as an OS-access call (`NotImplementedError`).

The `SandboxErrorCatchMiddleware` did its job (the LLM saw the actual error and self-corrected), but the LLM shouldn't have to *discover* these limits per-session. So:

- The custom `execute_description` (`server.py:_register_code_mode`) gains a "Known sandbox limits" line listing both — `asyncio.gather()` unavailable, OS-access functions blocked, and the practical workaround (sequential awaits, ISO strings as parameters or hardcoded literals).
- `docs/TOOLS.md`'s "Sandbox limits" section gains the same content.

### Tests

No new tests — the skill is content; the bundled-skills sanity test added in v2.3.0.0 auto-picks up the new file. 639 tests still pass.

### Bumped to a patch version

Adding a skill is purely additive content (no schema change, no new tool surface). Same versioning logic as adding a new middleware. Patch.

## [2.3.0.0] - 2026-04-27

**Adds a Skills system: markdown-defined multi-step procedures discoverable via two MCP tools.** Closes #189.

### Background

Three places already exist where multi-step network operations procedures could live, each with downsides:

1. **`INSTRUCTIONS.md`** — long, embedded "if user asks X, do Y then Z" guidance. Consumes baseline context every turn; AIs don't reliably follow it as the number of patterns grows.
2. **`@mcp.prompt` primitives** — work, but require a code edit + image rebuild to add or change a procedure.
3. **Cross-platform aggregator tools** (`site_health_check`, `manage_wlan_profile`, `site_rf_check`) — Python code that does N calls and returns one merged answer. Great when the procedure is stable; awful when it needs frequent tuning. Not registered in code mode (premise: LLM should compose).

None give us a procedure surface that is (a) discoverable on demand, (b) authored in markdown, (c) updatable without a code release.

### What's new

A **skill** is a markdown file with YAML frontmatter sitting in `src/hpe_networking_mcp/skills/`. The frontmatter carries metadata (name / title / description / platforms / tags / tools); the body is the runbook the AI follows step-by-step. The new engine indexes all `*.md` files in that directory at startup and exposes:

- **`skills_list(platform=..., tag=...)`** — returns metadata only (cheap browse)
- **`skills_load(name)`** — returns the full markdown body, with case-insensitive substring fallback if no exact match is found

Skills are **always-visible top-level tools** in every `MCP_TOOL_MODE` (dynamic, code, static) — they're an entry point, not an implementation detail.

### Why skills work in code mode (where aggregators don't)

| | Aggregators (`site_health_check`, etc.) | Skills (`change-pre-check`, etc.) |
|---|---|---|
| What it is | Python code that does 5 calls and returns one merged answer | Markdown that says "do these 5 calls and merge them this way" |
| Who composes the answer | The server, in Python | The LLM itself |
| In code mode? | Not registered (premise: LLM should compose) | Registered (it's a guide for that composition) |

The skill is the *textual* version of an aggregator. In code mode the LLM reads the runbook then writes a single `execute()` block calling `await call_tool("mist_search_alarms", ...)`, `call_tool("central_get_alerts", ...)`, etc. — exactly what code mode is built for.

### Seed skills (3 + TEMPLATE)

- **`infrastructure-health-check`** — cross-platform daily-standup style overview. `health()` → per-platform alarms/alerts → admin activity → formatted summary.
- **`change-pre-check`** — pre-change baseline snapshot. Confirms scope, runs reachability, captures pre-existing alarms, recent admin activity, current config, active impact metrics, and emits a structured snapshot the operator pastes into their change ticket.
- **`wlan-sync-validation`** — Mist ↔ Central WLAN drift detection. Pulls both catalogs, classifies each SSID as in-sync / Mist-only / Central-only / drift, lists field-level diffs (with the inverted `hide_ssid`/`broadcast_ssid` quirk called out).

Plus `TEMPLATE.md` for users who want to author their own (placeholder name `my-skill-name` so it's filtered out of the registry by the filename-stem check).

### Engine details

- **Loader** — `Path.glob("*.md")` at startup, sorted, parsed via PyYAML (already a transitive dep — no new dependency added).
- **Validation** — frontmatter must be a YAML mapping with at minimum `name` (must match filename stem), `title`, `description`. Bad frontmatter is logged and skipped; the server boots with the rest of the catalog rather than crashing on a malformed file.
- **Lookup** — case-insensitive exact match first, then case-insensitive substring fallback; multi-match returns the candidate list so the AI can disambiguate.
- **Reserved filenames** — `TEMPLATE.md` is excluded from the registry by name.

### Tool surface impact

| Mode | Before | After | Net |
|---|---|---|---|
| Dynamic | 22 always-visible tools | 24 (+`skills_list` + `skills_load`) | +2 |
| Code | 4 (`tags`/`search`/`get_schema`/`execute`) + `health` | 6 (+`skills_list` + `skills_load`) | +2 |
| Static | 305+ tools | 307+ | +2 |

Token-budget impact: ~+80 tokens baseline per session for the two new tool definitions. Skills are pulled on demand — the runbook bodies don't load until the AI calls `skills_load`.

### INSTRUCTIONS.md update

New rule #8 added: "Use Skills for multi-step procedures. When the user asks for something that's a known runbook — *infra health check*, *pre-change baseline*, *WLAN sync audit* — call `skills_list()` first to see whether a skill matches, then `skills_load(name=...)` to fetch the markdown runbook."

### Tests (612 → 639)

Twenty-seven new tests in `tests/unit/test_skills.py`:

- Frontmatter parsing — valid + every malformed shape we want to skip (no frontmatter, unterminated, bad YAML, list-not-mapping, missing required fields, name/filename mismatch)
- String-coerced-to-list field shape (`platforms: mist` works as well as `platforms: [mist]`)
- Filter behavior — string vs list, AND across fields, OR within a field
- Lookup — exact match, case-insensitive, substring fallback (unique + multi-match), empty/whitespace input, exact-beats-substring tiebreaker
- Bundled-skills sanity — the three seed skills load cleanly, bodies are nonempty, `TEMPLATE.md` is excluded

### Bumped to a minor version

This is a new feature surface (two new always-visible tools + an authored content library) and is purely additive — no existing tool changes behavior. Semver MINOR. Reserved MAJOR for things that would actually break existing clients (e.g. dropping dynamic mode, renaming platform prefixes, changing `*_invoke_tool` signatures).

### Out of scope (deferred)

- **User-authored skills via volume mount** — bundled-only for v1. Add later if there's demand.
- **Trust marker** (`trust: built-in` vs `trust: user`) — only meaningful once user-mounting exists; YAGNI today.
- **Skill chaining** (one skill referencing another) — keep v1 simple.
- **Skills with elicitation hooks** ("ask user before step 5") — deferred.

## [2.2.0.5] - 2026-04-27

**Adds `RetryMiddleware` for transparent retry of transient API failures (5xx server errors and 429 rate-limit responses).** Closes #133 (5xx retry) and #134 (429 + Retry-After).

### Background

Network APIs occasionally return transient failures — server overload (5xx), rate limiting (429), brief network blips. Without retry handling, every transient failure surfaces to the AI as a tool-level error, forcing the user to either re-ask or watch the model decide whether to retry. Both make the experience worse than necessary.

This middleware catches the two failure shapes our platforms produce:

1. **Response-dict pattern** (Mist / Central / ClearPass) — older clients return a dict shaped like `{"status_code": 503, ...}` (or `"code"` / `"status"` depending on platform).
2. **Exception pattern** (GreenLake / Apstra / Axis) — newer httpx-based clients raise `httpx.HTTPStatusError` whose `.response.status_code` indicates the failure.

### Behavior

| Status | Reads | Writes | Notes |
|---|---|---|---|
| 5xx (500/502/503/504) | retried | NOT retried | Writes may not be idempotent — better to surface and let the user decide |
| 429 | retried | retried | Always safe — server is asking us to slow down, not telling us the request was processed |
| 4xx (other) | not retried | not retried | Client error — retrying won't help |
| 2xx success | returned | returned | No retry path |

Read/write classification reads the FastMCP tool's `tags` at call time — any tag matching `*_write` or `*_write_delete` marks the tool as a write. Cross-platform convention; works for all six platforms.

### Configuration

| Env var | Default | Purpose |
|---|---|---|
| `RETRY_MAX_ATTEMPTS` | `3` | Max attempts including the first; set to `1` to disable |
| `RETRY_INITIAL_DELAY` | `1.0` | Initial backoff (seconds); doubles on each retry |
| `RETRY_MAX_DELAY` | `60.0` | Cap on a single retry sleep + on Retry-After header values |

### Retry-After header support

For 429 responses, the middleware honors a `Retry-After` header when present — both via the response-dict shape (looks for `Retry-After` / `retry_after` / `retry-after` keys) and via `httpx.HTTPStatusError.response.headers["Retry-After"]`. Only the integer-seconds form is honored; HTTP-date form falls back to exponential backoff. The Retry-After value is capped at `RETRY_MAX_DELAY` to prevent a runaway "retry in 24 hours" lock-up.

### Middleware chain (post-#208, post-#133/#134)

Outermost → innermost as of v2.2.0.5:

1. `NullStripMiddleware` — drop nulls before validation
2. `ValidationCatchMiddleware` — Pydantic ValidationError → string `ToolResult`
3. `SandboxErrorCatchMiddleware` — code-mode MontyError → string `ToolResult`
4. `ElicitationMiddleware` — write-tool confirmation gate
5. `RetryMiddleware` — innermost, so re-tries don't re-prompt elicitation

### Tests (598 → 612)

Fourteen new tests in `tests/unit/test_middleware.py::TestRetryMiddleware`:

- 5xx retry on reads, no-retry on writes
- 429 retry on both reads and writes
- 4xx and 2xx no-retry passthrough
- max-attempts cap respected
- Retry-After header honored (response-dict + httpx exception forms)
- Retry-After capped at `RETRY_MAX_DELAY`
- `max_attempts=1` disables retry entirely
- Central `code` field pattern + ClearPass `status` field pattern
- httpx 429 with Retry-After header
- Unknown exceptions (non-httpx, non-status) propagate unchanged

## [2.2.0.4] - 2026-04-27

**Unmasks code-mode sandbox errors and tells the LLM upfront which tools `call_tool` can dispatch to.** Closes #208.

### Background

When the LLM in code mode wrote `await call_tool("search", ...)` (or `get_schema` / `tags`) inside `execute()`, the sandbox raised `MontyRuntimeError: Unknown tool: search` because those discovery tools live at the outer MCP surface — they're not in the backend catalog `call_tool` resolves against. FastMCP's masking layer (`mask_error_details=True`, set for security) caught the runtime error and re-raised it as a generic `ToolError("Error calling tool 'execute'")`, leaving the LLM with nothing to self-correct from. Both gemma-4eb (LM Studio) and Claude were observed making this exact mistake in the wild.

### What's fixed

Two complementary changes:

1. **Custom `execute_description`** in [`server.py:_register_code_mode`](src/hpe_networking_mcp/server.py) — the default fastmcp string only said "`call_tool` is in scope" without telling the LLM what's *callable*. The new description names the platform-tool prefixes (`mist_*`, `central_*`, `greenlake_*`, `clearpass_*`, `apstra_*`, `axis_*`, plus `health`) and explicitly notes that `tags` / `search` / `get_schema` are NOT callable from inside `execute()` — they're for planning, before the code block.

2. **`SandboxErrorCatchMiddleware`** at [`src/hpe_networking_mcp/middleware/sandbox_error_catch.py`](src/hpe_networking_mcp/middleware/sandbox_error_catch.py) — sits next to `ValidationCatchMiddleware` in the chain. Catches the masked `ToolError` for the `execute` tool, inspects `__cause__`, and if it's a `MontyError` (any subclass: runtime / syntax / typing) returns a string `ToolResult` like:

```
Sandbox error: Exception: Unknown tool: search
```

The LLM can branch on this the same way it does on tool-level error strings from Axis / ClearPass.

### Why catch `ToolError` instead of `MontyError` directly

FastMCP's `server.call_tool` (line 1240) already special-cases `ValidationError` to re-raise unchanged — that's why `ValidationCatchMiddleware` (#206) catches the original type. Other exceptions fall through to `mask_error_details` and become `ToolError(...) from cause`. The `MontyError` is preserved as `__cause__`, so we unwrap there.

### Live-tested

Three scenarios verified against the running container in code mode:

| Test | Before | After |
|---|---|---|
| `await call_tool("search", ...)` from inside `execute()` | `Error calling tool 'execute'` | `Sandbox error: Exception: Unknown tool: search` |
| `return "hello"` from `execute()` | (no regression) | (no regression) |
| `await call_tool("health", {})` from inside `execute()` | (no regression) | (no regression) |

### Tests (592 → 598)

Six new tests in `tests/unit/test_middleware.py::TestSandboxErrorCatchMiddleware`:

- Catches the wrapped sandbox runtime error → returns ToolResult with the readable string
- Does NOT intercept `ToolError` on tools other than `execute`
- Does NOT intercept `ToolError` whose `__cause__` is something other than `MontyError`
- Does NOT intercept bare exceptions on `execute` (only the FastMCP-wrapped shape)
- Successful execute calls pass through unchanged
- The wrapped error's `str()` form is preserved verbatim in the returned text

Helper `_make_monty_error` runs real failing pydantic-monty code to capture a genuine `MontyError` instance, since the three concrete subclasses (`MontyRuntimeError` / `MontySyntaxError` / `MontyTypingError`) are Rust-backed and `@final` and cannot be constructed from Python.

## [2.2.0.3] - 2026-04-27

**Adds `ValidationCatchMiddleware` to convert Pydantic `ValidationError` into a structured tool-result string instead of letting it propagate as `MontyRuntimeError` and crash `execute()` in code mode.** Closes #206 (the FastMCP-layer follow-up to #202).

### Background

#202 (closed by PR #203) addressed tool-internal raises by converting them to error string returns. That fix didn't help **Pydantic validation errors**, which fire BEFORE the tool function runs — during FastMCP's parameter coercion step. Same crash symptom, but the fix lives at the FastMCP middleware layer rather than in tool code.

In code mode, the originally-crashing case looked like:

```
call_tool("mist_search_alarms", {"severity": "major"})
→ MontyRuntimeError: ValueError: 1 validation error for severity
→ Crashes execute(); try/except inside the sandbox CANNOT recover
```

After this fix:

```
"Error: validation failed for tool 'mist_search_alarms':
  - severity: Input should be 'critical', 'info' or 'warn' (got: 'major')"
→ AI receives a string, branches on it, retries with a valid value
```

### Implementation

New `ValidationCatchMiddleware` at [`src/hpe_networking_mcp/middleware/validation_catch.py`](src/hpe_networking_mcp/middleware/validation_catch.py) — ~50 LOC. Subclasses FastMCP's `Middleware` base class, hooks `on_call_tool`, wraps `await call_next(context)` in `try/except pydantic.ValidationError`, returns a `ToolResult(content=<readable string>)` on catch.

Registered between `NullStripMiddleware` and `ElicitationMiddleware` in the chain. Placement matches the FastMCP `ErrorHandlingMiddleware` precedent.

The error string lists each failing field with Pydantic's own "Input should be X, Y, or Z" formatting — actionable, lets the AI immediately retry with a valid value.

### What this protects against

- Apstra's 19 Pydantic field validators in `apstra/models.py` — the originally-flagged out-of-scope concern from #202
- Mist's enum-typed params (`AlarmSeverity`, `AlarmGroup`, `Action_type`, etc.) when given an invalid value
- Any tool with a `Field(...)` validator that rejects input
- Any UUID-typed param with malformed input
- **Any future Pydantic validator added by any platform** — protected for free

### Behavior change scope

| Mode | Today | After |
|---|---|---|
| **Code** | `MontyRuntimeError` crashes `execute()` (the bug) | Clean string return — bug fixed |
| **Static** | AI sees `McpError(-32602, "Invalid params: ...")` | AI sees string `"Error: validation failed..."` — message is more readable |
| **Dynamic** | `<platform>_invoke_tool` wraps and returns a string | Unchanged — middleware sees only the meta-tool's flexible-typed params (no ValidationError fires there); the underlying tool's validation is caught inside `_invoke_tool`'s body |

Verified by running the full dynamic-mode unit test suite (`test_*_dynamic_mode.py` × 6 platforms + `test_code_mode.py` + `test_middleware.py`) — all 100 tests pass with the middleware enabled.

### Live-tested

Three scenarios verified against the running container in code mode:

| Test | Result |
|---|---|
| Invalid enum: `severity="major"` | Returns string with "Input should be 'critical', 'info' or 'warn'" |
| Valid call: `mist_get_self(action_type="account_info")` | Returns dict with privileges (no regression) |
| Multi-field error: missing `site_id` + bogus `object_id` | Both errors listed in one readable string |

### Tests (587 → 592)

Five new tests in `tests/unit/test_middleware.py::TestValidationCatchMiddleware`:

- Catches ValidationError → returns ToolResult with a readable string
- Passes through valid calls unchanged
- Does NOT catch other exceptions (RuntimeError, etc.) — those propagate to existing handlers
- Multi-field validation errors list every failing field
- Tool name appears in the error string (so the AI knows which call failed)

Plus the existing `TestNullStripMiddleware` suite continues to pass — middleware ordering is unchanged for that one.

### Bundled in this release

This release also rolls forward the docs-only tool description cleanup from PR #205 (closes #183), which was on main as "Unreleased — docs only" pending the next versioned release. That content:

- **`mist_get_site_health`** description now leads with "Organization-wide health AGGREGATE — NOT a per-site breakdown" and redirects to `mist_get_org_or_site_info(info_type='site')` for the per-site-list case
- **`clearpass_get_guest_users`** docstring's first line now leads with the dual-mode behavior so summary views surface both modes immediately
- **`mist_get_org_or_site_info`** description lists the actual returned fields and cross-references the right tools for site health and per-site stats
- **`mist_get_org_sle`** description replaced confusing "all/worst sites" phrasing with explicit org-wide-vs-per-site scope language
- **`mist_get_constants`** reframed as a discovery tool with specific use cases; includes the "`insight_metrics` is NOT the same set as SLE metrics" warning

## [2.2.0.2] - 2026-04-27

**Mist tool schema tightening — alarm severity/group enum corrections + SLE metric description fixes that point at the right discovery tools.** Closes #186.

### Bug context

Issue #186 cited a live failure where the AI called `mist_get_site_sle(metric="wireless")` and got a 404. Root cause turned out to be deeper than "this param should be an Enum":

1. The `metric` description directed the AI at `mist_get_constants(object_type='insight_metrics')` — but **insight_metrics is a different vocabulary** from SLE metrics (insight_metrics returns time-series like `num_clients`, `bytes`; SLE metrics are `wifi-coverage`, `wired-throughput`, etc.). The AI followed the description, didn't see SLE metrics in the response, and guessed "wireless" instead.
2. There was already a discovery tool — `mist_list_site_sle_info(query_type='metrics', scope, scope_id)` — wrapping `GET /api/v1/sites/{site_id}/sle/{scope}/{scope_id}/metrics`. The SLE tool descriptions just weren't pointing at it.

This turned what looked like an Enum-tightening exercise into mostly description-tightening work that fixes the actual misdirection.

### Changes

**Enum corrections (`mist/tools/search_alarms.py`):**
- `AlarmSeverity` Enum: dropped `major` and `minor`. Mist's [search-org-alarms reference](https://www.juniper.net/documentation/us/en/software/mist/api/http/api/orgs/alarms/search-org-alarms) documents only three severity values — `critical`, `info`, `warn`. The previous Enum's two extras would have surfaced as 422s if the AI ever picked them.
- `AlarmGroup` Enum (added in this PR): wraps `severity` and `group` params (previously typed `str` with description-only enum hints).
- `severity` and `group` params on `mist_search_alarms` now `Annotated[AlarmSeverity, ...]` / `Annotated[AlarmGroup, ...]` for schema-time validation.

**SLE description fixes (the actual bug fix for the cited failure):**
- `mist_get_site_sle.metric` description now points at `mist_list_site_sle_info(query_type='metrics', scope, scope_id)` (the right discovery for site-scoped SLE metrics) and explicitly warns that `mist_get_constants(object_type='insight_metrics')` is a DIFFERENT set, not for SLE.
- `mist_get_org_sle.metric` description now points at `mist_get_constants(object_type='insight_metrics')` per [Mist's get-org-sle reference](https://www.juniper.net/documentation/us/en/software/mist/api/http/api/orgs/sles/get-org-sle) — that's the correct discovery path for org-level SLE.

### Why some params stayed `str`

Several `str`-typed Mist params are user-supplied content with tenant-specific or source-dependent valid sets — `mist_search_alarms.alarm_type` (per-tenant alarm definitions), `mist_search_events.event_type` (varies by `event_source`), `mist_get_insight_metrics.metric`. Their descriptions already correctly reference the right `mist_get_constants` discovery; tightening to `Enum` would freeze what's currently dynamic API content. Verified against Mist's docs as part of this PR.

### Tests (577 → 582)

Five new tests in `tests/unit/test_mist_dynamic_mode.py`:

- `TestMistAlarmEnums`:
  - `AlarmSeverity` values match Mist docs exactly (catches accidental re-add of `major`/`minor`)
  - `AlarmGroup` values match Mist docs exactly
  - Pydantic rejects invalid severity values pre-API
- `TestMistSleDescriptionDiscovery`:
  - AST-style guard pinning `mist_get_site_sle.metric` description references `mist_list_site_sle_info`
  - AST-style guard pinning `mist_get_org_sle.metric` description references `object_type=insight_metrics` constants
- Plus regression test: invalid severity (`"major"`) and invalid catch-all (`"emergency"`) both raise ValidationError.

### Audit summary

The Explore agent's full audit revealed **20 of the Mist tools already use proper Enum types correctly** (most prior sessions did this work). The remaining gap was much smaller than the issue framing suggested — and the actual high-value fix was correcting the misdirected SLE descriptions rather than enum-ing every loose `str` param.

## [2.2.0.1] - 2026-04-27

**Fixes tool-level `raise` patterns that crashed the entire `execute()` block in `MCP_TOOL_MODE=code`.** When a tool raised `ValueError` / `TypeError` / `RuntimeError`, the exception propagated through FastMCP's `call_tool` machinery as `MontyRuntimeError` and the AI's `try/except` inside the sandbox could not catch it. Closes #202.

### Background

Code mode replaces the exposed catalog with a 4-tool surface (`tags` / `search` / `get_schema` / `execute`); the LLM writes Python in `execute(code)` and dispatches via `call_tool(name, params)`. When a tool raises, the exception bubbles up at the runtime layer above the AI's Python — the `execute()` call returns "Error calling tool 'execute'" and the AI never sees the validation message. Same code path is fine in dynamic and static modes because the meta-tool wrapper (`<platform>_invoke_tool`) catches the exception and surfaces it as a structured tool result.

### Affected tools (now return error strings)

| Platform | Tool | What used to raise |
|---|---|---|
| GreenLake | `greenlake_get_users` | `_coerce_int` invalid `limit` / `offset` |
| GreenLake | `greenlake_get_user_details` | empty `id` |
| GreenLake | `greenlake_get_devices` | `_coerce_int` invalid `limit` / `offset` |
| GreenLake | `greenlake_get_device_by_id` | empty `id` |
| GreenLake | `greenlake_get_subscriptions` | `_coerce_int` invalid `limit` / `offset` |
| GreenLake | `greenlake_get_subscription_details` | empty `id` |
| GreenLake | `greenlake_get_audit_logs` | `_coerce_int` invalid `limit` / `offset` |
| GreenLake | `greenlake_get_audit_log_details` | empty `id` |
| GreenLake | `greenlake_get_workspace` | empty `workspaceId` |
| GreenLake | `greenlake_get_workspace_details` | empty `workspaceId` |
| Mist | `mist_get_insight_metrics` | `_mac_to_device_id` invalid MAC |
| Mist | `mist_get_configuration_object_schema` | schema-not-found |
| Central | `central_get_alerts` | `build_odata_filter` invalid value |
| Central | `central_get_clients` | `build_odata_filter` invalid value |
| Central | `central_get_devices` | `build_odata_filter` invalid value |
| Central | `central_find_device` | `build_odata_filter` invalid value |
| Central | `central_get_aps` (monitoring) | `build_odata_filter` invalid value |
| Central | `central_get_events` | `compute_time_window` invalid `time_range` |
| Central | `central_get_events_count` | `compute_time_window` invalid `time_range` |

Pattern: each tool now wraps the validation/helper call in a top-level `try/except ValueError` and `return f"Error: {e}"` (or returns an error string directly). Helpers (`_coerce_int`, `compute_time_window`, `build_odata_filter`) keep their existing raising contract — only public tool entries that face the LLM had to be made code-mode-safe.

`_mac_to_device_id` was changed from raising to returning `None` because its existing call sites flow through `handle_network_error` → `ToolError`, which also crashed the sandbox. Now the calling tool checks for `None` and returns an error string explicitly.

### Verified live against the running container

```
greenlake_get_user_details(id="")        → "Error: id is required and cannot be empty"
greenlake_get_users(limit="abc")         → "Error: Parameter 'limit' must be an integer, got 'abc'"
mist_get_insight_metrics(mac="not-a-mac", object_type="ap")
                                          → "Error: invalid MAC address format: 'not-a-mac'"
```

All previously crashed `execute()` with `MontyRuntimeError`. All now return strings the AI can branch on.

### Tests

6 new tests in `tests/unit/test_code_mode.py::TestCodeModeErrorReturns`:
- 3 dynamic tests calling the fixed tools directly with bad input
- 1 contract test pinning `_mac_to_device_id` returns `None` instead of raising
- 1 contract test pinning `_coerce_int` still raises (helpers stay raising; only entry points are wrapped)
- 1 static AST guard scanning every public function in `greenlake/tools/*.py` and failing if a `raise` re-appears (catches future regressions for free)

Total suite: 571 → 577 passing.

### Out of scope

The 19 raises in `apstra/models.py` are Pydantic field validators. Their `ValueError` becomes a `ValidationError` that fires during FastMCP parameter coercion *before* the tool function runs. Same crash symptom, but the fix lives at the FastMCP middleware layer, not in tool code. Tracking that separately if it becomes a real-world friction point.

## [2.2.0.0] - 2026-04-26

**Adds Axis Atmos Cloud as the 6th supported platform** — SASE / cloud-edge management via the Axis Atmos Admin API. Adds 25 underlying tools (12 read + 13 write) plus full documentation. The platform shipped behind the scenes in v2.1.0.x untagged commits and is publicly revealed here.

### What Axis adds

Axis Atmos Cloud is structurally different from the other five platforms — it manages a SASE/cloud-edge fabric rather than wired/wireless campus or datacenter infrastructure. The full tool surface:

- **Connectors** (1 read + 1 write + 1 action) — tunnel-endpoint devices linking customer networks into Atmos. `axis_regenerate_connector` issues a fresh install command (immediate, not staged) and invalidates the prior one.
- **Tunnels** (1 read + 1 write) — IPsec tunnels between customer sites and the Atmos cloud.
- **Connector zones** (1 read + 1 write) — logical groupings of connectors.
- **Locations + Sub-locations** (2 read + 2 write) — physical sites and nested subdivisions.
- **Status helper** (1 cross-entity read) — `axis_get_status(entity_type, entity_id)` returns rich runtime telemetry for connectors (CPU/memory/disk/network/hostname/OS) and tunnels (connection state).
- **Identity** (2 read + 2 write) — Atmos IdP users and groups.
- **Applications + Application Groups** (2 read + 2 write) — published apps and tag-style groupings.
- **Web Categories** (1 read + 1 write) — URL-classification categories for policy.
- **SSL Exclusions** (1 read + 1 write) — hosts excluded from SSL inspection.
- **Commit** (1 tool) — `axis_commit_changes` applies ALL pending staged writes for the tenant.

### Staged-write workflow (Axis-specific)

Every `axis_manage_*` write **stages** in Axis and only takes effect after `axis_commit_changes` runs — same pattern Axis enforces for changes made through the admin UI. Each write tool's response includes a `next_step` hint naming the commit tool. Commit is tenant-wide (no per-change selection) and uses a 60-second timeout. `axis_regenerate_connector` is the only mutation that does NOT stage.

### JWT bearer auth + expiry surfacing

Axis tokens are static JWTs generated in the admin portal at *Settings → Admin API → New API Token*. There is no refresh endpoint. The server decodes the `exp` claim at startup and:

- Logs `Axis: token expires in N day(s)` at startup
- Logs a warning when fewer than 30 days remain
- The cross-platform `health(platform="axis")` tool returns `degraded` with a `token_expires_in_days` countdown when inside the warning window
- A 401 surfaces a clear "regenerate at Settings → Admin API → New API Token" error

### Disabled-but-on-disk

Two endpoints documented in the Axis swagger return 403 even with read+write-scoped tokens — apparently hidden / unreleased upstream. Their tool implementations live on disk but are excluded from the registry via a `_DISABLED_TOOLS` dict in `platforms/axis/__init__.py`. Re-enabling either pair (`custom_ip_categories`, `ip_feed_categories`) is a one-line move when Axis flips them on.

### Tool surface impact

| Mode | Before | After |
|---|---|---|
| Dynamic (default, exposed to AI) | 19 tools (5 platforms × 3 meta + 4 cross-platform) | 22 tools (6 platforms × 3 meta + 4 cross-platform) |
| Static (every tool registers individually) | 280+ visible | 305+ visible |

Token cost in dynamic mode goes from ~3,100 to ~3,700 — the 600-token bump is the cost of three additional meta-tool entries. The four cross-platform aggregators (`health`, `site_health_check`, `site_rf_check`, `manage_wlan_profile`) are unchanged.

### Configuration

| | |
|---|---|
| Secret | `secrets/axis_api_token` |
| Write toggle | `ENABLE_AXIS_WRITE_TOOLS=true` (default `false`) |
| Health probe | `health(platform="axis")` |
| Auto-disables when | the secret file is missing or empty |

### Tests

571 tests passing (no new tests in this docs/reveal PR — Axis registry, write-tag, JWT-exp, and health-probe coverage all landed with the prior phases). Axis test coverage already includes:

- Registry population (12 active reads + 13 active writes; the 4 disabled tools must NOT appear)
- Every write carries `axis_write_delete` so the visibility transform + elicitation gate fires
- Every `axis_manage_*` description references `axis_commit_changes` (regression on the staged-write contract)
- ElicitationMiddleware reads `enable_axis_write_tools` and enables the `axis_write_delete` tag
- JWT exp decoder: well-formed JWT, opaque token, missing `exp`
- Health probe: outside warning, inside 30-day window, expired, undecodable

### Bundles in this release

- PR #198 — Phase 1 read-only surface (12 tools + JWT-exp surfacing + health-probe enrichment)
- PR #199 — Phase 2 write surface (13 manage tools + commit + regenerate + ElicitationMiddleware fix)
- This release — public reveal: docs (README capability matrix, INSTRUCTIONS.md tool categories, TOOLS.md overview + per-entity tables), uncomments compose entries, version bump 2.1.0.2 → 2.2.0.0

### Not in this release

- The Axis tools are not in scope for the cross-platform aggregators (`site_health_check`, `site_rf_check`, `manage_wlan_profile`) — Axis has no Wi-Fi / RF surface, and its "locations" concept doesn't map to the site-health aggregator's site model. Axis remains discoverable via the per-platform meta-trio in dynamic mode and via `tags(query=["axis"])` in code mode.

## [2.1.0.2] - 2026-04-26

**Fixes site-health field-name mismatches that caused `central_get_site_health`, `central_get_site_name_id_mapping`, and `site_health_check` to silently report empty/zero data.**

Reported by a user whose AI client noticed `site_health_check` returning 0 clients for a site that had real client traffic. Investigation traced it to three code paths reading the wrong field name from Aruba Central's `/network-monitoring/v1/sites-health` response, plus a fourth pagination bug that would silently truncate results for tenants with >100 sites.

### Bugs

- **`central_get_site_health` returned an empty list.** [`process_site_health_data`](src/hpe_networking_mcp/platforms/central/utils.py) keyed the result dict on `site["name"]` but the API returns `siteName`. Every site got filtered out at the dict-comprehension step. Fixed in three places (the main key, plus the device-merge and client-merge loops).
- **`central_get_site_name_id_mapping` returned `total_devices: 0` and `total_clients: 0` for every site.** Read `clients.total` and `devices.total` but the simplified shape (after `pycentral.simplified_site_resp`) uses `count`. Changed to `clients.count` / `devices.count`. `alerts.total` was already correct (it's the one field `simplified_site_resp` does map from `totalCount` → `total`).
- **`site_health_check` (cross-platform) reported the same `total_clients: 0` / `total_devices: 0` symptom.** Same root cause as above, same fix.
- **`fetch_site_data_parallel` used cursor pagination against offset-paginated endpoints.** All three site-health endpoints (`/sites-health`, `/sites-device-health`, `/sites-client-health`) accept `limit` + `offset` only — Aruba's dev portal does not document a cursor param. The default `paginated_fetch(use_cursor=True)` sent `next=1` and worked accidentally for tenants with ≤100 sites (the server tolerates the unknown param and returns page 1) but would silently stop after the first page for larger tenants. Switched these three calls to `use_cursor=False`.

### Mode coverage

The empty-list and zero-counts symptoms reproduced in both `dynamic` and `code` modes — the underlying tools share the same code path regardless of how they're surfaced. `site_health_check` is gated off in code mode (cross-platform aggregator), so its specific symptom doesn't surface there, but the per-platform tools that do appear (`central_get_site_health`, `central_get_site_name_id_mapping`) show the same data through both modes.

### Verified live against a real tenant

| Tool | Before | After |
|---|---|---|
| `central_get_site_health` | `[]` | 13 sites; HQ = 38 clients / 17 devices, with full per-type breakdown |
| `central_get_site_name_id_mapping` (HQ) | `health: 0, total_devices: 0, total_clients: 0, total_alerts: 0` | `health: 81, total_devices: 17, total_clients: 38, total_alerts: 3` |

### Tests

6 new tests in `tests/unit/test_central_utils.py` pinning `process_site_health_data` and `transform_to_site_data` against captured-from-live response shapes. If Aruba ever renames `siteName` → `name` (or back), these tests fail loudly instead of letting another silent regression ship.

Total: 562 → 568 tests passing.

## [2.1.0.1] - 2026-04-25

**ClearPass coverage follow-up — adds 14 read/write tools to close the dev-portal gap surfaced during the v2.1.0.0 audit.**

### New read tools (12)

- **Endpoint visibility** (new module category) — `clearpass_get_onguard_activity`, `clearpass_get_fingerprint_dictionary`, `clearpass_get_network_scan`, `clearpass_get_onguard_settings` (with `global_settings: bool` flag).
- **Certificate authority** (new module category) — `clearpass_get_certificates` (with `chain: bool` for chain retrieval), `clearpass_get_onboard_devices`. Path note: `/api/onboard/device` is CA-scope, distinct from `/api/device` (identity device records, already wrapped by `clearpass_get_devices`).
- **Identities** — `clearpass_get_external_accounts` for external-account records (lookup by ID or name + paginated list).
- **Certificates** — `clearpass_get_revocation_list` for the platform-cert CRL store.
- **Integrations** — `clearpass_get_extension_log` (path: `/extension-instance/{id}/log`, optional `tail`).
- **Policy elements** — `clearpass_get_radius_dynamic_authorization_template` for DUR template lookups.
- **Local config** — `clearpass_get_cluster_servers` (no params; lists every cluster node so the AI can find `server_uuid`s).

### New write tools (3, all `WRITE_DELETE`-tagged)

- **`clearpass_manage_certificate_authority`** — full internal-CA cert lifecycle dispatch (`import`, `new`, `request`, `sign`, `revoke`, `reject`, `export`, `delete`).
- **`clearpass_manage_onboard_device`** — `update` (PATCH) or `delete` for `/api/onboard/device/{id}` records.
- **`clearpass_manage_service_params`** — PATCH `/api/server/{uuid}/service/{id}` to align per-node service parameter values. Documented use case: cluster-consistency audits — list cluster servers → fetch services per node → diff → align drifted nodes.

### Path corrections caught in live testing

The first round of new tools shipped with several wrong paths (the dev-portal docs and SDK names diverge in places). Fixed before commit:

- `/fingerprint-dictionary` → `/fingerprint`
- `/network-scan` → `/config/network-scan`
- `/server` → `/cluster/server` (now uses the SDK's `get_cluster_server()` directly)
- `/cert/revocation-list` → `/revocation-list`

Dropped one tool that turned out to be a false positive: `clearpass_get_onboard_users` — `/api/onboard/user` returned 404 in our tenant and the `pyclearpass` SDK has no equivalent method, so the endpoint likely doesn't exist on this CPPM version. The matching `user` target_type was also dropped from `clearpass_manage_onboard*` (renamed to `clearpass_manage_onboard_device`).

### Audit false positives caught before shipping

Three tools the agent's coverage audit flagged as missing turned out to already be wrapped:

- `random/mpsk` → already covered by `clearpass_generate_random_password(type="mpsk")`.
- `run_insight_report` → already covered by `clearpass_manage_insight_report(action_type="run")`.
- `trigger_endpoint_context_server_poll` → already covered by `clearpass_manage_endpoint_context_server(action_type="trigger_poll")`.

ClearPass tool count: 126 → 140 (+14).

## [2.1.0.0] - 2026-04-25

**Adds `MCP_TOOL_MODE=code` as an experimental opt-in third tool mode.** Default stays on `dynamic` — no behavior change for existing users. Code mode wires FastMCP's `CodeMode` transform so the LLM writes sandboxed Python to compose multi-step workflows in a single round-trip, rather than walking the per-platform meta-trio N times. Cloudflare's ["Code Mode"](https://blog.cloudflare.com/code-mode/) argument: LLMs are better at writing code than at choosing from tool menus.

### Four-tier progressive disclosure

The exposed catalog in code mode is exactly 4 tools:

| Tier | Tool | Purpose |
|---|---|---|
| 1 | `tags(detail)` | Browse the tag space — platform names, read/write buckets, module categories |
| 2 | `search(query, tags, detail)` | BM25 tool search, optionally scoped by tag |
| 3 | `get_schema(tools, detail)` | Parameter shapes for named tools |
| 4 | `execute(code)` | Run async Python in a `pydantic-monty` sandbox with `call_tool(name, params)` in scope |

Inside `execute`, `call_tool` dispatches through the real FastMCP call_tool — so `NullStripMiddleware`, `ElicitationMiddleware`, and Pydantic coercion all continue to fire. Writes still prompt for confirmation. Per-platform write-gating Visibility transforms still apply.

### Cross-platform aggregators gated off in code mode

`site_health_check`, `site_rf_check`, and `manage_wlan_profile` are NOT registered when `MCP_TOOL_MODE=code`. Those tools exist to work around dynamic mode's "AI reaches for one platform and stops" problem — code mode's premise is that the LLM can do the cross-platform join itself via `call_tool`. Keeping them would contradict the premise and make measurement meaningless. `health` stays registered in every mode (reachability info, not aggregation).

### Platform tags on every tool

Every tool registered through a platform's `_registry.py` shim now carries its platform name in `tool.tags`:
- Mist tools: `{"mist", "dynamic_managed", ...optional write tags}`
- Central: `{"central", "dynamic_managed", ...}`
- etc.

This lets `tags(detail=brief)` surface useful platform buckets and `search(query=..., tags=["mist"])` scope filtering to one vendor. Side benefit: static and dynamic modes also gain platform tagging for free — no behavior change, but the data's now there if we want to use it.

### Config + server wiring

- `config.py` — `MCP_TOOL_MODE=code` is now a valid value (was `{"static", "dynamic"}`, now `{"static", "dynamic", "code"}`). Default stays `"dynamic"`; unknown values fall back to `"dynamic"` with a warning.
- `server.py` — new `_register_code_mode(mcp)` helper installs `CodeMode(sandbox_provider=MontySandboxProvider(limits=ResourceLimits(max_duration_secs=30.0, max_memory=128 MB, max_recursion_depth=50)), discovery_tools=[GetTags(brief), Search(brief), GetSchemas(detailed)])`. Falls back with a warning if `pydantic-monty` is missing.
- Per-platform `register_tools` — `build_meta_tools()` skipped in code mode (already skipped in static); log message now distinguishes "code mode" from "static mode" for accurate startup output.
- `docker-compose.yml` — untouched. Users opt in via `-e MCP_TOOL_MODE=code` or a compose override.

### Verified live against a real tenant

- `MCP_TOOL_MODE=code` — exposed catalog is exactly 4 tools (`tags`, `search`, `get_schema`, `execute`). No `site_health_check`, `site_rf_check`, or `manage_wlan_profile`.
- `tags(brief)` returns platform buckets (`mist (31 tools)`, `central (73)`, `axis (0)`, etc.) plus module categories.
- `search(query="disconnected", tags=["mist"])` returns 7 of 173 tools, BM25-ranked and platform-scoped.
- `execute` with `return await call_tool("health", {})` returns the live health report.
- Cross-platform join (mist_get_self → mist_search_device → central_get_aps) runs in ONE execute call, returning `{"mist_aps_count": 5, "central_aps_count": 3, "sample_mist_ap": "BRANCH-1-AP-1", "sample_central_ap": "HQ-AP-1", "cross_platform_match": True}`.
- `call_tool("site_health_check", ...)` correctly raises `Unknown tool: site_health_check` — gating verified.
- `MCP_TOOL_MODE=dynamic` (default) — unchanged. Still 18 tools advertised (15 meta + health + site_health_check + site_rf_check).

### Sandbox constraints the AI has to work around

`pydantic-monty` is a restricted Python subset. Some things NOT available in the sandbox:
- `hasattr`, `type`, and most introspection builtins
- stdlib imports beyond what monty whitelists

The AI learns these the same way it learns any API — via error messages from its first attempt. Early Phase 2 measurement will tell us how much friction this adds.

Tool return values inside `execute` are wrapped as `{"result": <value>}` (FastMCP's `structured_content` for non-schema-typed returns). The AI accesses via `me["result"]["..."]`.

### Tests

11 new tests in `tests/unit/test_code_mode.py`:
- Config parsing (`code` accepted, unknown falls back, `static`/`dynamic` unchanged, default is `dynamic`)
- Cross-platform aggregator gating (dynamic + static register all; code registers none; code invokes `_register_code_mode` hook)
- Registry platform tagging (Mist + Axis shims add platform name to effective tags)
- `_register_code_mode` falls back gracefully if `pydantic-monty` import fails

Total suite: **552 tests** passing (541 → 552).

### Not in this release

- No default flip. Code mode is opt-in experimental. A decision on whether to change the default will come after Phase 2 head-to-head measurement work — see `CODE_MODE_PLAN.md` (scratch).
- No `INSTRUCTIONS.md` changes. Dynamic mode remains the documented default pattern.
- `fastmcp.experimental.transforms.code_mode` is still in `experimental/` upstream. Using it means accepting that the API may change — `MCP_TOOL_MODE=dynamic` remains the production-stable choice.

### ClearPass query-param audit

Bundled into this release: a systematic audit of every `clearpass_get_*` tool against the public ClearPass API reference at https://developer.arubanetworks.com/cppm/reference. Surfaced two real gaps and fixed both.

#### `calculate_count` added to all 45 list-style read tools

Every `/api/<resource>` list endpoint accepts a `calculate_count: bool` query param (per Apigility convention) that adds a `count` field to the response. Useful for the AI to know whether a paginated query has more pages without doing another request — and surprisingly informative on its own (e.g. "your tenant has 85,515 active sessions" landed in measurement testing).

Only `clearpass_get_endpoints` had this param before. Added it to:
- `clearpass_get_system_events`, `clearpass_get_auth_sources`, `clearpass_get_auth_methods`, `clearpass_get_trust_list`, `clearpass_get_client_certificates`, `clearpass_get_service_certificates`
- `clearpass_get_enforcement_policies`, `clearpass_get_enforcement_profiles`
- `clearpass_get_pass_templates`, `clearpass_get_print_templates`, `clearpass_get_weblogin_pages`
- `clearpass_get_guest_users`, `clearpass_get_api_clients`, `clearpass_get_local_users`, `clearpass_get_static_host_lists`, `clearpass_get_devices`, `clearpass_get_deny_listed_users`
- `clearpass_get_extensions`, `clearpass_get_syslog_targets`, `clearpass_get_syslog_export_filters`, `clearpass_get_event_sources`, `clearpass_get_context_servers`, `clearpass_get_endpoint_context_servers`
- `clearpass_get_network_devices`, `clearpass_get_services`, `clearpass_get_posture_policies`, `clearpass_get_device_groups`, `clearpass_get_proxy_targets`, `clearpass_get_radius_dictionaries`, `clearpass_get_tacacs_dictionaries`, `clearpass_get_application_dictionaries`
- `clearpass_get_roles`, `clearpass_get_role_mappings`
- `clearpass_get_admin_users`, `clearpass_get_admin_privileges`, `clearpass_get_operator_profiles`, `clearpass_get_attributes`, `clearpass_get_data_filters`, `clearpass_get_file_backup_servers`, `clearpass_get_snmp_trap_receivers`, `clearpass_get_policy_manager_zones`
- `clearpass_get_sessions`

Implementation: 5 files share a `_build_query_string` helper (audit, certificates, guest_config, identities, integrations, network_devices, policy_elements, server_config); helper signature gained `calculate_count: bool = False`. Inline-pattern files (auth, endpoints, enforcement, guests, roles, sessions) had the param block updated directly.

#### `/alert` and `/report` no longer accept unsupported `filter` / `sort`

Per the dev portal, ClearPass `/alert` and `/report` endpoints document **only** `offset`, `limit`, and `calculate_count` — they do not support `filter` or `sort`. Our `clearpass_get_insight_alerts` and `clearpass_get_insight_reports` tools were exposing `filter` and `sort` and forwarding them in the query string. Either Mist would 400 or silently ignore them. Removed both params from those two tool signatures and switched to a simpler inlined query string. Other tools that DO support filter+sort are unchanged.

#### What this didn't touch

- 11 ClearPass API endpoints documented in the dev portal still don't have wrapping tools — high-value gaps include `/api/onguard-activity`, `/api/external-account`, `/api/cert/revocation-list`, `/api/fingerprint-dictionary`, `/api/extension-instance/{id}/log`, `/api/network-scan`, `/api/onguard/settings`, `/api/radius-dynamic-authorization-template`, plus a handful of write/POST endpoints. Tracked as a follow-up; the audit's coverage report lives in `~/Documents/Coding Projects/hpe-networking-mcp-scratch/` for reference.

## [2.0.0.5] - 2026-04-24

**New cross-platform tool: `site_rf_check`.** Closes the AI-discovery gap where channel-planning / RF / spectrum questions produced Mist-only answers even when the user had Aruba APs in Central at the same site.

### Why a new tool, not a docs rule

Tested approach: a docs rule in `INSTRUCTIONS.md` saying "for platform-agnostic questions, query every enabled platform first." Track record on this codebase ([#184](https://github.com/nowireless4u/hpe-networking-mcp/issues/184), [#185](https://github.com/nowireless4u/hpe-networking-mcp/issues/185)) shows soft "consider X before deciding" rules in long instruction blocks tend to lose to whatever shortcut pattern the AI matched on first ("Wi-Fi channels → Mist" is sticky). What changes behavior reliably is removing the judgment call: a purpose-built tool whose name + description put cross-platform aggregation directly in the tool list.

### What the tool does

Mirrors the `site_health_check` pattern. Single call returns:

- **Per-band aggregation (2.4 / 5 / 6 GHz):** AP count, channel distribution, avg/max channel utilization, avg noise floor, allowed channels (from the Mist RF template).
- **Per-AP radio snapshot:** name, model, platform, connected status, and one row per band with channel, bandwidth, TX power, utilization, noise floor.
- **Recommendations:** co-channel clusters (3+ APs on the same primary channel in 5/6 GHz), peak utilization ≥70%, noise floor >-70 dBm.
- **Pre-rendered ASCII RF dashboard** in `rendered_report` — channel-occupancy bars, utilization meters, per-AP table, recommendations list. Always-on by default so even clients that don't draw charts get a visual report. Opt out with `include_rendered_report=False`.

### Site-picker fallback

When `site_name` is omitted, the tool returns a list of selectable sites in `site_options` (with per-platform AP counts and online counts) instead of erroring. The `platform` filter still applies — `site_rf_check(platform="central")` lists only Central sites. Two cheap cross-platform calls (orgs/inventory + sites/aps) cover the listing — no per-site fan-out.

### Data sources

| Side | Calls | What we extract |
|---|---|---|
| Mist | `/sites/{id}/stats/devices?type=ap` + `getSiteCurrentChannelPlanning` | Per-AP `radio_stat` (per-band channel, power, usage, noise_floor, num_clients), template allowed channels |
| Central | `MonitoringAPs.get_all_aps(filter=siteId)` + per-AP `MonitoringAPs.get_ap_details` (parallel via asyncio.gather, capped by `max_aps_per_platform`) | Per-AP `radios` array (band, channel, bandwidth, power, channelUtilization, noiseFloor) |

Channel notation differs across platforms: Central uses bonded-channel suffixes (`165S`, `49T+`); the new `_parse_primary_channel` helper extracts the primary channel integer for aggregation while preserving the raw value.

### Verified live

3 Aruba AP-755s at site HQ (Central) — full report rendered with 2.4G/5G/6G channel bars, noise floors, utilization meters, per-AP table. Picker mode tested across 19 sites with accurate online counts. Mist-side picker uses `connected: bool` from `/orgs/{id}/inventory` (not the `status` field — that endpoint doesn't carry it).

### Test additions

49 new unit tests in `tests/unit/test_site_rf_check.py` covering parsers (channel/numeric/bandwidth/band normalization), platform-filter normalization, band aggregation (channel distribution, util/noise math, disconnected-AP exclusion), synthesis (co-channel detection per band, utilization/noise thresholds), the rendered report, and the site picker (sort order, truncation, empty case).

Total suite: **512 tests** passing (463 → 512).

### Code

- New module: `src/hpe_networking_mcp/platforms/site_rf_check.py` (~700 LoC; mirrors `site_health_check.py` shape).
- New registration: `_register_site_rf_check` in `server.py`, gated by `config.mist or config.central`.

### Docs in this PR

- `INSTRUCTIONS.md` — adds `site_rf_check` to the cross-platform-tools list with explicit "use for any channel-planning / spectrum / RF-health question" guidance.
- `README.md` — tool counts updated (18 → 19 default), new "Site RF Check" bullet under Cross-Platform Tools.
- `docs/TOOLS.md` — updated counts, full param doc + return-shape doc for `site_rf_check`.

## [2.0.0.4] - 2026-04-24

**Bug-fix triple for two Mist tools surfaced during live RF-planning use.** Fixes [#190](https://github.com/nowireless4u/hpe-networking-mcp/issues/190), [#191](https://github.com/nowireless4u/hpe-networking-mcp/issues/191), and [#192](https://github.com/nowireless4u/hpe-networking-mcp/issues/192).

### Bugs fixed

#### A. `mist_get_site_rrm_info` rejects its own defaults for non-events modes (#190)

`limit=200, page=1` were set as Pydantic field defaults, then validated against `if limit and rrm_info_type != "events": raise`. Result: `current_channel_planning`, `current_rrm_considerations`, and `current_rrm_neighbors` always returned `400 limit parameter can only be used when rrm_info_type is "events"` — three of four modes unreachable.

**Fix:** `limit`/`page` now default to `None` at the signature level; the 200/1 defaults are applied only inside the `events` case. Validation gate unchanged (still rejects explicit values for non-events modes).

**Bonus (same tool):** `band` is actually required for the `events` mode too (Mist returns `400 "valid band is required"` when omitted), but the tool description only listed it as required for `considerations` and `neighbors`. Added the missing client-side validation and updated the field description.

#### B. `mist_get_insight_metrics` leaks literal `"None"` into Mist API (#191)

Every case branch unconditionally wrapped optional time-range params with `str(start)`, `str(end)`, `str(duration)`, `str(interval)`. When the client omitted any of these, Pydantic filled in `None`, `str(None)` became the 4-char string `"None"`, and that landed in Mist query params → 400/404s.

**Fix:** Pre-compute `start_str = str(start) if start else None` (etc.) once, reuse across all 6 case branches. Matches the guard pattern already used in `get_site_rrm_info`'s events branch.

#### C. `mist_get_insight_metrics` dispatch broken across 5 of 6 branches (#192)

Every branch had at least one issue against the real `mistapi` SDK signatures:

| object_type | Was | Problem |
|---|---|---|
| `site` | `getSiteInsightMetrics(metric=...)` | Wrong kwarg (SDK wants `metrics=`); SDK function itself builds wrong URL (`/insights?metrics=X` vs real `/insights/{metric}`) |
| `client` | `metric=` | Wrong kwarg (SDK wants `metrics=`) — TypeError |
| `ap` | `getSiteInsightMetricsForDevice(device_mac=mac, metric=...)` → `/insights/device/{mac}/ap-rf-metrics` | Wrong SDK function; `ap-rf-metrics` only works via `getSiteInsightMetricsForAP` → `/insights/ap/{device_id}/stats` — 404 |
| `gateway` | `metric=` | Wrong kwarg — TypeError |
| `mxedge` | OK | (only `str(None)` leak) |
| `switch` | OK | (only `str(None)` leak) |

**Fix:**

- `site` branch: bypass the broken `getSiteInsightMetrics` and call `apisession.mist_get` directly with the correct `/api/v1/sites/{id}/insights/{metric}` URL. (Filed upstream — the SDK function's URL construction is wrong.)
- `client`, `ap`, `gateway`: rename `metric=` → `metrics=` kwarg; switch `ap` from `ForDevice` to `ForAP`; use `device_id` UUID (not MAC) for `ap` and `gateway` endpoints.
- New helper `_mac_to_device_id(mac)` derives the Mist device UUID from a MAC using the documented `00000000-0000-0000-1000-<mac>` convention — so callers can pass either `mac` or `device_id` for `ap`/`gateway`.
- All 6 branches now enforce the required device-identifier explicitly (`mac` for client/mxedge/switch; `mac` or `device_id` for ap/gateway).

### Verified against live Mist tenant

- `rrm_info(current_channel_planning)` → RF template data ✅
- `rrm_info(current_rrm_neighbors, band=5)` → neighbor list ✅
- `rrm_info(events, band=6, duration=1d)` → event list ✅
- `insight_metrics(object_type=site, metric=num_clients, duration=1d)` → 24h timeseries ✅
- `insight_metrics(object_type=site, metric=bytes, duration=1h)` → 1h timeseries ✅
- `insight_metrics(object_type=ap, metric=ap-rf-metrics, mac=04:cd:c0:d1:e5:5a, duration=1d)` → AP RF metrics (MAC-with-colons handling verified) ✅

### Scope: Mist-wide audit

Audit of all 30 Mist tool files for these two bug classes:

- **Default-trips-own-validation-gate (A):** 1/30 files affected (`get_site_rrm_info.py` only).
- **`str(None)` leak (B):** 1/30 files affected (`get_insight_metrics.py` only).

No other Mist tools exhibited either pattern. All other tools already use the correct `default=None` + guarded `str()` idioms.

## [2.0.0.3] - 2026-04-24

**UX win: cut one round-trip per simple tool invocation.** `<platform>_list_tools` responses now include a compact `params` map per tool entry, so AI clients can skip `<platform>_get_tool_schema` when the parameter names + types alone are enough to compose an `invoke` call. Fixes [#185](https://github.com/nowireless4u/hpe-networking-mcp/issues/185).

### What changed

Every tool entry in `<platform>_list_tools` now looks like:

```json
{
  "name": "mist_get_site_health",
  "category": "get_site_health",
  "summary": "Get a health overview across all sites...",
  "params": {"org_id": "UUID"}
}
```

- `params` is a `{name: "Type[?]"}` map.
- `?` suffix means optional (has a default or absent from the schema's `required`).
- Types: `UUID`, `string`, `integer`, `boolean`, `dict`, `list[...]`, or an Enum class name like `Action_type` / `Object_type` (AI still needs `get_tool_schema` to see the enum's valid values — for those, the round-trip isn't eliminated, just informed).

### Expected AI behavior change

- **Simple-tool path** (single common case — one required param whose type is obvious): `list_tools` → `invoke_tool` (**2 round-trips, down from 3**).
- **Enum/complex-tool path**: AI still calls `get_tool_schema` in between. No regression vs. v2.0.0.2.
- **Anti-pattern** (`invoke_tool` with `params={}` or guessed names): still fails with `invalid_params` — but now the remediation hint is explicit that the AI had the information it needed from `list_tools` already.

### Code changes

- **`platforms/_common/meta_tools.py`**:
  - New `_resolve_type_name(pdef)` helper extracts a compact type string from a JSON schema property. Handles `$ref` (enum / nested model), `format` hints (`uuid` → `UUID`, `date-time` → `datetime`), `anyOf`/`oneOf` unions (picks first non-null branch), and `array` types (emits `list[item_type]`).
  - New `_param_summary(fm_tool)` helper returns the `{name: "Type[?]"}` map from a FastMCP tool's parsed schema.
  - `_list_tools` now fetches each matching tool's parsed schema (via `mcp._get_tool(name)` — same private accessor we already use for `_get_tool_schema`) and includes the summary in its response.
  - Tool description updated to advertise the new `params` field and describe the `?` convention.

- **`INSTRUCTIONS.md`**:
  - TOOL DISCOVERY section: step 2 (`list_tools`) now explicitly mentions the new `params` field; step 3 (`get_tool_schema`) becomes conditional on whether step 2's info is sufficient; ✅/❌ example blocks updated to show the simple-tool 2-round-trip path alongside the full-schema 3-round-trip path.
  - Rule 5 reframed: "use the information you already have from `list_tools`" (soft-mandatory rather than v2.0.0.2's hard-mandatory schema fetch).
  - Rule 6 updated: names the specific cases where `get_tool_schema` is still needed (enum value lists, param descriptions, nested object shapes).

### Tests added

- `test_entries_include_params_summary` in `test_meta_tools.py::TestListTools` — verifies Enum-typed, UUID-typed, and str-typed params all surface correctly in the new `params` map.
- Updated the `mcp_with_fake_tools` fixture to also register fake tools via `mcp.tool(...)` so FastMCP has parsed schemas for them (previously the fixture only populated `REGISTRIES`, which was enough for the coercion tests but not for the new `list_tools` path).
- Fixed fake-tool ctx typing: `ctx` parameters in test fixtures are now typed as `FastMCPContext` so FastMCP recognizes them as the context-injection point and strips them from the advertised schema.

Total suite: 463 tests passing (462 → 463).

### Token-budget check

- **Baseline per-turn tool-schema payload**: unchanged (~2,910 tokens — we only touched the `list_tools` response, not the meta-tools' own input schemas).
- **Per-query `list_tools` response**: +10-20% depending on how many tools match. For a filtered call (`filter="health"` matching 3-5 tools): +60-100 tokens. For an unfiltered Mist list (35 tools): +400-600 tokens.
- **Per-query net**: saves ~500-1000 tokens per *avoided* `get_tool_schema` round-trip (the full schema response is typically 10× larger than the inlined param map). **Net positive on both baseline and per-query token budgets.**

### Users affected

Every AI client using dynamic mode. No configuration change needed — new `params` field is additive and ignored by older clients.

---

## [2.0.0.2] - 2026-04-24

**Second hotfix for v2.0 dynamic-mode dispatch.** v2.0.0.1 fixed the positional-`ctx` collision (Mist tools now accept `ctx: Context`), but live-testing surfaced two more dispatch-path bugs the earlier fix didn't address.

### Bugs fixed

**1. `AttributeError: 'str' object has no attribute 'value'` on Enum params.** The meta-tool was calling `spec.func(ctx, **safe_params)` directly — bypassing FastMCP's normal Pydantic validation/coercion layer. So tools doing `object_type.value` got back the raw string `"org_sites"` (from the incoming JSON) instead of the `Object_type.ORG_SITES` enum instance. Affected every tool with `Annotated[SomeEnum, ...]` params, including `mist_get_configuration_objects`, `mist_get_org_or_site_info`, `mist_get_stats`, `mist_get_site_sle`, and the `manage_*` tools.

**2. `input_schema: null` in `<platform>_get_tool_schema` responses.** The handler called `mcp.get_tool(name)` which respects the Visibility transform and returns `None` for hidden tools — i.e., every registered platform tool in dynamic mode. Since the AI couldn't see parameter schemas, it had to guess at param names, producing errors like `unexpected keyword argument 'stat_type'` (tool expected `stats_type`) or `missing 8 required positional arguments`.

### Fixes

**`platforms/_common/meta_tools.py`:**

- **New `_coerce_params(spec, raw_params)` helper.** Builds a Pydantic model from the tool's function signature via `inspect.signature` + `get_type_hints(include_extras=True)` (so `from __future__ import annotations`-style string annotations resolve against the tool module's globals), then validates `raw_params` against it. Returns the coerced Python objects (`Enum` instances, `UUID` objects, etc.) via attribute access rather than `model_dump()` so typed values survive to the tool body.
- **Strips explicit `None` from incoming params.** AI clients commonly pass `{"site_id": null}` for optional params, but Mist signatures use `Annotated[UUID, Field(default=None)]` (not `UUID | None`), which Pydantic rejects as "UUID required." The coercion helper now drops None-valued keys before validation so the Field-level default applies.
- **Handles Annotated-embedded defaults.** When `inspect.Parameter.default` is empty but the annotation is `Annotated[T, Field(default=X)]`, the helper now extracts `X` from the `FieldInfo` metadata and uses it — matching how FastMCP's own dispatch handles this pattern.
- **`_invoke_tool` now calls `_coerce_params` before `spec.func`.** `ValidationError` surfaces cleanly as `{"status": "invalid_params", "message": ...}` with actionable detail (missing fields, coercion failures).
- **`_get_tool_schema` uses `mcp._get_tool(name)` (underscore prefix) instead of `mcp.get_tool(name)`.** The underscore version bypasses the Visibility filter, so hidden underlying tools now return their JSON schema as expected. The AI can actually see parameter names + types + requiredness instead of guessing.

### Tests added

Four new coercion regression tests in `tests/unit/test_meta_tools.py::TestInvokeToolCoercion`:
- Enum string → Enum instance coercion
- UUID string → UUID object coercion
- Missing-required-param produces `invalid_params` (not the opaque API 404 v2.0.0.1 allowed through)
- Explicit `null` for optional params falls through to the Annotated default

Total suite: 462 tests passing (458 → 462).

### Affected users

Anyone on v2.0.0.1 who hit `AttributeError: 'str' object has no attribute 'value'` or `input_schema: null` when calling Mist tools via `mist_invoke_tool`. Same workaround as v2.0.0.1 while the image propagates: `MCP_TOOL_MODE=static` restores v1.x-style direct-tool surface.

### Note on v2.0.0.1 + v2.0.0.2

v2.0.0.1 and v2.0.0.2 together complete what should have been a single "dynamic dispatch actually works" fix — the bug class was simply bigger than the first pass caught. Both ship in the same 24-hour window post-v2.0.0.0.

---

## [2.0.0.1] - 2026-04-24

**Hotfix for a critical v2.0.0.0 regression.** Every Mist tool invocation through `mist_invoke_tool` failed in dynamic mode with `TypeError: got multiple values for argument 'action_type'` (or the equivalent for whichever parameter was the tool's actual first positional argument). Reported separately by Seth and Zach during v2.0 live testing. Fixes [#179](https://github.com/nowireless4u/hpe-networking-mcp/issues/179).

### Root cause

`_common/meta_tools.py::_invoke_tool` dispatches tool calls as `spec.func(ctx, **safe_params)` — `ctx: Context` is passed positionally. Central, ClearPass, GreenLake, and Apstra tools all accept `ctx` as their first parameter, so the dispatch is correct. Mist tools, however, were ported from Thomas Munzer's upstream `mistmcp` project, which uses FastMCP's `get_context()` helper inside `get_apisession()` instead of accepting `ctx` explicitly. The wrapper's positional `ctx` collided with the tool's real first parameter.

In static mode this isn't a problem because FastMCP's `@mcp.tool` decorator handles `ctx` injection internally — the bug only surfaces through the dynamic-mode meta-tool dispatch path.

### Fixed

- **`platforms/mist/client.py`** — `get_apisession(ctx)` and `validate_org_id(ctx, org_id)` now take `ctx: Context` explicitly. `process_response` and `handle_network_error` kept their existing signatures; the two `ctx.error()` calls in `process_response` were swapped for `logger.error` to avoid having to thread ctx through ~300 call sites just to surface identical information that's already in the raised `ToolError`. Matches Central's pattern where helpers only take ctx when they need `lifespan_context` access.
- **35 Mist tool files** under `platforms/mist/tools/` — every `@tool(...)`-decorated `async def` now accepts `ctx: Context` as its first parameter. All `get_apisession()` and `validate_org_id(...)` call sites updated to pass `ctx`. Imports of `from fastmcp.server.dependencies import get_context` removed; imports of `from fastmcp import Context` added.
- **New regression test** `tests/unit/test_invoke_tool_dispatch.py` — parametrized over all 5 platforms, uses `inspect.signature()` to assert every registered tool's first parameter is `ctx: Context`. This is the exact invariant `_invoke_tool` relies on. Would have caught the v2.0.0.0 bug at test time. Total suite: 458 tests passing (453 → 458, +5 new).

### Deferred to a follow-up

Mist still uses a different **module-organization convention** than the other four platforms (one-tool-per-file under `platforms/mist/tools/` vs. one-module-per-category elsewhere). Re-organizing those 35 files into ~15 category modules is planned for a later release — not in this hotfix so that Seth and Zach get the dispatch fix immediately.

### Users affected

Anyone on `v2.0.0.0` with `MCP_TOOL_MODE=dynamic` (the default) who tried to use Mist tools. Workaround until `v2.0.0.1` rolls out: set `MCP_TOOL_MODE=static` in `docker-compose.yml` to restore direct tool visibility (v1.x-style surface — every underlying tool advertised individually, avoiding the meta-tool wrapper path).

Closes [#179](https://github.com/nowireless4u/hpe-networking-mcp/issues/179).

---

## [2.0.0.0] - 2026-04-23

**Major release.** Default tool-exposure mode flipped from `static` to `dynamic`. The exposed tool surface drops from 261 tools to 18 without removing any underlying functionality — every platform tool is still here and still invokable, but now discovered on demand via three meta-tools per platform. Resolves the context-budget problem on 32K-context local LLMs (Zach Jennings' original report, [#163](https://github.com/nowireless4u/hpe-networking-mcp/issues/163)).

### Breaking changes

- **Default mode flip.** `MCP_TOOL_MODE=dynamic` is now the server default (was `static`). Set `MCP_TOOL_MODE=static` in `docker-compose.yml` under `environment:` to restore v1.x behavior. See [docs/MIGRATING_TO_V2.md](docs/MIGRATING_TO_V2.md).
- **GreenLake endpoint-dispatch meta-tools renamed.** v1.x exposed `greenlake_list_endpoints`, `greenlake_get_endpoint_schema`, `greenlake_invoke_endpoint` (REST-path-based). v2.0 replaces them with `greenlake_list_tools`, `greenlake_get_tool_schema`, `greenlake_invoke_tool` (tool-name-based, matching every other platform). AI agents that hard-coded the old names get `tool not found`.
- **`apstra_health` removed.** Use `health(platform="apstra")`.
- **`apstra_formatting_guidelines` removed.** Content migrated into `INSTRUCTIONS.md` under the Juniper Apstra section; the AI sees it at session init without a dedicated tool call. Per-response helpers (`get_base_guidelines`, `get_device_guidelines`, etc.) still fire inside Apstra tool bodies.
- **`ServerConfig.greenlake_tool_mode` property removed.** Phase 0 added the `tool_mode` field and kept `greenlake_tool_mode` as a deprecated read-only alias. v2.0 removes the alias. External code (if any) that referenced `config.greenlake_tool_mode` must switch to `config.tool_mode` — same semantics, shorter name. The `MCP_TOOL_MODE` env var is unchanged.

### Measured impact

Token count of the `tools` array passed to the LLM (cl100k_base tokenizer, all 5 platforms configured):

| Mode | Tools exposed | Tool-schema tokens | Fits 32K context? |
|---|---|---|---|
| `MCP_TOOL_MODE=static` | 267 | **64,036** | ❌ impossible |
| `MCP_TOOL_MODE=dynamic` (default) | 18 | **2,910** | ✅ 29K free for conversation + tool results |

**95.5% reduction.**

### Added — v2.0 infrastructure

Shared infrastructure now powers dynamic mode across every platform:

- `platforms/_common/tool_registry.py` — `ToolSpec` dataclass and `REGISTRIES` dict populated by each platform's `@tool(...)` shim; `is_tool_enabled()` gating honors `ENABLE_*_WRITE_TOOLS` flags.
- `platforms/_common/meta_tools.py` — `build_meta_tools(platform, mcp)` factory registers the three per-platform meta-tools.
- `platforms/health.py` — cross-platform `health` tool replacing `apstra_health` / `clearpass_test_connection`. Accepts `platform: str | list[str] | None` following the filter rule from v1.0.0.1. Per-platform probe helpers (`_probe_mist`, `_probe_central`, `_probe_greenlake`, `_probe_clearpass`, `_probe_apstra`) report `ok` / `degraded` / `unavailable` with platform-specific detail. `server.py:lifespan` runs these same probes at startup so startup logs and runtime `health` output come from a single source of truth.
- `middleware/elicitation.py` — `confirm_write(ctx, message)` helper consolidating 17 duplicated `_confirm_*` helpers from Apstra and ClearPass write tools ([#148](https://github.com/nowireless4u/hpe-networking-mcp/issues/148)).

### Changed — per-platform migrations

Each platform's `_registry.py` rewrote from a module-level `mcp` holder into a `tool()` decorator shim: delegates to `mcp.tool(...)`, adds the `dynamic_managed` tag so `Visibility` can hide individual tools in dynamic mode, and populates `REGISTRIES[platform]` so the meta-tools can dispatch by name.

- **Apstra** ([#158](https://github.com/nowireless4u/hpe-networking-mcp/issues/158)) — 19 tools swapped from `@mcp.tool(...)` to `@tool(...)`. Pilot platform.
- **Mist** ([#159](https://github.com/nowireless4u/hpe-networking-mcp/issues/159)) — 35 tools across 30 files. Prompts (`@mcp.prompt`) unaffected — prompts are a different MCP primitive than tools.
- **Central** ([#160](https://github.com/nowireless4u/hpe-networking-mcp/issues/160)) — 73 tools across 24 files. `prompts.py` unchanged (12 guided prompts). Dropped the "skip configuration when write disabled" branch in `central/__init__.py` — Visibility + `is_tool_enabled` handle gating uniformly now.
- **ClearPass** ([#161](https://github.com/nowireless4u/hpe-networking-mcp/issues/161)) — 127 tools across 31 files. 15 write-tool files replaced inline `_confirm_write` helpers with the shared `confirm_write()` middleware call (finishing [#148](https://github.com/nowireless4u/hpe-networking-mcp/issues/148)).
- **GreenLake** ([#162](https://github.com/nowireless4u/hpe-networking-mcp/issues/162)) — 10 tools across 5 service modules. Replaced the bespoke endpoint-dispatch dynamic surface from v0.9.x (the old `platforms/greenlake/tools/dynamic.py` with its 1100-line REST-URL router) with the standard tool-name-dispatch pattern.

### Removed

- `platforms/greenlake/tools/dynamic.py` (1100-line REST-endpoint-dispatch module).
- `apstra_health`, `apstra_formatting_guidelines` tools.
- `clearpass_test_connection` tool — the v1.x-era single-platform reachability probe. Use `health(platform="clearpass")`. MIGRATING_TO_V2.md had promised this was removed; the tool file still existed through Phase 6 and is now actually gone. ClearPass underlying-tool count drops 127 → 126.
- `ServerConfig.greenlake_tool_mode` property alias.
- `HANDOFF.md`, `TASKS.md` (stale internal docs, [#150](https://github.com/nowireless4u/hpe-networking-mcp/issues/150)).
- `factory-boy` dev dependency (unused, [#149](https://github.com/nowireless4u/hpe-networking-mcp/issues/149)).

### Tests

46 new infrastructure tests in `test_tool_registry.py`, `test_meta_tools.py`, `test_health.py`; five per-platform integration-style test modules (`test_apstra_dynamic_mode.py`, `test_mist_dynamic_mode.py`, `test_central_dynamic_mode.py`, `test_clearpass_dynamic_mode.py`, `test_greenlake_dynamic_mode.py`) each with 6 tests asserting registry population, category derivation, write-tool tagging, and absence of removed tools. Total suite: 421 tests passing.

### Pre-release polish (landed during v2.0 user-testing, bundled into the 2.0.0.0 tag)

- **`site_health_check` now accepts a `platform` filter** — optional `str | list[str] | None` parameter scopes the cross-platform aggregator to one platform when the user's question explicitly names one (e.g. "how is site X doing in Central" → `site_health_check(site_name="X", platform="central")`). Default (null/omit) preserves the existing every-platform behavior. Apstra and GreenLake are not valid values — they don't have site-scoped telemetry. Follows the `str | list[str] | None` filter convention established in v1.0.0.1 (#146).
- **`INSTRUCTIONS.md` scope rule rewritten as a positive parameterized table.** The previous "do NOT call `site_health_check` when a platform is named" phrasing didn't hold against AI bias toward the cross-platform aggregator in live testing. Replaced with an explicit decision table that maps user phrasing directly to the parameterized call. Verified: the AI now correctly stays in one platform when the user scopes their question.
- **Fixed silent config-loader logs.** Moved `setup_logging()` in `__main__.py` to run *before* `load_config()`. Previously the module-level `logger.remove()` in `utils/logging.py` left loguru with zero handlers during config load, so `Loading secrets from …`, `Mist: credentials loaded …`, `Enabled platforms: …`, `Tool mode: dynamic`, and `Apstra: disabled (missing secrets: …)` were all silently dropped. Now they reach stderr / `docker compose logs` as expected — useful for diagnosing secret-file / platform-enable problems at startup.
- **README secret-file guidance rewritten.** The v1.x README said "only create files for the platforms you use" and "the server auto-disables platforms with missing secret files" — both true at the app layer but misleading given Docker Compose's bind-mount model, which fails the container before the app runs if a declared secret file is absent. New guidance states the bind-mount reality up front and adds a dedicated "Disable platforms you don't use" section showing a `docker-compose.override.yml` pattern with `!reset` directives. The troubleshooting section gains a new "Container exits immediately with invalid mount config" entry pointing at the same fix. No code changes — docs only. Closes the long-standing confusion around the `apstra.example.com` placeholder problem discovered during v2.0 live testing.
- **New `docker-compose.override.yml.example` template.** Ready-to-copy override file with worked examples for the three most common tailoring needs: dropping unused platforms (via `!reset` on the service-level secrets list and the top-level secrets block), flipping per-platform write-tool flags, and changing the exposed host port. README section "3. Disable platforms you don't use" now points users at `cp docker-compose.override.yml.example docker-compose.override.yml` instead of making them hand-copy a code snippet. Lowers the Docker-Compose-expertise bar for the opt-out pattern.

### Boot verification

- `MCP_TOOL_MODE=dynamic` + all 5 platforms → **18 exposed tools** (15 meta-tools + 3 cross-platform static).
- `MCP_TOOL_MODE=static` + all 5 platforms → 267 tools visible (every individual per-platform tool).

Closes [#149](https://github.com/nowireless4u/hpe-networking-mcp/issues/149), [#150](https://github.com/nowireless4u/hpe-networking-mcp/issues/150), [#151](https://github.com/nowireless4u/hpe-networking-mcp/issues/151), [#152](https://github.com/nowireless4u/hpe-networking-mcp/issues/152), [#157](https://github.com/nowireless4u/hpe-networking-mcp/issues/157), [#158](https://github.com/nowireless4u/hpe-networking-mcp/issues/158), [#159](https://github.com/nowireless4u/hpe-networking-mcp/issues/159), [#160](https://github.com/nowireless4u/hpe-networking-mcp/issues/160), [#161](https://github.com/nowireless4u/hpe-networking-mcp/issues/161), [#162](https://github.com/nowireless4u/hpe-networking-mcp/issues/162), [#163](https://github.com/nowireless4u/hpe-networking-mcp/issues/163), [#164](https://github.com/nowireless4u/hpe-networking-mcp/issues/164).

---

### Historical phase entries (superseded by the 2.0.0.0 summary above)

The sections below were written incrementally as each phase merged — they're kept for history but the single 2.0.0.0 entry above is the authoritative release note.

### Added — GreenLake unification on the shared dynamic-mode pattern (#162)

All five platforms now run on the same shared tool-registry +
meta-tool infrastructure. GreenLake previously had its own
dynamic-mode implementation with three REST-endpoint-dispatch
meta-tools (`greenlake_list_endpoints`, `greenlake_get_endpoint_schema`,
`greenlake_invoke_endpoint`). Phase 4 replaces that bespoke mechanism
with the standard tool-name-dispatch pattern used by every other
platform.

- `platforms/greenlake/_registry.py` rewritten as a `tool()` decorator
  shim matching the other four platforms.
- All 5 GreenLake tool modules swapped from `@mcp.tool(...)` to
  `@tool(...)`.
- `platforms/greenlake/tools/__init__.py` — now exposes a `TOOLS` dict
  mapping category -> tool names (same shape as every other platform).
  Mode-branching `register_all` function removed.
- `platforms/greenlake/__init__.py` — uses the shared pattern: always
  imports every tool file, calls `build_meta_tools("greenlake", mcp)`
  when `tool_mode == "dynamic"`, logs consistently with the other
  platforms. Old `config.greenlake_tool_mode` read-site removed — the
  deprecated property alias still works but is no longer referenced
  anywhere in the codebase.

### Removed (v2.0 clean break)

- `platforms/greenlake/tools/dynamic.py` — 1100-line endpoint-dispatch
  meta-tools module replaced by the 4-line call to `build_meta_tools`.
- Old meta-tool names (`greenlake_list_endpoints`,
  `greenlake_get_endpoint_schema`, `greenlake_invoke_endpoint`) are
  **gone entirely**. Under `MCP_TOOL_MODE=dynamic` GreenLake now
  exposes `greenlake_list_tools`, `greenlake_get_tool_schema`,
  `greenlake_invoke_tool` — matching every other platform's naming
  convention. AI agents that hardcoded the old endpoint names against
  v1.x will need to update to the new names.

### Tests
- 6 new integration-style tests in `test_greenlake_dynamic_mode.py`
  (includes a regression check that the legacy endpoint-dispatch tool
  names are absent from the registry). Total suite: 421/421 passing.

### Boot verification
- `MCP_TOOL_MODE=static` + GreenLake configured → 10 `greenlake_*`
  tools visible.
- `MCP_TOOL_MODE=dynamic` + all five platforms configured → **15
  meta-tools total** (3 per platform × 5 platforms) + cross-platform
  `health` tool. Every underlying tool hidden.

### Summary — Phase 0-4 results

Every per-platform migration is complete. In dynamic mode the server
now exposes exactly:
- 15 per-platform meta-tools (3 each for Apstra, Mist, Central,
  ClearPass, GreenLake)
- 3 cross-platform static tools (`health`, `site_health_check`,
  `manage_wlan_profile`)
- **18 exposed tools total** (down from 261 in v1.x)

Remaining before the v2.0.0.0 cut:
- Phase 5 (#163) — dev/test validation against a 32K-context local
  model
- Phase 6 (#164) — flip the default to `MCP_TOOL_MODE=dynamic`, bump
  to v2.0.0.0, tag, release

### Phase 3 snapshot — ClearPass migration (#161) + confirm_write consolidation complete (#148)

### Added — ClearPass dynamic-mode migration (#161) + `confirm_write` consolidation complete (#148)

Fourth platform onto the dynamic-mode infrastructure. ClearPass is the
largest single platform by tool count (127 across 31 files). With
`MCP_TOOL_MODE=dynamic`, ClearPass exposes exactly three meta-tools
(`clearpass_list_tools`, `clearpass_get_tool_schema`,
`clearpass_invoke_tool`) and hides the 127 underlying tools via the
shared `Visibility(dynamic_managed)` transform. Static mode unchanged.

- `platforms/clearpass/_registry.py` rewritten as a `tool()` decorator
  shim mirroring Apstra / Mist / Central.
- All 31 ClearPass tool files under `platforms/clearpass/tools/*.py`
  swapped from `@mcp.tool(...)` to `@tool(...)`.
- `platforms/clearpass/__init__.py` — always imports every category;
  calls `build_meta_tools("clearpass", mcp)` when
  `tool_mode == "dynamic"`. Dropped the `WRITE_CATEGORIES` skip logic
  since Visibility + `is_tool_enabled` now handle gating uniformly.

### Changed — finishes `#148` confirm_write consolidation

All 15 ClearPass write-tool files (the 14 `_confirm_write` helpers plus
one inline copy in `manage_endpoints.py`) replaced with calls to the
shared `middleware.elicitation.confirm_write()` helper. The local
helper names are preserved as thin wrappers so existing call sites
don't change; the actual elicitation/decline/cancel decision logic
lives in the middleware. Same treatment Apstra got in Phase 0 PR B —
**#148 is now fully closed** (Apstra + ClearPass both consolidated).

### Tests
- 6 new integration-style tests in `test_clearpass_dynamic_mode.py`.
  Total suite: 415/415 passing.

### Boot verification
- `MCP_TOOL_MODE=static` + ClearPass configured → 127 `clearpass_*`
  tools visible.
- `MCP_TOOL_MODE=dynamic` + all four migrated platforms configured →
  12 meta-tools total (3 per platform × 4 platforms) + cross-platform
  `health` tool. Every underlying tool hidden.

### Phase 2 snapshot — Central dynamic-mode migration (#160)

### Added — Central dynamic-mode migration (#160)

Third platform onto the dynamic-mode infrastructure. With
`MCP_TOOL_MODE=dynamic`, Central exposes exactly three meta-tools
(`central_list_tools`, `central_get_tool_schema`, `central_invoke_tool`)
and hides the 73 underlying Central tools via the shared
`Visibility(dynamic_managed)` transform. Static mode is unchanged.

- `platforms/central/_registry.py` rewritten as a `tool()` decorator
  shim mirroring Apstra's and Mist's.
- All 24 Central tool files under `platforms/central/tools/*.py`
  swapped from `@mcp.tool(...)` to `@tool(...)`. The `prompts.py`
  module (12 guided prompts) is unchanged — prompts are a different
  MCP primitive and aren't part of the dynamic-mode meta-tool surface.
- `platforms/central/__init__.py` — always imports every category so
  the registry is complete regardless of `ENABLE_CENTRAL_WRITE_TOOLS`;
  calls `build_meta_tools("central", mcp)` when
  `tool_mode == "dynamic"`. Dropped the "skip configuration when write
  disabled" branch — Visibility + `is_tool_enabled` handle gating
  uniformly now.

### Tests
- 6 new integration-style tests in `test_central_dynamic_mode.py`.
  Total suite: 409/409 passing.

### Boot verification
- `MCP_TOOL_MODE=static` + Central configured → 73 `central_*` tools
  visible.
- `MCP_TOOL_MODE=dynamic` + Central + Mist + Apstra configured → 3
  meta-tools per migrated platform + cross-platform `health` tool;
  every underlying tool hidden by Visibility.

### Phase 1 snapshot — Mist dynamic-mode migration (#159)

### Added — Mist dynamic-mode migration (#159)

Second platform onto the dynamic-mode infrastructure. With
`MCP_TOOL_MODE=dynamic`, Mist exposes exactly three meta-tools
(`mist_list_tools`, `mist_get_tool_schema`, `mist_invoke_tool`) and hides
the 35 underlying Mist tools via the shared `Visibility(dynamic_managed)`
transform. Static mode is unchanged.

- `platforms/mist/_registry.py` rewritten as a `tool()` decorator shim
  mirroring Apstra's — delegates to `mcp.tool(...)`, adds the
  `dynamic_managed` tag, and records into `REGISTRIES["mist"]`.
- All 35 Mist tool files under `platforms/mist/tools/*.py` swapped from
  `@mcp.tool(...)` to `@tool(...)` (import path updated to match).
- `platforms/mist/__init__.py` — always imports every tool file so the
  registry is complete regardless of `ENABLE_MIST_WRITE_TOOLS`; calls
  `build_meta_tools("mist", mcp)` when `tool_mode == "dynamic"`.
- Mist prompts (`@mcp.prompt` in `prompts.py`) are unaffected — prompts
  are a different MCP primitive than tools and aren't part of the
  dynamic-mode meta-tool surface.

### Tests
- 6 new integration-style tests in `test_mist_dynamic_mode.py`. Total
  suite: 403/403 passing.

### Boot verification
- `MCP_TOOL_MODE=static` + Mist configured → 35 `mist_*` tools visible.
- `MCP_TOOL_MODE=dynamic` + Mist + Apstra configured → 3 Mist meta-tools
  + 3 Apstra meta-tools + cross-platform `health` tool; every underlying
  tool hidden.

### Phase 0 snapshot — shared infrastructure + Apstra pilot (#158)

### Added — Apstra dynamic-mode pilot (#158 part B)

First platform migrated onto the dynamic-mode infrastructure. With
`MCP_TOOL_MODE=dynamic`, Apstra exposes exactly three meta-tools
(`apstra_list_tools`, `apstra_get_tool_schema`, `apstra_invoke_tool`) and
hides the 19 underlying Apstra tools via a `Visibility` transform on the
`dynamic_managed` tag. Static mode is unchanged.

- `platforms/apstra/_registry.py` replaces the module-level `mcp` holder
  with a `tool()` decorator shim that (1) delegates to
  `mcp.tool(...)` exactly as before, (2) adds the `dynamic_managed` tag
  so `Visibility` can hide individual tools in dynamic mode, and
  (3) populates `REGISTRIES["apstra"]` so the meta-tools can dispatch by
  name.
- All 8 Apstra tool files under `platforms/apstra/tools/*.py` now
  decorate with `@tool(...)` (mechanical swap from `@mcp.tool(...)`).
- `platforms/apstra/__init__.py` wires the meta-tools onto FastMCP when
  `config.tool_mode == "dynamic"`.
- `server.py` installs `Visibility(False, tags={"dynamic_managed"})`
  when `tool_mode == "dynamic"`, so every migrated platform's individual
  tools become invisible in favor of its meta-tools.

### Removed

- `apstra_health` — use `health(platform="apstra")` (cross-platform, added
  in Phase 0 PR A).
- `apstra_formatting_guidelines` — content migrated into
  `src/hpe_networking_mcp/INSTRUCTIONS.md` under the Juniper Apstra section;
  the AI still sees the full guidance at session init without a dedicated
  tool call. Per-response `get_base_guidelines`, `get_device_guidelines`,
  etc. helpers still fire inside Apstra tool bodies.

### Changed

- Apstra write tools (`manage_blueprints.py`, `manage_networks.py`,
  `manage_connectivity.py`) now call the shared `confirm_write(ctx, message)`
  helper from `middleware/elicitation.py` rather than three identical local
  `_confirm()` copies (#148 — Apstra's share of the consolidation; ClearPass
  gets the same treatment in Phase 3).
- `server.py:lifespan` now runs the `platforms/health.py` probe helpers at
  startup via a minimal shim (`_LifespanProbeCtx`) that exposes the
  in-progress context dict as `lifespan_context`. One source of truth for
  "is this platform reachable" — the startup log line and the runtime
  `health` tool output are now generated from the same code path.

### Tests
- 6 new integration-style tests in `test_apstra_dynamic_mode.py` assert that
  every Apstra tool registers into `REGISTRIES["apstra"]` with the right
  category and tags, and that `apstra_health` / `apstra_formatting_guidelines`
  are gone. Total suite: 397/397 passing.

### Boot verification
- `MCP_TOOL_MODE=static` + Apstra configured → 19 `apstra_*` tools visible;
  `apstra_health` and `apstra_formatting_guidelines` absent.
- `MCP_TOOL_MODE=dynamic` + Apstra configured → 3 meta-tools
  (`apstra_list_tools`, `apstra_get_tool_schema`, `apstra_invoke_tool`)
  plus the cross-platform `health` tool; every underlying Apstra tool
  hidden.

### Added — shared tool-registry and meta-tool infrastructure (#158 part A)

Groundwork for the v2.0.0.0 dynamic-tool-mode default flip. No user-visible
changes in this release: individual platform tool surfaces are unchanged and
`MCP_TOOL_MODE=static` remains the default. The infrastructure lands first so
each per-platform migration PR (Apstra, Mist, Central, ClearPass, GreenLake)
is a small, mechanical swap.

- `src/hpe_networking_mcp/platforms/_common/` package:
  - `tool_registry.py` — `ToolSpec` dataclass and `REGISTRIES` dict populated
    by each platform's `@tool(...)` shim (PR B onward). Includes
    `is_tool_enabled()` gating honoring `ENABLE_*_WRITE_TOOLS` flags.
  - `meta_tools.py` — `build_meta_tools(platform, mcp)` factory that
    registers three meta-tools per platform: `<platform>_list_tools`,
    `<platform>_get_tool_schema`, `<platform>_invoke_tool`.
- `src/hpe_networking_mcp/platforms/health.py` — new cross-platform `health`
  tool replacing the per-platform `apstra_health` and
  `clearpass_test_connection`. Accepts `platform: str | list[str] | None`
  following the filter-parameter rule from v1.0.0.1. Per-platform probe
  helpers (`_probe_mist`, `_probe_central`, `_probe_greenlake`,
  `_probe_clearpass`, `_probe_apstra`) report `ok` / `degraded` /
  `unavailable` with platform-specific detail. The existing
  `apstra_health` and `clearpass_test_connection` tools remain in place in
  this release; they are removed in Phase 0 PR B and Phase 3 respectively.
- `src/hpe_networking_mcp/middleware/elicitation.py` — `confirm_write(ctx, message)`
  helper consolidating the 17 duplicated `_confirm` helpers from individual
  write tool files (#148). Write tools convert to it in subsequent phases.

### Changed

- `ServerConfig.greenlake_tool_mode` is now a read-only property aliasing
  `ServerConfig.tool_mode` (#151). Internal field renamed; `MCP_TOOL_MODE`
  env-var name unchanged. Alias slated for removal in v2.1.

### Tests
- 46 new unit tests (`test_tool_registry.py`, `test_meta_tools.py`,
  `test_health.py`). Total suite: 391/391 passing.

## [v1.1.0.0] - 2026-04-22

### Added — Mist/Central filter-parameter consistency (#156)

Eight filter parameters across five tools now accept either a single
string or a list of strings. The rule established in v1.0.0.1 — filter
parameters accept `str | list[str] | None`, named in the singular —
applied across Mist and Central. Identity parameters (`blueprint_id`,
`device_id`, etc.) and required-single-item parameters (`vn_name`,
`ssid`) stay scalar.

**Central** (`platforms/central/tools/`):
- `central_get_devices` — `device_name`, `serial_number`, `model`
- `central_get_aps` — `serial_number`, `device_name`, `model`, `firmware_version`

**Mist** (`platforms/mist/tools/`):
- `mist_search_device` — `model`, `version`
- `mist_list_upgrades` — `model`

Per-platform `as_comma_separated()` helper in `central/utils.py` and
new `mist/utils.py` normalizes both shapes to the comma-separated form
Central's OData helpers and mistapi expect. When Phase 0 of v2.0
introduces `platforms/_common/`, the two helpers collapse into one.

The `central_get_aps` tool was also refactored internally to use the
shared `build_odata_filter` + `FilterField` pattern already used by
`central_get_devices`. Multi-value filters now correctly emit OData
`in (...)` clauses instead of broken `eq '...comma...'` equality.

New test file `tests/unit/test_filter_value_helpers.py` parametrizes
eight cases against both the Central and Mist helpers so they stay
behaviour-identical.

**Minor version bump** (1.0.0.3 → 1.1.0.0) because the signatures of
eight public tool parameters changed — backward-compatible (old `str`
form still works) but not a pure patch fix.

## [v1.0.0.3] - 2026-04-22

### Fixed — silent PUT-clobber on Central configuration updates (#155)

Audited every `central_manage_*` write tool for the silent-clobber
pattern that v0.9.2.2 fixed in `central_manage_wlan_profile`. Three
tools shared the same bug via a common helper:

- `central_manage_site`
- `central_manage_site_collection`
- `central_manage_device_group`

All three called `_execute_config_action` in
`platforms/central/tools/configuration.py`, which hard-coded `PUT`
for updates. Central treats `PUT` as full-resource replacement, so
partial-update payloads silently dropped every field not included.
Exact same class of bug Zach reported in #141, same fix shape as PR
#142.

Updates now issue `PATCH` by default (Central merges the payload
server-side, preserving untouched fields). All three tools gain a
`replace_existing: bool = False` parameter that opts back into the
old `PUT` behavior for callers deliberately sending a full-resource
replacement. The elicitation prompt now warns when
`replace_existing=True` is in play.

Ten other `central_manage_*` tools already used `PATCH` via shared
helpers and were not affected.

New unit test file `tests/unit/test_central_configuration.py` covers
method selection for create / update-default / update-replace-existing /
delete and the resource-id validation paths.

### Changed — test fixture scope (internal)

The `_install_registry_stubs()` helper introduced in v1.0.0.2
(`tests/integration/conftest.py`) was lifted up to `tests/conftest.py`
so both unit and integration tests can import from tool modules
without tripping the `_registry.mcp is None` decorator error.
`tests/integration/conftest.py` keeps its integration-specific
fixtures. No behavior change at runtime.

## [v1.0.0.2] - 2026-04-22

### Fixed — test/dev infrastructure (pre-gate for v2.0 work)

- **Integration-test collection failure (#153)** — `tests/integration/test_ap_monitoring_live.py` and `test_wlans_live.py` import tool modules directly, and those modules call `@mcp.tool(...)` at import time against a `_registry.mcp` that is `None` outside of a running server. Collection aborted with `AttributeError: 'NoneType' object has no attribute 'tool'`. `tests/integration/conftest.py` now installs a `MagicMock` on each platform's `_registry.mcp` at conftest load, so tool modules import cleanly for collection. Unit tests unaffected (they don't import from tool modules). Test collection now discovers 353 tests (previously short-circuited at 322).
- **Dev compose read-only src mount (#154)** — `docker-compose.dev.yml` mounted `./src` as read-only, which broke `uv run ruff format` inside the container. Flipped to read-write in the dev overlay only; production `docker-compose.yml` does not mount `./src` at all, so end users are unaffected. Saves a per-PR papercut.

No user-facing code changes. Published image is functionally identical to v1.0.0.1.

## [v1.0.0.1] - 2026-04-22

### Fixed — `central_get_site_health` parameter name mismatch (#146)
- Reported by Zach Jennings. The tool used `site_names: list[str]`
  (plural) while every other single-site Central tool and prompt uses
  `site_name` (singular). Local LLMs pattern-matching against the
  Central surface consistently guessed `site_name=...` and hit
  "must NOT have additional properties" from the FastMCP JSON-schema
  validator — a framework-level error that told the model nothing about
  which parameter name was actually correct, causing reasoning loops
  and no successful tool call.
- Signature is now `site_name: str | list[str] | None = None`. Accepts
  either a single name string (`site_name="Owls Nest"`) or a list
  (`site_name=["A", "B"]`). Batch callers keep working; single-site
  callers match peer tools.
- Normalization extracted into `_normalize_site_name_filter` helper with
  unit tests covering str, list, tuple, empty-list, and None inputs.
- Updated docstrings, guided prompt bodies, INSTRUCTIONS.md, and
  docs/TOOLS.md to reference the new shape.

## [v1.0.0.0] - 2026-04-22

### Added — Juniper Apstra platform (21 tools), v1.0 milestone

First major release. The server now unifies all five platforms
(Juniper Mist, Aruba Central, HPE GreenLake, Aruba ClearPass, and
Juniper Apstra) into a single Docker-deployable MCP endpoint.

- New `apstra_*` tool namespace covering datacenter blueprint
  management, virtual networks, connectivity templates, routing zones,
  remote EVPN gateways, anomalies, BGP sessions, and deployment.
  14 read-only tools + 7 write tools.
- Docker secrets: `apstra_server`, `apstra_port` (optional, default 443),
  `apstra_username`, `apstra_password`, `apstra_verify_ssl` (optional,
  default `true`).
- `verify_ssl` defaults to **true**. The standalone Apstra MCP server
  it is ported from hardcoded `verify=False` on every HTTPS call;
  operators must now opt out explicitly.
- Login is sent with an `httpx` JSON body (`json={...}`) rather than
  f-string–interpolated payloads. The standalone server was vulnerable
  to injection if a password contained a `"` character.
- Async `httpx.AsyncClient` with in-memory token cache, `asyncio.Lock`
  serializing login, automatic refresh-and-retry on `HTTP 401`, split
  30s request / 10s authentication timeouts.
- Write tools (deploy, delete, create VN/gateway/blueprint, CT-policy
  apply) require user confirmation via the existing elicitation
  middleware and are gated behind `ENABLE_APSTRA_WRITE_TOOLS=true`.
- Tool renaming: the terse source names (`get_bp`, `get_rz`,
  `create_vn`) are now the descriptive `apstra_get_blueprints`,
  `apstra_get_routing_zones`, `apstra_create_virtual_network`, and so
  on, matching the established `mist_*`/`central_*`/`clearpass_*` style.
- The standalone `-f/--config-file`, `-t/--transport`, `-H/--host`,
  `-p/--port` CLI flags and the `apstra_config.json` plaintext
  credentials file are retired. Apstra now uses the unified server's
  transport wiring and Docker secrets at `/run/secrets/`.
- Legacy config field aliases (`aos_server`, `aos_port`) and the
  combined `"host:port"` server-string form are not supported. Use
  the canonical `apstra_server` and `apstra_port` secrets.

## [v0.9.2.2] - 2026-04-21

### Fixed — `central_manage_wlan_profile` silently clobbered entire profiles on update (#141)
- Reported by Zach Jennings. An update with a partial payload (e.g.
  `{"dtim-period": 2}`) was issued to Central as a `PUT`, which is
  full-resource replacement — every field missing from the payload was
  dropped. Security, VLAN, QoS, and client settings on the affected
  profiles were lost silently.
- `action_type="update"` now issues `PATCH /network-config/v1alpha1/wlan-ssids/{ssid}`
  and Central merges the payload with the existing profile server-side.
  Callers pass only the fields they want to change; untouched fields are
  preserved. One round trip, atomic on the server, uses Central's own
  merge semantics.
- Added `replace_existing: bool = False` parameter. When True, the tool
  falls back to the old `PUT` full-replacement behavior. The payload
  description and elicitation message make the consequences explicit.
- Elicitation prompt for partial updates now fetches the current profile
  and shows a per-field before → after diff, so the user sees exactly
  what will change before approving. Failures in the diff lookup are
  non-blocking — the write proceeds with a generic message if the GET
  fails.

## [v0.9.2.1] - 2026-04-20

### Changed
- **`central_recommend_firmware` now reads LSR/SSR classification directly
  from the API.** The hand-maintained `AOS10_AP_GW_RELEASE_TYPES` mapping
  has been removed. The tool now uses the `firmwareClassification` field
  returned by `/network-services/v1/firmware-details` (values: `"LSR"`,
  `"SSR"`, or empty for unclassified devices such as AOS 8).
- For SSR devices, the "next LSR train" target is now mined live from the
  same response: the tool scans every LSR-classified device in the fleet
  (across both `firmwareVersion` and `recommendedVersion`) and picks the
  highest version seen per device type. No more hardcoded train list to
  keep in sync with Aruba's release docs.
- Report schema: `lsr_train_reference` removed; replaced with
  `discovered_lsr_targets` showing the mined LSR targets per device type.
  Count field `on_aos8` and `unknown_train` collapsed into `unclassified`.
  `release_type` field now only emits `LSR`, `SSR`, or `UNCLASSIFIED`
  (the old `AOS8` and `UNKNOWN` buckets fold into the last).
- If no LSR device of a given type exists in the fleet, SSR devices of
  that type fall back to Central's recommendation with a note.

## [v0.9.2.0] - 2026-04-20

### Added — Central firmware recommendation tool
- New `central_recommend_firmware` tool that reads Central's
  `/network-services/v1/firmware-details` endpoint and applies an
  LSR-preferred upgrade policy on top of Central's built-in
  `recommendedVersion`.
- Classifies each AP or Gateway's current AOS 10 train as LSR or SSR using
  a hand-maintained mapping (`AOS10_AP_GW_RELEASE_TYPES`, currently
  covering 10.3–10.8). Switches and AOS 8 devices are passed through with
  Central's recommendation — the LSR/SSR concept doesn't apply to them.
- Output includes per-device current train, release type, current version,
  Central's recommended version, our recommended version or next LSR
  train, a rationale string, and a fleet-level count breakdown (on LSR,
  on SSR, on AOS 8, unknown train, needs action).
- Filters by `serial_number`, `device_type`, `site_id`, or `site_name`
  (server-side OData). Defaults to omitting devices that are already on
  Central's recommended version to keep the report actionable.
- Update `AOS10_AP_GW_RELEASE_TYPES` in
  `src/hpe_networking_mcp/platforms/central/tools/firmware.py` when Aruba
  designates a new LSR train.

## [v0.9.1.1] - 2026-04-17

### Fixed
- **`site_health_check` ClearPass matching missed gateway VIPs and subnet NADs.**
  The initial implementation matched site device IPs against ClearPass NAD
  `ip_address` fields using exact-string equality, so any NAD defined as a
  CIDR (`10.1.1.0/24`) or dashed range (`10.1.1.1-10.1.1.50`) was skipped
  even when site devices sat inside it. And because session `nasipaddress`
  fields point at the device that actually sourced the RADIUS request —
  usually a gateway cluster VIP in tunneled Aruba deployments — sessions
  coming from a VIP that wasn't in the Mist/Central device inventory were
  invisible to the aggregator.
- NADs are now parsed into IP/CIDR/range matchers using Python's
  `ipaddress` module. A NAD is treated as a "site NAD" if its address
  space *contains* any Mist/Central device IP at the site. Sessions are
  pulled time-bounded and filtered client-side by testing whether each
  session's `nasipaddress` falls inside any site NAD's address space —
  catching VIP-sourced sessions even when the VIP itself isn't in any
  device inventory. System events are counted similarly, filtered by
  description mentions of matched NAD names.
- `ClearPassSummary` gained `matched_nad_names: list[str]` so the report
  shows which NADs were matched (first 10).

## [v0.9.1.0] - 2026-04-17

### Added — Cross-Platform Site Health Check
- New `site_health_check` tool that aggregates site health across every
  enabled platform in a single call. Resolves the site on Mist and Central,
  pulls stats/alerts/alarms in parallel, and — when ClearPass is configured —
  matches the site's network access devices by IP to count active sessions
  and recent auth failures. Returns a compact report with overall status
  (healthy/degraded/critical), top alerts, and concrete next-step tool
  recommendations. Replaces ~8–12 separate tool calls, cutting response
  tokens by an order of magnitude for common site-health queries.
- Registered when at least Mist or Central is enabled; ClearPass is additive.

## [v0.9.0.2] - 2026-04-17

### Fixed
- **ClearPass tools returning 403 after ~8 hours** (#130) — OAuth2 access tokens
  issued via `client_credentials` expire after 8 hours, but the server cached the
  startup token indefinitely. After the token aged out every `clearpass_*` tool
  returned `403 Forbidden` even for Super Administrator clients. Replaced the
  single-shot cache with a pycentral-style reactive refresh: on any 401/403 the
  token is invalidated, a fresh one is fetched from `/oauth`, and the original
  request is replayed once. Implemented as a class-level patch on
  `ClearPassAPILogin._send_request` since pyclearpass methods bypass
  instance-level overrides.

## [v0.9.0.0] - 2026-04-16

### Added — Aruba ClearPass Platform
- Complete ClearPass Policy Manager integration using `pyclearpass` SDK with OAuth2 client credentials
- 127 new tools (55 read + 72 write) across 16 read modules and 15 write modules
- **Network Devices** — list, get, create, update, delete, clone, configure SNMP/RadSec/CLI/on-connect
- **Guest Management** — guest user CRUD, credential delivery (SMS/email), digital pass generation, sponsor workflows
- **Guest Configuration** — pass templates, print templates, web login pages, authentication and manager settings
- **Endpoints** — endpoint CRUD, device profiler fingerprinting
- **Session Control** — active session listing, disconnect (by session/username/MAC/IP/bulk), Change of Authorization (CoA)
- **Roles & Enforcement** — roles, role mappings, enforcement policies, enforcement profiles
- **Authentication** — authentication sources (LDAP/AD/RADIUS) and methods, with backup/filter/attribute configuration
- **Certificates** — trust list, client/server/service certificates, CSR generation, enable/disable server certs
- **Audit & Insight** — login audit, system events, endpoint insights (by MAC/IP/time), Insight alerts and reports with enable/disable/mute/run
- **Identities** — API clients, local users, static host lists, devices, deny-listed users
- **Policy Elements** — configuration services (enable/disable), posture policies, device groups, proxy targets, RADIUS/TACACS/application dictionaries
- **Server Configuration** — admin users/privileges, operator profiles, licenses (online/offline activation), cluster parameters, password policies, attributes, data filters, backup servers, messaging, SNMP trap receivers, policy manager zones
- **Local Configuration** — server access controls, Active Directory domain join/leave, cluster server management, service start/stop
- **Integrations** — extensions (start/stop/restart), syslog targets, syslog export filters, endpoint context servers
- **Utilities** — random password/MPSK generation, connection testing
- Docker secrets: `clearpass_server`, `clearpass_client_id`, `clearpass_client_secret`, `clearpass_verify_ssl` (optional)
- Write tools gated behind `ENABLE_CLEARPASS_WRITE_TOOLS` (default: disabled)
- Token caching — single OAuth2 token acquired at startup, shared across all tool calls
- SSL verification configurable via `clearpass_verify_ssl` secret (default: true)

### Changed
- Platform count: 3 → 4 (Mist, Central, GreenLake, ClearPass)
- Total tool count: ~117 → ~244

[v0.9.0.0]: https://github.com/nowireless4u/hpe-networking-mcp/releases/tag/v0.9.0.0

## [v0.8.3.0] - 2026-04-16

### Added — Central Roles & Policy Tools
- `central_get_net_groups` / `central_manage_net_group` — netdestinations (hosts, FQDNs, subnets, IP ranges, VLANs, ports)
- `central_get_net_services` / `central_manage_net_service` — protocol/port definitions
- `central_get_object_groups` / `central_manage_object_group` — named collections for ACL references
- `central_get_role_acls` / `central_manage_role_acl` — role-based access control lists
- `central_get_policies` / `central_manage_policy` — firewall policies (ordered rule sets)
- `central_get_policy_groups` / `central_manage_policy_group` — policy evaluation ordering
- `central_get_role_gpids` / `central_manage_role_gpid` — role to policy group ID mapping
- All write tools support shared (library) and local (scoped) objects via scope_id and device_function params
- Central tool count: 58 → 72

### Fixed
- Docker publish workflow now supports 4-digit versioning. Switched from `type=semver` (3-digit only) to `type=ref,event=tag` which uses the git tag as-is.

[v0.8.3.0]: https://github.com/nowireless4u/hpe-networking-mcp/releases/tag/v0.8.3.0

## [v0.8.2.0] - 2026-04-15

### Added — Central Role Management
- `central_get_roles` — read role configurations (VLAN, QoS, ACLs, bandwidth contracts, classification rules)
- `central_manage_role` — create, update, delete roles. Supports shared (library) and local (scoped) roles via `scope_id` and `device_function` params.
- Central tool count: 56 → 58

[v0.8.2.0]: https://github.com/nowireless4u/hpe-networking-mcp/releases/tag/v0.8.2.0

## [v0.8.1.0] - 2026-04-15

### Added — New Central Monitoring Tools
- `central_get_aps` — filtered AP listing with AP-specific filters (status, model, firmware, deployment type, cluster, site). Uses `MonitoringAPs.get_all_aps()` with OData filters.
- `central_get_ap_wlans` — get WLANs currently active on a specific AP by serial number. Uses `MonitoringAPs.get_ap_wlans()`. Supports optional `wlan_name` filter.
- `central_get_wlan_stats` — WLAN throughput trends (tx/rx time-series in bps) over a time window. Uses `GET /network-monitoring/v1/wlans/{name}/throughput-trends`. Supports predefined time ranges and custom RFC 3339 start/end.
- Central tool count: 53 → 56

### Added — Integration Test Scaffolding
- `tests/integration/conftest.py` — live API fixtures using Docker secrets. Creates real Central connection, skips gracefully if credentials missing.
- `tests/integration/test_ap_monitoring_live.py` — 6 live tests for AP listing, details, and WLAN-per-AP tools
- `tests/integration/test_wlans_live.py` — 5 live tests for WLAN listing, throughput stats, and time window filtering

### Added — Utility Functions
- `format_rfc3339()` — format datetime as RFC 3339 string with millisecond precision
- `resolve_time_window()` — resolve predefined time ranges or pass-through custom start/end times

### Changed — Versioning
- Moved to 4-digit versioning: `v0.MAJOR.MINOR.PATCH`

[v0.8.1.0]: https://github.com/nowireless4u/hpe-networking-mcp/releases/tag/v0.8.1.0

## [v0.8.7] - 2026-04-15

### Fixed
- Data rate mapping in manage_wlan workflow — AI was setting custom rates instead of using standard Central profiles (high-density, no-legacy, compatible). Workflow now includes exact rate values for both directions.
- Expanded all field mappings in workflow instructions to be fully explicit (RF bands, VLAN, roaming, EHT, ARP filter, isolation, performance fields).

## [v0.8.6] - 2026-04-15

### Added
- `central_get_config_assignments` — read which profiles are assigned to which scopes, filtered by scope_id and device_function (`GET /network-config/v1alpha1/config-assignments`)
- `central_manage_config_assignment` — assign or remove a profile at a scope (`POST`/`DELETE /network-config/v1alpha1/config-assignments`). Completes the WLAN sync workflow — profiles can now be assigned to scopes programmatically.
- Central tool count: 51 → 53

### Fixed
- manage_wlan Mist→Central Step 6 now calls `central_manage_config_assignment` to assign the profile instead of looping
- manage_wlan both-platforms workflow returns full configs and requires user to choose source

## [v0.8.5] - 2026-04-15

### Fixed
- Removed `source_platform` parameter from `central_manage_wlan_profile` and `mist_change_org_configuration_objects` — conflicted with unified `manage_wlan_profile` tool. The AI followed the workflow correctly but got blocked when the platform tool rejected the call.

## [v0.8.4] - 2026-04-15

### Added
- `manage_wlan_profile` — unified cross-platform entry point for all WLAN operations. Checks both Mist and Central for the SSID and returns the correct sync workflow automatically. Registered when both platforms are enabled.

## [v0.8.3] - 2026-04-15

### Added
- Mist org_id validation — server resolves the real org_id at startup. `validate_org_id()` catches fabricated org_ids before API calls.

## [v0.8.2] - 2026-04-15

### Fixed
- Sync prompt now enforces `mist_get_self` as mandatory first step with "Do NOT use any org_id from memory"
- Sync prompt Step 2 looks up WLAN template assignment: `template_id` → `sitegroup_ids` + `site_ids` → names
- Sync prompt Step 9 (REQUIRED) reports assignment mapping based on template assignment
- Added explicit opmode mapping table in sync prompt

## [v0.8.1] - 2026-04-15

### Fixed
- Added all 22 valid `opmode` enum values to `central_manage_wlan_profile` tool description — prevents invalid values like `WPA2_PSK_AES`
- Added valid enum values for `rf-band`, `forward-mode`, `vlan-selector`, `out-of-service`, `broadcast-filter-ipv4`
- Strengthened cross-platform WLAN sync guidance in INSTRUCTIONS.md

[v0.8.7]: https://github.com/nowireless4u/hpe-networking-mcp/releases/tag/v0.8.7
[v0.8.6]: https://github.com/nowireless4u/hpe-networking-mcp/releases/tag/v0.8.6
[v0.8.5]: https://github.com/nowireless4u/hpe-networking-mcp/releases/tag/v0.8.5
[v0.8.4]: https://github.com/nowireless4u/hpe-networking-mcp/releases/tag/v0.8.4
[v0.8.3]: https://github.com/nowireless4u/hpe-networking-mcp/releases/tag/v0.8.3
[v0.8.2]: https://github.com/nowireless4u/hpe-networking-mcp/releases/tag/v0.8.2
[v0.8.1]: https://github.com/nowireless4u/hpe-networking-mcp/releases/tag/v0.8.1

## [v0.8.0] - 2026-04-14

### Fixed — Central Write Tools (#99)
- Central delete operations now use bulk endpoint (`DELETE {path}/bulk` with `{"items": [{"id": "..."}]}`) instead of appending ID to URL path
- Central update operations now pass `scopeId` in request body instead of URL path
- Confirmation loop fix: added `confirmed` parameter to all write tools (Mist + Central). When `confirmed=true`, skips re-prompting. The AI sets this after the user confirms in chat.

### Added — Cross-Platform WLAN Sync (#94-98)
- `central_get_wlan_profiles` — read WLAN SSID profiles from Central's config library (`GET /network-config/v1alpha1/wlan-ssids`)
- `central_manage_wlan_profile` — create, update, delete WLAN SSID profiles in Central
- `central_get_aliases` — read alias configurations used in WLAN profiles, server groups, and VLANs (`GET /network-config/v1alpha1/aliases`)
- `central_get_server_groups` — read RADIUS/auth server group definitions (`GET /network-config/v1alpha1/server-groups`)
- `central_get_named_vlans` — read named VLAN configurations (`GET /network-config/v1alpha1/named-vlan`)
- `wlan_mapper.py` + `_wlan_helpers.py` — field translation modules between Central and Mist WLAN formats, supporting all mapped fields: opmode with pairwise arrays (WPA2/WPA3/transition), RADIUS with server group and template variable resolution, dynamic VLAN with airespace interface names, data rate profiles (MBR → rateset template), MAC auth, NAS ID/IP, CoA, RadSec, EHT/11be, and RF bands as arrays
- 3 cross-platform sync prompts: `sync_wlans_mist_to_central`, `sync_wlans_central_to_mist`, `sync_wlans_bidirectional` — registered as shared prompts (requires both Mist and Central enabled), with alias resolution, template variable creation, and comparison/diff workflows
- WLAN field mapping reference at `docs/mappings/WLAN.md` (~38 mapped fields)
- Tunneled SSIDs automatically excluded from migration
- Central tool count: 48 → 51 (+ 3 new read-only tools), Central prompt count: 15 → 12 (3 sync prompts moved to cross-platform)
- 81 new unit tests for `wlan_mapper.py` and `_wlan_helpers.py`

### Added — Site Collection Management
- `add_sites` and `remove_sites` action types for `central_manage_site_collection`
- Uses `POST /network-config/v1/site-collection-add-sites` and `DELETE /network-config/v1/site-collection-remove-sites`

[v0.8.0]: https://github.com/nowireless4u/hpe-networking-mcp/releases/tag/v0.8.0

## [v0.7.21] - 2026-04-14

### Added
- `central_get_sites` — new tool returning site configuration data (address, timezone, scopeName) from `network-config/v1/sites` with OData filter and sort support

### Changed
- Renamed old `central_get_sites` → `central_get_site_health` to accurately reflect it returns health metrics, not site config data
- Central tool count: 45 → 46 (+ 12 prompts)

### Fixed
- `central_get_site_health` crash (`KeyError: 'name'`) when sites returned from the health API lack a `name` field (e.g. newly created sites)

[v0.7.21]: https://github.com/nowireless4u/hpe-networking-mcp/releases/tag/v0.7.21

## [v0.7.20] - 2026-04-14

### Fixed
- Central site creation payload: timezone is required, all field values must use full names (no abbreviations). Updated tool description, INSTRUCTIONS.md, and TOOLS.md with correct format.

[v0.7.20]: https://github.com/nowireless4u/hpe-networking-mcp/releases/tag/v0.7.20

## [v0.7.19] - 2026-04-14

### Fixed
- Central write tools sending payload as query params instead of JSON body — pycentral `command()` uses `api_data` for request body, not `api_params`
- Added `api_data` parameter to `retry_central_command` for POST/PUT body support

[v0.7.19]: https://github.com/nowireless4u/hpe-networking-mcp/releases/tag/v0.7.19

## [v0.7.18] - 2026-04-14

### Fixed
- Central write tools using wrong API version (`v1` instead of `v1alpha1`) for sites, site-collections, and device-groups endpoints, causing DNS resolution failures

[v0.7.18]: https://github.com/nowireless4u/hpe-networking-mcp/releases/tag/v0.7.18

## [v0.7.17] - 2026-04-14

### Changed — Write Tool Confirmation
- Create operations now execute immediately without confirmation
- Update and delete operations require user confirmation (via elicitation prompt or AI chat confirmation)
- Matches the expected behavior: creates are safe, updates/deletes need approval

[v0.7.17]: https://github.com/nowireless4u/hpe-networking-mcp/releases/tag/v0.7.17

## [v0.7.16] - 2026-04-14

### Fixed — Write Tool Confirmation
- When `DISABLE_ELICITATION=false` and the client doesn't support elicitation prompts, write tools now return a `confirmation_required` response instructing the AI to confirm with the user in chat before re-calling the tool
- Previously, write tools auto-accepted silently when the client lacked elicitation support, bypassing user confirmation entirely

### Changed
- Elicitation middleware now tracks three modes: `disabled` (auto-accept), `prompt` (elicitation dialog), `chat_confirm` (AI asks user in conversation)

[v0.7.16]: https://github.com/nowireless4u/hpe-networking-mcp/releases/tag/v0.7.16

## [v0.7.15] - 2026-04-14

### Changed — Central Dynamic Registration (Issue #80)
- Converted Central tool registration from explicit imports to dynamic `TOOLS` dict + `importlib` pattern, matching Mist
- All 15 Central tool modules now use `_registry.mcp` decorator pattern instead of `register(mcp)` wrapper functions

### Fixed — Write Tool Visibility
- ElicitationMiddleware no longer overrides write tool visibility when client lacks elicitation support — write tools stay visible when enabled by config
- In-tool `elicitation_handler` now auto-accepts gracefully when client can't prompt (instead of throwing ToolError)
- Mist and Central write tools conditionally skip registration when their platform write flag is disabled

### Removed
- `ENABLE_WRITE_TOOLS` global flag — replaced by per-platform `ENABLE_MIST_WRITE_TOOLS` and `ENABLE_CENTRAL_WRITE_TOOLS`

[v0.7.15]: https://github.com/nowireless4u/hpe-networking-mcp/releases/tag/v0.7.15

## [v0.7.14] - 2026-04-13

### Added — Central Write Tools
- `central_manage_site` — create, update, and delete sites via `network-config/v1/sites`
- `central_manage_site_collection` — create, update, and delete site collections via `network-config/v1/site-collections`
- `central_manage_device_group` — create, update, and delete device groups via `network-config/v1/device-groups`
- All write tools gated behind `ENABLE_WRITE_TOOLS=true` with elicitation confirmation

### Fixed
- Write tool visibility: server.py Visibility transform and elicitation middleware now handle both `write` and `write_delete` tags consistently

### Changed
- Central tool count: 42 → 45 (+ 12 prompts)

[v0.7.14]: https://github.com/nowireless4u/hpe-networking-mcp/releases/tag/v0.7.14

## [v0.7.13] - 2026-04-13

### Added — Mist Best-Practice Guardrails
- `guardrails.py` validation module — inspects write tool payloads and warns when operations violate Mist best practices (site-level WLAN creation, hardcoded RADIUS IPs, fixed RF channels/power, static PSKs)
- Guardrails integrated into all 4 Mist write tools — warnings in elicitation message, suggestions in tool response
- `provision_site_from_template` prompt — guided workflow for cloning a site using templates
- `bulk_provision_sites` prompt — guided workflow for bulk site creation with source config analysis done once
- Mist Best Practices section in INSTRUCTIONS.md

### Added — Central Scope Tool Improvements
- Enriched scope tree output with `persona_count`, `resource_count`, `child_scope_count`, `device_count`, per-persona `categories` breakdown
- `include_details` parameter on `central_get_effective_config` — exposes full resource configuration data
- `inheritance_path` in effective config output — ordered path from Global to target scope
- `scope_configuration_overview` and `scope_effective_config` guided prompts
- Split `scope_builder.py` into `scope_builder.py` + `scope_queries.py`
- Mermaid diagram device labels now use hostnames instead of model numbers

### Changed
- Mist tool count: 35 tools + 2 prompts
- Central tool count: 42 tools + 12 prompts (was 10)
- Test count: 176 (was 119)

[v0.7.13]: https://github.com/nowireless4u/hpe-networking-mcp/releases/tag/v0.7.13

## [v0.7.12] - 2026-04-13

### Fixed
- Site update/delete calling nonexistent `mistapi.api.v1.orgs.sites.updateOrgSite` / `deleteOrgSite` — fixed to `mistapi.api.v1.sites.sites.updateSiteInfo(site_id)` and `deleteSite(site_id)`

[v0.7.12]: https://github.com/nowireless4u/hpe-networking-mcp/releases/tag/v0.7.12

## [v0.7.11] - 2026-04-13

### Added
- `sites` object type for `mist_change_org_configuration_objects` and `mist_update_org_configuration_objects` — enables site create, update, and delete via write tools

### Fixed
- Write tools failing with "AI App does not support elicitation" when both `ENABLE_WRITE_TOOLS=true` and `DISABLE_ELICITATION=true` — missing `ctx.set_state("disable_elicitation", True)` in the elicitation middleware

### Changed
- `__version__` now reads dynamically from package metadata instead of being hardcoded
- `pyproject.toml` is the single source of truth for version

[v0.7.11]: https://github.com/nowireless4u/hpe-networking-mcp/releases/tag/v0.7.11

## [v0.7.0] - 2026-04-03

### Added — Central Scope & Configuration Tools
- `central_get_scope_tree` — Full scope hierarchy (Global → Collections → Sites → Devices) with committed or effective view
- `central_get_scope_resources` — Configuration resources at a specific scope level, filterable by persona (AP, Switch, Gateway)
- `central_get_effective_config` — Show what configuration a device inherits and from which scope level
- `central_get_devices_in_scope` — List devices within a scope, filterable by device type
- `central_get_scope_diagram` — Pre-built Mermaid flowchart of the scope hierarchy with color-coded device types

### Added — Dependencies
- `treelib>=1.7.0` — Tree data structure for scope hierarchy building

### Changed
- Central tool count: 37 → 42 (+ 10 prompts)
- Total tools: 80 (dynamic mode) or 87 (static mode)

[v0.7.0]: https://github.com/nowireless4u/hpe-networking-mcp/releases/tag/v0.7.0

## [v0.6.6] - 2026-04-03

### Added
- `central_get_switch_hardware_trends` — Time-series hardware data per switch member (CPU, memory, temp, PoE capacity/consumption, power). Returns all stack members.
- `central_get_switch_poe` — Per-port PoE data showing powerDrawnInWatts per interface

### Improved
- PoE bounce: hardware-trends pre-check skips entire switch if total PoE consumption is zero (faster, avoids unnecessary per-port checks)
- PoE bounce: includes `total_poe_watts` in response for reporting

### Fixed
- Stack PoE reporting: `hardware-trends` returns all stack members, solving the conductor-only data issue

### Changed
- Central tool count: 35 → 37 (+ 10 prompts)
- Total tools: 75 (dynamic mode) or 82 (static mode)

[v0.6.6]: https://github.com/nowireless4u/hpe-networking-mcp/releases/tag/v0.6.6

## [v0.6.0] - 2026-04-02

### Added — Central
- `central_disconnect_users_ssid` — Disconnect all users from a specific SSID
- `central_disconnect_users_ap` — Disconnect all users from an AP
- `central_disconnect_client_ap` — Disconnect client by MAC from an AP
- `central_disconnect_client_gateway` — Disconnect client by MAC from a gateway
- `central_disconnect_clients_gateway` — Disconnect all clients from a gateway
- `central_port_bounce_switch` — Port bounce on CX switch
- `central_poe_bounce_switch` — PoE bounce on CX switch
- `central_port_bounce_gateway` — Port bounce on gateway
- `central_poe_bounce_gateway` — PoE bounce on gateway

### Added — Mist
- `mist_bounce_switch_port` — Port bounce on Juniper EX switch

### Added — Safety
- Port safety rules in INSTRUCTIONS.md — AI must check interfaces before bouncing
- Platform-specific port naming guidance (Aruba CX vs Juniper EX)

### Changed
- Mist tool count: 34 → 35
- Central tool count: 26 → 35 (+ 10 prompts)
- Total tools: 73 (dynamic mode) or 80 (static mode)

[v0.6.0]: https://github.com/nowireless4u/hpe-networking-mcp/releases/tag/v0.6.0

## [v0.5.1] - 2026-04-02

### Fixed
- `mist_search_device`: removed `vc_mac` parameter not supported by installed `mistapi` SDK version — fixes 503 errors on device search
- `mist_search_device`: use kwargs dict to only pass non-None parameters to SDK — prevents unexpected keyword argument errors
- Claude Desktop: switched from `mcp-remote` to `supergateway` for stdio-to-HTTP bridging — fixes tool call timeouts and session loss after system sleep
- Docker health check: use `uv run --no-sync python` instead of bare `python` to find httpx in the virtual environment — fixes persistent "unhealthy" status
- Docker Compose: default to local `build: .` instead of GHCR image for Apple Silicon / ARM compatibility

### Changed
- README: Claude Desktop setup now uses `supergateway` bridge with full troubleshooting guide
- README: Added troubleshooting for Claude Desktop configuration errors and tool timeouts

[v0.5.1]: https://github.com/nowireless4u/hpe-networking-mcp/releases/tag/v0.5.1

## [v0.5.0] - 2026-03-29

### Added — Central
- `central_get_audit_logs` — Retrieve audit logs with time range, OData filtering, and pagination
- `central_get_audit_log_detail` — Get detailed audit log entry by ID
- `central_get_ap_stats` — AP performance statistics with optional time range
- `central_get_ap_utilization` — AP CPU, memory, or PoE utilization trends
- `central_get_gateway_stats` — Gateway performance statistics
- `central_get_gateway_utilization` — Gateway CPU or memory utilization trends
- `central_get_gateway_wan_availability` — Gateway WAN uplink availability
- `central_get_tunnel_health` — IPSec tunnel health summary
- `central_ping` — Ping test from AP, CX switch, or gateway
- `central_traceroute` — Traceroute from AP, CX switch, or gateway
- `central_cable_test` — Cable test on switch ports
- `central_show_commands` — Execute show commands on devices
- `central_get_applications` — Application visibility per site (usage, risk, experience)

### Added — Mist
- `mist_get_wlans` — List WLANs/SSIDs at org or site level
- `mist_get_site_health` — Organization-wide site health overview
- `mist_get_ap_details` — Detailed AP info by device ID
- `mist_get_switch_details` — Detailed switch info by device ID
- `mist_get_gateway_details` — Detailed gateway info by device ID

### Changed
- Mist tool count: 29 → 34
- Central tool count: 13 → 26 (+ 10 prompts)
- Total tools: 63 (dynamic mode) or 70 (static mode)

[v0.5.0]: https://github.com/nowireless4u/hpe-networking-mcp/releases/tag/v0.5.0

## [v0.4.0] - 2026-03-28

### Added
- `central_get_wlans` — List all WLANs/SSIDs with filtering by site or AP
- `central_get_ap_details` — Detailed AP monitoring (model, status, firmware, radio info)
- `central_get_switch_details` — Detailed switch monitoring (health, deployment, firmware)
- `central_get_gateway_details` — Detailed gateway monitoring (interfaces, tunnels, health)

### Changed
- Central tool count: 9 → 13 tools (+ 10 prompts)
- Total tools across all platforms: 45 (dynamic mode) or 52 (static mode)

[v0.4.0]: https://github.com/nowireless4u/hpe-networking-mcp/releases/tag/v0.4.0

## [v0.3.3] - 2026-03-28

### Fixed
- All CI/CD pipeline failures (lint, format, mypy, bandit)
- Set `MCP_TOOL_MODE` default to `dynamic`

[v0.3.3]: https://github.com/nowireless4u/hpe-networking-mcp/releases/tag/v0.3.3

## [v0.2.0] - 2026-03-28

### Added
- Unified MCP server combining Juniper Mist, Aruba Central, and HPE GreenLake
- 49 tools: 29 Mist + 10 Central + 10 GreenLake
- 11 guided prompts for Central troubleshooting workflows
- Streamable HTTP transport on port 8000
- Docker Compose secrets for secure credential management (per-credential files at `/run/secrets/`)
- Elicitation middleware for write tool safety (user confirmation before mutations)
- NullStrip middleware for MCP client compatibility
- Write tools disabled by default (`ENABLE_WRITE_TOOLS=true` to enable)
- Platform auto-disable when credentials are missing
- Multi-stage Dockerfile with non-root user (`mcpuser`, uid 1000)
- `secrets/*.example` template files for all 9 credentials
- PRD and PRP documentation

### Platforms
- **Juniper Mist**: Account info, configuration objects (CRUD), device/client search, events, alarms, SLE metrics, RRM, rogue detection, firmware upgrades, Marvis troubleshooting
- **Aruba Central**: Site health, device inventory, client connectivity, alerts, events, 11 guided troubleshooting prompts
- **HPE GreenLake**: Audit logs, device inventory, subscriptions, user management, workspace management

[v0.2.0]: https://github.com/nowireless4u/hpe-networking-mcp/releases/tag/v0.2.0
