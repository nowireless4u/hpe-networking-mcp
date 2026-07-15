#!/usr/bin/env python3
"""Build the SQLite/FTS5 spec-lookup index from the vendored OpenAPI specs.

Parses every vendored OpenAPI spec under ``vendor/**`` into a deterministic
SQLite index — ``endpoints``, ``parameters``, ``schemas``, ``fields`` plus FTS5
mirrors — so the server can answer exact "which endpoint / field / enum / param"
questions and enrich ``get_schema`` output and validation errors WITHOUT a model,
embeddings, or hallucination.

Design is schema-centric: every component schema is indexed once, endpoints link
to their request/response schema by name, and nested structures are reached by
following ``ref_schema`` / ``item_ref`` — no dotted-path materialization.

Excluded from the index:
  * non-spec JSON (no ``openapi``/``swagger`` key): ``_manifest.json``,
    ``sources.json`` — vendoring metadata, not specs.
  * ``vendor/aoscx/**`` — orphan spec with no platform/tools (AOS-CX is reached
    via CNX / Central, never directly), so its endpoints would be pure noise.

Run at image build; the resulting ``.db`` is baked into the image.

Usage:
    python scripts/build_spec_index.py [OUTPUT_DB]
"""

from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
VENDOR = ROOT / "vendor"
DEFAULT_DB = ROOT / "src" / "hpe_networking_mcp" / "spec_index" / "spec_index.db"

# Vendored specs with no backing platform/tools — indexing them injects
# endpoints the model has no tool to call.
EXCLUDED_PLATFORMS = {"aoscx"}

# Per-platform source trust. All current vendored specs are trustworthy
# (auto-synced from vendor dev-portals, or — for EdgeConnect — exported from the
# orchestrator's own live Swagger). Kept as a column so a future low-trust source
# can be caveated in enrichment without a schema change.
PLATFORM_TRUST: dict[str, str] = {}

_BODY_MEDIA_PRIORITY = ("application/json", "application/merge-patch+json", "*/*")
_CONSTRAINT_KEYS = ("minimum", "maximum", "minLength", "maxLength", "pattern", "minItems", "maxItems")


def _platform_of(path: Path) -> str:
    return path.relative_to(VENDOR).parts[0]


def _load_spec(path: Path) -> dict[str, Any] | None:
    """Return a parsed OpenAPI spec, or None for non-spec / unparseable JSON."""
    try:
        data = json.loads(path.read_text())
    except (ValueError, OSError):
        return None
    if not isinstance(data, dict) or not (data.get("openapi") or data.get("swagger")):
        return None
    return data


def _ref_name(ref: Any) -> str | None:
    """``"#/components/schemas/Foo"`` -> ``"Foo"``."""
    return ref.rsplit("/", 1)[-1] if isinstance(ref, str) and ref.startswith("#/") else None


def _as_type(value: Any) -> str | None:
    """Normalize an OpenAPI ``type`` to a string.

    OpenAPI 3.1 permits a type array (e.g. ``["string", "null"]`` for a nullable
    field); collapse it to a ``"|"``-joined string so it stores as TEXT.
    """
    if value is None:
        return None
    if isinstance(value, list):
        return "|".join(str(v) for v in value) or None
    return str(value)


def _example_json(node: dict[str, Any]) -> str | None:
    """A representative example from a schema/param/media node, JSON-encoded.

    Prefers the singular ``example``; falls back to the first ``value`` of an
    ``examples`` map (OpenAPI media-type / parameter style — e.g. Mist's request
    body examples). Gives the model a known-valid starting value.
    """
    if "example" in node:
        return json.dumps(node["example"])
    examples = node.get("examples")
    if isinstance(examples, dict):
        for ex in examples.values():
            if isinstance(ex, dict) and "value" in ex:
                return json.dumps(ex["value"])
    return None


