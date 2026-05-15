# ruff: noqa: E501  (description templates are intentionally long inside f-strings)
"""One-shot importer for Aruba Central config-model tools.

Reads OpenAPI 3.x specs from ``api-endpoints/central/config/`` (the
local, gitignored snapshot the maintainer refreshes manually) and
emits hand-curated-style tool wrappers under
``src/hpe_networking_mcp/platforms/central/tools/``.

For each input spec, this emits two tools — ``central_get_<title>`` and
``central_manage_<title>`` — wrapping the shared
``_get_resource`` / ``_manage_resource`` helpers already used by the
hand-curated ``security_policy.py`` family.

This is **intentionally not a permanent generator.** The maintainer is
holding off on the broader spec-driven-generator decision. This script
exists so we can bulk-port the 197 net-new Central config-object types
into the codebase, then treat the emitted files as ordinary
hand-curated Python going forward (edit-by-hand, refine docstrings,
add per-type knobs as needed).

Output style mirrors ``src/.../central/tools/security_policy.py``:
  * Imports ``_get_resource`` / ``_manage_resource`` / ``_*_FIELD``
    from ``security_policy.py`` (precedent set by
    ``security_policy_ext.py``).
  * ``WRITE_DELETE`` ``ToolAnnotations`` defined per file.
  * ``@tool`` decorator from ``central._registry``.
  * One ``.py`` per ``x-tag-group``, snake-cased.

Skip list: 15 config-object types are already covered by hand-tuned
tools with rich docstrings, edge-case handling, and ``LOCAL`` filters.
We do not regenerate those — the existing files keep their value.

Run from the repo root::

    # Spike: AAA cluster only (9 Security types + mpsk-local)
    uv run python scripts/import_central_config_tools.py \\
        --include 'aaa-*,auth-*,mpsk-local'

    # Full import (all 197 net-new types)
    uv run python scripts/import_central_config_tools.py

    # Dry run (print summary, write nothing)
    uv run python scripts/import_central_config_tools.py --dry-run

This script lives outside ``src/`` so it never ships in the runtime
Docker image. The production Dockerfile only ``COPY src/``.
"""

from __future__ import annotations

import argparse
import fnmatch
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

# ---------------------------------------------------------------------------
# Skip list — types already covered by hand-curated tools
# ---------------------------------------------------------------------------

SKIP_FILENAMES: set[str] = {
    "alias",
    "auth-server-group",
    "config-assignment",
    "gw-cluster",
    "gw-cluster-intent",
    "named-vlan",
    "net-group",
    "net-service",
    "object-group",
    "policy",
    "policy-group",
    "role",
    "role-acl",
    "role-gpid",
    "wlan",
}


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ConfigObject:
    """One Central config-model object parsed from a single OpenAPI spec."""

    filename: str  # e.g. "aaa-profile" (without .json)
    title: str  # info.title, used for function names and resource labels
    tag_group: str  # info.x-tag-group, drives output filename
    path_segment: str  # first path segment, used as api_base in URL
    is_singleton: bool  # True when there is no /{name} item path (e.g. system-info)
    has_get_collection: bool
    has_get_item: bool
    has_create: bool
    has_update: bool
    has_delete: bool
    description: str  # short text for docstrings (best of available sources)
    name_param: str  # path parameter name on the item endpoint, usually "name"


@dataclass
class TagGroup:
    """Group of ConfigObjects sharing an x-tag-group."""

    name: str  # original tag group label
    slug: str  # filename slug, e.g. "routing_overlays"
    objects: list[ConfigObject] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _repo_root() -> Path:
    here = Path(__file__).resolve()
    for parent in (here.parent, *here.parents):
        if (parent / "pyproject.toml").exists():
            return parent
    raise RuntimeError("Could not locate repo root (no pyproject.toml found)")


