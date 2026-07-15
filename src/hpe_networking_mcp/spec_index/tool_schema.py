"""Map a tool name to its config-body schema via the spec index.

The opaque ``payload: dict`` config tools (``central_manage_*`` / ``central_get_*``)
give an AI client no field set to author against — the exact gap that left an
operator guessing field names to rename an AP. This resolves such a tool to its
network-config body schema in the spec index (fields + enums + examples +
constraints + device types + the scope query params), so ``get_schema`` can
surface it. Supersedes the distilled ``_config_payload_schemas.json`` mechanism:
the index is complete (it has ``system-info``, which the distilled artifact
lacked) and richer, and is the single schema source of truth.
"""

from __future__ import annotations

from typing import Any

from hpe_networking_mcp.spec_index.query import get_spec_index

# Config-body tool prefixes → their platform. The suffix after the prefix is the
# resource path segment (underscores → hyphens): ``central_manage_system_info``
# → ``system-info`` → ``/network-config/.../system-info/{name}``.
_CONFIG_TOOL_PREFIXES: dict[str, str] = {
    "central_manage_": "central",
    "central_get_": "central",
}

_MAX_ENUM_SHOWN = 40


def payload_schema_for_tool(tool_name: str) -> dict[str, Any] | None:
    """Return the config-body schema for a config tool, or ``None``.

    ``None`` covers every non-config tool, an unavailable index, and any tool
    whose resource can't be resolved — callers treat it as "no enrichment".
    """
    if not tool_name:
        return None
    idx = get_spec_index()
    if not idx.available:
        return None
    for prefix, platform in _CONFIG_TOOL_PREFIXES.items():
        if tool_name.startswith(prefix):
            resource = tool_name[len(prefix) :].replace("_", "-")
            return idx.config_body(platform, resource)
    return None


def render_payload_schema(tool_name: str, schema: dict[str, Any]) -> str:
    """Render a config-body schema as a compact text block for get_schema output.

    Format-agnostic (appended to whatever detail level get_schema produced), so
    it works for brief / detailed / full alike.
    """
    lines = [
        f"━━━ PAYLOAD SCHEMA for {tool_name} (spec index) ━━━",
        f"body: {schema['method']} {schema['path']}",
    ]
    for f in schema["fields"]:
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
    if schema.get("scope_parameters"):
        scope = ", ".join(f"{p['name']}{'*' if p['required'] else ''}" for p in schema["scope_parameters"])
        lines.append(f"scope query params: {scope}   (* = required)")
    return "\n".join(lines)
