# ruff: noqa: E501  (description templates are intentionally long inside f-strings)
"""One-shot importer for Aruba Central config-model tools.

Reads OpenAPI 3.x specs from ``vendor/central/config/`` (the committed
snapshot auto-synced from upstream Aruba Central by a GitHub Action) and
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
# Skip list — vendor domain-file STEMS to skip wholesale (rare; usually empty).
#
# Historically this was keyed to the old one-object-per-file ``api-endpoints/``
# layout (singular object stems like ``aaa-profile``). The vendor specs are now
# domain-grouped (``roles-policy.json`` holds /roles, /policies, /policy-groups,
# …), so a per-file stem skip is too coarse.
#
# Keep this empty unless an entire vendor domain file must be excluded.
SKIP_FILENAMES: set[str] = set()


# ---------------------------------------------------------------------------
# Hand-curated segment skip set — resource SEGMENTS whose tool surface is
# genuinely custom and must stay hand-written, never generated.
#
# This is the SOLE keep-set. The regen OWNS the entire Central config tool
# surface and REPLACES the hand-curated CRUD tools (which are deleted in
# Phase 2). The generator emits full OAS-renamed CRUD for every resource
# segment EXCEPT the ones listed here. There is intentionally no auto-derived
# "skip anything whose name collides with an existing hand-curated function"
# mechanism — that produced inconsistent singular/plural emit splits and
# conflicts with "regen owns everything."
#
# ``config-assignments`` is the canonical (and currently only) case: the
# collection ``POST /config-assignments`` (body create) and the deep-path
# ``DELETE /config-assignments/{scope-id}/{device-function}/{profile-type}/
# {profile-instance}`` (4 path params, no body) have fundamentally different
# shapes that a single generic ``manage(action_type, payload)`` wrapper can't
# express. The hand-curated ``config_assignments.py`` splits them. The
# generator skips emitting ANY CRUD object OR operation whose first segment is
# in this set, and flags those inventory rows ``hand_curated_skip=True``.
HAND_CURATED_SEGMENTS: set[str] = {
    "config-assignments",
    # scope-hierarchy + scope-write feature (sites.py / scope.py / configuration.py)
    "sites",
    "device-groups",
    "site-collections",
    "hierarchy",
    "global",
    "site-add-devices",
    "site-collection-add-sites",
    "site-collection-remove-sites",
    "device-groups-add-devices",
    "device-groups-remove-devices",
    "device-groups-create-and-add-devices",
    # cross-platform WLAN (wlan_profiles.py)
    "wlan-ssids",
    # custom health reads (config_health.py)
    "config-health",
}


# Resource segments that, when the SAME segment (or operation path tail)
# appears under multiple version prefixes (e.g. both ``v1`` and ``v1alpha1``),
# should resolve to the ``v1`` variant only. The vendor scope-management spec
# carries duplicate ``v1`` / ``v1alpha1`` paths for these; the hand-curated
# scope tools (sites.py, scope.py, …) all call ``network-config/v1/…`` for
# them, so ``v1`` wins and the ``v1alpha1`` duplicate is dropped. Segments that
# appear under only one version keep that version untouched (so the rest of the
# config API stays ``v1alpha1`` and ``global`` stays ``v1``).
#
# We do NOT hardcode the segment list — version dedupe is applied generically
# whenever a generated tool-name would arise from two different version
# prefixes (see ``_dedupe_crud_groups_by_version`` /
# ``_dedupe_operation_paths_by_version`` below). This comment documents intent.


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ConfigObject:
    """One Central config-model CRUD object parsed from an OpenAPI spec.

    The vendor specs are domain-grouped — a single file (e.g. ``roles-policy``)
    yields many ConfigObjects, one per resource segment that has a
    ``/<prefix>/<segment>`` collection and/or ``/<prefix>/<segment>/{name}``
    item path.
    """

    filename: str  # vendor domain-file stem, e.g. "roles-policy"
    title: str  # OAS path segment (the source of the tool name), e.g. "role-acls"
    tag_group: str  # info.x-tag-group (falls back to file stem), drives output module
    path_prefix: str  # version prefix, e.g. "network-config/v1alpha1"
    path_segment: str  # resource segment, used as api_base in the URL (after the prefix)
    is_singleton: bool  # True when there is no /{name} item path (e.g. system-info)
    has_get_collection: bool
    has_get_item: bool
    has_create: bool
    has_update: bool
    has_delete: bool
    description: str  # short text for docstrings (best of available sources)
    name_param: str  # path parameter name on the item endpoint, usually "name"


@dataclass(frozen=True)
class OperationObject:
    """One irregular / operation endpoint — a single (path, method) tool.

    Covers paths that are not a plain CRUD collection/item shape: fixed
    sub-verbs (``bulk``/``revoke``/``upload``/``import``/``export``/``status``),
    intermediate literal segments, deep nested items
    (``policy-groups/policy-group/policy-group-list/{name}``), and
    multi-param paths (``config-assignments/{a}/{b}/{c}/{d}``).
    """

    filename: str  # vendor domain-file stem
    tag_group: str  # drives output module
    path_prefix: str  # version prefix, e.g. "network-config/v1"
    path_tail: str  # everything after the prefix, e.g. "sites/bulk"
    methods: tuple[str, ...]  # one or more HTTP verbs collapsed into this tool
    tool_name: str  # derived tool name (central_<verb>_<snake tail>)
    is_read: bool  # GET-only → read tool
    has_body: bool  # request body present (drives the ``payload`` param)
    path_params: tuple[str, ...]  # ordered raw path-param names ({...})
    description: str


@dataclass
class SourceModule:
    """Group of ConfigObjects + OperationObjects sharing a vendor source file.

    The vendor specs have no ``x-tag-group``, so emitted tools are grouped by
    their source spec filename stem (snake-cased) and one ``.py`` module is
    written per source file. ``roles-policy.json`` → ``roles_policy.py``.
    """

    name: str  # original source-file stem, e.g. "roles-policy"
    slug: str  # snake-cased module stem, e.g. "roles_policy"
    objects: list[ConfigObject] = field(default_factory=list)
    operations: list[OperationObject] = field(default_factory=list)


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


# Version-prefix matcher: ``/network-config/v1alpha1/...`` or ``/network-config/v1/...``.
_PREFIX_RE = re.compile(r"^/((?:[^/]+/)*v[0-9][0-9a-z]*)/(.*)$")

# HTTP verbs we care about (in OpenAPI path-item objects).
_HTTP_METHODS = ("get", "post", "patch", "put", "delete")


def _split_prefix(path: str) -> tuple[str, str]:
    """Split an OAS path into (version_prefix, tail).

    ``/network-config/v1alpha1/role-acls/{name}`` →
    ``("network-config/v1alpha1", "role-acls/{name}")``.

    Falls back to ("", path-without-leading-slash) when no version prefix is
    recognized (no current vendor path hits that branch, but be defensive).
    """
    m = _PREFIX_RE.match(path)
    if m:
        return m.group(1), m.group(2)
    return "", path.lstrip("/")


def _version_rank(prefix: str) -> int:
    """Rank a version prefix so the preferred variant sorts FIRST (lowest).

    When the same resource segment (or operation tail) appears under multiple
    version prefixes, the stable ``vN`` form wins over a ``vNalphaM`` /
    ``vNbetaM`` pre-release form. A bare ``v1`` outranks ``v1alpha1``. Among
    bare versions, higher numbers win (``v2`` over ``v1``). The returned int is
    a sort key (smaller = preferred).

    ``"network-config/v1"``        → preferred over
    ``"network-config/v1alpha1"``  → over ``"network-config/v1beta1"``.
    """
    m = re.search(r"/?v([0-9]+)([a-z][0-9a-z]*)?$", prefix)
    if not m:
        return 10_000  # unrecognized prefix — sorts last
    major = int(m.group(1))
    is_prerelease = 1 if m.group(2) else 0  # stable (0) sorts before pre-release (1)
    # Prefer stable first, then higher major. Negate major so larger sorts lower.
    return is_prerelease * 1000 - major


def _first_path_segment(path: str) -> str | None:
    """``/network-config/v1alpha1/role-acls/{name}`` → ``"role-acls"``.

    Returns the first resource segment *after* the version prefix.
    """
    _prefix, tail = _split_prefix(path)
    m = re.match(r"^([^/{}]+)", tail)
    return m.group(1) if m else None


def _name_param_in_path(path: str) -> str | None:
    """Extract the first ``{xxx}`` path parameter name, if any."""
    m = re.search(r"\{([^}]+)\}", path)
    return m.group(1) if m else None


def _path_params(tail: str) -> tuple[str, ...]:
    """All ``{xxx}`` param names in a path tail, in order."""
    return tuple(re.findall(r"\{([^}]+)\}", tail))


def _is_crud_shape(tail: str) -> bool:
    """True when ``tail`` is a plain CRUD collection or item path.

    Collection: ``<segment>`` (one literal segment, no params).
    Item:       ``<segment>/{name}`` (one literal segment + one trailing param).
    Everything else (``sites/bulk``, ``cnac-image/upload``,
    ``policy-groups/.../policy-group-list/{name}``, multi-param paths) is an
    operation.
    """
    segs = tail.split("/")
    if len(segs) == 1:
        return "{" not in segs[0]
    if len(segs) == 2:
        return "{" not in segs[0] and bool(re.fullmatch(r"\{[^}]+\}", segs[1]))
    return False


# Trailing literal verb segments that mark a STANDALONE WRITE ACTION — the verb
# is already in the path, so the tool name is ``central_<segments_in_order>``
# (no extra get/manage/verb prefix). ``bulk`` is special: every vendor */bulk is
# a DELETE, so it renders as ``..._bulk_delete``.
_STANDALONE_WRITE_VERBS = {"revoke", "upload", "import", "export", "bulk"}

# Literal segments that are VERBS rather than resource nouns. When such a token
# sits immediately before a trailing ``{param}`` (e.g. ``download/{image-id}``)
# the path is NOT a nested CRUD item — the leaf is an action, not an identity —
# so it must NOT be named off the leaf alone. We keep all literal segments in
# resource-path-order instead (``cnac-image/download/{image-id}`` →
# ``central_get_cnac_image_download``).
_VERB_SEGMENTS = _STANDALONE_WRITE_VERBS | {"download"}


def _operation_tool_name(tail: str, method: str) -> str:
    """Derive an operation tool name in resource-path-order.

    Take the path tail (everything after the version prefix), keep the literal
    segments **in order**, DROP ``{param}`` segments, snake_case the whole join,
    then prefix by kind:

      * **GET** → ``central_get_<segments_in_order>``.
      * **Nested CRUD item** (trailing ``/{name}`` with write verbs) →
        ``central_get_<leaf>`` / ``central_manage_<leaf>`` (named off the leaf
        resource noun, matching the hand-curated precedent).
      * **Standalone write action** (trailing literal verb segment:
        revoke/upload/import/export/bulk) → ``central_<segments_in_order>``
        (the verb is already in the path). ``bulk`` DELETE →
        ``central_<segs>_bulk_delete``.

    Examples:
      * ``sites/bulk`` (DELETE)            → ``central_sites_bulk_delete``
      * ``cnac-certificate/revoke`` (POST) → ``central_cnac_certificate_revoke``
      * ``cnac-job/{job-id}/status`` (GET) → ``central_get_cnac_job_status``
      * ``cnac-image/upload`` (POST)       → ``central_cnac_image_upload``
      * ``cnac-image/download/{id}`` (GET) → ``central_get_cnac_image_download``
      * ``cnac-mac-reg/import`` (POST)     → ``central_cnac_mac_reg_import``
      * ``policy-groups/policy-group/policy-group-list/{name}`` (write)
                                           → ``central_manage_policy_group_list``
                                             (GET → ``central_get_policy_group_list``)
    """
    tokens = [t for t in tail.split("/") if not (t.startswith("{") and t.endswith("}"))]
    last_is_param = tail.rstrip("/").endswith("}")
    leaf = tokens[-1] if tokens else ""
    segments_in_order = _to_snake_case("_".join(tokens))

    # Nested CRUD item (e.g. .../policy-group-list/{name}) — the leaf is a noun
    # resource → clean get/manage on that leaf (matches hand-curated naming).
    # A verb leaf before a trailing param (e.g. ``download/{image-id}``) is an
    # action, not a CRUD item, so it falls through to the path-order rules.
    if last_is_param and leaf and leaf not in _VERB_SEGMENTS:
        verb = "get" if method == "get" else "manage"
        return f"central_{verb}_{_to_snake_case(leaf)}"

    # GET reads → ``central_get_<segments_in_order>`` regardless of leaf token.
    if method == "get":
        return f"central_get_{segments_in_order}"

    # Standalone write action with a trailing literal verb in the path. ``bulk``
    # is a DELETE → render ``..._bulk_delete``; other verbs are already the leaf.
    if leaf in _STANDALONE_WRITE_VERBS:
        if leaf == "bulk":
            return f"central_{segments_in_order}_delete"
        return f"central_{segments_in_order}"

    # No recognized trailing verb; fall back to a method-driven verb prefix in
    # resource-path-order.
    if method == "delete":
        return f"central_delete_{segments_in_order}"
    if method in ("patch", "put"):
        return f"central_update_{segments_in_order}"
    return f"central_manage_{segments_in_order}"


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


def _methods_for(paths: dict, path: str) -> set[str]:
    """Lower-case HTTP verbs declared on an OpenAPI path-item."""
    item = paths.get(path) or {}
    return {m.lower() for m in item if isinstance(m, str) and m.lower() in _HTTP_METHODS}


def _op_has_body(paths: dict, path: str, method: str) -> bool:
    """True when the (path, method) operation declares a requestBody."""
    op = (paths.get(path) or {}).get(method) or {}
    return isinstance(op, dict) and bool(op.get("requestBody"))


def _dedupe_crud_groups_by_version(
    crud_groups: dict[tuple[str, str], dict[str, str | None]],
) -> dict[tuple[str, str], dict[str, str | None]]:
    """Keep one version-variant per CRUD segment (the best-ranked prefix).

    Keyed on the resource segment alone: when ``(v1, sites)`` and
    ``(v1alpha1, sites)`` both exist they would generate the same tool name, so
    only the higher-ranked prefix (stable ``v1`` over ``v1alpha1``) survives.
    Segments present under a single version are returned unchanged.
    """
    best_prefix: dict[str, str] = {}
    for prefix, seg in crud_groups:
        cur = best_prefix.get(seg)
        if cur is None or _version_rank(prefix) < _version_rank(cur):
            best_prefix[seg] = prefix
    return {(prefix, seg): slot for (prefix, seg), slot in crud_groups.items() if best_prefix[seg] == prefix}


def _dedupe_operation_paths_by_version(operation_paths: list[tuple[str, str]]) -> list[tuple[str, str]]:
    """Keep one version-variant per operation tail (the best-ranked prefix).

    Keyed on the operation path tail (everything after the version prefix):
    when ``(v1, sites/bulk)`` and ``(v1alpha1, sites/bulk)`` both exist they
    generate the same tool name, so only the higher-ranked prefix survives.
    Order is preserved for the surviving entries.
    """
    best_prefix: dict[str, str] = {}
    for prefix, tail in operation_paths:
        cur = best_prefix.get(tail)
        if cur is None or _version_rank(prefix) < _version_rank(cur):
            best_prefix[tail] = prefix
    return [(prefix, tail) for prefix, tail in operation_paths if best_prefix[tail] == prefix]


def parse_spec_objects(spec_path: Path) -> tuple[list[ConfigObject], list[OperationObject]]:
    """Parse one (domain-grouped) OpenAPI spec into CRUD + operation objects.

    Groups ``paths`` by ``(version_prefix, first_segment)``. A segment that has
    a collection (``/<seg>``) and/or an item (``/<seg>/{name}``) path becomes a
    CRUD :class:`ConfigObject`. Every path that is *not* a plain CRUD shape
    becomes one :class:`OperationObject` per (path, method).
    """
    try:
        spec = json.loads(spec_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"WARN: {spec_path.name} — JSON parse failed: {exc}", file=sys.stderr)
        return [], []

    info = spec.get("info") or {}
    tag_group = (info.get("x-tag-group") or info.get("title") or spec_path.stem).strip()
    paths = spec.get("paths") or {}
    if not paths:
        print(f"WARN: {spec_path.name} — no paths in spec", file=sys.stderr)
        return [], []

    # crud_groups[(prefix, segment)] = {"coll": path|None, "item": path|None}
    crud_groups: dict[tuple[str, str], dict[str, str | None]] = {}
    operation_paths: list[tuple[str, str]] = []  # (prefix, tail)

    for p in paths:
        prefix, tail = _split_prefix(p)
        if _is_crud_shape(tail):
            segs = tail.split("/")
            seg = segs[0]
            key = (prefix, seg)
            slot = crud_groups.setdefault(key, {"coll": None, "item": None})
            if len(segs) == 1:
                slot["coll"] = p
            else:
                slot["item"] = p
        else:
            operation_paths.append((prefix, tail))

    # Fix 1: version dedupe for CRUD groups. The same resource segment may
    # appear under multiple version prefixes (e.g. /network-config/v1/sites and
    # /network-config/v1alpha1/sites). Both would generate the same tool name —
    # a self-collision. Keep only the best-ranked version (stable v1 over
    # v1alpha1); segments present under one version only are untouched.
    crud_groups = _dedupe_crud_groups_by_version(crud_groups)

    objects: list[ConfigObject] = []
    for (prefix, seg), slot in crud_groups.items():
        coll = slot["coll"]
        item = slot["item"]
        coll_methods = _methods_for(paths, coll) if coll else set()
        item_methods = _methods_for(paths, item) if item else set()
        all_methods = coll_methods | item_methods
        is_singleton = item is None
        name_param = (_name_param_in_path(item) if item else None) or "name"
        objects.append(
            ConfigObject(
                filename=spec_path.stem,
                title=seg,  # tool name derives from the OAS segment (decision #1)
                tag_group=tag_group,
                path_prefix=prefix,
                path_segment=seg,
                is_singleton=is_singleton,
                has_get_collection="get" in coll_methods,
                has_get_item="get" in item_methods or ("get" in coll_methods and is_singleton),
                has_create="post" in all_methods,
                has_update="patch" in all_methods or "put" in all_methods,
                has_delete="delete" in all_methods,
                description=_best_description(spec),
                name_param=name_param,
            )
        )

    # Fix 1 (operations): dedupe the same operation tail appearing under
    # multiple version prefixes (e.g. sites/bulk, device-groups-add-devices)
    # to the best-ranked version, mirroring the CRUD dedupe above.
    operation_paths = _dedupe_operation_paths_by_version(operation_paths)

    operations: list[OperationObject] = []
    for prefix, tail in operation_paths:
        full_path = f"/{prefix}/{tail}" if prefix else f"/{tail}"
        params = _path_params(tail)
        methods = _methods_for(paths, full_path)
        op_desc = _normalize_description((paths.get(full_path) or {}).get("get", {}).get("description") or "")

        # Collapse all write verbs on one path into a single manage-style tool
        # (action_type drives the verb, mirroring CRUD manage). GET stays its
        # own read tool. This keeps deep nested-item paths
        # (policy-group-list/{name}) to one get + one manage rather than 3-4
        # identically-named rows.
        write_methods = tuple(m for m in ("post", "patch", "put", "delete") if m in methods)
        if "get" in methods:
            operations.append(
                OperationObject(
                    filename=spec_path.stem,
                    tag_group=tag_group,
                    path_prefix=prefix,
                    path_tail=tail,
                    methods=("get",),
                    tool_name=_operation_tool_name(tail, "get"),
                    is_read=True,
                    has_body=False,
                    path_params=params,
                    description=op_desc,
                )
            )
        if write_methods:
            # Name comes from the dominant write verb: prefer post (create-ish),
            # else the single verb present. has_body if any non-delete verb has one.
            primary = write_methods[0]
            has_body = any(_op_has_body(paths, full_path, m) for m in write_methods if m != "delete")
            operations.append(
                OperationObject(
                    filename=spec_path.stem,
                    tag_group=tag_group,
                    path_prefix=prefix,
                    path_tail=tail,
                    methods=write_methods,
                    tool_name=_operation_tool_name(tail, primary),
                    is_read=False,
                    has_body=has_body,
                    path_params=params,
                    description=op_desc,
                )
            )

    return objects, operations


def load_objects(
    specs_dir: Path, include_filters: list[str] | None
) -> tuple[list[ConfigObject], list[OperationObject]]:
    """Walk the specs directory, parse each JSON, apply skip-list and filters."""
    if not specs_dir.exists():
        print(f"ERROR: specs directory not found: {specs_dir}", file=sys.stderr)
        sys.exit(1)

    files = sorted(specs_dir.glob("*.json"))
    files = [f for f in files if f.name != "_manifest.json"]
    if not files:
        print(f"ERROR: no .json specs under {specs_dir}", file=sys.stderr)
        sys.exit(1)

    objects: list[ConfigObject] = []
    operations: list[OperationObject] = []
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
        objs, ops = parse_spec_objects(fp)
        objects.extend(objs)
        operations.extend(ops)

    print(
        f"Loaded {len(objects)} CRUD objects + {len(operations)} operations "
        f"(skipped {skipped_covered} skip-listed files, "
        f"{skipped_filter} filtered out, "
        f"{len(files)} domain files in {specs_dir.name}/)"
    )
    return objects, operations


def parse_spec(spec_path: Path) -> ConfigObject | None:
    """Back-compat shim: return the first CRUD object in a spec (or None).

    The distiller historically imported ``parse_spec`` to drive its per-file
    schema resolution. It now uses :func:`parse_spec_objects` for multi-object
    iteration, but keep this for any external callers / older code paths.
    """
    objs, _ops = parse_spec_objects(spec_path)
    return objs[0] if objs else None


# ---------------------------------------------------------------------------
# Code emission
# ---------------------------------------------------------------------------


_FILE_HEADER = '''"""Aruba Central ``{source_file}`` config-model tools.

