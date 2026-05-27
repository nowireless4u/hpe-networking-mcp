# ruff: noqa: E501
"""Distill Central config-model payload schemas into a committed runtime artifact.

The OpenAPI specs under ``api-endpoints/central/config/`` are gitignored and
**never** shipped in the runtime image (the production Dockerfile only copies
``src/``). That leaves every ``central_manage_*`` / ``central_get_*`` config-model
tool exposing an opaque ``payload: dict`` whose only guidance is "consult the
OpenAPI schema" — which an AI client driving the tool cannot see at runtime. So
it guesses field names and enum values against the live tenant (see issue #384).

This script reads the same spec snapshot the one-shot importer
(``import_central_config_tools.py``) reads, resolves each object's request-body
schema (``allOf`` / ``$ref`` / ``oneOf``), distills it down to field names +
types + enum values + ``x-supportedDeviceType`` tags (descriptions dropped to
keep the artifact small), and writes a committed JSON file under ``src/``:

    src/hpe_networking_mcp/platforms/central/_config_payload_schemas.json

``central_get_tool_schema`` loads that artifact and attaches a ``payload_schema``
to its response for config-model tools (see ``central/config_schemas.py``).

Unlike the importer this is **safe to re-run** — it only writes the data artifact
and never touches the hand-curated tool modules.

Run from the repo root::

    uv run python scripts/distill_central_config_schemas.py
    uv run python scripts/distill_central_config_schemas.py --dry-run

This script lives outside ``src/`` so it never ships in the runtime image.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

# Reuse the importer's spec-parsing + naming so tool names match exactly.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from import_central_config_tools import (  # noqa: E402
    SKIP_FILENAMES,
    _name_param_in_path,
    _to_snake_case,
    parse_spec,
)

# ---------------------------------------------------------------------------
# Hand-curated tools (skip-list objects) whose tool names diverge from the
# importer's ``central_{get,manage}_<snake(title)>`` formula. Maps the spec
# filename stem to the get/manage tool names defined in the hand-written
# modules (security_policy.py et al.). Only objects whose payload an operator
# actually authors are worth indexing; entries can be added as needed.
# ---------------------------------------------------------------------------

HAND_CURATED_TOOL_NAMES: dict[str, list[str]] = {
    "net-group": ["central_get_net_groups", "central_manage_net_group"],
    "net-service": ["central_get_net_services", "central_manage_net_service"],
    "object-group": ["central_get_object_groups", "central_manage_object_group"],
    "policy": ["central_get_policies", "central_manage_policy"],
    "policy-group": ["central_get_policy_groups", "central_manage_policy_group"],
    "role-acl": ["central_get_role_acls", "central_manage_role_acl"],
    "role-gpid": ["central_get_role_gpids", "central_manage_role_gpid"],
    "role": ["central_get_roles", "central_manage_role"],
    "wlan": ["central_get_wlans", "central_manage_wlan_profile"],
    "config-assignment": ["central_get_config_assignments", "central_manage_config_assignment"],
    "gw-cluster": ["central_get_gateway_clusters", "central_manage_gateway_cluster"],
    "gw-cluster-intent": [
        "central_get_gateway_cluster_intent_profiles",
        "central_manage_gateway_cluster_intent_profile",
    ],
    # Read-only in this codebase (no central_manage_* tool) — map the GET tool
    # so the field set is still available as a reference.
    "named-vlan": ["central_get_named_vlans"],
    "alias": ["central_get_aliases"],
    "auth-server-group": ["central_get_server_groups"],
}

# Cap recursion so a self-referential or pathological schema can't blow the
# artifact size or hang. Config-model objects nest ~3-4 deep in practice.
_MAX_DEPTH = 8

# Cap enum length. A few fields carry catalog-sized enums (the DPI
# ``application`` list is ~4000 entries) that would dwarf the rest of the
# schema and are not hand-authored against a flat list anyway. Keep the first
# N and record the true count so the consumer knows the list is partial. All
# QoS/ACL-relevant enums (dscp=21, protocol=13, policy type, action type, …)
# fall well under this cap and survive intact.
_MAX_ENUM = 40


def _cap_enum(values: list[Any]) -> tuple[list[Any], int | None]:
    """Return (possibly-truncated enum, full-count-if-truncated)."""
    if len(values) > _MAX_ENUM:
        return values[:_MAX_ENUM], len(values)
    return values, None


def _resolve_ref(spec: dict[str, Any], ref: str) -> dict[str, Any]:
    """Resolve a local ``#/components/...`` JSON pointer within one spec."""
    parts = ref.lstrip("#/").split("/")
    node: Any = spec
    for part in parts:
        node = node.get(part, {})
    return node if isinstance(node, dict) else {}


