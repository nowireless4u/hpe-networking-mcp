"""EdgeConnect Orchestrator OpenAPI → tool source generator.

Reads ``vendor/edgeconnect/EdgeConnect-9-7-REST-API.json`` (the Silver Peak /
Aruba EdgeConnect Orchestrator OpenAPI 3.0 spec) and emits one Python file per
OpenAPI tag under ``src/hpe_networking_mcp/platforms/edgeconnect/tools/``. Each
emitted module is a set of decorated async functions that proxy to
``client.edgeconnect_request``.

Run::

    uv run python scripts/generate_edgeconnect_tools.py            # emit files
    uv run python scripts/generate_edgeconnect_tools.py --dry-run  # manifest only

This script lives outside ``src/`` so it never ships in the runtime image. The
generated files **are** committed so PR diffs show what changed when the spec
ships new endpoints.

Naming convention: ``edgeconnect_<method>_<path-slug>``. Operation IDs are
unusable here (687/1216 are auto-numbered like ``IdleTime415`` and 12 collide),
so names derive from HTTP method + URL path. The 2 residual path-slug collisions
are de-duped with a numeric suffix.

Capability classification (conservative, method-based — see CHANGELOG):
``GET → READ``, ``POST/PUT → WRITE``, ``DELETE → WRITE_DELETE``. EdgeConnect uses
POST for read-style "query with a body" calls, so those sit behind the
write-gate too; that is the safe direction (nothing mutating is ever exposed
un-gated).

Per the no-partial-implementations principle: generation is total. Every
operation in the spec produces a tool (no skip lists).
"""

from __future__ import annotations

import argparse
import json
import keyword
import re
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SPEC_PATH = ROOT / "vendor" / "edgeconnect" / "EdgeConnect-9-7-REST-API.json"
OUT_DIR = ROOT / "src" / "hpe_networking_mcp" / "platforms" / "edgeconnect" / "tools"

METHODS = ("get", "post", "put", "delete")
CAPABILITY = {
    "get": "READ",
    "post": "WRITE",
    "put": "WRITE",
    "delete": "WRITE_DELETE",
}
_TYPE_MAP = {
    "string": "str",
    "integer": "int",
    "boolean": "bool",
    "number": "float",
    "array": "list[str]",
    "object": "dict[str, Any]",
}


@dataclass
class Param:
    """A resolved query/header parameter."""

    name: str  # original API name
    ident: str  # sanitized python identifier
    location: str  # "query" | "header"
    required: bool
    py_type: str
    desc: str


@dataclass
class Operation:
    """A fully-resolved operation ready for code generation."""

    tool_name: str
    func_name: str
    method: str  # upper
    path: str
    capability: str
    summary: str
    operation_id: str
    module: str
    params: list[Param] = field(default_factory=list)
    has_body: bool = False


def _py_type(schema: object) -> str:
    if not isinstance(schema, dict):
        return "str"
    t = schema.get("type")
    if isinstance(t, list):
        t = next((x for x in t if x != "null"), "string")
    return _TYPE_MAP.get(t, "str")  # type: ignore[arg-type]


def _slug(value: str) -> str:
    """Slugify a path or tag into a snake_case token."""
    s = re.sub(r"[^a-zA-Z0-9]+", "_", value.strip("/"))
    s = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s)  # split camelCase boundaries
    return re.sub(r"_+", "_", s).strip("_").lower()


def _sanitize_ident(name: str) -> str:
    ident = re.sub(r"[^a-zA-Z0-9_]", "_", name)
    ident = re.sub(r"_+", "_", ident).strip("_")
    if not ident:
        ident = "param"
    if ident[0].isdigit():
        ident = f"p_{ident}"
    if keyword.iskeyword(ident):
        ident = f"{ident}_"
    return ident


def _resolve_ref(ref: str, spec: dict) -> dict:
    node: object = spec
    for part in ref.lstrip("#/").split("/"):
        node = node[part]  # type: ignore[index]
    return node  # type: ignore[return-value]


