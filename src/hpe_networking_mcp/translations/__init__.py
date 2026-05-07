"""Cross-platform configuration translations.

Each translation under ``targets/<platform>/`` describes how to construct a
target-platform configuration object (e.g. a Central named-VLAN with its
alias chain) from one or more source-platform objects (e.g. AOS 8
``vlan_name`` + ``vlan_name_id``). The format is REST-keyed and source-
pluggable; the ``target_platform`` field plus the ``sources.<platform_id>``
block let any source-target combination ship under the same engine. v1 ships
AOS 8 → Central only (see issue #279 for the architecture).

Three pieces:

* ``loader.py`` reads + pydantic-validates every JSON under
  ``targets/<platform>/`` at lifespan startup. Returns ``dict[str, Translation]``
  keyed by ``"<target_platform>:<target_id>"``.
* ``engine.py`` consumes a Translation + source data + ``runtime_values``
  (target-platform-specific runtime context such as Central's
  ``central_scope_id`` and ``device_functions``), walks ``target_emits``,
  applies transforms, expands iteration rules, and returns an ordered list
  of ``TargetCall`` descriptors ready for dispatch.
* ``transforms.py`` registers named transform functions
  (``split_csv_to_string_array``, ``direct_int``, ``flag_to_bool``, etc.)
  that translations reference by name.

The runtime engine does NOT call any target platform. It emits call
descriptors. Consumer skills (aos-migration Phase 3 / issue #240, future
WLAN-sync skill, etc.) iterate the descriptors and invoke the appropriate
platform's write tools with elicitation gating.

Why "translations" and not "migrations": migration is one-time and end-state-
oriented; this primitive also covers ongoing operational sync (Mist ↔ Central
WLAN reconciliation) where the same engine fires repeatedly. The engine
doesn't care which mode the consumer is in.
"""

from __future__ import annotations

from hpe_networking_mcp.translations.engine import (
    EngineError,
    TargetCall,
    emit_calls,
)
from hpe_networking_mcp.translations.loader import (
    LoaderError,
    SourceBlock,
    Translation,
    load_translations,
)

__all__ = [
    "EngineError",
    "LoaderError",
    "SourceBlock",
    "TargetCall",
    "Translation",
    "emit_calls",
    "load_translations",
]