Initial import emitted by ``scripts/import_central_config_tools.py``
from a snapshot of ``vendor/central/config/``. The import is
**one-shot**: this file is hand-curated going forward — edit freely,
refine docstrings, add per-type schema knobs, split into smaller files
as needed. Re-running the script will overwrite this file, so only do
so before any hand edits or with care.

Covers config objects sourced from the ``{source_file}.json`` vendor
spec file. Wrappers
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


def emit_source_module(group: SourceModule) -> str:
    """Render one .py file body for a SourceModule (one vendor source file)."""
    parts: list[str] = [_FILE_HEADER.format(source_file=group.name)]
    for obj in sorted(group.objects, key=lambda o: o.title):
        parts.append(f"\n# ----- {obj.title} -----\n")
        if obj.has_get_collection or obj.has_get_item:
            parts.append(_emit_get_function(obj))
        if obj.has_create or obj.has_update or obj.has_delete:
            parts.append(_emit_manage_function(obj))
    return "".join(parts)


# ---------------------------------------------------------------------------
# Inventory model (dry-run)
# ---------------------------------------------------------------------------


def _crud_get_row(obj: ConfigObject, hand_curated_skip: bool) -> dict:
    """One inventory row for a CRUD object's read tool."""
    tool_name = f"central_get_{_to_snake_case(obj.title)}"
    params: list[str] = [] if obj.is_singleton else [_safe_param_name(obj.name_param)]
    methods = ["get"]
    coll_path = f"/{obj.path_prefix}/{obj.path_segment}" if obj.path_prefix else f"/{obj.path_segment}"
    return {
        "tool_name": tool_name,
        "kind": "get",
        "http_methods": methods,
        "path": coll_path,
        "params": params,
        "annotation": "READ_ONLY",
        "source_file": f"{obj.filename}.json",
        "module": f"{_to_snake_case(obj.filename)}.py",
        "hand_curated_skip": hand_curated_skip,
    }


