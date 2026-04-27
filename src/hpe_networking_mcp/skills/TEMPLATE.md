---
name: my-skill-name
title: One-line human-readable title
description: |
  A 1-3 sentence summary describing when this skill is the right tool —
  it's what shows up in `skills_list` so make it specific. Mention the
  signal that should make the AI pick this skill over another.
platforms: [mist, central, clearpass, apstra, greenlake, axis]
tags: [tag1, tag2, tag3]
tools: [health, mist_invoke_tool, central_invoke_tool]
---

# Title (matches frontmatter title)

## Objective

What this skill accomplishes. One paragraph.

## Prerequisites

What must be true before running this skill — credentials configured,
specific platform reachable, the user has provided a site / org / device
identifier, etc. Use a bulleted list.

- All targeted platforms reachable (run `health(platform=...)` first)
- User has supplied a specific site_name or device identifier
- (etc.)

## Procedure

### Step 1 — Short label

**Tool:** `tool_name(param=value, ...)`
**Why:** One line on what this step proves or fetches.
**Expected result:** What success looks like.
**If anomaly:** What to do if the step doesn't return what's expected (skip,
fall back to a different tool, escalate to the user, etc.).

### Step 2 — Short label

**Tool:** `another_tool(...)`
**Why:** ...
**Expected result:** ...
**If anomaly:** ...

### Step 3 — ...

## Decision matrix

If the procedure has branches (e.g. "if site is wired-only, skip RF steps"),
spell them out as a small table:

| Condition | Action |
|---|---|
| Site has only `aos-s` / `cx` switches | Skip steps 4-6 (Wi-Fi RF) |
| ClearPass platform is `unavailable` | Skip step 7 (NAC session lookup) |

## Output formatting

How to present the result back to the user — a concise bullet list, a
markdown table, a structured JSON, an executive summary, etc. Be specific
so different skill runs produce comparable output.

## Example

A 1-2 line example query that should trigger this skill, e.g.:

> "give me the daily infra health snapshot"
> "is everything healthy at site HOME?"
