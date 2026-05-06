# Tool Reference

Complete reference for all tools registered by the HPE Networking MCP Server.
Tools are namespaced by platform: `mist_*` (Juniper Mist), `central_*` (Aruba Central),
`greenlake_*` (HPE GreenLake), `clearpass_*` (Aruba ClearPass), `apstra_*`
(Juniper Apstra), and `axis_*` (Axis Atmos Cloud).

## Dynamic mode (default since v2.0.0.0)

The server ships with `MCP_TOOL_MODE=dynamic` by default. At session start the AI sees **24 tools**:

- **4 cross-platform static tools**
  - `health(platform=...)`
  - `site_health_check(site_name=...)`
  - `site_rf_check(site_name=...)`
  - `manage_wlan_profile(...)`
- **3 meta-tools per platform** (× 6 platforms = 18)
  - `<platform>_list_tools(filter=...)` — list candidates
  - `<platform>_get_tool_schema(name=...)` — fetch parameter schema
  - `<platform>_invoke_tool(name=..., arguments={...})` — invoke by name
- **2 skills tools** (since v2.3.0.0)
  - `skills_list(filter=...)` — list bundled multi-step runbooks
  - `skills_load(name=...)` — load a runbook to execute

All 312 per-platform tools documented below still exist and are discoverable through the meta-tools. Their names, parameters, and return shapes are unchanged from v1.x. The per-platform sections below serve as the **full tool index** — humans read them directly; the AI discovers them via the meta-tools.

Set `MCP_TOOL_MODE=static` to restore the v1.x surface where every per-platform tool registers individually (312 visible). Set `MCP_TOOL_MODE=code` for an experimental four-tier discovery + sandboxed Python execution surface — see the next section.

## Code mode (experimental, opt-in since v2.1.0.0)

With `MCP_TOOL_MODE=code` the server replaces the exposed catalog with a 4-tool surface: `tags`, `search`, `get_schema`, and `execute`. The LLM writes async Python inside `execute`; `call_tool(tool_name, params)` dispatches through the real FastMCP call_tool so every middleware (NullStrip, Elicitation, Pydantic coercion) keeps working. Multi-step workflows collapse from N MCP round-trips to one.

### Four-tier progressive disclosure

| Tier | Tool | What the LLM calls |
|---|---|---|
| 1 | `tags(detail="brief")` | Browse the tag space — returns platform buckets (`mist (35 tools)`, `central (83)`, `axis (25)`, etc.) plus module categories |
| 2 | `search(query, tags=[...], detail)` | BM25 search the catalog, optionally scoped by tag |
| 3 | `get_schema(tools=[...], detail)` | Fetch parameter shape for named tools |
| 4 | `execute(code)` | Run async Python; `call_tool(name, params)` available in scope |

### Example — cross-platform join in one call

```python
me = await call_tool("mist_get_self", {"action_type": "account_info"})
org_id = me["result"]["privileges"][0]["org_id"]

mist_aps = await call_tool("mist_search_device", {"org_id": org_id, "device_type": "ap", "limit": 5})
central_aps = await call_tool("central_get_aps", {"site_name": "HQ", "status": "ONLINE"})

return {
    "mist_count": len(mist_aps["result"]["results"]),
    "central_count": len(central_aps["result"]),
}
```

Three tool calls inside one `execute`. In dynamic mode this same workflow would be 5+ MCP round-trips.

### Cross-platform aggregators are NOT registered in code mode

`site_health_check`, `site_rf_check`, and `manage_wlan_profile` exist to work around dynamic mode's "AI reaches for one platform and stops" problem. Code mode's premise is that the LLM can compose per-platform tools itself — keeping aggregators would contradict it and make head-to-head measurement with dynamic mode meaningless. `health` stays registered in every mode.

### Sandbox limits

The `pydantic-monty` sandbox restricts duration (30s), memory (128 MB), and recursion depth (50). Several Python features the LLM may reach for are also unavailable:

- **`asyncio.gather()`** — fails with `TypeError: 'list' object is not an iterator`. Use sequential `await` calls instead.
- **OS-access functions** — `datetime.now()`, `time.time()`, file I/O (`open`, `Path.read_text`), `os.environ`, and `subprocess` all raise `NotImplementedError`. For timestamps, accept ISO strings as parameters or hardcode literal ISO-8601 strings.
- **Some introspection** — `hasattr`, `type`, and parts of the introspection surface aren't available; the LLM discovers these via error messages.

The `execute` tool description tells the LLM these limits up front so it shouldn't waste turns rediscovering them.

### What `call_tool` can dispatch to

Inside `execute()`, `call_tool(name, params)` only resolves names from the backend platform catalog — every tool whose name starts with `mist_` / `central_` / `greenlake_` / `clearpass_` / `apstra_` / `axis_`, plus the cross-platform `health`. The discovery tools (`tags` / `search` / `get_schema`) are NOT callable from inside `execute()` — they live at the outer MCP surface for planning. Use them BEFORE writing your code block, then chain platform tools inside.

If you do try to dispatch to a discovery tool by mistake, `SandboxErrorCatchMiddleware` returns a string like `Sandbox error: Exception: Unknown tool: search` so you can fix the call on the next turn (rather than seeing a generic masked error). See v2.2.0.4 release notes / #208.

### When to use which mode

- **`dynamic` (default)** — stable, production-tested, best for lookup-style questions
- **`static`** — v1.x behavior, every tool visible, only useful for agents that hardcode tool names
- **`code`** — experimental; best for multi-step aggregations, cross-platform joins, filter/map/reduce workflows

If you're not sure, stay on `dynamic`. Code mode is meant for measurement + evaluation right now.

## Overview

| Platform | Read-Only Tools | Write Tools | Prompts | Total |
|----------|----------------|-------------|---------|-------|
| Juniper Mist | 31 | 4 | 2 | 37 |
| Aruba Central | 63 | 20 | 12 | 95 |
| Aruba ClearPass | 65 | 75 | -- | 140 |
| Juniper Apstra | 12 | 7 | -- | 19 |
| HPE GreenLake | 10 | -- | -- | 10 |
| Axis Atmos Cloud | 12 | 13 | -- | 25 |
| Aruba OS 8 | 26 | 12 | 9 | 47 |
| Cross-Platform | 3 | 1 | 3 | 7 |

Write tools are disabled by default per platform. Enable them with environment variables:
`ENABLE_MIST_WRITE_TOOLS=true`, `ENABLE_CENTRAL_WRITE_TOOLS=true`,
`ENABLE_CLEARPASS_WRITE_TOOLS=true`, `ENABLE_APSTRA_WRITE_TOOLS=true`, or `ENABLE_AXIS_WRITE_TOOLS=true`. Elicitation applies in both tool modes — the AI still gets a confirmation prompt before a destructive call, whether it invoked the tool directly (static mode) or through `<platform>_invoke_tool` (dynamic mode).

## Cross-platform static tools

Always registered regardless of `MCP_TOOL_MODE`:

- **`health`** — reports per-platform status in one call. Accepts
  `platform: str | list[str] | None`. Replaces the v1.x `apstra_health`
  and `clearpass_test_connection` tools (both removed in v2.0).
- **`site_health_check`** — cross-platform site aggregator.
- **`site_rf_check`** — cross-platform RF / channel-planning aggregator.
- **`manage_wlan_profile`** — cross-platform WLAN orchestrator.

In **code mode**, the three aggregators (`site_health_check`,
`site_rf_check`, `manage_wlan_profile`) are NOT registered — code mode's
premise is that the LLM composes per-platform calls itself. `health` is
registered in every mode.

## Skills (since v2.3.0.0)

A *skill* is a markdown file with YAML frontmatter sitting in
`src/hpe_networking_mcp/skills/`. The frontmatter carries metadata; the
body is a step-by-step runbook. The AI calls one of two tools to discover
and load skills, then follows the steps.

- **`skills_list(platform=..., tag=...)`** — metadata-only browse. Returns
  `count` + a list of `{name, title, description, platforms, tags, tools}`.
  Both filters accept a string or a list of strings.
- **`skills_load(name)`** — full markdown body. Case-insensitive exact
  match wins; substring fallback is tried if no exact match exists.
  Multi-match returns an error listing the candidates.

Skills are **always-visible** in every `MCP_TOOL_MODE` — they're an entry
point for known runbook-style queries (e.g. "infra health snapshot",
"pre-change baseline", "are our WLANs in sync?").

### Why skills work in code mode (where aggregators don't)

Aggregator tools do N calls in Python and return one merged answer; that
contradicts code mode's premise (LLM composes per-platform calls itself).
Skills are the *textual* equivalent — they tell the LLM which tools to
call in what order, and the LLM does the join itself in `execute()`. So
skills register in every mode without violating the code-mode design.

### Bundled skills

| Name | Purpose | Added |
|---|---|---|
| `infrastructure-health-check` | Cross-platform daily-standup style overview — `health()` then per-platform alarms/alerts | v2.3.0.0 |
| `change-pre-check` | Pre-change baseline snapshot — confirms scope, captures pre-existing alarms, recent admin activity, current config, active impact metrics | v2.3.0.0 |
| `wlan-sync-validation` | Mist ↔ Central WLAN drift detection — classifies each SSID as in-sync / Mist-only / Central-only / drift, lists field diffs | v2.3.0.0 |
| `change-post-check` | Post-change verification + diff against the pre-check baseline (CLEAN / IMPACT-OBSERVED / REGRESSION) | v2.3.0.1 |
| `central-scope-audit` | Aruba Central VSG-anchored scope audit — walks ~25 profile categories with per-setting checks, judges each finding against VSG-recommended scope | v2.3.0.5 |
| `mist-scope-audit` | Juniper Mist comprehensive scope audit — WLAN templates, RF templates, switch templates, port profiles, virtual chassis, firmware policy, PSK strategy | v2.3.0.5 |
| `aos-migration` | **AOS 8 → AOS 10 migration (PoC)** — two-act workflow with no operator interview. Act I = readiness audit: full /md hierarchy walk via live AOS 8 API, applicability-gated feature-parity rules (REGRESSION/DRIFT/INFO), GO / BLOCKED / PARTIAL / EMPTY-SOURCE verdict. Cluster-offline tolerant — degraded source data doesn't block the audit. Act II = per-object disposition matrix (every configured object regardless of usage state, with `usage_state` metadata), ordered Central API call sequence, post-translation validation checklist. AOS 6 and Instant AP are out of scope (different migration paths). Renamed from `aos-migration-readiness` in v2.5.0.0; tightened in v2.5.0.1 (delete operator interview; drop AOS 6/IAP support; convert controller-plumbing rules from REGRESSION to inventory; add hierarchy walk + EMPTY-SOURCE + cluster-offline tolerance + applicability gates + usage_state column + auto-recommend target mode). | v2.3.0.6 / v2.5.0.1 |
| `morning-coffee-report` | Daily ops digest covering the last 24h: who's been in (audit logs), what's broken (active alerts), top talkers (clients/APs by load), AI insights (Mist SLE). Day-over-day delta deferred to phase 2 | v2.3.1.8 |

The `TEMPLATE.md` file in the skills directory is a starting point if you
want to author a new skill — it's filtered out of the registry by name.

### Authoring rules

A skill file must:

- Have YAML frontmatter delimited by `---` lines at the top
- Set `name`, `title`, `description` as strings (required)
- Set `name` to match the filename stem exactly (e.g. `change-pre-check.md`
  must have `name: change-pre-check` — files whose name disagrees with
  frontmatter are skipped at load with a warning, not crashed on)

Optional frontmatter fields: `platforms` (list), `tags` (list), `tools`
(list — informational hint about which underlying tools the skill calls).

Bad frontmatter (missing fields, YAML errors, name/filename mismatch) is
logged and skipped; the rest of the catalog still loads. See
`skills/TEMPLATE.md` for the full structure.

---

## Juniper Mist (35 tools + 2 prompts)

### Account and Organization

#### `mist_get_self`

> Retrieve information about the current user and account.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| action_type | str | Yes | `account_info`, `api_usage`, or `login_failures`. |

#### `mist_get_org_or_site_info`

> Search information about the organizations or sites.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| info_type | str | Yes | `org` or `site`. |
| org_id | UUID | Yes | Organization ID. |
| site_id | UUID | No | Site ID. If omitted with info_type=site, lists all sites. |

#### `mist_get_org_licenses`

