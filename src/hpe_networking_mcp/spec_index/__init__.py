"""Read-only spec-lookup index (deterministic OpenAPI field/enum/endpoint lookup).

Backed by the SQLite/FTS5 index built by ``scripts/build_spec_index.py`` from the
vendored OpenAPI corpus. Powers exact "which endpoint / field / enum / parameter"
answers for ``get_schema`` enrichment and validation-error enrichment — no model,
no embeddings, no hallucination. Degrades to empty results when the index file is
absent (e.g. a dev checkout where it was not baked), so callers never crash.
"""

from __future__ import annotations

from hpe_networking_mcp.spec_index.query import SpecIndex, get_spec_index

__all__ = ["SpecIndex", "get_spec_index"]
