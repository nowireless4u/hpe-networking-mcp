"""Preprocessing modules for translations whose source shape doesn't fit
the standard per-field key_mapping template.

Each translation that needs preprocessing declares it via ``preprocessing``
in its JSON (dotted import path to the function). The engine invokes the
function before key_mappings, with signature
``(source_data: dict, runtime_values: dict) -> dict``. The function returns
an augmented source_data dict; key_mappings then operate on the augmented
shape.

Use cases for preprocessing:

* **Composite source merges** — translation has multiple source objects
  that need to be joined / cross-referenced before key_mappings can run
  (e.g. ``aos8_policy.preprocess_acl_for_policy`` looks up role records
  to compute ``role_attribution`` per ACL).
* **Parallel source arrays** — source has multiple parallel arrays that
  need to be merged into one tagged array before iteration (e.g. AOS 8's
  ``acl_sess__v4policy`` + ``acl_sess__v6policy`` collapse into a single
  ``_central_rules`` list).
* **Fan-out expansion** — one source rule produces multiple target rules
  (e.g. AOS 8 "any any" expanding to two Central rules).

When NOT to use preprocessing:

* **Per-field transformations** — use a regular ``key_mapping`` with a
  small transform instead. Preprocessing is for cases where the source
  shape itself needs restructuring before any per-field work.
* **Translations with simple 1:1 source shape** — most translations
  (vlan_id, role) don't need preprocessing at all. Don't add it
  speculatively.

See ``translations/AUTHORING.md`` for guidance on when preprocessing is
the right tool.
"""

from __future__ import annotations
