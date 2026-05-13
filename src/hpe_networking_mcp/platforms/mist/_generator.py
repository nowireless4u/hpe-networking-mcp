"""Mist OpenAPI → tool function source generator.

Reads ``vendor/mist_openapi.json`` (the upstream Juniper Mist OpenAPI 3.1
spec) and emits one Python file per OpenAPI tag under
``platforms/mist/tools/``. Each emitted module is a list of decorated
async functions that proxy to ``mist_request`` in ``_client.py``.

The generator is invoked at release time via
``uv run python -m hpe_networking_mcp.platforms.mist.regenerate``. The
generated files are committed to the repo so PR diffs show what changed
when the upstream spec ships new endpoints.

Naming convention: ``mist_<snake_case_operationId>``. Per-operationId
uniqueness in the upstream spec (verified at sync time) makes tool
names globally unique.

Per the no-partial-implementations principle: generation is total. Every
operation in the spec produces a tool function (no per-endpoint skip
lists), and the registry on disk matches the vendored spec exactly.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Types
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ResolvedParam:
    """One fully-resolved OpenAPI parameter ready for code generation."""

    name: str
    in_: str  # "path", "query", "header", "cookie"
    required: bool
    py_type: str  # python type expression (e.g. ``int``, ``str``, ``list[str] | None``)
    default_repr: str | None  # python expression for the default (e.g. ``100``, ``None``); None means "no default"
    description: str


@dataclass(frozen=True)
class ResolvedOperation:
    """One fully-resolved OpenAPI operation ready for code generation."""

    operation_id: str
    tool_name: str
    method: str  # GET / POST / PUT / PATCH / DELETE
    path: str
    summary: str
    description: str
    tag: str  # primary tag, used as file slug
    path_params: list[ResolvedParam]
    query_params: list[ResolvedParam]
    has_body: bool
    body_required: bool
    body_description: str


# ---------------------------------------------------------------------------
# Reference resolution
# ---------------------------------------------------------------------------


def _resolve_ref(spec: dict, ref: str) -> dict:
    """Resolve a ``#/...`` JSON pointer reference into the spec."""
    if not ref.startswith("#/"):
        raise ValueError(f"Only local $ref supported, got: {ref}")
    parts = ref[2:].split("/")
    node: Any = spec
    for segment in parts:
        if not isinstance(node, dict):
            raise ValueError(f"$ref path {ref} traversed a non-dict at segment {segment!r}")
        node = node.get(segment, {})
    if not isinstance(node, dict):
        raise ValueError(f"$ref {ref} resolved to non-dict")
    return node


# ---------------------------------------------------------------------------
# Name conversion (camelCase / PascalCase → snake_case)
# ---------------------------------------------------------------------------

_CAMEL_RE_1 = re.compile(r"(.)([A-Z][a-z]+)")
_CAMEL_RE_2 = re.compile(r"([a-z0-9])([A-Z])")


def to_snake_case(name: str) -> str:
    """Convert ``camelCase`` / ``PascalCase`` to ``snake_case``.

    Handles the 8 PascalCase exceptions in the Mist spec (e.g.
    ``GetOrgLicenseAsyncClaimStatus`` → ``get_org_license_async_claim_status``).
    """
    result = _CAMEL_RE_1.sub(r"\1_\2", name)
    result = _CAMEL_RE_2.sub(r"\1_\2", result)
    return result.lower()


def tag_to_slug(tag: str) -> str:
    """Convert an OpenAPI tag (e.g. ``Orgs Sites``) to a filename slug."""
    slug = re.sub(r"[^a-zA-Z0-9]+", "_", tag).strip("_").lower()
    return slug or "uncategorized"


# ---------------------------------------------------------------------------
# OpenAPI schema → Python type expression
# ---------------------------------------------------------------------------