def _resolve_params(op: dict, spec: dict) -> list[Param]:
    out: list[Param] = []
    used_idents: set[str] = set()
    for raw in op.get("parameters", []):
        pr = _resolve_ref(raw["$ref"], spec) if "$ref" in raw else raw
        loc = pr.get("in")
        if loc not in ("query", "header"):
            continue
        name = pr.get("name")
        if not name or name == "source":  # 'source' is injected by the client
            continue
        ident = _sanitize_ident(name)
        # de-dup identifiers within one operation
        base, n = ident, 2
        while ident in used_idents:
            ident = f"{base}_{n}"
            n += 1
        used_idents.add(ident)
        desc = (pr.get("description") or f"{loc} parameter '{name}'").replace("\n", " ").strip()
        out.append(
            Param(
                name=name,
                ident=ident,
                location=loc,
                required=bool(pr.get("required")),
                py_type=_py_type(pr.get("schema", {})),
                desc=desc,
            )
        )
    return out


def collect_operations(spec: dict) -> list[Operation]:
    """Walk the spec and build the de-collided, classified operation list."""
    paths = spec.get("paths", {})
    seen_names: set[str] = set()
    ops: list[Operation] = []
    for path in sorted(paths):
        path_ops = paths[path]
        for method in METHODS:
            op = path_ops.get(method)
            if not isinstance(op, dict):
                continue
            base_name = f"edgeconnect_{method}_{_slug(path)}"
            name = base_name
            n = 2
            while name in seen_names:  # de-collide the 2 residual slug clashes
                name = f"{base_name}_{n}"
                n += 1
            seen_names.add(name)

            tags = op.get("tags") or ["untagged"]
            module = _slug(tags[0]) or "untagged"
            if module[0].isdigit():
                module = f"t_{module}"
            summary = (op.get("summary") or op.get("description") or "").replace("\n", " ").strip()
            ops.append(
                Operation(
                    tool_name=name,
                    func_name=name,
                    method=method.upper(),
                    path=path,
                    capability=CAPABILITY[method],
                    summary=summary,
                    operation_id=op.get("operationId", ""),
                    module=module,
                    params=_resolve_params(op, spec),
                    has_body=bool(op.get("requestBody")),
                )
            )
    return ops


# N803: generated argument names intentionally mirror the EdgeConnect API's
# native (often camelCase) parameter names, so an operator sees the same names
# as the Orchestrator REST docs. E501: generated descriptions can be long.
_MODULE_HEADER = '''"""Generated EdgeConnect tools — DO NOT EDIT BY HAND.

Emitted by ``scripts/generate_edgeconnect_tools.py`` from
``vendor/edgeconnect/EdgeConnect-9-7-REST-API.json``. Regenerate via:

    uv run python scripts/generate_edgeconnect_tools.py

Tag: ``{tag}``
Operations in this file: {count}
"""
{noqa}
from __future__ import annotations

from typing import {typing_names}

from fastmcp import Context
{field_import}from hpe_networking_mcp.platforms._common.annotations import Capability
from hpe_networking_mcp.platforms.edgeconnect._registry import tool
from hpe_networking_mcp.platforms.edgeconnect.client import edgeconnect_request
'''


def _render_op(op: Operation) -> str:
    description = f"{op.method} {op.path}"
    if op.operation_id:
        description += f"\n\n{op.operation_id}"
    if op.summary:
        description += f"\n\n{op.summary}"

    # Order args: required params, then optional params, then body (optional).
    required = [p for p in op.params if p.required]
    optional = [p for p in op.params if not p.required]

    lines = [
        "@tool(",
        f"    name={op.tool_name!r},",
        f"    description={description!r},",
        f"    capability=Capability.{op.capability},",
        ")",
        f"async def {op.func_name}(",
        "    ctx: Context,",
    ]
    for p in required:
        lines.append(f"    {p.ident}: Annotated[{p.py_type}, Field(description={p.desc!r})],")
    for p in optional:
        lines.append(
            f"    {p.ident}: Annotated[{p.py_type} | None, Field(default=None, description={p.desc!r})] = None,"
        )
    if op.has_body:
        lines.append(
            '    body: Annotated[dict[str, Any] | None, Field(default=None, description="Request body")] = None,'
        )
    lines.append(") -> Any:")

    qparams = [p for p in op.params if p.location == "query"]
    hparams = [p for p in op.params if p.location == "header"]
    body_lines: list[str] = []
    if qparams:
        body_lines.append("    query_params: dict[str, Any] = {}")
        for p in qparams:
            body_lines.append(f"    if {p.ident} is not None:")
            body_lines.append(f"        query_params[{p.name!r}] = {p.ident}")
    if hparams:
        body_lines.append("    header_params: dict[str, Any] = {}")
        for p in hparams:
            body_lines.append(f"    if {p.ident} is not None:")
            body_lines.append(f"        header_params[{p.name!r}] = {p.ident}")

    call = ["    return await edgeconnect_request(", "        ctx,", f"        {op.method!r},", f"        {op.path!r},"]
    call.append("        query_params=query_params or None," if qparams else "        query_params=None,")
    if hparams:
        call.append("        header_params=header_params or None,")
    if op.has_body:
        call.append("        body=body,")
    call.append("    )")

    return "\n".join(lines) + "\n" + ("\n".join(body_lines) + "\n" if body_lines else "") + "\n".join(call)


