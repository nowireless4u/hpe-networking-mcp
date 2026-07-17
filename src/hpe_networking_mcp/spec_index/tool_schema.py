"""Map a tool name to its request-body schema via the spec index.

The opaque-body tools give an AI client no field set to author against — the gap
that left an operator guessing field names to rename an AP:
  * Central config tools (``central_manage_*`` / ``central_get_*``) take a
    ``payload: dict`` → resolved via the tool's network-config resource segment.
  * Mist write tools (``mist_create_*`` / ``mist_update_*`` / …) take a
    ``body: dict`` → resolved by reversing ``mist_<snake(operationId)>``.

Each resolves to the body schema in the spec index (fields + enums + examples +
constraints + device types + scope params, or a ``root``/``variants`` shape for
array/oneOf/map bodies), so ``get_schema`` surfaces it. This is the single schema
source of truth — it supersedes the distilled ``_config_payload_schemas.json``
(Central) and ``_request_body_schemas.json`` (Mist) artifacts, and is complete
where they were not (e.g. it has ``system-info``, which the Central artifact
lacked).
"""

from __future__ import annotations

import inspect
import re
from typing import Any

from hpe_networking_mcp.spec_index.query import SpecIndex, get_spec_index

# The network-config resource segment a Central config tool operates on is a
# literal first arg to its ``_get_resource`` / ``_manage_resource`` call — often
# unrelated to the tool name (renamed, pluralized, or hand-curated, e.g.
# ``central_manage_config_assignment`` → ``gw-cluster-intent-config``). Read it
# from the tool's own source so the mapping is exact rather than guessed.
_CENTRAL_RESOURCE_RE = re.compile(r'_(?:get|manage)_resource\(\s*ctx,\s*["\']([\w-]+)["\']')
# Hand-curated config tools call the API directly with an explicit path rather
# than ``_manage_resource`` — read the resource segment out of that path.
_CENTRAL_PATH_RE = re.compile(r"network-config/v[\w.]+/([\w-]+)")
# Some hand-curated tools hit a *nested* endpoint on a different namespace
# (e.g. ``network-monitoring/v1/sitemaps/{site-id}/buildings/{building-id}``)
# that neither pattern above matches. Capture the whole literal ``api_path`` so
# the resource segment can be taken from the tail of the path instead.
_CENTRAL_LITERAL_PATH_RE = re.compile(r'api_path\s*=\s*f?["\']([^"\'{][^"\']*)["\']')
_central_segment_cache: dict[str, str | None] = {}


def _tail_segment(path_template: str) -> str | None:
    """Last non-parameter segment of a URL path template.

    ``.../sitemaps/{site-id}/buildings/{building-id}`` → ``buildings``. That
    segment is what ``config_body`` matches on (``path LIKE '%/buildings/%'``),
    so it resolves the write body for nested endpoints the flat network-config
    patterns miss.
    """
    segs = [s for s in path_template.split("/") if s and not s.startswith("{")]
    # Skip the version-prefix segments (namespace + ``v1``/``v1alpha1``).
    meaningful = [s for s in segs if not re.fullmatch(r"v[\w.]+", s)]
    return meaningful[-1] if meaningful else None


def _central_segment(tool_name: str) -> str | None:
    """The exact network-config resource segment for a Central config tool.

    Resolves via the tool's registered function source; falls back to the
    name-derived guess. Cached (tool source is immutable at runtime).
    """
    if tool_name in _central_segment_cache:
        return _central_segment_cache[tool_name]
    seg: str | None = None
    try:
        from hpe_networking_mcp.platforms._common.tool_registry import REGISTRIES

        registry = REGISTRIES.get("central")
        spec = registry.get(tool_name) if registry is not None else None
        if spec is not None and getattr(spec, "func", None) is not None:
            src = inspect.getsource(spec.func)
            match = _CENTRAL_RESOURCE_RE.search(src) or _CENTRAL_PATH_RE.search(src)
            if match:
                seg = match.group(1)
            else:
                # Nested / non-config path — take the tail resource segment.
                lit = _CENTRAL_LITERAL_PATH_RE.search(src)
                if lit:
                    seg = _tail_segment(lit.group(1))
    except Exception:
        seg = None
    if seg is None:  # fall back to the name convention (covers regular tools pre-registration)
        for prefix in ("central_manage_", "central_get_"):
            if tool_name.startswith(prefix):
                seg = tool_name[len(prefix) :].replace("_", "-")
                break
    _central_segment_cache[tool_name] = seg
    return seg


