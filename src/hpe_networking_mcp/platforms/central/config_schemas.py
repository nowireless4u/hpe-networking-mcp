"""Runtime access to distilled Central config-model payload schemas.

The ``central_manage_*`` / ``central_get_*`` config-model tools expose an
opaque ``payload: dict``. The OpenAPI specs that describe each payload's field
set are gitignored and never shipped in the runtime image, so an AI client
driving these tools has no schema to author against and resorts to guessing
field names and enum values against the live tenant (issue #384).

``scripts/distill_central_config_schemas.py`` distills those specs into a
committed artifact (``_config_payload_schemas.json``) shipped alongside this
module. ``central_get_tool_schema`` calls :func:`lookup_payload_schema` to
attach the resolved field set (names, types, enums, ``x-supportedDeviceType``
tags) to its response for config-model tools.

The artifact is loaded once and cached. A missing or malformed artifact
degrades gracefully to "no payload schema" rather than raising.
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

from loguru import logger

_ARTIFACT_PATH = Path(__file__).with_name("_config_payload_schemas.json")


@lru_cache(maxsize=1)
def _load() -> dict[str, Any]:
    """Load and cache the distilled schema artifact.

    Returns an empty (but well-formed) structure if the artifact is missing or
    unreadable so callers never have to guard against ``None``.
    """
    try:
        data = json.loads(_ARTIFACT_PATH.read_text(encoding="utf-8"))
    except FileNotFoundError:
        logger.warning(
            "Central config payload schemas artifact not found at {} — "
            "payload schemas will not be surfaced. Run "
            "scripts/distill_central_config_schemas.py to regenerate.",
            _ARTIFACT_PATH.name,
        )
        return {"schemas": {}, "tool_index": {}}
    except (json.JSONDecodeError, OSError) as exc:
        logger.warning("Failed to load Central config payload schemas ({}): {}", _ARTIFACT_PATH.name, exc)
        return {"schemas": {}, "tool_index": {}}

    if not isinstance(data, dict):
        return {"schemas": {}, "tool_index": {}}
    data.setdefault("schemas", {})
    data.setdefault("tool_index", {})
    return data


def lookup_payload_schema(tool_name: str) -> dict[str, Any] | None:
    """Return the distilled payload schema for a config-model tool, or ``None``.

    Both the ``central_get_<obj>`` and ``central_manage_<obj>`` tools for a
    given config object resolve to the same schema (they share the object body).

    Args:
        tool_name: Fully-qualified tool name, e.g. ``"central_manage_named_condition"``.

    Returns:
        A dict ``{"object": <stem>, "fields": {...}}`` describing the payload
        field set, or ``None`` if the tool is not a config-model tool.
    """
    data = _load()
    stem = data["tool_index"].get(tool_name)
    if stem is None:
        return None
    entry = data["schemas"].get(stem)
    if not entry:
        return None
    return {"object": stem, **entry}