def render_module(tag_slug: str, ops: list[Operation], tag_display: str) -> str:
    bodies = [_render_op(op) for op in sorted(ops, key=lambda o: o.tool_name)]
    needs_field = any(op.params or op.has_body for op in ops)
    # Emit only the noqa codes actually triggered, else ruff's RUF100 flags the
    # directive itself as unused (small param-less modules have neither).
    needs_n803 = any(c.isupper() for op in ops for p in op.params for c in p.ident)
    needs_e501 = any(len(line) > 120 for body in bodies for line in body.splitlines())
    codes = [c for c, on in (("E501", needs_e501), ("N803", needs_n803)) if on]
    header = _MODULE_HEADER.format(
        tag=tag_display,
        count=len(ops),
        noqa=f"# ruff: noqa: {', '.join(codes)}" if codes else "",
        typing_names="Annotated, Any" if needs_field else "Any",
        field_import="from pydantic import Field\n\n" if needs_field else "\n",
    )
    return header + "\n\n" + "\n\n\n".join(bodies) + "\n"


def _module_display_names(spec: dict) -> dict[str, str]:
    """Map module slug -> a representative original tag name (for the docstring)."""
    out: dict[str, str] = {}
    for path_ops in spec.get("paths", {}).values():
        for method in METHODS:
            op = path_ops.get(method)
            if isinstance(op, dict):
                tags = op.get("tags") or ["untagged"]
                slug = _slug(tags[0]) or "untagged"
                out.setdefault(slug, tags[0])
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="Print the manifest; write nothing.")
    args = parser.parse_args()

    spec = json.loads(SPEC_PATH.read_text())
    ops = collect_operations(spec)
    by_module: dict[str, list[Operation]] = defaultdict(list)
    for op in ops:
        by_module[op.module].append(op)
    displays = _module_display_names(spec)

    cap_counts = Counter(op.capability for op in ops)
    collisions = [op.tool_name for op in ops if re.search(r"_\d+$", op.tool_name)]

    print(f"EdgeConnect generator manifest ({SPEC_PATH.name})")
    print(f"  operations : {len(ops)}")
    print(f"  modules    : {len(by_module)}")
    print(f"  capability : {dict(cap_counts)}")
    print(f"  de-collided: {len(collisions)} -> {collisions}")
    print("  sample tools:")
    for op in ops[:12]:
        nparams = len(op.params)
        print(f"    {op.tool_name}  [{op.capability}]  ({nparams} params{', +body' if op.has_body else ''})")
    print("  largest modules:")
    for mod, mod_ops in sorted(by_module.items(), key=lambda kv: -len(kv[1]))[:8]:
        print(f"    {mod}.py: {len(mod_ops)} tools")

    if args.dry_run:
        print("\n[dry-run] no files written.")
        return 0

    # Clear previously generated modules (keep __init__.py), then emit fresh.
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for existing in OUT_DIR.glob("*.py"):
        if existing.name != "__init__.py":
            existing.unlink()
    for module, mod_ops in sorted(by_module.items()):
        source = render_module(module, mod_ops, displays.get(module, module))
        (OUT_DIR / f"{module}.py").write_text(source)

    print(f"\nWrote {len(by_module)} module(s) / {len(ops)} tools to {OUT_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
