"""Runtime access to distilled Mist request-body schemas.

Mist write/config tools (`mist_create_*`, `mist_update_*`, …) take an opaque
`body: dict[str, Any]` described only as "Request Body". The field set lives in
the vendored OpenAPI spec, which is not shipped in the runtime image, so an AI
client has no schema to author against and guesses against the live org/site —
the same failure the Central config-model enrichment fixed (#384).

`scripts/distill_mist_schemas.py` distills those bodies into a committed
artifact (`_request_body_schemas.json`) shipped alongside this module.
`mist_get_tool_schema` calls :func:`lookup_payload_schema` to attach the
resolved field set to its response for body-bearing tools.

The artifact is keyed by component schema name (create/update tools that share
a body reference one entry); `tool_index` maps a tool name to its component.
A missing or malformed artifact degrades gracefully to "no schema".
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

from loguru import logger

_ARTIFACT_PATH = Path(__file__).with_name("_request_body_schemas.json")


@lru_cache(maxsize=1)
def _load() -> dict[str, Any]:
    """Load and cache the distilled artifact; empty structure on any failure."""
    try:
        data = json.loads(_ARTIFACT_PATH.read_text(encoding="utf-8"))
    except FileNotFoundError:
        logger.warning(
            "Mist request-body schemas artifact not found at {} — payload schemas "
            "will not be surfaced. Run scripts/distill_mist_schemas.py to regenerate.",
            _ARTIFACT_PATH.name,
        )
        return {"schemas": {}, "tool_index": {}}
    except (json.JSONDecodeError, OSError) as exc:
        logger.warning("Failed to load Mist request-body schemas ({}): {}", _ARTIFACT_PATH.name, exc)
        return {"schemas": {}, "tool_index": {}}

    if not isinstance(data, dict):
        return {"schemas": {}, "tool_index": {}}
    data.setdefault("schemas", {})
    data.setdefault("tool_index", {})
    return data


def lookup_payload_schema(tool_name: str) -> dict[str, Any] | None:
    """Return the distilled body schema for a Mist tool, or ``None``.

    Args:
        tool_name: Fully-qualified tool name, e.g. ``"mist_create_site_wlan"``.

    Returns:
        ``{"object": <component>, "fields": {...}}`` for an object body, or
        ``{"object": <component>, "root": {...}}`` for an array / oneOf / map
        body. ``None`` when the tool takes no request body (e.g. GET tools).
    """
    data = _load()
    comp = data["tool_index"].get(tool_name)
    if comp is None:
        return None
    entry = data["schemas"].get(comp)
    if not entry:
        return None
    return {"object": comp, **entry}
