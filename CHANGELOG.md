# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
| `central_get_site_health` | `[]` | 13 sites; HOME = 38 clients / 17 devices, with full per-type breakdown |
| `central_get_site_name_id_mapping` (HOME) | `health: 0, total_devices: 0, total_clients: 0, total_alerts: 0` | `health: 81, total_devices: 17, total_clients: 38, total_alerts: 3` |

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
- Cross-platform join (mist_get_self → mist_search_device → central_get_aps) runs in ONE execute call, returning `{"mist_aps_count": 5, "central_aps_count": 3, "sample_mist_ap": "KNAPP-BASEMENT", "sample_central_ap": "HOME-GARAGE-AP", "cross_platform_match": True}`.
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

3 Aruba AP-755s at site HOME (Central) — full report rendered with 2.4G/5G/6G channel bars, noise floors, utilization meters, per-AP table. Picker mode tested across 19 sites with accurate online counts. Mist-side picker uses `connected: bool` from `/orgs/{id}/inventory` (not the `status` field — that endpoint doesn't carry it).

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
