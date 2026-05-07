"""Migration mappings TO Central — data-driven translations from source platforms.

Each mapping under ``central_targets/`` describes how to construct a Central
configuration target (e.g. a named-VLAN with its alias chain) from one or more
source-platform objects (e.g. AOS 8 ``vlan_name`` + ``vlan_name_id``). The
mapping format is REST-keyed and source-pluggable: AOS 8 is the only source
platform v1 ships, but the format accommodates additional sources via the
``sources.<platform_id>`` block (see issue #279 for the architecture).

Three pieces:

* ``loader.py`` reads + pydantic-validates every JSON under ``central_targets/``
  at lifespan startup. Returns ``dict[str, Mapping]`` keyed by ``central_target_id``.
* ``engine.py`` consumes a Mapping + source data + Central scope_id, walks the
  ``central_emits`` array, applies transforms, expands iteration rules, and
  returns an ordered list of ``CentralCall`` descriptors ready for dispatch.
* ``transforms.py`` registers named transform functions (``split_csv_to_string_array``,
  ``direct_int``, ``flag_to_bool``, etc.) that mappings reference by name.

The runtime engine does NOT call Central. It emits call descriptors. The
aos-migration skill (Phase 3 / issue #240) is the dispatcher — it iterates
the descriptors and invokes ``central_*`` write tools with elicitation gating.
"""

from __future__ import annotations

from hpe_networking_mcp.migrations.engine import CentralCall, EngineError, emit_calls
from hpe_networking_mcp.migrations.loader import (
    LoaderError,
    Mapping,
    SourceBlock,
    load_mappings,
)

__all__ = [
    "CentralCall",
    "EngineError",
    "LoaderError",
    "Mapping",
    "SourceBlock",
    "emit_calls",
    "load_mappings",
]