def _crud_manage_row(obj: ConfigObject, hand_curated_skip: bool) -> dict:
    """One inventory row for a CRUD object's manage tool."""
    tool_name = f"central_manage_{_to_snake_case(obj.title)}"
    params = ["action_type", "payload", "scope_id", "device_function", "confirmed"]
    if not obj.is_singleton:
        params = [_safe_param_name(obj.name_param), *params]
    methods = []
    if obj.has_create:
        methods.append("post")
    if obj.has_update:
        methods.append("patch")
    if obj.has_delete:
        methods.append("delete")
    item_path = (
        f"/{obj.path_prefix}/{obj.path_segment}"
        if obj.is_singleton
        else f"/{obj.path_prefix}/{obj.path_segment}/{{{obj.name_param}}}"
    )
    return {
        "tool_name": tool_name,
        "kind": "manage",
        "http_methods": methods,
        "path": item_path,
        "params": params,
        "annotation": "WRITE_DELETE",
        "source_file": f"{obj.filename}.json",
        "module": f"{_to_snake_case(obj.filename)}.py",
        "hand_curated_skip": hand_curated_skip,
    }


def _operation_row(op: OperationObject, hand_curated_skip: bool) -> dict:
    """One inventory row for an operation (path, method) tool."""
    params = [_safe_param_name(p) for p in op.path_params]
    if op.has_body:
        params.append("payload")
    full_path = f"/{op.path_prefix}/{op.path_tail}" if op.path_prefix else f"/{op.path_tail}"
    return {
        "tool_name": op.tool_name,
        "kind": "operation",
        "http_methods": list(op.methods),
        "path": full_path,
        "params": params,
        "annotation": "READ_ONLY" if op.is_read else "WRITE_DELETE",
        "source_file": f"{op.filename}.json",
        "module": f"{_to_snake_case(op.filename)}.py",
        "hand_curated_skip": hand_curated_skip,
    }