def schema_to_py_type(schema: dict, *, optional: bool = False) -> str:
    """Map an OpenAPI schema fragment to a Python type expression.

    Conservative: handles the common cases that appear in the Mist spec
    (string, integer, number, boolean, array of primitives, string enum)
    and falls back to ``Any`` for shapes we don't simplify. The fall-back
    is safe — Pydantic accepts ``Any`` and the AI dispatches on the
    parameter's description.
    """
    if not schema:
        suffix = " | None" if optional else ""
        return f"Any{suffix}"

    t = schema.get("type")
    enum = schema.get("enum")
    base: str

    if enum:
        # Strict enums become Literal[...] for autocomplete + validation.
        # Mist enum values are strings overwhelmingly; render as quoted
        # string literals. Numeric enums fall through to schema type below
        # if Literal would be malformed.
        if all(isinstance(v, str) for v in enum) or all(isinstance(v, (int, float, bool)) for v in enum):
            literals = ", ".join(repr(v) for v in enum)
            base = f"Literal[{literals}]"
        else:
            base = "Any"
    elif t == "string":
        # ``format: uuid`` could become ``UUID`` but Mist's spec is inconsistent
        # about marking UUIDs; keep ``str`` and let runtime handle.
        base = "str"
    elif t == "integer":
        base = "int"
    elif t == "number":
        base = "float"
    elif t == "boolean":
        base = "bool"
    elif t == "array":
        items = schema.get("items") or {}
        # Only one level — items-of-items collapses to Any for simplicity.
        item_type = schema_to_py_type(items, optional=False) if items else "Any"
        base = f"list[{item_type}]"
    elif t == "object":
        # Inline object schemas are common in request bodies; accept any dict.
        base = "dict[str, Any]"
    else:
        # No type / unknown → Any
        base = "Any"

    return f"{base} | None" if optional else base


def default_to_py_repr(default: Any) -> str:
    """Render an OpenAPI default value as a Python expression literal."""
    if isinstance(default, str):
        return repr(default)
    if isinstance(default, bool):
        return repr(default)
    if isinstance(default, (int, float)):
        return repr(default)
    if default is None:
        return "None"
    # Lists / dicts: emit JSON-style literal that Python also accepts
    return json.dumps(default)


# ---------------------------------------------------------------------------
# Parameter resolution
# ---------------------------------------------------------------------------


def resolve_parameter(spec: dict, raw_param: dict) -> ResolvedParam | None:
    """Resolve one OpenAPI parameter (raw dict OR ``$ref``) into our form."""
    if "$ref" in raw_param:
        try:
            raw_param = _resolve_ref(spec, raw_param["$ref"])
        except ValueError:
            return None

    name = raw_param.get("name")
    in_ = raw_param.get("in")
    if not name or in_ not in ("path", "query"):
        # Skip header / cookie params — generator doesn't surface those.
        return None

    schema = raw_param.get("schema") or {}
    required = bool(raw_param.get("required"))
    default = schema.get("default")
    has_default = "default" in schema and not required

    # Path params are always required (per OpenAPI); query params with no
    # explicit default get an Optional + None default for ergonomics.
    if in_ == "path":
        py_type = schema_to_py_type(schema, optional=False)
        default_repr = None
    elif has_default:
        py_type = schema_to_py_type(schema, optional=False)
        default_repr = default_to_py_repr(default)
    elif required:
        py_type = schema_to_py_type(schema, optional=False)
        default_repr = None
    else:
        py_type = schema_to_py_type(schema, optional=True)
        default_repr = "None"

    description = (raw_param.get("description") or "").strip()
    if not description:
        description = f"{in_} parameter {name!r}"

    return ResolvedParam(
        name=name,
        in_=in_,
        required=required or in_ == "path",
        py_type=py_type,
        default_repr=default_repr,
        description=description,
    )


# ---------------------------------------------------------------------------
# Operation resolution
# ---------------------------------------------------------------------------


def resolve_operation(
    spec: dict,
    path: str,
    method: str,
    op: dict,
    path_level_params: list[dict],
) -> ResolvedOperation | None:
    """Resolve one OpenAPI operation into the data the emitter consumes."""
    op_id = op.get("operationId")
    if not op_id:
        # Skip ops with no operationId — generator doesn't fabricate names.
        return None
    tool_name = "mist_" + to_snake_case(op_id)

    summary = (op.get("summary") or "").strip()
    description = (op.get("description") or "").strip()
    tags = op.get("tags") or ["Uncategorized"]
    tag = tags[0]

    # Merge path-level + method-level parameters, dedupe by (name, in).
    all_raw: list[dict] = list(path_level_params) + list(op.get("parameters") or [])
    seen: set[tuple[str, str]] = set()
    resolved: list[ResolvedParam] = []
    for raw in all_raw:
        rp = resolve_parameter(spec, raw)
        if rp is None:
            continue
        key = (rp.name, rp.in_)
        if key in seen:
            continue
        seen.add(key)
        resolved.append(rp)

    path_params = [p for p in resolved if p.in_ == "path"]
    query_params = [p for p in resolved if p.in_ == "query"]

    # Request-body shape: just whether the operation takes one and whether
    # it's required. The body is passed as ``dict[str, Any]`` — the AI
    # discovers the schema through the spec inspection in code mode.
    request_body = op.get("requestBody") or {}
    has_body = bool(request_body.get("content"))
    body_required = bool(request_body.get("required"))
    body_description = (request_body.get("description") or "").strip()

    return ResolvedOperation(
        operation_id=op_id,
        tool_name=tool_name,
        method=method.upper(),
        path=path,
        summary=summary,
        description=description,
        tag=tag,
        path_params=path_params,
        query_params=query_params,
        has_body=has_body,
        body_required=body_required,
        body_description=body_description,
    )


