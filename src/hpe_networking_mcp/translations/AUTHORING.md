# Translation Authoring Guide

This document is the canonical reference for authoring new translation JSON
files under `src/hpe_networking_mcp/translations/targets/<platform>/`. The
goals are:

1. **Repeatability** — every translation follows the same template so the
   engine code path is uniform and reviewers know what to expect.
2. **Engine simplicity** — the engine has a small, fixed surface area;
   per-translation complexity lives in the JSON or in a declared
   preprocessing function, never in special-case engine branches.
3. **Reviewability** — translation behavior is readable by walking the JSON
   plus (optionally) one preprocessing module, without having to trace
   transforms across files.

`tests/unit/test_translations_lint.py` enforces the rules below; CI fails
on drift. Run `python -m hpe_networking_mcp.translations.lint` locally to
check before opening a PR.

## The standard template (Paradigm B)

Every translation MUST use this shape unless an explicit exemption is
documented in `draft_notes` and reviewed:

1. **Per-field `key_mappings`** — one entry per source field, each with a
   small named transform (the simple `direct_str` / `direct_int` /
   `flag_to_bool` family, or a translation-specific transform <50 lines).
2. **Structurally complete `body`** in each emit — the body shape is
   readable as JSON; placeholders `{name}` substitute leaf values, not
   whole sub-trees of computed structure. (`{policy_rules}` substituting
   an array is OK when the array was pre-computed by preprocessing — see
   the escape hatch below.)
3. **Step 2 (when scope binding applies) is `config-assignments`** —
   Central-targeted translations use the `body_template` config-assignment
   pattern for scope binding so the engine renders multi-device-function
   arrays uniformly.
4. **`required_runtime_values`** declares every key the consumer must
   supply (e.g. `central_scope_id`, `role_records`). The engine validates
   their presence before emitting; missing values fail loud.
5. **No fat transforms** — individual transforms must be focused (≤ ~50
   lines). When a transform would need source-wide access (multiple
   fields, cross-record lookups, fan-out), use the **preprocessing**
   escape hatch below — don't push complexity into a 2-arg transform.
6. **`draft_notes`** documents idempotency, inversions, live-verified
   shapes, and any caveats. Authors write these as they go; they're
   first-class API for the consumer skill.

## The preprocessing escape hatch

Some source shapes don't fit per-field `key_mapping`:

* Two parallel source arrays that need to merge into a single tagged
  target array (AOS 8 `acl_sess__v4policy` + `acl_sess__v6policy`).
* Cross-record lookups (compute `role_attribution` by reverse-indexing
  all role records to find which ones reference a given ACL).
* Fan-out (one source rule produces multiple target rules — AOS 8
  bidirectional `any any` → two Central rules).

For these, declare a **preprocessing function** at the top of the JSON:

```json
{
  "version": 1,
  "target_platform": "central",
  "target_id": "policy",
  "preprocessing": "hpe_networking_mcp.translations.preprocessing.aos8_policy.preprocess_acl_for_policy",
  ...
}
```

The function signature is:

```python
def preprocess_<name>(source_data: dict, runtime_values: dict) -> dict:
    """Return an augmented source_data dict — don't mutate the input."""
```

The engine invokes the function **before** `key_mappings`, after the
source-platform check + `required_runtime_values` validation. The
function returns a new dict (typically `{**source_data, "_<augment>":
...}`) and `key_mappings` then operate on the augmented shape.

Modules live under
`src/hpe_networking_mcp/translations/preprocessing/<name>.py`. Each module
is a single-purpose helper; transforms it uses internally are private
(`_build_address`, `_compute_role_attribution`, …). The module is unit-
tested directly; the translation's engine tests just verify the
augmented `source_data` flows through key_mappings correctly.

### When NOT to use preprocessing

* **Per-field transformations** that fit a 1-arg transform — use a
  regular `key_mapping` entry. Don't create a preprocessing module just
  to wrap one transform.
* **Translations with a simple 1:1 source shape** — most translations
  (`vlan_id`, `role`) don't need preprocessing at all. Don't add it
  speculatively.

## Decision tree: when authoring a new translation