def _crud_is_hand_curated_skip(obj: ConfigObject) -> bool:
    """True when a CRUD object's segment is in the hand-curated skip set."""
    return obj.path_segment in HAND_CURATED_SEGMENTS


def _operation_is_hand_curated_skip(op: OperationObject) -> bool:
    """True when an operation's first path segment is in the hand-curated skip set."""
    first_seg = op.path_tail.split("/", 1)[0]
    return first_seg in HAND_CURATED_SEGMENTS


def build_inventory(
    objects: list[ConfigObject],
    operations: list[OperationObject],
) -> list[dict]:
    """Build the dry-run inventory of every tool the generator would emit.

    A row whose resource segment is in ``HAND_CURATED_SEGMENTS`` is flagged
    ``hand_curated_skip=True``. The real (non-dry-run) emitter skips emitting
    those rows (the explicit keep-set stays hand-written), and they are
    excluded from the generated-name collision check. Every other row emits —
    the regen owns the full Central config CRUD surface.
    """
    rows: list[dict] = []
    for obj in sorted(objects, key=lambda o: (o.filename, o.title)):
        skip = _crud_is_hand_curated_skip(obj)
        if obj.has_get_collection or obj.has_get_item:
            rows.append(_crud_get_row(obj, skip))
        if obj.has_create or obj.has_update or obj.has_delete:
            rows.append(_crud_manage_row(obj, skip))
    for op in sorted(operations, key=lambda o: (o.filename, o.path_tail, o.methods)):
        skip = _operation_is_hand_curated_skip(op)
        rows.append(_operation_row(op, skip))
    return rows


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
        help="Override the default ``vendor/central/config/`` source directory.",
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
        help="Do not write any tool files. Implied by --inventory.",
    )
    parser.add_argument(
        "--inventory",
        type=Path,
        default=None,
        help="Write a JSON inventory of every tool the generator WOULD emit to "
        "this path, and write no tool .py files (dry-run). Used to review the "
        "full generated surface before committing to a regeneration.",
    )
    args = parser.parse_args()

    root = _repo_root()
    specs_dir = args.specs_dir or (root / "vendor" / "central" / "config")
    output_dir = args.output_dir or (root / "src" / "hpe_networking_mcp" / "platforms" / "central" / "tools")

    include_filters = [s.strip() for s in args.include.split(",")] if args.include else None

    print(f"Specs dir:  {specs_dir}")
    print(f"Output dir: {output_dir}")
    if include_filters:
        print(f"Filters:    {include_filters}")
    print()

    objects, operations = load_objects(specs_dir, include_filters)
    if not objects and not operations:
        print("No objects to emit. Exiting.")
        return 0

    print(f"Hand-curated keep-set (never generated): {sorted(HAND_CURATED_SEGMENTS)}")

    # --- Inventory / dry-run path ---------------------------------------
    if args.inventory is not None:
        rows = build_inventory(objects, operations)
        _report_and_write_inventory(rows, objects, specs_dir, args.inventory, root)
        return 0

    # The vendor specs carry no x-tag-group, so emitted tools are grouped by
    # their source spec filename stem (snake-cased) — one module per source
    # file. The regen owns the full config CRUD surface — the ONLY objects /
    # operations it skips are those whose resource segment is in the explicit
    # ``HAND_CURATED_SEGMENTS`` keep-set (genuinely custom shapes that stay
    # hand-written). Everything else emits.
    groups: dict[str, SourceModule] = {}

    def _module_for(stem: str) -> SourceModule:
        slug = _to_snake_case(stem)
        if slug not in groups:
            groups[slug] = SourceModule(name=stem, slug=slug)
        return groups[slug]

    for obj in objects:
        if _crud_is_hand_curated_skip(obj):
            continue
        _module_for(obj.filename).objects.append(obj)
    for op in operations:
        if _operation_is_hand_curated_skip(op):
            continue
        _module_for(op.filename).operations.append(op)

    print(f"\nGrouped into {len(groups)} source-file module(s):")
    for slug, group in sorted(groups.items()):
        print(f"  {slug}.py — {len(group.objects)} objects + {len(group.operations)} operations ({group.name}.json)")

    if args.dry_run:
        print("\n(--dry-run; no files written)")
        return 0

    output_dir.mkdir(parents=True, exist_ok=True)
    written = 0
    for slug, group in sorted(groups.items()):
        target = output_dir / f"{slug}.py"
        source = emit_source_module(group)
        target.write_text(source, encoding="utf-8")
        written += 1
        print(f"  wrote {target.relative_to(root)} ({len(group.objects)} objects + {len(group.operations)} operations)")

    print(f"\nDone. Wrote {written} module(s) under {output_dir.relative_to(root)}.")
    print("Run `uv run ruff format <output_dir>` to canonicalize whitespace, then review the diff.")
    return 0