def _deprecated_note(node: dict[str, Any]) -> str | None:
    """Deprecation reason/sunset text from vendor extensions, if present.

    OpenAPI ``deprecated`` is only a boolean; vendors carry the *why*/*when* in
    ``x-deprecation-notice`` / ``x-deprecated-reason`` (EdgeConnect) — or inline
    in ``description`` (GreenLake), which is already indexed. Surfacing the
    extension lets the model see the sunset context.
    """
    note = node.get("x-deprecation-notice") or node.get("x-deprecated-reason")
    return str(note) if note else None


def _root_descriptor(schema: dict[str, Any]) -> str | None:
    """A compact shape for a non-object body (array of primitives, or a scalar).

    Object bodies (fields) and oneOf/anyOf bodies (variants) are described
    elsewhere; this covers ``[string]`` / ``[<Schema>]`` / bare scalar bodies so
    enrichment isn't blank for e.g. Mist's ``claim``/``import`` serial-list tools.
    Returns ``None`` for object schemas (they have fields).
    """
    t = schema.get("type")
    if t == "array":
        items = schema.get("items") or {}
        if isinstance(items, dict):
            item = _ref_name(items.get("$ref")) or _as_type(items.get("type")) or "object"
        else:
            item = "object"
        return f"array[{item}]"
    if isinstance(t, str) and t in ("string", "integer", "number", "boolean"):
        return t
    # Free-form map: object with dynamic keys (additionalProperties) and no fixed
    # properties — e.g. Mist per-port / per-device config keyed by name.
    ap = schema.get("additionalProperties")
    if ap and not schema.get("properties"):
        val = "any"
        if isinstance(ap, dict):
            val = _ref_name(ap.get("$ref")) or _as_type(ap.get("type")) or "object"
        return f"map[string→{val}]"
    return None


def _variant_refs(node: dict[str, Any]) -> list[str]:
    """Schema names a field/schema may take via ``oneOf``/``anyOf`` (alternatives).

    Unlike ``allOf`` (merged), these are mutually-exclusive shapes; capturing the
    variant names lets enrichment show "this may be any of [A, B, C]".
    """
    out: list[str] = []
    for key in ("oneOf", "anyOf"):
        for member in node.get(key, []) or []:
            if isinstance(member, dict):
                name = _ref_name(member.get("$ref"))
                if name:
                    out.append(name)
    return out


def _resolve_ref(spec: dict[str, Any], ref: str) -> Any:
    """Resolve a local ``#/a/b/c`` JSON pointer within one spec."""
    node: Any = spec
    for part in ref.lstrip("#/").split("/"):
        if not isinstance(node, dict):
            return None
        node = node.get(part.replace("~1", "/").replace("~0", "~"))
    return node


def _schema_from_content(spec: dict[str, Any], container: dict[str, Any]) -> tuple[str | None, dict | None]:
    """From a requestBody/response object, return (schema_name_ref, inline_schema)."""
    if not isinstance(container, dict):
        return None, None
    if "$ref" in container:
        container = _resolve_ref(spec, container["$ref"]) or {}
    content = container.get("content", {}) or {}
    media = None
    for mt in _BODY_MEDIA_PRIORITY:
        if mt in content:
            media = content[mt]
            break
    if media is None and content:
        media = next(iter(content.values()))
    if not isinstance(media, dict):
        return None, None
    sch = media.get("schema")
    if not isinstance(sch, dict):
        return None, None
    if "$ref" in sch:
        return _ref_name(sch["$ref"]), None
    return None, sch


def _request_example(spec: dict[str, Any], request_body: dict[str, Any]) -> str | None:
    """A copy-paste-valid request body example, if the spec provides one."""
    if not isinstance(request_body, dict):
        return None
    if "$ref" in request_body:
        request_body = _resolve_ref(spec, request_body["$ref"]) or {}
    content = request_body.get("content", {}) or {}
    media = None
    for mt in _BODY_MEDIA_PRIORITY:
        if mt in content:
            media = content[mt]
            break
    if media is None and content:
        media = next(iter(content.values()))
    return _example_json(media) if isinstance(media, dict) else None