> Retrieve information about the licenses of an organization.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| org_id | UUID | Yes | Organization ID. |
| response_type | str | Yes | `claim_status`, `by_site`, or `summary`. |

#### `mist_get_site_health`

> Get a health overview across all sites in the organization.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| org_id | UUID | Yes | Organization ID. |

#### `mist_get_next_page`

> Retrieve the next page of results using the `_next` URL from a previous response.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| url | str | Yes | The `_next` URL from a previous response. |

### Configuration

#### `mist_get_configuration_objects`

> Retrieve configuration objects (WLANs, profiles, templates, devices) from an org or site.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| org_id | UUID | Yes | Organization ID. |
| object_type | str | Yes | Object type enum (e.g. `org_wlans`, `site_devices`). |
| site_id | UUID | No | Site ID. Required for `site_*` object types. |
| object_id | UUID | No | Retrieve a single object by ID. |
| name | str | No | Filter by name. Case-insensitive, supports `*` wildcards. |
| computed | bool | No | Include inherited settings. For `org_sites`, `site_devices`, `site_wlans`. |
| limit | int | No | Default: 20. Max: 1000. |

#### `mist_get_configuration_object_schema`

> Retrieve the JSON schema for a Mist configuration object type from the OpenAPI spec.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| schema_name | str | Yes | Name of the configuration object schema. |
| verbose | bool | No | Default: false. True returns full schema with all constraints. |

#### `mist_search_device_config_history`

> Search for entries in device config history to track configuration changes over time.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| site_id | UUID | Yes | Site ID. |
| query_type | str | Yes | `history` or `last_configs`. |
| device_type | str | Yes | `ap`, `switch`, or `gateway`. |
| device_mac | str | No | MAC address of the device. |
| start | int | No | Start of time range (epoch seconds). |
| end | int | No | End of time range (epoch seconds). |
| limit | int | No | Default: 20. |

#### `mist_get_wlans`

> List WLANs/SSIDs configured in the organization or a specific site.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| org_id | UUID | Yes | Organization ID. |
| site_id | UUID | No | Site ID. If provided, returns WLANs for this site only. |

### Clients

#### `mist_search_client`

> Search for clients across an organization or site by type, MAC, hostname, IP, and more.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| client_type | str | Yes | `wan`, `wired`, `wireless`, or `nac`. |
| org_id | UUID | Yes | Organization ID. |
| site_id | UUID | No | Site ID. |
| device_mac | str | No | MAC of the connected AP or switch. Supports `*` wildcards. |
| band | str | No | `24`, `5`, or `6`. Wireless clients only. |
| ssid | str | No | SSID name. Wireless or NAC clients only. |
| mac | str | No | Client MAC address. Supports `*` wildcards. |
| hostname | str | No | Client hostname. Supports `*` wildcards. Not for WAN/wired. |
| ip | str | No | Client IP address. Supports `*` wildcards. Not for NAC. |
| text | str | No | Free text search. Not for WAN clients. |
| start | int | No | Start of time range (epoch seconds). |
| end | int | No | End of time range (epoch seconds). |
| limit | int | No | Default: 20. |

#### `mist_search_guest_authorization`

> Search for guest authorization entries in an organization or site.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| scope | str | Yes | `org` or `site`. |
| org_id | UUID | Yes | Organization ID. |
| site_id | UUID | No | Site ID. Required when scope is `site`. |
| guest_mac | str | No | MAC address of the guest. |
| wlan_id | UUID | No | WLAN ID to filter by. |
| auth_method | str | No | Authentication method to filter by. |
| ssid | str | No | SSID to filter by. |
| start | int | No | Start of time range (epoch seconds). |
| end | int | No | End of time range (epoch seconds). |
| limit | int | No | Default: 20. |

### Device Management

#### `mist_search_device`

> Search for a device in the organization inventory by serial, model, MAC, type, or status.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| org_id | UUID | Yes | Organization ID. |
| site_id | UUID | No | Site ID. |
| serial | str | No | Serial number filter. |
| model | str | No | Device model. Supports `*` wildcards. |
| mac | str | No | MAC address. Supports `*` wildcards. |
| version | str | No | Firmware version filter. |
| vc_mac | str | No | Virtual chassis MAC address filter. |
| device_type | str | No | `ap`, `switch`, or `gateway`. |
| status | str | No | `connected` or `disconnected`. |
| text | str | No | Free text search across device attributes. Supports `*` wildcards. |
| limit | int | No | Default: 20. |

#### `mist_get_ap_details`

> Get detailed AP information including model, firmware, radio config, IP, and status.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| site_id | UUID | Yes | Site ID. |
| device_id | UUID | Yes | AP device ID (use `mist_search_device` to find it). |

#### `mist_get_switch_details`

> Get detailed switch information including model, firmware, port config, IP, and status.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| site_id | UUID | Yes | Site ID. |
| device_id | UUID | Yes | Switch device ID (use `mist_search_device` to find it). |

#### `mist_get_gateway_details`

> Get detailed gateway information including model, firmware, interfaces, tunnels, and status.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| site_id | UUID | Yes | Site ID. |
| device_id | UUID | Yes | Gateway device ID (use `mist_search_device` to find it). |

#### `mist_bounce_switch_port`

> Bounce ports on a Juniper EX switch to reset link state. Only bounce edge/access ports — never uplinks, stack, or aggregation ports.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| site_id | UUID | Yes | Site ID. |
| device_id | UUID | Yes | Device ID of the EX switch (use `mist_search_device` to find it). |
| ports | str | Yes | Comma-separated port names (e.g., `ge-0/0/0,ge-0/0/1`). Juniper format: `ge-0/0/0` (1G), `mge-0/0/0` (multi-gig). |

### Events, Alarms, and Audit Logs

#### `mist_search_events`

> Search for events from devices, MX Edge, clients, roaming, or rogue sources.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| event_source | str | Yes | `device`, `mxedge`, `wan_client`, `wireless_client`, `nac_client`, `roaming`, `rogue`. |
| org_id | UUID | Yes | Organization ID. |
| event_type | str | No | Comma-separated event types. Use `mist_get_constants` to discover types. |
| site_id | UUID | No | Site ID. Required for `roaming` and `rogue` sources. |
| mac | str | No | MAC address filter (device/WAN/NAC/rogue events). |
| text | str | No | Text search (device/NAC events only). |
| ssid | str | No | SSID filter (wireless/NAC/rogue events only). |
| start | int | No | Start of time range (epoch seconds). |
| end | int | No | End of time range (epoch seconds). |
| limit | int | No | Default: 20. |

#### `mist_search_audit_logs`

> Search audit logs for the current account or an organization.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| scope | str | Yes | `self` or `org`. |
| org_id | UUID | No | Organization ID. Required when scope is `org`. |
| start | int | No | Start of time range (epoch seconds). |
| end | int | No | End of time range (epoch seconds). |
| message | str | No | Message text filter (partial search). |
| limit | int | No | Default: 20. |

#### `mist_search_alarms`

> Search for raised alarms in an organization or site with filtering by group, severity, and type.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| org_id | UUID | Yes | Organization ID. |
| scope | str | Yes | `org`, `site`, or `suppressed`. |
| site_id | UUID | No | Site ID. Required when scope is `site`. |
| group | str | No | `infrastructure`, `marvis`, or `security`. org/site scope only. |
| severity | str | No | `critical`, `major`, `minor`, `warn`, or `info`. org/site scope only. |
| alarm_type | str | No | Comma-separated alarm types. Use `mist_get_constants` to discover types. |
| acked | bool | No | Filter acknowledged (true) or unacknowledged (false) alarms. |
| start | int | No | Start of time range (epoch seconds). |
| end | int | No | End of time range (epoch seconds). |
| limit | int | No | Default: 20. |

### Marvis AI Troubleshooting

#### `mist_troubleshoot`

> Troubleshoot sites, devices, or clients using Marvis AI. Requires Marvis subscription license.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| org_id | UUID | Yes | Organization ID. |
| troubleshoot_type | str | Yes | `wan`, `wired`, or `wireless`. |
| site_id | UUID | No | Site ID. |
| mac | str | No | MAC address of the client or device. |
| start | int | No | Start of time range (epoch seconds). |
| end | int | No | End of time range (epoch seconds). |

### Constants

#### `mist_get_constants`

> Retrieve Mist platform constants (event types, alarm definitions, device models, etc.).

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| object_type | str | Yes | One of: `fingerprint_types`, `insight_metrics`, `license_types`, `webhook_topics`, `device_models`, `device_events`, `mxedge_models`, `alarm_definitions`, `client_events`, `mxedge_events`, `nac_events`. |

### NAC

#### `mist_search_nac_user_macs`

> Search for NAC user MAC addresses used for MAC Authentication with Juniper Mist NAC.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| org_id | UUID | Yes | Organization ID. |
| usermac_id | str | No | ID of a specific User MAC to retrieve. |
| mac | str | No | Client MAC address. Supports `*` wildcards. |
| labels | list[str] | No | Labels to filter by (all must match). |
| limit | int | No | Default: 20. |

### Insight Metrics

#### `mist_get_insight_metrics`

> Get insight metrics for a site, client, AP, gateway, MX Edge, or switch.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| site_id | UUID | Yes | Site ID. |
| object_type | str | Yes | `site`, `client`, `ap`, `gateway`, `mxedge`, or `switch`. |
| metric | str | Yes | Metric name. Use `mist_get_constants` with `insight_metrics` to discover. |
| mac | str | No | MAC address (with or without colons). Required for client, mxedge, switch. Optional for ap, gateway — converted to device_id UUID automatically. |
| device_id | UUID | No | Device UUID. Optional alternative to `mac` for ap and gateway (either is accepted). |
| start | int | No | Start of time range (epoch seconds). |
| end | int | No | End of time range (epoch seconds). |
| duration | str | No | Duration shorthand (e.g. `1d`, `1h`, `10m`). |
| interval | str | No | Aggregation interval (e.g. `1h`, `1d`). |
| page | int | No | Page number for pagination. |
| limit | int | No | Default: 20. |

### Rogue Detection

#### `mist_list_rogue_devices`

> List rogue APs or clients detected at a site.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| site_id | UUID | Yes | Site ID. |
| rogue_type | str | Yes | `ap` or `client`. |
| rogue_ap_type | str | No | `honeypot`, `lan`, `others`, or `spoof`. AP type only. |
| start | int | No | Start of time range (epoch seconds). |
| end | int | No | End of time range (epoch seconds). |
| limit | int | No | Default: 20. |

### Radio Resource Management (RRM)

#### `mist_get_site_rrm_info`

> Retrieve RRM information: channel planning, considerations, neighbors, or events.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| site_id | UUID | Yes | Site ID. |
| rrm_info_type | str | Yes | `current_channel_planning`, `current_rrm_considerations`, `current_rrm_neighbors`, or `events`. |
| device_id | UUID | No | AP device ID. Required for `current_rrm_considerations`. |
| band | str | No | `24`, `5`, or `6`. Required for considerations, neighbors, and events. |
| start | int | No | Start of time range (epoch seconds). Events only. |
| end | int | No | End of time range (epoch seconds). Events only. |
| duration | str | No | Duration shorthand. Events only. |
| limit | int | No | Events only; defaults to 200 when `rrm_info_type=events`. Rejected for other modes. |
| page | int | No | Events only; defaults to 1 when `rrm_info_type=events`. Rejected for other modes. |

### Service Level Expectations (SLE)

#### `mist_get_site_sle`

> Get SLE data for a site scope including summaries, impact, impacted entities, and histograms.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| site_id | UUID | Yes | Site ID. |
| scope | str | Yes | `client`, `ap`, `gateway`, `mxedge`, `switch`, or `site`. |
| scope_id | str | Yes | ID of the scoped object. |
| metric | str | Yes | SLE metric name. |
| object_type | str | Yes | `summary`, `impact_summary`, `summary_trend`, `impacted_applications`, `impacted_aps`, `impacted_gateways`, `impacted_interfaces`, `impacted_switches`, `impacted_wireless_clients`, `impacted_wired_clients`, `impacted_chassis`, `histogram`, `classifier_summary_trend`, or `threshold`. |
| start | int | No | Start of time range (epoch seconds). |
| end | int | No | End of time range (epoch seconds). |
| classifier | str | No | Classifier name. Required for `classifier_summary_trend`. |
| duration | str | No | Duration shorthand (e.g. `1d`, `1h`). |

