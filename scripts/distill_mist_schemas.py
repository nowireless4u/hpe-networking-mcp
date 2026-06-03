# ruff: noqa: E501
"""Distill Mist request-body schemas into a committed runtime artifact.

Mist write/config tools (`mist_create_*`, `mist_update_*`, …) take an opaque
`body: dict[str, Any]` described only as "Request Body" — the field set lives
only in the vendored OpenAPI spec, which is **not** shipped in the runtime
image (the Dockerfile copies `src/` only). So an AI client driving these tools
has no schema to author against and guesses against the live org/site, exactly
the failure the Central config-model enrichment fixed (#384 / #386). This is
the Mist counterpart.

This script reads `vendor/mist/mist_openapi.json` (the upstream Juniper Mist
OpenAPI 3.1 spec, auto-synced daily), reuses `_mist_generator` for operation
walking + tool naming so names match the generated tools exactly, resolves
each body's request schema (`$ref` / `allOf` / `oneOf` / `anyOf` / array
root), distills it to field names + types + enums (descriptions dropped,
catalog-sized enums capped), and writes a committed JSON file under `src/`:

    src/hpe_networking_mcp/platforms/mist/_request_body_schemas.json

`mist_get_tool_schema` loads it and attaches a `payload_schema` to its response
for body-bearing tools (see `mist/request_body_schemas.py`).

Bodies are deduped by their component-schema name (every Mist body is a direct
`$ref`), so create/update tools that share one component reference one entry.

Safe to re-run; emits only the data artifact. Keep it in lockstep with the
spec sync by running it from `regenerate_mist_tools.py`.

    uv run python scripts/distill_mist_schemas.py
    uv run python scripts/distill_mist_schemas.py --dry-run
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _mist_generator import load_spec, walk_operations  # noqa: E402

# Cap recursion depth and enum length so a deep or catalog-sized schema can't
# dwarf the artifact. Mist bodies nest ~3-5 deep; the few huge enums are not
# hand-authored against a flat list anyway.
_MAX_DEPTH = 8
_MAX_ENUM = 40


def _cap_enum(values: list[Any]) -> tuple[list[Any], int | None]:
    if len(values) > _MAX_ENUM:
        return values[:_MAX_ENUM], len(values)
    return values, None


def _resolve_ref(spec: dict[str, Any], ref: str) -> dict[str, Any]:
    """Resolve a local ``#/...`` JSON pointer within the spec."""
    node: Any = spec
    for part in ref.lstrip("#/").split("/"):
        if not isinstance(node, dict):
            return {}
        node = node.get(part, {})
    return node if isinstance(node, dict) else {}


def _ref_name(ref: str) -> str:
    """Component name from a ``$ref`` — ``#/components/schemas/wlan`` → ``wlan``."""
    return ref.rsplit("/", 1)[-1]


def _distill_fields(schema: dict[str, Any], spec: dict[str, Any], depth: int) -> dict[str, Any]:
    """Object schema → {field: descriptor}. Merges allOf; {} if not an object."""
    if depth > _MAX_DEPTH or not isinstance(schema, dict):
        return {}
    if "$ref" in schema:
        return _distill_fields(_resolve_ref(spec, schema["$ref"]), spec, depth)
    if "allOf" in schema:
        merged: dict[str, Any] = {}
        for member in schema["allOf"]:
            part = _distill_fields(member, spec, depth)
            if isinstance(part, dict):
                merged.update(part)
        if "properties" in schema:
            merged.update(_distill_fields({"properties": schema["properties"]}, spec, depth))
        return merged
    props = schema.get("properties")
    if isinstance(props, dict):
        required = set(schema.get("required") or [])
        return {name: _distill_field(fdef, spec, depth, name in required) for name, fdef in props.items()}
    return {}


def _distill_field(fdef: dict[str, Any], spec: dict[str, Any], depth: int, required: bool) -> dict[str, Any]:
    """One property → compact descriptor (type, enum, nested properties/items)."""
    if "$ref" in fdef:
        fdef = _resolve_ref(spec, fdef["$ref"])

    entry: dict[str, Any] = {}

    # oneOf/anyOf: capture a type union + any enum; recurse object variants once.
    variants = fdef.get("oneOf") or fdef.get("anyOf")
    if variants:
        types: list[str] = []
        enum_vals: list[Any] = []
        for member in variants:
            m = _resolve_ref(spec, member["$ref"]) if "$ref" in member else member
            if m.get("type"):
                types.append(m["type"])
            if m.get("enum"):
                enum_vals = m["enum"]
        if types:
            entry["type"] = "|".join(dict.fromkeys(types))
        if enum_vals:
            capped, full = _cap_enum(enum_vals)
            entry["enum"] = capped
            if full is not None:
                entry["enum_count"] = full

    ftype = fdef.get("type")
    if ftype and "type" not in entry:
        entry["type"] = ftype
    if fdef.get("enum") and "enum" not in entry:
        capped, full = _cap_enum(fdef["enum"])
        entry["enum"] = capped
        if full is not None:
            entry["enum_count"] = full
    if required:
        entry["mandatory"] = True

    # Nested object.
    if (fdef.get("properties") or fdef.get("allOf")) and ftype != "array":
        children = _distill_fields(fdef, spec, depth + 1)
        if children:
            entry["type"] = entry.get("type") or "object"
            entry["properties"] = children

    # Array → distill the item schema.
    if ftype == "array":
        item_children = _distill_fields(fdef.get("items") or {}, spec, depth + 1)
        entry["type"] = "array"
        if item_children:
            entry["items"] = item_children

    return entry