# camelCase/PascalCase → snake_case, matching the Mist tool generator verbatim
# (``tool_name == "mist_" + to_snake_case(operationId)``), so reversing the tool
# name resolves the exact operation → request body schema.
_CAMEL_RE_1 = re.compile(r"(.)([A-Z][a-z]+)")
_CAMEL_RE_2 = re.compile(r"([a-z0-9])([A-Z])")


def _to_snake(name: str) -> str:
    result = _CAMEL_RE_1.sub(r"\1_\2", name)
    result = _CAMEL_RE_2.sub(r"\1_\2", result)
    return result.lower()


_MAX_ENUM_SHOWN = 40


def _mist_body_schema(idx: SpecIndex, tool_name: str) -> dict[str, Any] | None:
    """Resolve a Mist tool's opaque ``body`` schema by reversing its name.

    ``mist_create_site_wlan`` → operationId whose snake form is
    ``create_site_wlan`` → that endpoint's request schema → its fields.
    """
    snake = tool_name[len("mist_") :]
    schema_name = next(
        (sch for op_id, sch in idx.operation_schemas("mist").items() if _to_snake(op_id) == snake),
        None,
    )
    if not schema_name:
        return None
    body = idx.schema_body("mist", schema_name)
    return {"object": schema_name, **body} if body else None


def payload_schema_for_tool(tool_name: str) -> dict[str, Any] | None:
    """Return the request-body schema for a body-bearing tool, or ``None``.

    Covers the opaque ``payload: dict`` Central config tools and the opaque
    ``body: dict`` Mist write tools. ``None`` for every other tool, an
    unavailable index, and any tool whose body can't be resolved — callers treat
    it as "no enrichment".
    """
    if not tool_name:
        return None
    idx = get_spec_index()
    if not idx.available:
        return None
    if tool_name.startswith(("central_manage_", "central_get_")):
        resource = _central_segment(tool_name)
        return idx.config_body("central", resource) if resource else None
    if tool_name.startswith("mist_"):
        return _mist_body_schema(idx, tool_name)
    return None


def render_payload_schema(tool_name: str, schema: dict[str, Any]) -> str:
    """Render a config-body schema as a compact text block for get_schema output.

    Format-agnostic (appended to whatever detail level get_schema produced), so
    it works for brief / detailed / full alike.
    """
    lines = [f"━━━ PAYLOAD SCHEMA for {tool_name} (spec index) ━━━"]
    if schema.get("path"):
        lines.append(f"body: {schema['method']} {schema['path']}")
    # Non-object bodies: describe the shape instead of a field list.
    if schema.get("root"):
        lines.append(f"body shape: {schema['root']}")
    if schema.get("variants"):
        lines.append("body — one of: " + ", ".join(schema["variants"]))
    for f in schema.get("fields", []):
        parts = [f["type"] or "any"]
        if f["required"]:
            parts.append("required")
        if f.get("read_only"):
            parts.append("read-only")
        if f.get("deprecated"):
            parts.append("DEPRECATED")
        if f.get("device_types"):
            parts.append("devices=" + ",".join(f["device_types"]))
        line = f"  {f['name']} ({', '.join(parts)})"
        if f.get("enum"):
            vals = f["enum"][:_MAX_ENUM_SHOWN]
            more = "" if len(f["enum"]) <= _MAX_ENUM_SHOWN else f" … (+{len(f['enum']) - _MAX_ENUM_SHOWN})"
            line += " — one of: " + ", ".join(str(v) for v in vals) + more
        if f.get("description"):
            line += f" — {f['description']}"
        lines.append(line)
    # Query/scope params (object-type, scope-id, device-function, …) are
    # intentionally NOT rendered here: the tool signature declares them, so they
    # already appear in the tool's own input_schema. Advertising them a second
    # time from the spec index is what let get_schema list a parameter the
    # wrapper didn't accept — the "advertised but rejected" mismatch. The index
    # owns the request body (which the opaque payload: dict can't express); the
    # tool owns its parameters.
    return "\n".join(lines)
