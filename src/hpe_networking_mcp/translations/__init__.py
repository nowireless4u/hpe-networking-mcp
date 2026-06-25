"""Cross-platform configuration translations (canonical reader/writer engine).

Each translation goes ``source object → CanonicalX → ordered target calls``:

* ``canonical/`` — platform-neutral models (the pivot every reader/writer shares).
* ``readers/<platform>/`` — build a canonical model from a source-platform record.
* ``writers/<platform>*`` — emit ordered target API call descriptors from a canonical.
* ``orchestrator.py`` — ties readers + writers together (``plan`` is pure, no I/O;
  ``execute`` runs a plan against a live client with ensure-or-create semantics) and
  holds the ``(platform, kind)`` reader/writer registry.

v1 ships AOS 8 → Central (vlan / role / policy / net_group / the AAA chain /
gateway_cluster) plus bidirectional WLAN (Mist ↔ Central, AOS 8 → both). The
engine does NOT call any target platform — it emits call descriptors; the bridge
tools (``platforms/translate_config.py``, ``platforms/translate_wlan.py``) and the
aos-migration skill dispatch them with elicitation gating.

The legacy JSON ``emit_calls`` engine (``engine.py`` / ``loader.py`` / per-kind
``targets`` + ``preprocessing``) was retired once every kind moved to this engine.
"""

from __future__ import annotations

from hpe_networking_mcp.translations import orchestrator
from hpe_networking_mcp.translations.orchestrator import TranslationPlan, plan, supported

__all__ = [
    "TranslationPlan",
    "orchestrator",
    "plan",
    "supported",
]