# ---------------------------------------------------------------------------
# Code emission
# ---------------------------------------------------------------------------

_FILE_HEADER_BASE = '''"""Generated Mist tools — DO NOT EDIT BY HAND.

This file was emitted by ``hpe_networking_mcp.platforms.mist._generator``
from ``vendor/mist_openapi.json``. Regenerate via:

    uv run python -m hpe_networking_mcp.platforms.mist.regenerate

Tag: ``{tag}``
Operations in this file: {n_ops}
"""

# ruff: noqa: E501

from __future__ import annotations

from typing import {typing_imports}

from fastmcp import Context
from mcp.types import ToolAnnotations
from pydantic import Field

from hpe_networking_mcp.platforms.mist._client import mist_request
from hpe_networking_mcp.platforms.mist._registry import tool as _mcp_tool


'''


def _py_string_literal(s: str, max_len: int = 240) -> str:
    """Render ``s`` as a Python string literal, safely escaping every char.

    Uses ``repr()`` rather than ``json.dumps`` because Python's repr
    follows ruff's preferred quote-style rules: single-quote by default,
    double-quote when the string contains single but not double quotes.
    Avoids the post-format pass that previously required a subprocess
    call to ``ruff format`` after generation.

    Handles real newlines / carriage returns / tabs / non-ASCII Unicode
    correctly via Python's standard escape sequences.
    """
    if len(s) > max_len:
        s = s[: max_len - 3] + "..."
    return repr(s)


def _format_param_annotation(p: ResolvedParam) -> str:
    """Render a single parameter as a Python function-signature line.

    Path params come first (required, no default). Required query params
    follow (required, no default). Optional query params come last
    (typed as ``T | None``, default ``None``).
    """
    py_type = p.py_type
    desc = _py_string_literal(p.description)
    annotated = f"Annotated[{py_type}, Field(description={desc})]"
    if p.default_repr is None:
        return f"    {p.name}: {annotated},"
    return f"    {p.name}: {annotated} = {p.default_repr},"


def _format_body_annotation(op: ResolvedOperation) -> str:
    """Render the ``body`` parameter for write methods."""
    desc = _py_string_literal(op.body_description or f"Request body for {op.method} {op.path}")
    if op.body_required:
        return f"    body: Annotated[dict[str, Any], Field(description={desc})],"
    return f"    body: Annotated[dict[str, Any] | None, Field(default=None, description={desc})] = None,"


def _format_description(op: ResolvedOperation) -> str:
    """Human-readable description for the tool decorator.

    Returns a Python string literal (quoted, fully escaped) suitable for
    direct interpolation into emitted source. Builds a structured form:

        <METHOD> <path>

        <summary>

        <description>
    """
    summary = op.summary or op.operation_id
    description = op.description.strip() if op.description else ""
    full = f"{op.method} {op.path}\n\n{summary}"
    if description and description.lower() != summary.lower():
        full += f"\n\n{description}"
    return _py_string_literal(full, max_len=600)


def emit_operation_function(op: ResolvedOperation) -> str:
    """Emit the Python source for one tool function."""
    description = _format_description(op)
    # Read-only vs write classification → tags + ToolAnnotations.
    if op.method in ("GET",):
        tags = '{"mist"}'
        readonly = True
        destructive = False
    elif op.method == "DELETE":
        tags = '{"mist", "mist_write", "mist_write_delete"}'
        readonly = False
        destructive = True
    else:  # POST / PUT / PATCH
        tags = '{"mist", "mist_write"}'
        readonly = False
        destructive = False

    lines: list[str] = []
    lines.append("@_mcp_tool(")
    lines.append(f"    name={_py_string_literal(op.tool_name, max_len=200)},")
    lines.append(f"    description={description},")
    lines.append(f"    tags={tags},")
    lines.append(f"    annotations=ToolAnnotations(readOnlyHint={readonly}, destructiveHint={destructive}),")
    lines.append(")")
    lines.append(f"async def {op.tool_name}(")
    lines.append("    ctx: Context,")

    # Order: path params (required), then required query, then optional query, then body
    for p in op.path_params:
        lines.append(_format_param_annotation(p))
    required_query = [p for p in op.query_params if p.default_repr is None]
    optional_query = [p for p in op.query_params if p.default_repr is not None]
    for p in required_query:
        lines.append(_format_param_annotation(p))
    for p in optional_query:
        lines.append(_format_param_annotation(p))
    if op.has_body:
        lines.append(_format_body_annotation(op))

    lines.append(") -> Any:")

    # Function body
    if op.path_params:
        path_kwargs = ", ".join(f'"{p.name}": {p.name}' for p in op.path_params)
        path_dict = f"path_params={{{path_kwargs}}}"
    else:
        path_dict = "path_params=None"

    if op.query_params:
        q_kwargs = ", ".join(f'"{p.name}": {p.name}' for p in op.query_params)
        query_dict = f"query_params={{{q_kwargs}}}"
    else:
        query_dict = "query_params=None"

    body_arg = "body=body," if op.has_body else "body=None,"

    lines.append("    return await mist_request(")
    lines.append("        ctx,")
    lines.append(f'        "{op.method}",')
    lines.append(f'        "{op.path}",')
    lines.append(f"        {path_dict},")
    lines.append(f"        {query_dict},")
    lines.append(f"        {body_arg}")
    lines.append("    )")
    return "\n".join(lines) + "\n"