def _iter_field_defs(
    spec: dict[str, Any], schema: dict[str, Any], _seen: set[str] | None = None
) -> list[tuple[str, dict, bool]]:
    """Yield (field_name, field_def, required) for a schema, flattening allOf.

    Both inline **and** ``$ref`` ``allOf`` members are merged (recursively, with
    cycle protection) — many Central config bodies are a pure
    ``{"allOf": [{"$ref": Base}]}`` whose fields live entirely in the referenced
    base, so not following the ref would leave the composed schema with zero
    fields. oneOf/anyOf are not flattened (their variants are separate schemas).
    """
    _seen = _seen if _seen is not None else set()
    out: list[tuple[str, dict, bool]] = []
    required = set(schema.get("required", []) or [])
    props = schema.get("properties", {}) or {}
    for fname, fdef in props.items():
        if isinstance(fdef, dict):
            out.append((fname, fdef, fname in required))
    # Array body: fields live on the element schema (many Mist bulk/import tools
    # take ``[{item}]``), so descend into ``items`` so the body isn't empty.
    items = schema.get("items")
    if not props and isinstance(items, dict):
        if "$ref" in items and items["$ref"] not in _seen:
            _seen.add(items["$ref"])
            resolved = _resolve_ref(spec, items["$ref"])
            if isinstance(resolved, dict):
                out.extend(_iter_field_defs(spec, resolved, _seen))
        elif "properties" in items or "allOf" in items:
            out.extend(_iter_field_defs(spec, items, _seen))
    for member in schema.get("allOf", []) or []:
        if not isinstance(member, dict):
            continue
        if "$ref" in member:
            ref = member["$ref"]
            if ref in _seen:
                continue
            _seen.add(ref)
            resolved = _resolve_ref(spec, ref)
            if isinstance(resolved, dict):
                for fname, fdef, req in _iter_field_defs(spec, resolved, _seen):
                    out.append((fname, fdef, req or fname in required))
        elif "properties" in member:
            member_req = set(member.get("required", []) or [])
            for fname, fdef in (member.get("properties") or {}).items():
                if isinstance(fdef, dict):
                    out.append((fname, fdef, fname in required or fname in member_req))
    return out


def _field_row(fname: str, fdef: dict[str, Any], required: bool) -> dict[str, Any]:
    ref = _ref_name(fdef.get("$ref"))
    item_type = item_ref = None
    items = fdef.get("items")
    if isinstance(items, dict):
        item_ref = _ref_name(items.get("$ref"))
        item_type = items.get("type")
    enum = fdef.get("enum")
    constraints = {k: fdef[k] for k in _CONSTRAINT_KEYS if k in fdef}
    variants = _variant_refs(fdef)
    return {
        "field_name": fname,
        "type": _as_type(fdef.get("type")),
        "ref_schema": ref,
        "item_type": _as_type(item_type),
        "item_ref": item_ref,
        "format": fdef.get("format"),
        "required": 1 if required else 0,
        "default": json.dumps(fdef["default"]) if "default" in fdef else None,
        "enum_json": json.dumps(enum) if isinstance(enum, list) and enum else None,
        "constraints_json": json.dumps(constraints) if constraints else None,
        "read_only": 1 if fdef.get("readOnly") else 0,
        "write_only": 1 if fdef.get("writeOnly") else 0,
        "deprecated": 1 if fdef.get("deprecated") else 0,
        "deprecated_note": _deprecated_note(fdef),
        "example": _example_json(fdef),
        "variants_json": json.dumps(variants) if variants else None,
        "device_types": (
            json.dumps(fdef["x-supportedDeviceType"]) if isinstance(fdef.get("x-supportedDeviceType"), list) else None
        ),
        "description": fdef.get("description"),
    }