def distill_request_body(schema: dict[str, Any], spec: dict[str, Any]) -> dict[str, Any]:
    """Top-level distill of a request-body schema.

    Returns ``{"fields": {...}}`` for the common object body, or ``{"root": {...}}``
    for array-rooted (bulk import/claim) and oneOf/anyOf-rooted (device-profile,
    packet-capture) bodies so those don't distill to nothing.
    """
    if "$ref" in schema:
        schema = _resolve_ref(spec, schema["$ref"])

    fields = _distill_fields(schema, spec, 0)
    if fields:
        return {"fields": fields}

    # Non-object root: array or oneOf/anyOf union.
    if schema.get("type") == "array":
        items = _distill_fields(schema.get("items") or {}, spec, 1)
        return {"root": {"type": "array", "items": items}}

    variants = schema.get("oneOf") or schema.get("anyOf")
    if variants:
        out_variants = []
        for member in variants:
            mf = _distill_fields(member, spec, 1)
            if mf:
                out_variants.append({"type": "object", "properties": mf})
        if out_variants:
            return {"root": {"variants": out_variants}}

    # Free-form map: object with additionalProperties and no fixed fields
    # (e.g. port-name → config). Describe the value shape so it's not empty.
    addl = schema.get("additionalProperties")
    if isinstance(addl, dict):
        return {"root": {"type": "object", "additional_properties": _distill_field(addl, spec, 1, False)}}

    return {"fields": {}}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spec", type=Path, default=None)
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument("--dry-run", action="store_true", help="Report counts/size, write nothing.")
    args = parser.parse_args(argv)

    here = Path(__file__).resolve()
    root = next(p for p in here.parents if (p / "pyproject.toml").exists())
    spec_path = args.spec or (root / "vendor" / "mist" / "mist_openapi.json")
    output = args.output or (root / "src" / "hpe_networking_mcp" / "platforms" / "mist" / "_request_body_schemas.json")

    if not spec_path.exists():
        print(f"ERROR: Mist spec not found at {spec_path}", file=sys.stderr)
        return 1

    spec = load_spec(spec_path)
    body_ops = [o for o in walk_operations(spec) if o.has_body]

    def _body_ref(op: Any) -> str | None:
        node = spec["paths"][op.path][op.method.lower()].get("requestBody") or {}
        if "$ref" in node:
            node = _resolve_ref(spec, node["$ref"])
        for media in (node.get("content") or {}).values():
            return (media.get("schema") or {}).get("$ref")
        return None

    schemas: dict[str, Any] = {}
    tool_index: dict[str, str] = {}
    inline = 0
    empty: list[str] = []

    for op in body_ops:
        ref = _body_ref(op)
        if ref:
            comp = _ref_name(ref)
            raw = _resolve_ref(spec, ref)
        else:
            # Inline body schema (rare) — key by tool name.
            comp = op.tool_name
            inline += 1
            node = spec["paths"][op.path][op.method.lower()].get("requestBody") or {}
            raw = {}
            for media in (node.get("content") or {}).values():
                raw = media.get("schema") or {}
                break

        tool_index[op.tool_name] = comp
        if comp not in schemas:
            distilled = distill_request_body(raw, spec)
            if not distilled.get("fields") and not distilled.get("root"):
                empty.append(comp)
            schemas[comp] = distilled

    artifact = {
        "_comment": (
            "Generated by scripts/distill_mist_schemas.py from vendor/mist/mist_openapi.json. "
            "Do not edit by hand; re-run the distiller. Keyed by component schema name; "
            "tool_index maps tool name -> component. See issue #384 (Mist counterpart)."
        ),
        "schemas": schemas,
        "tool_index": tool_index,
    }
    blob = json.dumps(artifact, indent=1, sort_keys=True)
    size_kb = len(blob.encode("utf-8")) / 1024

    print(f"Body-bearing ops: {len(body_ops)} ({inline} inline-body).")
    print(f"Distinct component schemas: {len(schemas)} ({len(empty)} distilled empty).")
    print(f"Indexed {len(tool_index)} tool names → schema.")
    print(f"Artifact size: {size_kb:.1f} KiB")
    if empty:
        print(f"  empty (no distillable shape): {empty[:10]}{' …' if len(empty) > 10 else ''}", file=sys.stderr)

    if args.dry_run:
        print("(--dry-run; nothing written)")
        return 0

    output.write_text(blob + "\n", encoding="utf-8")
    print(f"Wrote {output.relative_to(root)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