def _find_request_schema(spec: dict[str, Any]) -> dict[str, Any] | None:
    """Locate the single-object request-body schema for a config-model spec.

    The item path (``/<segment>/{name}``) carries a ``post`` whose
    ``requestBody`` is a ``$ref`` into ``components/requestBodies``, which in
    turn references ``components/schemas``. Falls back to the collection path
    for singletons.
    """
    paths = spec.get("paths") or {}

    def _schema_for(op: dict[str, Any]) -> dict[str, Any] | None:
        rb = op.get("requestBody") or {}
        if "$ref" in rb:
            rb = _resolve_ref(spec, rb["$ref"])
        content = rb.get("content") or {}
        for media in content.values():
            sch = media.get("schema") or {}
            if "$ref" in sch:
                return _resolve_ref(spec, sch["$ref"])
            if sch:
                return sch
        return None

    # Prefer the item ({name}) path, then the collection path.
    ordered = sorted(paths.items(), key=lambda kv: _name_param_in_path(kv[0]) is None)
    for _path, methods in ordered:
        for verb in ("post", "patch", "put"):
            op = methods.get(verb)
            if isinstance(op, dict):
                schema = _schema_for(op)
                if schema:
                    return schema
    return None


def _distill(schema: dict[str, Any], spec: dict[str, Any], depth: int = 0) -> Any:
    """Recursively reduce an OpenAPI schema to {field: {type, enum, device_types, ...}}.

    Resolves ``$ref`` / ``allOf`` (merged) / ``oneOf`` (int|enum unions are
    common for protocol & DSCP fields). Drops descriptions, examples, and
    formatting metadata. Returns a compact dict describing the field set.
    """
    if depth > _MAX_DEPTH or not isinstance(schema, dict):
        return {}

    if "$ref" in schema:
        return _distill(_resolve_ref(spec, schema["$ref"]), spec, depth)

    # Merge allOf members into one property bag.
    if "allOf" in schema:
        merged: dict[str, Any] = {}
        for member in schema["allOf"]:
            part = _distill(member, spec, depth)
            if isinstance(part, dict):
                merged.update(part)
        # An allOf can also carry sibling ``properties``.
        if "properties" in schema:
            sibling = _distill({"properties": schema["properties"]}, spec, depth)
            if isinstance(sibling, dict):
                merged.update(sibling)
        return merged

    props = schema.get("properties")
    if isinstance(props, dict):
        out: dict[str, Any] = {}
        required = set(schema.get("required") or [])
        for fname, fdef in props.items():
            out[fname] = _distill_field(fname, fdef, spec, depth, fname in required)
        return out

    return {}


