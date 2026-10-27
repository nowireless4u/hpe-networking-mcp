# Aruba New Central — vendored OpenAPI definitions

Auto-synced by [`.github/workflows/sync-new-central-oas.yml`](../../.github/workflows/sync-new-central-oas.yml)
via [`.github/scripts/fetch_aruba_oas.py`](../../.github/scripts/fetch_aruba_oas.py).
**Do not hand-edit** — changes are overwritten on the next sync.

## Source

`developer.arubanetworks.com` is a [ReadMe](https://readme.com)-hosted developer
hub. Each project's API reference is split across **multiple** uploaded OpenAPI
definitions.

Each project's `/reference` page server-renders its props into a
`<script id="ssr-props">` JSON block. The fetcher reads the active branch's
definitions (`apiDefinitions`), resolves each filename to its per-file `uuid` in
the registry list, and fetches the compiled definition as raw JSON from:

```
https://dash.readme.com/api/v1/api-registry/<uuid>
```

Some current definitions have **no** registry entry. Those are located through
the reference page that renders them and rebuilt from the per-operation
documents each page's Markdown view embeds (indexed by the project's
`llms.txt`), rather than skipped. Every definition must parse as OpenAPI 3.x
with at least one path, and is written as one `<title-slug>.json` with keys
sorted for stable diffs.

The run refuses to update a project, failing loudly, when the definition count
drops or a definition loses more than half its paths versus the committed
`_manifest.json`: a partial fetch must never auto-merge as an upstream removal.

> History: the original `/<project>/openapi/<apiSetting-id>` endpoint was
> retired when the hub moved to ReadMe's SuperHub (2026-07-02), and the registry
> list moved within ssr-props around 2026-09-29.

## Layout

| Path | Project | Contents |
|------|---------|----------|
| `vendor/central/mrt/`    | `new-central`        | Monitoring / Reporting / Troubleshooting / Notifications / Services / MSP / Authorization |
| `vendor/central/config/` | `new-central-config` | Configuration model (Scope, Security, System, Interfaces, NAC, Routing, …) |

Each directory's `_manifest.json` records the definition inventory (slug, title,
version, path count, branch definition count) for regression detection. Where
each definition came from (upstream filename, registry uuid or reference page)
is printed in the workflow log rather than stored, so a provenance-only change
never opens a sync PR.

## Regeneration

This workflow vendors the specs only — it does **not** regenerate tools. The
maintainer re-runs the Central importer against this snapshot at release time so
tool-surface changes are reviewed before tagging.