#### `mist_list_site_sle_info`

> List available SLE metrics or classifiers for a site scope.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| site_id | UUID | Yes | Site ID. |
| query_type | str | Yes | `metrics` or `classifiers`. |
| scope | str | Yes | `site`, `ap`, `client`, `gateway`, or `switch`. |
| scope_id | str | Yes | ID of the scoped object. |
| metric | str | No | SLE metric name. Required when query_type is `classifiers`. |

#### `mist_get_org_sle`

> Get organization-level SLE data (all/worst sites, MX Edges).

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| org_id | UUID | Yes | Organization ID. |
| metric | str | Yes | SLE metric name. |
| sle | str | No | SLE type to retrieve. |
| start | int | No | Start of time range (epoch seconds). |
| end | int | No | End of time range (epoch seconds). |
| limit | int | No | Default: 20. |

#### `mist_get_org_sites_sle`

> Get SLE summary across all organization sites.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| org_id | UUID | Yes | Organization ID. |
| sle | str | Yes | `wifi`, `wired`, or `wan`. |
| start | int | No | Start of time range (epoch seconds). |
| end | int | No | End of time range (epoch seconds). |
| limit | int | No | Default: 20. |

### Statistics

#### `mist_get_stats`

> Retrieve statistics for org, sites, devices, MX Edges, BGP, OSPF, peer paths, ports, or clients.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| stats_type | str | Yes | `org`, `sites`, `org_mxedges`, `org_devices`, `org_bgp`, `org_ospf`, `org_peer_paths`, `org_ports`, `site_mxedges`, `site_wireless_clients`, `site_devices`, `site_bgp`, `site_ospf`, or `site_ports`. |
| org_id | UUID | Yes | Organization ID. |
| site_id | UUID | No | Site ID. Required for `site_*` stats types. |
| device_type | str | No | `ap`, `switch`, or `gateway`. For `org_devices`/`site_devices` only. |
| object_id | str | No | Object ID or MAC to filter by (format varies by stats_type). |
| start | int | No | Start of time range (epoch seconds). |
| end | int | No | End of time range (epoch seconds). |
| limit | int | No | Default: 20. |

### Upgrades

#### `mist_list_upgrades`

> Retrieve upgrade jobs or available firmware versions for the organization.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| org_id | UUID | Yes | Organization ID. |
| device_type | str | Yes | `ap`, `switch`, `srx`, `mxedge`, `ssr`, `available_device_versions`, or `available_ssr_versions`. |
| upgrade_id | UUID | No | Specific upgrade job ID. For ap/switch/srx/mxedge/ssr only. |
| firmware_type | str | No | `ap`, `switch`, or `gateway`. For `available_device_versions` only. |
| model | str | No | Device model filter. For `available_device_versions` only. |
| channel | str | No | `alpha`, `beta`, or `stable`. For `available_ssr_versions` only. |
| mac | str | No | SSR MAC address(es). For `available_ssr_versions` only. |

### Write Tools (disabled by default)

#### `mist_update_site_configuration_objects`

> Update or create a configuration object for a site. Requires `ENABLE_MIST_WRITE_TOOLS=true`.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| site_id | UUID | Yes | Site ID. |
| object_type | str | Yes | `devices`, `evpn_topologies`, `psks`, `webhooks`, `wlans`, `wxrules`, or `wxtags`. |
| object_id | UUID | No | ID of the object to update. Omit to create new. |
| body | dict | Yes | Configuration object body. |

#### `mist_update_org_configuration_objects`

> Update or create a configuration object for an organization. Requires `ENABLE_MIST_WRITE_TOOLS=true`.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| org_id | UUID | Yes | Organization ID. |
| object_type | str | Yes | `alarmtemplates`, `sites`, `wlans`, `sitegroups`, `avprofiles`, `deviceprofiles`, `gatewaytemplates`, `idpprofiles`, `aamwprofiles`, `nactags`, `nacrules`, `networktemplates`, `networks`, `psks`, `rftemplates`, `services`, `servicepolicies`, `sitetemplates`, `vpns`, `webhooks`, `wlantemplates`, `wxrules`, or `wxtags`. |
| object_id | UUID | No | ID of the object to update. Omit to create new. |
| body | dict | Yes | Configuration object body. |

#### `mist_change_site_configuration_objects`

> Create, update, or delete a site-level configuration object. Requires `ENABLE_MIST_WRITE_TOOLS=true`.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| action_type | str | Yes | `create`, `update`, or `delete`. |
| site_id | UUID | Yes | Site ID. |
| object_type | str | Yes | `devices`, `evpn_topologies`, `psks`, `webhooks`, `wlans`, `wxrules`, or `wxtags`. |
| object_id | UUID | No | ID of the object to update or delete. |
| body | dict | No | Configuration object body. Required for create/update. |

#### `mist_change_org_configuration_objects`

> Create, update, or delete an org-level configuration object. Requires `ENABLE_MIST_WRITE_TOOLS=true`.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| action_type | str | Yes | `create`, `update`, or `delete`. |
| org_id | UUID | Yes | Organization ID. |
| object_type | str | Yes | `alarmtemplates`, `sites`, `wlans`, `sitegroups`, `avprofiles`, `deviceprofiles`, `gatewaytemplates`, `idpprofiles`, `aamwprofiles`, `nactags`, `nacrules`, `networktemplates`, `networks`, `psks`, `rftemplates`, `services`, `servicepolicies`, `sitetemplates`, `vpns`, `webhooks`, `wlantemplates`, `wxrules`, or `wxtags`. |
| object_id | UUID | No | ID of the object to update or delete. |
| body | dict | No | Configuration object body. Required for create/update. |

### Guided Prompts

| Prompt | Parameters | Description |
|--------|------------|-------------|
| `provision_site_from_template` | source_site_name, target_site_name, target_address | Clone a site's configuration using org-level templates. Never copies site-level WLANs. |
| `bulk_provision_sites` | source_site_name, site_list_description | Bulk provision multiple sites from a template site. Analyzes source config once, creates each site with template assignments. |

---

## Aruba Central (87 tools + 12 prompts)

### Sites

#### `central_get_sites`

> Returns site configuration data (address, timezone, scopeName) from the network-config API. Use for site details. For health metrics, use `central_get_site_health`.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| filter | str | No | OData 4.0 filter on scopeName, address, city, state, country, zipcode, collectionName. |
| sort | str | No | Sort by scopeName, address, state, country, city, deviceCount, collectionName, zipcode, timezone, longitude, latitude. |
| limit | int | No | Results per page (1-100, default 100). |
| offset | int | No | Pagination offset (default 0). |

#### `central_get_site_health`

> Returns health metrics and device/client counts for sites. For site config data, use `central_get_sites`.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| site_name | str \| list[str] | No | One site name or a list of site names to filter by (exact match). Omit for all sites. |

#### `central_get_site_name_id_mapping`

> Returns a lightweight mapping of all site names to IDs, health scores, and counts.

No parameters. Returns a dict sorted by health score (worst first).

### Devices

#### `central_get_devices`

> Returns a filtered list of devices using OData v4.0 filter syntax.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| site_id | str | No | Site ID or comma-separated list. |
| device_type | str | No | `ACCESS_POINT`, `SWITCH`, or `GATEWAY`. Comma-separated for multiple. |
| device_name | str | No | Device display name. Comma-separated for multiple. |
| serial_number | str | No | Device serial number. Comma-separated for multiple. |
| model | str | No | Device model (e.g. `AP-735-RWF1`). |
| device_function | str | No | Device function classification. |
| is_provisioned | bool | No | True for provisioned devices only. |
| site_assigned | bool | No | True for devices assigned to a site only. |
| sort | str | No | Sort expression (e.g. `deviceName asc, model desc`). |

#### `central_find_device`

> Find a single device by serial number or name. Returns one device or an error message.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| serial_number | str | No | Device serial number (preferred). |
| device_name | str | No | Device display name. Provide only one identifier. |

### AP Monitoring

#### `central_get_aps`

> List access points with AP-specific filters (status, model, firmware, deployment, cluster, site).

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| site_id | str | No | Filter by site ID. |
| site_name | str | No | Filter by site name. |
| serial_number | str | No | AP serial (comma-separated for multiple). |
| device_name | str | No | AP name (comma-separated for multiple). |
| status | str | No | `ONLINE` or `OFFLINE`. |
| model | str | No | AP model (comma-separated). |
| firmware_version | str | No | Firmware version (comma-separated). |
| deployment | str | No | `Standalone`, `Cluster`, or `Unspecified`. |
| sort | str | No | Sort expression (e.g. `deviceName asc`). |

#### `central_get_ap_wlans`

> Get WLANs currently active on a specific AP. Useful for troubleshooting which SSIDs an AP is broadcasting.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| serial_number | str | Yes | AP serial number. |
| wlan_name | str | No | Filter by exact WLAN name (client-side). |

### Device Monitoring

#### `central_get_ap_details`

> Get detailed monitoring data for a specific AP (name, model, status, firmware, clients, radios).

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| serial_number | str | Yes | AP serial number. |

#### `central_get_switch_details`

> Get detailed monitoring data for a specific switch (name, model, status, health reasons).

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| serial_number | str | Yes | Switch serial number. |

#### `central_get_gateway_details`

> Get detailed monitoring data for a specific gateway (interfaces, tunnels, health).

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| serial_number | str | Yes | Gateway serial number. |

### Clients

#### `central_get_clients`

> Returns a filtered list of clients using OData v4.0 filter syntax.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| site_id | str | No | Site ID. |
| site_name | str | No | Site name. |
| serial_number | str | No | Serial number of the connected device. |
| connection_type | str | No | `Wired` or `Wireless`. |
| status | str | No | `Connected` or `Failed`. |
| wlan_name | str | No | WLAN name filter (wireless only). |
| vlan_id | str | No | VLAN ID filter. |
| tunnel_type | str | No | `Port-based`, `User-based`, or `Overlay`. |
| start_query_time | str | No | Start of time window (ISO 8601). |
| end_query_time | str | No | End of time window (ISO 8601). |

#### `central_find_client`

> Find a single client by MAC address.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| mac_address | str | Yes | Client MAC address. |

### Alerts

#### `central_get_alerts`

> Returns a filtered, paginated list of alerts for a specific site. Requires site_id.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| site_id | str | Yes | Site ID. Obtain from `central_get_sites`. |
| status | str | No | Default: `Active`. Also `Cleared` or `Deferred`. |
| device_type | str | No | `Access Point`, `Gateway`, `Switch`, or `Bridge`. |
| category | str | No | `Clients`, `System`, `LAN`, `WLAN`, `WAN`, `Cluster`, `Routing`, or `Security`. |
| sort | str | No | Default: `severity desc`. |
| limit | int | No | Default: 50. Max: 100. |
| cursor | int | No | Pagination cursor from previous `next_cursor`. |

Each returned `Alert` includes a `key` field — pass to the action tools below.

#### `central_get_alert_classification` (v2.3.1.5+)

> Group alerts by a classification dimension and return per-bucket counts.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| classify_by | str | Yes | One of `severity`, `status`, `priority`, `category`, `device_type`, `impacted_devices`. |
| filter | str | No | OData filter (same syntax as `central_get_alerts`). |
| search | str | No | Free-text search over alert name and summary. |

#### `central_get_alert_action_status` (v2.3.1.5+)

> Poll the status of an async alert action (clear / defer / reactivate / set_priority).

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| task_id | str | Yes | Task identifier returned from any of the alert-action tools. |

#### `central_clear_alerts` (v2.3.1.5+)

> Clear (resolve) one or more alerts. Active → Cleared. **Operational** — fires elicitation. Async — returns `task_id`.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| keys | list[str] | Yes | Alert keys (from `central_get_alerts(...)`). |
| reason | str | Yes | One of `Problem was resolved`, `False Positive`, `Insufficient information for troubleshooting`, `Alert is not important`, `Other`. |
| notes | str | No | Free-text notes. |

#### `central_defer_alerts` (v2.3.1.5+)

> Defer one or more alerts until a future time. Active → Deferred. **Operational** — fires elicitation. Async — returns `task_id`.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| keys | list[str] | Yes | Alert keys. |
| defer_until | str | Yes | ISO 8601 datetime, e.g. `2026-05-15T10:00:00Z`. |

#### `central_reactivate_alerts` (v2.3.1.5+)