def _objects_without_request_schema(objects: list[ConfigObject], specs_dir: Path) -> list[str]:
    """Return tool names of write-capable CRUD objects with no resolvable request schema.

    Mirrors the distiller's per-object request-schema resolution so the
    inventory can flag objects whose ``payload`` field would be unguided.
    """

    def _resolve_ref(spec: dict, ref: str) -> dict:
        node: object = spec
        for part in ref.lstrip("#/").split("/"):
            node = node.get(part, {}) if isinstance(node, dict) else {}
        return node if isinstance(node, dict) else {}

    def _schema_for_op(spec: dict, op: dict) -> dict | None:
        rb = op.get("requestBody") or {}
        if "$ref" in rb:
            rb = _resolve_ref(spec, rb["$ref"])
        for media in (rb.get("content") or {}).values():
            sch = media.get("schema") or {}
            if "$ref" in sch:
                return _resolve_ref(spec, sch["$ref"])
            if sch:
                return sch
        return None

    # Pre-load each spec once.
    spec_cache: dict[str, dict] = {}
    missing: list[str] = []
    for obj in objects:
        if not (obj.has_create or obj.has_update or obj.has_delete):
            continue
        spec = spec_cache.get(obj.filename)
        if spec is None:
            spec = json.loads((specs_dir / f"{obj.filename}.json").read_text(encoding="utf-8"))
            spec_cache[obj.filename] = spec
        paths = spec.get("paths") or {}
        coll = f"/{obj.path_prefix}/{obj.path_segment}" if obj.path_prefix else f"/{obj.path_segment}"
        item = f"{coll}/{{{obj.name_param}}}"
        found = False
        for path in (item, coll):
            methods = paths.get(path) or {}
            for verb in ("post", "patch", "put"):
                op = methods.get(verb)
                if isinstance(op, dict) and _schema_for_op(spec, op):
                    found = True
                    break
            if found:
                break
        if not found:
            missing.append(f"central_manage_{_to_snake_case(obj.title)}")
    return missing