_SCHEMA = """
CREATE TABLE endpoints (
    id INTEGER PRIMARY KEY, platform TEXT, spec_file TEXT, path TEXT, method TEXT,
    operation_id TEXT, summary TEXT, description TEXT, tags TEXT,
    request_schema TEXT, request_example TEXT, deprecated INTEGER, deprecated_note TEXT, trust TEXT
);
CREATE TABLE responses (
    id INTEGER PRIMARY KEY, endpoint_id INTEGER, status_code TEXT,
    description TEXT, schema_name TEXT
);
CREATE TABLE parameters (
    id INTEGER PRIMARY KEY, endpoint_id INTEGER, name TEXT, location TEXT,
    required INTEGER, type TEXT, format TEXT, enum_json TEXT, example TEXT,
    deprecated INTEGER, description TEXT
);
CREATE TABLE schemas (
    id INTEGER PRIMARY KEY, platform TEXT, spec_file TEXT, schema_name TEXT,
    description TEXT, enum_json TEXT, example TEXT, variants TEXT, root TEXT, trust TEXT
);
CREATE TABLE fields (
    id INTEGER PRIMARY KEY, schema_id INTEGER, field_name TEXT, type TEXT,
    ref_schema TEXT, item_type TEXT, item_ref TEXT, format TEXT, required INTEGER,
    "default" TEXT, enum_json TEXT, constraints_json TEXT, read_only INTEGER,
    write_only INTEGER, deprecated INTEGER, deprecated_note TEXT, example TEXT, variants TEXT,
    device_types TEXT, description TEXT
);
CREATE INDEX idx_endpoints_platform ON endpoints(platform);
CREATE INDEX idx_endpoints_opid ON endpoints(operation_id);
CREATE INDEX idx_endpoints_path ON endpoints(path);
CREATE INDEX idx_responses_endpoint ON responses(endpoint_id);
CREATE INDEX idx_params_endpoint ON parameters(endpoint_id);
CREATE INDEX idx_schemas_name ON schemas(platform, schema_name);
CREATE INDEX idx_fields_schema ON fields(schema_id);
CREATE INDEX idx_fields_name ON fields(field_name);
-- FTS rowid == the corresponding base-table id, so joins use ``fts.rowid = base.id``.
CREATE VIRTUAL TABLE endpoints_fts USING fts5(text);
CREATE VIRTUAL TABLE fields_fts USING fts5(text);
CREATE VIRTUAL TABLE schemas_fts USING fts5(text);
CREATE VIRTUAL TABLE parameters_fts USING fts5(text);
CREATE VIRTUAL TABLE responses_fts USING fts5(text);
"""


def build(db_path: Path) -> dict[str, int]:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    if db_path.exists():
        db_path.unlink()
    con = sqlite3.connect(db_path)
    con.executescript(_SCHEMA)
    counts = {
        "specs": 0,
        "endpoints": 0,
        "responses": 0,
        "parameters": 0,
        "schemas": 0,
        "fields": 0,
        "skipped": 0,
    }

    for spec_path in sorted(VENDOR.rglob("*.json")):
        platform = _platform_of(spec_path)
        if platform in EXCLUDED_PLATFORMS:
            continue
        spec = _load_spec(spec_path)
        if spec is None:
            counts["skipped"] += 1
            continue
        counts["specs"] += 1
        trust = PLATFORM_TRUST.get(platform, "high")
        spec_file = str(spec_path.relative_to(ROOT))

        # --- component schemas (index each once) ---
        for sname, sdef in (spec.get("components", {}).get("schemas", {}) or {}).items():
            if not isinstance(sdef, dict):
                continue
            _insert_schema(con, platform, spec_file, trust, sname, sdef, spec, counts)

        # --- paths → endpoints, params, inline schemas ---
        for path, path_item in (spec.get("paths", {}) or {}).items():
            if not isinstance(path_item, dict):
                continue
            shared_params = path_item.get("parameters", []) or []
            for method in ("get", "post", "put", "patch", "delete"):
                op = path_item.get(method)
                if not isinstance(op, dict):
                    continue
                request_body = op.get("requestBody", {}) or {}
                req_name, req_inline = _schema_from_content(spec, request_body)
                op_id = op.get("operationId")
                synth = op_id or f"{method}:{path}"
                if req_inline is not None:
                    req_name = _index_inline_schema(
                        con, platform, spec_file, trust, f"{synth}__request", spec, req_inline, counts
                    )

                cur = con.execute(
                    "INSERT INTO endpoints(platform, spec_file, path, method, operation_id, summary, "
                    "description, tags, request_schema, request_example, deprecated, deprecated_note, trust) "
                    "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
                    (
                        platform,
                        spec_file,
                        path,
                        method.upper(),
                        op_id,
                        op.get("summary"),
                        op.get("description"),
                        json.dumps(op.get("tags")) if op.get("tags") else None,
                        req_name,
                        _request_example(spec, request_body),
                        1 if op.get("deprecated") else 0,
                        _deprecated_note(op),
                        trust,
                    ),
                )
                eid = cur.lastrowid
                counts["endpoints"] += 1
                con.execute(
                    "INSERT INTO endpoints_fts(rowid, text) VALUES (?,?)",
                    (eid, f"{path} {op_id or ''} {op.get('summary') or ''} {' '.join(op.get('tags') or [])}"),
                )
                _insert_responses(con, spec, platform, spec_file, trust, eid, synth, op, counts)
                for p in list(shared_params) + list(op.get("parameters", []) or []):
                    _insert_parameter(con, spec, eid, p, counts)

    con.commit()
    con.execute("INSERT INTO endpoints_fts(endpoints_fts) VALUES('optimize')")
    con.execute("INSERT INTO fields_fts(fields_fts) VALUES('optimize')")
    con.commit()
    con.close()
    return counts


