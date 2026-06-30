# Vendored HPE GreenLake OpenAPI specs

Public **northbound** OpenAPI specs for the HPE GreenLake platform services,
vendored from the developer portal (<https://developer.greenlake.hpe.com>) so
the server's GreenLake tooling can be built/regenerated from a pinned, reviewed
source rather than fetched at runtime.

## What's here

- `sources.json` — the manifest: one entry per spec with its `service`, `title`,
  path count, vendored `file`, and exact upstream `url`.
- `<service>.json` / `<service>__<spec>.json` — the canonicalized specs
  (`indent=2`, `sort_keys` for stable diffs). Services exposing several distinct
  northbound APIs get one file each (e.g. `service-catalog__*`).

Specs are © HPE and reproduced here under their developer terms for tooling
generation; they are not part of this project's MIT-licensed source.

## How it's refreshed

`.github/workflows/greenlake-specs-refresh.yml` runs weekly (and on demand):
it re-downloads every URL in `sources.json`, canonicalizes, and opens a PR if
anything changed. It also diffs the live `llms.txt` against `sources.json` and
warns about **newly-published services** to add.

## Why a curated manifest (not auto-derived URLs)

The portal is a Redocly SPA. The reliable spec index is **`/llms.txt`**, which
lists every API doc page. But the raw download lives under `/_bundle/...` and
**preserves source casing / odd segments** — `openApi.json`, `openapiBeta.json`,
`@v1` — while the `llms.txt` paths are lowercased. So the download URL **cannot
be derived from the doc path by string transform**; each must be the exact,
verified `_bundle/...json?download` URL. `sources.json` holds those verified URLs.

## Curation

Included: the public northbound spec(s) per service. Excluded: `*-internal`,
`*uiapi`/`*appapi`, events-only fragments, `changelog`, and pure duplicates
(e.g. `-latest` mirrors). `audit-logs` is collapsed to its primary API.
Changelog-only / "coming soon" services (no published spec yet) are absent and
will be flagged by the refresh workflow once they ship.