def _to_snake_case(s: str) -> str:
    """Convert a hyphen/space-separated string to lower snake_case.

    ``"AAA Profile"`` → ``"aaa_profile"``
    ``"aaa-stateful-dot1x"`` → ``"aaa_stateful_dot1x"``
    ``"802dot11k-bcn-rpt-req"`` → ``"_802dot11k_bcn_rpt_req"`` (digit-leading
    identifiers get a leading underscore so they're valid Python names).
    """
    out = re.sub(r"[^a-zA-Z0-9]+", "_", s).strip("_").lower()
    if out and out[0].isdigit():
        out = "_" + out
    return out


# Parameter names reserved by the manage-tool signature template. Path
# params that snake_case to one of these would shadow the helper kwarg
# they share a name with; the emitter retargets them to a ``target_<name>``
# variant so the path param and the helper param coexist. Real-world
# offender today is ``persona-assignment/{device-function}``.
_RESERVED_PARAM_NAMES = {
    "ctx",
    "action_type",
    "payload",
    "scope_id",
    "device_function",
    "confirmed",
}


def _safe_param_name(raw: str) -> str:
    """Snake-case the OpenAPI path param and avoid collisions with reserved names."""
    base = _to_snake_case(raw)
    if base in _RESERVED_PARAM_NAMES:
        return f"target_{base}"
    return base


def _tag_group_slug(name: str) -> str:
    """Filename slug for an x-tag-group label.

    ``"Routing & Overlays"`` → ``"routing_overlays"``
    ``"VLANs & Networks"`` → ``"vlans_networks"``
    ``"Roles & Policy"`` → ``"roles_policy"``
    """
    cleaned = re.sub(r"[&/]", " ", name)
    return _to_snake_case(cleaned)


def _first_path_segment(path: str) -> str | None:
    """``/aaa-profile/{name}`` → ``"aaa-profile"``."""
    m = re.match(r"^/([^/{}]+)", path)
    return m.group(1) if m else None


def _name_param_in_path(path: str) -> str | None:
    """Extract the first ``{xxx}`` path parameter name, if any."""
    m = re.search(r"\{([^}]+)\}", path)
    return m.group(1) if m else None


def _best_description(spec: dict) -> str:
    """Pick the most informative description text for the object.

    Falls back through: GET-collection description → POST-item description
    → info.description → empty string. The YANG-derived OpenAPI specs
    have terse but usable descriptions on these fields; nothing fancy.
    """
    paths = spec.get("paths", {})
    for path, methods in paths.items():
        if _name_param_in_path(path) is None:
            get_op = methods.get("get", {})
            desc = (get_op.get("description") or "").strip()
            if desc:
                return _normalize_description(desc)
    for path, methods in paths.items():
        if _name_param_in_path(path) is not None:
            post_op = methods.get("post", {})
            desc = (post_op.get("description") or "").strip()
            if desc:
                return _normalize_description(desc)
    return _normalize_description((spec.get("info", {}).get("description") or "").strip())


def _normalize_description(text: str) -> str:
    """Collapse a YANG-derived description into a single, indent-safe paragraph.

    The Aruba Central OpenAPI specs often carry descriptions that originated
    as wrapped YANG comments — with hard line breaks inside what is logically
    one paragraph, plus occasional double-newline paragraph separators. We:

      * Strip per-line whitespace.
      * Join wrapped lines within a paragraph with a single space.
      * Preserve paragraph breaks (double-newline) as a single space too —
        the goal is one flat paragraph that survives any reflow ruff applies
        to docstrings.
      * Squeeze runs of whitespace.

    This keeps docstrings legible regardless of how they're indented at the
    insertion point in the generated wrapper.
    """
    if not text:
        return ""
    flat = " ".join(line.strip() for line in text.splitlines() if line.strip())
    return re.sub(r"\s+", " ", flat).strip()


# ---------------------------------------------------------------------------
# Spec parsing
# ---------------------------------------------------------------------------