def _insert_field(con: sqlite3.Connection, schema_id: int, row: dict[str, Any], counts: dict[str, int]) -> None:
    cur = con.execute(
        "INSERT INTO fields(schema_id, field_name, type, ref_schema, item_type, item_ref, format, "
        'required, "default", enum_json, constraints_json, read_only, write_only, deprecated, '
        "deprecated_note, example, variants, device_types, description) "
        "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        (
            schema_id,
            row["field_name"],
            row["type"],
            row["ref_schema"],
            row["item_type"],
            row["item_ref"],
            row["format"],
            row["required"],
            row["default"],
            row["enum_json"],
            row["constraints_json"],
            row["read_only"],
            row["write_only"],
            row["deprecated"],
            row["deprecated_note"],
            row["example"],
            row["variants_json"],
            row["device_types"],
            row["description"],
        ),
    )
    counts["fields"] += 1
    enum_text = " ".join(str(v) for v in json.loads(row["enum_json"])) if row["enum_json"] else ""
    con.execute(
        "INSERT INTO fields_fts(rowid, text) VALUES (?,?)",
        (cur.lastrowid, f"{row['field_name']} {row['description'] or ''} {enum_text}"),
    )


def _insert_responses(
    con: sqlite3.Connection,
    spec: dict[str, Any],
    platform: str,
    spec_file: str,
    trust: str,
    endpoint_id: int,
    synth: str,
    op: dict[str, Any],
    counts: dict[str, int],
) -> None:
    """Record every declared response (all status codes) + its description + body.

    The description is what tells the model "429 = rate limited". The success
    (2xx) body schema is materialized so its fields are queryable; inline error
    bodies are not synthesized (keeps the index bounded — ClearPass alone has
    thousands of error responses).
    """
    for code, resp in (op.get("responses") or {}).items():
        if isinstance(resp, dict) and "$ref" in resp:
            resp = _resolve_ref(spec, resp["$ref"]) or {}
        if not isinstance(resp, dict):
            continue
        schema_name, inline = _schema_from_content(spec, resp)
        if inline is not None and str(code).startswith("2"):
            schema_name = _index_inline_schema(
                con, platform, spec_file, trust, f"{synth}__resp_{code}", spec, inline, counts
            )
        cur = con.execute(
            "INSERT INTO responses(endpoint_id, status_code, description, schema_name) VALUES (?,?,?,?)",
            (endpoint_id, str(code), resp.get("description"), schema_name),
        )
        counts["responses"] += 1
        con.execute(
            "INSERT INTO responses_fts(rowid, text) VALUES (?,?)",
            (cur.lastrowid, f"{code} {resp.get('description') or ''}"),
        )


