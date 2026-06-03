# Aruba New Central — vendored OpenAPI definitions

Auto-synced by [`.github/workflows/sync-new-central-oas.yml`](../../.github/workflows/sync-new-central-oas.yml)
via [`.github/scripts/fetch_aruba_oas.py`](../../.github/scripts/fetch_aruba_oas.py).
**Do not hand-edit** — changes are overwritten on the next sync.

## Source

`developer.arubanetworks.com` is a [ReadMe](https://readme.com)-hosted developer
hub. Each project's API reference is split across **multiple** uploaded OpenAPI
definitions, and ReadMe serves each compiled definition as raw JSON at:

```
https://developer.arubanetworks.com/<project>/openapi/<apiSetting-id>
```

The `<apiSetting-id>` values are 24-char hex ids embedded in every reference
page's HTML. The fetcher scrapes the project's `/reference` page for them,
fetches each definition, validates it parses as OpenAPI 3.x with at least one
path (stale/retired ids return a tiny error body and are skipped), and writes
one `<title-slug>.json` per definition with keys sorted for stable diffs.

> Note: the portal embeds specs in server-rendered HTML and does **not** fetch
> them as a standalone JSON response at runtime, so browser/network-interception
> approaches do not work — the `/openapi/<id>` endpoint is the real source.

## Layout

| Path | Project | Contents |
|------|---------|----------|
| `vendor/central/mrt/`    | `new-central`        | Monitoring / Reporting / Troubleshooting / Notifications / Services / MSP / Authorization |
| `vendor/central/config/` | `new-central-config` | Configuration model (Scope, Security, System, Interfaces, NAC, Routing, …) |

Each directory's `_manifest.json` records the definition inventory (slug, id,
title, version, path count) for provenance and regression detection.

## Regeneration

This workflow vendors the specs only — it does **not** regenerate tools. The
maintainer re-runs the Central importer against this snapshot at release time so
tool-surface changes are reviewed before tagging.