```
Does the source have a 1:1 shape with the target?
├── Yes → Per-field key_mappings + structurally complete body. Done.
│         (Examples: central:vlan_id, central:role)
│
└── No, source needs restructuring
    │
    ├── Does iteration need to fan out one source object across
    │   multiple emits (e.g. one binding → 6 Central API calls)?
    │   ├── Yes → Use the engine's iteration rules (`once`,
    │   │         `per_vlan_id_in_binding`, `per_device_function`,
    │   │         `per_vlan_id_per_device_function`). Per-field
    │   │         key_mappings still apply per emit. (Example:
    │   │         central:named_vlan with 6 emits driven by
    │   │         iteration rules.)
    │   └── No → Continue.
    │
    └── Does the source have parallel arrays / cross-record lookups /
        per-rule fan-out?
        ├── Yes → Author a preprocessing module. The JSON stays thin
        │         (per-field key_mappings), the preprocessing fn
        │         augments source_data with the precomputed structure,
        │         and the body substitutes the precomputed value via a
        │         whole-string placeholder. (Example: central:policy.)
        └── No → Reconsider whether you actually need preprocessing,
                 or whether a small per-field transform suffices.
```

## Lint rules (enforced by CI)

`tests/unit/test_translations_lint.py` runs every shipped translation
through these checks:

| Rule | What it enforces |
|------|------------------|
| `check_no_fat_transforms` | Each registered transform is < 50 lines. Composite logic must live in `preprocessing/` instead. |
| `check_body_or_body_template` | Each emit declares exactly one of `body` or `body_template`, never both — and POST/PUT/PATCH emits must declare one. |
| `check_required_runtime_values_referenced` | Every key in `required_runtime_values` is referenced somewhere in the JSON (body / body_template / query_params / merge_rule / preprocessing-aware code path) so it can't drift to documentation-only. |
| `check_preprocessing_path_resolves` | When `preprocessing` is set, the dotted import path resolves to a callable with the right signature `(source_data, runtime_values)`. |

## Examples by translation

* **central:named_vlan** — Composite source (`vlan_name` + `vlan_name_id`
  joined by `name`). Uses iteration rules to fan out to 6 emits. Per-
  field `key_mappings` still apply. No preprocessing needed because the
  composite merge is described declaratively via `merge_rule` and the
  consumer skill performs the join before calling `emit_calls`.
* **central:vlan_id** — Simple 1:1 source. Per-field `key_mappings` with
  `optional: true` for sub-properties. No preprocessing. Body is
  structurally complete with optional fields auto-dropped by
  `_drop_none_keys`.
* **central:role** — Simple source, many fields. Per-field
  `key_mappings` (~25 entries). Several disambiguating transforms
  (`vlanstr_to_id_if_numeric` / `_name_if_nonnumeric` / `_to_vlan_type`)
  that share a source path but produce different target keys. No
  preprocessing.
* **central:policy** — Source has parallel arrays + cross-record lookups
  + fan-out. Uses the **preprocessing escape hatch**. JSON has only two
  thin `key_mappings` (`name` + `policy_rules`); all complex logic
  lives in `preprocessing/aos8_policy.py`. Body is structurally
  complete with `"policy-rule": "{policy_rules}"` as the only computed
  substitution.

## Adding a new translation: checklist

- [ ] JSON file at `targets/<platform>/<id>_v1.json`.
- [ ] Per-field `key_mappings`. Need preprocessing? Add a module under
      `preprocessing/`, declare its dotted path in JSON.
- [ ] `required_runtime_values` lists every consumer-supplied key.
- [ ] `draft_notes` covers idempotency + any inversions / caveats.
- [ ] Engine tests under `tests/unit/test_translations_engine.py`
      exercise all paths.
- [ ] If preprocessing was added, unit-test the module directly under
      `tests/unit/test_translations_preprocessing_<name>.py`.
- [ ] Lint passes: `python -m hpe_networking_mcp.translations.lint`.
- [ ] Update README + CHANGELOG + INSTRUCTIONS.md per the
      Documentation Checklist in `CLAUDE.md`.