def _distill_field(
    fname: str, fdef: dict[str, Any], spec: dict[str, Any], depth: int, required: bool
) -> dict[str, Any]:
    """Distill one property definition into a compact descriptor."""
    if "$ref" in fdef:
        fdef = _resolve_ref(spec, fdef["$ref"])

    entry: dict[str, Any] = {}

    # oneOf unions (e.g. protocol/dscp accept int OR a named enum; subnet
    # fields accept an IPv4 OR IPv6 pattern). Collect the string-format hints
    # (``x-patternSources``) too — that's how "dotted-mask" (ipv4-subnet-mask)
    # is distinguished from "CIDR" (ipv4-prefix), which the bare type can't show.
    fmts: list[str] = []
    if "oneOf" in fdef:
        types: list[str] = []
        enum_vals: list[Any] = []
        for member in fdef["oneOf"]:
            m = _resolve_ref(spec, member["$ref"]) if "$ref" in member else member
            if m.get("type"):
                types.append(m["type"])
            if m.get("enum"):
                enum_vals = m["enum"]
            if m.get("x-patternSources"):
                fmts.append(m["x-patternSources"])
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

    # String-format hint: tells the AI the accepted literal form (e.g.
    # ``ipv4-subnet-mask`` = dotted quad + slash + dotted mask, NOT CIDR).
    if fdef.get("x-patternSources"):
        fmts.append(fdef["x-patternSources"])
    if fmts:
        entry["format"] = "|".join(dict.fromkeys(fmts))

    dts = fdef.get("x-supportedDeviceType")
    if dts:
        entry["device_types"] = dts
    if required or fdef.get("x-mandatory"):
        entry["mandatory"] = True

    # Nested object — recurse into properties (handles inline objects and allOf).
    if (fdef.get("properties") or fdef.get("allOf")) and ftype != "array":
        children = _distill(fdef, spec, depth + 1)
        if children:
            entry["type"] = entry.get("type") or "object"
            entry["properties"] = children

    # Array — distill the item schema.
    if ftype == "array":
        items = fdef.get("items") or {}
        item_children = _distill(items, spec, depth + 1)
        entry["type"] = "array"
        if item_children:
            entry["items"] = item_children

    return entry


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--specs-dir", type=Path, default=None)
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument("--dry-run", action="store_true", help="Report counts/size, write nothing.")
    args = parser.parse_args()

    here = Path(__file__).resolve()
    root = next(p for p in here.parents if (p / "pyproject.toml").exists())
    specs_dir = args.specs_dir or (root / "api-endpoints" / "central" / "config")
    output = args.output or (
        root / "src" / "hpe_networking_mcp" / "platforms" / "central" / "_config_payload_schemas.json"
    )

    if not specs_dir.exists():
        print(f"ERROR: specs dir not found: {specs_dir}", file=sys.stderr)
        return 1

    schemas: dict[str, Any] = {}
    tool_index: dict[str, str] = {}
    distilled = 0
    skipped_no_schema = 0

    for fp in sorted(specs_dir.glob("*.json")):
        spec = json.loads(fp.read_text(encoding="utf-8"))
        obj = parse_spec(fp)
        if obj is None:
            continue
        raw = _find_request_schema(spec)
        if not raw:
            skipped_no_schema += 1
            continue
        fields = _distill(raw, spec)
        if not fields:
            skipped_no_schema += 1
            continue

        stem = fp.stem
        schemas[stem] = {"fields": fields}
        distilled += 1

        # Map tool names → spec stem.
        if stem in SKIP_FILENAMES:
            mapped = HAND_CURATED_TOOL_NAMES.get(stem)
            if not mapped:
                # A hand-curated object has a real payload schema but no entry
                # in HAND_CURATED_TOOL_NAMES — its tool(s) won't surface the
                # schema. Make that visible at regeneration time rather than
                # letting it silently fall through (the gap closed in #386).
                print(
                    f"WARN: skip-list object {stem!r} has a payload schema but no "
                    f"HAND_CURATED_TOOL_NAMES entry — its tools will NOT surface a "
                    f"payload_schema. Add it to the map.",
                    file=sys.stderr,
                )
            for tool_name in mapped or []:
                tool_index[tool_name] = stem
        else:
            snake = _to_snake_case(obj.title)
            tool_index[f"central_get_{snake}"] = stem
            tool_index[f"central_manage_{snake}"] = stem

    artifact = {
        "_comment": (
            "Generated by scripts/distill_central_config_schemas.py from the "
            "api-endpoints/central/config/ OpenAPI snapshot. Do not edit by hand; "
            "re-run the distiller instead. See issue #384."
        ),
        "schemas": schemas,
        "tool_index": tool_index,
    }
    blob = json.dumps(artifact, indent=1, sort_keys=True)
    size_kb = len(blob.encode("utf-8")) / 1024

    print(f"Distilled {distilled} config objects ({skipped_no_schema} had no request schema).")
    print(f"Indexed {len(tool_index)} tool names → schema.")
    print(f"Artifact size: {size_kb:.1f} KiB")

    if args.dry_run:
        print("(--dry-run; nothing written)")
        return 0

    output.write_text(blob + "\n", encoding="utf-8")
    print(f"Wrote {output.relative_to(root)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
