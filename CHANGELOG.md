# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
