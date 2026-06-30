---
name: greenlake-device-onboarding
title: GreenLake device onboarding — add + subscribe + assign service
description: |
  PRIMARY TRIGGER — invoke this skill whenever the operator wants to add,
  onboard, register, or import devices into HPE GreenLake. Do NOT call
  `greenlake_bulk_add_devices` bare: onboarding is a lifecycle (add →
  subscribe → assign to a service), and this runbook also carries the
  choose-your-source step and the mandatory paste-visibility warning that a
  bare tool call skips.

  Trigger phrases include but are not limited to: "add devices to GreenLake",
  "onboard devices", "register devices in GreenLake", "import my devices",
  "add APs / switches / gateways to GreenLake", "bulk add devices",
  "add devices and assign subscriptions", "subscribe my new devices",
  "get these devices into Central via GreenLake".

  Covers: gathering the device list (server-side upload OR paste, with the
  paste warning), choosing a subscription, assigning a service/application,
  optional location + tags, running the bulk add, and verifying the result.
  Write-gated (ENABLE_GREENLAKE_WRITE_TOOLS) + confirmation-gated.
platforms: [greenlake]
tags: [greenlake, onboarding, devices, subscription, service, write]
tools: [health, greenlake_get_workspace, greenlake_get_subscriptions, greenlake_get_subscription_details, greenlake_get_devices, greenlake_bulk_add_devices, file_manager, list_files]
---

# GreenLake device onboarding

## Objective

Take one or more devices from "I have serials + MACs" to "added to the
workspace, subscribed, and assigned to a service" — in a single guided flow.
Onboarding is a lifecycle, not a single write: operators almost never add
devices and walk away; they expect to subscribe and assign them too. This
runbook drives the whole thing and never lets device data leak into the model
context unnecessarily.

Prerequisite: `ENABLE_GREENLAKE_WRITE_TOOLS=true` (the add tool is hidden
otherwise). The universal confirmation gate fires before the write — surface
the device count and the chosen subscription/service when you confirm.

## Stage 0 — Confirm scope

Tell the operator what onboarding will do and confirm: **add the devices →
subscribe them → assign them to a service** (location + tags optional). If
they only want to add (no subscribe/assign), that's fine — skip Stages 2–4.

## Stage 1 — Get the device list (choose the source; WARN on paste)

Ask the operator how they want to provide the list, and present BOTH options
with the trade-off stated plainly. **You MUST include the paste warning** —
do not offer paste silently:

- **Upload (recommended for anything beyond a handful):** call `file_manager`
  to render the upload widget. The file is read **server-side** — its contents
  (serials, MACs) **never enter this conversation**. After they upload, call
  `list_files` to get the file's name (metadata only — you will NOT see its
  contents), and use that name as `csv_filename` in Stage 5.
- **Paste (small lists only):** the operator pastes the rows into chat. ⚠️
  **State this verbatim before they paste:** *"Anything you paste here is
  visible to me (the AI) and may be retained in this conversation's context.
  For sensitive or large lists, use the upload option instead — it's read
  server-side and never enters the chat."* Only use paste for a few devices.

There is intentionally **no tool that returns an uploaded file's contents** to
you — do not try to read the file. Mandatory columns: `serialNumber` and
`macAddress` (aliases: serial/sn, mac). For paste, build the CSV yourself from
what they gave you.

## Stage 2 — Choose a subscription

Call `greenlake_get_subscriptions` and show the operator the available
subscriptions (key, tier/product, available seats, expiry). Let them pick the
one to apply. Use `greenlake_get_subscription_details` if they want specifics.
Capture the chosen **subscription key** for Stage 5 (`subscription_key`).

If they don't want to subscribe now, note that the devices will be added
unsubscribed and can be subscribed later, and skip to Stage 5.

## Stage 3 — Assign a service

Determine which service/application the devices should be assigned to (e.g. an
Aruba Central instance). Confirm the **service ID** with the operator and
capture it for Stage 5 (`service_id`). If unsure, ask — don't guess a service.

## Stage 4 — Location + tags (optional)

Ask whether they want a location and/or tags applied to the batch. Capture
`location` and `tags` for Stage 5 if provided.

## Stage 5 — Run the bulk add

Call `greenlake_bulk_add_devices` ONCE with the source from Stage 1 plus the
batch-uniform assignments from Stages 2–4:

- Upload path: `csv_filename="<name from list_files>"`
- Paste path: `csv_text="<the CSV you built>"`
- Plus, as applicable: `subscription_key=...`, `service_id=...`,
  `location=...`, `tags=...` — these apply to every device that doesn't carry
  that column in the CSV, so an uploaded serial/MAC list gets subscribed +
  assigned without you ever editing (or seeing) the file.

The confirmation gate fires here — present the device count + chosen
subscription/service before confirming.

## Stage 6 — Verify + report

The tool returns counts (`succeeded` / `failed` / `skipped`) plus per-phase
results (subscription / service / location / tags) and a capped `failures`
list. Report these to the operator.

Note on identifiers: failed-row **serials are tokenized** (`[[SERIAL:uuid]]`
when PII tokenization is enabled, else `[serial]`) — this is intentional
redaction, NOT a sign the CSV had placeholder data. If a device already exists
in the workspace it surfaces as a per-row failure ("device already exists") —
that is expected, not an error in the input.

If devices failed for transient reasons, re-running with the same source
resumes from the `.cache.json` checkpoint (already-succeeded rows are skipped).