> Reactivate one or more cleared/deferred alerts. **Operational** — fires elicitation. Async — returns `task_id`.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| keys | list[str] | Yes | Alert keys. |

#### `central_set_alert_priority` (v2.3.1.5+)

> Set operator-assigned priority on one or more alerts. **Operational** — fires elicitation. Async — returns `task_id`.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| keys | list[str] | Yes | Alert keys. |
| priority | str | Yes | One of `Very High`, `High`, `Medium`, `Low`, `Very Low`. |

### Alert Configurations (v2.3.1.6+)

Manage alert *definitions* — the rules that determine when alerts fire (thresholds, durations, severity buckets). Distinct from the alert action tools above which act on already-fired alert instances.

#### `central_get_alert_configs`

> List alert configurations defined at the given scope. Each item shows `inherited` (using parent's config?) and `ruleSource` (`SYSTEM` vs. `USER`).

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| scope_id | str | Yes | Scope identifier. From `central_get_scope_tree` or `central_get_scope_resources`. |
| scope_type | str | No | Default: `GLOBAL`. Also `SITE` or `DEVICE`. |

#### `central_create_alert_config`

> Create a custom alert configuration. **Write** — fires elicitation, gated behind `ENABLE_CENTRAL_WRITE_TOOLS`.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| type_id | str | Yes | Alert type identifier (e.g. `1250` or `CUSTOM-AP-CPU-HIGH`). |
| scope_id | str | Yes | Where to apply the config. |
| enabled | bool | Yes | Whether the alert fires when conditions are met. |
| clear_timeout | str | No | Duration for auto-clear (`1H`, `30D`, `15m`). Pass None to omit. |
| rules | list[dict] | No | Threshold rules. See shape below. |
| scope_type | str | No | Default: `GLOBAL`. Also `SITE` or `DEVICE`. |

Rule shape:

```python
{
    "ruleNumber": 0,
    "duration": 300,
    "conditions": [
        {"severity": "CRITICAL", "operator": "GT", "threshold": 90.0},
        {"severity": "MAJOR",    "operator": "GT", "threshold": 80.0},
    ],
    "additionalConditions": [],
}
```

- Severity: `CRITICAL`, `MAJOR`, `MINOR`, `INFO`
- Operator: `EQ`, `NEQ`, `GT`, `GTE`, `LT`, `LTE`, `IN`, `NIN`

#### `central_update_alert_config`

> Update an existing alert configuration. Partial update — fields you omit are left unchanged. **Write** — fires elicitation.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| type_id | str | Yes | Alert type identifier. |
| scope_id | str | Yes | Scope where the config currently lives. |
| enabled | bool | No | Toggle on/off. Omit to leave unchanged. |
| clear_timeout | str | No | New auto-clear duration. Omit to leave unchanged. |
| rules | list[dict] | No | Replace the rule set. Omit to leave unchanged. |
| scope_type | str | No | Default: `GLOBAL`. Also `SITE` or `DEVICE`. |

#### `central_reset_alert_config`

> Reset to inherited (parent scope) — removes the scope-level override. The alert type is NOT deleted. **Write** — fires elicitation.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| type_id | str | Yes | Alert type identifier of the override to reset. |
| scope_id | str | Yes | Scope where the override currently lives. |
| scope_type | str | No | Default: `GLOBAL`. Also `SITE` or `DEVICE`. |

### Events

#### `central_get_events`

> Retrieve events for a context (site, device, or client) within a time range.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| context_type | str | Yes | `SITE`, `ACCESS_POINT`, `SWITCH`, `GATEWAY`, `WIRELESS_CLIENT`, `WIRED_CLIENT`, or `BRIDGE`. |
| context_identifier | str | Yes | Site ID, device serial, or client MAC. |
| site_id | str | Yes | Site ID to scope events. |
| time_range | str | No | Default: `last_1h`. Options: `last_1h`, `last_6h`, `last_24h`, `last_7d`, `last_30d`, `today`, `yesterday`. |
| start_time | str | No | RFC 3339 format. Overrides time_range with end_time. |
| end_time | str | No | RFC 3339 format. Overrides time_range with start_time. |
| search | str | No | Search by name, serial, hostname, or MAC. |
| limit | int | No | Default: 50. Max: 100. |
| cursor | int | No | Pagination cursor from previous `next_cursor`. |

#### `central_get_events_count`

> Return event count breakdown for a context without fetching full details.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| context_type | str | Yes | `SITE`, `ACCESS_POINT`, `SWITCH`, `GATEWAY`, `WIRELESS_CLIENT`, `WIRED_CLIENT`, or `BRIDGE`. |
| context_identifier | str | Yes | Site ID, device serial, or client MAC. |
| site_id | str | Yes | Site ID to scope events. |
| time_range | str | No | Default: `last_1h`. |
| start_time | str | No | RFC 3339 format. |
| end_time | str | No | RFC 3339 format. |

### WLANs

#### `central_get_wlans`

> List all WLANs/SSIDs configured in Aruba Central.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| site_id | str | No | Filter WLANs by site ID. |
| serial_number | str | No | Filter WLANs served by a specific AP. |
| filter | str | No | OData filter string. |
| sort | str | No | Sort expression (e.g. `essid asc`). |
| limit | int | No | Default: 100. |

#### `central_get_wlan_stats`

> Get throughput trend data (tx/rx time-series in bps) for a specific WLAN over a time window.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| wlan_name | str | Yes | WLAN name (SSID) to get stats for. |
| time_range | str | No | `last_1h` (default), `last_6h`, `last_24h`, `last_7d`, `last_30d`, `today`, `yesterday`. |
| start_time | str | No | RFC 3339 format. Overrides time_range when combined with end_time. |
| end_time | str | No | RFC 3339 format. |

### Audit Logs

#### `central_get_audit_logs`

> Retrieve audit logs within a time window (user actions, config changes, system events).

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| start_at | str | Yes | Start of time window in epoch milliseconds. |
| end_at | str | Yes | End of time window in epoch milliseconds. |
| filter | str | No | OData filter expression. |
| sort | str | No | Sort order (e.g. `+timestamp` or `-timestamp`). |
| limit | int | No | Default: 200. Max: 200. |
| offset | int | No | Default: 1. Page number. |

#### `central_get_audit_log_detail`

> Get the full detail of a single audit log entry.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| id | str | Yes | Audit log entry ID. |

### Statistics

#### `central_get_ap_stats`

> Get performance statistics for a specific AP (radio stats, client counts, throughput).

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| serial_number | str | Yes | AP serial number. |
| start_time | str | No | Start of time window in epoch seconds. |
| end_time | str | No | End of time window in epoch seconds. |
| duration | str | No | Duration shorthand (e.g. `3H`, `1D`, `1W`). |

#### `central_get_ap_utilization`

> Get AP utilization data for CPU, memory, or PoE.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| serial_number | str | Yes | AP serial number. |
| metric | str | Yes | `cpu`, `memory`, or `poe`. |
| start_time | str | No | Start of time window in epoch seconds. |
| end_time | str | No | End of time window in epoch seconds. |
| duration | str | No | Duration shorthand (e.g. `3H`, `1D`, `1W`). |

#### `central_get_gateway_stats`

> Get performance statistics for a specific gateway (interface stats, tunnels, throughput).

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| serial_number | str | Yes | Gateway serial number. |
| start_time | str | No | Start of time window in epoch seconds. |
| end_time | str | No | End of time window in epoch seconds. |
| duration | str | No | Duration shorthand (e.g. `3H`, `1D`, `1W`). |

#### `central_get_gateway_utilization`

> Get gateway utilization data for CPU or memory.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| serial_number | str | Yes | Gateway serial number. |
| metric | str | Yes | `cpu` or `memory`. |
| start_time | str | No | Start of time window in epoch seconds. |
| end_time | str | No | End of time window in epoch seconds. |
| duration | str | No | Duration shorthand (e.g. `3H`, `1D`, `1W`). |

#### `central_get_gateway_wan_availability`

> Get WAN availability data for a gateway (uplink percentages and downtime windows).

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| serial_number | str | Yes | Gateway serial number. |
| start_time | str | No | Start of time window in epoch seconds. |
| end_time | str | No | End of time window in epoch seconds. |
| duration | str | No | Duration shorthand (e.g. `3H`, `1D`, `1W`). |

#### `central_get_tunnel_health`

> Get tunnel health summary for a gateway (VPN/overlay tunnel status and latency).

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| serial_number | str | Yes | Gateway serial number. |

### Applications

#### `central_get_applications`

> Get application usage data for a site (traffic volume, client counts, categorization).

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| site_id | str | Yes | Site ID. |
| start_query_time | str | Yes | Start of time window in epoch milliseconds. |
| end_query_time | str | Yes | End of time window in epoch milliseconds. |
| limit | int | No | Default: 1000. |
| offset | int | No | Default: 0. |
| client_id | str | No | Filter to a specific client ID. |
| filter | str | No | OData filter expression. |
| sort | str | No | Sort order. |

### Troubleshooting

#### `central_ping`

> Initiate a ping test from a device to a destination.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| serial_number | str | Yes | Device serial number. |
| destination | str | Yes | IP address or hostname to ping. |
| device_type | str | Yes | `ap`, `cx`, or `gateway`. |
| count | int | No | Number of pings to send. |
| packet_size | int | No | Ping packet size in bytes. |

#### `central_traceroute`

> Initiate a traceroute from a device to a destination.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| serial_number | str | Yes | Device serial number. |
| destination | str | Yes | IP address or hostname. |
| device_type | str | Yes | `ap`, `cx`, or `gateway`. |

#### `central_cable_test`

> Initiate a cable test on switch ports (cable status and length).

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| serial_number | str | Yes | Switch serial number. |
| device_type | str | Yes | `aos-s` or `cx`. |
| ports | str | Yes | Comma-separated port list (e.g. `1/1/1,1/1/2`). |

#### `central_show_commands`

> Execute show commands on a device and return the output.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| serial_number | str | Yes | Device serial number. |
| device_type | str | Yes | `aos-s`, `cx`, or `gateways`. |
| commands | str | Yes | Comma-separated show commands (e.g. `show version,show interfaces`). |

#### `central_disconnect_users_ssid`

> Disconnect all users from a specific SSID.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| serial_number | str | Yes | AP serial number. |
| ssid | str | Yes | SSID name to disconnect all users from. |

#### `central_disconnect_users_ap`

> Disconnect all users from a specific AP.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| serial_number | str | Yes | AP serial number. |

#### `central_disconnect_client_ap`

> Disconnect a specific client by MAC address from an AP.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| serial_number | str | Yes | AP serial number. |
| mac_address | str | Yes | Client MAC address. |

#### `central_disconnect_client_gateway`

> Disconnect a specific client by MAC address from a gateway.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| serial_number | str | Yes | Gateway serial number. |
| mac_address | str | Yes | Client MAC address. |

#### `central_disconnect_clients_gateway`

> Disconnect all clients from a gateway.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| serial_number | str | Yes | Gateway serial number. |

#### `central_port_bounce_switch`

> Bounce a port on a CX switch to reset link state.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| serial_number | str | Yes | Switch serial number. |
| ports | str | Yes | Comma-separated port list in CX format (e.g. `1/1/1,1/1/2`). |

#### `central_poe_bounce_switch`

> Cycle PoE power on a CX switch port to reset a connected PoE device.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| serial_number | str | Yes | Switch serial number. |
| ports | str | Yes | Comma-separated port list in CX format (e.g. `1/1/1,1/1/2`). |

#### `central_port_bounce_gateway`

> Bounce a port on a gateway to reset link state.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| serial_number | str | Yes | Gateway serial number. |
| ports | str | Yes | Comma-separated port list. |

#### `central_poe_bounce_gateway`

> Cycle PoE power on a gateway port to reset a connected PoE device.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| serial_number | str | Yes | Gateway serial number. |
| ports | str | Yes | Comma-separated port list. |

### WLAN Profiles

#### `central_get_wlan_profiles`

> Read WLAN SSID profiles from Central's configuration library. Returns full config data.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| ssid | str | No | Specific SSID name. If omitted, returns all profiles. |

#### `central_manage_wlan_profile`

> Create, update, or delete a WLAN SSID profile. Requires `ENABLE_CENTRAL_WRITE_TOOLS=true`.
>
> **For cross-platform WLAN sync, use the sync prompts instead of calling this tool directly.**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| ssid | str | Yes | SSID name (used as identifier in API path). |
| action_type | str | Yes | `create`, `update`, or `delete`. |
| payload | dict | Yes | WLAN profile config. For `update` (default), pass only the fields you want to change — the tool issues a `PATCH` and Central merges. For `create`, pass a full profile. For `delete`, payload is ignored. |
| replace_existing | bool | No | Destructive flag. When True, `update` issues a `PUT` that replaces the entire profile — fields not in the payload will be dropped. Default False (safe partial-patch). |
| confirmed | bool | No | Set to true after user confirms update/delete in chat. |

**Update semantics:** By default, `action_type="update"` issues `PATCH /network-config/v1alpha1/wlan-ssids/{ssid}` and the Central API merges the payload with the existing profile server-side. Pass only the fields you want to change; everything else is preserved. The elicitation prompt fetches the current profile and shows a per-field `before → after` diff before applying the change. Set `replace_existing=True` only when you have the complete profile in `payload` and genuinely want a wholesale swap (uses `PUT`).

**Valid `opmode` values** (do NOT invent values — use only these):

`OPEN`, `WPA2_PERSONAL`, `WPA3_SAE`, `WPA2_ENTERPRISE`, `WPA3_ENTERPRISE_CCM_128`,
`WPA3_ENTERPRISE_GCM_256`, `WPA3_ENTERPRISE_CNSA`, `WPA_ENTERPRISE`, `WPA_PERSONAL`,
`WPA2_MPSK_AES`, `WPA2_MPSK_LOCAL`, `ENHANCED_OPEN`, `DPP`, `WPA2_PSK_AES_DPP`,
`WPA2_AES_DPP`, `WPA3_SAE_DPP`, `WPA3_AES_CCM_128_DPP`, `WPA3_AES_GCM_256_DPP`,
`BOTH_WPA_WPA2_PSK`, `BOTH_WPA_WPA2_DOT1X`, `STATIC_WEP`, `DYNAMIC_WEP`

**Other key enums**: `forward-mode`: `FORWARD_MODE_BRIDGE`, `FORWARD_MODE_L2` |
`rf-band`: `BAND_ALL`, `24GHZ_5GHZ`, `5GHZ_6GHZ`, `24GHZ`, `5GHZ`, `6GHZ`, `BAND_NONE` |
`vlan-selector`: `NAMED_VLAN` (with `vlan-name`), `VLAN_RANGES` (with `vlan-id-range`) |
`out-of-service`: `NONE`, `UPLINK_DOWN`, `TUNNEL_DOWN`

### Aliases, Server Groups, Named VLANs

These tools resolve named references used in WLAN profiles. Used by sync prompts
to translate between Central's named/aliased config and Mist's inline config.

#### `central_get_aliases`

> Get alias configurations from Aruba Central. Aliases are named references used in WLAN profiles (SSID aliases, PSK aliases), server groups, and VLAN definitions.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| alias_name | str | No | Specific alias name. If omitted, returns all aliases. |

#### `central_get_server_groups`

> Get RADIUS/auth server group configurations. Resolve a server group name (from a WLAN profile's auth-server-group field) to its actual server addresses and settings.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| name | str | No | Specific server group name. If omitted, returns all groups. |

#### `central_get_named_vlans`

> Get named VLAN configurations. Resolve a named VLAN (from a WLAN profile's vlan-name field) to its actual VLAN ID.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| name | str | No | Specific named VLAN name. If omitted, returns all named VLANs. |

### Write Tools (disabled by default)

#### `central_manage_site`

> Create, update, or delete a site in Aruba Central. Requires `ENABLE_CENTRAL_WRITE_TOOLS=true`.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| action_type | str | Yes | `create`, `update`, or `delete`. |
| payload | dict | Yes | Site payload. All values must use full names (no abbreviations). For create: `address`, `name`, `city`, `state`, `country`, `zipcode`, and `timezone` (object with `timezoneName`, `timezoneId`, `rawOffset` in ms) are required. |
| site_id | str | No | Site ID. Required for update and delete. |

#### `central_manage_site_collection`

> Create, update, delete, or manage sites within a site collection. Requires `ENABLE_CENTRAL_WRITE_TOOLS=true`.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| action_type | str | Yes | `create`, `update`, `delete`, `add_sites`, or `remove_sites`. |
| payload | dict | Yes | For create: `scopeName` required, optional `description`, `siteIds`. For add_sites/remove_sites: `siteIds` list required. |
| collection_id | str | No | Collection ID. Required for update, delete, add_sites, remove_sites. |
| confirmed | bool | No | Set to true after user confirms update/delete in chat. |

#### `central_manage_device_group`

> Create, update, or delete a device group in Aruba Central. Requires `ENABLE_CENTRAL_WRITE_TOOLS=true`.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| action_type | str | Yes | `create`, `update`, or `delete`. |
| payload | dict | Yes | Device group payload. For create: `scopeName` required. Optional: `description`. |
| group_id | str | No | Group ID. Required for update and delete. |

### Config Assignments

#### `central_get_config_assignments`

> Read which configuration profiles are assigned to which scopes and device functions.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| scope_id | str | No | Scope ID to filter. Get from `central_get_scope_tree`. |
| device_function | str | No | Device function filter. `CAMPUS_AP` for WLANs, `ACCESS_SWITCH` for switches, etc. |

#### `central_manage_config_assignment`

> Assign or remove a configuration profile at a scope in Central's hierarchy. Requires `ENABLE_CENTRAL_WRITE_TOOLS=true`. This is how WLAN profiles, roles, and policies get applied to scopes.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| action_type | str | Yes | `assign` or `remove`. |
| scope_id | str | Yes | Scope ID. Get from `central_get_scope_tree`. |
| device_function | str | Yes | `CAMPUS_AP` for WLANs. Others: `ACCESS_SWITCH`, `BRANCH_GW`, `MOBILITY_GW`, `ALL`, etc. |
| profile_type | str | Yes | Profile type: `wlan-ssids`, `roles`, `policies`, `auth-server-groups`, `named-vlans`, `aliases`. |
| profile_instance | str | Yes | Profile name (e.g. the SSID name for WLAN profiles). |
| confirmed | bool | No | Set to true after user confirms. |

### Roles

#### `central_get_roles`

> Get role configurations. Roles define network access (VLAN, QoS, ACLs, bandwidth contracts) for clients and are used in WLAN profiles, switch ports, NAC policies, and firewall rules.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| name | str | No | Specific role name. If omitted, returns all roles. |

#### `central_manage_role`

> Create, update, or delete a role. Requires `ENABLE_CENTRAL_WRITE_TOOLS=true`. Roles can be shared (library) or local (scoped to a site/collection).

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| name | str | Yes | Role name (identifier in API path). |
| action_type | str | Yes | `create`, `update`, or `delete`. |
| payload | dict | Yes | Role config (VLAN, ACLs, QoS, bandwidth, etc.). Empty dict for delete. |
| scope_id | str | No | Scope ID for local roles. Omit for shared/library roles. |
| device_function | str | No | `CAMPUS_AP`, `ACCESS_SWITCH`, `BRANCH_GW`, etc. Required with scope_id. |
| confirmed | bool | No | Set to true after user confirms update/delete. |

### Security & Policy

All tools below follow the same CRUD pattern. Read tools accept an optional `name` to get a specific
resource or omit for all. Write tools accept `name`, `action_type` (create/update/delete), `payload`,
and optional `scope_id` + `device_function` for local (scoped) objects.

#### `central_get_net_groups` / `central_manage_net_group`

> Network groups (netdestinations) — reusable named objects defining hosts, FQDNs, subnets, IP ranges, VLANs, ports for use in ACLs and policies.

#### `central_get_net_services` / `central_manage_net_service`

> Network service definitions — protocol and port combinations (TCP/443, UDP/53, etc.) for identifying traffic types in policies.

#### `central_get_object_groups` / `central_manage_object_group`

> Object groups — named collections of addresses, services, or other objects for ACL references.

#### `central_get_role_acls` / `central_manage_role_acl`

> Role ACLs — access control lists with ordered permit/deny rules referencing net-groups and net-services.

#### `central_get_policies` / `central_manage_policy`

> Firewall policies — ordered rule sets that match traffic and apply actions (permit, deny, NAT, redirect, policy-based routing).

#### `central_get_policy_groups` / `central_manage_policy_group`

> Policy groups — define the evaluation sequence for all firewall policies. Collection-level resource (no per-name path).

#### `central_get_role_gpids` / `central_manage_role_gpid`

> Role GPIDs — map roles to policy group IDs. Controls which policy group is assigned to each role.

### Gateway Clustering (since v2.5.2.0)

#### `central_get_gateway_cluster_intent_profiles` / `central_manage_gateway_cluster_intent_profile`

> Read or manage Gateway Cluster Intent (GCIS) profiles — the policy/intent layer for AOS 10 gateway clusters. An intent profile bound at a scope (Global / Site Collection / Site) declares cluster behavior and Central auto-forms realized cluster profiles per the intent. Key field: `cluster-mode` (`CM_SITE` for auto-clustering at Site level, or `CM_MANUAL` to disable auto-formation). Other fields: `device-type` (persona — MOBILITY_GW, BRANCH_GW, VPNC, CAMPUS_AP, MICROBRANCH_AP, etc.), `multicast-vlan`, `heartbeat-threshold`, `coa-vrrp`, `default-gateway-mode` (1:1 redundancy), `uplink-tracking`, `uplink-sharing`, `ipv6-enable`. The realized cluster profiles for CM_SITE intents are auto-created with `auto_*` naming. Manage tool gated by `ENABLE_CENTRAL_WRITE_TOOLS=true`. API: `network-config/v1alpha1/gw-cluster-intent-config`.

#### `central_get_gateway_clusters` / `central_manage_gateway_cluster`

> Read or manage realized gateway cluster profiles. Each profile contains the actual member gateways (keyed by MAC, not IP — up to 12 per profile, fewer on some platforms) and runtime configuration (heartbeat, multicast VLAN, CoA-VRRP, redundancy mode). For GCIS-managed CM_SITE clusters, Central creates and maintains realized profiles automatically (`auto_*` naming). For manual (CM_MANUAL) clusters, operators create them directly here with explicit member MACs. Key field: `auto-cluster` (false for manual clusters; true is reserved for GCIS-managed). Manual cluster names cannot start with `auto_` or contain spaces. `ipv6-enable` is set-once at creation. Manage tool gated by `ENABLE_CENTRAL_WRITE_TOOLS=true`. API: `network-config/v1alpha1/gateway-clusters`.

### Firmware

#### `central_recommend_firmware`

> Applies an LSR-preferred upgrade policy on top of Central's built-in `recommendedVersion`. The LSR/SSR classification comes directly from the `firmwareClassification` field in the firmware-details API response — no hand-maintained mapping. For devices classified as SSR, the "next LSR" target is mined live from the same response: the highest LSR version observed across the fleet for that device type.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| serial_number | str | No | Narrow to one device. |
| device_type | str | No | `ACCESS_POINT`, `SWITCH`, or `GATEWAY`. Filtering this narrows the pool used to mine the newest LSR target for SSR devices — leave unset for best SSR recommendations. |
| site_id | str | No | Limit to a site by ID. |
| site_name | str | No | Limit to a site by exact name. |
| include_up_to_date | bool | No | If True, include devices already on Central's recommended version. Default False. |
| max_pages | int | No | Safety cap on paginated fetches (1000 items × max_pages). Default 10. |

**Policy:**

- Classified **LSR** → upgrade in place to Central's recommended version (latest in same train).
- Classified **SSR** → move to the newest LSR version seen in the fleet for that device type (mined live).
- Classified **empty / unclassified** (typically AOS 8) → pass Central's recommendation through.
- No LSR device of the same type in the fleet → SSR devices fall back to Central's recommendation with a note.

**Returned report:**

- `discovered_lsr_targets` — `{device_type: newest LSR version}` mined from the response. Empty if no LSR devices were observed.
- `total_devices_scanned`, `up_to_date`, `on_lsr`, `on_ssr`, `unclassified`, `needs_action` — fleet-level counts.
- `recommendations[]` — per-device records: current version, release type (`LSR`/`SSR`/`UNCLASSIFIED`), Central's recommendation, our recommendation, action (`upgrade_in_place`, `move_to_lsr_train`, `follow_central`, `up_to_date`), and a rationale string.

### Guided Prompts

Prompts are pre-built workflows that chain multiple tools together. They guide the
LLM through a recommended sequence of tool calls for common network operations.

| Prompt | Parameters | Description |
|--------|-----------|-------------|
| `network_health_overview` | (none) | Full network health overview across all sites. |
| `troubleshoot_site` | site_name | Deep-dive troubleshooting for a specific site. |
| `client_connectivity_check` | mac_address | Investigate a client's connectivity and related site health. |
| `investigate_device_events` | serial_number, time_range | Investigate recent events for a specific device. |
| `site_event_summary` | site_name, time_range | Summarize all events at a site to identify patterns. |
| `failed_clients_investigation` | site_name | Find and diagnose all failed clients at a site. |
| `site_client_overview` | site_name | Overview of all client connectivity at a site. |
| `device_type_health` | site_name, device_type | Health check for all devices of a type at a site. |
| `critical_alerts_review` | (none) | Review all active critical alerts across the network. |
| `compare_site_health` | site_names (list) | Compare health metrics across multiple sites. |
| `scope_configuration_overview` | scope_name | View committed configuration resources at a scope with category grouping. |
| `scope_effective_config` | scope_name | View effective (inherited + committed) configuration as a layered inheritance view. |

---

## Cross-Platform (3 tools + 3 prompts)

Tools that span multiple platforms. Each replaces several individual tool calls with a single aggregated response.

### `site_health_check`

> **One-call site health snapshot across every enabled platform.** Aggregates Mist, Central, and (optionally) ClearPass into a single compact report. Replaces ~8–12 separate tool calls. Registered when at least Mist or Central is enabled; ClearPass is additive.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| site_name | str | Yes | Exact site name as shown in Mist and/or Central. |
| time_window_hours | int | No | Lookback window for alarms, sessions, and events (1–168, default 24). |

**What it returns:**

- `overall_status` — `healthy`, `degraded`, `critical`, or `unknown`.
- `headline` — One-line summary suitable for the user.
- `mist` — Site stats (device/client counts, connected/offline), top alarms, critical count.
- `central` — Health score, device/client totals, active alerts, critical count, top alerts.
- `clearpass` — NADs matched to the site's device IPs, active session count, recent auth-failure count (when ClearPass is configured).
- `recommendations` — Concrete follow-up tool calls with the right site_id already filled in, targeting only the platforms and categories that showed issues.

**Typical use:** "How is site X doing?", "Is site X healthy?", "Give me a status on site X." After reviewing the summary, follow the recommendations for deeper investigation — do not re-query the per-platform health tools unless needed.

### `site_rf_check`

> **One-call RF / channel-planning snapshot across every enabled platform.** Aggregates per-AP, per-band radio state from Mist AND Central in parallel — current channel, bandwidth, TX power, channel utilization, and noise floor — into a single report with an embedded ASCII RF dashboard. Replaces 10+ separate per-platform calls. Registered when at least Mist or Central is enabled.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| site_name | str | No | Exact site name as shown in Mist and/or Central. When omitted, the tool returns a list of selectable sites (with AP counts per platform) in `site_options` instead of a full RF report — call back with one of those names. |
| platform | str \| list \| null | No | Optional filter (`mist`, `central`, or both as a list). Omit (null) for the default cross-platform aggregation. ClearPass / Apstra / GreenLake are not valid — they don't expose per-AP RF telemetry. |
| max_aps_per_platform | int | No | Cap on per-AP detail fetches per platform (Central fans out serial-by-serial). Default 50; range 1–500. |
| include_rendered_report | bool | No | When true (default), embed a pre-rendered markdown/ASCII RF dashboard in `rendered_report`. Set false for scripted callers that only want structured data. |

**What it returns:**

- `headline` — One-line summary (`Site 'X': N/M APs online | 2.4GHz: ch1×2... | 5GHz: ...`).
- `bands` — Per-band (2.4 / 5 / 6) summary: AP count, channel distribution, avg/max utilization, avg noise floor, allowed channels (from the Mist RF template).
- `aps` — Per-AP radio snapshot: name, model, platform, connected status, and a list of radios (one per band) with channel / bandwidth / power / utilization / noise.
- `mist` — Mist-side metadata: site_id, AP count, RF template name, allowed channels per band.
- `central` — Central-side metadata: site_id, AP count, online count.
- `recommendations` — Co-channel cluster warnings (3+ APs on the same primary channel in 5/6 GHz), high-utilization warnings (peak ≥70%), elevated-noise-floor warnings (>-70 dBm).
- `site_options` — Populated only when `site_name` is omitted. Each entry: name, platform, site_id, ap_count, online_ap_count.
- `rendered_report` — Pre-formatted markdown/ASCII dashboard. Includes per-band channel-occupancy bars, utilization meters, a per-AP table, and the recommendations list. Designed to render directly even in clients that don't draw charts.

**Typical use:** "Show me 5 GHz / 6 GHz channels at site X", "How is RF doing at site X?", "Channel planning report for site X", "Are any APs on the same channel?" Use this *instead of* picking one vendor's RF tools — even when only one platform's APs are at the site, the cross-platform call is cheap and surfaces both sides cleanly.

### `manage_wlan_profile`

> **Primary entry point for all WLAN operations.** Automatically checks both Mist and Central for the SSID and returns the correct workflow. Detects cross-platform scenarios without relying on AI instructions.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| ssid | str | Yes | The SSID name to create, update, delete, or sync. |
| action_type | str | Yes | `create`, `update`, `delete`, or `sync`. |
| target_platform | str | No | `central`, `mist`, or `both` (default). |
| payload | dict | No | WLAN profile payload for create/update. Empty dict for sync/delete. |

**Behavior by scenario:**

| Scenario | Response |
|----------|----------|
| SSID in Mist only, target Central | Mist→Central sync workflow with field mapping and scope assignment |
| SSID in Central only, target Mist | Central→Mist sync workflow with alias resolution |
| SSID on both platforms | Returns both configs, asks user to choose source |
| New SSID (neither platform) | Directs to platform-specific create tool |
| action_type="sync" | Compares both platforms regardless of target |

### Prompts

| Prompt | Parameters | Description |
|--------|-----------|-------------|
| `sync_wlans_mist_to_central` | (none) | Sync WLAN profiles from Mist to Central with full field mapping and scope assignment. |
| `sync_wlans_central_to_mist` | (none) | Sync WLAN profiles from Central to Mist with alias resolution and template variables. |
| `sync_wlans_bidirectional` | (none) | Compare WLANs across both platforms, show field-level differences, sync in either direction. |

---

## HPE GreenLake (10 tools)

GreenLake uses the same dynamic-mode meta-tool pattern as every other platform since v2.0.0.0. In the default `MCP_TOOL_MODE=dynamic`, the AI sees `greenlake_list_tools`, `greenlake_get_tool_schema`, and `greenlake_invoke_tool` and discovers the 10 underlying tools below through them. The v1.x endpoint-dispatch tools (`greenlake_list_endpoints`, `greenlake_get_endpoint_schema`, `greenlake_invoke_endpoint`) are **removed** in v2.0.

All 10 GreenLake tools are read-only today. Write tools would follow the same gating pattern as the other platforms (tag + `ENABLE_GREENLAKE_WRITE_TOOLS`) when/if they're added.

#### `greenlake_get_audit_logs`

> Retrieve GreenLake audit logs with optional OData filtering and pagination.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| filter | str | No | OData filter expression. Values in single quotes. |
| select | str | No | Comma-separated properties to include. |
| all | str | No | Free-text search across all properties. |
| limit | int | No | Default: 50. Max: 2000. |
| offset | int | No | Zero-based offset for pagination. |

#### `greenlake_get_audit_log_details`

> Get additional detail for a single GreenLake audit log entry.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| id | str | Yes | Audit log record ID (must have `hasDetails=true`). |

#### `greenlake_get_devices`

> List devices managed in a GreenLake workspace with filtering, sorting, and pagination.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| filter | str | No | OData filter expression. Values in single quotes. |
| filter_tags | str | No | Tag filter expression. |
| sort | str | No | Sort expressions (e.g. `serialNumber,macAddress desc`). |
| select | list[str] | No | Property names to include. |
| limit | int | No | Default: 2000. |
| offset | int | No | Zero-based offset for pagination. |

#### `greenlake_get_device_by_id`

> Get details on a specific GreenLake device by its resource ID.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| id | str | Yes | Device resource ID. |

#### `greenlake_get_subscriptions`

> List subscriptions in a GreenLake workspace with filtering, sorting, and pagination.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| filter | str | No | OData filter expression. Values in single quotes. |
| filter_tags | str | No | Tag filter expression. |
| sort | str | No | Sort expressions. |
| select | list[str] | No | Property names to include. |
| limit | int | No | Default: 50. |
| offset | int | No | Zero-based offset for pagination. |

#### `greenlake_get_subscription_details`

> Get detailed information for a single GreenLake subscription by ID.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| id | str | Yes | Subscription ID. |

#### `greenlake_get_users`

> List users in a GreenLake workspace with OData filtering and pagination.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| filter | str | No | OData filter expression. Values in single quotes. |
| limit | int | No | Default: 300. Max: 600. |
| offset | int | No | Pagination offset (number of pages to skip). |

#### `greenlake_get_user_details`

> Retrieve a single GreenLake user by user ID.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| id | str | Yes | User ID. |

#### `greenlake_get_workspace`

> Retrieve basic workspace information for a given GreenLake workspace ID.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| workspaceId | str | Yes | Workspace ID. |

#### `greenlake_get_workspace_details`

> Retrieve contact information for a GreenLake workspace.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| workspaceId | str | Yes | Workspace ID. |

---

## Aruba ClearPass (140 tools)

ClearPass tools use the `pyclearpass` SDK with OAuth2 client credentials. Write tools require
`ENABLE_CLEARPASS_WRITE_TOOLS=true`. Update/delete operations require user confirmation.

### Network Devices (4 read + 1 write)

| Tool | Description |
|------|-------------|
| `clearpass_get_network_devices` | List or get NADs (RADIUS/TACACS+ clients) by ID or name |
| `clearpass_get_network_device_stats` | Get detailed device record by ID |
| `clearpass_test_device_connectivity` | Fetch device record for connectivity review |
| `clearpass_validate_device_config` | Validate device configuration for missing fields |
| `clearpass_manage_network_device` | Create, update, delete, clone, configure SNMP/RadSec/CLI/on-connect |

### Guest Management (1 read + 4 write)

| Tool | Description |
|------|-------------|
| `clearpass_get_guest_users` | List or get guest users by ID or username |
| `clearpass_manage_guest_user` | Create, update, delete guest users |
| `clearpass_send_guest_credentials` | Send credentials via SMS or email (`delivery_method`: sms/email) |
| `clearpass_generate_guest_pass` | Generate digital pass or receipt (`pass_type`: digital/receipt) |
| `clearpass_process_sponsor_action` | Approve or reject guest sponsorship requests |

### Guest Configuration (5 read + 4 write)

| Tool | Description |
|------|-------------|
| `clearpass_get_pass_templates` | List or get digital pass templates |
| `clearpass_get_print_templates` | List or get print receipt templates |
| `clearpass_get_weblogin_pages` | List or get captive portal web login pages |
| `clearpass_get_guest_auth_settings` | Get guest authentication global settings |
| `clearpass_get_guest_manager_settings` | Get guest manager global settings |
| `clearpass_manage_pass_template` | Create, update, replace, delete pass templates |
| `clearpass_manage_print_template` | Create, update, replace, delete print templates |
| `clearpass_manage_weblogin_page` | Create, update, replace, delete web login pages |
| `clearpass_manage_guest_settings` | Update guest authentication and manager settings |

### Endpoints (2 read + 1 write)

| Tool | Description |
|------|-------------|
| `clearpass_get_endpoints` | List or get endpoints by ID or MAC address |
| `clearpass_get_endpoint_profiler` | Get device profiler fingerprint data |
| `clearpass_manage_endpoint` | Create, update, delete endpoints |

### Endpoint Visibility (4 read)

| Tool | Description |
|------|-------------|
| `clearpass_get_onguard_activity` | List active OnGuard posture sessions; lookup by `activity_id` or `mac` |
| `clearpass_get_fingerprint_dictionary` | List or get profiler fingerprint dictionary entries (DHCP/HTTP/etc.) |
| `clearpass_get_network_scan` | List or get network discovery scan jobs |
| `clearpass_get_onguard_settings` | Get OnGuard posture engine settings (`global_settings: bool` for cluster-wide) |

### Certificate Authority (2 read + 2 write)

| Tool | Description |
|------|-------------|
| `clearpass_get_certificates` | List or get internal-CA certificates; `chain=true` returns the issuer chain |
| `clearpass_get_onboard_devices` | List or get onboarded-device CA records (distinct from `/api/device` identity records) |
| `clearpass_manage_certificate_authority` | CA cert lifecycle: import, new, request, sign, revoke, reject, export, delete |
| `clearpass_manage_onboard_device` | Update or delete onboard device records |

### Session Control (3 read + 2 write)

| Tool | Description |
|------|-------------|
| `clearpass_get_sessions` | List active sessions or get session by ID |
| `clearpass_get_session_action_status` | Check status of disconnect/CoA action |
| `clearpass_get_reauth_profiles` | Get reauthorization profiles for a session |
| `clearpass_disconnect_session` | Disconnect session(s) — `target_type`: session_id/username/mac/ip/bulk |
| `clearpass_perform_coa` | Change of Authorization — `target_type`: session_id/username/mac/ip/bulk |

### Roles & Role Mappings (2 read + 2 write)

| Tool | Description |
|------|-------------|
| `clearpass_get_roles` | List or get roles by ID or name |
| `clearpass_get_role_mappings` | List or get role mappings by ID or name |
| `clearpass_manage_role` | Create, update, delete roles |
| `clearpass_manage_role_mapping` | Create, update, delete role mappings |

### Enforcement (3 read + 2 write)

| Tool | Description |
|------|-------------|
| `clearpass_get_enforcement_policies` | List or get enforcement policies |
| `clearpass_get_enforcement_profiles` | List or get enforcement profiles |
| `clearpass_get_profile_templates` | Reference list of common enforcement profile patterns |
| `clearpass_manage_enforcement_policy` | Create, update, delete enforcement policies |
| `clearpass_manage_enforcement_profile` | Create, update, delete enforcement profiles |

### Authentication (4 read + 2 write)

| Tool | Description |
|------|-------------|
| `clearpass_get_auth_sources` | List or get authentication sources (LDAP/AD/RADIUS) |
| `clearpass_get_auth_source_status` | Get auth source connection status and statistics |
| `clearpass_test_auth_source` | Fetch auth source details for connectivity review |
| `clearpass_get_auth_methods` | List or get authentication methods (EAP, certificates) |
| `clearpass_manage_auth_source` | Create, update, delete, configure_backup, configure_filters, configure_radius_attrs |
| `clearpass_manage_auth_method` | Create, update, delete authentication methods |

### Certificates (5 read + 2 write)

| Tool | Description |
|------|-------------|
| `clearpass_get_trust_list` | List or get certificate trust list entries |
| `clearpass_get_client_certificates` | List or get client certificates |
| `clearpass_get_server_certificates` | List or get server certificates |
| `clearpass_get_service_certificates` | List service certificates |
| `clearpass_get_revocation_list` | List or get certificate revocation lists (CRLs) |
| `clearpass_manage_certificate` | Import/delete trust list, delete client cert, enable/disable server cert |
| `clearpass_create_csr` | Generate Certificate Signing Request |

### Audit & Insight (5 read + 3 write)

| Tool | Description |
|------|-------------|
| `clearpass_get_audit_logs` | Get admin login audit records by username |
| `clearpass_get_system_events` | List system events with filtering |
| `clearpass_get_insight_alerts` | List or get Insight alert configurations |
| `clearpass_get_insight_reports` | List or get Insight report configurations |
| `clearpass_get_endpoint_insights` | Endpoint insights by MAC, IP, IP range, or time range |
| `clearpass_manage_insight_alert` | Create, update, delete, enable, disable, mute, unmute alerts |
| `clearpass_manage_insight_report` | Create, delete, enable, disable, run reports |
| `clearpass_create_system_event` | Create a custom system event |

### Identities (6 read + 5 write)

| Tool | Description |
|------|-------------|
| `clearpass_get_api_clients` | List or get API clients |
| `clearpass_get_local_users` | List or get local users |
| `clearpass_get_static_host_lists` | List or get static host lists |
| `clearpass_get_devices` | List or get devices by ID or MAC |
| `clearpass_get_deny_listed_users` | List or get deny-listed users |
| `clearpass_get_external_accounts` | List or get external account records by ID or name |
| `clearpass_manage_api_client` | Create, update, delete API clients |
| `clearpass_manage_local_user` | Create, update, delete local users |
| `clearpass_manage_static_host_list` | Create, update, delete static host lists |
| `clearpass_manage_device` | Create, update, delete devices |
| `clearpass_manage_deny_listed_user` | Create, delete deny-listed users |

### Policy Elements (8 read + 7 write)

| Tool | Description |
|------|-------------|
| `clearpass_get_services` | List or get configuration services |
| `clearpass_get_posture_policies` | List or get posture policies |
| `clearpass_get_device_groups` | List or get network device groups |
| `clearpass_get_proxy_targets` | List or get proxy targets |
| `clearpass_get_radius_dictionaries` | List or get RADIUS dictionaries |
| `clearpass_get_tacacs_dictionaries` | List or get TACACS+ service dictionaries |
| `clearpass_get_application_dictionaries` | List or get application dictionaries |
| `clearpass_get_radius_dynamic_authorization_template` | List or get RADIUS Dynamic Authorization (DUR) templates |
| `clearpass_manage_service` | Create, update, delete, enable, disable config services |
| `clearpass_manage_device_group` | Create, update, delete device groups |
| `clearpass_manage_posture_policy` | Create, update, delete posture policies |
| `clearpass_manage_proxy_target` | Create, update, delete proxy targets |
| `clearpass_manage_radius_dictionary` | Create, update, delete, enable, disable RADIUS dictionaries |
| `clearpass_manage_tacacs_dictionary` | Create, update, delete TACACS+ dictionaries |
| `clearpass_manage_application_dictionary` | Create, update, delete application dictionaries |

### Server Configuration (13 read + 12 write)

| Tool | Description |
|------|-------------|
| `clearpass_get_admin_users` | List or get admin users |
| `clearpass_get_admin_privileges` | List or get admin privilege sets |
| `clearpass_get_operator_profiles` | List or get operator profiles |
| `clearpass_get_licenses` | List licenses, get details, or get summary |
| `clearpass_get_cluster_params` | Get cluster parameters |
| `clearpass_get_password_policies` | Get admin and local user password policies |
| `clearpass_get_attributes` | List or get custom attributes |
| `clearpass_get_data_filters` | List or get data filters |
| `clearpass_get_file_backup_servers` | List or get file backup servers |
| `clearpass_get_messaging_setup` | Get messaging (email/SMS) configuration |
| `clearpass_get_snmp_trap_receivers` | List or get SNMP trap receivers |
| `clearpass_get_policy_manager_zones` | List or get policy manager zones |
| `clearpass_get_oauth_privileges` | Get OAuth privileges |
| `clearpass_manage_admin_user` | Create, update, delete admin users |
| `clearpass_manage_admin_privilege` | Create, update, delete admin privileges |
| `clearpass_manage_operator_profile` | Create, update, delete operator profiles |
| `clearpass_manage_license` | Create, delete, activate_online, activate_offline |
| `clearpass_manage_cluster_params` | Update cluster parameters |
| `clearpass_manage_password_policy` | Update admin or local user password policies |
| `clearpass_manage_attribute` | Create, update, delete attributes |
| `clearpass_manage_data_filter` | Create, update, delete data filters |
| `clearpass_manage_file_backup_server` | Create, update, delete backup servers |
| `clearpass_manage_messaging_setup` | Create, update, delete messaging config |
| `clearpass_manage_snmp_trap_receiver` | Create, update, delete SNMP trap receivers |
| `clearpass_manage_policy_manager_zone` | Create, update, delete policy manager zones |

### Local Configuration (7 read + 5 write)

| Tool | Description |
|------|-------------|
| `clearpass_get_access_controls` | Get server access controls by UUID and/or resource |
| `clearpass_get_ad_domains` | List or get Active Directory domains |
| `clearpass_get_server_version` | Get ClearPass version, cluster info |
| `clearpass_get_fips_status` | Get server FIPS status |
| `clearpass_get_server_services` | List or get server services |
| `clearpass_get_server_snmp` | Get server SNMP configuration |
| `clearpass_get_cluster_servers` | List all cluster nodes (UUID, name, IP, role) — discovery for `server_uuid` |
| `clearpass_manage_access_control` | Update, delete server access controls |
| `clearpass_manage_ad_domain` | Join, leave, configure_password_servers for AD domains |
| `clearpass_manage_cluster_server` | Update cluster server configuration |
| `clearpass_manage_server_service` | Start, stop server services |
| `clearpass_manage_service_params` | PATCH per-server service parameters — used for cluster-consistency audits |

### Integrations (7 read + 4 write)

| Tool | Description |
|------|-------------|
| `clearpass_get_extensions` | List or get extension instances |
| `clearpass_get_syslog_targets` | List or get syslog targets |
| `clearpass_get_syslog_export_filters` | List or get syslog export filters |
| `clearpass_get_event_sources` | List or get event sources |
| `clearpass_get_context_servers` | List or get context server actions |
| `clearpass_get_endpoint_context_servers` | List or get endpoint context servers |
| `clearpass_get_extension_log` | Fetch logs for a specific extension instance (`tail` for last N lines) |
| `clearpass_manage_extension` | Start, stop, restart, delete extensions |
| `clearpass_manage_syslog_target` | Create, update, delete syslog targets |
| `clearpass_manage_syslog_export_filter` | Create, update, delete syslog export filters |
| `clearpass_manage_endpoint_context_server` | Create, update, delete, trigger_poll context servers |

### Utilities (1 tool)

| Tool | Description |
|------|-------------|
| `clearpass_generate_random_password` | Generate random password or MPSK |

For ClearPass API reachability, use the cross-platform `health(platform="clearpass")` tool (the v1.x `clearpass_test_connection` tool was removed in v2.0).

---

## Juniper Apstra (19 tools)

Ported from a standalone Apstra MCP server. Requires Apstra credentials in
Docker secrets (`apstra_server`, `apstra_username`, `apstra_password`, plus
optional `apstra_port` (default 443) and `apstra_verify_ssl` (default true)).
Write tools require `ENABLE_APSTRA_WRITE_TOOLS=true` and go through the
elicitation confirmation flow.

### Health and Meta (2 tools)

| Tool | Description |
|------|-------------|
| `apstra_health` | Server health plus live login probe of the configured Apstra server |
| `apstra_formatting_guidelines` | Full formatting guidance for Apstra output |

### Blueprints (2 tools)

| Tool | Description |
|------|-------------|
| `apstra_get_blueprints` | List all blueprints (id, label, design, status) |
| `apstra_get_templates` | List design templates available for new blueprints |

### Topology (3 tools)

| Tool | Description |
|------|-------------|
| `apstra_get_racks` | All racks in a blueprint (`blueprint_id`) |
| `apstra_get_routing_zones` | Security zones / VRFs in a blueprint (`blueprint_id`) |
| `apstra_get_system_info` | Systems (spines, leafs, redundancy groups) in a blueprint (`blueprint_id`) |

### Virtual Networks (2 tools)

| Tool | Description |
|------|-------------|
| `apstra_get_virtual_networks` | VNs with bound systems and VLAN IDs (`blueprint_id`) |
| `apstra_get_remote_gateways` | Remote EVPN gateways in a blueprint (`blueprint_id`) |

### Connectivity Templates (2 tools)

| Tool | Description |
|------|-------------|
| `apstra_get_connectivity_templates` | Policy templates visible for assignment (`blueprint_id`) |
| `apstra_get_application_endpoints` | Interfaces available as CT attachment points (`blueprint_id`) |

### Status (3 tools)

| Tool | Description |
|------|-------------|
| `apstra_get_anomalies` | Active anomalies in a blueprint (`blueprint_id`) |
| `apstra_get_diff_status` | Staging vs active-version diff (`blueprint_id`) |
| `apstra_get_protocol_sessions` | BGP and other protocol sessions (`blueprint_id`) |

### Management (write, destructive)

| Tool | Description |
|------|-------------|
| `apstra_deploy` | Deploy a staged version to the fabric (`blueprint_id`, `description`, `staging_version`, `confirmed`) |
| `apstra_delete_blueprint` | Permanently delete a blueprint (`blueprint_id`, `confirmed`) |

### Management (write, create)

| Tool | Description |
|------|-------------|
| `apstra_create_datacenter_blueprint` | Instantiate a new datacenter blueprint from a template |
| `apstra_create_freeform_blueprint` | Create a new freeform blueprint |
| `apstra_create_virtual_network` | Create a VXLAN or VLAN virtual network via `virtual-networks-batch` |
| `apstra_create_remote_gateway` | Create a remote EVPN gateway |
| `apstra_apply_ct_policies` | Apply or remove connectivity-template policies on interfaces |

---

## Axis Atmos Cloud (25 tools)

Axis tools wrap the Axis Atmos Cloud Admin API
(`https://admin-api.axissecurity.com/api/v1.0`). Auth is a static JWT
bearer token generated in the Axis admin portal at *Settings → Admin API
→ New API Token* — there is no refresh endpoint, so the server decodes
the token's `exp` claim at startup and surfaces a `token_expires_in_days`
countdown when inside the 30-day warning window. Write tools require
`ENABLE_AXIS_WRITE_TOOLS=true`; every write **stages** in Axis and the
caller must invoke `axis_commit_changes` to apply pending edits — the
same workflow Axis enforces for changes made through the admin UI.

All read tools accept optional `page_number` (1-indexed) and
`page_size` (max 100) parameters. The Axis API uses offset-based
pagination with a `PagedApiResponse<IEnumerable<T>>` envelope; the
response is passed through unchanged so callers see `totalRecords`,
`totalPages`, and `nextPage`/`firstPage`/`lastPage` cursors.

### Connectors (1 read + 1 write + 1 action)

| Tool | Description |
|------|-------------|
| `axis_get_connectors` | List or get connectors (tunnel-endpoint devices) by GUID |
| `axis_manage_connector` | Create, update, or delete a connector. Stages — call `axis_commit_changes` |
| `axis_regenerate_connector` | Issue a fresh installation command for an existing connector. **Invalidates the prior install command.** Immediate (not staged) |

### Tunnels (1 read + 1 write)

| Tool | Description |
|------|-------------|
| `axis_get_tunnels` | List or get tunnels by GUID |
| `axis_manage_tunnel` | Create, update, or delete a tunnel. Stages — call `axis_commit_changes` |

### Connector Zones (1 read + 1 write)

| Tool | Description |
|------|-------------|
| `axis_get_connector_zones` | List or get connector zones (groupings of connectors) |
| `axis_manage_connector_zone` | Create, update, or delete a connector zone. Stages — call `axis_commit_changes` |

### Locations and Sub-Locations (2 read + 2 write)

| Tool | Description |
|------|-------------|
| `axis_get_locations` | List or get locations (physical sites) |
| `axis_get_sub_locations` | List or get sub-locations under a parent location (location-scoped) |
| `axis_manage_location` | Create, update, or delete a location. Stages — call `axis_commit_changes` |
| `axis_manage_sub_location` | Create, update, or delete a sub-location under a parent location. Stages |

### Status (cross-entity helper)

| Tool | Description |
|------|-------------|
| `axis_get_status` | Runtime status for a connector or tunnel (`entity_type='connector' \| 'tunnel'`, `entity_id=GUID`). Connector status returns rich telemetry — CPU/memory/disk/network, hostname, OS version. Tunnel status returns connection state |

### Identity — Users and Groups (2 read + 2 write)

| Tool | Description |
|------|-------------|
| `axis_get_users` | List or get Axis IdP users |
| `axis_get_groups` | List or get IdP user groups |
| `axis_manage_user` | Create, update, or delete a user. Stages — call `axis_commit_changes` |
| `axis_manage_group` | Create, update, or delete a group. Stages — call `axis_commit_changes` |

### Applications and Application Groups (2 read + 2 write)

| Tool | Description |
|------|-------------|
| `axis_get_applications` | List or get published applications |
| `axis_get_application_groups` | List or get application groups (referred to as "tags" in the API) |
| `axis_manage_application` | Create, update, or delete an application. Stages — call `axis_commit_changes` |
| `axis_manage_application_group` | Create, update, or delete an application group / tag. Stages |

### Web Categories (1 read + 1 write)

| Tool | Description |
|------|-------------|
| `axis_get_web_categories` | List or get URL-classification categories used in policy |
| `axis_manage_web_category` | Create, update, or delete a web category. Stages — call `axis_commit_changes` |

### SSL Exclusions (1 read + 1 write)

| Tool | Description |
|------|-------------|
| `axis_get_ssl_exclusions` | List or get hosts excluded from SSL inspection |
| `axis_manage_ssl_exclusion` | Create, update, or delete an SSL exclusion. Stages — call `axis_commit_changes` |

### Commit (1 tool)

| Tool | Description |
|------|-------------|
| `axis_commit_changes` | `POST /Commit` — apply ALL pending staged writes for the tenant. Tenant-wide; no per-change selection. Uses a 60s timeout because commit can take a while when there's a lot staged |

### Currently disabled (kept on disk, off the registry)

These endpoints exist in the Axis swagger but return 403 even with
fully-scoped tokens — Axis appears to gate them server-side without a
corresponding scope toggle in the admin portal (likely
unreleased / hidden APIs). The implementations stay on disk so
re-enabling is a one-line move from `_DISABLED_TOOLS` back into `TOOLS`
in `platforms/axis/__init__.py` if Axis ever flips them on.

| Tool | Endpoint |
|------|----------|
| `axis_get_custom_ip_categories` | `GET /api/v1.0/IpCategories` |
| `axis_manage_custom_ip_category` | `POST/PUT/DELETE /api/v1.0/IpCategories` |
| `axis_get_ip_feed_categories` | `GET /api/v1.0/IpCategoriesFeed` |
| `axis_manage_ip_feed_category` | `POST/PUT/DELETE /api/v1.0/IpCategoriesFeed` |

## Aruba OS 8 / Mobility Conductor (47 tools + 9 prompts)

Tools are exposed in dynamic mode by default via 3 meta-tools (`aos8_list_tools`,
`aos8_get_tool_schema`, `aos8_invoke_tool`). Set `MCP_TOOL_MODE=static` to expose
each underlying tool individually. Write tools require `ENABLE_AOS8_WRITE_TOOLS=true`.

### Health & Inventory (8)

| Tool | Purpose |
|---|---|
| `aos8_get_controllers` | List all controllers/MDs under the Conductor with status and role |
| `aos8_get_ap_database` | Full AP database (name, MAC, IP, model, status, AP group) |
| `aos8_get_active_aps` | Currently up APs with association counts |
| `aos8_get_ap_detail` | Detailed stats for a single AP by name or MAC |
| `aos8_get_bss_table` | BSS table — radio/BSSID associations at a scope |
| `aos8_get_radio_summary` | Per-AP radio state: channel, power, utilization, noise floor |
| `aos8_get_version` | AOS8 software version on Conductor and MDs |
| `aos8_get_licenses` | Installed licenses and feature entitlements |

### Clients (4)

| Tool | Purpose |
|---|---|
| `aos8_get_clients` | List connected wireless clients at a config_path scope |
| `aos8_find_client` | Find client by MAC address, IP address, or username |
| `aos8_get_client_detail` | Full association/auth/connection info for a single client |
| `aos8_get_client_history` | Historical connection events for a client |

### Alerts & Audit (3)

| Tool | Purpose |
|---|---|
| `aos8_get_alarms` | Active alarms with severity, category, and timestamp |
| `aos8_get_audit_trail` | Configuration audit log (who changed what, when) |
| `aos8_get_events` | System event log filterable by type/severity/time |

### WLAN & Config (4)

| Tool | Purpose |
|---|---|
| `aos8_get_ssid_profiles` | List all SSID profiles with key settings |
| `aos8_get_virtual_aps` | Virtual AP profiles mapped to SSIDs and AP groups |
| `aos8_get_ap_groups` | AP group list with member APs and applied profiles |
| `aos8_get_user_roles` | Defined user roles and policy assignments |

### Troubleshooting (7)

| Tool | Purpose |
|---|---|
| `aos8_ping` | Ping from a controller to a target IP |
| `aos8_traceroute` | Traceroute from a controller to a target IP |
| `aos8_show_command` | Passthrough for any AOS8 CLI show command (`_meta` stripped) |
| `aos8_get_logs` | Recent system log entries filterable by severity |
| `aos8_get_controller_stats` | CPU, memory, uptime, session counts on a controller |
| `aos8_get_arm_history` | ARM channel-change and power-adjustment history |
| `aos8_get_rf_monitor` | RF monitor data: interference and rogue detections |

### Differentiators (9)

AOS8-unique read tools that go beyond Aruba Central parity — Conductor
hierarchy, effective configuration after inheritance, RF neighbors,
cluster state, IPsec tunnels, and a unified per-MD health roll-up.

| Tool | Purpose |
|---|---|
| `aos8_get_md_hierarchy` | Conductor → Managed Device tree with config_path for each node |
| `aos8_get_effective_config` | Resolved config a specific MD or AP group sees after inheritance |
| `aos8_get_pending_changes` | Staged Conductor changes not yet persisted via `aos8_write_memory` |
| `aos8_get_rf_neighbors` | ARM neighbor graph for an AP — co-channel and adjacent-channel |
| `aos8_get_cluster_state` | AP cluster membership, master/standby roles, failover state |
| `aos8_get_air_monitors` | APs in air-monitor mode with scan results |
| `aos8_get_ap_wired_ports` | Wired downlink port configuration and state for APs |
| `aos8_get_ipsec_tunnels` | Site-to-site IPsec and Remote AP tunnel state |
| `aos8_get_md_health_check` | Unified per-MD health: APs + clients + alarms + firmware in one call |

### Writes (12) — gated behind `ENABLE_AOS8_WRITE_TOOLS=true`

All write tools require an explicit `config_path` parameter (no default) and return a
`requires_write_memory_for` field listing the config_paths needing persistence via
`aos8_write_memory`.

| Tool | Tag | Purpose |
|---|---|---|
| `aos8_manage_ssid_profile` | `aos8_write` / `aos8_write_delete` | Create/update/delete SSID profile |
| `aos8_manage_virtual_ap` | `aos8_write` / `aos8_write_delete` | Create/update/delete virtual AP profile |
| `aos8_manage_ap_group` | `aos8_write` / `aos8_write_delete` | Create/update/delete AP group |
| `aos8_manage_user_role` | `aos8_write` / `aos8_write_delete` | Create/update/delete user role |
| `aos8_manage_vlan` | `aos8_write` / `aos8_write_delete` | Create/update/delete VLAN |
| `aos8_manage_aaa_server` | `aos8_write` / `aos8_write_delete` | Create/update/delete AAA server |
| `aos8_manage_aaa_server_group` | `aos8_write` / `aos8_write_delete` | Create/update/delete AAA server group |
| `aos8_manage_acl` | `aos8_write` / `aos8_write_delete` | Create/update/delete session ACL |
| `aos8_manage_netdestination` | `aos8_write` / `aos8_write_delete` | Create/update/delete network destination |
| `aos8_disconnect_client` | `aos8_write` | Force-disconnect a client by MAC |
| `aos8_reboot_ap` | `aos8_write` | Reboot a specific AP by name |
| `aos8_write_memory` | `aos8_write` | Persist staged config to startup config (explicit operator action only) |

### Guided Prompts (9)

| Prompt | Parameters | Workflow |
|---|---|---|
| `aos8_triage_client` | `mac_address: str` | Triage a client connectivity problem |
| `aos8_triage_ap` | `ap_name: str` | Deep-dive an AP's health |
| `aos8_health_check` | — | Network-wide health assessment |
| `aos8_audit_change` | — | Recent audit-trail review with risk flagging |
| `aos8_rf_analysis` | `config_path: str = "/md"` | RF environment report |
| `aos8_wlan_review` | — | SSID/VAP/AP-group/role consistency check |
| `aos8_client_flood` | `config_path: str = "/md"` | High client count / failed connection investigation |
| `aos8_compare_md_config` | `md_path_1: str`, `md_path_2: str` | Side-by-side effective-config diff |
| `aos8_pre_change_check` | `config_path: str` | Pre-maintenance checklist (ends with write_memory reminder) |

See [INSTRUCTIONS.md](../INSTRUCTIONS.md) for `config_path` semantics and the
`write_memory` contract.