def parse_spec(spec_path: Path) -> ConfigObject | None:
    """Parse one OpenAPI spec file into a ConfigObject.

    Returns ``None`` if the spec doesn't have the expected shape (single
    object with a ``/<segment>`` collection endpoint and a
    ``/<segment>/{name}`` item endpoint). The Central config-model specs
    are uniform enough that this is essentially "every spec under
    api-endpoints/central/config/ should match."
    """
    try:
        spec = json.loads(spec_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"WARN: {spec_path.name} — JSON parse failed: {exc}", file=sys.stderr)
        return None

    info = spec.get("info") or {}
    title = (info.get("title") or spec_path.stem).strip()
    tag_group = (info.get("x-tag-group") or "Uncategorized").strip()
    paths = spec.get("paths") or {}
    if not paths:
        print(f"WARN: {spec_path.name} — no paths in spec", file=sys.stderr)
        return None

    collection_path = None
    item_path = None
    for p in paths:
        if _name_param_in_path(p) is None and collection_path is None:
            collection_path = p
        elif _name_param_in_path(p) is not None and item_path is None:
            item_path = p

    # Three valid shapes:
    #   (a) collection + item — the common case (aaa-profile, etc.)
    #   (b) collection only — singleton config (system-info, firmware-compliance, etc.)
    #   (c) item only with {param} — parameterized singleton (persona-assignment/{device-function})
    if collection_path is None and item_path is None:
        print(
            f"WARN: {spec_path.name} — no usable paths (paths={list(paths.keys())}); skipping",
            file=sys.stderr,
        )
        return None

    is_singleton = item_path is None
    coll_methods: set[str] = set()
    item_methods: set[str] = set()
    if collection_path:
        coll_methods = {m.lower() for m in (paths.get(collection_path) or {}) if isinstance(m, str)}
    if item_path:
        item_methods = {m.lower() for m in (paths.get(item_path) or {}) if isinstance(m, str)}

    path_segment = _first_path_segment(collection_path or item_path or "") or ""
    name_param = _name_param_in_path(item_path) if item_path else "name"
    name_param = name_param or "name"

    # For singletons, CRUD lives on the collection path; for parameterized
    # singletons (no collection path), CRUD lives on the item path. Either
    # way, fold the per-shape method sets into one set for emission flags.
    all_methods = coll_methods | item_methods

    return ConfigObject(
        filename=spec_path.stem,
        title=title,
        tag_group=tag_group,
        path_segment=path_segment,
        is_singleton=is_singleton,
        has_get_collection="get" in coll_methods,
        has_get_item="get" in item_methods or ("get" in coll_methods and is_singleton),
        has_create="post" in all_methods,
        has_update="patch" in all_methods or "put" in all_methods,
        has_delete="delete" in all_methods,
        description=_best_description(spec),
        name_param=name_param,
    )


def load_objects(specs_dir: Path, include_filters: list[str] | None) -> list[ConfigObject]:
    """Walk the specs directory, parse each JSON, apply skip-list and filters."""
    if not specs_dir.exists():
        print(f"ERROR: specs directory not found: {specs_dir}", file=sys.stderr)
        sys.exit(1)

    files = sorted(specs_dir.glob("*.json"))
    if not files:
        print(f"ERROR: no .json specs under {specs_dir}", file=sys.stderr)
        sys.exit(1)

    objects: list[ConfigObject] = []
    skipped_covered = 0
    skipped_filter = 0
    for fp in files:
        stem = fp.stem
        if stem in SKIP_FILENAMES:
            skipped_covered += 1
            continue
        if include_filters and not any(fnmatch.fnmatch(stem, pat) for pat in include_filters):
            skipped_filter += 1
            continue
        obj = parse_spec(fp)
        if obj is not None:
            objects.append(obj)

    print(
        f"Loaded {len(objects)} objects "
        f"(skipped {skipped_covered} hand-curated, "
        f"{skipped_filter} filtered out, "
        f"{len(files)} total in {specs_dir.name}/)"
    )
    return objects


# ---------------------------------------------------------------------------
# Code emission
# ---------------------------------------------------------------------------


