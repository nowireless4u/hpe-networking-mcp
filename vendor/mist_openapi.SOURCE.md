# Vendored: Mist OpenAPI Specification

## Source

- **Upstream repository**: https://github.com/mistsys/mist_openapi
- **File**: `mist.openapi.json` (root of the upstream repo, `master` branch)
- **Raw URL**: https://raw.githubusercontent.com/mistsys/mist_openapi/master/mist.openapi.json

## Current sync

- **Spec API version**: `2604.1.0` (per the spec's `info.version` field)
- **Upstream blob SHA**: `1a2731850b6074a590da7c66cb69121801e09d96`
- **Vendored at**: 2026-05-12

## License

Upstream `LICENSE`: **MIT License**, Copyright (c) 2020 Thomas Munzer.

The MIT license grants full rights to use, copy, modify, merge, publish, distribute, and sublicense. The upstream `LICENSE` file is reproduced where relevant in our `LICENSE` notice text.

## Intended use — caveat

The upstream `README.md` notes:

> *"This specification is intended for documentation only, and NOT for code generation, testing tools, or other use cases."*

This is a disclaimer about *intent*, not a license restriction. We use the spec to generate Mist tool wrappers as one source of truth. The MIT license grants the right; the upstream disclaims warranties about generator suitability. Bugs in generated tools may not be tracked by upstream as bugs in the spec.

**Risk mitigation**:
- Mist's own UI is driven by the spec; catastrophic spec breakage would also break the Mist UI. The upstream's CI/CD validates the spec before merges.
- We control the generator and can patch around spec quirks on our side without an upstream fix.
- The spec auto-sync workflow (see `.github/workflows/sync-mist-openapi.yml`) only updates the vendored file; tool regeneration happens at release time under maintainer review.

## Automated sync workflow

The GitHub Actions workflow at `.github/workflows/sync-mist-openapi.yml` runs daily:

1. Fetches the upstream `mist.openapi.json` from `mistsys/mist_openapi:master`.
2. Validates the spec parses cleanly as OpenAPI 3.x.
3. If changed AND parses: auto-commits the new spec to `main` and updates this file's `Current sync` section.
4. If parse fails: opens a GitHub issue flagging the regression.

**Tool regeneration does NOT happen on auto-sync.** Regeneration runs at release time, manually by the maintainer:

```bash
uv run python -m hpe_networking_mcp.platforms.mist.regenerate
```

This decouples spec freshness from release cadence — the vendored spec is always current, but the live Mist tool surface only changes when the maintainer deliberately ships.

## Stats (at current sync)

- **OpenAPI version**: 3.1.0
- **Paths**: 736
- **Operations**: 1,037 (516 GET, 296 POST, 109 PUT, 116 DELETE)
- **Tags / domains**: ~100 functional areas (Orgs Sites, Orgs WLANs, Sites Devices, etc.)

## Tool naming convention

Tools are generated as `mist_<snake_case_operationId>`:

- `listOrgSites` → `mist_list_org_sites`
- `getOrgSite` → `mist_get_org_site`
- `createOrgSite` → `mist_create_org_site`
- `updateOrgSite` → `mist_update_org_site`
- `deleteOrgSite` → `mist_delete_org_site`
- `searchOrgClients` → `mist_search_org_clients`

OperationIds are unique across the spec, so tool names are guaranteed unique. PascalCase exceptions (e.g. `GetOrgLicenseAsyncClaimStatus`) are handled by case-insensitive snake_case conversion.