def _report_and_write_inventory(
    rows: list[dict],
    objects: list[ConfigObject],
    specs_dir: Path,
    inventory_path: Path,
    root: Path,
) -> None:
    """Write the inventory JSON and print the summary (writes NO tool files)."""
    n_get = sum(1 for r in rows if r["kind"] == "get")
    n_manage = sum(1 for r in rows if r["kind"] == "manage")
    n_op = sum(1 for r in rows if r["kind"] == "operation")
    n_hand_curated_skip = sum(1 for r in rows if r.get("hand_curated_skip"))

    # Tool-name collisions AMONG generated tools (two paths → same name).
    # Rows that the real emitter would skip — hand-curated-segment skips — are
    # excluded: they never get emitted, so a shared name among them is not a
    # live collision.
    emitted_rows = [r for r in rows if not r.get("hand_curated_skip")]
    name_counts: dict[str, list[str]] = {}
    for r in emitted_rows:
        name_counts.setdefault(r["tool_name"], []).append(r["path"])
    dup_names = {n: ps for n, ps in name_counts.items() if len(ps) > 1}

    no_schema = _objects_without_request_schema(objects, specs_dir)

    inventory_path.parent.mkdir(parents=True, exist_ok=True)
    inventory_path.write_text(json.dumps(rows, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print("\n=== DRY-RUN INVENTORY (no tool files written) ===")
    print(f"Inventory written to: {inventory_path}")
    print(f"Total tools:                 {len(rows)}")
    print(f"  CRUD get:                  {n_get}")
    print(f"  CRUD manage:               {n_manage}")
    print(f"  operations:                {n_op}")
    print(f"  hand-curated-segment skip: {n_hand_curated_skip} (would be SKIPPED on real emit)")
    print(f"Objects w/ no request schema: {len(no_schema)}")
    for name in sorted(no_schema):
        print(f"    {name}")
    print(f"Generated-name collisions:    {len(dup_names)}")
    for name, paths in sorted(dup_names.items()):
        print(f"    {name}:")
        for p in paths:
            print(f"        {p}")


if __name__ == "__main__":
    sys.exit(main())