_FILE_HEADER = '''"""Aruba Central ``{tag_group}`` config-model tools.

Initial import emitted by ``scripts/import_central_config_tools.py``
from a snapshot of ``api-endpoints/central/config/``. The import is
**one-shot**: this file is hand-curated going forward — edit freely,
refine docstrings, add per-type schema knobs, split into smaller files
as needed. Re-running the script will overwrite this file, so only do
so before any hand edits or with care.

Covers config objects in the ``{tag_group}`` OpenAPI tag-group. Wrappers
delegate to ``_get_resource`` / ``_manage_resource`` in
``security_policy.py`` — the same shared helpers used by the
hand-curated Roles & Policy tools.
"""

# ruff: noqa: E501

from typing import Annotated

from fastmcp import Context
from mcp.types import ToolAnnotations
from pydantic import Field

from hpe_networking_mcp.platforms.central._registry import tool
from hpe_networking_mcp.platforms.central.tools import READ_ONLY
from hpe_networking_mcp.platforms.central.tools.security_policy import (
    _CONFIRMED_FIELD,
    _DEVICE_FUNCTION_FIELD,
    _SCOPE_ID_FIELD,
    _get_resource,
    _manage_resource,
)

WRITE_DELETE = ToolAnnotations(
    readOnlyHint=False,
    destructiveHint=True,
    idempotentHint=False,
    openWorldHint=True,
)
'''


def _emit_get_function(obj: ConfigObject) -> str:
    """Emit a ``central_get_<title>`` async function.

    For most config objects the wrapper takes an optional identifier
    (``name=None`` lists all, ``name=X`` returns one). For singleton
    configs (``is_singleton=True``) the wrapper takes no identifier and
    fetches the lone instance directly.
    """
    fn_name = f"central_get_{_to_snake_case(obj.title)}"
    desc = obj.description or f"{obj.title} configurations from Central."
    if not desc.endswith("."):
        desc = desc + "."

    if obj.is_singleton:
        return f'''
@tool(annotations=READ_ONLY)
async def {fn_name}(
    ctx: Context,
) -> dict | list | str:
    """Get the ``{obj.title}`` singleton configuration from Central.

    {desc}
    """
    return await _get_resource(ctx, "{obj.path_segment}", None)
'''

    # OpenAPI path params may be hyphenated (e.g. ``{mac-address}``) — those
    # aren't valid Python identifiers, so snake_case them for the function
    # signature. The docstring still names the original spelling so the
    # operator can map back to the OpenAPI spec.
    safe_param = _safe_param_name(obj.name_param)
    original_param = obj.name_param
    return f'''
@tool(annotations=READ_ONLY)
async def {fn_name}(
    ctx: Context,
    {safe_param}: str | None = None,
) -> dict | list | str:
    """Get ``{obj.title}`` configurations from Central.

    {desc}

    Parameters:
        {safe_param}: Specific ``{obj.title}`` identifier (OpenAPI path param: ``{original_param}``). If omitted, returns all.
    """
    return await _get_resource(ctx, "{obj.path_segment}", {safe_param})
'''


def _emit_manage_function(obj: ConfigObject) -> str:
    """Emit a ``central_manage_<title>`` async function.

    For singleton configs, no identifier parameter is required — the URL
    omits the trailing ``/{{name}}`` segment. ``_manage_resource``
    handles both shapes via its ``name`` parameter (None → singleton URL).
    """
    fn_name = f"central_manage_{_to_snake_case(obj.title)}"
    desc = obj.description or f"Manage {obj.title} configurations in Central."
    if not desc.endswith("."):
        desc = desc + "."

    if obj.is_singleton:
        return f'''
@tool(annotations=WRITE_DELETE, tags={{"central_write_delete"}})
async def {fn_name}(
    ctx: Context,
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the singleton ``{obj.title}`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_{_to_snake_case(obj.title)}`` to "
                "inspect the current state. For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete the singleton ``{obj.title}`` configuration in Central.

    {desc}
    """
    return await _manage_resource(
        ctx,
        "{obj.path_segment}",
        "{obj.title}",
        None,
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )
'''

    safe_param = _safe_param_name(obj.name_param)
    original_param = obj.name_param
    return f'''
@tool(annotations=WRITE_DELETE, tags={{"central_write_delete"}})
async def {fn_name}(
    ctx: Context,
    {safe_param}: Annotated[str, Field(description="``{obj.title}`` identifier (OpenAPI path param: ``{original_param}``).")],
    action_type: Annotated[str, Field(description="``'create'``, ``'update'``, or ``'delete'``.")],
    payload: Annotated[
        dict,
        Field(
            description=(
                "Payload for the ``{obj.title}`` object. "
                "Consult the Aruba Central config-model OpenAPI schema for the "
                "field set; use ``central_get_{_to_snake_case(obj.title)}`` to "
                "inspect an existing object for reference. "
                "For ``delete``, ``payload`` is ignored."
            )
        ),
    ],
    scope_id: Annotated[str | None, _SCOPE_ID_FIELD] = None,
    device_function: Annotated[str | None, _DEVICE_FUNCTION_FIELD] = None,
    confirmed: Annotated[bool, _CONFIRMED_FIELD] = False,
) -> dict | str:
    """Create, update, or delete a ``{obj.title}`` configuration in Central.

    {desc}
    """
    return await _manage_resource(
        ctx,
        "{obj.path_segment}",
        "{obj.title}",
        {safe_param},
        action_type,
        payload,
        scope_id,
        device_function,
        confirmed,
    )
'''