def emit_module(tag: str, ops: list[ResolvedOperation]) -> str:
    """Emit the full source of one per-tag module."""
    # Stable order by tool name → minimizes spurious diffs across regenerations.
    sorted_ops = sorted(ops, key=lambda o: o.tool_name)
    body_parts = [emit_operation_function(op) for op in sorted_ops]
    body = "\n\n".join(body_parts)
    # Conditional imports — only include ``Literal`` when at least one tool's
    # generated source actually references it. Avoids ruff F401 noise on
    # modules whose operations have no enum-typed parameters.
    imports = ["Annotated", "Any"]
    if "Literal[" in body:
        imports.insert(2, "Literal")
    return _FILE_HEADER_BASE.format(tag=tag, n_ops=len(ops), typing_imports=", ".join(imports)) + body


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------


def load_spec(spec_path: Path) -> dict:
    """Load and minimally validate the vendored OpenAPI spec."""
    with spec_path.open(encoding="utf-8") as fh:
        spec: dict = json.load(fh)
    if "paths" not in spec or "info" not in spec:
        raise ValueError(f"{spec_path} doesn't look like an OpenAPI spec (missing paths/info)")
    return spec


def walk_operations(spec: dict) -> list[ResolvedOperation]:
    """Walk every (path, method) pair in the spec → resolved operations."""
    ops: list[ResolvedOperation] = []
    for path, methods in spec["paths"].items():
        if not isinstance(methods, dict):
            continue
        path_level_params = methods.get("parameters") or []
        for method, op_body in methods.items():
            if method not in ("get", "post", "put", "patch", "delete"):
                continue
            if not isinstance(op_body, dict):
                continue
            resolved = resolve_operation(
                spec=spec,
                path=path,
                method=method,
                op=op_body,
                path_level_params=path_level_params,
            )
            if resolved is not None:
                ops.append(resolved)
    return ops


def group_by_tag(ops: list[ResolvedOperation]) -> dict[str, list[ResolvedOperation]]:
    """Bucket operations by primary tag → emitter slug → file."""
    by_slug: dict[str, list[ResolvedOperation]] = {}
    for op in ops:
        slug = tag_to_slug(op.tag)
        by_slug.setdefault(slug, []).append(op)
    return by_slug


def generate_tool_files(
    spec_path: Path,
    output_dir: Path,
) -> dict[str, int]:
    """Read the spec, generate per-tag tool files, return summary stats.

    Returns a dict ``{slug: operation_count}`` for the caller to report.
    Doesn't delete pre-existing files in ``output_dir`` — that's the
    caller's responsibility (the regenerate CLI deletes + recreates).
    """
    spec = load_spec(spec_path)
    ops = walk_operations(spec)
    by_slug = group_by_tag(ops)

    output_dir.mkdir(parents=True, exist_ok=True)

    # Emit __init__.py that imports every generated module so the
    # @_mcp_tool decorators run at platform-init time.
    summary: dict[str, int] = {}
    for slug, slug_ops in sorted(by_slug.items()):
        target = output_dir / f"{slug}.py"
        target.write_text(emit_module(slug_ops[0].tag, slug_ops), encoding="utf-8")
        summary[slug] = len(slug_ops)

    # Emit the __init__.py barrel file
    init_lines: list[str] = [
        '"""Auto-generated Mist tools — see ``_generator.py``."""',
        "",
        "# ruff: noqa: F401",
        "",
    ]
    for slug in sorted(by_slug.keys()):
        init_lines.append(f"from . import {slug}  # noqa: F401")
    init_lines.append("")
    (output_dir / "__init__.py").write_text("\n".join(init_lines), encoding="utf-8")

    return summary