def _insert_schema(
    con: sqlite3.Connection,
    platform: str,
    spec_file: str,
    trust: str,
    name: str,
    sdef: dict[str, Any],
    spec: dict[str, Any],
    counts: dict[str, int],
) -> int:
    """Index one schema row (+ its fields, + FTS). Captures a schema-LEVEL enum.

    Mist / ClearPass model an enum as a standalone named schema whose root is
    ``{"type": "string", "enum": [...]}`` (referenced by fields via ``$ref``), so
    the enum lives on the schema, not a property. Storing it here lets enrichment
    resolve a field's legal values by following ``ref_schema`` to this row.
    """
    enum = sdef.get("enum")
    enum_json = json.dumps(enum) if isinstance(enum, list) and enum else None
    variants = _variant_refs(sdef)
    cur = con.execute(
        "INSERT INTO schemas(platform, spec_file, schema_name, description, enum_json, example, variants, root, trust) "
        "VALUES (?,?,?,?,?,?,?,?,?)",
        (
            platform,
            spec_file,
            name,
            sdef.get("description"),
            enum_json,
            _example_json(sdef),
            json.dumps(variants) if variants else None,
            _root_descriptor(sdef),
            trust,
        ),
    )
    sid = cur.lastrowid
    counts["schemas"] += 1
    enum_text = " ".join(str(v) for v in enum) if isinstance(enum, list) else ""
    con.execute(
        "INSERT INTO schemas_fts(rowid, text) VALUES (?,?)",
        (sid, f"{name} {sdef.get('description') or ''} {enum_text}"),
    )
    for fname, fdef, req in _iter_field_defs(spec, sdef):
        _insert_field(con, sid, _field_row(fname, fdef, req), counts)
    return sid


def _index_inline_schema(
    con: sqlite3.Connection,
    platform: str,
    spec_file: str,
    trust: str,
    name: str,
    spec: dict[str, Any],
    schema: dict[str, Any],
    counts: dict[str, int],
) -> str:
    _insert_schema(con, platform, spec_file, trust, name, schema, spec, counts)
    return name


def _insert_parameter(
    con: sqlite3.Connection, spec: dict[str, Any], endpoint_id: int, param: Any, counts: dict[str, int]
) -> None:
    if isinstance(param, dict) and "$ref" in param:
        param = _resolve_ref(spec, param["$ref"])
    if not isinstance(param, dict) or not param.get("name"):
        return
    psch = param.get("schema", {}) or {}
    enum = psch.get("enum")
    cur = con.execute(
        "INSERT INTO parameters(endpoint_id, name, location, required, type, format, enum_json, "
        "example, deprecated, description) VALUES (?,?,?,?,?,?,?,?,?,?)",
        (
            endpoint_id,
            param.get("name"),
            param.get("in"),
            1 if param.get("required") else 0,
            _as_type(psch.get("type")),
            psch.get("format"),
            json.dumps(enum) if isinstance(enum, list) and enum else None,
            _example_json(param) or _example_json(psch),
            1 if param.get("deprecated") else 0,
            param.get("description"),
        ),
    )
    counts["parameters"] += 1
    enum_text = " ".join(str(v) for v in enum) if isinstance(enum, list) else ""
    con.execute(
        "INSERT INTO parameters_fts(rowid, text) VALUES (?,?)",
        (cur.lastrowid, f"{param.get('name')} {param.get('description') or ''} {enum_text}"),
    )


def main() -> int:
    db_path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_DB
    counts = build(db_path)
    size_mb = db_path.stat().st_size / 1_000_000
    print(f"spec index → {db_path}  ({size_mb:.1f} MB)")
    for k, v in counts.items():
        print(f"  {k:12} {v}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