def emit_tag_group_module(group: TagGroup) -> str:
    """Render one .py file body for a TagGroup."""
    parts: list[str] = [_FILE_HEADER.format(tag_group=group.name)]
    for obj in sorted(group.objects, key=lambda o: o.title):
        parts.append(f"\n# ----- {obj.title} -----\n")
        if obj.has_get_collection or obj.has_get_item:
            parts.append(_emit_get_function(obj))
        if obj.has_create or obj.has_update or obj.has_delete:
            parts.append(_emit_manage_function(obj))
    return "".join(parts)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Import Aruba Central config-model OpenAPI specs as tool wrappers.",
    )
    parser.add_argument(
        "--specs-dir",
        type=Path,
        default=None,
        help="Override the default ``api-endpoints/central/config/`` source directory.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Override the default ``src/.../central/tools/`` output directory.",
    )
    parser.add_argument(
        "--include",
        type=str,
        default=None,
        help="Comma-separated fnmatch globs against the spec filename stem "
        "(without .json). Example: ``--include 'aaa-*,auth-*,mpsk-local'`` "
        "for the AAA spike.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the per-tag-group summary without writing any files.",
    )
    args = parser.parse_args()

    root = _repo_root()
    specs_dir = args.specs_dir or (root / "api-endpoints" / "central" / "config")
    output_dir = args.output_dir or (root / "src" / "hpe_networking_mcp" / "platforms" / "central" / "tools")

    include_filters = [s.strip() for s in args.include.split(",")] if args.include else None

    print(f"Specs dir:  {specs_dir}")
    print(f"Output dir: {output_dir}")
    if include_filters:
        print(f"Filters:    {include_filters}")
    print()

    objects = load_objects(specs_dir, include_filters)
    if not objects:
        print("No objects to emit. Exiting.")
        return 0

    groups: dict[str, TagGroup] = {}
    for obj in objects:
        slug = _tag_group_slug(obj.tag_group)
        if slug not in groups:
            groups[slug] = TagGroup(name=obj.tag_group, slug=slug)
        groups[slug].objects.append(obj)

    print(f"\nGrouped into {len(groups)} tag-group module(s):")
    for slug, group in sorted(groups.items()):
        print(f"  {slug}.py — {len(group.objects)} objects ({group.name})")

    if args.dry_run:
        print("\n(--dry-run; no files written)")
        return 0

    output_dir.mkdir(parents=True, exist_ok=True)
    written = 0
    for slug, group in sorted(groups.items()):
        target = output_dir / f"{slug}.py"
        source = emit_tag_group_module(group)
        target.write_text(source, encoding="utf-8")
        written += 1
        print(f"  wrote {target.relative_to(root)} ({len(group.objects)} objects)")

    print(f"\nDone. Wrote {written} module(s) under {output_dir.relative_to(root)}.")
    print("Run `uv run ruff format <output_dir>` to canonicalize whitespace, then review the diff.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
