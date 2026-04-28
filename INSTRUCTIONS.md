# AOS8 / Mobility Conductor — Operator Instructions

> Operator-facing reference for the Aruba OS 8 / Mobility Conductor platform module.
> For the AI-facing system prompt that ships inside the container, see
> [src/hpe_networking_mcp/INSTRUCTIONS.md](src/hpe_networking_mcp/INSTRUCTIONS.md).

## Overview

The AOS8 module is the seventh platform exposed by `hpe-networking-mcp`. It surfaces 38
tools (8 health, 4 client, 3 alert, 4 WLAN, 7 troubleshooting, 12 write) plus 9 guided
prompts that drive an AI assistant through recognizable AOS8 operator workflows. See
[README.md](README.md) for setup, secrets, and platform enablement; this document
covers the AOS8-specific concepts an operator must understand to use the tools
correctly.

## Connecting to a Conductor vs. a Standalone Controller

The AOS8 module connects to a single AOS8 endpoint via HTTPS on the configured `aos8_port`
(default 4343). The endpoint can be either a **Mobility Conductor** (managing one or more
Managed Devices) or a **standalone controller** (no Conductor; manages its own APs).

| Topology | What `aos8_host` points at | What `config_path` looks like |
|---|---|---|
| Mobility Conductor + MDs | Conductor IP/hostname | `/md`, `/md/<MD-name>`, `/md/<AP-group>` |
| Standalone controller | Controller IP/hostname | `/mm/mynode` (the node's own scope) |

The AI uses the same tool surface for both topologies; only the `config_path` value
differs. Tools that require a `config_path` parameter accept either form.

## `config_path` Semantics

`config_path` is the AOS8 hierarchical scope identifier. It tells the Conductor *where*
a configuration object lives in the inheritance tree.

| Path | Meaning |
|---|---|
| `/md` | All Managed Devices under the Conductor |
| `/md/<MD-name>` | A specific Managed Device |
| `/md/<AP-group-name>` | A specific AP group beneath /md |
| `/mm/mynode` | The local node (used on standalone controllers) |

Inheritance flows top-down: an SSID profile defined at `/md` is visible to every MD;
the same name defined at `/md/<MD-name>` overrides it for that MD. Always pass the
**most specific** scope at which you want the change to take effect — never assume the
default.

Every write tool (WRITE-01..09) requires an explicit `config_path` parameter. There is
no default. This is intentional — operating against the wrong scope is the most common
self-inflicted AOS8 outage.

## The `aos8_write_memory` Contract

AOS8 distinguishes **running config** from **startup config**. Every write tool
(`aos8_manage_*`) modifies the running config and returns a response containing a
`requires_write_memory_for` field listing the `config_path` values whose changes need to
be persisted to startup config.

**`aos8_write_memory` is never called automatically.** It is always an explicit operator
action. The flow is:

1. Operator calls a write tool (e.g., `aos8_manage_ssid_profile`) with explicit `config_path`.
2. Response includes `requires_write_memory_for: ["/md/site-a"]` (for example).
3. Operator reviews the change and confirms the intent.
4. Operator explicitly calls `aos8_write_memory` with `config_path="/md/site-a"`.

This two-step contract exists to make staged-change rollback trivial (a controller
reboot reverts unsaved changes) and to prevent the AI from silently persisting changes
the operator has not approved. The `aos8_pre_change_check` guided prompt ends with a
reminder of this contract.

## Using `aos8_show_command`

`aos8_show_command` is a passthrough for any AOS8 CLI `show` command. The response is
structured JSON wherever the AOS8 API returns table-formatted data; the `_meta` field
(column-schema metadata) is stripped before the JSON is returned to the AI to keep the
payload focused.

Useful invocations:

| Command | Purpose |
|---|---|
| `show version` | Conductor + MD firmware versions |
| `show ap database` | Full AP inventory |
| `show user-table` | Active client list |
| `show configuration committed` | Current saved-to-startup config baseline |
| `show configuration pending` | Staged changes not yet persisted via write_memory |
| `show ap radio-summary` | Per-radio channel/power/utilization |

The command string is preserved as-typed (case-sensitive) — only the `show` prefix is
case-insensitive. Always include the `config_path` for commands that produce
scope-specific output.

## Guided Prompt Index

The AOS8 module ships with 9 guided prompts. Each is a multi-step workflow the AI will
follow when invoked, capturing tool outputs and producing a summary with recommended
next actions. MCP clients (e.g., Claude Desktop) surface these in the slash-command
menu.

| Prompt | Parameters | Workflow |
|---|---|---|
| `aos8_triage_client` | `mac_address: str` | Find a client, check AP health, review auth/association events, identify likely root cause |
| `aos8_triage_ap` | `ap_name: str` | Deep-dive an AP: radio state, clients, alarms, ARM history, event timeline |
| `aos8_health_check` | (none) | Network-wide health: controllers, AP counts, clients, alarms, firmware drift |
| `aos8_audit_change` | (none) | Recent audit-trail review with high-risk-change flagging |
| `aos8_rf_analysis` | `config_path: str = "/md"` | Channel distribution, co-channel clusters, ARM oscillation, interferers/rogues |
| `aos8_wlan_review` | (none) | SSID/VAP/AP-group/role inventory and consistency check |
| `aos8_client_flood` | `config_path: str = "/md"` | High-client-count / failed-connection investigation at a scope |
| `aos8_compare_md_config` | `md_path_1: str`, `md_path_2: str` | Side-by-side effective-config diff between two MDs or AP groups |
| `aos8_pre_change_check` | `config_path: str` | Pre-maintenance checklist: alarms, controller stats, audit trail, pending changes, write_memory reminder |

For SSID/VAP/AP-group/role/VLAN/AAA/ACL/netdestination changes — and especially before
any maintenance window — invoke `aos8_pre_change_check` first to capture the
GO/NO-GO baseline.
